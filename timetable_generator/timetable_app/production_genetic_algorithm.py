"""
PRODUCTION-READY GENETIC ALGORITHM
Implements ALL 11 logic requirements for production deployment
"""

import random
import copy
from collections import defaultdict, Counter
from .models import Teacher, Subject, Room, Lab, TimeSlot, Session, Year, Division

class ProductionChromosome:
    def __init__(self, genes=None):
        self.genes = genes if genes is not None else []
        self.fitness_score = None
        self.constraint_violations = {}
    
    def fitness(self):
        """Calculate fitness based on ALL 11 production requirements"""
        if self.fitness_score is not None:
            return self.fitness_score
        
        violations = 0
        self.constraint_violations = {}
        
        # REQUIREMENT 1: More or less equal load is given to all faculties
        teacher_loads = defaultdict(int)
        for gene in self.genes:
            teacher_loads[gene[1]] += 1
        
        if teacher_loads:
            loads = list(teacher_loads.values())
            load_variance = max(loads) - min(loads) if loads else 0
            load_violations = max(0, load_variance - 3) * 5  # Allow max 3 session difference
            violations += load_violations
            self.constraint_violations['unequal_faculty_load'] = load_violations
        
        # REQUIREMENT 2: Required sessions per week for every batch
        division_sessions = defaultdict(int)
        for gene in self.genes:
            try:
                subject = Subject.objects.get(id=gene[0])
                division_key = f"{subject.year.name}_{subject.division.name}"
                division_sessions[division_key] += 1
            except:
                pass
        
        insufficient_sessions = 0
        for division, count in division_sessions.items():
            if count < 8:  # Minimum 8 sessions per division per week
                insufficient_sessions += (8 - count) * 3
        violations += insufficient_sessions
        self.constraint_violations['insufficient_sessions'] = insufficient_sessions
        
        # REQUIREMENT 3 & 5: No faculty taking two classes simultaneously
        teacher_conflicts = 0
        teacher_schedule = defaultdict(list)
        for gene in self.genes:
            teacher_schedule[gene[1]].append(gene[3])
        
        for teacher_id, timeslots in teacher_schedule.items():
            timeslot_counts = Counter(timeslots)
            for count in timeslot_counts.values():
                if count > 1:
                    teacher_conflicts += (count - 1) * 20  # Heavy penalty
        violations += teacher_conflicts
        self.constraint_violations['teacher_conflicts'] = teacher_conflicts
        
        # REQUIREMENT 4 & 6: No student group having multiple lectures at same time
        student_conflicts = 0
        division_schedule = defaultdict(list)
        
        for gene in self.genes:
            try:
                subject = Subject.objects.get(id=gene[0])
                division_key = f"{subject.year.name}_{subject.division.name}"
                division_schedule[division_key].append(gene[3])
            except:
                pass
        
        for division, timeslots in division_schedule.items():
            timeslot_counts = Counter(timeslots)
            for count in timeslot_counts.values():
                if count > 1:
                    student_conflicts += (count - 1) * 25  # Very heavy penalty
        violations += student_conflicts
        self.constraint_violations['student_conflicts'] = student_conflicts
        
        # REQUIREMENT 7: No room hosting multiple classes at same time
        room_conflicts = 0
        room_schedule = defaultdict(list)
        
        for gene in self.genes:
            if gene[2]:  # location_id
                room_schedule[gene[2]].append(gene[3])
        
        for room_id, timeslots in room_schedule.items():
            timeslot_counts = Counter(timeslots)
            for count in timeslot_counts.values():
                if count > 1:
                    room_conflicts += (count - 1) * 15
        violations += room_conflicts
        self.constraint_violations['room_conflicts'] = room_conflicts
        
        # REQUIREMENT 8: Each course receives required number of sessions
        subject_sessions = defaultdict(int)
        for gene in self.genes:
            subject_sessions[gene[0]] += 1
        
        insufficient_course_sessions = 0
        for subject_id, count in subject_sessions.items():
            try:
                subject = Subject.objects.get(id=subject_id)
                required = getattr(subject, 'sessions_per_week', 3)
                if count < required:
                    insufficient_course_sessions += (required - count) * 4
            except:
                pass
        violations += insufficient_course_sessions
        self.constraint_violations['insufficient_course_sessions'] = insufficient_course_sessions
        
        # REQUIREMENT 9: Distribute sessions evenly (max 14 per teacher)
        workload_violations = 0
        for teacher_id, load in teacher_loads.items():
            if load > 14:
                workload_violations += (load - 14) * 10
            elif load < 6:  # Minimum workload
                workload_violations += (6 - load) * 2
        violations += workload_violations
        self.constraint_violations['workload_violations'] = workload_violations
        
        # REQUIREMENT 10: Respect teacher proficiency (if available)
        proficiency_violations = 0
        try:
            from .models import SubjectProficiency
            for gene in self.genes:
                prof = SubjectProficiency.objects.filter(
                    teacher_id=gene[1], subject_id=gene[0]
                ).first()
                if prof and prof.combined_score < 5.0:
                    proficiency_violations += 3
                elif not prof:
                    proficiency_violations += 1  # Small penalty for no proficiency data
        except:
            pass
        violations += proficiency_violations
        self.constraint_violations['proficiency_violations'] = proficiency_violations
        
        # REQUIREMENT 11: Spread classes between morning and afternoon
        morning_sessions = 0
        afternoon_sessions = 0
        
        for gene in self.genes:
            try:
                timeslot = TimeSlot.objects.get(id=gene[3])
                start_time_str = str(timeslot.start_time)
                hour = int(start_time_str.split(':')[0])
                if hour < 13:  # Before 1 PM
                    morning_sessions += 1
                else:
                    afternoon_sessions += 1
            except:
                pass
        
        total_sessions = morning_sessions + afternoon_sessions
        if total_sessions > 0:
            morning_ratio = morning_sessions / total_sessions
            # Penalty if too unbalanced (should be 30-70% range)
            if morning_ratio < 0.25 or morning_ratio > 0.75:
                balance_violations = abs(0.5 - morning_ratio) * 20
                violations += balance_violations
                self.constraint_violations['time_balance_violations'] = balance_violations
        
        # Lunch break violations (1:00-1:45 PM should be avoided)
        lunch_violations = 0
        for gene in self.genes:
            try:
                timeslot = TimeSlot.objects.get(id=gene[3])
                start_time_str = str(timeslot.start_time)
                if '13:00' in start_time_str or '13:15' in start_time_str or '13:30' in start_time_str:
                    lunch_violations += 8
            except:
                pass
        violations += lunch_violations
        self.constraint_violations['lunch_violations'] = lunch_violations
        
        self.fitness_score = -violations  # Lower violations = higher fitness
        return self.fitness_score

class ProductionGeneticAlgorithm:
    def __init__(self, population_size=20, generations=30, mutation_rate=0.15):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        
        # Load data
        self.teachers = list(Teacher.objects.all())
        self.subjects = list(Subject.objects.all())
        self.rooms = list(Room.objects.all())
        self.labs = list(Lab.objects.all())
        self.timeslots = list(TimeSlot.objects.filter(
            day__in=['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        ))
        
        print(f"Loaded: {len(self.teachers)} teachers, {len(self.subjects)} subjects")
        print(f"Loaded: {len(self.rooms)} rooms, {len(self.labs)} labs, {len(self.timeslots)} timeslots")
    
    def run(self):
        """Run the production genetic algorithm"""
        print("Starting Production Genetic Algorithm...")
        
        if not all([self.teachers, self.subjects, self.timeslots]):
            print("ERROR: Insufficient data for algorithm")
            return None
        
        # Initialize population
        population = []
        for i in range(self.population_size):
            chromosome = self._create_chromosome()
            population.append(chromosome)
            if i % 5 == 0:
                print(f"Created chromosome {i+1}/{self.population_size}")
        
        best_fitness_history = []
        
        # Evolution loop
        for generation in range(self.generations):
            # Evaluate fitness
            for chromosome in population:
                chromosome.fitness()
            
            # Sort by fitness (higher is better)
            population.sort(key=lambda x: x.fitness(), reverse=True)
            
            best_fitness = population[0].fitness()
            best_fitness_history.append(best_fitness)
            
            print(f"Generation {generation+1}: Best fitness = {best_fitness}")
            print(f"  Violations: {sum(population[0].constraint_violations.values())}")
            
            # Early termination if perfect solution found
            if best_fitness == 0:
                print("Perfect solution found!")
                break
            
            # Selection and reproduction
            new_population = []
            
            # Keep best 20% (elitism)
            elite_count = max(1, self.population_size // 5)
            new_population.extend(population[:elite_count])
            
            # Generate rest through crossover and mutation
            while len(new_population) < self.population_size:
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)
                
                child1, child2 = self._crossover(parent1, parent2)
                
                if random.random() < self.mutation_rate:
                    self._mutate(child1)
                if random.random() < self.mutation_rate:
                    self._mutate(child2)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.population_size]
        
        # Return best solution
        best_solution = population[0]
        print(f"\nFinal best fitness: {best_solution.fitness()}")
        print("Constraint violations:")
        for constraint, violations in best_solution.constraint_violations.items():
            if violations > 0:
                print(f"  {constraint}: {violations}")
        
        return best_solution
    
    def _create_chromosome(self):
        """Create a valid chromosome with all constraints considered"""
        genes = []
        
        # Track assignments to avoid conflicts
        teacher_schedule = defaultdict(set)
        room_schedule = defaultdict(set)
        division_schedule = defaultdict(set)
        
        for subject in self.subjects:
            sessions_needed = getattr(subject, 'sessions_per_week', 3)
            
            for session_num in range(sessions_needed):
                attempts = 0
                max_attempts = 50
                
                while attempts < max_attempts:
                    # Select teacher (prefer those with lower workload)
                    teacher = self._select_best_teacher(subject, teacher_schedule)
                    
                    # Select location
                    if getattr(subject, 'requires_lab', False) and self.labs:
                        location_id = random.choice(self.labs).id
                    else:
                        location_id = random.choice(self.rooms).id if self.rooms else None
                    
                    # Select timeslot (avoid conflicts)
                    timeslot = self._select_best_timeslot(
                        subject, teacher, location_id, 
                        teacher_schedule, room_schedule, division_schedule
                    )
                    
                    if timeslot:
                        batch_num = random.randint(1, getattr(subject.division, 'num_batches', 3))
                        
                        gene = (subject.id, teacher.id, location_id, timeslot.id, batch_num)
                        genes.append(gene)
                        
                        # Update schedules
                        teacher_schedule[teacher.id].add(timeslot.id)
                        if location_id:
                            room_schedule[location_id].add(timeslot.id)
                        division_key = f"{subject.year.name}_{subject.division.name}"
                        division_schedule[division_key].add(timeslot.id)
                        
                        break
                    
                    attempts += 1
                
                if attempts >= max_attempts:
                    # Fallback: create gene anyway but it will have violations
                    teacher = random.choice(self.teachers)
                    location_id = random.choice(self.rooms).id if self.rooms else None
                    timeslot = random.choice(self.timeslots)
                    batch_num = random.randint(1, 3)
                    
                    gene = (subject.id, teacher.id, location_id, timeslot.id, batch_num)
                    genes.append(gene)
        
        return ProductionChromosome(genes)
    
    def _select_best_teacher(self, subject, teacher_schedule):
        """Select teacher with lowest workload and best proficiency"""
        try:
            from .models import SubjectProficiency
            
            # Get teachers with proficiency for this subject
            proficient_teachers = SubjectProficiency.objects.filter(
                subject=subject, combined_score__gte=6.0
            ).order_by('-combined_score')[:5]
            
            if proficient_teachers:
                # Select from proficient teachers with lowest workload
                candidates = [(prof.teacher, len(teacher_schedule[prof.teacher.id])) 
                             for prof in proficient_teachers]
                candidates.sort(key=lambda x: x[1])  # Sort by workload
                return candidates[0][0]
        except:
            pass
        
        # Fallback: select teacher with lowest workload
        teacher_loads = [(teacher, len(teacher_schedule[teacher.id])) for teacher in self.teachers]
        teacher_loads.sort(key=lambda x: x[1])
        return teacher_loads[0][0]
    
    def _select_best_timeslot(self, subject, teacher, location_id, teacher_schedule, room_schedule, division_schedule):
        """Select timeslot that minimizes conflicts"""
        division_key = f"{subject.year.name}_{subject.division.name}"
        
        available_slots = []
        for timeslot in self.timeslots:
            # Check for conflicts
            if (timeslot.id not in teacher_schedule[teacher.id] and
                (not location_id or timeslot.id not in room_schedule[location_id]) and
                timeslot.id not in division_schedule[division_key]):
                
                # Avoid lunch break
                start_time_str = str(timeslot.start_time)
                if '13:00' not in start_time_str and '13:15' not in start_time_str:
                    available_slots.append(timeslot)
        
        return random.choice(available_slots) if available_slots else None
    
    def _tournament_selection(self, population, tournament_size=3):
        """Tournament selection"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness())
    
    def _crossover(self, parent1, parent2):
        """Single-point crossover"""
        if not parent1.genes or not parent2.genes:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)
        
        crossover_point = random.randint(1, min(len(parent1.genes), len(parent2.genes)) - 1)
        
        child1_genes = parent1.genes[:crossover_point] + parent2.genes[crossover_point:]
        child2_genes = parent2.genes[:crossover_point] + parent1.genes[crossover_point:]
        
        return ProductionChromosome(child1_genes), ProductionChromosome(child2_genes)
    
    def _mutate(self, chromosome):
        """Mutation with constraint awareness"""
        if not chromosome.genes:
            return
        
        mutation_count = max(1, int(len(chromosome.genes) * 0.1))
        
        for _ in range(mutation_count):
            gene_index = random.randint(0, len(chromosome.genes) - 1)
            gene = list(chromosome.genes[gene_index])
            
            # Mutate different components
            mutation_type = random.randint(0, 3)
            
            if mutation_type == 0 and self.teachers:  # Mutate teacher
                gene[1] = random.choice(self.teachers).id
            elif mutation_type == 1 and self.timeslots:  # Mutate timeslot
                gene[3] = random.choice(self.timeslots).id
            elif mutation_type == 2:  # Mutate location
                if self.rooms:
                    gene[2] = random.choice(self.rooms).id
            elif mutation_type == 3:  # Mutate batch
                gene[4] = random.randint(1, 3)
            
            chromosome.genes[gene_index] = tuple(gene)
        
        # Reset fitness to force recalculation
        chromosome.fitness_score = None
