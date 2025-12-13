from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# Academic structure
class Year(models.Model):
    name = models.CharField(max_length=10)  # SE, TE, BE

    def __str__(self):
        return self.name


class Division(models.Model):
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    name = models.CharField(max_length=5)   # A, B, C
    num_batches = models.IntegerField(default=3)     # SE has 3 batches each, TE/BE have 3 each
    student_count = models.IntegerField(default=30)  # Number of students in division

    def __str__(self):
        return f"{self.year.name} {self.name}"


# System Configuration Model for Incharge Settings
class SystemConfiguration(models.Model):
    """Global system configuration managed by timetable incharge"""
    
    # Break time configuration
    break_start_time = models.TimeField(default='13:00')  # Configurable break start
    break_end_time = models.TimeField(default='13:45')    # Configurable break end
    
    # Session distribution settings
    max_sessions_per_teacher_per_week = models.IntegerField(default=14)
    min_sessions_per_teacher_per_week = models.IntegerField(default=10)
    
    # Lab settings
    default_lab_duration_hours = models.IntegerField(default=2)
    allow_cross_year_lab_conflicts = models.BooleanField(default=False)
    
    # Remedial lecture settings
    remedial_lectures_per_week = models.IntegerField(default=1)
    remedial_preferred_time = models.CharField(
        max_length=20,
        choices=[('morning', 'Morning'), ('afternoon', 'Afternoon'), ('either', 'Either')],
        default='afternoon'
    )
    
    # Project time settings
    project_time_slots_per_week = models.IntegerField(default=2)
    
    # Morning/afternoon balance
    morning_afternoon_balance_percentage = models.IntegerField(default=50)  # 50-50 balance
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = "System Configuration"
        verbose_name_plural = "System Configurations"
    
    def __str__(self):
        return f"System Config - {self.created_at.strftime('%Y-%m-%d')}"


# Remedial Lecture Model
class RemedialLecture(models.Model):
    """Manages mandatory remedial lectures for subjects"""
    
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)
    teacher = models.ForeignKey('Teacher', on_delete=models.CASCADE)
    division = models.ForeignKey('Division', on_delete=models.CASCADE)
    
    # Scheduling preferences
    preferred_day = models.CharField(
        max_length=10,
        choices=[
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'), 
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('any', 'Any Day')
        ],
        default='any'
    )
    
    preferred_time = models.CharField(
        max_length=20,
        choices=[('morning', 'Morning'), ('afternoon', 'Afternoon'), ('either', 'Either')],
        default='afternoon'
    )
    
    is_scheduled = models.BooleanField(default=False)
    scheduled_timeslot = models.ForeignKey('TimeSlot', on_delete=models.SET_NULL, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['subject', 'division']  # One remedial per subject per division
        verbose_name = "Remedial Lecture"
        verbose_name_plural = "Remedial Lectures"
    
    def __str__(self):
        return f"Remedial: {self.subject.code} - {self.division}"


# Teachers (18 faculty members)
class Teacher(models.Model):
    PREFERENCE_CHOICES = [
        ('first_half', 'Prefer First Half (Before Lunch)'),
        ('second_half', 'Prefer Second Half (After Lunch)'),
        ('no_preference', 'No Preference'),
        ('mixed', 'Mixed (Both Halves)'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('resigned', 'Resigned'),
        ('on_leave', 'On Leave'),
        ('temporary', 'Temporary'),
    ]
    
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)
    department = models.CharField(max_length=100, default='Information Technology')
    max_sessions_per_week = models.IntegerField(default=14)
    experience_years = models.IntegerField(default=0, help_text="Years of teaching experience")
    specialization = models.CharField(max_length=200, blank=True, help_text="Area of specialization")
    
    # Enhanced fields for real-world functionality
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    time_preference = models.CharField(max_length=20, choices=PREFERENCE_CHOICES, default='no_preference')
    can_teach_labs = models.BooleanField(default=True)
    can_teach_projects = models.BooleanField(default=True)
    availability = models.JSONField(default=dict, blank=True)  # Store availability as JSON
    preferences = models.JSONField(default=dict, blank=True)  # Store preferences as JSON
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name


# Room models
class Room(models.Model):
    name = models.CharField(max_length=10)  # 801, 803, 303, etc.
    capacity = models.IntegerField(default=60)
    room_type = models.CharField(max_length=20, default='classroom')
    available = models.BooleanField(default=True)  # Room availability status
    available_equipment = models.JSONField(default=list)  # Equipment available in room

    def __str__(self):
        return self.name


class Lab(models.Model):
    name = models.CharField(max_length=10)  # 701, 702, 703, 706, 707, 902, 807
    capacity = models.IntegerField(default=30)
    lab_type = models.CharField(max_length=50, blank=True)
    available_equipment = models.JSONField(default=list)  # Equipment available in lab

    def __str__(self):
        return self.name


# Subject model
class Subject(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)  # AIDS-II, IOE, DEL-5-IRS, etc.
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    sessions_per_week = models.IntegerField(default=4)
    requires_lab = models.BooleanField(default=False)
    lecture_duration_hours = models.IntegerField(default=1)  # Variable lecture duration
    lab_frequency_per_week = models.IntegerField(default=1)  # Configurable lab frequency
    requires_remedial = models.BooleanField(default=True)  # Remedial lecture requirement
    equipment_requirements = models.JSONField(default=list)  # Required equipment for subject

    def __str__(self):
        return f"{self.code} - {self.name}"


class TimeSlot(models.Model):
    DAYS_OF_WEEK = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
    ]
    
    SLOT_TYPES = [
        ('lecture', 'Lecture (1 hour)'),
        ('lab', 'Lab (2 hours)'),
        ('break', 'Break'),
        ('project', 'Project Time'),
    ]
    
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_type = models.CharField(max_length=10, choices=SLOT_TYPES, default='lecture')
    slot_number = models.IntegerField(help_text="Slot position in day (1-9)")
    is_first_half = models.BooleanField(default=True, help_text="Before lunch break")
    
    class Meta:
        unique_together = ['day', 'slot_number']
        ordering = ['day', 'slot_number']
    
    def __str__(self):
        return f"{self.get_day_display()} Slot {self.slot_number} ({self.start_time}-{self.end_time})"


class Session(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE, null=True, blank=True)
    timeslot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    batch_number = models.IntegerField()   # 1, 2, or 3

    def __str__(self):
        return f"{self.subject.name} - {self.teacher.name} - {self.timeslot}"


# Enhanced models for real-world functionality
class SubjectProficiency(models.Model):
    """Teacher's proficiency rating for each subject"""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    knowledge_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Knowledge level (1-10)"
    )
    willingness_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text="Willingness to teach (1-10)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['teacher', 'subject']
        ordering = ['-knowledge_rating', '-willingness_rating']
    
    def __str__(self):
        return f"{self.teacher.name} - {self.subject.code} (K:{self.knowledge_rating}, W:{self.willingness_rating})"
    
    @property
    def combined_score(self):
        """Weighted score: 60% knowledge + 40% willingness"""
        return (self.knowledge_rating * 0.6) + (self.willingness_rating * 0.4)


    """Dedicated project time for students"""
    PROJECT_TYPES = [
        ('mini', 'Mini Project'),
        ('major', 'Major Project'),
        ('internship', 'Internship'),
        ('research', 'Research Work'),
    ]


class TimetableConfiguration(models.Model):
    """Configuration for timetable generation"""
    name = models.CharField(max_length=100, help_text='Configuration name (e.g., Semester 1 2024)')
    academic_year = models.CharField(max_length=20, help_text='Academic year (e.g., 2024-25)')
    semester = models.CharField(max_length=20, help_text='Semester (e.g., Odd/Even)')
    
    # Configurable time settings
    college_start_time = models.TimeField(default='09:00:00', help_text='College start time')
    college_end_time = models.TimeField(default='17:45:00', help_text='College end time')
    lunch_start_time = models.TimeField(default='13:00:00', help_text='Lunch break start')
    lunch_end_time = models.TimeField(default='13:45:00', help_text='Lunch break end')
    
    # Project/free time configuration
    project_half_days_per_week = models.IntegerField(default=1, help_text='Number of half-days for project work')
    project_day_preference = models.CharField(max_length=20, choices=[
        ('friday_afternoon', 'Friday Afternoon'),
        ('thursday_afternoon', 'Thursday Afternoon'),
        ('wednesday_afternoon', 'Wednesday Afternoon'),
        ('flexible', 'Flexible - Algorithm decides')
    ], default='friday_afternoon')
    
    # Load balancing settings
    max_sessions_per_teacher = models.IntegerField(default=14, help_text='Maximum sessions per teacher per week')
    min_sessions_per_teacher = models.IntegerField(default=8, help_text='Minimum sessions per teacher per week')
    
    is_active = models.BooleanField(default=False, help_text='Active configuration')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.is_active:
            # Ensure only one active configuration
            TimetableConfiguration.objects.filter(is_active=True).update(is_active=False)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Inactive'})"


class TeacherReplacement(models.Model):
    """Handle teacher resignations and replacements with automatic reassignment"""
    original_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='replacements_from')
    replacement_teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='replacements_to', null=True, blank=True)
    reason = models.CharField(max_length=200, help_text="Reason for replacement")
    effective_date = models.DateField()
    subjects_transferred = models.ManyToManyField(Subject, blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def auto_assign_replacement(self):
        """Automatically assign best replacement teacher based on proficiency"""
        if self.replacement_teacher:
            return self.replacement_teacher
        
        # Get subjects that need replacement
        subjects_to_replace = self.subjects_transferred.all()
        
        # Find best replacement teacher based on proficiency scores
        best_teacher = None
        best_score = 0
        
        available_teachers = Teacher.objects.filter(status='active').exclude(id=self.original_teacher.id)
        
        for teacher in available_teachers:
            total_score = 0
            subject_count = 0
            
            for subject in subjects_to_replace:
                proficiency = SubjectProficiency.objects.filter(
                    teacher=teacher, subject=subject
                ).first()
                
                if proficiency:
                    total_score += proficiency.combined_score
                    subject_count += 1
            
            if subject_count > 0:
                avg_score = total_score / subject_count
                if avg_score > best_score:
                    best_score = avg_score
                    best_teacher = teacher
        
        if best_teacher:
            self.replacement_teacher = best_teacher
            self.save()
        
        return best_teacher
    
    def __str__(self):
        replacement_name = self.replacement_teacher.name if self.replacement_teacher else "TBD"
        return f"{self.original_teacher.name} → {replacement_name} ({self.effective_date})"


# For timetable versioning
class TimetableVersion(models.Model):
    version_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    algorithm_used = models.CharField(max_length=50, default='enhanced_genetic')
    fitness_score = models.FloatField(null=True, blank=True)
    generation_time = models.FloatField(null=True, blank=True, help_text="Time taken to generate in seconds")
    
    def __str__(self):
        return f"{self.version_name} ({'Active' if self.is_active else 'Inactive'})"


# Project Time Allocation for real-world functionality
class ProjectTimeAllocation(models.Model):
    """Manages dedicated project time slots for students"""
    
    PROJECT_TYPE_CHOICES = [
        ('mini', 'Mini Project'),
        ('major', 'Major Project'),
        ('both', 'Both Mini and Major'),
    ]
    
    DAY_CHOICES = [
        ('monday', 'Monday'),
        ('tuesday', 'Tuesday'),
        ('wednesday', 'Wednesday'),
        ('thursday', 'Thursday'),
        ('friday', 'Friday'),
    ]
    
    TIME_PREFERENCE_CHOICES = [
        ('morning', 'Morning (First Half)'),
        ('afternoon', 'Afternoon (Second Half)'),
        ('full_day', 'Full Day'),
    ]
    
    year = models.ForeignKey(Year, on_delete=models.CASCADE)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    project_type = models.CharField(max_length=10, choices=PROJECT_TYPE_CHOICES, default='mini')
    preferred_day = models.CharField(max_length=10, choices=DAY_CHOICES, default='friday')
    time_preference = models.CharField(max_length=15, choices=TIME_PREFERENCE_CHOICES, default='afternoon')
    hours_per_week = models.IntegerField(default=4, help_text="Hours allocated per week for projects")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['year', 'division', 'project_type']
    
    def __str__(self):
        return f"{self.year.name} {self.division.name} - {self.get_project_type_display()} ({self.preferred_day})"
