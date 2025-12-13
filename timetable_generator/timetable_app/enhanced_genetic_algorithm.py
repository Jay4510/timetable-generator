import random
import copy
import time
from datetime import datetime, time as dt_time
from .models import Teacher, Subject, Room, Lab, TimeSlot, SubjectProficiency, ProjectTimeAllocation

class EnhancedChromosome:
    def __init__(self, genes=None):
        self.genes = genes if genes is not None else []
        self.fitness_score = None
    
    def fitness(self):
        if self.fitness_score is not None:
            return self.fitness_score
        
        violations = 0
        violations += self.check_teacher_conflicts()
        violations += self.check_room_conflicts()
        violations += self.check_time_preferences()
        violations += self.check_proficiency_match()
        
        self.fitness_score = -violations
        return self.fitness_score
    
    def check_teacher_conflicts(self):
        violations = 0
        teacher_schedule = {}
        for gene in self.genes:
            subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
            key = (teacher_id, timeslot_id)
            if key in teacher_schedule:
                violations += 1
            else:
                teacher_schedule[key] = True
        return violations
    
    def check_room_conflicts(self):
        violations = 0
        room_schedule = {}
        for gene in self.genes:
            subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
            if location_id:
                key = (location_id, timeslot_id)
                if key in room_schedule:
                    violations += 1
                else:
                    room_schedule[key] = True
        return violations
    
    def check_time_preferences(self):
        violations = 0
        try:
            for gene in self.genes:
                subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
                teacher = Teacher.objects.get(id=teacher_id)
                timeslot = TimeSlot.objects.get(id=timeslot_id)
                
                if teacher.time_preference == 'first_half' and not timeslot.is_first_half:
                    violations += 1
                elif teacher.time_preference == 'second_half' and timeslot.is_first_half:
                    violations += 1
        except:
            pass
        return violations
    
    def check_proficiency_match(self):
        violations = 0
        try:
            for gene in self.genes:
                subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
                proficiency = SubjectProficiency.objects.filter(
                    teacher_id=teacher_id, subject_id=subject_id
                ).first()
                
                if proficiency and proficiency.combined_score < 5.0:
                    violations += 1
                elif not proficiency:
                    violations += 2
        except:
            pass
        return violations

class EnhancedGeneticAlgorithm:
    def __init__(self, population_size=30, generations=50):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = 0.2
    
    def run(self):
        print("Starting Enhanced Genetic Algorithm...")
        
        try:
            teachers = list(Teacher.objects.filter(status='active'))
            subjects = list(Subject.objects.all())
            rooms = list(Room.objects.all())
            labs = list(Lab.objects.all())
            timeslots = list(TimeSlot.objects.filter(is_break=False))
            
            if not all([teachers, subjects, timeslots]):
                return None
            
            population = self.initialize_population(teachers, subjects, rooms, labs, timeslots)
            
            for generation in range(self.generations):
                fitness_scores = [individual.fitness() for individual in population]
                best_fitness = max(fitness_scores)
                
                if best_fitness >= -10:  # Good enough solution
                    return population[fitness_scores.index(best_fitness)]
                
                # Simple evolution
                new_population = []
                for _ in range(self.population_size):
                    parent = self.tournament_selection(population)
                    child = self.mutate(copy.deepcopy(parent))
                    new_population.append(child)
                
                population = new_population
                
                if generation % 10 == 0:
                    print(f"Generation {generation}, Best fitness: {best_fitness}")
            
            # Return best solution
            fitness_scores = [individual.fitness() for individual in population]
            return population[fitness_scores.index(max(fitness_scores))]
            
        except Exception as e:
            print(f"Error in genetic algorithm: {e}")
            return None
    
    def initialize_population(self, teachers, subjects, rooms, labs, timeslots):
        population = []
        
        for _ in range(self.population_size):
            chromosome = EnhancedChromosome()
            
            for subject in subjects:
                for _ in range(min(subject.sessions_per_week, 3)):  # Limit sessions
                    teacher = self.get_best_teacher(subject, teachers)
                    location_id = random.choice(labs).id if subject.requires_lab and labs else (random.choice(rooms).id if rooms else None)
                    timeslot = self.get_preferred_timeslot(teacher, timeslots)
                    batch_num = random.randint(1, 3)
                    
                    gene = (subject.id, teacher.id, location_id, timeslot.id, batch_num)
                    chromosome.genes.append(gene)
            
            population.append(chromosome)
        
        return population
    
    def get_best_teacher(self, subject, teachers):
        try:
            proficiencies = SubjectProficiency.objects.filter(subject=subject).order_by('-combined_score')[:3]
            if proficiencies:
                return random.choice([p.teacher for p in proficiencies])
        except:
            pass
        return random.choice(teachers)
    
    def get_preferred_timeslot(self, teacher, timeslots):
        try:
            if teacher.time_preference == 'first_half':
                preferred = [ts for ts in timeslots if ts.is_first_half]
                return random.choice(preferred) if preferred else random.choice(timeslots)
            elif teacher.time_preference == 'second_half':
                preferred = [ts for ts in timeslots if not ts.is_first_half]
                return random.choice(preferred) if preferred else random.choice(timeslots)
        except:
            pass
        return random.choice(timeslots)
    
    def tournament_selection(self, population):
        tournament_size = 3
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness())
    
    def mutate(self, chromosome):
        if random.random() < self.mutation_rate and chromosome.genes:
            # Simple mutation: change one random gene
            gene_index = random.randint(0, len(chromosome.genes) - 1)
            # Reset fitness to force recalculation
            chromosome.fitness_score = None
        return chromosome
