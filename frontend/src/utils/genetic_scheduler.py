import random
import time
from typing import List, Dict, Any

# --- 1. GA STRUCTURES ---

class Gene:
    """Represents a single class slot (the smallest unit of the timetable)."""
    def __init__(self, subject_id, faculty_id, room_id, time_slot_id, batch_id):
        # Yeh IDs database se aayengi
        self.subject_id = subject_id
        self.faculty_id = faculty_id
        self.room_id = room_id
        self.time_slot_id = time_slot_id
        self.batch_id = batch_id
    
    def __repr__(self):
        # Debugging ke liye
        return f"G({self.subject_id}/{self.faculty_id}/{self.room_id}/{self.time_slot_id})"

class Chromosome:
    """Represents a complete, potential timetable (a solution)."""
    def __init__(self, genes: List[Gene]):
        self.genes = genes
        self.fitness = 0.0 # Fitness value 0 se 100 tak hogi
        
    def calculate_fitness(self, constraints: Dict[str, Any]):
        """
        GA ka sabse zaroori function. Conflicts ko check karke fitness score deta hai.
        Fitness jitni zyada (100 ke kareeb), timetable utna behtar.
        """
        hard_violations = 0 # Conflicts jo allowed nahi hain (e.g., double booking)
        soft_violations = 0 # Conflicts jo adjust kiye ja sakte hain (e.g., faculty preference)

        # 1. HARD CONSTRAINTS (DB Data se check honge)
        
        # a. Double Booking: Check if a Faculty/Room/Batch is assigned to two different slots at the same time.
        slot_map = {} # Key: (time_slot_id, day_of_week), Value: (faculty_id, room_id, batch_id)
        for gene in self.genes:
            key = (gene.time_slot_id, gene.batch_id) # Example: (Slot 5, Batch CSE-B)
            
            if key in slot_map:
                # Check for same time slot conflicts
                if gene.faculty_id in slot_map[key]['faculty']:
                    hard_violations += 1 # Faculty double booked
                if gene.room_id in slot_map[key]['room']:
                    hard_violations += 1   # Room double booked
                # Batch is already covered by the key (key=batch_id)
            
            # Update the map (Simplified way to check conflicts)
            slot_map.setdefault(key, {'faculty': set(), 'room': set()})
            slot_map[key]['faculty'].add(gene.faculty_id)
            slot_map[key]['room'].add(gene.room_id)
        
        # b. Room Capacity: Check if batch size exceeds room capacity
        # c. Faculty Max Load: Check if faculty max_load (from constraints['faculty']) is exceeded
        
        # 2. SOFT CONSTRAINTS (Optional, for better timetable quality)
        # soft_violations += check_for_consecutive_classes() 
        # soft_violations += check_for_lunch_time_classes()

        # Final Fitness Calculation
        # Hard violations se fitness bahut zyada kam ho jaati hai
        self.fitness = 100 - (hard_violations * 50) - (soft_violations * 5)
        self.fitness = max(0, self.fitness) # Fitness cannot be negative
        
        return self.fitness

# --- 2. CORE GA FUNCTIONS ---

def create_initial_population(constraints: Dict[str, Any], population_size=100) -> List[Chromosome]:
    """Generates the first set of random timetables."""
    # Logic: Har subject ki required number of classes ke liye random Gene banao.
    # Har Gene ko random Faculty, random Room, aur random Time Slot assign karo.
    
    # Simple Example: Assume required_classes is a list of tuples (subject_id, batch_id, num_slots)
    # This is a complex step, needs proper structure from constraints!
    required_classes = [(1, 'B1', 5), (2, 'B1', 4), ...] 
    
    population = []
    for _ in range(population_size):
        genes = []
        for subj_id, batch_id, count in required_classes:
            for _ in range(count):
                # Randomly pick components from constraints
                random_faculty = random.choice(constraints['faculty'])['faculty_id']
                random_room = random.choice(constraints['rooms'])['room_id']
                random_slot = random.choice(constraints['slots'])['slot_id']
                
                genes.append(Gene(subj_id, random_faculty, random_room, random_slot, batch_id))
        
        population.append(Chromosome(genes))
    return population

def selection(population: List[Chromosome]):
    # Tournament selection ya Roulette wheel use karo. 
    # Best fitness waale chromosomes ko select karo.
    population.sort(key=lambda c: c.fitness, reverse=True)
    return population[:len(population)//2] # Top 50% select kiye

def crossover(parent1: Chromosome, parent2: Chromosome):
    # Two-point crossover is common. Parents ke genes mix karke naye child banao.
    # Complexity ke liye, yahan simplify kiya gaya hai.
    mid = len(parent1.genes) // 2
    child_genes = parent1.genes[:mid] + parent2.genes[mid:]
    return Chromosome(child_genes)

def mutation(chromosome: Chromosome, constraints: Dict[str, Any], mutation_rate=0.01):
    # Randomly kuch Genes (slots) ke components change kar do (e.g., room change)
    for gene in chromosome.genes:
        if random.random() < mutation_rate:
             # Example: Change room_id randomly
             gene.room_id = random.choice(constraints['rooms'])['room_id']
    return chromosome

# --- 3. THE MAIN CONTROLLER FUNCTION (The one you call from app.py) ---

def run_ga(constraints_data: Dict[str, Any]) -> List[tuple]:
    """
    Main function to run the Genetic Algorithm.
    Input: Data from MySQL (Constraints).
    Output: List of tuples ready for bulk INSERT into timetable_timetableentry.
    """
    start_time = time.time()
    GENERATIONS = 100 # Adjust this number
    
    # 1. Create Initial Population
    population = create_initial_population(constraints_data, population_size=100)
    
    for generation in range(GENERATIONS):
        # 2. Evaluate Fitness for all chromosomes
        for chromosome in population:
            chromosome.calculate_fitness(constraints_data)

        # Find the best chromosome in current generation
        best_chromosome = max(population, key=lambda c: c.fitness)
        print(f"Gen {generation}: Best Fitness = {best_chromosome.fitness:.2f}")

        if best_chromosome.fitness >= 99:
            print(f"Goal achieved in Generation {generation}!")
            break

        # 3. Selection, Crossover, Mutation to create the next generation
        new_population = selection(population)
        while len(new_population) < 100:
            parent1, parent2 = random.choices(new_population, k=2)
            child = crossover(parent1, parent2)
            child = mutation(child, constraints_data)
            new_population.append(child)
        
        population = new_population

    final_best_chromosome = max(population, key=lambda c: c.fitness)
    
    print(f"\nGA Finished in {time.time() - start_time:.2f} seconds.")
    print(f"Final Best Fitness: {final_best_chromosome.fitness:.2f}")

    # 4. Format Output for MySQL
    # Output format should be: [(subject_id, faculty_id, room_id, time_slot_id, batch_id), ...]
    mysql_insert_data = []
    for gene in final_best_chromosome.genes:
        mysql_insert_data.append((
            gene.subject_id, 
            gene.faculty_id, 
            gene.room_id, 
            gene.time_slot_id, 
            gene.batch_id
        ))
        
    return mysql_insert_data

# Note: constraints_data (global variable use karne ke liye) ko remove kiya gaya hai 
# aur use function mein pass kiya gaya hai, jo clean