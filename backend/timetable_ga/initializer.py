# timetable_ga/initializer.py
import random
from typing import Dict, List, Set
from collections import defaultdict
from .models import GAInput, Gene

def _block_starts(usable: Set[int], pday: int, block_size: int):
    """Yield valid starts where a block fully fits inside usable slots."""
    if not usable or pday <= 0:
        return
    usable_sorted = sorted(usable)
    max_slot = max(usable_sorted)
    days = (max_slot + pday - 1) // pday

    for d in range(days):
        base = d * pday
        for s in range(1, pday - block_size + 2):
            block = {base + s + k for k in range(block_size)}
            if block.issubset(usable):
                yield base + s

def _slot_day(slot: int, data: GAInput) -> int:
    """Return 0-based day index for a slot using slot_order if present, else fallback."""
    pday = int(getattr(data, "periods_per_day", 0) or 0)
    slot_order = getattr(data, "slot_order", None)
    if slot_order and pday > 0:
        # index in slot_order -> day = index // pday
        try:
            idx = slot_order.index(slot)
            return idx // pday
        except ValueError:
            # if not found, fallback
            return (slot - 1) // pday if pday else 0
    # fallback arithmetic
    return (slot - 1) // pday if pday else 0

def _rtype(r):
    """
    Robust room-type accessor:
      - prefer models.Room.rtype
      - fallback to room_type / type fields if present (DB-shaped objects)
      - default to 'LECTURE'
    """
    if r is None:
        return "LECTURE"
    # try model attribute first
    val = getattr(r, "rtype", None)
    if val:
        return str(val).upper()
    # fallback names
    val = getattr(r, "room_type", None) or getattr(r, "type", None)
    if val:
        return str(val).upper()
    return "LECTURE"

def _rcap(r):
    """Robust capacity accessor: capacity or cap or 0"""
    if r is None:
        return 0
    try:
        return int(getattr(r, "capacity", getattr(r, "cap", 0)) or 0)
    except Exception:
        try:
            return int(r)  # if r itself is number-like
        except Exception:
            return 0

def random_room_for(kind: str, data: GAInput, min_cap: int):
    kind = (kind or "THEORY").upper()
    desired = "LAB" if kind == "LAB" else "LECTURE"

    rooms = list(data.rooms.values())
    # 1) match type + cap
    pool = [r.room_id for r in rooms if _rtype(r) == desired and _rcap(r) >= min_cap]
    if pool:
        return random.choice(pool)
    # 2) match cap only
    pool = [r.room_id for r in rooms if _rcap(r) >= min_cap]
    if pool:
        return random.choice(pool)
    # 3) match type only
    pool = [r.room_id for r in rooms if _rtype(r) == desired]
    if pool:
        return random.choice(pool)
    # 4) any room
    return random.choice([r.room_id for r in rooms])

def random_slot_start(block_size: int, data: GAInput) -> int:
    """Pick a random valid block start respecting usable timeslots."""
    starts = list(_block_starts(getattr(data, "timeslots_usable", set()), data.periods_per_day, block_size))
    if starts:
        return random.choice(starts)
    usable = getattr(data, "timeslots_usable", None)
    if usable:
        return min(usable)
    return 1

def random_chromosome(data: GAInput) -> Dict[int, List[Gene]]:
    """
    Build initial chromosome honoring:
      - contiguous_block_size for labs (exactly),
      - at most one occurrence of same subject per section per day,
      - no section/faculty/room overlaps,
      - attempts many starts before fallback.
    """
    chrom: Dict[int, List[Gene]] = {sec_id: [] for sec_id in data.sections.keys()}

    used_slots_section = defaultdict(set)   # section_id -> set(slot_ids)
    used_slots_faculty = defaultdict(set)   # faculty_id -> set(slot_ids)
    used_slots_room = defaultdict(set)      # room_id -> set(slot_ids)
    subject_days = defaultdict(set)         # (section_id, subject_id) -> set(day_index)

    # Curriculum list: (section_id, subject_id, faculty_id)
    for (sec_id, subj_id, fac_id) in data.curriculum:
        subj = data.subjects.get(subj_id)
        sec = data.sections.get(sec_id)

        if subj is None or sec is None:
            continue

        total_lectures = int(getattr(subj, "lecture_count", 0) or 0)
        is_lab = (getattr(subj, "subj_type", "THEORY") or "THEORY").upper() == "LAB"
        block_size = int(getattr(subj, "contiguous_block_size", 1) or 1) if is_lab else 1
        block_size = max(1, block_size)

        # number of blocks to schedule
        if block_size == 1:
            blocks = max(0, total_lectures)
        else:
            # ensure labs divide into blocks: if not divisible, round down (constraint will catch mismatch)
            blocks = max(0, total_lectures // block_size)

        # candidate starts precomputed
        starts = list(_block_starts(getattr(data, "timeslots_usable", set()), data.periods_per_day, block_size))
        if not starts:
            # fallback to simple list of first N slots
            usable = sorted(list(getattr(data, "timeslots_usable", {1})))
            starts = usable

        # For each required block, try to find a non-conflicting placement
        for _ in range(blocks):
            placed = False
            random.shuffle(starts)
            for s in starts:
                day_idx = _slot_day(s, data)

                # Prevent same subject twice a day for this section
                if day_idx in subject_days[(sec_id, subj_id)]:
                    continue

                # Try multiple rooms in heuristics order
                # prefer type+capacity then capacity then any
                room_candidates = []

                # prefer rooms that match type + capacity
                for r in data.rooms.values():
                    if _rtype(r) == ("LAB" if is_lab else "LECTURE") and _rcap(r) >= int(getattr(sec, "student_count", 0) or 0):
                        room_candidates.append(r.room_id)
                # capacity only
                for r in data.rooms.values():
                    if _rcap(r) >= int(getattr(sec, "student_count", 0) or 0) and r.room_id not in room_candidates:
                        room_candidates.append(r.room_id)
                # fallback any
                for r in data.rooms.values():
                    if r.room_id not in room_candidates:
                        room_candidates.append(r.room_id)

                for room_id in room_candidates:
                    conflict = False
                    # check every slot in block
                    for k in range(block_size):
                        slot = s + k
                        if slot not in getattr(data, "timeslots_usable", {slot}):
                            conflict = True
                            break
                        if slot in used_slots_section[sec_id] or slot in used_slots_faculty[fac_id] or slot in used_slots_room[room_id]:
                            conflict = True
                            break
                    if not conflict:
                        # create gene
                        gene = Gene(section_id=sec_id, subject_id=subj_id, faculty_id=fac_id, room_id=room_id, slot_id=s, block_size=block_size)
                        chrom[sec_id].append(gene)
                        # mark used
                        subject_days[(sec_id, subj_id)].add(day_idx)
                        for k in range(block_size):
                            slot = s + k
                            used_slots_section[sec_id].add(slot)
                            used_slots_faculty[fac_id].add(slot)
                            used_slots_room[room_id].add(slot)
                        placed = True
                        break
                if placed:
                    break

            if not placed:
                # last-resort fallback: choose random usable start and room (will be penalized by fitness)
                s = random_slot_start(block_size, data)
                r = random_room_for("LAB" if is_lab else "THEORY", data, int(getattr(sec, "student_count", 0) or 0))
                gene = Gene(section_id=sec_id, subject_id=subj_id, faculty_id=fac_id, room_id=r, slot_id=s, block_size=block_size)
                chrom[sec_id].append(gene)
                day_idx = _slot_day(s, data)
                subject_days[(sec_id, subj_id)].add(day_idx)
                for k in range(block_size):
                    slot = s + k
                    used_slots_section[sec_id].add(slot)
                    used_slots_faculty[fac_id].add(slot)
                    used_slots_room[r].add(slot)

    return chrom