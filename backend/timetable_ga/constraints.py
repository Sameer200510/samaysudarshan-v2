# timetable_ga/constraints.py
from typing import List, Dict, Tuple, Set, Iterable
from collections import defaultdict
from .models import Gene, GAInput

# ---------- Hard constraints ----------

def violates_hard(g: List[Gene], data: GAInput) -> Dict[str, int]:
    """Returns count of each hard-constraint violation."""
    v = defaultdict(int)

    # Indexes
    teacher_at_slot: Dict[Tuple[int,int], int] = {}      # (faculty_id, slot) -> gene_ix
    room_at_slot: Dict[Tuple[int,int], int] = {}         # (room_id, slot) -> gene_ix
    section_at_slot: Dict[Tuple[int,int], int] = {}      # (section_id, slot) -> gene_ix

    for gene in g:
        subj = data.subjects[gene.subject_id]
        room = data.rooms.get(gene.room_id)

        # Faculty availability
        if gene.faculty_id in data.faculty_unavailability:
            for s in gene.occupied_slots():
                if s in data.faculty_unavailability[gene.faculty_id]:
                    v["faculty_unavailable"] += 1

        # Usable slot check
        for s in gene.occupied_slots():
            if s not in data.timeslots_usable:
                v["slot_not_usable"] += 1

        # Room type
        if subj.subj_type == 'LAB' and room.rtype != 'LAB':
            v["room_type_mismatch"] += 1
        if subj.subj_type == 'THEORY' and room.rtype != 'LECTURE':
            v["room_type_mismatch"] += 1

        # Room capacity
        section_size = data.sections[gene.section_id].student_count
        if room.capacity < section_size:
            v["room_capacity"] += 1

        # Contiguity for labs (must be consecutive slots within the same day)
        if subj.subj_type == 'LAB':
            if gene.block_size != subj.contiguous_block_size:
                v["lab_block_size_wrong"] += 1
            # Day boundary check
            pday = data.periods_per_day
            base_day = (gene.slot_id - 1) // pday
            for k,s in enumerate(gene.occupied_slots()):
                if (s - 1) // pday != base_day:
                    v["lab_crosses_day"] += 1

        # Overlaps (teacher/room/section)
        for s in gene.occupied_slots():
            key_t = (gene.faculty_id, s)
            key_r = (gene.room_id, s)
            key_sec = (gene.section_id, s)
            if key_t in teacher_at_slot: v["teacher_overlap"] += 1
            else: teacher_at_slot[key_t] = 1
            if key_r in room_at_slot: v["room_overlap"] += 1
            else: room_at_slot[key_r] = 1
            if key_sec in section_at_slot: v["section_overlap"] += 1
            else: section_at_slot[key_sec] = 1

    # Subject weekly quota (count sessions per (section,subject))
    need = defaultdict(int)
    have = defaultdict(int)
    for (section_id, subject_id, _f) in data.curriculum:
        need[(section_id, subject_id)] += data.subjects[subject_id].lecture_count

    for gene in g:
        key = (gene.section_id, gene.subject_id)
        have[key] += gene.block_size  # theory=1, lab=block_size periods

    for k, required in need.items():
        if have[k] != required:
            v["subject_weekly_quota"] += abs(required - have[k])

    return v

# ---------- Soft constraints (weighted penalties) ----------

def soft_penalty(g: List[Gene], data: GAInput, weights: Dict[str,int]) -> Tuple[int, Dict[str,int]]:
    """Returns total soft penalty and breakdown (higher = worse)."""
    p = defaultdict(int)

    # Index by section/day/periods for gap & repeats
    pday = data.periods_per_day

    # 1) Minimize section idle gaps (weight: high)
    by_sec_slots = defaultdict(list)
    for gene in g:
        for s in gene.occupied_slots():
            by_sec_slots[gene.section_id].append(s)
    for sec, slots in by_sec_slots.items():
        if not slots: continue
        slots = sorted(slots)
        # gaps between consecutive occupied slots within a day
        prev_day = (slots[0]-1)//pday
        prev_s = slots[0]
        for s in slots[1:]:
            day = (s-1)//pday
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
        prev_day = (slots[0]-1)//pday
        prev_s = slots[0]
        for s in slots[1:]:
            day = (s-1)//pday
            if day == prev_day and s - prev_s > 1:
                p["teacher_gaps"] += (s - prev_s - 1)
            prev_day, prev_s = day, s

    # 3) Spread subjects across week (penalize clustering: same subject twice on same day)
    seen_day_subj = defaultdict(lambda: defaultdict(int))  # (section)->(day,subject)->count
    for gene in g:
        day = (gene.slot_id - 1)//pday
        seen_day_subj[(gene.section_id)][(day, gene.subject_id)] += 1
    for sec, dmap in seen_day_subj.items():
        for (_day, _subj), cnt in dmap.items():
            if cnt > 1:
                p["repeat_same_day"] += (cnt - 1)

    # 4) Avoid first/last period (low)
    for gene in g:
        day = (gene.slot_id - 1)//pday
        first = day*pday + 1
        last  = day*pday + pday
        # for labs, count if either end touches first/last
        occ = gene.occupied_slots()
        if first in occ: p["avoid_first_last"] += 1
        if last  in occ: p["avoid_first_last"] += 1

    # 5) Balance daily load (section): prefer <=5 per day
    sec_day_load = defaultdict(lambda: defaultdict(int))
    for gene in g:
        for s in gene.occupied_slots():
            day = (s-1)//pday
            sec_day_load[gene.section_id][day] += 1
    for sec, dmap in sec_day_load.items():
        for day, cnt in dmap.items():
            if cnt > 5:
                p["over_daily_load"] += (cnt - 5)

    # 6) Faculty daily load cap (soft)
    fac_day_load = defaultdict(lambda: defaultdict(int))
    for gene in g:
        for s in gene.occupied_slots():
            day = (s-1)//pday
            fac_day_load[gene.faculty_id][day] += 1
    for fac, dmap in fac_day_load.items():
        for day, cnt in dmap.items():
            if cnt > 6:
                p["faculty_daily_load"] += (cnt - 6)

    # 7) Avoid too many labs in one day (per section)
    sec_day_lab = defaultdict(lambda: defaultdict(int))
    from .models import GAInput  # avoid cycle
    for gene in g:
        subj_type = 'LAB' if data.subjects[gene.subject_id].subj_type == 'LAB' else 'THEORY'
        if subj_type == 'LAB':
            day = (gene.slot_id - 1)//pday
            sec_day_lab[gene.section_id][day] += 1
    for sec, dmap in sec_day_lab.items():
        for day, cnt in dmap.items():
            if cnt > 1:
                p["too_many_labs"] += (cnt - 1)

    # 8) Faculty preferences (morning avoid etc.) – placeholder hook
    # You can feed a set of discouraged slots per faculty as "preferences_avoid"
    # For V1, skip unless you pass extra map.

    # Weighted sum
    WEI = {
        "section_gaps": 90,
        "teacher_gaps": 70,
        "repeat_same_day": 90,         # Keep same subject not repeated same day
        "avoid_first_last": 30,
        "over_daily_load": 80,
        "faculty_daily_load": 50,
        "too_many_labs": 60,
        # "faculty_preferences": 60,    # if you wire preferences
    }
    WEI.update(weights or {})

    total = 0
    for k, cnt in p.items():
        total += WEI.get(k, 0) * cnt

    return total, dict(p)