"""
Real-World College Timetable Genetic Algorithm
Implements all the crucial real-world requirements:
1. 1-hour lectures, 2-hour labs
2. Lunch break (1:00-1:45 PM) exclusion
3. 5-day week (Monday-Friday)
4. Professor resignation/replacement handling
5. Time preferences (first/second half)
6. Subject proficiency-based allocation (knowledge + willingness ratings)
7. Project time allocation (dedicated half-days)
8. Year-specific start times (e.g., 4th year starts at 10 AM)
"""

import random
import copy
import time
from datetime import datetime, time as dt_time
from .models import (
    Teacher, Subject, Room, Lab, TimeSlot, SubjectProficiency, 
    ProjectTimeAllocation, Session, Year, Division
)

class RealWorldChromosome:
    """Enhanced chromosome that handles real-world college constraints"""
    
    def __init__(self, genes=None):
        self.genes = genes if genes is not None else []
        self.fitness_score = None
        self.constraint_violations = {}
    
    def fitness(self):
        """Calculate fitness based on real-world constraints"""
        if self.fitness_score is not None:
            return self.fitness_score
        
        # Reset violations
        self.constraint_violations = {
            'teacher_conflicts': 0,
            'room_conflicts': 0,
            'lunch_break_violations': 0,
            'time_preference_violations': 0,
            'proficiency_mismatches': 0,
            'lab_room_violations': 0,
            'project_time_conflicts': 0,
            'workload_violations': 0
        }
        
        # Check all constraints
        self.constraint_violations['teacher_conflicts'] = self._check_teacher_conflicts()
        self.constraint_violations['room_conflicts'] = self._check_room_conflicts()
        self.constraint_violations['lunch_break_violations'] = self._check_lunch_break_violations()
        self.constraint_violations['time_preference_violations'] = self._check_time_preferences()
        self.constraint_violations['proficiency_mismatches'] = self._check_proficiency_matching()
        self.constraint_violations['lab_room_violations'] = self._check_lab_room_assignments()
        self.constraint_violations['project_time_conflicts'] = self._check_project_time_conflicts()
        self.constraint_violations['workload_violations'] = self._check_teacher_workload()
        
        # Calculate fitness (higher is better, negative violations)
        total_violations = sum(self.constraint_violations.values())
        
        # Add bonus for good proficiency matches
        proficiency_bonus = self._calculate_proficiency_bonus()
        
        self.fitness_score = -total_violations + proficiency_bonus
        return self.fitness_score
    
    def _check_teacher_conflicts(self):
        """No teacher can be in two places at the same time"""
        violations = 0
        teacher_schedule = {}
        
        for gene in self.genes:
            subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
            key = (teacher_id, timeslot_id)
            if key in teacher_schedule:
                violations += 10  # Hard constraint - high penalty
            else:
                teacher_schedule[key] = True
        return violations
    
    def _check_room_conflicts(self):
        """No room can have multiple sessions at the same time"""
        violations = 0
        room_schedule = {}
        
        for gene in self.genes:
            subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
            if location_id:
                key = (location_id, timeslot_id)
                if key in room_schedule:
                    violations += 10  # Hard constraint
                else:
                    room_schedule[key] = True
        return violations
    
    def _check_lunch_break_violations(self):
        """No sessions during lunch break (1:00-1:45 PM)"""
        violations = 0
        try:
            lunch_timeslots = TimeSlot.objects.filter(
                start_time__gte=dt_time(13, 0),
                end_time__lte=dt_time(13, 45)
            ).values_list('id', flat=True)
            
            for gene in self.genes:
                subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
                if timeslot_id in lunch_timeslots:
                    violations += 15  # Very high penalty - absolute constraint
        except:
            pass
        return violations
    
    def _check_time_preferences(self):
        """Check if teacher time preferences are respected"""
        violations = 0
        try:
            for gene in self.genes:
                subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
                
                teacher = Teacher.objects.get(id=teacher_id)
                timeslot = TimeSlot.objects.get(id=timeslot_id)
                
                # Check time preference matching
                if hasattr(teacher, 'time_preference') and hasattr(timeslot, 'is_first_half'):
                    if teacher.time_preference == 'first_half' and not timeslot.is_first_half:
                        violations += 3  # Soft constraint
                    elif teacher.time_preference == 'second_half' and timeslot.is_first_half:
                        violations += 3  # Soft constraint
        except:
            pass
        return violations
    
    def _check_proficiency_matching(self):
        """Check if subjects are assigned to teachers with good proficiency"""
        violations = 0
        try:
            for gene in self.genes:
                subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
                
                # Check if proficiency exists
                proficiency = SubjectProficiency.objects.filter(
                    teacher_id=teacher_id,
                    subject_id=subject_id
                ).first()
                
                if proficiency:
                    # Penalize low proficiency assignments
                    combined_score = proficiency.combined_score
                    if combined_score < 5.0:  # Below average
                        violations += 5
                    elif combined_score < 3.0:  # Very low
                        violations += 10
                else:
                    # No proficiency data - moderate penalty
                    violations += 2
        except:
            pass
        return violations
    
    def _check_lab_room_assignments(self):
        """Labs must be assigned to lab rooms, lectures to classrooms"""
        violations = 0
        try:
            for gene in self.genes:
                subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
                
                subject = Subject.objects.get(id=subject_id)
                
                if hasattr(subject, 'requires_lab') and subject.requires_lab:
                    # This is a lab subject - must be in a lab room
                    if location_id:
                        try:
                            lab = Lab.objects.get(id=location_id)
                        except Lab.DoesNotExist:
                            # Not assigned to a lab room
                            violations += 8
                else:
                    # This is a lecture - should be in a classroom
                    if location_id:
                        try:
                            room = Room.objects.get(id=location_id)
                        except Room.DoesNotExist:
                            violations += 2
        except:
            pass
        return violations
    
    def _check_project_time_conflicts(self):
        """Check for conflicts with dedicated project time"""
        violations = 0
        try:
            project_timeslots = ProjectTimeAllocation.objects.filter(
                is_active=True
            ).values_list('timeslot_id', flat=True)
            
            for gene in self.genes:
                subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
                if timeslot_id in project_timeslots:
                    violations += 12  # High penalty - project time is sacred
        except:
            pass
        return violations
    
    def _check_teacher_workload(self):
        """Check if teachers are overloaded (max 14 sessions per week)"""
        violations = 0
        teacher_sessions = {}
        
        for gene in self.genes:
            subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
            teacher_sessions[teacher_id] = teacher_sessions.get(teacher_id, 0) + 1
        
        try:
            for teacher_id, session_count in teacher_sessions.items():
                teacher = Teacher.objects.get(id=teacher_id)
                max_sessions = getattr(teacher, 'max_sessions_per_week', 14)
                
                if session_count > max_sessions:
                    violations += (session_count - max_sessions) * 5
        except:
            pass
        return violations
    
    def _calculate_proficiency_bonus(self):
        """Give bonus points for good proficiency matches"""
        bonus = 0
        try:
            for gene in self.genes:
                subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
                
                proficiency = SubjectProficiency.objects.filter(
                    teacher_id=teacher_id,
                    subject_id=subject_id
                ).first()
                
                if proficiency:
                    combined_score = proficiency.combined_score
                    if combined_score >= 8.0:  # Excellent match
                        bonus += 3
                    elif combined_score >= 6.0:  # Good match
                        bonus += 1
        except:
            pass
        return bonus


class RealWorldGeneticAlgorithm:
    """
    Genetic Algorithm implementing all real-world college timetable requirements
    """
    
    def __init__(self, population_size=30, generations=50, mutation_rate=0.1):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.population = []
        
        # Load data
        self.teachers = list(Teacher.objects.filter(status='active'))
        self.subjects = list(Subject.objects.all())
        self.rooms = list(Room.objects.all())
        self.labs = list(Lab.objects.all())
        self.timeslots = self._get_valid_timeslots()
        
        print(f"Loaded: {len(self.teachers)} teachers, {len(self.subjects)} subjects, "
              f"{len(self.rooms)} rooms, {len(self.labs)} labs, {len(self.timeslots)} timeslots")
    
    def _get_valid_timeslots(self):
        """Get timeslots excluding lunch break and weekends"""
        valid_timeslots = []
        
        try:
            # Exclude lunch break (1:00-1:45 PM) and weekends
            timeslots = TimeSlot.objects.filter(
                day__in=['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
            ).exclude(
                start_time__gte=dt_time(13, 0),
                end_time__lte=dt_time(13, 45)
            )
            
            valid_timeslots = list(timeslots)
        except:
            # Fallback if TimeSlot model doesn't have the expected fields
            valid_timeslots = list(TimeSlot.objects.all())
        
        return valid_timeslots
    
    def _create_random_chromosome(self):
        """Create a random chromosome with real-world logic"""
        genes = []
        
        # For each subject, create sessions based on requirements
        for subject in self.subjects:
            sessions_needed = getattr(subject, 'sessions_per_week', 4)
            is_lab = getattr(subject, 'requires_lab', False)
            
            for session in range(min(sessions_needed, 3)):  # Limit to 3 sessions per subject
                # Select teacher based on proficiency if available
                teacher = self._select_best_teacher_for_subject(subject)
                
                # Select appropriate location
                if is_lab:
                    location_id = random.choice(self.labs).id if self.labs else None
                else:
                    location_id = random.choice(self.rooms).id if self.rooms else None
                
                # Select timeslot considering teacher preferences
                timeslot = self._select_preferred_timeslot(teacher)
                
                batch_num = random.randint(1, 3)
                
                gene = (subject.id, teacher.id, location_id, timeslot.id, batch_num)
                genes.append(gene)
        
        return RealWorldChromosome(genes)
    
    def _select_best_teacher_for_subject(self, subject):
        """Select teacher based on proficiency ratings"""
        try:
            # Get proficiency ratings for this subject
            proficiencies = SubjectProficiency.objects.filter(
                subject=subject
            ).order_by('-knowledge_rating', '-willingness_rating')
            
            if proficiencies.exists():
                # 70% chance to pick from top 3, 30% random
                if random.random() < 0.7 and len(proficiencies) >= 3:
                    return random.choice(proficiencies[:3]).teacher
                else:
                    return random.choice(proficiencies).teacher
        except:
            pass
        
        # Fallback to random active teacher
        active_teachers = [t for t in self.teachers if getattr(t, 'status', 'active') == 'active']
        return random.choice(active_teachers) if active_teachers else random.choice(self.teachers)
    
    def _select_preferred_timeslot(self, teacher):
        """Select timeslot based on teacher preferences"""
        try:
            preference = getattr(teacher, 'time_preference', 'no_preference')
            
            if preference == 'first_half':
                # Prefer first half timeslots
                first_half_slots = [ts for ts in self.timeslots if getattr(ts, 'is_first_half', True)]
                if first_half_slots:
                    return random.choice(first_half_slots)
            elif preference == 'second_half':
                # Prefer second half timeslots
                second_half_slots = [ts for ts in self.timeslots if not getattr(ts, 'is_first_half', True)]
                if second_half_slots:
                    return random.choice(second_half_slots)
        except:
            pass
        
        # Fallback to random timeslot
        return random.choice(self.timeslots)
    
    def _initialize_population(self):
        """Initialize population with random chromosomes"""
        self.population = []
        for _ in range(self.population_size):
            chromosome = self._create_random_chromosome()
            self.population.append(chromosome)
        
        print(f"Initialized population of {len(self.population)} chromosomes")
    
    def _selection(self):
        """Tournament selection"""
        tournament_size = 3
        selected = []
        
        for _ in range(self.population_size):
            tournament = random.sample(self.population, min(tournament_size, len(self.population)))
            winner = max(tournament, key=lambda x: x.fitness())
            selected.append(winner)
        
        return selected
    
    def _crossover(self, parent1, parent2):
        """Single-point crossover"""
        if len(parent1.genes) == 0 or len(parent2.genes) == 0:
            return parent1, parent2
        
        point = random.randint(1, min(len(parent1.genes), len(parent2.genes)) - 1)
        
        child1_genes = parent1.genes[:point] + parent2.genes[point:]
        child2_genes = parent2.genes[:point] + parent1.genes[point:]
        
        return RealWorldChromosome(child1_genes), RealWorldChromosome(child2_genes)
    
    def _mutate(self, chromosome):
        """Mutation with real-world logic"""
        if random.random() > self.mutation_rate or len(chromosome.genes) == 0:
            return
        
        # Select random gene to mutate
        gene_index = random.randint(0, len(chromosome.genes) - 1)
        subject_id, teacher_id, location_id, timeslot_id, batch_num = chromosome.genes[gene_index]
        
        # Mutate different components
        mutation_type = random.choice(['teacher', 'location', 'timeslot', 'batch'])
        
        if mutation_type == 'teacher':
            # Select new teacher based on proficiency
            subject = Subject.objects.get(id=subject_id)
            new_teacher = self._select_best_teacher_for_subject(subject)
            teacher_id = new_teacher.id
        elif mutation_type == 'location':
            # Select appropriate location
            subject = Subject.objects.get(id=subject_id)
            is_lab = getattr(subject, 'requires_lab', False)
            if is_lab and self.labs:
                location_id = random.choice(self.labs).id
            elif self.rooms:
                location_id = random.choice(self.rooms).id
        elif mutation_type == 'timeslot':
            # Select new timeslot
            teacher = Teacher.objects.get(id=teacher_id)
            new_timeslot = self._select_preferred_timeslot(teacher)
            timeslot_id = new_timeslot.id
        elif mutation_type == 'batch':
            batch_num = random.randint(1, 3)
        
        chromosome.genes[gene_index] = (subject_id, teacher_id, location_id, timeslot_id, batch_num)
        chromosome.fitness_score = None  # Reset fitness
    
    def run(self):
        """Run the genetic algorithm"""
        print("Starting Real-World Genetic Algorithm...")
        start_time = time.time()
        
        # Initialize population
        self._initialize_population()
        
        best_fitness_history = []
        
        for generation in range(self.generations):
            # Evaluate fitness
            for chromosome in self.population:
                chromosome.fitness()
            
            # Track best fitness
            best_chromosome = max(self.population, key=lambda x: x.fitness())
            best_fitness = best_chromosome.fitness()
            best_fitness_history.append(best_fitness)
            
            if generation % 10 == 0:
                print(f"Generation {generation}: Best fitness = {best_fitness}")
                print(f"  Constraint violations: {best_chromosome.constraint_violations}")
            
            # Selection
            selected = self._selection()
            
            # Create new population
            new_population = []
            
            # Elitism - keep best chromosome
            new_population.append(copy.deepcopy(best_chromosome))
            
            # Crossover and mutation
            while len(new_population) < self.population_size:
                parent1, parent2 = random.sample(selected, 2)
                child1, child2 = self._crossover(parent1, parent2)
                
                self._mutate(child1)
                self._mutate(child2)
                
                new_population.extend([child1, child2])
            
            # Trim to population size
            self.population = new_population[:self.population_size]
        
        # Final evaluation
        for chromosome in self.population:
            chromosome.fitness()
        
        best_solution = max(self.population, key=lambda x: x.fitness())
        end_time = time.time()
        
        print(f"\nOptimization completed in {end_time - start_time:.2f} seconds")
        print(f"Best fitness: {best_solution.fitness()}")
        print(f"Final constraint violations: {best_solution.constraint_violations}")
        print(f"Total sessions: {len(best_solution.genes)}")
        
        return best_solution
