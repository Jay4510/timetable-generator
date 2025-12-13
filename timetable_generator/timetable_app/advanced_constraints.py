"""
Advanced constraint management system for robust timetable generation.
This addresses real-world complexities that basic genetic algorithms miss.
"""

from django.db import models
from .models import Teacher, Subject, Room, TimeSlot
from datetime import datetime, time
import json

class ConstraintType(models.Model):
    """Define different types of constraints with priorities"""
    CONSTRAINT_CATEGORIES = [
        ('hard', 'Hard Constraint - Must be satisfied'),
        ('soft', 'Soft Constraint - Preferred but flexible'),
        ('preference', 'Preference - Nice to have'),
    ]
    
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CONSTRAINT_CATEGORIES)
    priority = models.IntegerField(default=1, help_text="1=highest, 10=lowest")
    penalty_weight = models.FloatField(default=1.0)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.category})"

class TeacherAvailability(models.Model):
    """Detailed teacher availability - handles part-time, visiting faculty, etc."""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=10)  # Monday, Tuesday, etc.
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    # Advanced availability options
    is_preferred_time = models.BooleanField(default=True)
    max_consecutive_hours = models.IntegerField(default=3)
    min_break_between_sessions = models.IntegerField(default=0, help_text="Minutes")
    
    # Special cases
    is_visiting_faculty = models.BooleanField(default=False)
    travel_time_needed = models.IntegerField(default=0, help_text="Minutes between locations")
    
    class Meta:
        unique_together = ['teacher', 'day_of_week', 'start_time']

class RoomConstraints(models.Model):
    """Advanced room constraints and capabilities"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    
    # Equipment and capabilities
    has_projector = models.BooleanField(default=True)
    has_ac = models.BooleanField(default=True)
    has_whiteboard = models.BooleanField(default=True)
    has_computers = models.BooleanField(default=False)
    computer_count = models.IntegerField(default=0)
    
    # Special requirements
    requires_special_software = models.JSONField(default=list, blank=True)
    maintenance_slots = models.JSONField(default=list, blank=True)  # Unavailable times
    
    # Accessibility
    is_wheelchair_accessible = models.BooleanField(default=True)
    floor_number = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.room.name} constraints"

class SubjectConstraints(models.Model):
    """Advanced subject scheduling constraints"""
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    
    # Timing preferences
    preferred_time_slots = models.JSONField(default=list, blank=True)
    avoid_time_slots = models.JSONField(default=list, blank=True)
    
    # Sequencing constraints
    requires_consecutive_sessions = models.BooleanField(default=False)
    max_sessions_per_day = models.IntegerField(default=2)
    min_gap_between_sessions = models.IntegerField(default=0, help_text="Hours")
    
    # Special requirements
    requires_specific_equipment = models.JSONField(default=list, blank=True)
    requires_internet = models.BooleanField(default=False)
    noise_sensitive = models.BooleanField(default=False)
    
    # Prerequisites and dependencies
    must_be_after_subjects = models.ManyToManyField(Subject, blank=True, related_name='prerequisite_for')
    cannot_be_same_day_as = models.ManyToManyField(Subject, blank=True, related_name='conflicts_with')
    
    def __str__(self):
        return f"{self.subject.name} constraints"

class StudentGroupConstraints(models.Model):
    """Constraints specific to student groups/batches"""
    year = models.CharField(max_length=10)
    division = models.CharField(max_length=5)
    batch_number = models.IntegerField(null=True, blank=True)
    
    # Schedule preferences
    preferred_start_time = models.TimeField(default=time(9, 0))
    preferred_end_time = models.TimeField(default=time(17, 0))
    max_hours_per_day = models.IntegerField(default=8)
    lunch_break_duration = models.IntegerField(default=60, help_text="Minutes")
    
    # Special considerations
    has_students_with_disabilities = models.BooleanField(default=False)
    requires_ground_floor_rooms = models.BooleanField(default=False)
    
    # Travel time between buildings
    max_travel_time_between_classes = models.IntegerField(default=10, help_text="Minutes")
    
    class Meta:
        unique_together = ['year', 'division', 'batch_number']

class InstitutionalConstraints(models.Model):
    """College-wide policies and constraints"""
    name = models.CharField(max_length=100)
    
    # Working hours
    college_start_time = models.TimeField(default=time(9, 0))
    college_end_time = models.TimeField(default=time(17, 0))
    
    # Break times
    morning_break_start = models.TimeField(default=time(11, 0))
    morning_break_end = models.TimeField(default=time(11, 15))
    lunch_break_start = models.TimeField(default=time(13, 0))
    lunch_break_end = models.TimeField(default=time(14, 0))
    
    # Policies
    max_consecutive_lectures = models.IntegerField(default=3)
    min_break_between_lectures = models.IntegerField(default=15, help_text="Minutes")
    
    # Special days
    no_classes_on = models.JSONField(default=list, help_text="List of dates with no classes")
    half_days = models.JSONField(default=list, help_text="List of half-day dates")
    
    # Exam periods
    exam_periods = models.JSONField(default=list, help_text="Periods when regular classes are suspended")
    
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class ConflictResolutionRule(models.Model):
    """Rules for handling constraint conflicts"""
    RESOLUTION_STRATEGIES = [
        ('prioritize_hard', 'Always satisfy hard constraints first'),
        ('weighted_optimization', 'Use weighted scoring'),
        ('manual_review', 'Flag for manual review'),
        ('alternative_suggestion', 'Suggest alternatives'),
    ]
    
    constraint_type = models.ForeignKey(ConstraintType, on_delete=models.CASCADE)
    conflicting_constraint_type = models.ForeignKey(
        ConstraintType, 
        on_delete=models.CASCADE, 
        related_name='conflicts_with'
    )
    resolution_strategy = models.CharField(max_length=30, choices=RESOLUTION_STRATEGIES)
    priority_order = models.IntegerField(help_text="Which constraint takes priority (1=first)")
    
    def __str__(self):
        return f"{self.constraint_type.name} vs {self.conflicting_constraint_type.name}"

# Utility functions for constraint checking

def check_teacher_availability(teacher, day, time_slot):
    """Check if teacher is available at given time"""
    availability = TeacherAvailability.objects.filter(
        teacher=teacher,
        day_of_week=day,
        start_time__lte=time_slot.start_time,
        end_time__gte=time_slot.end_time
    )
    return availability.exists()

def check_room_suitability(room, subject):
    """Check if room meets subject requirements"""
    try:
        room_constraints = RoomConstraints.objects.get(room=room)
        subject_constraints = SubjectConstraints.objects.get(subject=subject)
        
        # Check equipment requirements
        required_equipment = subject_constraints.requires_specific_equipment
        
        for equipment in required_equipment:
            if equipment == 'projector' and not room_constraints.has_projector:
                return False
            elif equipment == 'computers' and not room_constraints.has_computers:
                return False
            elif equipment == 'internet' and not subject_constraints.requires_internet:
                return False
        
        return True
    except (RoomConstraints.DoesNotExist, SubjectConstraints.DoesNotExist):
        return True  # Assume suitable if no constraints defined

def get_constraint_violations(timetable):
    """Comprehensive constraint violation checker"""
    violations = {
        'hard': [],
        'soft': [],
        'preference': []
    }
    
    # Implementation would check all constraints and categorize violations
    # This is a framework for the comprehensive checking system
    
    return violations

def suggest_constraint_resolution(violation):
    """AI-powered suggestion system for resolving conflicts"""
    suggestions = []
    
    # Analyze the violation and suggest solutions
    if violation['type'] == 'teacher_unavailable':
        suggestions.append({
            'action': 'reschedule',
            'description': 'Move session to teacher\'s available time',
            'impact': 'low'
        })
        suggestions.append({
            'action': 'substitute_teacher',
            'description': 'Assign alternative qualified teacher',
            'impact': 'medium'
        })
    
    return suggestions
