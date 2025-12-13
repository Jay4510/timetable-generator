# Comprehensive Timetable Generation Algorithm
# Implements all identified constraints and fixes critical bugs

import random
import copy
from collections import defaultdict, Counter
from datetime import datetime, timedelta, time
from typing import List, Dict, Tuple, Optional, Set
import logging

from .models import (
    Teacher, Subject, Room, Lab, TimeSlot, Session, Year, Division,
    SubjectProficiency, SystemConfiguration, RemedialLecture
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedChromosome:
    """Enhanced chromosome with comprehensive constraint checking"""
    
    def __init__(self, genes=None):
        self.genes = genes if genes is not None else []
        self.fitness_score = None
        self.violations = {}
        self.constraint_details = {}
    
    def fitness(self, algorithm_instance):
        """Calculate fitness with all 15+ constraints implemented"""
        if self.fitness_score is not None:
            return self.fitness_score
        
        violations = 0
        self.violations = {}
        self.constraint_details = {}
        
        try:
            # 1. Teacher workload constraints (Requirements 1 & 9)
            violations += self._check_teacher_workload(algorithm_instance)
            
            # 2. Teacher time conflicts (Requirements 3 & 5)
            violations += self._check_teacher_conflicts()
            
            # 3. Room conflicts and capacity (Requirement 7 + Enhancement)
            violations += self._check_room_conflicts(algorithm_instance)
            
            # 4. Student group conflicts (Requirements 4 & 6)
            violations += self._check_student_conflicts()
            
            # 5. Required sessions per subject (Requirement 8)
            violations += self._check_required_sessions()
            
            # 6. Teacher-subject proficiency matching (Requirement 10)
            violations += self._check_proficiency_matching()
            
            # 7. Teacher timing preferences
            violations += self._check_teacher_preferences()
            
            # 8. Cross-year teaching conflicts
            violations += self._check_cross_year_conflicts()
            
            # 9. Morning/afternoon balance (Requirement 11)
            violations += self._check_time_balance()
            
            # 10. Break time enforcement (NEW - High Priority)
            violations += self._check_break_times(algorithm_instance)
            
            # 11. Lab duration constraints (NEW - High Priority)
            violations += self._check_lab_durations(algorithm_instance)
            
            # 12. Consecutive class limits (NEW - Medium Priority)
            violations += self._check_consecutive_limits(algorithm_instance)
            
            # 13. Equipment and resource requirements (NEW)
            violations += self._check_equipment_requirements(algorithm_instance)
            
            # 14. Remedial lecture scheduling (NEW)
            violations += self._check_remedial_scheduling(algorithm_instance)
            
            # 15. Time slot validation (NEW)
            violations += self._check_timeslot_validity(algorithm_instance)
            
        except Exception as e:
            logger.error(f"Error in fitness calculation: {e}")
            violations += 1000  # Heavy penalty for calculation errors
        
        self.violations['total'] = violations
        self.fitness_score = -violations
        return self.fitness_score
    
    def _check_teacher_workload(self, algorithm_instance):
        """Check both minimum and maximum teacher workload"""
        violations = 0
        teacher_loads = defaultdict(int)
        
        for gene in self.genes:
            teacher_loads[gene[1]] += 1
        
        max_sessions = algorithm_instance.system_config.max_sessions_per_teacher_per_week
        min_sessions = algorithm_instance.system_config.min_sessions_per_teacher_per_week
        
        for teacher_id, load in teacher_loads.items():
            if load > max_sessions:
                violations += (load - max_sessions) * 15  # Heavy penalty for overload
            elif load < min_sessions:
                violations += (min_sessions - load) * 8   # Moderate penalty for underload
        
        self.constraint_details['teacher_workload'] = teacher_loads
        return violations
    
    def _check_teacher_conflicts(self):
        """Check for teacher time conflicts"""
        violations = 0
        teacher_times = defaultdict(list)
        
        for gene in self.genes:
            teacher_times[gene[1]].append(gene[3])
        
        for teacher_id, times in teacher_times.items():
            time_counts = Counter(times)
            conflicts = sum(max(0, count - 1) for count in time_counts.values())
            violations += conflicts * 25  # Heavy penalty for conflicts
        
        self.constraint_details['teacher_conflicts'] = sum(
            max(0, len(times) - len(set(times))) for times in teacher_times.values()
        )
        return violations
    
    def _check_room_conflicts(self, algorithm_instance):
        """Check room conflicts and capacity constraints"""
        violations = 0
        room_times = defaultdict(list)
        capacity_violations = 0
        
        for gene in self.genes:
            room_id = gene[2]
            if room_id:
                room_times[room_id].append(gene[3])
                
                # Check room capacity
                try:
                    subject = Subject.objects.get(id=gene[0])
                    student_count = self._get_student_count(subject)
                    room_capacity = self._get_room_capacity(room_id, algorithm_instance)
                    
                    if student_count > room_capacity:
                        capacity_violations += (student_count - room_capacity) * 10
                        
                except Exception as e:
                    logger.warning(f"Error checking room capacity: {e}")
                    violations += 5  # Penalty for missing data
        
        # Check time conflicts
        for times in room_times.values():
            time_counts = Counter(times)
            conflicts = sum(max(0, count - 1) for count in time_counts.values())
            violations += conflicts * 20
        
        violations += capacity_violations
        self.constraint_details['room_capacity_violations'] = capacity_violations
        return violations
    
    def _check_student_conflicts(self):
        """Check student group conflicts"""
        violations = 0
        division_times = defaultdict(list)
        
        for gene in self.genes:
            try:
                subject = Subject.objects.get(id=gene[0])
                division_key = f"{subject.year.name}_{subject.division.name}"
                division_times[division_key].append(gene[3])
            except Exception as e:
                logger.warning(f"Error in student conflict check: {e}")
        
        for times in division_times.values():
            time_counts = Counter(times)
            conflicts = sum(max(0, count - 1) for count in time_counts.values())
            violations += conflicts * 30  # Very heavy penalty
        
        return violations
    
    def _check_required_sessions(self):
        """Check if subjects have required number of sessions"""
        violations = 0
        subject_counts = Counter(gene[0] for gene in self.genes)
        
        for subject_id, count in subject_counts.items():
            try:
                subject = Subject.objects.get(id=subject_id)
                required = getattr(subject, 'sessions_per_week', 3)
                if count < required:
                    violations += (required - count) * 8
                elif count > required:
                    violations += (count - required) * 3  # Light penalty for excess
            except Exception as e:
                logger.warning(f"Error checking required sessions: {e}")
        
        return violations
    
    def _check_proficiency_matching(self):
        """Enhanced proficiency matching"""
        violations = 0
        
        for gene in self.genes:
            try:
                prof = SubjectProficiency.objects.filter(
                    teacher_id=gene[1], subject_id=gene[0]
                ).first()
                
                if not prof:
                    violations += 12  # Heavy penalty for no proficiency data
                else:
                    score = prof.combined_score
                    if score < 4.0:
                        violations += 15  # Very heavy penalty for poor match
                    elif score < 6.0:
                        violations += 10  # Heavy penalty for below average
                    elif score < 7.5:
                        violations += 4   # Light penalty for average
                    # No penalty for good matches (7.5+)
                        
            except Exception as e:
                logger.warning(f"Error in proficiency check: {e}")
                violations += 8
        
        return violations
    
    def _check_teacher_preferences(self):
        """Check teacher timing preferences"""
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
                            violations += 6
                        elif lab_pref == 'afternoon' and is_morning:
                            violations += 6
                    else:
                        lecture_pref = preferences.get('lecture_time_preference', 'no_preference')
                        if lecture_pref == 'morning' and not is_morning:
                            violations += 4
                        elif lecture_pref == 'afternoon' and is_morning:
                            violations += 4
                            
            except Exception as e:
                logger.warning(f"Error checking teacher preferences: {e}")
        
        return violations
    
    def _check_cross_year_conflicts(self):
        """Check cross-year teaching conflicts"""
        violations = 0
        teacher_year_schedule = defaultdict(lambda: defaultdict(list))
        
        for gene in self.genes:
            try:
                subject = Subject.objects.get(id=gene[0])
                teacher_year_schedule[gene[1]][subject.year.name].append(gene[3])
            except Exception as e:
                logger.warning(f"Error in cross-year check: {e}")
        
        for teacher_id, year_schedules in teacher_year_schedule.items():
            if len(year_schedules) > 1:
                all_timeslots = []
                for year_timeslots in year_schedules.values():
                    all_timeslots.extend(year_timeslots)
                
                time_counts = Counter(all_timeslots)
                conflicts = sum(max(0, count - 1) for count in time_counts.values())
                violations += conflicts * 35  # Very heavy penalty
        
        return violations
    
    def _check_time_balance(self):
        """Check morning/afternoon balance"""
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
            except Exception as e:
                logger.warning(f"Error in time balance check: {e}")
        
        total = morning + afternoon
        if total > 0:
            ratio = morning / total
            target_ratio = 0.5  # 50% balance
            if abs(ratio - target_ratio) > 0.25:  # Allow 25% deviation
                violations += int(abs(ratio - target_ratio) * 40)
        
        return violations
    
    def _check_break_times(self, algorithm_instance):
        """NEW: Check break time enforcement"""
        violations = 0
        teacher_schedules = defaultdict(list)
        
        # Group by teacher
        for gene in self.genes:
            try:
                timeslot = TimeSlot.objects.get(id=gene[3])
                teacher_schedules[gene[1]].append(timeslot)
            except Exception as e:
                logger.warning(f"Error in break time check: {e}")
        
        # Check each teacher's schedule for break violations
        break_start = algorithm_instance.system_config.break_start_time
        break_end = algorithm_instance.system_config.break_end_time
        
        for teacher_id, timeslots in teacher_schedules.items():
            # Sort timeslots by start time
            sorted_slots = sorted(timeslots, key=lambda x: x.start_time)
            
            # Check for classes during break time
            for slot in sorted_slots:
                if self._time_overlaps_break(slot, break_start, break_end):
                    violations += 20  # Heavy penalty for break violations
        
        return violations
    
    def _check_lab_durations(self, algorithm_instance):
        """NEW: Check lab duration constraints"""
        violations = 0
        lab_sessions = defaultdict(list)
        
        # Collect all lab sessions
        for gene in self.genes:
            try:
                subject = Subject.objects.get(id=gene[0])
                if getattr(subject, 'requires_lab', False):
                    timeslot = TimeSlot.objects.get(id=gene[3])
                    lab_sessions[gene[0]].append(timeslot)
            except Exception as e:
                logger.warning(f"Error in lab duration check: {e}")
        
        # Check if lab sessions are in continuous blocks
        min_lab_duration = algorithm_instance.system_config.default_lab_duration_hours
        
        for subject_id, timeslots in lab_sessions.items():
            if len(timeslots) > 1:
                # Check if timeslots form continuous blocks
                sorted_slots = sorted(timeslots, key=lambda x: x.start_time)
                for i in range(len(sorted_slots) - 1):
                    gap = self._calculate_time_gap(sorted_slots[i], sorted_slots[i + 1])
                    if gap > timedelta(minutes=15):  # Allow 15-minute buffer
                        violations += 15  # Penalty for fragmented labs
        
        return violations
    
    def _check_consecutive_limits(self, algorithm_instance):
        """NEW: Check consecutive class limits for teachers"""
        violations = 0
        teacher_schedules = defaultdict(list)
        
        # Group by teacher and day
        for gene in self.genes:
            try:
                timeslot = TimeSlot.objects.get(id=gene[3])
                day_of_week = getattr(timeslot, 'day_of_week', 'Monday')  # Default fallback
                teacher_schedules[f"{gene[1]}_{day_of_week}"].append(timeslot)
            except Exception as e:
                logger.warning(f"Error in consecutive check: {e}")
        
        max_consecutive = 4  # Maximum 4 consecutive hours
        
        for teacher_day, timeslots in teacher_schedules.items():
            if len(timeslots) > max_consecutive:
                # Sort and check for consecutive blocks
                sorted_slots = sorted(timeslots, key=lambda x: x.start_time)
                consecutive_count = self._count_consecutive_slots(sorted_slots)
                
                if consecutive_count > max_consecutive:
                    violations += (consecutive_count - max_consecutive) * 12
        
        return violations
    
    def _check_equipment_requirements(self, algorithm_instance):
        """NEW: Check equipment and resource requirements"""
        violations = 0
        
        for gene in self.genes:
            try:
                subject = Subject.objects.get(id=gene[0])
                room_id = gene[2]
                
                if room_id and hasattr(subject, 'equipment_requirements'):
                    required_equipment = getattr(subject, 'equipment_requirements', [])
                    available_equipment = self._get_room_equipment(room_id, algorithm_instance)
                    
                    missing_equipment = set(required_equipment) - set(available_equipment)
                    violations += len(missing_equipment) * 8
                    
            except Exception as e:
                logger.warning(f"Error in equipment check: {e}")
        
        return violations
    
    def _check_remedial_scheduling(self, algorithm_instance):
        """NEW: Check remedial lecture scheduling"""
        violations = 0
        remedial_count = 0
        
        try:
            # Count remedial lectures in schedule
            for gene in self.genes:
                subject = Subject.objects.get(id=gene[0])
                if hasattr(subject, 'is_remedial') and subject.is_remedial:
                    remedial_count += 1
            
            # Check against configuration
            required_remedial = algorithm_instance.system_config.remedial_lectures_per_week
            if remedial_count < required_remedial:
                violations += (required_remedial - remedial_count) * 6
                
        except Exception as e:
            logger.warning(f"Error in remedial check: {e}")
        
        return violations
    
    def _check_timeslot_validity(self, algorithm_instance):
        """NEW: Check time slot validity"""
        violations = 0
        valid_timeslots = set(ts.id for ts in algorithm_instance.timeslots)
        
        for gene in self.genes:
            if gene[3] not in valid_timeslots:
                violations += 25  # Heavy penalty for invalid timeslots
        
        return violations
    
    # Helper methods
    def _get_student_count(self, subject):
        """Get student count for a subject"""
        try:
            return getattr(subject.division, 'student_count', 30)  # Default 30
        except:
            return 30
    
    def _get_room_capacity(self, room_id, algorithm_instance):
        """Get room capacity"""
        try:
            for room in algorithm_instance.rooms + algorithm_instance.labs:
                if room.id == room_id:
                    return getattr(room, 'capacity', 50)  # Default 50
        except:
            pass
        return 50  # Default capacity
    
    def _time_overlaps_break(self, timeslot, break_start, break_end):
        """Check if timeslot overlaps with break time"""
        try:
            slot_start = timeslot.start_time
            slot_end = timeslot.end_time
            
            # Convert to comparable time objects if needed
            if isinstance(break_start, str):
                break_start = datetime.strptime(break_start, '%H:%M').time()
            if isinstance(break_end, str):
                break_end = datetime.strptime(break_end, '%H:%M').time()
            
            return not (slot_end <= break_start or slot_start >= break_end)
        except:
            return False
    
    def _calculate_time_gap(self, slot1, slot2):
        """Calculate gap between two time slots"""
        try:
            return datetime.combine(datetime.today(), slot2.start_time) - \
                   datetime.combine(datetime.today(), slot1.end_time)
        except:
            return timedelta(hours=1)  # Default gap
    
    def _count_consecutive_slots(self, sorted_slots):
        """Count maximum consecutive time slots"""
        if not sorted_slots:
            return 0
        
        max_consecutive = 1
        current_consecutive = 1
        
        for i in range(1, len(sorted_slots)):
            gap = self._calculate_time_gap(sorted_slots[i-1], sorted_slots[i])
            if gap <= timedelta(minutes=15):  # 15-minute buffer
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1
        
        return max_consecutive
    
    def _get_room_equipment(self, room_id, algorithm_instance):
        """Get available equipment for a room"""
        try:
            for room in algorithm_instance.rooms + algorithm_instance.labs:
                if room.id == room_id:
                    return getattr(room, 'available_equipment', [])
        except:
            pass
        return []


class ComprehensiveGeneticAlgorithm:
    """Enhanced genetic algorithm with comprehensive constraint handling"""
    
    def __init__(self, population_size=25, generations=100, mutation_rate=0.15):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.population = []
        self.best_solution = None
        self.system_config = self._load_system_configuration()
        
        # Initialize data
        self._initialize_data()
        
        # Performance tracking
        self.generation_stats = []
        
    def _load_system_configuration(self):
        """Load system configuration with proper error handling"""
        try:
            config = SystemConfiguration.objects.filter(is_active=True).first()
            if not config:
                logger.info("No active configuration found, creating default")
                config = SystemConfiguration.objects.create()
            return config
        except Exception as e:
            logger.warning(f"Could not load system configuration: {e}")
            # Return object with default values
            return self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration object"""
        class DefaultConfig:
            max_sessions_per_teacher_per_week = 14
            min_sessions_per_teacher_per_week = 8
            default_lab_duration_hours = 2
            allow_cross_year_lab_conflicts = False
            remedial_lectures_per_week = 1
            morning_afternoon_balance_percentage = 50
            break_start_time = time(13, 0)  # 1:00 PM
            break_end_time = time(13, 45)   # 1:45 PM
        
        return DefaultConfig()
    
    def _initialize_data(self):
        """Initialize all required data with error handling"""
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
            
            if not all([self.subjects, self.teachers, self.timeslots]):
                raise ValueError("Missing essential data")
                
        except Exception as e:
            logger.error(f"Failed to initialize data: {e}")
            raise
    
    def _create_chromosome(self):
        """Create a chromosome with improved logic"""
        genes = []
        
        # Process all subjects (not just first 20)
        for subject in self.subjects:
            sessions_needed = min(getattr(subject, 'sessions_per_week', 3), 5)
            
            for session_num in range(sessions_needed):
                teacher = self._select_optimal_teacher(subject)
                location = self._select_optimal_location(subject)
                timeslot = self._select_optimal_timeslot(subject, teacher)
                batch = getattr(subject, 'batch_number', 1)
                
                if teacher and timeslot:
                    genes.append((subject.id, teacher.id, location, timeslot.id, batch))
        
        return EnhancedChromosome(genes)
    
    def _select_optimal_teacher(self, subject):
        """Select teacher based on proficiency and availability"""
        try:
            # Get proficiency ratings
            proficiencies = SubjectProficiency.objects.filter(
                subject=subject
            ).order_by('-combined_score')
            
            if proficiencies.exists():
                # Prefer highly proficient teachers
                top_teachers = [p.teacher for p in proficiencies 
                              if p.combined_score >= 7.0]
                
                if top_teachers:
                    return random.choice(top_teachers[:3])  # Top 3 choices
                else:
                    # Use any teacher with proficiency data
                    return random.choice([p.teacher for p in proficiencies[:5]])
            
            # Fallback to random teacher
            return random.choice(self.teachers) if self.teachers else None
            
        except Exception as e:
            logger.warning(f"Error selecting teacher: {e}")
            return random.choice(self.teachers) if self.teachers else None
    
    def _select_optimal_location(self, subject):
        """Select location based on subject requirements"""
        try:
            is_lab = getattr(subject, 'requires_lab', False)
            
            if is_lab and self.labs:
                # For labs, consider capacity and equipment
                suitable_labs = []
                for lab in self.labs:
                    capacity = getattr(lab, 'capacity', 50)
                    student_count = self._get_subject_student_count(subject)
                    
                    if capacity >= student_count:
                        suitable_labs.append(lab)
                
                if suitable_labs:
                    return random.choice(suitable_labs).id
                else:
                    return random.choice(self.labs).id if self.labs else None
            
            elif self.rooms:
                # For lectures, consider capacity
                suitable_rooms = []
                for room in self.rooms:
                    capacity = getattr(room, 'capacity', 50)
                    student_count = self._get_subject_student_count(subject)
                    
                    if capacity >= student_count:
                        suitable_rooms.append(room)
                
                if suitable_rooms:
                    return random.choice(suitable_rooms).id
                else:
                    return random.choice(self.rooms).id if self.rooms else None
                    
        except Exception as e:
            logger.warning(f"Error selecting location: {e}")
        
        return None
    
    def _select_optimal_timeslot(self, subject, teacher):
        """Select timeslot based on preferences and constraints"""
        try:
            is_lab = getattr(subject, 'requires_lab', False)
            available_slots = list(self.timeslots)
            
            if teacher and hasattr(teacher, 'preferences'):
                preferences = getattr(teacher, 'preferences', {})
                if preferences:
                    preferred_slots = []
                    
                    for slot in available_slots:
                        hour = int(str(slot.start_time).split(':')[0])
                        is_morning = hour < 13
                        
                        if is_lab:
                            lab_pref = preferences.get('lab_time_preference', 'no_preference')
                            if ((lab_pref == 'morning' and is_morning) or
                                (lab_pref == 'afternoon' and not is_morning) or
                                lab_pref == 'no_preference'):
                                preferred_slots.append(slot)
                        else:
                            lecture_pref = preferences.get('lecture_time_preference', 'no_preference')
                            if ((lecture_pref == 'morning' and is_morning) or
                                (lecture_pref == 'afternoon' and not is_morning) or
                                lecture_pref == 'no_preference'):
                                preferred_slots.append(slot)
                    
                    if preferred_slots:
                        available_slots = preferred_slots
            
            return random.choice(available_slots) if available_slots else None
            
        except Exception as e:
            logger.warning(f"Error selecting timeslot: {e}")
            return random.choice(self.timeslots) if self.timeslots else None
    
    def _get_subject_student_count(self, subject):
        """Get student count for subject"""
        try:
            return getattr(subject.division, 'student_count', 30)
        except:
            return 30
    
    def run(self):
        """Run the enhanced genetic algorithm"""
        logger.info("Starting Comprehensive Genetic Algorithm...")
        logger.info(f"Population: {self.population_size}, Generations: {self.generations}")
        
        # Initialize population
        try:
            self.population = [self._create_chromosome() for _ in range(self.population_size)]
            logger.info(f"Created initial population of {len(self.population)} chromosomes")
        except Exception as e:
            logger.error(f"Failed to create initial population: {e}")
            raise
        
        best_fitness_history = []
        
        for generation in range(self.generations):
            try:
                # Evaluate fitness
                for chromosome in self.population:
                    chromosome.fitness(self)
                
                # Sort by fitness (higher is better)
                self.population.sort(key=lambda x: x.fitness_score, reverse=True)
                
                # Track progress
                best_fitness = self.population[0].fitness_score
                avg_fitness = sum(c.fitness_score for c in self.population) / len(self.population)
                worst_fitness = self.population[-1].fitness_score
                
                best_fitness_history.append(best_fitness)
                
                # Log progress
                if generation % 10 == 0:
                    logger.info(f"Generation {generation}: "
                              f"Best={best_fitness:.2f}, "
                              f"Avg={avg_fitness:.2f}, "
                              f"Worst={worst_fitness:.2f}")
                
                # Check for convergence
                if len(best_fitness_history) > 10:
                    recent_improvement = (best_fitness_history[-1] - 
                                        best_fitness_history[-10])
                    if abs(recent_improvement) < 1:
                        logger.info(f"Converged at generation {generation}")
                        break
                
                # Create next generation
                next_population = []
                
                # Keep best performers (elitism)
                elite_count = max(2, self.population_size // 10)
                next_population.extend(self.population[:elite_count])
                
                # Generate offspring
                while len(next_population) < self.population_size:
                    # Tournament selection
                    parent1 = self._tournament_selection()
                    parent2 = self._tournament_selection()
                    
                    # Crossover
                    child = self._enhanced_crossover(parent1, parent2)
                    
                    # Mutation
                    if random.random() < self.mutation_rate:
                        self._enhanced_mutation(child)
                    
                    next_population.append(child)
                
                self.population = next_population
                
            except Exception as e:
                logger.error(f"Error in generation {generation}: {e}")
                break
        
        # Final evaluation and results
        for chromosome in self.population:
            chromosome.fitness(self)
        
        self.population.sort(key=lambda x: x.fitness_score, reverse=True)
        best_solution = self.population[0]
        
        logger.info(f"Algorithm completed. Best fitness: {best_solution.fitness_score}")
        logger.info(f"Total violations: {best_solution.violations.get('total', 'Unknown')}")
        
        # Log constraint details
        if hasattr(best_solution, 'constraint_details'):
            for constraint, value in best_solution.constraint_details.items():
                logger.info(f"{constraint}: {value}")
        
        return best_solution
    
    def _tournament_selection(self, tournament_size=3):
        """Tournament selection for parent choosing"""
        tournament = random.sample(self.population, 
                                 min(tournament_size, len(self.population)))
        return max(tournament, key=lambda x: x.fitness_score)
    
    def _enhanced_crossover(self, parent1, parent2):
        """Enhanced crossover with subject-aware gene selection"""
        if not parent1.genes or not parent2.genes:
            return copy.deepcopy(parent1 if parent1.genes else parent2)
        
        # Subject-based crossover
        subject_genes_p1 = defaultdict(list)
        subject_genes_p2 = defaultdict(list)
        
        for gene in parent1.genes:
            subject_genes_p1[gene[0]].append(gene)
        
        for gene in parent2.genes:
            subject_genes_p2[gene[0]].append(gene)
        
        child_genes = []
        all_subjects = set(subject_genes_p1.keys()) | set(subject_genes_p2.keys())
        
        for subject_id in all_subjects:
            genes_p1 = subject_genes_p1.get(subject_id, [])
            genes_p2 = subject_genes_p2.get(subject_id, [])
            
            # Choose genes from one parent for this subject
            if genes_p1 and genes_p2:
                chosen_genes = random.choice([genes_p1, genes_p2])
            elif genes_p1:
                chosen_genes = genes_p1
            else:
                chosen_genes = genes_p2
            
            child_genes.extend(chosen_genes)
        
        return EnhancedChromosome(child_genes)
    
    def _enhanced_mutation(self, chromosome):
        """Enhanced mutation with multiple strategies"""
        if not chromosome.genes:
            return
        
        mutation_strategies = [
            self._mutate_teacher,
            self._mutate_timeslot,
            self._mutate_location,
            self._swap_genes
        ]
        
        # Apply random mutation strategy
        strategy = random.choice(mutation_strategies)
        strategy(chromosome)
        
        # Reset fitness for recalculation
        chromosome.fitness_score = None
    
    def _mutate_teacher(self, chromosome):
        """Mutate teacher assignment"""
        if not chromosome.genes:
            return
            
        gene_idx = random.randint(0, len(chromosome.genes) - 1)
        gene = list(chromosome.genes[gene_idx])
        
        try:
            subject = Subject.objects.get(id=gene[0])
            new_teacher = self._select_optimal_teacher(subject)
            if new_teacher:
                gene[1] = new_teacher.id
                chromosome.genes[gene_idx] = tuple(gene)
        except Exception as e:
            logger.warning(f"Error in teacher mutation: {e}")
    
    def _mutate_timeslot(self, chromosome):
        """Mutate timeslot assignment"""
        if not chromosome.genes:
            return
            
        gene_idx = random.randint(0, len(chromosome.genes) - 1)
        gene = list(chromosome.genes[gene_idx])
        
        new_timeslot = random.choice(self.timeslots)
        gene[3] = new_timeslot.id
        chromosome.genes[gene_idx] = tuple(gene)
    
    def _mutate_location(self, chromosome):
        """Mutate location assignment"""
        if not chromosome.genes:
            return
            
        gene_idx = random.randint(0, len(chromosome.genes) - 1)
        gene = list(chromosome.genes[gene_idx])
        
        try:
            subject = Subject.objects.get(id=gene[0])
            new_location = self._select_optimal_location(subject)
            if new_location:
                gene[2] = new_location
                chromosome.genes[gene_idx] = tuple(gene)
        except Exception as e:
            logger.warning(f"Error in location mutation: {e}")
    
    def _swap_genes(self, chromosome):
        """Swap two genes"""
        if len(chromosome.genes) < 2:
            return
            
        idx1, idx2 = random.sample(range(len(chromosome.genes)), 2)
        chromosome.genes[idx1], chromosome.genes[idx2] = \
            chromosome.genes[idx2], chromosome.genes[idx1]
    
    def get_schedule_summary(self, solution):
        """Generate a comprehensive schedule summary"""
        if not solution or not solution.genes:
            return "No valid solution found"
        
        summary = []
        summary.append(f"Schedule Summary - Fitness Score: {solution.fitness_score}")
        summary.append(f"Total Violations: {solution.violations.get('total', 'Unknown')}")
        summary.append("="*60)
        
        # Group by day and time
        schedule_by_time = defaultdict(list)
        
        for gene in solution.genes:
            try:
                subject = Subject.objects.get(id=gene[0])
                teacher = Teacher.objects.get(id=gene[1])
                timeslot = TimeSlot.objects.get(id=gene[3])
                
                room_info = "TBD"
                if gene[2]:
                    try:
                        room = Room.objects.get(id=gene[2])
                        room_info = f"Room {room.name}"
                    except:
                        try:
                            lab = Lab.objects.get(id=gene[2])
                            room_info = f"Lab {lab.name}"
                        except:
                            room_info = f"Location {gene[2]}"
                
                time_key = f"{getattr(timeslot, 'day_of_week', 'Unknown')} {timeslot.start_time}"
                schedule_entry = f"{subject.name} | {teacher.name} | {room_info}"
                schedule_by_time[time_key].append(schedule_entry)
                
            except Exception as e:
                logger.warning(f"Error creating schedule summary: {e}")
        
        # Sort and display
        for time_key in sorted(schedule_by_time.keys()):
            summary.append(f"\n{time_key}:")
            for entry in schedule_by_time[time_key]:
                summary.append(f"  {entry}")
        
        return "\n".join(summary)


# Usage example and testing
if __name__ == "__main__":
    try:
        algorithm = ComprehensiveGeneticAlgorithm(
            population_size=30,
            generations=150,
            mutation_rate=0.2
        )
        
        best_solution = algorithm.run()
        
        if best_solution:
            print("\n" + "="*80)
            print("FINAL RESULTS")
            print("="*80)
            print(algorithm.get_schedule_summary(best_solution))
            
            # Additional analysis
            if hasattr(best_solution, 'constraint_details'):
                print("\nCONSTRAINT ANALYSIS:")
                for constraint, details in best_solution.constraint_details.items():
                    print(f"{constraint}: {details}")
        
    except Exception as e:
        logger.error(f"Algorithm execution failed: {e}")
        raise