"""
Division-Specific Genetic Algorithm
Generates separate optimized timetables for each division while preventing teacher conflicts
"""

import random
import copy
from collections import defaultdict, Counter
from .models import Teacher, Subject, Room, Lab, TimeSlot, Session, Year, Division

class DivisionChromosome:
    def __init__(self, genes=None, division_key=""):
        self.genes = genes if genes is not None else []
        self.division_key = division_key
        self.fitness_score = None
        self.violations = {}
    
    def fitness(self, global_teacher_schedule=None):
        """Calculate fitness for this division's timetable"""
        if self.fitness_score is not None:
            return self.fitness_score
        
        violations = 0
        self.violations = {}
        
        if not self.genes:
            self.fitness_score = -1000
            return self.fitness_score
        
        # 1. Teacher conflicts within this division
        teacher_times = defaultdict(list)
        for gene in self.genes:
            teacher_times[gene[1]].append(gene[3])
        
        teacher_conflicts = 0
        for times in teacher_times.values():
            time_counts = Counter(times)
            for count in time_counts.values():
                if count > 1:
                    teacher_conflicts += (count - 1) * 20
        violations += teacher_conflicts
        
        # 2. Room conflicts within this division
        room_times = defaultdict(list)
        for gene in self.genes:
            if gene[2]:
                room_times[gene[2]].append(gene[3])
        
        room_conflicts = 0
        for times in room_times.values():
            time_counts = Counter(times)
            for count in time_counts.values():
                if count > 1:
                    room_conflicts += (count - 1) * 15
        violations += room_conflicts
        
        # 3. Student conflicts (multiple lectures at same time for this division)
        all_times = [gene[3] for gene in self.genes]
        time_counts = Counter(all_times)
        student_conflicts = 0
        for count in time_counts.values():
            if count > 1:
                student_conflicts += (count - 1) * 25
        violations += student_conflicts
        
        # 4. Cross-division teacher conflicts (if global schedule provided)
        if global_teacher_schedule:
            cross_division_conflicts = 0
            for gene in self.genes:
                teacher_id, timeslot_id = gene[1], gene[3]
                if timeslot_id in global_teacher_schedule.get(teacher_id, set()):
                    cross_division_conflicts += 30  # Very heavy penalty
            violations += cross_division_conflicts
        
        # 5. Subject session requirements
        subject_counts = defaultdict(int)
        for gene in self.genes:
            subject_counts[gene[0]] += 1
        
        for subject_id, count in subject_counts.items():
            try:
                subject = Subject.objects.get(id=subject_id)
                required = getattr(subject, 'sessions_per_week', 3)
                if count < required:
                    violations += (required - count) * 5
            except:
                pass
        
        # 6. Teacher proficiency
        try:
            from .models import SubjectProficiency
            for gene in self.genes:
                prof = SubjectProficiency.objects.filter(
                    teacher_id=gene[1], subject_id=gene[0]
                ).first()
                if not prof or prof.combined_score < 5.0:
                    violations += 3
        except:
            pass
        
        self.violations = {'total': violations}
        self.fitness_score = -violations
        return self.fitness_score

class DivisionGeneticAlgorithm:
    def __init__(self, division, global_teacher_schedule, population_size=10, generations=15):
        self.division = division
        self.global_teacher_schedule = global_teacher_schedule
        self.population_size = population_size
        self.generations = generations
        
        # Get subjects for this specific division
        self.subjects = list(Subject.objects.filter(
            year=division.year, 
            division=division
        ))
        
        self.teachers = list(Teacher.objects.all())
        self.rooms = list(Room.objects.all())
        self.labs = list(Lab.objects.all())
        self.timeslots = list(TimeSlot.objects.filter(
            day__in=['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        ))
        
        # Filter out lunch break timeslots
        self.available_timeslots = []
        for ts in self.timeslots:
            start_time_str = str(ts.start_time)
            if not ('13:00' in start_time_str or '13:15' in start_time_str or '13:30' in start_time_str):
                self.available_timeslots.append(ts)
        
        self.division_key = f"{division.year.name}_{division.name}"
        
        print(f"  Division {self.division_key}: {len(self.subjects)} subjects, {len(self.available_timeslots)} timeslots")
    
    def run(self):
        """Run genetic algorithm for this specific division"""
        if not all([self.subjects, self.teachers, self.available_timeslots]):
            print(f"  ERROR: Insufficient data for division {self.division_key}")
            return None
        
        # Initialize population
        population = []
        for i in range(self.population_size):
            chromosome = self._create_chromosome()
            population.append(chromosome)
        
        # Evolution loop
        for generation in range(self.generations):
            # Evaluate fitness
            for chromosome in population:
                chromosome.fitness(self.global_teacher_schedule)
            
            # Sort by fitness
            population.sort(key=lambda x: x.fitness_score, reverse=True)
            
            best_fitness = population[0].fitness_score
            
            if generation % 5 == 0:
                print(f"    Generation {generation+1}: Best fitness = {best_fitness}")
            
            # Early termination if good solution
            if best_fitness > -20:
                break
            
            # Create new population
            new_population = []
            
            # Keep best 30%
            elite_count = max(1, self.population_size // 3)
            new_population.extend(population[:elite_count])
            
            # Generate rest through crossover and mutation
            while len(new_population) < self.population_size:
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)
                
                child1, child2 = self._crossover(parent1, parent2)
                
                if random.random() < 0.3:
                    self._mutate(child1)
                if random.random() < 0.3:
                    self._mutate(child2)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.population_size]
        
        best_solution = population[0]
        print(f"    Final fitness for {self.division_key}: {best_solution.fitness_score}")
        
        return best_solution
    
    def _create_chromosome(self):
        """Create chromosome for this division avoiding global teacher conflicts"""
        genes = []
        
        for subject in self.subjects:
            sessions_needed = min(getattr(subject, 'sessions_per_week', 3), 3)
            
            for _ in range(sessions_needed):
                # Select teacher avoiding global conflicts
                available_teachers = []
                for teacher in self.teachers:
                    teacher_available_slots = []
                    for ts in self.available_timeslots:
                        if ts.id not in self.global_teacher_schedule.get(teacher.id, set()):
                            teacher_available_slots.append(ts)
                    
                    if teacher_available_slots:
                        available_teachers.append((teacher, teacher_available_slots))
                
                if not available_teachers:
                    continue
                
                # Select teacher and timeslot
                teacher, available_slots = random.choice(available_teachers)
                timeslot = random.choice(available_slots)
                
                # Select location
                if getattr(subject, 'requires_lab', False) and self.labs:
                    location_id = random.choice(self.labs).id
                else:
                    location_id = random.choice(self.rooms).id if self.rooms else None
                
                batch_num = random.randint(1, getattr(self.division, 'num_batches', 3))
                
                gene = (subject.id, teacher.id, location_id, timeslot.id, batch_num)
                genes.append(gene)
        
        return DivisionChromosome(genes, self.division_key)
    
    def _tournament_selection(self, population, tournament_size=3):
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness_score)
    
    def _crossover(self, parent1, parent2):
        if not parent1.genes or not parent2.genes:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)
        
        min_length = min(len(parent1.genes), len(parent2.genes))
        if min_length <= 1:
            return copy.deepcopy(parent1), copy.deepcopy(parent2)
        
        crossover_point = random.randint(1, min_length - 1)
        
        child1_genes = parent1.genes[:crossover_point] + parent2.genes[crossover_point:]
        child2_genes = parent2.genes[:crossover_point] + parent1.genes[crossover_point:]
        
        return (DivisionChromosome(child1_genes, self.division_key), 
                DivisionChromosome(child2_genes, self.division_key))
    
    def _mutate(self, chromosome):
        if not chromosome.genes:
            return
        
        mutation_count = max(1, len(chromosome.genes) // 5)
        
        for _ in range(mutation_count):
            gene_index = random.randint(0, len(chromosome.genes) - 1)
            gene = list(chromosome.genes[gene_index])
            
            mutation_type = random.randint(0, 2)
            
            if mutation_type == 0 and self.teachers:
                gene[1] = random.choice(self.teachers).id
            elif mutation_type == 1 and self.available_timeslots:
                gene[3] = random.choice(self.available_timeslots).id
            elif mutation_type == 2:
                gene[4] = random.randint(1, 3)
            
            chromosome.genes[gene_index] = tuple(gene)
        
        chromosome.fitness_score = None
