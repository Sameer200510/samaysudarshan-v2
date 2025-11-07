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
    # Flatten
    genes: List[Gene] = []
    for _sec, arr in chromosome.items():
        genes.extend(arr)

    hard_v = violates_hard(genes, data)
    hard_count = sum(hard_v.values())

    if hard_count > 0:
        fitness = -HARD_HUGE_PENALTY * hard_count
        return {
            "fitness": fitness,
            "hard_breakdown": dict(hard_v),
            "soft_breakdown": {},
        }

    # Soft penalties
    soft_total, soft_bd = soft_penalty(genes, data, weights={})
    # As per spec: start 1000, minus penalties
    quality = 1000 - soft_total
    return {
        "fitness": quality,
        "hard_breakdown": {},
        "soft_breakdown": soft_bd,
    }