# FINAL PRODUCTION-READY TIMETABLE ALGORITHM 
# Enhanced with Morning/Afternoon Balance + Mid-Semester Integration
# File: final_production_timetable_algorithm.py (DIRECT REPLACEMENT)

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
    Teacher, Subject, Room, Lab, TimeSlot, Session, Year, Division, Batch,
    SubjectProficiency, SystemConfiguration, ProjectWork, TimetableIncharge
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MidSemesterReplacementTracker:
    """Simple mid-semester faculty replacement tracking"""
    
    def __init__(self):
        self.replacements = {}  # {old_teacher_id: new_teacher_id}
        self.replacement_dates = {}  # {old_teacher_id: replacement_date}
        self.replacement_notes = {}  # {old_teacher_id: notes}
    
    def add_replacement(self, old_teacher_id, new_teacher_id, replacement_date, notes=""):
        """TT Incharge enters replacement information"""
        self.replacements[old_teacher_id] = new_teacher_id
        self.replacement_dates[old_teacher_id] = replacement_date
        self.replacement_notes[old_teacher_id] = notes
        
        logger.info(f"Mid-semester replacement: Teacher {old_teacher_id} → {new_teacher_id} on {replacement_date}")
    
    def get_current_teacher(self, original_teacher_id, current_date=None):
        """Get current teacher (considering replacements)"""
        if current_date is None:
            current_date = timezone.now().date()
        
        # Check if there's a replacement
        if original_teacher_id in self.replacements:
            replacement_date = self.replacement_dates[original_teacher_id]
            if current_date >= replacement_date:
                return self.replacements[original_teacher_id]
        
        return original_teacher_id
    
    def get_replacement_history(self):
        """Get complete replacement history for reporting"""
        return {
            'replacements': self.replacements,
            'dates': self.replacement_dates,
            'notes': self.replacement_notes
        }


class EnhancedTimetableConfiguration:
    """Enhanced configuration with morning/afternoon balance and mid-semester support"""
    
    def __init__(self, config_data):
        # Basic configuration
        self.college_start_time = config_data.get('college_start_time', time(9, 0))
        self.college_end_time = config_data.get('college_end_time', time(17, 45))
        self.recess_start = config_data.get('recess_start', time(13, 0))
        self.recess_end = config_data.get('recess_end', time(13, 45))
        
        # Professor assignments by year
        self.professor_year_assignments = config_data.get('professor_year_assignments', {})
        
        # Proficiency data (with mid-semester updates support)
        self.proficiency_data = config_data.get('proficiency_data', {})
        
        # Room assignments by year (can overlap)
        self.room_assignments = config_data.get('room_assignments', {})
        
        # Remedial configuration per year
        self.remedial_config = config_data.get('remedial_config', {})
        
        # Professor preferences
        self.professor_preferences = config_data.get('professor_preferences', {})
        
        # Division configuration per year
        self.division_config = config_data.get('division_config', {})
        
        # Batch configuration per division
        self.batch_config = config_data.get('batch_config', {})
        
        # Project work configuration per year
        self.project_config = config_data.get('project_config', {})
        
        # NEW: Morning/Afternoon balance configuration
        self.balance_config = config_data.get('balance_config', {
            'enforce_balance': True,  # Enable morning/afternoon balance
            'balance_tolerance': 0.3,  # 30% tolerance (70-30 split acceptable)
            'prefer_morning_subjects': [],  # Subject IDs that prefer morning
            'prefer_afternoon_subjects': [],  # Subject IDs that prefer afternoon
            'balance_per_division': True  # Balance within each division
        })
        
        # NEW: Mid-semester replacement support
        self.mid_semester_replacements = config_data.get('mid_semester_replacements', {})
        self.replacement_tracker = MidSemesterReplacementTracker()
        
        # Load existing replacements
        for old_id, replacement_info in self.mid_semester_replacements.items():
            self.replacement_tracker.add_replacement(
                old_teacher_id=int(old_id),
                new_teacher_id=replacement_info['new_teacher_id'],
                replacement_date=replacement_info['replacement_date'],
                notes=replacement_info.get('notes', '')
            )
        
        # Generate time slots based on college hours
        self.time_slots = self._generate_time_slots()
        self.morning_slots = self._identify_morning_slots()
        self.afternoon_slots = self._identify_afternoon_slots()
    
    def _generate_time_slots(self):
        """Generate time slots based on college start/end times"""
        slots = {}
        slot_number = 1
        
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
    
    def _identify_morning_slots(self):
        """Identify morning time slots"""
        morning_slots = []
        for slot_num, slot_info in self.time_slots.items():
            if not slot_info.get('is_recess', False) and slot_info['start'] < self.recess_start:
                morning_slots.append(slot_num)
        return morning_slots
    
    def _identify_afternoon_slots(self):
        """Identify afternoon time slots"""
        afternoon_slots = []
        for slot_num, slot_info in self.time_slots.items():
            if not slot_info.get('is_recess', False) and slot_info['start'] >= self.recess_end:
                afternoon_slots.append(slot_num)
        return afternoon_slots
    
    def get_current_teacher_for_assignment(self, original_teacher_id):
        """Get current teacher considering mid-semester replacements"""
        return self.replacement_tracker.get_current_teacher(original_teacher_id)
    
    def add_mid_semester_replacement(self, old_teacher_id, new_teacher_id, replacement_date, notes=""):
        """TT Incharge adds mid-semester replacement"""
        self.replacement_tracker.add_replacement(old_teacher_id, new_teacher_id, replacement_date, notes)
        
        # Update proficiency data for new teacher (if not exists, copy from old teacher)
        if new_teacher_id not in self.proficiency_data and old_teacher_id in self.proficiency_data:
            self.proficiency_data[new_teacher_id] = self.proficiency_data[old_teacher_id].copy()
            logger.info(f"Copied proficiency data from teacher {old_teacher_id} to {new_teacher_id}")
    
    def get_professor_proficiency(self, teacher_id, subject_id):
        """Get proficiency scores considering mid-semester replacements"""
        # Get current teacher (may be replacement)
        current_teacher_id = self.get_current_teacher_for_assignment(teacher_id)
        
        teacher_profs = self.proficiency_data.get(current_teacher_id, {})
        subject_prof = teacher_profs.get(subject_id, {'knowledge': 5.0, 'willingness': 5.0})
        
        knowledge = subject_prof.get('knowledge', 5.0)
        willingness = subject_prof.get('willingness', 5.0)
        
        return (knowledge * 0.6) + (willingness * 0.4)
    
    def get_professor_time_preference(self, teacher_id):
        """Get professor's time preference considering replacements"""
        current_teacher_id = self.get_current_teacher_for_assignment(teacher_id)
        prefs = self.professor_preferences.get(current_teacher_id, {})
        return prefs.get('first_half_second_half', 'flexible')
    
    # Existing methods remain the same...
    def get_available_professors_for_year(self, year_name):
        return self.professor_year_assignments.get(year_name, [])
    
    def get_available_rooms_for_year(self, year_name, room_type='lectures'):
        year_rooms = self.room_assignments.get(year_name, {})
        return year_rooms.get(room_type, [])
    
    def get_divisions_for_year(self, year_name):
        return self.division_config.get(year_name, ['A', 'B'])
    
    def get_batches_for_division(self, division_key):
        return self.batch_config.get(division_key, 3)
    
    def get_project_halves_for_year(self, year_name):
        return self.project_config.get(year_name, 0)
    
    def get_remedial_count_for_year(self, year_name):
        return self.remedial_config.get(year_name, 1)


class EnhancedMorningAfternoonBalance:
    """Enforces morning/afternoon balance for fairness"""
    
    def __init__(self, config: EnhancedTimetableConfiguration):
        self.config = config
        self.balance_config = config.balance_config
    
    def check_division_balance(self, genes, division):
        """Check morning/afternoon balance for division"""
        if not self.balance_config.get('enforce_balance', True):
            return 0  # Balance checking disabled
        
        violations = 0
        morning_sessions = []
        afternoon_sessions = []
        
        # Categorize sessions by morning/afternoon
        for gene in genes:
            slot_number = gene[3]
            
            if slot_number in self.config.morning_slots:
                morning_sessions.append(gene)
            elif slot_number in self.config.afternoon_slots:
                afternoon_sessions.append(gene)
        
        total_sessions = len(morning_sessions) + len(afternoon_sessions)
        
        if total_sessions == 0:
            return 0
        
        morning_ratio = len(morning_sessions) / total_sessions
        afternoon_ratio = len(afternoon_sessions) / total_sessions
        
        # Target: 50-50 balance with tolerance
        tolerance = self.balance_config.get('balance_tolerance', 0.3)
        target_ratio = 0.5
        
        # Check if balance is within tolerance
        morning_deviation = abs(morning_ratio - target_ratio)
        afternoon_deviation = abs(afternoon_ratio - target_ratio)
        
        if morning_deviation > tolerance:
            violations += int(morning_deviation * 100)  # Scale violation
        
        if afternoon_deviation > tolerance:
            violations += int(afternoon_deviation * 100)
        
        return violations
    
    def check_subject_time_preferences(self, genes):
        """Check subject-specific time preferences"""
        violations = 0
        
        prefer_morning = self.balance_config.get('prefer_morning_subjects', [])
        prefer_afternoon = self.balance_config.get('prefer_afternoon_subjects', [])
        
        for gene in genes:
            subject_id = gene[0]
            slot_number = gene[3]
            
            # Check morning preference violations
            if subject_id in prefer_morning and slot_number not in self.config.morning_slots:
                violations += 15  # Penalty for wrong time placement
            
            # Check afternoon preference violations
            if subject_id in prefer_afternoon and slot_number not in self.config.afternoon_slots:
                violations += 15
        
        return violations
    
    def get_balance_statistics(self, genes):
        """Get balance statistics for reporting"""
        morning_count = sum(1 for gene in genes if gene[3] in self.config.morning_slots)
        afternoon_count = sum(1 for gene in genes if gene[3] in self.config.afternoon_slots)
        total = morning_count + afternoon_count
        
        if total == 0:
            return {'morning_ratio': 0, 'afternoon_ratio': 0, 'balance_score': 0}
        
        morning_ratio = morning_count / total
        afternoon_ratio = afternoon_count / total
        balance_score = 100 - (abs(morning_ratio - 0.5) * 200)  # 100 = perfect balance
        
        return {
            'morning_count': morning_count,
            'afternoon_count': afternoon_count,
            'morning_ratio': morning_ratio,
            'afternoon_ratio': afternoon_ratio,
            'balance_score': balance_score
        }


class EnhancedProficiencyBasedTeacherSelector:
    """Enhanced teacher selector with mid-semester replacement support"""
    
    def __init__(self, config: EnhancedTimetableConfiguration):
        self.config = config
        self.teacher_availability = defaultdict(lambda: defaultdict(bool))
    
    def select_best_teacher_for_subject(self, subject, year_name, exclude_teachers=None):
        """Select best teacher considering mid-semester replacements"""
        exclude_teachers = exclude_teachers or []
        available_teachers = self.config.get_available_professors_for_year(year_name)
        
        candidates = []
        
        for teacher_id in available_teachers:
            if teacher_id in exclude_teachers:
                continue
            
            # Get current teacher (may be replacement)
            current_teacher_id = self.config.get_current_teacher_for_assignment(teacher_id)
            
            try:
                teacher = Teacher.objects.get(id=current_teacher_id)
                proficiency = self.config.get_professor_proficiency(teacher_id, subject.id)
                
                candidates.append({
                    'original_teacher_id': teacher_id,
                    'current_teacher_id': current_teacher_id,
                    'teacher': teacher,
                    'proficiency': proficiency,
                    'is_replacement': current_teacher_id != teacher_id
                })
                
            except Teacher.DoesNotExist:
                logger.warning(f"Teacher {current_teacher_id} not found (replacement scenario)")
                continue
        
        if not candidates:
            return None
        
        # Sort by proficiency (highest first)
        candidates.sort(key=lambda x: x['proficiency'], reverse=True)
        
        return candidates[0]
    
    def check_teacher_availability(self, teacher_id, slot_number):
        return self.teacher_availability[teacher_id][slot_number]
    
    def mark_teacher_busy(self, teacher_id, slot_number):
        self.teacher_availability[teacher_id][slot_number] = False
    
    def mark_teacher_available(self, teacher_id, slot_number):
        self.teacher_availability[teacher_id][slot_number] = True


class EnhancedCrossYearResourceManager:
    """Enhanced resource manager with mid-semester replacement tracking"""
    
    def __init__(self, config: EnhancedTimetableConfiguration):
        self.config = config
        self.global_room_usage = defaultdict(lambda: defaultdict(list))
        self.global_teacher_usage = defaultdict(lambda: defaultdict(list))
    
    def check_room_availability(self, room_id, slot_number, year_name):
        current_users = self.global_room_usage[room_id][slot_number]
        return len(current_users) == 0 or year_name in [user.split('-')[0] for user in current_users]
    
    def allocate_room(self, room_id, slot_number, year_name, division_name):
        self.global_room_usage[room_id][slot_number].append(f"{year_name}-{division_name}")
    
    def check_teacher_cross_year_availability(self, teacher_id, slot_number):
        # Consider both original and replacement teacher
        current_teacher_id = self.config.get_current_teacher_for_assignment(teacher_id)
        
        # Check availability for both original and current teacher
        original_allocations = self.global_teacher_usage[teacher_id][slot_number]
        current_allocations = self.global_teacher_usage[current_teacher_id][slot_number]
        
        return len(original_allocations) == 0 and len(current_allocations) == 0
    
    def allocate_teacher(self, teacher_id, slot_number, year_name, division_name, subject_name):
        current_teacher_id = self.config.get_current_teacher_for_assignment(teacher_id)
        
        allocation_info = {
            'year_div': f"{year_name}-{division_name}",
            'subject': subject_name,
            'original_teacher': teacher_id,
            'current_teacher': current_teacher_id,
            'is_replacement': current_teacher_id != teacher_id
        }
        
        # Allocate under current teacher ID
        self.global_teacher_usage[current_teacher_id][slot_number].append(allocation_info)
    
    def get_conflicts_report(self):
        """Generate enhanced conflicts report with replacement info"""
        conflicts = {
            'teacher_conflicts': [],
            'room_conflicts': [],
            'replacement_conflicts': []
        }
        
        # Teacher conflicts
        for teacher_id, schedule in self.global_teacher_usage.items():
            for slot, allocations in schedule.items():
                if len(allocations) > 1:
                    try:
                        teacher_name = Teacher.objects.get(id=teacher_id).name
                        conflicts['teacher_conflicts'].append({
                            'teacher': teacher_name,
                            'teacher_id': teacher_id,
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
        
        # Replacement-specific conflicts
        replacement_history = self.config.replacement_tracker.get_replacement_history()
        conflicts['replacement_conflicts'] = replacement_history
        
        return conflicts


class EnhancedUserConfigurableChromosome:
    """Enhanced chromosome with morning/afternoon balance and mid-semester support"""
    
    def __init__(self, genes=None, division=None, year=None, config=None):
        self.genes = genes if genes is not None else []
        self.division = division
        self.year = year
        self.config = config
        self.fitness_score = None
        self.violations = {}
        self.balance_checker = EnhancedMorningAfternoonBalance(config) if config else None
    
    def fitness(self, algorithm_instance):
        """Enhanced fitness calculation with morning/afternoon balance"""
        if self.fitness_score is not None:
            return self.fitness_score
        
        violations = 0
        
        try:
            # Core conflicts (always critical)
            violations += self._check_teacher_conflicts()
            violations += self._check_room_conflicts() 
            violations += self._check_student_conflicts()
            violations += self._check_recess_violations()
            
            # Lab continuity (2-hour blocks)
            violations += self._check_lab_continuity()
            
            # Project work blocks (half-day periods)
            violations += self._check_project_blocks()
            
            # Proficiency matching (with replacement support)
            violations += self._check_proficiency_matching()
            
            # Teacher preferences (with replacement support)
            violations += self._check_teacher_time_preferences()
            
            # NEW: Morning/Afternoon balance
            violations += self._check_morning_afternoon_balance()
            
            # Room capacity
            violations += self._check_room_capacity()
            
        except Exception as e:
            logger.error(f"Error in enhanced fitness calculation: {e}")
            violations += 10000
        
        self.fitness_score = -violations
        return self.fitness_score
    
    def _check_morning_afternoon_balance(self):
        """NEW: Check morning/afternoon balance constraint"""
        violations = 0
        
        if self.balance_checker:
            # Check division-level balance
            balance_violations = self.balance_checker.check_division_balance(self.genes, self.division)
            violations += balance_violations
            
            # Check subject time preferences
            preference_violations = self.balance_checker.check_subject_time_preferences(self.genes)
            violations += preference_violations
        
        return violations
    
    def _check_proficiency_matching(self):
        """Enhanced proficiency check with replacement support"""
        violations = 0
        
        for gene in self.genes:
            try:
                subject_id = gene[0]
                teacher_id = gene[1]
                
                # Get proficiency considering mid-semester replacements
                proficiency = self.config.get_professor_proficiency(teacher_id, subject_id)
                
                if proficiency < 6.0:  # Below acceptable threshold
                    violations += int((6.0 - proficiency) * 10)
                elif proficiency >= 8.0:  # Excellent match
                    violations -= 2  # Small bonus
                    
            except Exception as e:
                violations += 50
        
        return violations
    
    def _check_teacher_time_preferences(self):
        """Enhanced preference check with replacement support"""
        violations = 0
        
        for gene in self.genes:
            try:
                teacher_id = gene[1]
                slot_number = gene[3]
                
                # Get preference considering replacements
                preference = self.config.get_professor_time_preference(teacher_id)
                
                if preference != 'flexible':
                    slot_time = self.config.time_slots.get(slot_number, {}).get('start')
                    
                    if slot_time:
                        is_morning = slot_time < time(13, 0)
                        
                        if (preference == 'morning' and not is_morning) or \
                           (preference == 'afternoon' and is_morning):
                            violations += 5
                            
            except Exception as e:
                logger.warning(f"Error checking enhanced preferences: {e}")
        
        return violations
    
    def get_balance_report(self):
        """Get morning/afternoon balance report"""
        if self.balance_checker:
            return self.balance_checker.get_balance_statistics(self.genes)
        return {}
    
    # Existing constraint methods remain the same...
    def _check_teacher_conflicts(self):
        violations = 0
        teacher_schedule = defaultdict(list)
        
        for gene in self.genes:
            teacher_id = gene[1]
            slot_number = gene[3]
            teacher_schedule[teacher_id].append(slot_number)
        
        for teacher_id, slots in teacher_schedule.items():
            conflicts = len(slots) - len(set(slots))
            violations += conflicts * 100
        
        return violations
    
    def _check_room_conflicts(self):
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
        violations = 0
        
        for gene in self.genes:
            slot_number = gene[3]
            slot_info = self.config.time_slots.get(slot_number, {})
            
            if slot_info.get('is_recess', False):
                violations += 150
        
        return violations
    
    def _check_lab_continuity(self):
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
                violations += 80
            elif len(unique_slots) == 2:
                slot1, slot2 = unique_slots
                if slot2 - slot1 != 1:
                    violations += 80
            elif len(unique_slots) > 2:
                violations += (len(unique_slots) - 2) * 40
        
        return violations
    
    def _check_project_blocks(self):
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
            
            if len(unique_slots) != 4:
                violations += 60
            else:
                for i in range(3):
                    if unique_slots[i+1] - unique_slots[i] != 1:
                        violations += 60
                        break
        
        return violations
    
    def _check_room_capacity(self):
        violations = 0
        
        for gene in self.genes:
            try:
                room_id = gene[2]
                batch_id = gene[4]
                
                if room_id and batch_id:
                    division_key = f"{self.year}-{self.division.name}"
                    students_per_batch = self.config.get_batches_for_division(division_key)
                    total_students = students_per_batch * 10
                    
                    room_capacity = 50
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


class FinalProductionTimetableAlgorithm:
    """FINAL production-ready algorithm with all enhancements"""
    
    def __init__(self, config_data, target_years=None):
        self.config = EnhancedTimetableConfiguration(config_data)
        self.target_years = target_years or ['FE', 'SE', 'TE', 'BE']
        
        # Enhanced components
        self.teacher_selector = EnhancedProficiencyBasedTeacherSelector(self.config)
        self.resource_manager = EnhancedCrossYearResourceManager(self.config)
        
        # Algorithm parameters
        self.population_size = 40
        self.generations = 200
        self.mutation_rate = 0.25
        self.elite_count = 4
        
        # Initialize data
        self._initialize_data()
        
        logger.info(f"Final production algorithm initialized for years: {self.target_years}")
        logger.info(f"Morning/Afternoon balance: {'Enabled' if self.config.balance_config['enforce_balance'] else 'Disabled'}")
        logger.info(f"Mid-semester replacements: {len(self.config.replacement_tracker.replacements)} active")
    
    def add_mid_semester_replacement(self, old_teacher_id, new_teacher_id, replacement_date, notes=""):
        """TT Incharge interface for adding mid-semester replacement"""
        self.config.add_mid_semester_replacement(old_teacher_id, new_teacher_id, replacement_date, notes)
        logger.info(f"Added mid-semester replacement: {old_teacher_id} → {new_teacher_id}")
    
    def generate_all_timetables(self):
        """Generate timetables with all enhancements"""
        results = {}
        
        logger.info("Starting final production timetable generation...")
        
        # Process each year
        for year_name in self.target_years:
            year_results = self._generate_year_timetables(year_name)
            results[year_name] = year_results
        
        # Generate enhanced conflicts report
        conflicts = self.resource_manager.get_conflicts_report()
        results['_conflicts_report'] = conflicts
        results['_balance_report'] = self._generate_balance_report(results)
        results['_replacement_report'] = self.config.replacement_tracker.get_replacement_history()
        
        # Log summary
        total_divisions = sum(len(year_results) for year_results in results.values() if isinstance(year_results, dict))
        successful = sum(1 for year_results in results.values() 
                        if isinstance(year_results, dict) 
                        for result in year_results.values() 
                        if result.get('timetable'))
        
        logger.info(f"Generation complete: {successful}/{total_divisions} divisions successful")
        logger.info(f"Conflicts: {len(conflicts['teacher_conflicts'])} teacher, {len(conflicts['room_conflicts'])} room")
        
        return results
    
    def _generate_balance_report(self, results):
        """Generate morning/afternoon balance report"""
        balance_report = {}
        
        for year_name, year_results in results.items():
            if isinstance(year_results, dict) and not year_name.startswith('_'):
                balance_report[year_name] = {}
                
                for division_name, result in year_results.items():
                    if result.get('timetable'):
                        balance_stats = result['timetable'].get_balance_report()
                        balance_report[year_name][division_name] = balance_stats
        
        return balance_report
    
    def _generate_year_timetables(self, year_name):
        """Generate timetables for all divisions in a year"""
        year_results = {}
        
        try:
            year = Year.objects.get(name=year_name)
            divisions = Division.objects.filter(year=year)
            
            for division in divisions:
                division_result = self._generate_division_timetable(division, year_name)
                year_results[division.name] = division_result
                
        except Exception as e:
            logger.error(f"Error generating timetables for year {year_name}: {e}")
            year_results['error'] = str(e)
        
        return year_results
    
    def _generate_division_timetable(self, division, year_name):
        """Generate enhanced timetable for single division"""
        try:
            logger.info(f"Generating enhanced timetable for {year_name} Division {division.name}")
            
            # Create population
            population = self._create_population(division, year_name)
            
            if not population:
                return {'division': division, 'timetable': None, 'error': 'Population creation failed'}
            
            # Evolve population
            best_solution = self._evolve_population(population, division, year_name)
            
            if best_solution:
                balance_stats = best_solution.get_balance_report()
                
                return {
                    'division': division,
                    'timetable': best_solution,
                    'fitness_score': best_solution.fitness_score,
                    'violations': best_solution.violations,
                    'balance_statistics': balance_stats,
                    'replacement_info': self._get_division_replacement_info(division, year_name)
                }
            else:
                return {'division': division, 'timetable': None, 'error': 'Evolution failed'}
                
        except Exception as e:
            logger.error(f"Error generating enhanced division timetable: {e}")
            return {'division': division, 'timetable': None, 'error': str(e)}
    
    def _get_division_replacement_info(self, division, year_name):
        """Get replacement info for division"""
        available_teachers = self.config.get_available_professors_for_year(year_name)
        replacement_info = {}
        
        for teacher_id in available_teachers:
            current_teacher_id = self.config.get_current_teacher_for_assignment(teacher_id)
            if current_teacher_id != teacher_id:
                replacement_info[teacher_id] = {
                    'original_teacher': teacher_id,
                    'replacement_teacher': current_teacher_id,
                    'replacement_date': self.config.replacement_tracker.replacement_dates.get(teacher_id),
                    'notes': self.config.replacement_tracker.replacement_notes.get(teacher_id, '')
                }
        
        return replacement_info
    
    def _create_population(self, division, year_name):
        """Create enhanced population for division"""
        population = []
        
        for _ in range(self.population_size):
            try:
                chromosome = self._create_chromosome(division, year_name)
                if chromosome and chromosome.genes:
                    population.append(chromosome)
            except Exception as e:
                logger.warning(f"Error creating enhanced chromosome: {e}")
        
        return population
    
    def _create_chromosome(self, division, year_name):
        """Create enhanced chromosome with balance consideration"""
        genes = []
        
        try:
            # Get division subjects
            subjects = Subject.objects.filter(year__name=year_name, division=division)
            
            # Get/create batches
            division_key = f"{year_name}-{division.name}"
            num_batches = self.config.get_batches_for_division(division_key)
            batches = self._ensure_batches_exist(division, num_batches)
            
            # Schedule each subject with balance consideration
            for subject in subjects:
                subject_genes = self._schedule_subject_with_balance(subject, division, year_name, batches)
                genes.extend(subject_genes)
            
            # Add remedial if configured
            remedial_count = self.config.get_remedial_count_for_year(year_name)
            if remedial_count > 0:
                remedial_genes = self._schedule_remedial(division, year_name, batches, remedial_count)
                genes.extend(remedial_genes)
            
            return EnhancedUserConfigurableChromosome(genes, division, year_name, self.config)
            
        except Exception as e:
            logger.error(f"Error creating enhanced chromosome: {e}")
            return None
    
    def _schedule_subject_with_balance(self, subject, division, year_name, batches):
        """Schedule subject considering morning/afternoon balance"""
        genes = []
        
        try:
            is_lab = getattr(subject, 'requires_lab', False)
            is_project = getattr(subject, 'is_project_work', False)
            
            if is_project:
                genes = self._schedule_project_work(subject, division, year_name, batches)
            elif is_lab:
                genes = self._schedule_lab_subject(subject, division, year_name, batches)
            else:
                genes = self._schedule_lecture_with_balance(subject, division, year_name, batches)
                
        except Exception as e:
            logger.warning(f"Error scheduling subject with balance: {e}")
        
        return genes
    
    def _schedule_lecture_with_balance(self, subject, division, year_name, batches):
        """Schedule lecture considering morning/afternoon balance"""
        genes = []
        
        try:
            # Get teacher with replacement support
            teacher_selection = self.teacher_selector.select_best_teacher_for_subject(subject, year_name)
            
            if not teacher_selection:
                return genes
            
            teacher_id = teacher_selection['original_teacher_id']
            current_teacher = teacher_selection['teacher']
            
            # Get teacher's time preference (from current teacher)
            time_pref = self.config.get_professor_time_preference(teacher_id)
            
            # Get available rooms
            available_rooms = self.config.get_available_rooms_for_year(year_name, 'lectures')
            
            if not available_rooms:
                return genes
            
            room_id = random.choice(available_rooms)
            
            # Balance-aware slot selection
            preferred_slots = self._get_balanced_slots_for_subject(subject, time_pref)
            sessions_needed = getattr(subject, 'sessions_per_week', 3)
            
            selected_slots = random.sample(
                preferred_slots, 
                min(sessions_needed, len(preferred_slots))
            )
            
            for slot in selected_slots:
                for batch in batches:
                    genes.append((subject.id, teacher_id, room_id, slot, batch.id))
                
                # Allocate resources globally
                self.resource_manager.allocate_teacher(
                    teacher_id, slot, year_name, division.name, subject.name
                )
                self.resource_manager.allocate_room(
                    room_id, slot, year_name, division.name
                )
                
        except Exception as e:
            logger.warning(f"Error scheduling balanced lecture: {e}")
        
        return genes
    
    def _get_balanced_slots_for_subject(self, subject, teacher_preference):
        """Get slots considering both teacher preference and balance requirements"""
        available_slots = [slot for slot in self.config.time_slots.keys() 
                          if not self.config.time_slots[slot].get('is_recess', False)]
        
        # Check subject-specific time preferences
        prefer_morning = self.config.balance_config.get('prefer_morning_subjects', [])
        prefer_afternoon = self.config.balance_config.get('prefer_afternoon_subjects', [])
        
        if subject.id in prefer_morning:
            preferred_slots = [s for s in available_slots if s in self.config.morning_slots]
        elif subject.id in prefer_afternoon:
            preferred_slots = [s for s in available_slots if s in self.config.afternoon_slots]
        elif teacher_preference == 'morning':
            preferred_slots = [s for s in available_slots if s in self.config.morning_slots]
        elif teacher_preference == 'afternoon':
            preferred_slots = [s for s in available_slots if s in self.config.afternoon_slots]
        else:
            # For flexible teachers, try to balance morning/afternoon
            morning_slots = [s for s in available_slots if s in self.config.morning_slots]
            afternoon_slots = [s for s in available_slots if s in self.config.afternoon_slots]
            
            # Mix morning and afternoon slots for balance
            preferred_slots = morning_slots + afternoon_slots
            random.shuffle(preferred_slots)
        
        return preferred_slots if preferred_slots else available_slots
    
    # Rest of the methods remain largely the same but use enhanced components
    def _schedule_project_work(self, subject, division, year_name, batches):
        """Schedule project work (existing logic)"""
        genes = []
        
        try:
            teacher_selection = self.teacher_selector.select_best_teacher_for_subject(subject, year_name)
            
            if not teacher_selection:
                return genes
            
            teacher_id = teacher_selection['original_teacher_id']
            time_pref = self.config.get_professor_time_preference(teacher_id)
            
            # Project work scheduling logic (4-hour blocks)
            if time_pref == 'morning':
                slots = self.config.morning_slots[:4]  # First 4 morning slots
            elif time_pref == 'afternoon':
                slots = self.config.afternoon_slots[:4]  # First 4 afternoon slots
            else:
                slots = random.choice([self.config.morning_slots[:4], self.config.afternoon_slots[:4]])
            
            available_rooms = self.config.get_available_rooms_for_year(year_name, 'lectures')
            if available_rooms:
                room_id = random.choice(available_rooms)
                
                for batch in batches:
                    for slot in slots:
                        genes.append((subject.id, teacher_id, room_id, slot, batch.id))
                        
        except Exception as e:
            logger.warning(f"Error scheduling enhanced project work: {e}")
        
        return genes
    
    def _schedule_lab_subject(self, subject, division, year_name, batches):
        """Schedule lab subject (existing logic with enhancements)"""
        genes = []
        
        try:
            teacher_selection = self.teacher_selector.select_best_teacher_for_subject(subject, year_name)
            
            if not teacher_selection:
                return genes
            
            teacher_id = teacher_selection['original_teacher_id']
            available_labs = self.config.get_available_rooms_for_year(year_name, 'labs')
            
            if not available_labs:
                return genes
            
            lab_id = random.choice(available_labs)
            
            # Find 2 consecutive available slots
            available_slots = [slot for slot in self.config.time_slots.keys() 
                             if not self.config.time_slots[slot].get('is_recess', False)]
            
            for i in range(len(available_slots) - 1):
                slot1, slot2 = available_slots[i], available_slots[i + 1]
                
                if (slot2 - slot1 == 1 and 
                    self.resource_manager.check_teacher_cross_year_availability(teacher_id, slot1) and
                    self.resource_manager.check_teacher_cross_year_availability(teacher_id, slot2) and
                    self.resource_manager.check_room_availability(lab_id, slot1, year_name) and
                    self.resource_manager.check_room_availability(lab_id, slot2, year_name)):
                    
                    for batch in batches:
                        genes.append((subject.id, teacher_id, lab_id, slot1, batch.id))
                        genes.append((subject.id, teacher_id, lab_id, slot2, batch.id))
                    
                    # Allocate resources
                    for slot in [slot1, slot2]:
                        self.resource_manager.allocate_teacher(
                            teacher_id, slot, year_name, division.name, subject.name
                        )
                        self.resource_manager.allocate_room(
                            lab_id, slot, year_name, division.name
                        )
                    
                    break
                    
        except Exception as e:
            logger.warning(f"Error scheduling enhanced lab: {e}")
        
        return genes
    
    # Remaining methods (evolution, mutation, etc.) remain the same
    def _schedule_remedial(self, division, year_name, batches, remedial_count):
        """Schedule remedial (existing logic)"""
        genes = []
        
        try:
            available_teachers = self.config.get_available_professors_for_year(year_name)
            if available_teachers:
                teacher_id = random.choice(available_teachers)
                available_rooms = self.config.get_available_rooms_for_year(year_name, 'lectures')
                
                if available_rooms:
                    room_id = random.choice(available_rooms)
                    available_slots = self.config.afternoon_slots  # Prefer afternoon for remedial
                    selected_slots = random.sample(available_slots, min(remedial_count, len(available_slots)))
                    
                    for slot in selected_slots:
                        for batch in batches:
                            genes.append((-1, teacher_id, room_id, slot, batch.id))
                        
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
        """Ensure batches exist for division (existing logic)"""
        batches = []
        
        for i in range(num_batches):
            batch_name = chr(65 + i)  # A, B, C, ...
            
            try:
                batch = Batch.objects.get(division=division, name=batch_name)
            except Batch.DoesNotExist:
                batch = Batch.objects.create(
                    division=division,
                    name=batch_name,
                    student_count=30
                )
            
            batches.append(batch)
        
        return batches
    
    def _evolve_population(self, population, division, year_name):
        """Evolve population (existing logic)"""
        for generation in range(self.generations):
            # Evaluate fitness
            for chromosome in population:
                chromosome.fitness(self)
            
            # Sort by fitness
            population.sort(key=lambda x: x.fitness_score, reverse=True)
            
            current_best = population[0].fitness_score
            
            # Logging
            if generation % 50 == 0:
                balance_stats = population[0].get_balance_report()
                balance_score = balance_stats.get('balance_score', 0)
                
                logger.info(f"{year_name}-{division.name} Gen {generation}: "
                           f"Fitness={current_best}, Balance={balance_score:.1f}%")
            
            # Early termination
            if current_best >= -10:
                logger.info(f"{year_name}-{division.name} converged at generation {generation}")
                break
            
            # Create next generation
            population = self._create_next_generation(population, division, year_name)
        
        return population[0] if population else None
    
    def _create_next_generation(self, population, division, year_name):
        """Create next generation (existing logic)"""
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
        """Tournament selection (existing logic)"""
        tournament = random.sample(population, min(tournament_size, len(population)))
        return max(tournament, key=lambda x: x.fitness_score)
    
    def _crossover(self, parent1, parent2, division, year_name):
        """Crossover (existing logic)"""
        if not parent1.genes or not parent2.genes:
            return copy.deepcopy(parent1)
        
        crossover_point = random.randint(1, min(len(parent1.genes), len(parent2.genes)) - 1)
        child_genes = parent1.genes[:crossover_point] + parent2.genes[crossover_point:]
        
        return EnhancedUserConfigurableChromosome(child_genes, division, year_name, self.config)
    
    def _mutate(self, chromosome):
        """Enhanced mutation (existing logic)"""
        if random.random() > self.mutation_rate or not chromosome.genes:
            return
        
        idx = random.randint(0, len(chromosome.genes) - 1)
        gene = list(chromosome.genes[idx])
        
        # Mutate time slot with balance consideration
        available_slots = [slot for slot in self.config.time_slots.keys() 
                          if not self.config.time_slots[slot].get('is_recess', False)]
        
        gene[3] = random.choice(available_slots)
        chromosome.genes[idx] = tuple(gene)
        chromosome.fitness_score = None
    
    def _initialize_data(self):
        """Initialize required data (existing logic)"""
        try:
            self.subjects = list(Subject.objects.all())
            self.teachers = list(Teacher.objects.all())
            self.rooms = list(Room.objects.all())
            self.labs = list(Lab.objects.all())
            
            logger.info(f"Initialized enhanced data: {len(self.subjects)} subjects, "
                       f"{len(self.teachers)} teachers, "
                       f"{len(self.rooms + self.labs)} rooms/labs")
            
        except Exception as e:
            logger.error(f"Failed to initialize enhanced data: {e}")
            raise


# USAGE EXAMPLE WITH ENHANCEMENTS
"""
# Enhanced configuration with new features
config_data = {
    # Basic configuration (same as before)
    'college_start_time': time(9, 0),
    'college_end_time': time(17, 45),
    'recess_start': time(13, 0),
    'recess_end': time(13, 45),
    
    # Professor assignments, proficiency data, etc. (same as before)
    'professor_year_assignments': {'TE': [4, 5, 6, 7, 8], 'BE': [6, 7, 8, 9, 10]},
    'proficiency_data': {5: {25: {'knowledge': 9.0, 'willingness': 8.5}}},
    
    # NEW: Morning/Afternoon balance configuration
    'balance_config': {
        'enforce_balance': True,  # Enable balance checking
        'balance_tolerance': 0.3,  # 30% tolerance (70-30 acceptable)
        'prefer_morning_subjects': [25, 26],  # Subject IDs for morning
        'prefer_afternoon_subjects': [27, 28],  # Subject IDs for afternoon
        'balance_per_division': True
    },
    
    # NEW: Mid-semester replacement support
    'mid_semester_replacements': {
        '5': {  # Gaidhane replaced by new teacher
            'new_teacher_id': 12,
            'replacement_date': datetime(2025, 10, 15).date(),
            'notes': 'Medical leave replacement'
        }
    }
}

# Create algorithm with enhancements
algorithm = FinalProductionTimetableAlgorithm(config_data, ['TE', 'BE'])

# TT Incharge can add replacement during semester
algorithm.add_mid_semester_replacement(
    old_teacher_id=6,  # Kumane
    new_teacher_id=13,  # New teacher
    replacement_date=datetime(2025, 11, 1).date(),
    notes="Resignation replacement"
)

# Generate timetables
results = algorithm.generate_all_timetables()

# Enhanced results structure
for year, year_results in results.items():
    if not year.startswith('_'):
        for division, result in year_results.items():
            if result.get('timetable'):
                print(f"{year}-{division}:")
                print(f"  Fitness: {result['fitness_score']}")
                print(f"  Balance: {result['balance_statistics']['balance_score']:.1f}%")
                print(f"  Replacements: {len(result['replacement_info'])}")

# View enhanced reports
print("Balance Report:", results['_balance_report'])
print("Replacement Report:", results['_replacement_report'])
print("Conflicts Report:", results['_conflicts_report'])
"""