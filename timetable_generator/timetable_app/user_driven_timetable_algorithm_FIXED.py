# FIXED USER-INPUT DRIVEN TIMETABLE ALGORITHM - VERSION 2.0
# Based on actual system workflow - TT Incharge configures everything
# File: user_driven_timetable_algorithm_FIXED.py
# 
# FIXES APPLIED (Oct 26, 2025):
#   1. ✅ Project work NO LONGER assigns teachers (students work independently)
#   2. ✅ Success rate and fitness scores now properly returned
#   3. ✅ Room capacity calculation fixed (uses actual Division.student_count)
#   4. ✅ Workload balancing constraint added
#   5. ✅ Schedule gap optimization added
#   6. ✅ Stronger preference enforcement (20 points instead of 5)
#   7. ✅ Lab continuity improved with better checks

import random
import copy
from collections import defaultdict, Counter
from datetime import datetime, timedelta, time
from typing import List, Dict, Tuple, Optional, Set
import logging
import json

# Django imports
from django.db import models
from django.utils import timezone

# Your existing model imports
from .models import (
    Teacher, Subject, Room, Lab, TimeSlot, Session, Year, Division,
    SubjectProficiency, SystemConfiguration, ProjectTimeAllocation
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TimetableConfiguration:
    """Holds all user-configured data from TT Incharge interface"""
    
    def __init__(self, config_data):
        # Store raw config data for access to wizard data
        self.raw_config = config_data
        
        # Basic configuration - parse time strings if needed
        def parse_time(time_input):
            if isinstance(time_input, str):
                try:
                    hour, minute = map(int, time_input.split(':'))
                    return time(hour, minute)
                except (ValueError, AttributeError):
                    return time(9, 0)  # Default fallback
            elif isinstance(time_input, time):
                return time_input
            else:
                return time(9, 0)  # Default fallback
        
        self.college_start_time = parse_time(config_data.get('college_start_time', '09:00'))
        self.college_end_time = parse_time(config_data.get('college_end_time', '17:45'))
        self.recess_start = parse_time(config_data.get('recess_start', '13:00'))
        self.recess_end = parse_time(config_data.get('recess_end', '13:45'))
        
        # ✅ NEW: Store wizard data
        self.wizard_subjects = config_data.get('subjects', [])
        self.wizard_teachers = config_data.get('teachers', [])
        self.wizard_rooms = config_data.get('rooms', {})
        
        # Professor assignments by year (TT Incharge input)
        self.professor_year_assignments = config_data.get('professor_year_assignments', {})
        # Format: {'FE': [teacher_ids], 'SE': [teacher_ids], 'TE': [teacher_ids], 'BE': [teacher_ids]}
        
        # Proficiency data (TT Incharge marks for each professor-subject)
        self.proficiency_data = config_data.get('proficiency_data', {})
        # Format: {teacher_id: {subject_id: {'knowledge': score, 'willingness': score}}}
        
        # Room assignments by year (can overlap)
        self.room_assignments = config_data.get('room_assignments', {})
        # Format: {'FE': {'lectures': [room_ids], 'labs': [lab_ids]}, 'SE': {...}, ...}
        
        # Remedial configuration per year
        self.remedial_config = config_data.get('remedial_config', {})
        # Format: {'FE': 1, 'SE': 1, 'TE': 1, 'BE': 1} (lectures per week)
        
        # Professor preferences (TT Incharge sets)
        self.professor_preferences = config_data.get('professor_preferences', {})
        # Format: {teacher_id: {'first_half_second_half': 'morning'/'afternoon'/'flexible'}}
        
        # Division configuration per year
        self.division_config = config_data.get('division_config', {})
        # Format: {'FE': ['A', 'B'], 'SE': ['A', 'B'], 'TE': ['A', 'B'], 'BE': ['A', 'B']}
        
        # Batch configuration per division
        self.batch_config = config_data.get('batch_config', {})
        # Format: {'FE-A': 3, 'FE-B': 3, 'SE-A': 3, ...} (number of batches)
        
        # Project work configuration per year
        self.project_config = config_data.get('project_config', {})
        # Format: {'FE': 0, 'SE': 1, 'TE': 1, 'BE': 2} (half-days per week)
        
        # Generate time slots based on college hours
        self.time_slots = self._generate_time_slots()
    
    def _generate_time_slots(self):
        """Generate time slots based on college start/end times"""
        slots = {}
        slot_number = 1
        
        # Standard 1-hour slots
        current_time = self.college_start_time
        
        while current_time < self.college_end_time:
            slot_end = (datetime.combine(datetime.today(), current_time) + timedelta(hours=1)).time()
            
            # Skip recess slot
            if not (current_time >= self.recess_start and current_time < self.recess_end):
                slots[slot_number] = {
                    "start": current_time,
                    "end": slot_end,
                    "name": f"{current_time.strftime('%H:%M')}-{slot_end.strftime('%H:%M')}"
                }
                slot_number += 1
            elif current_time == self.recess_start:
                # Add recess slot
                slots[slot_number] = {
                    "start": self.recess_start,
                    "end": self.recess_end,
                    "name": f"{self.recess_start.strftime('%H:%M')}-{self.recess_end.strftime('%H:%M')} (RECESS)",
                    "is_recess": True
                }
                slot_number += 1
            
            current_time = slot_end
        
        return slots
    
    def get_available_professors_for_year(self, year_name):
        """Get professors assigned to specific year"""
        return self.professor_year_assignments.get(year_name, [])
    
    def get_professor_proficiency(self, teacher_id, subject_id):
        """Get proficiency scores for teacher-subject pair"""
        teacher_profs = self.proficiency_data.get(teacher_id, {})
        subject_prof = teacher_profs.get(subject_id, {'knowledge': 5.0, 'willingness': 5.0})
        
        knowledge = subject_prof.get('knowledge', 5.0)
        willingness = subject_prof.get('willingness', 5.0)
        
        # Simple proficiency calculation (TT Incharge's scores are final)
        return (knowledge * 0.6) + (willingness * 0.4)
    
    def get_available_rooms_for_year(self, year_name, room_type='lectures'):
        """Get rooms assigned to specific year"""
        year_rooms = self.room_assignments.get(year_name, {})
        rooms = year_rooms.get(room_type, [])
        
        # ✅ FIX: If no rooms from wizard, use database rooms
        if not rooms:
            from timetable_app.models import Room, Lab
            if room_type == 'labs':
                rooms = list(Lab.objects.values_list('id', flat=True))
            else:
                rooms = list(Room.objects.values_list('id', flat=True))
            logger.info(f"Using {len(rooms)} {room_type} from database for {year_name}")
        
        return rooms
    
    def get_professor_time_preference(self, teacher_id):
        """Get professor's time preference"""
        prefs = self.professor_preferences.get(teacher_id, {})
        return prefs.get('first_half_second_half', 'flexible')
    
    def get_divisions_for_year(self, year_name):
        """Get division names for year"""
        return self.division_config.get(year_name, ['A', 'B'])
    
    def get_batches_for_division(self, division_key):
        """Get number of batches for division (e.g., 'FE-A')"""
        return self.batch_config.get(division_key, 3)
    
    def get_project_halves_for_year(self, year_name):
        """Get project half-days per week for year"""
        return self.project_config.get(year_name, 0)
    
    def get_remedial_count_for_year(self, year_name):
        """Get remedial lectures per week for year"""
        return self.remedial_config.get(year_name, 1)


class ProficiencyBasedTeacherSelector:
    """Selects teachers based ONLY on proficiency scores (no hardcoded rules)"""
    
    def __init__(self, config: TimetableConfiguration):
        self.config = config
        self.teacher_availability = defaultdict(lambda: defaultdict(bool))  # [teacher_id][slot] = available
    
    def select_best_teacher_for_subject(self, subject, year_name, exclude_teachers=None):
        """Select best teacher for subject based ONLY on proficiency"""
        exclude_teachers = exclude_teachers or []
        available_teachers = self.config.get_available_professors_for_year(year_name)
        
        # ✅ Get subject ID (handle both dict and model)
        subject_id = subject.get('id') if isinstance(subject, dict) else subject.id
        
        candidates = []
        
        for teacher_id in available_teachers:
            if teacher_id in exclude_teachers:
                continue
            
            try:
                teacher = Teacher.objects.get(id=teacher_id)
                proficiency = self.config.get_professor_proficiency(teacher_id, subject_id)
                
                # Only criteria: proficiency score
                candidates.append({
                    'teacher_id': teacher_id,
                    'teacher': teacher,
                    'proficiency': proficiency
                })
                
            except Teacher.DoesNotExist:
                continue
        
        if not candidates:
            return None
        
        # Sort by proficiency (highest first)
        candidates.sort(key=lambda x: x['proficiency'], reverse=True)
        
        # Return best match
        return candidates[0]
    
    def check_teacher_availability(self, teacher_id, slot_number):
        """Check if teacher is available at given slot"""
        return self.teacher_availability[teacher_id][slot_number]
    
    def mark_teacher_busy(self, teacher_id, slot_number):
        """Mark teacher as busy at given slot"""
        self.teacher_availability[teacher_id][slot_number] = False
    
    def mark_teacher_available(self, teacher_id, slot_number):
        """Mark teacher as available at given slot"""
        self.teacher_availability[teacher_id][slot_number] = True


class CrossYearResourceManager:
    """Manages cross-year resource conflicts (rooms, teachers, etc.)"""
    
    def __init__(self, config: TimetableConfiguration):
        self.config = config
        self.global_room_usage = defaultdict(lambda: defaultdict(list))  # [room_id][slot] = [year_names]
        self.global_teacher_usage = defaultdict(lambda: defaultdict(list))  # [teacher_id][slot] = [year_names]
    
    def check_room_availability(self, room_id, slot_number, year_name):
        """Check if room is available for year at given slot"""
        current_users = self.global_room_usage[room_id][slot_number]
        return len(current_users) == 0 or year_name in current_users
    
    def allocate_room(self, room_id, slot_number, year_name, division_name):
        """Allocate room for specific year/division"""
        self.global_room_usage[room_id][slot_number].append(f"{year_name}-{division_name}")
    
    def check_teacher_cross_year_availability(self, teacher_id, slot_number):
        """Check if teacher is available across all years"""
        return len(self.global_teacher_usage[teacher_id][slot_number]) == 0
    
    def allocate_teacher(self, teacher_id, slot_number, year_name, division_name, subject_name):
        """Allocate teacher globally"""
        allocation_info = {
            'year_div': f"{year_name}-{division_name}",
            'subject': subject_name
        }
        self.global_teacher_usage[teacher_id][slot_number].append(allocation_info)
    
    def get_conflicts_report(self):
        """Generate conflicts report for manual review"""
        conflicts = {
            'teacher_conflicts': [],
            'room_conflicts': []
        }
        
        # Teacher conflicts
        for teacher_id, schedule in self.global_teacher_usage.items():
            for slot, allocations in schedule.items():
                if len(allocations) > 1:
                    try:
                        teacher_name = Teacher.objects.get(id=teacher_id).name
                        conflicts['teacher_conflicts'].append({
                            'teacher': teacher_name,
                            'slot': slot,
                            'conflicts': allocations
                        })
                    except:
                        pass
        
        # Room conflicts
        for room_id, schedule in self.global_room_usage.items():
            for slot, allocations in schedule.items():
                if len(allocations) > 1:
                    conflicts['room_conflicts'].append({
                        'room_id': room_id,
                        'slot': slot,
                        'conflicts': allocations
                    })
        
        return conflicts


class UserConfigurableChromosome:
    """Chromosome based on user configuration (not hardcoded patterns)"""
    
    def __init__(self, genes=None, division=None, year=None, config=None):
        self.genes = genes if genes is not None else []
        self.division = division
        self.year = year
        self.config = config
        self.fitness_score = None
        self.violations = {}
    
    def fitness(self, algorithm_instance):
        """Calculate fitness based on user-configured constraints only"""
        if self.fitness_score is not None:
            return self.fitness_score
        
        violations = 0
        self.violations = {}  # ✅ FIX #2: Track individual violation types
        
        try:
            # Core conflicts (always critical)
            teacher_conflicts = self._check_teacher_conflicts()
            room_conflicts = self._check_room_conflicts()
            student_conflicts = self._check_student_conflicts()
            recess_violations = self._check_recess_violations()
            
            violations += teacher_conflicts
            violations += room_conflicts
            violations += student_conflicts
            violations += recess_violations
            
            self.violations['teacher_conflicts'] = teacher_conflicts
            self.violations['room_conflicts'] = room_conflicts
            self.violations['student_conflicts'] = student_conflicts
            self.violations['recess_violations'] = recess_violations
            
            # Lab continuity (2-hour blocks)
            lab_continuity = self._check_lab_continuity()
            violations += lab_continuity
            self.violations['lab_continuity'] = lab_continuity
            
            # Project work blocks (half-day periods)
            project_blocks = self._check_project_blocks()
            violations += project_blocks
            self.violations['project_blocks'] = project_blocks
            
            # Proficiency matching (user-defined scores)
            proficiency_matching = self._check_proficiency_matching()
            violations += proficiency_matching
            self.violations['proficiency_matching'] = proficiency_matching
            
            # Teacher preferences (user-configured) - STRONGER ENFORCEMENT
            preference_violations = self._check_teacher_time_preferences()
            violations += preference_violations
            self.violations['preference_violations'] = preference_violations
            
            # Room capacity - FIXED CALCULATION
            capacity_violations = self._check_room_capacity()
            violations += capacity_violations
            self.violations['capacity_violations'] = capacity_violations
            
            # ✅ FIX #4: NEW - Workload balancing
            workload_violations = self._check_workload_balance()
            violations += workload_violations
            self.violations['workload_violations'] = workload_violations
            
            # ✅ FIX #5: NEW - Schedule gap optimization
            gap_violations = self._check_schedule_gaps()
            violations += gap_violations
            self.violations['gap_violations'] = gap_violations
            
        except Exception as e:
            logger.error(f"Error in fitness calculation: {e}")
            violations += 10000
        
        self.fitness_score = -violations
        self.violations['total'] = violations
        return self.fitness_score
    
    def _check_proficiency_matching(self):
        """Check proficiency matching using user-configured scores"""
        violations = 0
        
        for gene in self.genes:
            try:
                subject_id = gene[0]
                teacher_id = gene[1]
                
                proficiency = self.config.get_professor_proficiency(teacher_id, subject_id)
                
                # Penalty based on low proficiency (user's scores are authoritative)
                if proficiency < 6.0:  # Below acceptable threshold
                    violations += int((6.0 - proficiency) * 10)
                elif proficiency >= 8.0:  # Excellent match
                    violations -= 2  # Small bonus
                    
            except Exception as e:
                violations += 50  # Penalty for invalid assignments
        
        return violations
    
    def _check_teacher_time_preferences(self):
        """Check teacher time preferences from user configuration"""
        violations = 0
        
        for gene in self.genes:
            try:
                teacher_id = gene[1]
                slot_number = gene[3]
                
                preference = self.config.get_professor_time_preference(teacher_id)
                
                if preference != 'flexible':
                    slot_time = self.config.time_slots.get(slot_number, {}).get('start')
                    
                    if slot_time:
                        is_morning = slot_time < time(13, 0)
                        
                        if (preference == 'morning' and not is_morning) or \
                           (preference == 'afternoon' and is_morning):
                            violations += 20  # ✅ FIX #6: INCREASED from 5 to 20 for stronger enforcement
                            
            except Exception as e:
                logger.warning(f"Error checking preferences: {e}")
        
        return violations
    
    def _check_teacher_conflicts(self):
        """Check teacher double-booking"""
        violations = 0
        teacher_schedule = defaultdict(list)
        
        for gene in self.genes:
            teacher_id = gene[1]
            slot_number = gene[3]
            
            # ✅ Skip project work (no teacher assigned)
            if teacher_id is None:
                continue
                
            teacher_schedule[teacher_id].append(slot_number)
        
        for teacher_id, slots in teacher_schedule.items():
            conflicts = len(slots) - len(set(slots))
            violations += conflicts * 100
        
        return violations
    
    def _check_room_conflicts(self):
        """Check room double-booking within division"""
        violations = 0
        room_schedule = defaultdict(list)
        
        for gene in self.genes:
            room_id = gene[2]
            slot_number = gene[3]
            if room_id:
                room_schedule[room_id].append(slot_number)
        
        for room_id, slots in room_schedule.items():
            conflicts = len(slots) - len(set(slots))
            violations += conflicts * 90
        
        return violations
    
    def _check_student_conflicts(self):
        """Check student double-booking"""
        violations = 0
        student_schedule = defaultdict(list)
        
        for gene in self.genes:
            batch_id = gene[4]
            slot_number = gene[3]
            student_schedule[batch_id].append(slot_number)
        
        for batch_id, slots in student_schedule.items():
            conflicts = len(slots) - len(set(slots))
            violations += conflicts * 85
        
        return violations
    
    def _check_recess_violations(self):
        """Check sessions during recess"""
        violations = 0
        
        for gene in self.genes:
            slot_number = gene[3]
            slot_info = self.config.time_slots.get(slot_number, {})
            
            if slot_info.get('is_recess', False):
                violations += 150
        
        return violations
    
    def _check_lab_continuity(self):
        """Check lab 2-hour continuity"""
        violations = 0
        lab_sessions = defaultdict(list)
        
        for gene in self.genes:
            try:
                subject = Subject.objects.get(id=gene[0])
                if getattr(subject, 'requires_lab', False):
                    lab_sessions[subject.id].append(gene[3])
            except:
                continue
        
        for subject_id, slots in lab_sessions.items():
            unique_slots = sorted(set(slots))
            
            if len(unique_slots) == 1:
                violations += 80  # Single hour lab
            elif len(unique_slots) == 2:
                slot1, slot2 = unique_slots
                if slot2 - slot1 != 1:  # Not consecutive
                    violations += 80
            elif len(unique_slots) > 2:
                violations += (len(unique_slots) - 2) * 40
        
        return violations
    
    def _check_project_blocks(self):
        """Check project work half-day blocks"""
        violations = 0
        project_sessions = defaultdict(list)
        
        for gene in self.genes:
            try:
                subject = Subject.objects.get(id=gene[0])
                if getattr(subject, 'is_project_work', False):
                    project_sessions[subject.id].append(gene[3])
            except:
                continue
        
        for subject_id, slots in project_sessions.items():
            unique_slots = sorted(set(slots))
            
            # Check if forms half-day block (4 consecutive slots)
            if len(unique_slots) != 4:
                violations += 60
            else:
                for i in range(3):
                    if unique_slots[i+1] - unique_slots[i] != 1:
                        violations += 60
                        break
        
        return violations
    
    def _check_room_capacity(self):
        """Check room capacity constraints - FIXED CALCULATION"""
        violations = 0
        
        for gene in self.genes:
            try:
                room_id = gene[2]
                
                if room_id:
                    # ✅ FIX #3: Get actual student count from Division model
                    try:
                        division = Division.objects.get(year__name=self.year, name=self.division.name)
                        total_students = division.student_count
                    except:
                        # Fallback to default if division not found
                        total_students = 60
                    
                    # Check room capacity (simplified)
                    room_capacity = 50  # Default capacity
                    try:
                        room = Room.objects.get(id=room_id)
                        room_capacity = getattr(room, 'capacity', 50)
                    except:
                        try:
                            lab = Lab.objects.get(id=room_id)
                            room_capacity = getattr(lab, 'capacity', 30)
                        except:
                            pass
                    
                    if total_students > room_capacity:
                        violations += (total_students - room_capacity) * 5
                        
            except Exception as e:
                logger.warning(f"Error checking capacity: {e}")
        
        return violations
    
    def _check_workload_balance(self):
        """✅ FIX #4: NEW - Check teacher workload balance"""
        violations = 0
        teacher_loads = defaultdict(int)
        
        for gene in self.genes:
            teacher_id = gene[1]
            if teacher_id is not None:  # Skip project work
                teacher_loads[teacher_id] += 1
        
        if teacher_loads:
            loads = list(teacher_loads.values())
            avg_load = sum(loads) / len(loads)
            
            # Penalize deviation from average
            for load in loads:
                deviation = abs(load - avg_load)
                if deviation > 3:  # Allow 3-session tolerance
                    violations += int(deviation * 2)
        
        return violations
    
    def _check_schedule_gaps(self):
        """✅ FIX #5: NEW - Penalize gaps in teacher and student schedules"""
        violations = 0
        
        # Check teacher schedule gaps
        teacher_schedules = defaultdict(list)
        for gene in self.genes:
            teacher_id = gene[1]
            if teacher_id is not None:  # Skip project work
                teacher_schedules[teacher_id].append(gene[3])
        
        for teacher_id, slots in teacher_schedules.items():
            sorted_slots = sorted(set(slots))
            for i in range(len(sorted_slots) - 1):
                gap = sorted_slots[i+1] - sorted_slots[i]
                if gap > 1:  # Gap detected
                    violations += (gap - 1) * 3  # Penalty per gap slot
        
        # Check student schedule gaps
        student_schedules = defaultdict(list)
        for gene in self.genes:
            batch_id = gene[4]
            student_schedules[batch_id].append(gene[3])
        
        for batch_id, slots in student_schedules.items():
            sorted_slots = sorted(set(slots))
            for i in range(len(sorted_slots) - 1):
                gap = sorted_slots[i+1] - sorted_slots[i]
                if gap > 1:  # Gap detected
                    violations += (gap - 1) * 2  # Smaller penalty for students
        
        return violations


class UserDrivenTimetableAlgorithm:
    """Main algorithm driven by user configuration (TT Incharge setup)"""
    
    def __init__(self, config_data, target_years=None):
        self.config = TimetableConfiguration(config_data)
        self.target_years = target_years or ['FE', 'SE', 'TE', 'BE']
        
        # Resource managers
        self.teacher_selector = ProficiencyBasedTeacherSelector(self.config)
        self.resource_manager = CrossYearResourceManager(self.config)
        
        # Algorithm parameters
        self.population_size = 40
        self.generations = 200
        self.mutation_rate = 0.25
        self.elite_count = 4
        
        # Initialize data
        self._initialize_data()
        
        logger.info(f"User-driven algorithm (FIXED v2.0) initialized for years: {self.target_years}")
    
    def generate_all_timetables(self):
        """Generate timetables for all configured years and divisions"""
        results = {}
        
        # Process each year
        for year_name in self.target_years:
            year_results = self._generate_year_timetables(year_name)
            results[year_name] = year_results
        
        # Generate cross-year conflicts report
        conflicts = self.resource_manager.get_conflicts_report()
        results['_conflicts_report'] = conflicts
        
        # ✅ FIX #2: Calculate overall success metrics
        results['_success_metrics'] = self._calculate_success_metrics(results)
        
        if conflicts['teacher_conflicts'] or conflicts['room_conflicts']:
            logger.warning(f"Cross-year conflicts detected: "
                          f"{len(conflicts['teacher_conflicts'])} teacher conflicts, "
                          f"{len(conflicts['room_conflicts'])} room conflicts")
        else:
            logger.info("No cross-year conflicts detected")
        
        return results
    
    def _calculate_success_metrics(self, results):
        """✅ FIX #2: NEW - Calculate overall success rate and metrics"""
        total_divisions = 0
        successful_divisions = 0
        total_fitness = 0
        total_violations = 0
        
        for year, year_results in results.items():
            if year.startswith('_'):  # Skip metadata
                continue
            
            if isinstance(year_results, dict):
                for division, result in year_results.items():
                    if isinstance(result, dict) and not result.get('error'):
                        total_divisions += 1
                        if result.get('success'):
                            successful_divisions += 1
                        total_fitness += result.get('fitness_score', 0)
                        total_violations += result.get('total_violations', 0)
        
        success_rate = (successful_divisions / total_divisions * 100) if total_divisions > 0 else 0
        avg_fitness = total_fitness / total_divisions if total_divisions > 0 else 0
        
        return {
            'total_divisions': total_divisions,
            'successful_divisions': successful_divisions,
            'success_rate': round(success_rate, 2),
            'average_fitness_score': round(avg_fitness, 2),
            'total_violations': total_violations,
            'conflict_free': total_violations == 0
        }
    
    def _generate_year_timetables(self, year_name):
        """Generate timetables for all divisions in a year"""
        year_results = {}
        
        try:
            logger.info(f"Looking for year: {year_name}")
            year = Year.objects.get(name=year_name)
            logger.info(f"Found year: {year}")
            
            divisions = Division.objects.filter(year=year)
            logger.info(f"Found {len(divisions)} divisions for year {year_name}")
            
            if not divisions:
                logger.warning(f"No divisions found for year {year_name}, creating default divisions")
                divisions = self._create_default_divisions(year, year_name)
                logger.info(f"Created {len(divisions)} default divisions for year {year_name}")
            
            for division in divisions:
                logger.info(f"Processing division: {division.name}")
                division_result = self._generate_division_timetable(division, year_name)
                year_results[division.name] = division_result
                
        except Year.DoesNotExist:
            error_msg = f"Year {year_name} not found in database"
            logger.error(error_msg)
            year_results['error'] = error_msg
        except Exception as e:
            logger.error(f"Error generating timetables for year {year_name}: {e}")
            year_results['error'] = str(e)
        
        return year_results
    
    def _create_default_divisions(self, year, year_name):
        """Create default divisions A and B for a year"""
        divisions = []
        
        for division_name in ['A', 'B']:
            division, created = Division.objects.get_or_create(
                year=year,
                name=division_name,
                defaults={
                    'capacity': 60,  # Default capacity
                    'is_active': True
                }
            )
            divisions.append(division)
            if created:
                logger.info(f"Created division {year_name} {division_name}")
            else:
                logger.info(f"Division {year_name} {division_name} already exists")
        
        return divisions
    
    def _create_basic_sessions(self, division, year_name):
        """Create basic timetable sessions for a division"""
        sessions_created = 0
        
        try:
            # Get available subjects for this year
            subjects = Subject.objects.filter(year__name=year_name)[:6]  # Limit to 6 subjects for testing
            
            if not subjects:
                logger.warning(f"No subjects found for year {year_name}")
                return 0
            
            # Get available time slots
            time_slots = TimeSlot.objects.all()[:6]  # Limit to 6 time slots
            
            if not time_slots:
                logger.warning("No time slots found")
                return 0
            
            # Get available teachers
            teachers = Teacher.objects.all()[:len(subjects)]
            
            if not teachers:
                logger.warning("No teachers found")
                return 0
            
            # Create sessions
            for i, subject in enumerate(subjects):
                if i < len(time_slots) and i < len(teachers):
                    session, created = Session.objects.get_or_create(
                        subject=subject,
                        teacher=teachers[i],
                        division=division,
                        time_slot=time_slots[i],
                        defaults={
                            'room': None,  # Room assignment can be added later
                            'session_type': 'Lecture'
                        }
                    )
                    if created:
                        sessions_created += 1
                        logger.info(f"Created session: {subject.name} with {teachers[i].name} for {year_name} {division.name}")
            
            return sessions_created
            
        except Exception as e:
            logger.error(f"Error creating basic sessions: {e}")
            return 0
    
    def _generate_division_timetable(self, division, year_name):
        """Generate timetable for single division - ✅ FIX #2: Returns proper metrics"""
        try:
            logger.info(f"Generating timetable for {year_name} Division {division.name}")
            
            # ✅ SKIP basic session creation - go straight to genetic algorithm
            # The genetic algorithm will create chromosomes with genes, not database sessions
            # Database sessions are only created at the END after optimization
            
            # ✅ Run genetic algorithm optimization
            logger.info(f"Creating population for {year_name} Division {division.name}")
            population = self._create_population(division, year_name)
            
            if not population:
                logger.warning(f"Failed to create population for {year_name} Division {division.name}")
                return {
                    'division': division.name,
                    'timetable': None,
                    'error': 'Failed to create population - check if subjects and teachers are configured',
                    'sessions_count': 0,
                    'success': False,
                    'fitness_score': 0,
                    'total_violations': 0,
                    'violations': {
                        'note': 'Population creation failed - may need more data in database'
                    }
                }
            
            # Evolve population using genetic algorithm
            logger.info(f"Evolving population for {year_name} Division {division.name}")
            best_solution = self._evolve_population(population, division, year_name)
            
            if best_solution:
                logger.info(f"Evolution successful for {year_name} Division {division.name}")
                return {
                    'division': division.name,
                    'timetable': best_solution,
                    'fitness_score': best_solution.fitness_score,
                    'total_violations': best_solution.violations.get('total', 0),
                    'violations': best_solution.violations,
                    'sessions_count': len(best_solution.genes),
                    'success': True
                }
            else:
                logger.warning(f"Evolution failed for {year_name} Division {division.name}")
                return {
                    'division': division.name,
                    'timetable': None,
                    'error': 'Evolution failed',
                    'success': False,
                    'fitness_score': 0,
                    'total_violations': 0,
                    'violations': {}
                }
                
        except Exception as e:
            logger.error(f"Error generating division timetable: {e}")
            return {
                'division': division.name,
                'timetable': None,
                'error': str(e),
                'success': False,
                'fitness_score': 0,
                'total_violations': 0,
                'violations': {}
            }
    
    def _create_population(self, division, year_name):
        """Create initial population for division"""
        population = []
        
        for _ in range(self.population_size):
            try:
                chromosome = self._create_chromosome(division, year_name)
                if chromosome and chromosome.genes:
                    population.append(chromosome)
            except Exception as e:
                logger.warning(f"Error creating chromosome: {e}")
        
        return population
    
    def _create_chromosome(self, division, year_name):
        """Create chromosome for division using user configuration"""
        genes = []
        
        try:
            # ✅ FIXED: Use wizard subjects if available, otherwise fall back to database
            if self.config.wizard_subjects and len(self.config.wizard_subjects) > 0:
                logger.info(f"Using {len(self.config.wizard_subjects)} subjects from wizard data")
                # Wizard subjects are just data dictionaries, not Django models
                # We'll create mock subject objects for the algorithm
                subjects = self.config.wizard_subjects
            else:
                logger.info(f"No wizard subjects, querying database for {year_name}")
                # Get division subjects from database
                subjects = Subject.objects.filter(year__name=year_name, division=division)
            
            # Get/create batches based on user configuration
            division_key = f"{year_name}-{division.name}"
            num_batches = self.config.get_batches_for_division(division_key)
            batches = self._ensure_batches_exist(division, num_batches)
            
            # Schedule each subject
            for subject in subjects:
                subject_genes = self._schedule_subject(subject, division, year_name, batches)
                genes.extend(subject_genes)
            
            # Add remedial if configured
            remedial_count = self.config.get_remedial_count_for_year(year_name)
            if remedial_count > 0:
                remedial_genes = self._schedule_remedial(division, year_name, batches, remedial_count)
                genes.extend(remedial_genes)
            
            return UserConfigurableChromosome(genes, division, year_name, self.config)
            
        except Exception as e:
            logger.error(f"Error creating chromosome: {e}")
            return None
    
    def _schedule_subject(self, subject, division, year_name, batches):
        """Schedule subject using user configuration"""
        genes = []
        
        try:
            # ✅ Handle both Django models and wizard dictionaries
            if isinstance(subject, dict):
                # Wizard data
                subject_id = subject.get('id', subject.get('code', f"SUBJ-{hash(subject.get('name'))}"))
                subject_name = subject.get('name', 'Unknown')
                is_lab = subject.get('requiresLab', False) or subject.get('requires_lab', False)
                is_project = subject.get('isProject', False) or subject.get('is_project_work', False)
                sessions_needed = subject.get('sessionsPerWeek', 3) or subject.get('sessions_per_week', 3)
            else:
                # Django model
                subject_id = subject.id
                subject_name = subject.name
                is_lab = getattr(subject, 'requires_lab', False)
                is_project = getattr(subject, 'is_project_work', False)
                sessions_needed = getattr(subject, 'sessions_per_week', 3)
            
            if is_project:
                genes = self._schedule_project_work(subject, division, year_name, batches)
            elif is_lab:
                genes = self._schedule_lab_subject(subject, division, year_name, batches)
            else:
                genes = self._schedule_lecture_subject(subject, division, year_name, batches, sessions_needed)
                
        except Exception as e:
            subj_name = subject.get('name') if isinstance(subject, dict) else getattr(subject, 'name', 'Unknown')
            logger.warning(f"Error scheduling subject {subj_name}: {e}")
        
        return genes
    
    def _schedule_project_work(self, subject, division, year_name, batches):
        """Schedule project work - NO TEACHER ASSIGNMENT (students work independently)"""
        genes = []
        
        try:
            # ✅ FIX #1: DO NOT assign teacher for project work
            # Project work = student independent work (Mini/Major projects)
            # NO professor should be occupied during project time
            
            # teacher_selection = self.teacher_selector.select_best_teacher_for_subject(subject, year_name)
            # teacher_id = teacher_selection['teacher_id']  # ❌ REMOVED
            
            teacher_id = None  # ✅ No teacher for project work
            
            # ✅ Get subject ID (handle both dict and model)
            subject_id = subject.get('id') if isinstance(subject, dict) else subject.id
            
            # Get available rooms for this year
            available_rooms = self.config.get_available_rooms_for_year(year_name, 'lectures')
            
            if not available_rooms:
                return genes
            
            room_id = random.choice(available_rooms)
            
            # Schedule 4-hour project block (prefer afternoon for project work)
            available_slots = [slot for slot in self.config.time_slots.keys() 
                             if not self.config.time_slots[slot].get('is_recess', False)]
            
            # Prefer afternoon for project work
            mid_point = len(available_slots) // 2
            block_start = sorted(available_slots)[mid_point]
            
            # Schedule 4 consecutive slots
            for i in range(4):
                slot = block_start + i
                if slot in available_slots:
                    for batch in batches:
                        # ✅ Gene with NULL teacher (project time)
                        genes.append((subject_id, None, room_id, slot, batch['batch_number']))
                        
                        # ✅ Only allocate room, NOT teacher
                        self.resource_manager.allocate_room(
                            room_id, slot, year_name, division.name
                        )
                        # ❌ DO NOT allocate teacher for project work
                        # self.resource_manager.allocate_teacher(...)
                        
        except Exception as e:
            logger.warning(f"Error scheduling project work: {e}")
        
        return genes
    
    def _schedule_lab_subject(self, subject, division, year_name, batches):
        """Schedule lab subject (2 consecutive hours)"""
        genes = []
        
        try:
            # ✅ Get subject ID and name (handle both dict and model)
            subject_id = subject.get('id') if isinstance(subject, dict) else subject.id
            subject_name = subject.get('name') if isinstance(subject, dict) else subject.name
            
            # Get teacher based on proficiency
            teacher_selection = self.teacher_selector.select_best_teacher_for_subject(subject, year_name)
            
            if not teacher_selection:
                return genes
            
            teacher_id = teacher_selection['teacher_id']
            
            # Get available labs for this year
            available_labs = self.config.get_available_rooms_for_year(year_name, 'labs')
            
            if not available_labs:
                return genes
            
            lab_id = random.choice(available_labs)
            
            # Find 2 consecutive available slots
            available_slots = [slot for slot in self.config.time_slots.keys() 
                             if not self.config.time_slots[slot].get('is_recess', False)]
            
            for i in range(len(available_slots) - 1):
                slot1, slot2 = available_slots[i], available_slots[i + 1]
                
                # Check if both slots are consecutive and available
                if (slot2 - slot1 == 1 and 
                    self.resource_manager.check_teacher_cross_year_availability(teacher_id, slot1) and
                    self.resource_manager.check_teacher_cross_year_availability(teacher_id, slot2) and
                    self.resource_manager.check_room_availability(lab_id, slot1, year_name) and
                    self.resource_manager.check_room_availability(lab_id, slot2, year_name)):
                    
                    # Schedule 2-hour lab
                    for batch in batches:
                        genes.append((subject_id, teacher_id, lab_id, slot1, batch['batch_number']))
                        genes.append((subject_id, teacher_id, lab_id, slot2, batch['batch_number']))
                    
                    # Allocate resources globally
                    for slot in [slot1, slot2]:
                        self.resource_manager.allocate_teacher(
                            teacher_id, slot, year_name, division.name, subject_name
                        )
                        self.resource_manager.allocate_room(
                            lab_id, slot, year_name, division.name
                        )
                    
                    break
                    
        except Exception as e:
            logger.warning(f"Error scheduling lab: {e}")
        
        return genes
    
    def _schedule_lecture_subject(self, subject, division, year_name, batches, sessions_needed):
        """Schedule regular lecture subject"""
        genes = []
        
        try:
            # ✅ Get subject ID and name (handle both dict and model)
            subject_id = subject.get('id') if isinstance(subject, dict) else subject.id
            subject_name = subject.get('name') if isinstance(subject, dict) else subject.name
            
            # Get teacher based on proficiency
            teacher_selection = self.teacher_selector.select_best_teacher_for_subject(subject, year_name)
            
            if not teacher_selection:
                logger.warning(f"No teacher found for subject {subject_name}")
                return genes
            
            teacher_id = teacher_selection['teacher_id']
            
            # Get available lecture rooms for this year
            available_rooms = self.config.get_available_rooms_for_year(year_name, 'lectures')
            
            if not available_rooms:
                logger.warning(f"No rooms available for {year_name}")
                return genes
            
            # Get teacher's time preference
            time_pref = self.config.get_professor_time_preference(teacher_id)
            
            # Filter slots based on preference
            available_slots = [slot for slot in self.config.time_slots.keys() 
                             if not self.config.time_slots[slot].get('is_recess', False)]
            
            if time_pref == 'morning':
                preferred_slots = [s for s in available_slots 
                                 if self.config.time_slots[s]['start'] < time(13, 0)]
            elif time_pref == 'afternoon':
                preferred_slots = [s for s in available_slots 
                                 if self.config.time_slots[s]['start'] >= time(13, 45)]
            else:
                preferred_slots = available_slots
            
            # Schedule required sessions
            selected_slots = random.sample(
                preferred_slots, 
                min(sessions_needed, len(preferred_slots))
            )
            
            room_id = random.choice(available_rooms)
            
            for slot in selected_slots:
                for batch in batches:
                    genes.append((subject_id, teacher_id, room_id, slot, batch['batch_number']))
                
                # Allocate resources globally
                self.resource_manager.allocate_teacher(
                    teacher_id, slot, year_name, division.name, subject_name
                )
                self.resource_manager.allocate_room(
                    room_id, slot, year_name, division.name
                )
                
        except Exception as e:
            logger.warning(f"Error scheduling lecture: {e}")
        
        return genes
    
    def _schedule_remedial(self, division, year_name, batches, remedial_count):
        """Schedule remedial lectures based on user configuration"""
        genes = []
        
        try:
            # Get any available teacher for remedial
            available_teachers = self.config.get_available_professors_for_year(year_name)
            
            if not available_teachers:
                return genes
            
            teacher_id = random.choice(available_teachers)
            
            # Get available rooms
            available_rooms = self.config.get_available_rooms_for_year(year_name, 'lectures')
            
            if not available_rooms:
                return genes
            
            room_id = random.choice(available_rooms)
            
            # Schedule remedial sessions
            available_slots = [slot for slot in self.config.time_slots.keys() 
                             if not self.config.time_slots[slot].get('is_recess', False)]
            
            selected_slots = random.sample(available_slots, min(remedial_count, len(available_slots)))
            
            for slot in selected_slots:
                for batch in batches:
                    genes.append((-1, teacher_id, room_id, slot, batch['batch_number']))  # -1 for remedial
                
                # Allocate resources
                self.resource_manager.allocate_teacher(
                    teacher_id, slot, year_name, division.name, "Remedial"
                )
                self.resource_manager.allocate_room(
                    room_id, slot, year_name, division.name
                )
                
        except Exception as e:
            logger.warning(f"Error scheduling remedial: {e}")
        
        return genes
    
    def _ensure_batches_exist(self, division, num_batches):
        """Generate batch information for division (no Batch model needed)"""
        batches = []
        
        for i in range(num_batches):
            batch_name = chr(65 + i)  # A, B, C, ...
            # Create a simple batch object with the info we need
            batch_info = {
                'name': batch_name,
                'division': division,
                'student_count': 30,
                'batch_number': i + 1
            }
            batches.append(batch_info)
        
        return batches
    
    def _evolve_population(self, population, division, year_name):
        """Evolve population using genetic algorithm"""
        for generation in range(self.generations):
            # Evaluate fitness
            for chromosome in population:
                chromosome.fitness(self)
            
            # Sort by fitness
            population.sort(key=lambda x: x.fitness_score, reverse=True)
            
            current_best = population[0].fitness_score
            
            # Logging
            if generation % 50 == 0:
                logger.info(f"{year_name}-{division.name} Gen {generation}: "
                           f"Best fitness = {current_best}, Violations = {-current_best}")
            
            # Early termination
            if current_best >= -10:
                logger.info(f"{year_name}-{division.name} converged at generation {generation}")
                break
            
            # Create next generation
            population = self._create_next_generation(population, division, year_name)
        
        return population[0] if population else None
    
    def _create_next_generation(self, population, division, year_name):
        """Create next generation"""
        new_population = []
        
        # Elitism
        new_population.extend(population[:self.elite_count])
        
        # Generate offspring
        while len(new_population) < self.population_size:
            parent1 = self._tournament_selection(population)
            parent2 = self._tournament_selection(population)
            
            child = self._crossover(parent1, parent2, division, year_name)
            self._mutate(child)
            
            new_population.append(child)
        
        return new_population
    
    def _tournament_selection(self, population, tournament_size=3):
        """Tournament selection"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness_score)
    
    def _crossover(self, parent1, parent2, division, year_name):
        """Single-point crossover"""
        if not parent1.genes or not parent2.genes:
            return copy.deepcopy(parent1)
        
        crossover_point = random.randint(1, min(len(parent1.genes), len(parent2.genes)) - 1)
        child_genes = parent1.genes[:crossover_point] + parent2.genes[crossover_point:]
        
        return UserConfigurableChromosome(child_genes, division, year_name, self.config)
    
    def _mutate(self, chromosome):
        """Mutation operation"""
        if random.random() > self.mutation_rate or not chromosome.genes:
            return
        
        idx = random.randint(0, len(chromosome.genes) - 1)
        gene = list(chromosome.genes[idx])
        
        # Mutate time slot
        available_slots = [slot for slot in self.config.time_slots.keys() 
                          if not self.config.time_slots[slot].get('is_recess', False)]
        
        gene[3] = random.choice(available_slots)
        chromosome.genes[idx] = tuple(gene)
        chromosome.fitness_score = None
    
    def _initialize_data(self):
        """Initialize required data"""
        try:
            self.subjects = list(Subject.objects.all())
            self.teachers = list(Teacher.objects.all())
            self.rooms = list(Room.objects.all())
            self.labs = list(Lab.objects.all())
            
            logger.info(f"Initialized data: {len(self.subjects)} subjects, "
                       f"{len(self.teachers)} teachers, "
                       f"{len(self.rooms + self.labs)} rooms/labs")
            
            # Check if we have minimum required data
            if len(self.subjects) == 0:
                logger.warning("No subjects found in database")
            if len(self.teachers) == 0:
                logger.warning("No teachers found in database")
            if len(self.rooms) == 0 and len(self.labs) == 0:
                logger.warning("No rooms or labs found in database")
            
        except Exception as e:
            logger.error(f"Failed to initialize data: {e}")
            raise


# USAGE EXAMPLE - TT Incharge Configuration Interface
"""
# Example configuration data from TT Incharge interface:

config_data = {
    # Basic timing
    'college_start_time': time(9, 0),
    'college_end_time': time(17, 45),
    'recess_start': time(13, 0),
    'recess_end': time(13, 45),
    
    # Professor assignments by year (TT Incharge selects)
    'professor_year_assignments': {
        'FE': [1, 2, 3],  # Teacher IDs
        'SE': [2, 3, 4],
        'TE': [4, 5, 6, 7, 8],  # More teachers for senior years
        'BE': [5, 6, 7, 8, 9]
    },
    
    # Proficiency scores (TT Incharge marks each professor-subject)
    'proficiency_data': {
        1: {  # Teacher ID 1
            10: {'knowledge': 8.0, 'willingness': 7.0},  # Subject ID 10
            11: {'knowledge': 6.0, 'willingness': 8.0},
        },
        # ... more teachers
    },
    
    # Room assignments by year
    'room_assignments': {
        'FE': {'lectures': [101, 102, 103], 'labs': [201, 202]},
        'SE': {'lectures': [104, 105, 106], 'labs': [203, 204]},
        'TE': {'lectures': [107, 108, 803], 'labs': [205, 701, 702]},  # Room 803 shared
        'BE': {'lectures': [109, 110, 803], 'labs': [206, 703, 704]}   # Room 803 shared
    },
    
    # Remedial configuration per year
    'remedial_config': {
        'FE': 1,  # 1 remedial lecture per week
        'SE': 1,
        'TE': 1,
        'BE': 1
    },
    
    # Professor time preferences (TT Incharge sets)
    'professor_preferences': {
        1: {'first_half_second_half': 'morning'},
        2: {'first_half_second_half': 'afternoon'},
        3: {'first_half_second_half': 'flexible'},
        # ... more professors
    },
    
    # Division configuration
    'division_config': {
        'FE': ['A', 'B'],
        'SE': ['A', 'B'],
        'TE': ['A', 'B'],
        'BE': ['A', 'B']
    },
    
    # Batch configuration
    'batch_config': {
        'FE-A': 3, 'FE-B': 3,
        'SE-A': 3, 'SE-B': 3,
        'TE-A': 3, 'TE-B': 3,
        'BE-A': 3, 'BE-B': 3
    },
    
    # Project work configuration
    'project_config': {
        'FE': 0,  # No project work
        'SE': 1,  # 1 half-day per week
        'TE': 1,
        'BE': 2   # 2 half-days per week
    }
}

# Generate timetables
algorithm = UserDrivenTimetableAlgorithm(
    config_data=config_data,
    target_years=['FE', 'SE', 'TE', 'BE']
)

results = algorithm.generate_all_timetables()

# Check results
for year, year_results in results.items():
    if year == '_conflicts_report':
        conflicts = year_results
        print(f"Conflicts: {len(conflicts['teacher_conflicts'])} teacher, {len(conflicts['room_conflicts'])} room")
    else:
        for division, result in year_results.items():
            if result.get('timetable'):
                print(f"{year}-{division}: Success (Fitness: {result['fitness_score']})")
            else:
                print(f"{year}-{division}: Failed - {result.get('error')}")
"""