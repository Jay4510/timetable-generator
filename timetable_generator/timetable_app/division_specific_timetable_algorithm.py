# DIVISION-SPECIFIC TIMETABLE ALGORITHM - Final Corrected Version

import random
import copy
from collections import defaultdict, Counter
from datetime import datetime, timedelta, time
from typing import List, Dict, Tuple, Optional, Set
import logging

from .models import (
    Teacher, Subject, Room, Lab, TimeSlot, Session, Year, Division, Batch,
    SubjectProficiency, SystemConfiguration, ProjectWork, TimetableIncharge
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DivisionSpecificChromosome:
    """Division-specific chromosome for generating per-division timetables"""
    
    def __init__(self, genes=None, division=None):
        self.genes = genes if genes is not None else []
        self.division = division  # Target division for this chromosome
        self.fitness_score = None
        self.violations = {}
        self.constraint_details = {}
    
    def fitness(self, algorithm_instance):
        """Calculate fitness with division-specific constraints"""
        if self.fitness_score is not None:
            return self.fitness_score
        
        violations = 0
        self.violations = {}
        self.constraint_details = {}
        
        try:
            # Division-specific constraint checking
            violations += self._check_division_specific_conflicts(algorithm_instance)
            violations += self._check_batch_level_conflicts(algorithm_instance)
            violations += self._check_cross_division_resource_conflicts(algorithm_instance)
            violations += self._check_division_teacher_load(algorithm_instance)
            violations += self._check_division_lab_equipment_conflicts(algorithm_instance)
            violations += self._check_project_work_for_division(algorithm_instance)
            violations += self._check_remedial_for_division(algorithm_instance)
            
            # Standard constraints (adapted for division scope)
            violations += self._check_break_times(algorithm_instance)
            violations += self._check_teacher_preferences()
            violations += self._auto_balance_morning_afternoon()
            
        except Exception as e:
            logger.error(f"Error in fitness calculation for division {self.division}: {e}")
            violations += 1000
        
        self.violations['total'] = violations
        self.fitness_score = -violations
        return self.fitness_score
    
    def _check_division_specific_conflicts(self, algorithm_instance):
        """Check conflicts within this specific division"""
        violations = 0
        
        # Teacher conflicts within division
        teacher_times = defaultdict(list)
        for gene in self.genes:
            teacher_times[gene[1]].append(gene[3])
        
        for times in teacher_times.values():
            time_counts = Counter(times)
            conflicts = sum(max(0, count - 1) for count in time_counts.values())
            violations += conflicts * 30
        
        # Room conflicts within division
        room_times = defaultdict(list)
        for gene in self.genes:
            if gene[2]:
                room_times[gene[2]].append(gene[3])
        
        for times in room_times.values():
            time_counts = Counter(times)
            conflicts = sum(max(0, count - 1) for count in time_counts.values())
            violations += conflicts * 25
        
        return violations
    
    def _check_batch_level_conflicts(self, algorithm_instance):
        """Check conflicts at batch level within the division"""
        violations = 0
        batch_times = defaultdict(list)
        
        for gene in self.genes:
            batch_id = gene[4]  # batch identifier
            timeslot_id = gene[3]
            batch_times[batch_id].append(timeslot_id)
        
        # Check each batch for time conflicts
        for batch_id, times in batch_times.items():
            time_counts = Counter(times)
            conflicts = sum(max(0, count - 1) for count in time_counts.values())
            violations += conflicts * 35  # Heavy penalty for student conflicts
        
        self.constraint_details['batch_conflicts'] = len([
            batch_id for batch_id, times in batch_times.items() 
            if len(times) != len(set(times))
        ])
        
        return violations
    
    def _check_cross_division_resource_conflicts(self, algorithm_instance):
        """Check resource conflicts across divisions (especially labs)"""
        violations = 0
        
        # Get all other active divisions' timetables for conflict checking
        other_division_schedules = algorithm_instance.get_other_divisions_schedules(self.division)
        
        for gene in self.genes:
            room_id = gene[2]
            timeslot_id = gene[3]
            
            if room_id:
                # Check if this room+time is used by other divisions
                for other_div_schedule in other_division_schedules:
                    for other_gene in other_div_schedule.genes:
                        if other_gene[2] == room_id and other_gene[3] == timeslot_id:
                            # Resource conflict across divisions
                            violations += 40  # Very heavy penalty
        
        return violations
    
    def _check_division_teacher_load(self, algorithm_instance):
        """Check teacher load distribution within this division"""
        violations = 0
        teacher_loads = defaultdict(int)
        
        for gene in self.genes:
            teacher_loads[gene[1]] += 1
        
        if teacher_loads:
            total_sessions = sum(teacher_loads.values())
            num_teachers = len(teacher_loads)
            ideal_load = total_sessions / num_teachers if num_teachers > 0 else 0
            
            tolerance = max(1, int(ideal_load * 0.3))  # 30% tolerance
            
            for teacher_id, load in teacher_loads.items():
                deviation = abs(load - ideal_load)
                if deviation > tolerance:
                    violations += int(deviation * 3)  # Moderate penalty
        
        return violations
    
    def _check_division_lab_equipment_conflicts(self, algorithm_instance):
        """Check lab equipment conflicts specific to division and cross-year"""
        violations = 0
        
        # Group lab sessions by equipment type and time
        equipment_schedule = defaultdict(lambda: defaultdict(list))
        
        for gene in self.genes:
            try:
                subject = Subject.objects.get(id=gene[0])
                if getattr(subject, 'requires_lab', False):
                    room_id = gene[2]
                    timeslot_id = gene[3]
                    
                    # Get room equipment category
                    room_equipment = self._get_room_equipment_category(room_id, algorithm_instance)
                    
                    equipment_schedule[room_equipment][timeslot_id].append({
                        'division': self.division.name,
                        'year': subject.year.name,
                        'subject': subject.name,
                        'batch': gene[4]
                    })
                    
            except Exception as e:
                logger.warning(f"Error in lab equipment check: {e}")
        
        # Check for cross-year equipment conflicts
        for equipment_type, schedule in equipment_schedule.items():
            for timeslot_id, sessions in schedule.items():
                if len(sessions) > 1:
                    years = set(s['year'] for s in sessions)
                    if len(years) > 1:
                        violations += 25 * (len(sessions) - 1)
        
        return violations
    
    def _check_project_work_for_division(self, algorithm_instance):
        """Check project work constraints for this division"""
        violations = 0
        
        try:
            division_year = self.division.year
            project_configs = ProjectWork.objects.filter(year=division_year)
            
            for project_config in project_configs:
                dedicated_timeslots = project_config.dedicated_timeslots.all()
                
                # Check if any regular sessions conflict with project time
                for timeslot in dedicated_timeslots:
                    conflicting_sessions = 0
                    
                    for gene in self.genes:
                        if gene[3] == timeslot.id:
                            try:
                                subject = Subject.objects.get(id=gene[0])
                                if not getattr(subject, 'is_project_work', False):
                                    conflicting_sessions += 1
                            except:
                                pass
                    
                    violations += conflicting_sessions * 30
                    
        except Exception as e:
            logger.warning(f"Error checking project work: {e}")
        
        return violations
    
    def _check_remedial_for_division(self, algorithm_instance):
        """Check remedial lecture for this division (one per department, not per division)"""
        violations = 0
        
        # Only check remedial if this is the "primary" division for remedial scheduling
        if algorithm_instance.is_remedial_division(self.division):
            remedial_count = 0
            
            for gene in self.genes:
                try:
                    subject = Subject.objects.get(id=gene[0])
                    if getattr(subject, 'is_remedial', False):
                        remedial_count += 1
                except:
                    pass
            
            if remedial_count == 0:
                violations += 15  # Missing remedial
            elif remedial_count > 1:
                violations += (remedial_count - 1) * 10  # Too many
        
        return violations
    
    # Helper methods remain similar but adapted for division scope
    def _get_room_equipment_category(self, room_id, algorithm_instance):
        """Get equipment category for room"""
        try:
            for room in algorithm_instance.rooms + algorithm_instance.labs:
                if room.id == room_id:
                    return getattr(room, 'equipment_category', 'general')
        except:
            pass
        return 'general'
    
    def _check_break_times(self, algorithm_instance):
        """Check break time enforcement"""
        violations = 0
        
        try:
            break_start = algorithm_instance.system_config.break_start_time
            break_end = algorithm_instance.system_config.break_end_time
            
            for gene in self.genes:
                try:
                    timeslot = TimeSlot.objects.get(id=gene[3])
                    if self._time_overlaps_break(timeslot, break_start, break_end):
                        violations += 25
                except:
                    pass
                    
        except Exception as e:
            logger.warning(f"Error checking break times: {e}")
        
        return violations
    
    def _check_teacher_preferences(self):
        """Check teacher time preferences"""
        violations = 0
        
        for gene in self.genes:
            try:
                teacher = Teacher.objects.get(id=gene[1])
                timeslot = TimeSlot.objects.get(id=gene[3])
                subject = Subject.objects.get(id=gene[0])
                
                preferences = getattr(teacher, 'preferences', {}) or {}
                
                if preferences:
                    hour = int(str(timeslot.start_time).split(':')[0])
                    is_morning = hour < 13
                    is_lab = getattr(subject, 'requires_lab', False)
                    
                    if is_lab:
                        lab_pref = preferences.get('lab_time_preference', 'no_preference')
                        if lab_pref == 'morning' and not is_morning:
                            violations += 5
                        elif lab_pref == 'afternoon' and is_morning:
                            violations += 5
                    else:
                        lecture_pref = preferences.get('lecture_time_preference', 'no_preference')
                        if lecture_pref == 'morning' and not is_morning:
                            violations += 3
                        elif lecture_pref == 'afternoon' and is_morning:
                            violations += 3
                            
            except Exception as e:
                logger.warning(f"Error checking teacher preferences: {e}")
        
        return violations
    
    def _auto_balance_morning_afternoon(self):
        """Automatic morning/afternoon balance"""
        violations = 0
        morning = afternoon = 0
        
        for gene in self.genes:
            try:
                timeslot = TimeSlot.objects.get(id=gene[3])
                hour = int(str(timeslot.start_time).split(':')[0])
                if hour < 13:
                    morning += 1
                else:
                    afternoon += 1
            except:
                pass
        
        total = morning + afternoon
        if total > 0:
            morning_ratio = morning / total
            if morning_ratio < 0.35 or morning_ratio > 0.65:
                imbalance = abs(0.5 - morning_ratio)
                violations += int(imbalance * 15)
        
        return violations
    
    def _time_overlaps_break(self, timeslot, break_start, break_end):
        """Check if timeslot overlaps with break time"""
        try:
            slot_start = timeslot.start_time
            slot_end = timeslot.end_time
            
            if isinstance(break_start, str):
                break_start = datetime.strptime(break_start, '%H:%M').time()
            if isinstance(break_end, str):
                break_end = datetime.strptime(break_end, '%H:%M').time()
            
            return not (slot_end <= break_start or slot_start >= break_end)
        except:
            return False


class DivisionSpecificGeneticAlgorithm:
    """Division-specific genetic algorithm that generates separate timetables per division"""
    
    def __init__(self, target_divisions=None, incharge_role="department", 
                 population_size=30, generations=150, mutation_rate=0.2):
        self.target_divisions = target_divisions or []
        self.incharge_role = incharge_role  # "first_year" or "department"
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        
        self.system_config = self._load_system_configuration()
        self._initialize_data()
        
        # Store division-specific timetables
        self.division_timetables = {}
        self.active_division_schedules = {}  # For cross-division conflict checking
    
    def generate_all_division_timetables(self):
        """Generate separate timetable for each target division"""
        logger.info(f"Generating timetables for {len(self.target_divisions)} divisions...")
        
        results = {}
        
        for division in self.target_divisions:
            logger.info(f"Generating timetable for Division: {division.name}, Year: {division.year.name}")
            
            # Generate timetable for this specific division
            division_timetable = self._generate_division_timetable(division)
            
            # Store result
            results[division.id] = {
                'division': division,
                'timetable': division_timetable,
                'fitness_score': division_timetable.fitness_score if division_timetable else None,
                'violations': division_timetable.violations if division_timetable else {}
            }
            
            # Add to active schedules for cross-division conflict checking
            if division_timetable:
                self.active_division_schedules[division.id] = division_timetable
        
        return results
    
    def _generate_division_timetable(self, division):
        """Generate timetable for a specific division"""
        try:
            # Filter subjects for this division
            division_subjects = Subject.objects.filter(
                year=division.year,
                division=division
            )
            
            logger.info(f"Found {len(division_subjects)} subjects for {division.name}")
            
            # Create population for this division
            population = []
            for _ in range(self.population_size):
                chromosome = self._create_division_chromosome(division, division_subjects)
                population.append(chromosome)
            
            # Run genetic algorithm for this division
            best_solution = self._evolve_division_population(population, division)
            
            return best_solution
            
        except Exception as e:
            logger.error(f"Error generating timetable for division {division.name}: {e}")
            return None
    
    def _create_division_chromosome(self, division, subjects):
        """Create chromosome specific to a division"""
        genes = []
        
        for subject in subjects:
            sessions_needed = getattr(subject, 'sessions_per_week', 3)
            
            # Get batches for this division
            division_batches = Batch.objects.filter(division=division)
            
            for batch in division_batches:
                for session_num in range(sessions_needed):
                    teacher = self._select_teacher_for_subject(subject)
                    location = self._select_location_for_subject(subject)
                    timeslot = self._select_valid_timeslot_for_division(subject, teacher, division)
                    
                    if teacher and timeslot:
                        genes.append((subject.id, teacher.id, location, timeslot.id, batch.id))
        
        return DivisionSpecificChromosome(genes, division)
    
    def _evolve_division_population(self, population, division):
        """Evolve population for specific division"""
        for generation in range(self.generations):
            # Evaluate fitness
            for chromosome in population:
                chromosome.fitness(self)
            
            # Sort by fitness
            population.sort(key=lambda x: x.fitness_score, reverse=True)
            
            if generation % 20 == 0:
                best_fitness = population[0].fitness_score
                logger.info(f"Division {division.name} - Generation {generation}: Best fitness = {best_fitness}")
            
            # Evolution
            new_pop = population[:3]  # Keep best 3
            
            while len(new_pop) < self.population_size:
                parent1, parent2 = random.sample(population[:8], 2)
                child = self._crossover_division(parent1, parent2, division)
                self._mutate_division(child, division)
                new_pop.append(child)
            
            population = new_pop
        
        # Final evaluation
        for chromo in population:
            chromo.fitness(self)
        
        best = max(population, key=lambda x: x.fitness_score)
        logger.info(f"Division {division.name} final fitness: {best.fitness_score}")
        
        return best
    
    def get_other_divisions_schedules(self, current_division):
        """Get schedules of other divisions for conflict checking"""
        other_schedules = []
        for div_id, schedule in self.active_division_schedules.items():
            if div_id != current_division.id:
                other_schedules.append(schedule)
        return other_schedules
    
    def is_remedial_division(self, division):
        """Check if this division should handle remedial lecture"""
        # Only the first division of each year handles remedial
        try:
            first_division = Division.objects.filter(year=division.year).order_by('name').first()
            return division.id == first_division.id
        except:
            return False
    
    def _select_teacher_for_subject(self, subject):
        """Select teacher based on knowledge + willingness proficiency"""
        try:
            proficiencies = SubjectProficiency.objects.filter(subject=subject)
            
            scored_teachers = []
            for prof in proficiencies:
                knowledge = getattr(prof, 'knowledge_score', 5)
                willingness = getattr(prof, 'willingness_score', 5)
                combined_score = (knowledge * 0.6) + (willingness * 0.4)
                scored_teachers.append((prof.teacher, combined_score))
            
            if scored_teachers:
                scored_teachers.sort(key=lambda x: x[1], reverse=True)
                top_candidates = scored_teachers[:3]
                return random.choice(top_candidates)[0]
                
        except Exception as e:
            logger.warning(f"Error in teacher selection: {e}")
        
        return random.choice(self.teachers) if self.teachers else None
    
    def _select_location_for_subject(self, subject):
        """Select location with equipment matching"""
        try:
            is_lab = getattr(subject, 'requires_lab', False)
            equipment_needed = getattr(subject, 'equipment_requirements', [])
            
            if is_lab:
                suitable_labs = []
                for lab in self.labs:
                    lab_equipment = getattr(lab, 'available_equipment', [])
                    if not equipment_needed or set(equipment_needed).issubset(set(lab_equipment)):
                        suitable_labs.append(lab)
                return random.choice(suitable_labs).id if suitable_labs else None
            else:
                suitable_rooms = []
                for room in self.rooms:
                    room_equipment = getattr(room, 'available_equipment', [])
                    if not equipment_needed or set(equipment_needed).issubset(set(room_equipment)):
                        suitable_rooms.append(room)
                return random.choice(suitable_rooms).id if suitable_rooms else None
                
        except Exception as e:
            logger.warning(f"Error selecting location: {e}")
        
        return None
    
    def _select_valid_timeslot_for_division(self, subject, teacher, division):
        """Select valid timeslot for division avoiding project conflicts"""
        try:
            available_slots = []
            
            for timeslot in self.timeslots:
                # Check if slot is reserved for project work
                if self._is_slot_reserved_for_projects(timeslot, division.year):
                    continue
                    
                available_slots.append(timeslot)
            
            # Apply teacher preferences
            if teacher and available_slots:
                preferred_slots = self._filter_by_teacher_preference(available_slots, teacher, subject)
                if preferred_slots:
                    available_slots = preferred_slots
            
            return random.choice(available_slots) if available_slots else None
            
        except Exception as e:
            logger.warning(f"Error selecting timeslot: {e}")
            return random.choice(self.timeslots) if self.timeslots else None
    
    def _is_slot_reserved_for_projects(self, timeslot, year):
        """Check if timeslot is reserved for project work"""
        try:
            project_configs = ProjectWork.objects.filter(year=year)
            for project_config in project_configs:
                reserved_slots = project_config.dedicated_timeslots.all()
                if timeslot in reserved_slots:
                    return True
        except:
            pass
        return False
    
    def _filter_by_teacher_preference(self, timeslots, teacher, subject):
        """Filter timeslots by teacher preferences"""
        try:
            preferences = getattr(teacher, 'preferences', {})
            if not preferences:
                return timeslots
            
            is_lab = getattr(subject, 'requires_lab', False)
            preferred_slots = []
            
            for slot in timeslots:
                hour = int(str(slot.start_time).split(':')[0])
                is_morning = hour < 13
                
                if is_lab:
                    lab_pref = preferences.get('lab_time_preference', 'no_preference')
                    if (lab_pref == 'morning' and is_morning) or \
                       (lab_pref == 'afternoon' and not is_morning) or \
                       lab_pref == 'no_preference':
                        preferred_slots.append(slot)
                else:
                    lecture_pref = preferences.get('lecture_time_preference', 'no_preference')
                    if (lecture_pref == 'morning' and is_morning) or \
                       (lecture_pref == 'afternoon' and not is_morning) or \
                       lecture_pref == 'no_preference':
                        preferred_slots.append(slot)
            
            return preferred_slots if preferred_slots else timeslots
            
        except:
            return timeslots
    
    def _crossover_division(self, parent1, parent2, division):
        """Crossover operation for division-specific chromosomes"""
        if not parent1.genes or not parent2.genes:
            return parent1
        
        point = random.randint(1, min(len(parent1.genes), len(parent2.genes)) - 1)
        child_genes = parent1.genes[:point] + parent2.genes[point:]
        return DivisionSpecificChromosome(child_genes, division)
    
    def _mutate_division(self, chromosome, division):
        """Mutation operation for division-specific chromosome"""
        if random.random() > self.mutation_rate or not chromosome.genes:
            return
        
        idx = random.randint(0, len(chromosome.genes) - 1)
        gene = list(chromosome.genes[idx])
        
        # Mutate teacher
        if random.random() < 0.4:
            try:
                subject = Subject.objects.get(id=gene[0])
                new_teacher = self._select_teacher_for_subject(subject)
                if new_teacher:
                    gene[1] = new_teacher.id
            except:
                pass
        
        # Mutate timeslot
        if random.random() < 0.4:
            try:
                subject = Subject.objects.get(id=gene[0])
                new_timeslot = self._select_valid_timeslot_for_division(subject, None, division)
                if new_timeslot:
                    gene[3] = new_timeslot.id
            except:
                pass
        
        chromosome.genes[idx] = tuple(gene)
        chromosome.fitness_score = None
    
    def _initialize_data(self):
        """Initialize data for division-specific processing"""
        try:
            self.subjects = list(Subject.objects.all())
            self.teachers = list(Teacher.objects.all())
            self.rooms = list(Room.objects.all())
            self.labs = list(Lab.objects.all())
            self.timeslots = list(TimeSlot.objects.all())
            
            logger.info(f"Loaded: {len(self.subjects)} subjects, "
                       f"{len(self.teachers)} teachers, "
                       f"{len(self.rooms + self.labs)} rooms, "
                       f"{len(self.timeslots)} timeslots")
            
        except Exception as e:
            logger.error(f"Failed to initialize data: {e}")
            raise
    
    def _load_system_configuration(self):
        """Load system configuration"""
        try:
            config = SystemConfiguration.objects.filter(is_active=True).first()
            if not config:
                config = SystemConfiguration.objects.create()
            return config
        except Exception as e:
            logger.warning(f"Could not load system configuration: {e}")
            return self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        class DefaultConfig:
            break_start_time = time(13, 0)
            break_end_time = time(13, 45)
            default_lab_duration_hours = 2
            lecture_duration_hours = 1
            project_half_days_enabled = True
            remedial_lectures_per_week = 1
            remedial_afternoon_preferred = True
            strict_equipment_matching = True
        
        return DefaultConfig()


# Usage Example:
"""
# For Department Incharge (SE, TE, BE)
department_divisions = Division.objects.filter(
    year__name__in=['SE', 'TE', 'BE']
)

dept_algorithm = DivisionSpecificGeneticAlgorithm(
    target_divisions=list(department_divisions),
    incharge_role="department"
)

dept_results = dept_algorithm.generate_all_division_timetables()

# For First Year Incharge
first_year_divisions = Division.objects.filter(
    year__name='FE'  # First year
)

fy_algorithm = DivisionSpecificGeneticAlgorithm(
    target_divisions=list(first_year_divisions),
    incharge_role="first_year"
)

fy_results = fy_algorithm.generate_all_division_timetables()

# Results structure:
for division_id, result in dept_results.items():
    division = result['division']
    timetable = result['timetable'] 
    fitness = result['fitness_score']
    violations = result['violations']
    
    print(f"Division {division.name} - Fitness: {fitness}")
    print(f"Violations: {violations['total']}")
"""