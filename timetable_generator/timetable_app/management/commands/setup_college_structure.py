from django.core.management.base import BaseCommand
from datetime import time
from timetable_app.enhanced_models import (
    TimeSlot, Teacher, Subject, Room, Lab, Year, Division, 
    SubjectProficiency, ProjectTimeAllocation
)

class Command(BaseCommand):
    help = 'Set up college timetable structure based on real requirements'

    def handle(self, *args, **options):
        self.stdout.write('Setting up college timetable structure...')
        
        # Create time slots based on your college schedule
        self.create_time_slots()
        
        # Update teacher preferences
        self.setup_teacher_preferences()
        
        # Create subject proficiency ratings
        self.setup_subject_proficiencies()
        
        # Set up project time allocations
        self.setup_project_allocations()
        
        self.stdout.write(self.style.SUCCESS('College structure setup completed!'))
    
    def create_time_slots(self):
        """Create time slots matching your college schedule"""
        self.stdout.write('Creating time slots...')
        
        # Clear existing slots
        TimeSlot.objects.all().delete()
        
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        
        # Time slots based on your PDF structure
        time_slots = [
            (1, time(9, 0), time(10, 0), 'lecture', True),   # 9:00-10:00
            (2, time(10, 0), time(11, 0), 'lecture', True),  # 10:00-11:00
            (3, time(11, 0), time(12, 0), 'lecture', True),  # 11:00-12:00
            (4, time(12, 0), time(13, 0), 'lecture', True),  # 12:00-13:00
            (5, time(13, 0), time(13, 45), 'break', False),  # 13:00-13:45 LUNCH BREAK
            (6, time(13, 45), time(14, 45), 'lecture', False), # 13:45-14:45
            (7, time(14, 45), time(15, 45), 'lecture', False), # 14:45-15:45
            (8, time(15, 45), time(16, 45), 'lecture', False), # 15:45-16:45
            (9, time(16, 45), time(17, 45), 'lecture', False), # 16:45-17:45
        ]
        
        for day in days:
            for slot_num, start, end, slot_type, is_first_half in time_slots:
                TimeSlot.objects.create(
                    day=day,
                    start_time=start,
                    end_time=end,
                    slot_type=slot_type,
                    slot_number=slot_num,
                    is_first_half=is_first_half,
                    is_break=(slot_type == 'break')
                )
        
        self.stdout.write(f'Created {TimeSlot.objects.count()} time slots')
    
    def setup_teacher_preferences(self):
        """Set up teacher time preferences"""
        self.stdout.write('Setting up teacher preferences...')
        
        try:
            # Example preferences - you can modify based on actual teacher preferences
            preferences = {
                'first_half': ['KPR sir', 'VSK sir', 'SUK sir'],
                'second_half': ['JRG sir', 'ARR sir', 'DDG sir'],
                'mixed': ['Khaire sir', 'Gabhane sir'],
            }
            
            for pref_type, teacher_names in preferences.items():
                for name in teacher_names:
                    try:
                        teacher = Teacher.objects.get(name__icontains=name.split()[0])
                        teacher.time_preference = pref_type
                        teacher.save()
                        self.stdout.write(f'Set {teacher.name} preference to {pref_type}')
                    except Teacher.DoesNotExist:
                        self.stdout.write(f'Teacher {name} not found')
                    except Teacher.MultipleObjectsReturned:
                        teachers = Teacher.objects.filter(name__icontains=name.split()[0])
                        for teacher in teachers:
                            teacher.time_preference = pref_type
                            teacher.save()
        except Exception as e:
            self.stdout.write(f'Error setting preferences: {e}')
    
    def setup_subject_proficiencies(self):
        """Create sample subject proficiency ratings"""
        self.stdout.write('Setting up subject proficiencies...')
        
        try:
            # Clear existing proficiencies
            SubjectProficiency.objects.all().delete()
            
            teachers = Teacher.objects.filter(status='active')
            subjects = Subject.objects.all()
            
            # Create sample proficiency ratings
            import random
            
            for teacher in teachers:
                # Each teacher gets proficiency for 3-5 subjects
                teacher_subjects = random.sample(list(subjects), min(5, len(subjects)))
                
                for subject in teacher_subjects:
                    # Generate realistic ratings
                    knowledge = random.randint(6, 10)  # Teachers generally know their subjects well
                    willingness = random.randint(5, 9)  # Varying willingness
                    
                    # Some subjects get lower ratings to simulate real preferences
                    if random.random() < 0.2:  # 20% chance of lower rating
                        knowledge = random.randint(4, 7)
                        willingness = random.randint(3, 6)
                    
                    SubjectProficiency.objects.create(
                        teacher=teacher,
                        subject=subject,
                        knowledge_rating=knowledge,
                        willingness_rating=willingness,
                        has_taught_before=random.choice([True, False])
                    )
            
            self.stdout.write(f'Created {SubjectProficiency.objects.count()} proficiency ratings')
            
        except Exception as e:
            self.stdout.write(f'Error creating proficiencies: {e}')
    
    def setup_project_allocations(self):
        """Set up project time allocations"""
        self.stdout.write('Setting up project allocations...')
        
        try:
            # Clear existing allocations
            ProjectTimeAllocation.objects.all().delete()
            
            divisions = Division.objects.all()
            
            # Based on your PDF, some divisions have dedicated project time
            project_schedule = [
                ('tuesday', 'first_half'),   # Tuesday morning project
                ('friday', 'second_half'),   # Friday afternoon project
            ]
            
            for division in divisions:
                # Assign project time based on year
                if division.year.name in ['TE', 'BE']:  # Final years get more project time
                    for day, half in project_schedule:
                        try:
                            # Assign a project guide (random for now)
                            guide = Teacher.objects.filter(can_teach_projects=True).first()
                            
                            ProjectTimeAllocation.objects.create(
                                division=division,
                                day=day,
                                half=half,
                                project_guide=guide
                            )
                        except Exception as e:
                            self.stdout.write(f'Error creating project allocation: {e}')
            
            self.stdout.write(f'Created {ProjectTimeAllocation.objects.count()} project allocations')
            
        except Exception as e:
            self.stdout.write(f'Error setting up project allocations: {e}')
