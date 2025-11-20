# timetable_ga/fitness.py
from typing import List, Dict
from .models import Gene, GAInput
from .constraints import violates_hard, soft_penalty

HARD_HUGE_PENALTY = 1_000_000

def evaluate(chromosome: Dict[int, List[Gene]], data: GAInput) -> Dict:
    """
    Chromosome: { section_id: [Gene, ...], ... }
    Returns dict with 'fitness', 'hard_breakdown', 'soft_breakdown'
    """

    # Flatten genes list
    genes: List[Gene] = []
    for _sec, arr in chromosome.items():
        genes.extend(arr)

    # --- existing hard constraint checks ---
    hard_v = violates_hard(genes, data) or {}
    # --- NEW: hard check - same subject more than once per section per day ---
    # Build map: (section_id, day_index, subject_id) -> count
    subj_day_counts = {}
    # Prepare slot -> index mapping if slot_order exists
    slot_index_map = {}
    try:
        slot_order = getattr(data, "slot_order", None)
        if slot_order:
            slot_index_map = {int(sid): idx for idx, sid in enumerate(slot_order)}
    except Exception:
        slot_index_map = {}

    pday = getattr(data, "periods_per_day", None)

    for g in genes:
        # determine day index for gene g
        day_idx = None
        try:
            if slot_index_map:
                idx = slot_index_map.get(int(g.slot_id))
                if idx is not None:
                    day_idx = idx // (pday or 1)
            if day_idx is None and pday:
                # fallback arithmetic (assumes contiguous 1..N layout)
                day_idx = (int(g.slot_id) - 1) // int(pday)
        except Exception:
            # last-resort fallback (treat all as same day 0)
            day_idx = 0

        key = (int(g.section_id), int(day_idx), int(g.subject_id))
        subj_day_counts[key] = subj_day_counts.get(key, 0) + 1

    # Count violations: every extra occurrence beyond 1 is a violation
    multi_day_violations = 0
    for cnt in subj_day_counts.values():
        if cnt > 1:
            multi_day_violations += (cnt - 1)

    if multi_day_violations:
        hard_v = dict(hard_v)  # copy to modify
        hard_v["subject_multiple_per_day"] = hard_v.get("subject_multiple_per_day", 0) + multi_day_violations

    hard_count = sum(hard_v.values()) if hard_v else 0

    # If any hard violations -> very negative fitness
    if hard_count > 0:
        fitness = -HARD_HUGE_PENALTY * hard_count
        return {
            "fitness": fitness,
            "hard_breakdown": dict(hard_v),
            "soft_breakdown": {},
        }

    # Soft penalties (unchanged)
    soft_total, soft_bd = soft_penalty(genes, data, weights={})
    # As per spec: start 1000, minus penalties
    quality = 1000 - soft_total
    return {
        "fitness": quality,
        "hard_breakdown": {},
        "soft_breakdown": soft_bd,
    }