# CORRECTED TIMETABLE ALGORITHM - Based on PDF Requirements

import random
import copy
from collections import defaultdict, Counter
from datetime import datetime, timedelta, time
from typing import List, Dict, Tuple, Optional, Set
import logging

from .models import (
    Teacher, Subject, Room, Lab, TimeSlot, Session, Year, Division, Batch,
    SubjectProficiency, SystemConfiguration, ProjectWork
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CorrectedChromosome:
    """Corrected chromosome based on actual PDF requirements"""
    
    def __init__(self, genes=None):
        self.genes = genes if genes is not None else []
        self.fitness_score = None
        self.violations = {}
        self.constraint_details = {}
    
    def fitness(self, algorithm_instance):
        """Calculate fitness with corrected constraints from PDF"""
        if self.fitness_score is not None:
            return self.fitness_score
        
        violations = 0
        self.violations = {}
        self.constraint_details = {}
        
        try:
            # 1-2. Equal faculty load + Required sessions per batch
            violations += self._check_faculty_load_distribution(algorithm_instance)
            
            # 3-7. Conflict prevention (faculty, class, student, room)
            violations += self._check_all_conflicts(algorithm_instance)
            
            # 8. Required sessions per subject
            violations += self._check_required_sessions()
            
            # 10. Teacher time preferences (morning/afternoon)
            violations += self._check_teacher_preferences()
            
            # 11. AUTOMATIC Morning/afternoon balance (internal logic)
            violations += self._auto_balance_morning_afternoon()
            
            # 14. Break time enforcement
            violations += self._check_break_times(algorithm_instance)
            
            # 15-16. Lab constraints with equipment-specific rooms
            violations += self._check_lab_constraints_with_equipment(algorithm_instance)
            
            # 17. MISSING: Dedicated project work half-days
            violations += self._check_project_work_constraints(algorithm_instance)
            
            # 20. CORRECTED: Remedial lecture (one general lecture per week)
            violations += self._check_remedial_lecture_constraint(algorithm_instance)
            
            # 21. Cross-year professor conflicts
            violations += self._check_cross_year_conflicts()
            
            # REMOVED: Manual morning/afternoon settings
            # REMOVED: Teacher workload limit inputs (auto-calculated)
            
        except Exception as e:
            logger.error(f"Error in fitness calculation: {e}")
            violations += 1000
        
        self.violations['total'] = violations
        self.fitness_score = -violations
        return self.fitness_score
    
    def _check_faculty_load_distribution(self, algorithm_instance):
        """Constraint 1 & 9: Auto-distribute faculty load fairly (no manual limits)"""
        violations = 0
        teacher_loads = defaultdict(int)
        
        for gene in self.genes:
            teacher_loads[gene[1]] += 1
        
        if not teacher_loads:
            return violations
        
        # Auto-calculate fair distribution (no manual input)
        total_sessions = sum(teacher_loads.values())
        num_teachers = len(teacher_loads)
        ideal_load = total_sessions / num_teachers if num_teachers > 0 else 0
        
        # Allow 20% variance from ideal load
        tolerance = max(2, int(ideal_load * 0.2))
        
        for teacher_id, load in teacher_loads.items():
            deviation = abs(load - ideal_load)
            if deviation > tolerance:
                violations += int(deviation * 5)
        
        self.constraint_details['faculty_load_distribution'] = {
            'ideal_load': ideal_load,
            'actual_loads': dict(teacher_loads),
            'tolerance': tolerance
        }
        return violations
    
    def _check_all_conflicts(self, algorithm_instance):
        """Constraints 3-7: All conflict prevention"""
        violations = 0
        
        # Check teacher conflicts (constraints 3 & 5)
        teacher_times = defaultdict(list)
        for gene in self.genes:
            teacher_times[gene[1]].append(gene[3])
        
        for times in teacher_times.values():
            time_counts = Counter(times)
            conflicts = sum(max(0, count - 1) for count in time_counts.values())
            violations += conflicts * 30  # Heavy penalty
        
        # Check room conflicts (constraint 7)
        room_times = defaultdict(list)
        for gene in self.genes:
            if gene[2]:  # If room assigned
                room_times[gene[2]].append(gene[3])
        
        for times in room_times.values():
            time_counts = Counter(times)
            conflicts = sum(max(0, count - 1) for count in time_counts.values())
            violations += conflicts * 25
        
        # Check student group conflicts (constraints 4 & 6)
        batch_times = defaultdict(list)
        for gene in self.genes:
            try:
                subject = Subject.objects.get(id=gene[0])
                # Use batch information for finer conflict detection
                batch_key = f"{subject.year.name}_{subject.division.name}_{gene[4]}"  # gene[4] is batch
                batch_times[batch_key].append(gene[3])
            except:
                pass
        
        for times in batch_times.values():
            time_counts = Counter(times)
            conflicts = sum(max(0, count - 1) for count in time_counts.values())
            violations += conflicts * 35  # Very heavy penalty for student conflicts
        
        return violations
    
    def _auto_balance_morning_afternoon(self):
        """Constraint 11: AUTOMATIC morning/afternoon balance (no user input)"""
        violations = 0
        morning = afternoon = 0
        
        for gene in self.genes:
            try:
                timeslot = TimeSlot.objects.get(id=gene[3])
                hour = int(str(timeslot.start_time).split(':')[0])
                if hour < 13:  # Before 1 PM
                    morning += 1
                else:
                    afternoon += 1
            except:
                pass
        
        total = morning + afternoon
        if total > 0:
            morning_ratio = morning / total
            # Automatically aim for 40-60% balance (flexible)
            if morning_ratio < 0.35 or morning_ratio > 0.65:
                imbalance = abs(0.5 - morning_ratio)
                violations += int(imbalance * 15)  # Moderate penalty
        
        self.constraint_details['morning_afternoon_balance'] = {
            'morning': morning,
            'afternoon': afternoon,
            'ratio': morning / total if total > 0 else 0
        }
        return violations
    
    def _check_lab_constraints_with_equipment(self, algorithm_instance):
        """Constraints 15-16: Lab duration + Equipment-specific room assignment"""
        violations = 0
        
        # Group labs by equipment type and time
        equipment_schedule = defaultdict(lambda: defaultdict(list))
        
        for gene in self.genes:
            try:
                subject = Subject.objects.get(id=gene[0])
                if getattr(subject, 'requires_lab', False):
                    room_id = gene[2]
                    timeslot = TimeSlot.objects.get(id=gene[3])
                    
                    # Get room equipment category
                    room_equipment = self._get_room_equipment_category(room_id, algorithm_instance)
                    
                    # Check if subject matches room equipment
                    subject_equipment_needed = getattr(subject, 'equipment_requirements', [])
                    
                    if subject_equipment_needed and room_equipment:
                        if not set(subject_equipment_needed).issubset(set(room_equipment)):
                            violations += 20  # Equipment mismatch
                    
                    # Constraint 16: Cross-year lab conflict with equipment
                    year_name = subject.year.name
                    equipment_schedule[room_equipment][timeslot.id].append({
                        'year': year_name,
                        'subject': subject.name,
                        'batch': gene[4]
                    })
                    
            except Exception as e:
                logger.warning(f"Error in lab constraint check: {e}")
        
        # Check equipment-based conflicts across years
        for equipment_type, schedule in equipment_schedule.items():
            for timeslot_id, sessions in schedule.items():
                if len(sessions) > 1:
                    # Check if different years are using same equipment type
                    years = set(s['year'] for s in sessions)
                    if len(years) > 1:
                        violations += 25 * (len(sessions) - 1)  # Heavy penalty
        
        return violations
    
    def _check_project_work_constraints(self, algorithm_instance):
        """Constraint 17: MISSING - Dedicated project work half-days"""
        violations = 0
        
        try:
            # Get project work configuration
            project_configs = ProjectWork.objects.all()
            
            for project_config in project_configs:
                year = project_config.year
                required_half_days = project_config.half_days_per_week
                dedicated_timeslots = project_config.dedicated_timeslots.all()
                
                # Check if project timeslots are protected (no regular classes)
                for timeslot in dedicated_timeslots:
                    conflicting_sessions = 0
                    
                    for gene in self.genes:
                        try:
                            subject = Subject.objects.get(id=gene[0])
                            if subject.year == year and gene[3] == timeslot.id:
                                # Regular subject scheduled during project time
                                if not getattr(subject, 'is_project_work', False):
                                    conflicting_sessions += 1
                        except:
                            pass
                    
                    violations += conflicting_sessions * 30  # Heavy penalty
                    
        except Exception as e:
            logger.warning(f"Error checking project work constraints: {e}")
        
        return violations
    
    def _check_remedial_lecture_constraint(self, algorithm_instance):
        """Constraint 20: CORRECTED - One general remedial lecture per week (any professor)"""
        violations = 0
        
        try:
            # Count total remedial lectures across all schedules
            remedial_count = 0
            
            for gene in self.genes:
                try:
                    subject = Subject.objects.get(id=gene[0])
                    if getattr(subject, 'is_remedial', False):
                        remedial_count += 1
                except:
                    pass
            
            # Should have exactly one remedial lecture per week for the entire department
            if remedial_count == 0:
                violations += 15  # Missing remedial lecture
            elif remedial_count > 1:
                violations += (remedial_count - 1) * 10  # Too many remedial lectures
                
            self.constraint_details['remedial_lectures'] = remedial_count
            
        except Exception as e:
            logger.warning(f"Error checking remedial constraint: {e}")
        
        return violations
    
    def _check_teacher_preferences(self):
        """Constraint 10: Teacher time preferences"""
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
    
    def _check_break_times(self, algorithm_instance):
        """Constraint 14: Break time enforcement"""
        violations = 0
        
        try:
            break_start = algorithm_instance.system_config.break_start_time
            break_end = algorithm_instance.system_config.break_end_time
            
            for gene in self.genes:
                try:
                    timeslot = TimeSlot.objects.get(id=gene[3])
                    if self._time_overlaps_break(timeslot, break_start, break_end):
                        violations += 25  # Heavy penalty for break violations
                except:
                    pass
                    
        except Exception as e:
            logger.warning(f"Error checking break times: {e}")
        
        return violations
    
    def _check_required_sessions(self):
        """Constraint 8: Required sessions per subject"""
        violations = 0
        subject_counts = Counter(gene[0] for gene in self.genes)
        
        for subject_id, count in subject_counts.items():
            try:
                subject = Subject.objects.get(id=subject_id)
                required = getattr(subject, 'sessions_per_week', 3)
                if count < required:
                    violations += (required - count) * 8
                elif count > required + 1:  # Allow 1 extra session flexibility
                    violations += (count - required - 1) * 3
            except:
                pass
        
        return violations
    
    def _check_cross_year_conflicts(self):
        """Constraint 21: Cross-year professor assignment conflicts"""
        violations = 0
        teacher_year_schedule = defaultdict(lambda: defaultdict(list))
        
        for gene in self.genes:
            try:
                subject = Subject.objects.get(id=gene[0])
                teacher_year_schedule[gene[1]][subject.year.name].append(gene[3])
            except:
                pass
        
        for teacher_id, year_schedules in teacher_year_schedule.items():
            if len(year_schedules) > 1:  # Teaching multiple years
                all_timeslots = []
                for year_timeslots in year_schedules.values():
                    all_timeslots.extend(year_timeslots)
                
                time_counts = Counter(all_timeslots)
                conflicts = sum(max(0, count - 1) for count in time_counts.values())
                violations += conflicts * 40  # Very heavy penalty
        
        return violations
    
    # Helper methods
    def _get_room_equipment_category(self, room_id, algorithm_instance):
        """Get equipment category for room"""
        try:
            for room in algorithm_instance.rooms + algorithm_instance.labs:
                if room.id == room_id:
                    return getattr(room, 'equipment_category', 'general')
        except:
            pass
        return 'general'
    
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


class CorrectedGeneticAlgorithm:
    """Corrected genetic algorithm based on PDF requirements"""
    
    def __init__(self, population_size=30, generations=150, mutation_rate=0.2):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.population = []
        self.best_solution = None
        self.system_config = self._load_system_configuration()
        
        # Initialize data
        self._initialize_data()
    
    def _load_system_configuration(self):
        """Load system configuration with corrected defaults"""
        try:
            config = SystemConfiguration.objects.filter(is_active=True).first()
            if not config:
                config = SystemConfiguration.objects.create()
            return config
        except Exception as e:
            logger.warning(f"Could not load system configuration: {e}")
            return self._create_corrected_default_config()
    
    def _create_corrected_default_config(self):
        """Create corrected default configuration"""
        class CorrectedConfig:
            # REMOVED: Manual teacher workload limits
            # Auto-calculated based on fair distribution
            
            # Time Constraints  
            break_start_time = time(13, 0)        # 1:00 PM
            break_end_time = time(13, 45)         # 1:45 PM
            
            # REMOVED: Manual morning/afternoon balance
            # Auto-balanced by algorithm (40-60% range)
            
            # Lab & Session Constraints
            default_lab_duration_hours = 2        # 2 hours as per constraint 15
            lecture_duration_hours = 1            # 1 hour as per constraint 13
            
            # Project Work (NEW - Constraint 17)
            project_half_days_enabled = True      # Enable project work scheduling
            
            # Remedial (CORRECTED - Constraint 20) 
            remedial_lectures_per_week = 1        # One general lecture for entire department
            remedial_afternoon_preferred = True   # Prefer afternoon scheduling
            
            # Cross-year lab conflicts (Constraint 16)
            strict_equipment_matching = True      # Enforce equipment-specific room assignment
            
        return CorrectedConfig()
    
    def _initialize_data(self):
        """Initialize data with batch support"""
        try:
            self.subjects = list(Subject.objects.all())
            self.teachers = list(Teacher.objects.all())
            self.rooms = list(Room.objects.all())
            self.labs = list(Lab.objects.all())
            self.timeslots = list(TimeSlot.objects.all())
            self.batches = list(Batch.objects.all()) if hasattr(Batch, 'objects') else []
            self.project_configs = list(ProjectWork.objects.all()) if hasattr(ProjectWork, 'objects') else []
            
            logger.info(f"Loaded: {len(self.subjects)} subjects, "
                       f"{len(self.teachers)} teachers, "
                       f"{len(self.rooms + self.labs)} rooms, "
                       f"{len(self.timeslots)} timeslots, "
                       f"{len(self.batches)} batches")
            
        except Exception as e:
            logger.error(f"Failed to initialize data: {e}")
            raise
    
    def _create_chromosome(self):
        """Create chromosome with corrected logic"""
        genes = []
        
        for subject in self.subjects:
            # Skip if this is a project work time slot
            if self._is_project_time_slot(subject):
                continue
                
            sessions_needed = getattr(subject, 'sessions_per_week', 3)
            
            for session_num in range(sessions_needed):
                # CORRECTED: Use knowledge + willingness scoring for teacher selection
                teacher = self._select_teacher_by_proficiency_scoring(subject)
                location = self._select_location_with_equipment_matching(subject)
                timeslot = self._select_valid_timeslot(subject, teacher)
                batch = self._get_subject_batch(subject)
                
                if teacher and timeslot:
                    genes.append((subject.id, teacher.id, location, timeslot.id, batch))
        
        # Add one remedial lecture (constraint 20)
        remedial_gene = self._create_remedial_gene()
        if remedial_gene:
            genes.append(remedial_gene)
        
        return CorrectedChromosome(genes)
    
    def _select_teacher_by_proficiency_scoring(self, subject):
        """CORRECTED: Use knowledge + willingness combined scoring"""
        try:
            proficiencies = SubjectProficiency.objects.filter(subject=subject)
            
            # Calculate combined score: (knowledge * 0.6) + (willingness * 0.4)
            scored_teachers = []
            for prof in proficiencies:
                knowledge = getattr(prof, 'knowledge_score', 5)
                willingness = getattr(prof, 'willingness_score', 5)
                combined_score = (knowledge * 0.6) + (willingness * 0.4)
                scored_teachers.append((prof.teacher, combined_score))
            
            if scored_teachers:
                # Sort by combined score and pick from top candidates
                scored_teachers.sort(key=lambda x: x[1], reverse=True)
                top_candidates = scored_teachers[:3]  # Top 3 candidates
                return random.choice(top_candidates)[0]
                
        except Exception as e:
            logger.warning(f"Error in teacher selection: {e}")
        
        return random.choice(self.teachers) if self.teachers else None
    
    def _select_location_with_equipment_matching(self, subject):
        """CORRECTED: Equipment-specific room matching (constraint 16)"""
        try:
            is_lab = getattr(subject, 'requires_lab', False)
            equipment_needed = getattr(subject, 'equipment_requirements', [])
            
            if is_lab:
                suitable_labs = []
                for lab in self.labs:
                    lab_equipment = getattr(lab, 'available_equipment', [])
                    
                    # Check equipment compatibility
                    if not equipment_needed or set(equipment_needed).issubset(set(lab_equipment)):
                        suitable_labs.append(lab)
                
                return random.choice(suitable_labs).id if suitable_labs else None
            
            else:
                # For regular classrooms
                suitable_rooms = []
                for room in self.rooms:
                    room_equipment = getattr(room, 'available_equipment', [])
                    
                    if not equipment_needed or set(equipment_needed).issubset(set(room_equipment)):
                        suitable_rooms.append(room)
                
                return random.choice(suitable_rooms).id if suitable_rooms else None
                
        except Exception as e:
            logger.warning(f"Error selecting location: {e}")
        
        return None
    
    def _is_project_time_slot(self, subject):
        """Check if timeslot is reserved for project work"""
        try:
            year = subject.year
            for project_config in self.project_configs:
                if project_config.year == year:
                    # This year has dedicated project time
                    return False  # Allow normal subjects, project slots handled separately
        except:
            pass
        return False
    
    def _create_remedial_gene(self):
        """Create remedial lecture gene (constraint 20 - corrected)"""
        try:
            # Create a general remedial subject/session
            available_teachers = list(self.teachers)
            available_rooms = list(self.rooms)
            afternoon_slots = [ts for ts in self.timeslots 
                             if int(str(ts.start_time).split(':')[0]) >= 13]
            
            if available_teachers and available_rooms and afternoon_slots:
                teacher = random.choice(available_teachers)
                room = random.choice(available_rooms)
                timeslot = random.choice(afternoon_slots)
                
                # Use special remedial subject ID (or create one)
                remedial_subject_id = self._get_remedial_subject_id()
                
                return (remedial_subject_id, teacher.id, room.id, timeslot.id, 1)
                
        except Exception as e:
            logger.warning(f"Error creating remedial gene: {e}")
        
        return None
    
    def _get_remedial_subject_id(self):
        """Get or create remedial subject"""
        try:
            remedial_subject = Subject.objects.filter(is_remedial=True).first()
            if remedial_subject:
                return remedial_subject.id
        except:
            pass
        
        # Return a placeholder ID or handle differently based on your model structure
        return -1  # Special ID for remedial
    
    def _get_subject_batch(self, subject):
        """Get appropriate batch for subject"""
        try:
            # Get batches for this subject's division
            division = subject.division
            batches = Batch.objects.filter(division=division)
            
            if batches:
                return random.choice(batches).id
        except:
            pass
        
        return 1  # Default batch
    
    def _select_valid_timeslot(self, subject, teacher):
        """Select valid timeslot avoiding project work conflicts"""
        try:
            available_slots = []
            
            for timeslot in self.timeslots:
                # Check if this slot is reserved for project work
                if self._is_slot_reserved_for_projects(timeslot, subject.year):
                    continue
                    
                available_slots.append(timeslot)
            
            # Apply teacher preferences if available
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
            for project_config in self.project_configs:
                if project_config.year == year:
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
    
    # Rest of the genetic algorithm methods remain similar but use CorrectedChromosome
    def run(self):
        """Run the corrected genetic algorithm"""
        logger.info("Starting Corrected Genetic Algorithm...")
        
        # Initialize population
        self.population = [self._create_chromosome() for _ in range(self.population_size)]
        
        for generation in range(self.generations):
            # Evaluate fitness
            for chromosome in self.population:
                chromosome.fitness(self)
            
            # Sort by fitness
            self.population.sort(key=lambda x: x.fitness_score, reverse=True)
            
            if generation % 10 == 0:
                best_fitness = self.population[0].fitness_score
                logger.info(f"Generation {generation}: Best fitness = {best_fitness}")
            
            # Evolution process (similar to original but uses corrected chromosome)
            new_pop = self.population[:5]  # Elitism
            
            while len(new_pop) < self.population_size:
                parent1, parent2 = random.sample(self.population[:10], 2)
                child = self._crossover(parent1, parent2)
                self._mutate(child)
                new_pop.append(child)
            
            self.population = new_pop
        
        # Final evaluation
        for chromo in self.population:
            chromo.fitness(self)
        
        best = max(self.population, key=lambda x: x.fitness_score)
        logger.info(f"Final best fitness: {best.fitness_score}")
        
        return best
    
    def _crossover(self, parent1, parent2):
        """Crossover operation"""
        if not parent1.genes or not parent2.genes:
            return parent1
        
        point = random.randint(1, min(len(parent1.genes), len(parent2.genes)) - 1)
        child_genes = parent1.genes[:point] + parent2.genes[point:]
        return CorrectedChromosome(child_genes)
    
    def _mutate(self, chromosome):
        """Mutation operation"""
        if random.random() > self.mutation_rate or not chromosome.genes:
            return
        
        idx = random.randint(0, len(chromosome.genes) - 1)
        gene = list(chromosome.genes[idx])
        
        # Mutate teacher (with proficiency consideration)
        if random.random() < 0.4:
            try:
                subject = Subject.objects.get(id=gene[0])
                new_teacher = self._select_teacher_by_proficiency_scoring(subject)
                if new_teacher:
                    gene[1] = new_teacher.id
            except:
                pass
        
        # Mutate timeslot (avoiding project work conflicts)
        if random.random() < 0.4:
            try:
                subject = Subject.objects.get(id=gene[0])
                new_timeslot = self._select_valid_timeslot(subject, None)
                if new_timeslot:
                    gene[3] = new_timeslot.id
            except:
                pass
        
        chromosome.genes[idx] = tuple(gene)
        chromosome.fitness_score = None  # Reset for recalculation


# Additional Models needed for corrected implementation
"""
Add these to your models.py:

class Batch(models.Model):
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)  # A1, A2, B1, etc.
    student_count = models.IntegerField(default=24)  # Max 24 as per PDF

class ProjectWork(models.Model):
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    half_days_per_week = models.IntegerField(default=1)  # Configurable
    dedicated_timeslots = models.ManyToManyField(TimeSlot)

# Add these fields to existing models:

class Subject(models.Model):
    # ... existing fields ...
    is_remedial = models.BooleanField(default=False)
    is_project_work = models.BooleanField(default=False)
    equipment_requirements = models.JSONField(default=list, blank=True)
    
class Room(models.Model):
    # ... existing fields ...
    available_equipment = models.JSONField(default=list, blank=True)
    equipment_category = models.CharField(max_length=50, default='general')
    
class Lab(models.Model):
    # ... existing fields ...
    available_equipment = models.JSONField(default=list, blank=True)
    equipment_category = models.CharField(max_length=50, default='computer')
    
class SubjectProficiency(models.Model):
    # ... existing fields ...
    knowledge_score = models.FloatField()  # 1-10 scale
    willingness_score = models.FloatField()  # 1-10 scale
    combined_score = models.FloatField()  # Auto-calculated
"""