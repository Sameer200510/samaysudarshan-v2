# timetable_ga/ga.py
import random
from typing import Dict, List, Tuple
from copy import deepcopy
from .models import Gene, GAInput
from .initializer import random_chromosome
from .fitness import evaluate

def tournament(pop, fitnesses, k=3):
    cand = random.sample(range(len(pop)), k=min(k, len(pop)))
    cand.sort(key=lambda i: fitnesses[i], reverse=True)
    return pop[cand[0]]

def sectionwise_crossover(p1: Dict[int,List[Gene]], p2: Dict[int,List[Gene]], rate=0.9):
    if random.random() > rate:
        return deepcopy(p1), deepcopy(p2)
    c1, c2 = {}, {}
    for sec in p1.keys():
        a = p1[sec]
        b = p2[sec]
        if len(a) != len(b):
            # should be identical demand length per section
            a, b = deepcopy(a), deepcopy(b)
            c1[sec], c2[sec] = a, b
            continue
        # single-point cut on gene order
        cut = random.randint(1, len(a)-1) if len(a) > 1 else 1
        c1[sec] = a[:cut] + b[cut:]
        c2[sec] = b[:cut] + a[cut:]
    return c1, c2

def mutate_swap_in_section(chrom: Dict[int,List[Gene]], rate=0.10):
    for sec, arr in chrom.items():
        if random.random() < rate and len(arr) > 1:
            i, j = random.sample(range(len(arr)), 2)
            arr[i], arr[j] = arr[j], arr[i]

def mutate_perturb(chrom: Dict[int,List[Gene]], data: GAInput, rate=0.05):
    # small chance: random new slot or room
    for sec, arr in chrom.items():
        for idx, g in enumerate(arr):
            if random.random() < rate:
                # 50/50 slot or room tweak
                if random.random() < 0.5:
                    # nudge within same day if possible
                    pday = data.periods_per_day
                    base_day = (g.slot_id - 1)//pday
                    new_start = base_day*pday + random.randint(1, pday - g.block_size + 1)
                    arr[idx] = Gene(g.section_id, g.subject_id, g.faculty_id, g.room_id, new_start, g.block_size)
                else:
                    # room flip among valid type & capacity
                    from .initializer import random_room_for
                    subj_type = 'LAB' if g.block_size > 1 else 'THEORY'
                    size = data.sections[g.section_id].student_count
                    nr = random_room_for(subj_type, data, size)
                    arr[idx] = Gene(g.section_id, g.subject_id, g.faculty_id, nr, g.slot_id, g.block_size)

def run_ga(data: GAInput,
           population_size=100,
           generations=500,
           tournament_k=3,
           crossover_rate=0.9,
           swap_rate=0.10,
           perturb_rate=0.05,
           elitism_fraction=0.05,
           seed=None):
    if seed is not None:
        random.seed(seed)

    # init
    population = [random_chromosome(data) for _ in range(population_size)]
    evals = [evaluate(c, data) for c in population]
    fits = [e["fitness"] for e in evals]

    elite_n = max(1, int(elitism_fraction * population_size))
    best = max(zip(fits, population, evals), key=lambda x: x[0])

    for gen in range(1, generations+1):
        new_pop = []

        # Elitism
        elite_idx = sorted(range(len(population)), key=lambda i: fits[i], reverse=True)[:elite_n]
        for i in elite_idx:
            new_pop.append(deepcopy(population[i]))

        # Fill rest
        while len(new_pop) < population_size:
            p1 = tournament(population, fits, k=tournament_k)
            p2 = tournament(population, fits, k=tournament_k)
            c1, c2 = sectionwise_crossover(p1, p2, rate=crossover_rate)
            mutate_swap_in_section(c1, rate=swap_rate)
            mutate_swap_in_section(c2, rate=swap_rate)
            mutate_perturb(c1, data, rate=perturb_rate)
            mutate_perturb(c2, data, rate=perturb_rate)
            new_pop.extend([c1, c2])

        # trim
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