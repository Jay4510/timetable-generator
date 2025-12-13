from django.db import models
from .models import Teacher, Subject

class TeacherSubjectPreference(models.Model):
    """
    Model to handle teacher-subject preferences and constraints.
    This addresses the real-world scenario where teachers have preferences
    and constraints about which subjects they teach.
    """
    PREFERENCE_CHOICES = [
        ('preferred', 'Preferred - Teacher wants to teach this subject'),
        ('willing', 'Willing - Teacher can teach this subject'),
        ('reluctant', 'Reluctant - Teacher prefers not to teach but can if needed'),
        ('refused', 'Refused - Teacher refuses to teach this subject'),
        ('unavailable', 'Unavailable - Teacher cannot teach this subject'),
    ]
    
    COMPETENCY_CHOICES = [
        ('expert', 'Expert - Highly qualified and experienced'),
        ('proficient', 'Proficient - Qualified and capable'),
        ('basic', 'Basic - Can teach but limited experience'),
        ('learning', 'Learning - New to this subject'),
        ('unqualified', 'Unqualified - Cannot teach this subject'),
    ]
    
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    preference = models.CharField(max_length=20, choices=PREFERENCE_CHOICES, default='willing')
    competency = models.CharField(max_length=20, choices=COMPETENCY_CHOICES, default='proficient')
    
    # Historical data
    years_taught = models.IntegerField(default=0, help_text="How many years has this teacher taught this subject")
    last_taught_semester = models.CharField(max_length=20, blank=True, help_text="When did they last teach this subject")
    
    # Constraints
    max_sessions_for_subject = models.IntegerField(null=True, blank=True, help_text="Maximum sessions per week for this subject")
    notes = models.TextField(blank=True, help_text="Additional notes about this assignment")
    
    # Priority scoring (calculated field)
    priority_score = models.FloatField(default=0.0, help_text="Calculated priority for assignment")
    
    class Meta:
        unique_together = ['teacher', 'subject']
        ordering = ['-priority_score', 'teacher__name']
    
    def calculate_priority_score(self):
        """
        Calculate priority score based on preference, competency, and experience.
        Higher score = better match for assignment.
        """
        preference_scores = {
            'preferred': 100,
            'willing': 70,
            'reluctant': 30,
            'refused': -100,
            'unavailable': -1000,
        }
        
        competency_scores = {
            'expert': 50,
            'proficient': 30,
            'basic': 10,
            'learning': 5,
            'unqualified': -100,
        }
        
        # Base score from preference and competency
        score = preference_scores.get(self.preference, 0) + competency_scores.get(self.competency, 0)
        
        # Bonus for experience
        experience_bonus = min(self.years_taught * 5, 25)  # Max 25 points for experience
        
        # Penalty for being overloaded (if they already teach many subjects)
        current_subjects = TeacherSubjectPreference.objects.filter(
            teacher=self.teacher, 
            preference__in=['preferred', 'willing']
        ).count()
        overload_penalty = max(0, (current_subjects - 3) * 10)  # Penalty after 3 subjects
        
        self.priority_score = score + experience_bonus - overload_penalty
        return self.priority_score
    
    def save(self, *args, **kwargs):
        self.priority_score = self.calculate_priority_score()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.teacher.name} -> {self.subject.name} ({self.preference}, {self.competency})"


class SubjectAllocationHistory(models.Model):
    """
    Track historical subject allocations to help with future decisions.
    This helps implement the "meeting-based allocation" process you described.
    """
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    semester = models.CharField(max_length=20)
    year = models.IntegerField()
    
    # Allocation details
    allocation_reason = models.CharField(max_length=200, help_text="Why was this teacher assigned this subject")
    teacher_satisfaction = models.IntegerField(default=5, help_text="Teacher satisfaction (1-10)")
    student_feedback = models.FloatField(null=True, blank=True, help_text="Average student rating")
    
    # Meeting notes
    meeting_notes = models.TextField(blank=True, help_text="Notes from the allocation meeting")
    was_voluntary = models.BooleanField(default=True, help_text="Did teacher volunteer or was assigned")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-year', '-semester']
    
    def __str__(self):
        return f"{self.subject.name} -> {self.teacher.name} ({self.semester} {self.year})"


def get_subject_allocation_recommendations(subject):
    """
    Get recommended teachers for a subject based on preferences, competency, and history.
    This simulates the "meeting discussion" process.
    """
    # Get all teacher preferences for this subject
    preferences = TeacherSubjectPreference.objects.filter(
        subject=subject
    ).exclude(
        preference__in=['refused', 'unavailable']
    ).order_by('-priority_score')
    
    recommendations = []
    
    for pref in preferences:
        # Get historical data
        history = SubjectAllocationHistory.objects.filter(
            subject=subject,
            teacher=pref.teacher
        ).order_by('-year', '-semester').first()
        
        recommendation = {
            'teacher': pref.teacher,
            'preference': pref.preference,
            'competency': pref.competency,
            'priority_score': pref.priority_score,
            'years_taught': pref.years_taught,
            'last_taught': pref.last_taught_semester,
            'historical_satisfaction': history.teacher_satisfaction if history else None,
            'historical_feedback': history.student_feedback if history else None,
            'notes': pref.notes,
        }
        recommendations.append(recommendation)
    
    return recommendations


def simulate_allocation_meeting(subjects):
    """
    Simulate the allocation meeting process you described.
    Returns a dictionary of subject -> recommended teacher assignments.
    """
    allocations = {}
    teacher_workload = {}
    
    # Initialize teacher workload tracking
    for teacher in Teacher.objects.all():
        teacher_workload[teacher.id] = 0
    
    # Sort subjects by difficulty of allocation (fewer willing teachers = higher priority)
    subject_difficulty = []
    for subject in subjects:
        willing_teachers = TeacherSubjectPreference.objects.filter(
            subject=subject,
            preference__in=['preferred', 'willing']
        ).count()
        subject_difficulty.append((subject, willing_teachers))
    
    # Sort by difficulty (fewer willing teachers first)
    subject_difficulty.sort(key=lambda x: x[1])
    
    for subject, willing_count in subject_difficulty:
        recommendations = get_subject_allocation_recommendations(subject)
        
        if not recommendations:
            # No one wants to teach this - assign to least loaded teacher
            # This simulates the "Geeta Madam DSA" scenario
            least_loaded_teacher = min(teacher_workload.items(), key=lambda x: x[1])
            teacher = Teacher.objects.get(id=least_loaded_teacher[0])
            allocations[subject] = {
                'teacher': teacher,
                'reason': 'Assigned due to no volunteers (like DSA to Geeta Madam)',
                'voluntary': False
            }
            teacher_workload[teacher.id] += subject.sessions_per_week
        else:
            # Find best available teacher considering workload
            best_teacher = None
            for rec in recommendations:
                teacher_id = rec['teacher'].id
                if teacher_workload[teacher_id] + subject.sessions_per_week <= rec['teacher'].max_sessions_per_week:
                    best_teacher = rec
                    break
            
            if best_teacher:
                allocations[subject] = {
                    'teacher': best_teacher['teacher'],
                    'reason': f"Best match: {best_teacher['preference']} preference, {best_teacher['competency']} competency",
                    'voluntary': best_teacher['preference'] in ['preferred', 'willing']
                }
                teacher_workload[best_teacher['teacher'].id] += subject.sessions_per_week
            else:
                # All preferred teachers are overloaded - assign to least loaded willing teacher
                willing_teachers = [rec for rec in recommendations if rec['preference'] in ['willing', 'reluctant']]
                if willing_teachers:
                    least_loaded = min(willing_teachers, key=lambda x: teacher_workload[x['teacher'].id])
                    allocations[subject] = {
                        'teacher': least_loaded['teacher'],
                        'reason': 'Assigned to least loaded willing teacher',
                        'voluntary': least_loaded['preference'] == 'willing'
                    }
                    teacher_workload[least_loaded['teacher'].id] += subject.sessions_per_week
    
    return allocations
