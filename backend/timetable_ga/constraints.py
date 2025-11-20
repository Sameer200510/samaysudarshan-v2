# timetable_ga/constraints.py
from typing import List, Dict, Tuple, Set, Iterable
from collections import defaultdict
from .models import Gene, GAInput

# ---------- Hard constraints ----------

def _build_slot_day_map(data: GAInput) -> Dict[int, int]:
    """
    Map slot_id -> day_index (0-based) using data.slot_order and periods_per_day.
    Falls back to integer division if slot_order missing.
    """
    mapping: Dict[int, int] = {}
    pday = int(getattr(data, "periods_per_day", 0) or 0)
    slot_order = getattr(data, "slot_order", None)

    if slot_order and pday > 0:
        for idx, sid in enumerate(slot_order):
            day = idx // pday
            mapping[int(sid)] = day
        return mapping

    # fallback: assume slots numbered sequentially starting at 1 and pday available
    if pday > 0:
        # fallback handled by caller via (slot-1)//pday
        return {}
    # last resort: map slot -> 0
    return {}

def violates_hard(g: List[Gene], data: GAInput) -> Dict[str, int]:
    """
    Returns dict of hard-constraint violation counts.
    NOTE: For certain violations we return immediately with a very large count
    (effectively rejecting the chromosome) to enforce 'hard' semantics.
    """
    v = defaultdict(int)

    # Indexes for overlap checks
    teacher_at_slot: Dict[Tuple[int,int], int] = {}      # (faculty_id, slot) -> gene_ix
    room_at_slot: Dict[Tuple[int,int], int] = {}         # (room_id, slot) -> gene_ix
    section_at_slot: Dict[Tuple[int,int], int] = {}      # (section_id, slot) -> gene_ix

    # build robust mapping slot_id -> day_idx
    slot_to_day = _build_slot_day_map(data)
    pday = int(getattr(data, "periods_per_day", 0) or 0)

    # counters to enforce "one subject per day per section" and "one lab block per day"
    subj_day_count = defaultdict(int)       # (section_id, subject_id, day) -> count
    subj_day_lab_count = defaultdict(int)   # (section_id, subject_id, day) -> lab-block-count

    # Iterate genes
    for gene in g:
        # defensive getattr usage
        subj = data.subjects.get(gene.subject_id)
        room = data.rooms.get(gene.room_id)

        if subj is None or room is None:
            # missing reference -> count as violation (foreign-key-like)
            v["missing_reference"] += 1
            continue

        # Faculty availability: if faculty unavailable at any occupied slot -> violation
        if gene.faculty_id in getattr(data, "faculty_unavailability", {}):
            for s in gene.occupied_slots():
                if s in data.faculty_unavailability[gene.faculty_id]:
                    # hard fail candidate (faculty scheduled when unavailable)
                    return {"faculty_unavailable": 999999}

        # Usable slot check
        usable_set = getattr(data, "timeslots_usable", None)
        if usable_set is not None:
            for s in gene.occupied_slots():
                if s not in usable_set:
                    # hard fail: using unusable slot
                    return {"slot_not_usable": 999999}

        # Room type mismatch
        rtype = getattr(room, "rtype", None) or getattr(room, "room_type", None) or getattr(room, "type", None) or "LECTURE"
        rtype = str(rtype).upper()
        if subj.subj_type == 'LAB' and rtype != 'LAB':
            return {"room_type_mismatch": 999999}
        if subj.subj_type == 'THEORY' and rtype != 'LECTURE':
            return {"room_type_mismatch": 999999}

        # Room capacity
        sec_obj = data.sections.get(gene.section_id)
        section_size = getattr(sec_obj, "student_count", None) if sec_obj is not None else None
        if section_size is None:
            # missing section mapping -> hard fail
            return {"missing_section": 999999}
        else:
            try:
                if int(getattr(room, "capacity", 0) or 0) < int(section_size or 0):
                    return {"room_capacity": 999999}
            except Exception:
                return {"room_capacity": 999999}

        # Contiguity for labs (must be consecutive slots within the same day)
        if subj.subj_type == 'LAB':
            # block size correctness
            expected_block = int(getattr(subj, "contiguous_block_size", 1) or 1)
            gene_block = int(getattr(gene, "block_size", 1) or 1)
            if gene_block != expected_block:
                # hard fail: gene uses wrong block size
                return {"lab_block_size_wrong": 999999}

            # ensure occupied_slots length matches block_size
            occ = gene.occupied_slots()
            if len(occ) != gene_block:
                return {"lab_block_size_mismatch": 999999}

            # day boundary check: all occupied slots must be in same day (use slot_to_day mapping)
            try:
                first_slot = occ[0]
                day = slot_to_day.get(first_slot, (first_slot - 1) // pday if pday else 0)
            except Exception:
                day = 0
            for s in occ:
                s_day = slot_to_day.get(s, (s - 1) // pday if pday else 0)
                if s_day != day:
                    return {"lab_crosses_day": 999999}

        # Overlaps (teacher/room/section) per occupied slot
        for s in gene.occupied_slots():
            key_t = (gene.faculty_id, s)
            key_r = (gene.room_id, s)
            key_sec = (gene.section_id, s)
            if key_t in teacher_at_slot:
                # immediate reject: teacher double-booked
                return {"teacher_overlap": 999999}
            else:
                teacher_at_slot[key_t] = 1
            if key_r in room_at_slot:
                # immediate reject: room double-booked
                return {"room_overlap": 999999}
            else:
                room_at_slot[key_r] = 1
            if key_sec in section_at_slot:
                # immediate reject: section double-booked
                return {"section_overlap": 999999}
            else:
                section_at_slot[key_sec] = 1

        # Compute day index for this gene (based on its first occupied slot)
        try:
            first_slot = int(gene.occupied_slots()[0])
            day_idx = slot_to_day.get(first_slot, (first_slot - 1) // pday if pday else 0)
        except Exception:
            day_idx = 0

        subj_day_count[(gene.section_id, gene.subject_id, day_idx)] += 1
        if subj.subj_type == 'LAB':
            subj_day_lab_count[(gene.section_id, gene.subject_id, day_idx)] += 1

    # After all genes, detect repeats / multiple labs per day
    for (sec, subj, day), cnt in subj_day_count.items():
        if cnt > 1:
            # immediate reject: subject scheduled more than once in same day
            return {"subject_daily_repeat": 999999}

    for (sec, subj, day), cnt in subj_day_lab_count.items():
        if cnt > 1:
            # immediate reject: more than one lab-block of same subject on same day
            return {"lab_multiple_per_day": 999999}

    # Subject weekly quota (count sessions per (section,subject))
    # need = required periods; have = scheduled periods (theory=1 per gene, lab=block_size)
    need = defaultdict(int)
    have = defaultdict(int)
    for (section_id, subject_id, _f) in data.curriculum:
        need[(section_id, subject_id)] += int(getattr(data.subjects[subject_id], "lecture_count", 0) or 0)

    for gene in g:
        key = (gene.section_id, gene.subject_id)
        have[key] += int(getattr(gene, "block_size", 1) or 1)

    for k, required in need.items():
        if have.get(k, 0) != required:
            # don't hard-return here — return counted mismatch so GA can try to fix
            v["subject_weekly_quota"] += abs(required - have.get(k, 0))

    return dict(v)


# ---------- Soft constraints (weighted penalties) ----------

def soft_penalty(g: List[Gene], data: GAInput, weights: Dict[str,int]) -> Tuple[int, Dict[str,int]]:
    """Returns total soft penalty and breakdown (higher = worse)."""
    p = defaultdict(int)

    # Index by section/day/periods for gap & repeats
    pday = int(getattr(data, "periods_per_day", 0) or 0)

    # Build per-section occupied slots map (used for several soft checks including lunch)
    by_sec_slots = defaultdict(list)
    for gene in g:
        for s in gene.occupied_slots():
            by_sec_slots[gene.section_id].append(s)

    # 1) Minimize section idle gaps (weight: high)
    for sec, slots in by_sec_slots.items():
        if not slots: continue
        slots = sorted(slots)
        prev_day = (slots[0]-1)//pday if pday else 0
        prev_s = slots[0]
        for s in slots[1:]:
            day = (s-1)//pday if pday else 0
            if day == prev_day:
                if s - prev_s > 1:
                    p["section_gaps"] += (s - prev_s - 1)
            prev_day, prev_s = day, s

    # 2) Minimize teacher gaps
    by_fac_slots = defaultdict(list)
    for gene in g:
        for s in gene.occupied_slots():
            by_fac_slots[gene.faculty_id].append(s)
    for fac, slots in by_fac_slots.items():
        if not slots: continue
        slots = sorted(slots)
        prev_day = (slots[0]-1)//pday if pday else 0
        prev_s = slots[0]
        for s in slots[1:]:
            day = (s-1)//pday if pday else 0
            if day == prev_day and s - prev_s > 1:
                p["teacher_gaps"] += (s - prev_s - 1)
            prev_day, prev_s = day, s

    # 3) Spread subjects across week (penalize clustering: same subject twice on same day)
    seen_day_subj = defaultdict(lambda: defaultdict(int))  # (section)->(day,subject)->count
    for gene in g:
        day = (gene.slot_id - 1)//pday if pday else 0
        seen_day_subj[(gene.section_id)][(day, gene.subject_id)] += 1
    for sec, dmap in seen_day_subj.items():
        for (_day, _subj), cnt in dmap.items():
            if cnt > 1:
                p["repeat_same_day"] += (cnt - 1)

    # 4) Avoid first/last period (low)
    for gene in g:
        day = (gene.slot_id - 1)//pday if pday else 0
        first = day*pday + 1 if pday else gene.slot_id
        last  = day*pday + pday if pday else gene.slot_id
        occ = gene.occupied_slots()
        if first in occ: p["avoid_first_last"] += 1
        if last  in occ: p["avoid_first_last"] += 1

    # 5) Balance daily load (section): prefer <=5 per day
    sec_day_load = defaultdict(lambda: defaultdict(int))
    for gene in g:
        for s in gene.occupied_slots():
            day = (s-1)//pday if pday else 0
            sec_day_load[gene.section_id][day] += 1
    for sec, dmap in sec_day_load.items():
        for day, cnt in dmap.items():
            if cnt > 5:
                p["over_daily_load"] += (cnt - 5)

    # 6) Faculty daily load cap (soft)
    fac_day_load = defaultdict(lambda: defaultdict(int))
    for gene in g:
        for s in gene.occupied_slots():
            day = (s-1)//pday if pday else 0
            fac_day_load[gene.faculty_id][day] += 1
    for fac, dmap in fac_day_load.items():
        for day, cnt in dmap.items():
            if cnt > 6:
                p["faculty_daily_load"] += (cnt - 6)

    # 7) Avoid too many labs in one day (per section)
    sec_day_lab = defaultdict(lambda: defaultdict(int))
    for gene in g:
        subj_type = 'LAB' if data.subjects[gene.subject_id].subj_type == 'LAB' else 'THEORY'
        if subj_type == 'LAB':
            day = (gene.slot_id - 1)//pday if pday else 0
            sec_day_lab[gene.section_id][day] += 1
    for sec, dmap in sec_day_lab.items():
        for day, cnt in dmap.items():
            if cnt > 1:
                p["too_many_labs"] += (cnt - 1)

    # 8) Lunch window: prefer at least one free lunch slot per section (soft)
    lunch_slots = set(getattr(data, "lunch_slots", set()) or set())
    if lunch_slots:
        # by_sec_slots built earlier
        for sec_id in data.sections.keys():
            occ = set(by_sec_slots.get(sec_id, []))
            free_found = any((ls not in occ) for ls in lunch_slots)
            if not free_found:
                p["lunch_missing"] += 1

    # Weighted sum
    WEI = {
        "section_gaps": 90,
        "teacher_gaps": 70,
        "repeat_same_day": 90,         # Keep same subject not repeated same day
        "avoid_first_last": 30,
        "over_daily_load": 80,
        "faculty_daily_load": 50,
        "too_many_labs": 60,
        "lunch_missing": 200,          # strong penalty to encourage freeing lunch slot
    }
    WEI.update(weights or {})

    total = 0
    for k, cnt in p.items():
        total += WEI.get(k, 0) * cnt

    return total, dict(p)