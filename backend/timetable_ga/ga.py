# timetable_ga/ga.py
import random
from typing import Dict, List, Set, Tuple
from copy import deepcopy
from .models import Gene, GAInput
from .initializer import random_chromosome, random_room_for
from .fitness import evaluate
from collections import defaultdict

# ---------------- SAFE HELPERS ---------------- #

def rebuild_usage_table(chrom: Dict[int, List[Gene]], data: GAInput):
    """Return used slots maps for section/faculty/room and also subject-day counts."""
    used_sec = defaultdict(set)   # section_id -> set(slot_ids)
    used_fac = defaultdict(set)   # faculty_id -> set(slot_ids)
    used_room = defaultdict(set)  # room_id -> set(slot_ids)
    # subject-day map: (section_id, subject_id, day_idx) -> count
    subj_day = defaultdict(int)

    pday = int(getattr(data, "periods_per_day", 0) or 0)
    slot_order = getattr(data, "slot_order", None)

    def slot_day(s: int) -> int:
        if slot_order and pday:
            try:
                idx = slot_order.index(s)
                return idx // pday
            except ValueError:
                return (s - 1) // pday if pday else 0
        return (s - 1) // pday if pday else 0

    for sec, arr in chrom.items():
        for g in arr:
            for k in range(g.block_size):
                s = g.slot_id + k
                used_sec[g.section_id].add(s)
                used_fac[g.faculty_id].add(s)
                used_room[g.room_id].add(s)
            # count per-day subject blocks (use first slot to infer day)
            day = slot_day(g.slot_id)
            subj_day[(g.section_id, g.subject_id, day)] += 1

    return used_sec, used_fac, used_room, subj_day

def can_place_block(start: int, block: int, room: int, g: Gene, data: GAInput,
                    used_sec: Dict[int, Set[int]], used_fac: Dict[int, Set[int]], used_room: Dict[int, Set[int]]) -> bool:
    """Check whether placing block [start, start+block-1] for gene g in room is conflict-free."""
    for k in range(block):
        s = start + k
        # slot must be usable
        if s not in getattr(data, "timeslots_usable", {s}):
            return False
        # no overlaps
        if s in used_sec[g.section_id] or s in used_fac[g.faculty_id] or s in used_room[room]:
            return False
    return True

def _slot_day(slot: int, data: GAInput) -> int:
    pday = int(getattr(data, "periods_per_day", 0) or 0)
    slot_order = getattr(data, "slot_order", None)
    if slot_order and pday > 0:
        try:
            idx = slot_order.index(slot)
            return idx // pday
        except ValueError:
            return (slot - 1) // pday if pday else 0
    return (slot - 1) // pday if pday else 0

# ---------------- SAFE CROSSOVER ---------------- #

def safe_sectionwise_crossover(p1: Dict[int, List[Gene]],
                               p2: Dict[int, List[Gene]],
                               data: GAInput,
                               rate: float = 0.9) -> Tuple[Dict[int, List[Gene]], Dict[int, List[Gene]]]:
    if random.random() > rate:
        return deepcopy(p1), deepcopy(p2)

    c1, c2 = {}, {}
    for sec in p1.keys():
        a = deepcopy(p1[sec])
        b = deepcopy(p2[sec])
        if len(a) != len(b):
            c1[sec], c2[sec] = a, b
            continue
        cut = random.randint(1, len(a)-1) if len(a) > 1 else 1
        childA = a[:cut] + b[cut:]
        childB = b[:cut] + a[cut:]
        c1[sec] = childA
        c2[sec] = childB
    return c1, c2

# ---------------- SAFE MUTATION ---------------- #

def mutate_safe(chrom: Dict[int, List[Gene]], data: GAInput, rate: float = 0.05) -> Dict[int, List[Gene]]:
    """
    Safe mutation:
     - creates new Gene objects (models.Gene is frozen)
     - tries to nudge start within same day and/or change room
     - checks conflicts using usage tables
     - prevents same subject more than once per day for a section and multiple lab-blocks per day
    """
    used_sec, used_fac, used_room, subj_day = rebuild_usage_table(chrom, data)
    pday = int(getattr(data, "periods_per_day", 0) or 0)

    for sec, arr in chrom.items():
        for idx, g in enumerate(arr):
            if random.random() >= rate:
                continue

            # choose a day-preserving new start (nudge) and a candidate room
            # determine base day
            base_day = _slot_day(g.slot_id, data)
            max_start_in_day = max(1, pday - g.block_size + 1)
            new_start = base_day * pday + random.randint(1, max_start_in_day)

            # pick candidate rooms (heuristic ordering)
            subj = data.subjects.get(g.subject_id)
            want = subj.subj_type if subj is not None else "THEORY"
            need_cap = int(getattr(data.sections[g.section_id], "student_count", 0) or 0)
            room_candidate = random_room_for(want, data, need_cap)

            # Quick checks: can_place_block and subject/day constraints
            # Temporarily remove current gene usage to allow repositioning within same day
            for k in range(g.block_size):
                s_old = g.slot_id + k
                used_sec[g.section_id].discard(s_old)
                used_fac[g.faculty_id].discard(s_old)
                used_room[g.room_id].discard(s_old)
            # reduce subj_day count for current gene day
            curr_day = _slot_day(g.slot_id, data)
            subj_day[(g.section_id, g.subject_id, curr_day)] = max(0, subj_day.get((g.section_id, g.subject_id, curr_day), 1) - 1)

            # 1) subject already scheduled same day? (disallow)
            conflict_same_subject = False
            day_new = _slot_day(new_start, data)
            # if there exists any other block for same (section,subject,day_new), we must not place
            if subj_day.get((g.section_id, g.subject_id, day_new), 0) > 0:
                conflict_same_subject = True

            # 2) if subject is LAB ensure not more than one lab-block of same subject in that day
            is_lab = (subj.subj_type if subj is not None else "THEORY").upper() == "LAB"
            if is_lab and subj_day.get((g.section_id, g.subject_id, day_new), 0) > 0:
                conflict_same_subject = True

            placed = False
            if not conflict_same_subject and can_place_block(new_start, g.block_size, room_candidate, g, data, used_sec, used_fac, used_room):
                # create a new Gene (can't mutate frozen dataclass)
                new_gene = Gene(section_id=g.section_id,
                                subject_id=g.subject_id,
                                faculty_id=g.faculty_id,
                                room_id=room_candidate,
                                slot_id=new_start,
                                block_size=g.block_size)
                arr[idx] = new_gene
                # register usage
                for k in range(new_gene.block_size):
                    s_new = new_gene.slot_id + k
                    used_sec[new_gene.section_id].add(s_new)
                    used_fac[new_gene.faculty_id].add(s_new)
                    used_room[new_gene.room_id].add(s_new)
                subj_day[(new_gene.section_id, new_gene.subject_id, day_new)] += 1
                placed = True

            if not placed:
                # revert: put back old usage & counts (no change)
                for k in range(g.block_size):
                    s_old = g.slot_id + k
                    used_sec[g.section_id].add(s_old)
                    used_fac[g.faculty_id].add(s_old)
                    used_room[g.room_id].add(s_old)
                subj_day[(g.section_id, g.subject_id, curr_day)] += 1

    return chrom

# ---------------- GA MAIN ---------------- #

def run_ga(data: GAInput,
           population_size: int = 80,
           generations: int = 300,
           tournament_k: int = 3,
           crossover_rate: float = 0.9,
           mutate_rate: float = 0.05,
           elitism_fraction: float = 0.08,
           seed = None):

    if seed is not None:
        random.seed(seed)

    # initialize
    population = [random_chromosome(data) for _ in range(population_size)]
    evals = [evaluate(c, data) for c in population]
    fits = [e["fitness"] for e in evals]

    elite_n = max(1, int(elitism_fraction * population_size))
    best = max(zip(fits, population, evals), key=lambda x: x[0])

    for gen in range(generations):
        new_pop = []

        # Elitism
        elite_idx = sorted(range(len(population)), key=lambda i: fits[i], reverse=True)[:elite_n]
        for i in elite_idx:
            new_pop.append(deepcopy(population[i]))

        # Fill remaining slots
        while len(new_pop) < population_size:
            # tournament selection
            cand_idx = random.sample(range(len(population)), k=min(tournament_k, len(population)))
            cand_idx.sort(key=lambda i: fits[i], reverse=True)
            p1 = deepcopy(population[cand_idx[0]])
            # second parent
            cand_idx2 = random.sample(range(len(population)), k=min(tournament_k, len(population)))
            cand_idx2.sort(key=lambda i: fits[i], reverse=True)
            p2 = deepcopy(population[cand_idx2[0]])

            # crossover
            c1, c2 = safe_sectionwise_crossover(p1, p2, data, rate=crossover_rate)

            # mutate safely
            mutate_safe(c1, data, rate=mutate_rate)
            mutate_safe(c2, data, rate=mutate_rate)

            new_pop.extend([c1, c2])

        population = new_pop[:population_size]
        evals = [evaluate(c, data) for c in population]
        fits = [e["fitness"] for e in evals]

        # track best
        cand = max(zip(fits, population, evals), key=lambda x: x[0])
        if cand[0] > best[0]:
            best = cand

    best_fitness, best_chrom, best_eval = best
    return {
        "best_chromosome": best_chrom,
        "fitness": best_fitness,
        "eval": best_eval,
        "generations": generations
    }