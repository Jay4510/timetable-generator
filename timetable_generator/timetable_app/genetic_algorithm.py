import random
import copy
import time
from .models import Teacher, Year, Division, Room, Lab, Subject, TimeSlot, Session
from .teacher_subject_assignment import TeacherSubjectPreference, get_subject_allocation_recommendations


class Chromosome:
    """
    Represent a timetable solution as a list of genes.
    Each gene is a tuple: (subject_id, teacher_id, room_id, timeslot_id, batch_num)
    """
    
    def __init__(self, genes=None):
        self.genes = genes if genes is not None else []
        self.fitness_score = None
    
    def fitness(self):
        """Calculate fitness score based on constraint violations"""
        if self.fitness_score is not None:
            return self.fitness_score
            
        hard_violations = self.check_hard_constraints()
        soft_violations = self.check_soft_constraints()
        self.fitness_score = -(hard_violations * 1000 + soft_violations * 10)
        return self.fitness_score
    
    def check_hard_constraints(self):
        """Count all hard constraint violations"""
        violations = 0
        
        # Check 1: No teacher can teach two classes simultaneously
        teacher_timeslot_map = {}
        for gene in self.genes:
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            if (teacher_id, timeslot_id) in teacher_timeslot_map:
                violations += 1
            else:
                teacher_timeslot_map[(teacher_id, timeslot_id)] = True
        
        # Check 2: No batch can have two lectures at the same time
        batch_timeslot_map = {}
        for gene in self.genes:
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            if (batch_num, timeslot_id) in batch_timeslot_map:
                violations += 1
            else:
                batch_timeslot_map[(batch_num, timeslot_id)] = True
        
        # Check 3: No room can host two classes simultaneously
        room_timeslot_map = {}
        for gene in self.genes:
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            if room_id is not None and (room_id, timeslot_id) in room_timeslot_map:
                violations += 1
            else:
                room_timeslot_map[(room_id, timeslot_id)] = True
        
        # Check 4: Each subject must receive its required weekly sessions
        subject_session_count = {}
        for gene in self.genes:
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            if subject_id not in subject_session_count:
                subject_session_count[subject_id] = 0
            subject_session_count[subject_id] += 1
        
        # Get all subjects and their required sessions
        subjects = Subject.objects.all()
        for subject in subjects:
            required_sessions = subject.sessions_per_week
            actual_sessions = subject_session_count.get(subject.id, 0)
            if actual_sessions != required_sessions:
                violations += abs(required_sessions - actual_sessions)
        
        # Check 5: Teachers cannot exceed 14 sessions per week
        teacher_session_count = {}
        for gene in self.genes:
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            if teacher_id not in teacher_session_count:
                teacher_session_count[teacher_id] = 0
            teacher_session_count[teacher_id] += 1
        
        teachers = Teacher.objects.all()
        for teacher in teachers:
            max_sessions = teacher.max_sessions_per_week
            actual_sessions = teacher_session_count.get(teacher.id, 0)
            if actual_sessions > max_sessions:
                violations += (actual_sessions - max_sessions)
        
        # Check 7: Lab subjects must be assigned to lab rooms only
        for gene in self.genes:
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            try:
                subject = Subject.objects.get(id=subject_id)
                # A room must be assigned for any session
                if room_id is None:
                    violations += 1
                    continue

                room = Room.objects.get(id=room_id)
                
                # If subject is a lab, it must be in a lab room.
                if subject.is_lab and room.room_type != 'lab':
                    violations += 1
                # If subject is not a lab, it must be in a class room.
                elif not subject.is_lab and room.room_type != 'class':
                    violations += 1
            except (Subject.DoesNotExist, Room.DoesNotExist):
                # If we can't find the subject or room, it's a violation
                violations += 1
        
        # Check 8: Teacher-Subject preference constraints (HARD)
        # Teachers who have "refused" or are "unavailable" should not be assigned
        for gene in self.genes:
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            try:
                preference = TeacherSubjectPreference.objects.get(
                    teacher_id=teacher_id, 
                    subject_id=subject_id
                )
                if preference.preference in ['refused', 'unavailable']:
                    violations += 10  # Heavy penalty for violating teacher refusal
                elif preference.competency == 'unqualified':
                    violations += 5   # Penalty for assigning unqualified teacher
            except TeacherSubjectPreference.DoesNotExist:
                # If no preference exists, assume neutral (small penalty)
                violations += 1
        
        return violations
    
    def check_soft_constraints(self):
        """Count soft constraint violations"""
        violations = 0
        
        # Check 1: Equal distribution of sessions across all teachers
        teacher_session_count = {}
        for gene in self.genes:
            _, teacher_id, _, _, _ = gene
            teacher_session_count[teacher_id] = teacher_session_count.get(teacher_id, 0) + 1
        
        teachers = list(Teacher.objects.all())
        if teachers:
            # Ensure all teachers are in the count map, even if they have 0 sessions
            for teacher in teachers:
                if teacher.id not in teacher_session_count:
                    teacher_session_count[teacher.id] = 0

            total_sessions = sum(teacher_session_count.values())
            # Avoid division by zero if there are no teachers
            avg_sessions_per_teacher = total_sessions / len(teachers) if teachers else 0
            
            for teacher_id, count in teacher_session_count.items():
                # Penalize deviation from the average
                violations += abs(count - avg_sessions_per_teacher)

        # Check 2: Teacher-Subject preference optimization (SOFT)
        # Reward good matches, penalize poor matches
        for gene in self.genes:
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            try:
                preference = TeacherSubjectPreference.objects.get(
                    teacher_id=teacher_id, 
                    subject_id=subject_id
                )
                
                # Reward preferred assignments, penalize reluctant ones
                preference_scores = {
                    'preferred': -20,    # Negative = reward (reduces violations)
                    'willing': -10,      # Small reward
                    'reluctant': 15,     # Penalty
                    'refused': 50,       # Heavy penalty (should be caught by hard constraints)
                    'unavailable': 100,  # Very heavy penalty
                }
                
                competency_scores = {
                    'expert': -15,       # Reward expert assignments
                    'proficient': -5,    # Small reward
                    'basic': 5,          # Small penalty
                    'learning': 10,      # Penalty
                    'unqualified': 30,   # Heavy penalty
                }
                
                violations += preference_scores.get(preference.preference, 0)
                violations += competency_scores.get(preference.competency, 0)
                
                # Bonus for experience
                if preference.years_taught > 0:
                    violations -= min(preference.years_taught, 5)  # Max 5 point bonus
                    
            except TeacherSubjectPreference.DoesNotExist:
                # No preference data - neutral penalty
                violations += 5
        
        # Check 3: Minimize teacher overload beyond preferences
        teacher_subject_count = {}
        for gene in self.genes:
            subject_id, teacher_id, _, _, _ = gene
            if teacher_id not in teacher_subject_count:
                teacher_subject_count[teacher_id] = set()
            teacher_subject_count[teacher_id].add(subject_id)
        
        # Penalize teachers teaching too many different subjects
        for teacher_id, subjects in teacher_subject_count.items():
            if len(subjects) > 4:  # More than 4 different subjects
                violations += (len(subjects) - 4) * 5

        return int(violations) # Return as integer


def select_teacher_for_subject(subject, teachers):
    """
    Smart teacher selection based on preferences and competency.
    This implements the 'meeting-based allocation' logic you described.
    """
    try:
        # Get teacher preferences for this subject
        preferences = TeacherSubjectPreference.objects.filter(
            subject=subject
        ).exclude(
            preference__in=['refused', 'unavailable']
        ).order_by('-priority_score')
        
        if preferences.exists():
            # Use weighted random selection based on priority scores
            weights = []
            available_teachers = []
            
            for pref in preferences:
                if pref.teacher in teachers:  # Make sure teacher is in our list
                    # Convert priority score to positive weight
                    weight = max(1, pref.priority_score + 100)  # Ensure positive
                    weights.append(weight)
                    available_teachers.append(pref.teacher)
            
            if available_teachers:
                # Weighted random selection
                total_weight = sum(weights)
                r = random.uniform(0, total_weight)
                cumulative = 0
                
                for i, weight in enumerate(weights):
                    cumulative += weight
                    if r <= cumulative:
                        return available_teachers[i]
        
        # Fallback: random selection if no preferences found
        return random.choice(teachers) if teachers else None
        
    except Exception:
        # Fallback to random selection on any error
        return random.choice(teachers) if teachers else None


def generate_random_chromosome():
    """Generate a random timetable chromosome"""
    # Get all required data
    subjects = list(Subject.objects.all())
    teachers = list(Teacher.objects.all())
    rooms = list(Room.objects.all())
    labs = list(Lab.objects.all())
    timeslots = list(TimeSlot.objects.all())
    
    # For this example, we'll create a simplified chromosome
    # In a real implementation, this would be much more complex
    genes = []
    
    # For each subject, create the required number of sessions
    for subject in subjects:
        for _ in range(subject.sessions_per_week):
            # Select teacher based on preferences (smart selection)
            teacher = select_teacher_for_subject(subject, teachers)
            
            # Select room or lab based on subject type
            if subject.is_lab:
                # For lab subjects, we need to use lab rooms (which are stored as Room objects with room_type='lab')
                lab_rooms = [r for r in rooms if r.room_type == 'lab']
                room = random.choice(lab_rooms) if lab_rooms else None
            else:
                # For regular subjects, use classroom rooms
                class_rooms = [r for r in rooms if r.room_type == 'class']
                room = random.choice(class_rooms) if class_rooms else None
            
            # Randomly select a timeslot
            timeslot = random.choice(timeslots) if timeslots else None
            
            # For batch number, we'll use a random number between 1-3
            batch_num = random.randint(1, 3)
            
            # Create gene
            gene = (
                subject.id,
                teacher.id if teacher else None,
                room.id if room else None,
                timeslot.id if timeslot else None,
                batch_num
            )
            genes.append(gene)
    
    return Chromosome(genes)


def tournament_selection(population, tournament_size=5):
    """Select parents using tournament selection"""
    parents = []
    for _ in range(len(population)):
        # Select random individuals for tournament
        tournament = random.sample(population, min(tournament_size, len(population)))
        # Select the best individual from tournament
        winner = max(tournament, key=lambda x: x.fitness())
        parents.append(copy.deepcopy(winner))
    return parents


def single_point_crossover(parent1, parent2):
    """Perform single point crossover"""
    if not parent1.genes or not parent2.genes:
        return copy.deepcopy(parent1), copy.deepcopy(parent2)
    
    # Select crossover point
    crossover_point = random.randint(1, min(len(parent1.genes), len(parent2.genes)) - 1)
    
    # Create children
    child1_genes = parent1.genes[:crossover_point] + parent2.genes[crossover_point:]
    child2_genes = parent2.genes[:crossover_point] + parent1.genes[crossover_point:]
    
    child1 = Chromosome(child1_genes)
    child2 = Chromosome(child2_genes)
    
    return child1, child2


def mutate(chromosome, mutation_rate=0.1):
    """Mutate a chromosome by randomly changing genes"""
    if not chromosome.genes:
        return
    
    # Get all required data for mutations
    teachers = list(Teacher.objects.all())
    rooms = list(Room.objects.all())
    labs = list(Lab.objects.all())
    timeslots = list(TimeSlot.objects.all())
    
    for i in range(len(chromosome.genes)):
        if random.random() < mutation_rate:
            gene = chromosome.genes[i]
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            
            # Randomly mutate one component of the gene
            mutation_type = random.randint(1, 5)
            
            try:
                if mutation_type == 1 and teachers:  # Mutate teacher
                    new_teacher = random.choice(teachers)
                    chromosome.genes[i] = (
                        subject_id,
                        new_teacher.id,
                        room_id,
                        timeslot_id,
                        batch_num
                    )
                elif mutation_type == 2 and rooms:  # Mutate room
                    subject = Subject.objects.get(id=subject_id)
                    if subject.is_lab:
                        lab_rooms = [r for r in rooms if r.room_type == 'lab']
                        new_room = random.choice(lab_rooms) if lab_rooms else None
                    else:
                        class_rooms = [r for r in rooms if r.room_type == 'class']
                        new_room = random.choice(class_rooms) if class_rooms else None
                    if new_room:
                        chromosome.genes[i] = (
                            subject_id,
                            teacher_id,
                            new_room.id,
                            timeslot_id,
                            batch_num
                        )
                elif mutation_type == 3 and timeslots:  # Mutate timeslot
                    new_timeslot = random.choice(timeslots)
                    chromosome.genes[i] = (
                        subject_id,
                        teacher_id,
                        room_id,
                        new_timeslot.id,
                        batch_num
                    )
                elif mutation_type == 4:  # Mutate batch number
                    new_batch = random.randint(1, 3)
                    chromosome.genes[i] = (
                        subject_id,
                        teacher_id,
                        room_id,
                        timeslot_id,
                        new_batch
                    )
            except Subject.DoesNotExist:
                # If we can't find the subject, skip mutation
                pass


def select_best(population, num_to_select):
    """Select the best individuals from population"""
    # Sort population by fitness (descending order)
    sorted_population = sorted(population, key=lambda x: x.fitness(), reverse=True)
    return sorted_population[:num_to_select]


class GeneticAlgorithm:
    def __init__(self, population_size=50, generations=100, mutation_rate=0.2, elite_size=2):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.elite_size = elite_size

    def initialize_population(self):
        """Create initial population of random chromosomes"""
        population = []
        for _ in range(self.population_size):
            chromosome = generate_random_chromosome()
            population.append(chromosome)
        return population

    def evolve(self, population):
        """Evolve the population for one generation"""
        # Selection
        parents = tournament_selection(population)
        
        # Crossover and mutation
        offspring = []
        for i in range(0, len(parents) - 1, 2):
            parent1 = parents[i]
            parent2 = parents[i + 1]
            
            # Crossover
            if random.random() < 0.8:  # 80% crossover rate
                child1, child2 = single_point_crossover(parent1, parent2)
            else:
                child1 = copy.deepcopy(parent1)
                child2 = copy.deepcopy(parent2)
            
            # Mutation
            mutate(child1, self.mutation_rate)
            mutate(child2, self.mutation_rate)
            
            # Reset fitness scores for children
            child1.fitness_score = None
            child2.fitness_score = None
            
            offspring.extend([child1, child2])
        
        # Elitism - keep best individuals
        elite = select_best(population, self.elite_size)
        
        # Combine elite with offspring and select best
        combined = elite + offspring
        new_population = select_best(combined, self.population_size)
        
        return new_population

    def calculate_fitness(self, chromosome):
        """Calculate fitness of a chromosome"""
        return chromosome.fitness()

    def run(self):
        """Run the genetic algorithm"""
        population = self.initialize_population()
        best_fitness = float('-inf')
        no_improvement = 0
        
        for generation in range(self.generations):
            population = self.evolve(population)
            current_best = max(population, key=self.calculate_fitness)
            current_fitness = self.calculate_fitness(current_best)
            
            # Early stopping if no improvement for 10 generations
            if current_fitness > best_fitness:
                best_fitness = current_fitness
                no_improvement = 0
            else:
                no_improvement += 1
                if no_improvement >= 10 and generation > 20:  # Don't stop too early
                    print(f"Early stopping at generation {generation+1}")
                    break
                    
            # Print progress
            if generation % 5 == 0:
                print(f"Generation {generation+1}/{self.generations}, Best Fitness: {best_fitness:.2f}")
                
        return max(population, key=self.calculate_fitness)


class MultiAlgorithmOptimizer:
    """
    Enhanced optimizer that combines multiple algorithms for better results.
    This implements Phase 1 of our enhancement plan.
    """
    
    def __init__(self):
        self.algorithms = {
            'genetic': GeneticAlgorithm,
            'hybrid_genetic': HybridGeneticAlgorithm,
            'simulated_annealing': SimulatedAnnealingOptimizer
        }
        self.performance_history = []
        
    def optimize_timetable(self, constraints=None, time_limit=300):
        """
        Run multi-algorithm optimization with intelligent algorithm selection
        """
        print("Starting Multi-Algorithm Optimization...")
        
        # Analyze problem characteristics
        problem_profile = self.analyze_problem_complexity(constraints)
        print(f"Problem complexity: {problem_profile['complexity_level']}")
        
        # Select algorithm sequence based on problem profile
        algorithm_sequence = self.select_algorithm_sequence(problem_profile)
        print(f"Selected algorithms: {algorithm_sequence}")
        
        best_solution = None
        best_fitness = float('-inf')
        start_time = time.time()
        
        for algorithm_name in algorithm_sequence:
            if time.time() - start_time > time_limit:
                print(f"Time limit reached, stopping optimization")
                break
                
            print(f"\n--- Running {algorithm_name.upper()} Algorithm ---")
            
            try:
                # Get algorithm parameters based on problem profile
                params = self.get_algorithm_parameters(algorithm_name, problem_profile)
                
                # Initialize algorithm
                if algorithm_name == 'genetic':
                    algorithm = GeneticAlgorithm(**params)
                elif algorithm_name == 'hybrid_genetic':
                    algorithm = self.create_hybrid_genetic_algorithm(params)
                elif algorithm_name == 'simulated_annealing':
                    algorithm = self.create_simulated_annealing(params)
                
                # Run algorithm
                solution = algorithm.run()
                fitness = algorithm.calculate_fitness(solution)
                
                print(f"{algorithm_name} fitness: {fitness}")
                
                # Update best solution
                if fitness > best_fitness:
                    best_solution = solution
                    best_fitness = fitness
                    print(f"New best solution found! Fitness: {fitness}")
                
                # Record performance
                self.record_performance(algorithm_name, fitness, problem_profile)
                
                # Early termination if perfect solution found
                if fitness >= 0:  # No violations
                    print(f"Perfect solution found with {algorithm_name}!")
                    break
                    
            except Exception as e:
                print(f"Algorithm {algorithm_name} failed: {e}")
                continue
        
        total_time = time.time() - start_time
        print(f"\nOptimization completed in {total_time:.2f} seconds")
        print(f"Best fitness achieved: {best_fitness}")
        
        return {
            'solution': best_solution,
            'fitness': best_fitness,
            'optimization_time': total_time,
            'algorithms_used': algorithm_sequence
        }
    
    def analyze_problem_complexity(self, constraints):
        """Analyze problem characteristics to guide algorithm selection"""
        from .models import Teacher, Subject, Room, TimeSlot
        
        # Get problem dimensions
        num_teachers = Teacher.objects.count()
        num_subjects = Subject.objects.count()
        num_rooms = Room.objects.count()
        num_timeslots = TimeSlot.objects.count()
        
        # Calculate complexity metrics
        total_variables = num_subjects * 5  # Each subject has 5 variables in gene
        search_space_size = num_teachers * num_rooms * num_timeslots * 3  # 3 batches
        constraint_density = len(constraints) if constraints else 10
        
        # Determine complexity level
        if total_variables < 100 and search_space_size < 10000:
            complexity_level = 'low'
        elif total_variables < 500 and search_space_size < 100000:
            complexity_level = 'medium'
        else:
            complexity_level = 'high'
        
        return {
            'complexity_level': complexity_level,
            'num_teachers': num_teachers,
            'num_subjects': num_subjects,
            'num_rooms': num_rooms,
            'num_timeslots': num_timeslots,
            'total_variables': total_variables,
            'search_space_size': search_space_size,
            'constraint_density': constraint_density
        }
    
    def select_algorithm_sequence(self, problem_profile):
        """Select optimal algorithm sequence based on problem characteristics"""
        complexity = problem_profile['complexity_level']
        
        if complexity == 'low':
            # For simple problems, genetic algorithm alone is sufficient
            return ['genetic']
        elif complexity == 'medium':
            # For medium problems, use genetic + simulated annealing
            return ['genetic', 'simulated_annealing']
        else:
            # For complex problems, use full sequence
            return ['genetic', 'hybrid_genetic', 'simulated_annealing']
    
    def get_algorithm_parameters(self, algorithm_name, problem_profile):
        """Get optimal parameters for each algorithm based on problem profile"""
        complexity = problem_profile['complexity_level']
        
        if algorithm_name == 'genetic':
            if complexity == 'low':
                return {'population_size': 30, 'generations': 50, 'mutation_rate': 0.1}
            elif complexity == 'medium':
                return {'population_size': 50, 'generations': 100, 'mutation_rate': 0.15}
            else:
                return {'population_size': 100, 'generations': 200, 'mutation_rate': 0.2}
        
        elif algorithm_name == 'hybrid_genetic':
            return {
                'population_size': min(100, problem_profile['total_variables']),
                'generations': 150,
                'mutation_rate': 0.2,
                'elite_ratio': 0.1
            }
        
        elif algorithm_name == 'simulated_annealing':
            return {
                'initial_temp': 1000,
                'cooling_rate': 0.95,
                'min_temp': 1,
                'max_iterations': 5000
            }
        
        return {}
    
    def create_hybrid_genetic_algorithm(self, params):
        """Create enhanced genetic algorithm with adaptive features"""
        class AdaptiveGeneticAlgorithm(GeneticAlgorithm):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.adaptive_mutation = True
                self.diversity_threshold = 0.1
                
            def run(self):
                """Enhanced run method with adaptive features"""
                population = self.initialize_population()
                best_fitness = float('-inf')
                no_improvement = 0
                diversity_history = []
                
                for generation in range(self.generations):
                    # Calculate population diversity
                    diversity = self.calculate_diversity(population)
                    diversity_history.append(diversity)
                    
                    # Adaptive mutation rate based on diversity
                    if self.adaptive_mutation:
                        if diversity < self.diversity_threshold:
                            self.mutation_rate = min(0.5, self.mutation_rate * 1.2)
                        else:
                            self.mutation_rate = max(0.05, self.mutation_rate * 0.9)
                    
                    population = self.evolve(population)
                    current_best = max(population, key=self.calculate_fitness)
                    current_fitness = self.calculate_fitness(current_best)
                    
                    # Enhanced early stopping
                    if current_fitness > best_fitness:
                        best_fitness = current_fitness
                        no_improvement = 0
                    else:
                        no_improvement += 1
                        if no_improvement >= 15 and generation > 30:
                            print(f"Early stopping at generation {generation+1}")
                            break
                    
                    # Progress reporting
                    if generation % 10 == 0:
                        print(f"Generation {generation+1}/{self.generations}, "
                              f"Best Fitness: {best_fitness:.2f}, "
                              f"Diversity: {diversity:.3f}, "
                              f"Mutation Rate: {self.mutation_rate:.3f}")
                
                return max(population, key=self.calculate_fitness)
            
            def calculate_diversity(self, population):
                """Calculate population diversity"""
                if len(population) < 2:
                    return 1.0
                
                total_distance = 0
                comparisons = 0
                
                for i in range(len(population)):
                    for j in range(i + 1, len(population)):
                        distance = self.hamming_distance(population[i], population[j])
                        total_distance += distance
                        comparisons += 1
                
                return total_distance / comparisons if comparisons > 0 else 0
            
            def hamming_distance(self, chromosome1, chromosome2):
                """Calculate Hamming distance between two chromosomes"""
                if len(chromosome1.genes) != len(chromosome2.genes):
                    return 1.0
                
                differences = sum(1 for g1, g2 in zip(chromosome1.genes, chromosome2.genes) if g1 != g2)
                return differences / len(chromosome1.genes)
        
        return AdaptiveGeneticAlgorithm(**params)
    
    def create_simulated_annealing(self, params):
        """Create simulated annealing optimizer"""
        class TimetableSimulatedAnnealing:
            def __init__(self, initial_temp=1000, cooling_rate=0.95, min_temp=1, max_iterations=5000):
                self.initial_temp = initial_temp
                self.cooling_rate = cooling_rate
                self.min_temp = min_temp
                self.max_iterations = max_iterations
            
            def run(self):
                """Run simulated annealing optimization"""
                import math
                
                # Start with a random solution
                current_solution = generate_random_chromosome()
                current_fitness = current_solution.fitness()
                
                best_solution = copy.deepcopy(current_solution)
                best_fitness = current_fitness
                
                temperature = self.initial_temp
                
                for iteration in range(self.max_iterations):
                    if temperature < self.min_temp:
                        break
                    
                    # Generate neighbor solution
                    neighbor = self.generate_neighbor(current_solution)
                    neighbor_fitness = neighbor.fitness()
                    
                    # Accept or reject neighbor
                    if self.should_accept(current_fitness, neighbor_fitness, temperature):
                        current_solution = neighbor
                        current_fitness = neighbor_fitness
                        
                        # Update best solution
                        if neighbor_fitness > best_fitness:
                            best_solution = copy.deepcopy(neighbor)
                            best_fitness = neighbor_fitness
                    
                    # Cool down
                    temperature *= self.cooling_rate
                    
                    # Progress reporting
                    if iteration % 500 == 0:
                        print(f"SA Iteration {iteration}, Best Fitness: {best_fitness:.2f}, Temp: {temperature:.2f}")
                
                return best_solution
            
            def generate_neighbor(self, solution):
                """Generate a neighbor solution by making small changes"""
                neighbor = copy.deepcopy(solution)
                
                # Randomly modify 1-3 genes
                num_changes = random.randint(1, 3)
                for _ in range(num_changes):
                    if neighbor.genes:
                        mutate(neighbor, mutation_rate=0.1)
                
                return neighbor
            
            def should_accept(self, current_fitness, neighbor_fitness, temperature):
                """Decide whether to accept a neighbor solution"""
                if neighbor_fitness > current_fitness:
                    return True
                
                if temperature <= 0:
                    return False
                
                # Calculate acceptance probability
                delta = neighbor_fitness - current_fitness
                probability = math.exp(delta / temperature)
                return random.random() < probability
            
            def calculate_fitness(self, chromosome):
                """Calculate fitness of a chromosome"""
                return chromosome.fitness()
        
        return TimetableSimulatedAnnealing(**params)
    
    def record_performance(self, algorithm_name, fitness, problem_profile):
        """Record algorithm performance for future optimization"""
        performance_record = {
            'algorithm': algorithm_name,
            'fitness': fitness,
            'problem_complexity': problem_profile['complexity_level'],
            'timestamp': time.time()
        }
        
        self.performance_history.append(performance_record)
        
        # Keep only recent history (last 100 records)
        if len(self.performance_history) > 100:
            self.performance_history = self.performance_history[-100:]


# Enhanced constraint checking with advanced features
class AdvancedConstraintChecker:
    """
    Advanced constraint checking system that handles complex real-world constraints
    """
    
    def __init__(self):
        self.constraint_weights = {
            'hard': 1000,
            'soft': 10,
            'preference': 1
        }
    
    def check_all_constraints(self, chromosome):
        """Check all constraints with detailed reporting"""
        violations = {
            'hard': [],
            'soft': [],
            'preference': [],
            'total_score': 0
        }
        
        # Hard constraints
        hard_violations = self.check_hard_constraints_detailed(chromosome)
        violations['hard'] = hard_violations
        violations['total_score'] -= len(hard_violations) * self.constraint_weights['hard']
        
        # Soft constraints
        soft_violations = self.check_soft_constraints_detailed(chromosome)
        violations['soft'] = soft_violations
        violations['total_score'] -= len(soft_violations) * self.constraint_weights['soft']
        
        # Preference constraints
        preference_violations = self.check_preference_constraints(chromosome)
        violations['preference'] = preference_violations
        violations['total_score'] -= len(preference_violations) * self.constraint_weights['preference']
        
        return violations
    
    def check_hard_constraints_detailed(self, chromosome):
        """Check hard constraints with detailed violation reporting"""
        violations = []
        
        # Teacher conflicts
        teacher_schedule = {}
        for i, gene in enumerate(chromosome.genes):
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            key = (teacher_id, timeslot_id)
            
            if key in teacher_schedule:
                violations.append({
                    'type': 'teacher_conflict',
                    'description': f'Teacher {teacher_id} has conflicting sessions',
                    'gene_indices': [teacher_schedule[key], i],
                    'severity': 'critical'
                })
            else:
                teacher_schedule[key] = i
        
        # Room conflicts
        room_schedule = {}
        for i, gene in enumerate(chromosome.genes):
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            if room_id:
                key = (room_id, timeslot_id)
                
                if key in room_schedule:
                    violations.append({
                        'type': 'room_conflict',
                        'description': f'Room {room_id} has conflicting sessions',
                        'gene_indices': [room_schedule[key], i],
                        'severity': 'critical'
                    })
                else:
                    room_schedule[key] = i
        
        # Add more detailed constraint checks here...
        
        return violations
    
    def check_soft_constraints_detailed(self, chromosome):
        """Check soft constraints with detailed reporting"""
        violations = []
        
        # Teacher workload balance
        teacher_loads = {}
        for gene in chromosome.genes:
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            teacher_loads[teacher_id] = teacher_loads.get(teacher_id, 0) + 1
        
        if teacher_loads:
            avg_load = sum(teacher_loads.values()) / len(teacher_loads)
            for teacher_id, load in teacher_loads.items():
                if abs(load - avg_load) > 3:  # Threshold for imbalance
                    violations.append({
                        'type': 'workload_imbalance',
                        'description': f'Teacher {teacher_id} has unbalanced workload: {load} vs avg {avg_load:.1f}',
                        'teacher_id': teacher_id,
                        'severity': 'medium'
                    })
        
        return violations
    
    def check_preference_constraints(self, chromosome):
        """Check preference-based constraints"""
        violations = []
        
        # Check teacher-subject preferences
        for gene in chromosome.genes:
            subject_id, teacher_id, room_id, timeslot_id, batch_num = gene
            
            try:
                from .teacher_subject_assignment import TeacherSubjectPreference
                preference = TeacherSubjectPreference.objects.get(
                    teacher_id=teacher_id,
                    subject_id=subject_id
                )
                
                if preference.preference == 'reluctant':
                    violations.append({
                        'type': 'teacher_reluctance',
                        'description': f'Teacher {teacher_id} is reluctant to teach subject {subject_id}',
                        'teacher_id': teacher_id,
                        'subject_id': subject_id,
                        'severity': 'low'
                    })
                    
            except:
                # No preference data available
                pass
        
        return violations


class HybridGeneticAlgorithm(GeneticAlgorithm):
    """
    Hybrid Genetic Algorithm that combines GA with local search optimization.
    This provides better convergence for complex timetabling problems.
    """
    
    def __init__(self, population_size=100, max_generations=300, mutation_rate=0.15, crossover_rate=0.85):
        super().__init__(population_size, max_generations, mutation_rate, crossover_rate)
        self.local_search_probability = 0.3
        
    def run(self):
        """Run hybrid genetic algorithm with local search"""
        print("Starting Hybrid Genetic Algorithm...")
        
        # Initialize population
        population = self.initialize_population()
        
        for generation in range(self.max_generations):
            # Evaluate fitness
            fitness_scores = [self.calculate_fitness(individual) for individual in population]
            
            # Check for early termination
            best_fitness = max(fitness_scores)
            if best_fitness >= 0:  # Perfect solution found
                best_individual = population[fitness_scores.index(best_fitness)]
                print(f"Perfect solution found at generation {generation}")
                return best_individual
            
            # Selection
            new_population = []
            for _ in range(self.population_size):
                parent1 = self.tournament_selection(population)
                parent2 = self.tournament_selection(population)
                
                # Crossover
                if random.random() < self.crossover_rate:
                    child = self.crossover(parent1, parent2)
                else:
                    child = copy.deepcopy(parent1)
                
                # Mutation
                if random.random() < self.mutation_rate:
                    child = self.mutate(child)
                
                # Local search with probability
                if random.random() < self.local_search_probability:
                    child = self.local_search(child)
                
                new_population.append(child)
            
            population = new_population
            
            if generation % 50 == 0:
                print(f"Generation {generation}, Best fitness: {best_fitness}")
        
        # Return best solution
        fitness_scores = [self.calculate_fitness(individual) for individual in population]
        best_individual = population[fitness_scores.index(max(fitness_scores))]
        return best_individual
    
    def local_search(self, chromosome):
        """Apply local search to improve the chromosome"""
        improved = copy.deepcopy(chromosome)
        
        # Try swapping random genes to improve fitness
        for _ in range(5):  # Limited number of local search steps
            if len(improved.genes) < 2:
                break
                
            # Select two random genes to swap
            i, j = random.sample(range(len(improved.genes)), 2)
            
            # Create a copy and swap
            test_chromosome = copy.deepcopy(improved)
            test_chromosome.genes[i], test_chromosome.genes[j] = test_chromosome.genes[j], test_chromosome.genes[i]
            
            # Keep the swap if it improves fitness
            if self.calculate_fitness(test_chromosome) > self.calculate_fitness(improved):
                improved = test_chromosome
        
        return improved


class SimulatedAnnealingOptimizer:
    """
    Simulated Annealing optimizer for timetable generation.
    Good for escaping local optima in complex constraint problems.
    """
    
    def __init__(self, initial_temperature=1000, cooling_rate=0.95, min_temperature=1, max_iterations=1000):
        self.initial_temperature = initial_temperature
        self.cooling_rate = cooling_rate
        self.min_temperature = min_temperature
        self.max_iterations = max_iterations
        
    def run(self):
        """Run simulated annealing optimization"""
        print("Starting Simulated Annealing Optimization...")
        
        # Initialize with a random solution
        ga = GeneticAlgorithm(population_size=1, max_generations=1)
        current_solution = ga.initialize_population()[0]
        current_fitness = self.calculate_fitness(current_solution)
        
        best_solution = copy.deepcopy(current_solution)
        best_fitness = current_fitness
        
        temperature = self.initial_temperature
        
        for iteration in range(self.max_iterations):
            if temperature < self.min_temperature:
                break
            
            # Generate neighbor solution
            neighbor = self.generate_neighbor(current_solution)
            neighbor_fitness = self.calculate_fitness(neighbor)
            
            # Accept or reject the neighbor
            if self.accept_solution(current_fitness, neighbor_fitness, temperature):
                current_solution = neighbor
                current_fitness = neighbor_fitness
                
                # Update best solution
                if neighbor_fitness > best_fitness:
                    best_solution = copy.deepcopy(neighbor)
                    best_fitness = neighbor_fitness
                    print(f"New best fitness: {best_fitness} at iteration {iteration}")
            
            # Cool down
            temperature *= self.cooling_rate
            
            if iteration % 100 == 0:
                print(f"Iteration {iteration}, Temperature: {temperature:.2f}, Current fitness: {current_fitness}")
        
        print(f"Simulated Annealing completed. Best fitness: {best_fitness}")
        return best_solution
    
    def generate_neighbor(self, solution):
        """Generate a neighbor solution by making small changes"""
        neighbor = copy.deepcopy(solution)
        
        if len(neighbor.genes) == 0:
            return neighbor
        
        # Randomly modify 1-3 genes
        num_changes = random.randint(1, min(3, len(neighbor.genes)))
        
        for _ in range(num_changes):
            gene_index = random.randint(0, len(neighbor.genes) - 1)
            
            # Get available options for modification
            teachers = list(Teacher.objects.all())
            rooms = list(Room.objects.all())
            timeslots = list(TimeSlot.objects.all())
            
            if teachers and rooms and timeslots:
                # Modify the gene
                subject_id, _, _, _, batch_num = neighbor.genes[gene_index]
                new_teacher = random.choice(teachers)
                new_room = random.choice(rooms)
                new_timeslot = random.choice(timeslots)
                
                neighbor.genes[gene_index] = (subject_id, new_teacher.id, new_room.id, new_timeslot.id, batch_num)
        
        return neighbor
    
    def accept_solution(self, current_fitness, neighbor_fitness, temperature):
        """Decide whether to accept the neighbor solution"""
        if neighbor_fitness > current_fitness:
            return True
        
        # Accept worse solution with probability based on temperature
        if temperature > 0:
            probability = random.random()
            threshold = pow(2.718, (neighbor_fitness - current_fitness) / temperature)
            return probability < threshold
        
        return False
    
    def calculate_fitness(self, chromosome):
        """Calculate fitness score for the chromosome"""
        return chromosome.fitness()