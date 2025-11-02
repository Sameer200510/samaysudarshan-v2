import random

POPULATION_SIZE = 100
GENERATIONS = 500
MUTATION_RATE = 0.1
PERFECT_FITNESS_SCORE = 1000



class Gene:
    def __init__(self, subject_id, faculty_id, room_id, batch_id, time_slot_id):
        self.subject_id = subject_id
        self.faculty_id = faculty_id
        self.room_id = room_id
        self.batch_id = batch_id
        self.time_slot_id = time_slot_id


       
        
    def __repr__(self):
        return f"Gene({self.subject_id}-{self.time_slot_id})"

class Chromosome:
    def __init__(self, genes):
        self.genes = genes
        self.fitness = 0
        
    def calculate_fitness(self, hard_constraints, soft_constraints):
        score = 0
        
         # hard constraint

        time_slot_usage = {}
        for gene in self.genes:
            key = (gene.time_slot_id, gene.room_id)
            if key in time_slot_usage:
                score -= 500
            time_slot_usage[key] = True

        self.fitness = max(1, score)

         # soft constraint

    def __repr__(self):
        return f"Chromosome(Fitness: {self.fitness})"


def initialize_population(initial_data, size):
    population = []
    for _ in range(size):
        random_genes = list(initial_data)
        random.shuffle(random_genes)
        population.append(Chromosome(random_genes))
    return population

def selection(population):
    population.sort(key=lambda x: x.fitness, reverse=True)
    return population[:int(POPULATION_SIZE * 0.2)]

def crossover(parent1, parent2):
    split_point = random.randint(1, len(parent1.genes) - 1)
    child_genes = parent1.genes[:split_point] + parent2.genes[split_point:]
    return Chromosome(child_genes)

def mutate(chromosome):
    if random.random() < MUTATION_RATE:
        index_to_mutate = random.randint(0, len(chromosome.genes) - 1)
        swap_index = random.randint(0, len(chromosome.genes) - 1)
        chromosome.genes[index_to_mutate], chromosome.genes[swap_index] = \
            chromosome.genes[swap_index], chromosome.genes[index_to_mutate]
        

# scheduler

def run_genetic_algorithm(data_from_db):
    initial_genes = [
        Gene('TCS503', 'F01', 'CR7', 'CSEB1', 'T1'),
        Gene('TCS597', 'F02', 'LAB1', 'CYSB1', 'T2'),
    ]

    population = initialize_population(initial_genes, POPULATION_SIZE)
    
    for generation in range(GENERATIONS):
        for chromosome in population:
            chromosome.calculate_fitness(hard_constraints={}, soft_constraints={})
        
        best_chromosome = max(population, key=lambda x: x.fitness)
        if best_chromosome.fitness >= PERFECT_FITNESS_SCORE:
            return best_chromosome
            
        fittest_parents = selection(population)
        
        new_population = []
        while len(new_population) < POPULATION_SIZE:
            p1, p2 = random.choices(fittest_parents, k=2)
            child = crossover(p1, p2)
            mutate(child)
            new_population.append(child)
            
        population = new_population

    return best_chromosome

if __name__ == '__main__':
    best_schedule = run_genetic_algorithm(data_from_db=None)