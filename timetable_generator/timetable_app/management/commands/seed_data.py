from django.core.management.base import BaseCommand
from timetable_app.models import Teacher, Year, Division, Room, Lab, Subject, TimeSlot
from django.utils import timezone
import datetime


class Command(BaseCommand):
    help = 'Seed the database with initial timetable data'

    def handle(self, *args, **options):
        self.stdout.write('Seeding data...')

        # Create teachers
        teachers_data = [
            "Kumane sir", "Gaydhane sir", "Khaire sir", "Rashmi Mam", "Roshni mam",
            "Urmila mam", "Shalini mam", "Ashwini mam", "Kirti mam", "Nisha Mam",
            "Geeta mam", "Vidya mam", "Deepali mam", "Neeta moharkar", "Sonali Patil",
            "Diksha mam", "Anita Mam", "Harshita mam"
        ]

        for teacher_name in teachers_data:
            teacher, created = Teacher.objects.get_or_create(
                name=teacher_name,
                defaults={
                    'max_sessions_per_week': 14,
                    'availability': {},
                    'preferences': {}
                }
            )
            if created:
                self.stdout.write(f'Created teacher: {teacher_name}')

        # Create years
        years_data = ['SE', 'TE', 'BE']
        years = {}
        for year_name in years_data:
            year, created = Year.objects.get_or_create(name=year_name)
            years[year_name] = year
            if created:
                self.stdout.write(f'Created year: {year_name}')

        # Create divisions
        divisions_data = {
            'SE': [('A', 3), ('B', 3), ('C', 3)],
            'TE': [('A', 3), ('B', 3)],
            'BE': [('A', 3), ('B', 3)]
        }

        divisions = {}
        for year_name, divs in divisions_data.items():
            year = years[year_name]
            for div_name, num_batches in divs:
                division, created = Division.objects.get_or_create(
                    year=year,
                    name=div_name,
                    defaults={'num_batches': num_batches}
                )
                divisions[f"{year_name}_{div_name}"] = division
                if created:
                    self.stdout.write(f'Created division: {year_name} {div_name}')
        
        # Debug: Print all division keys
        self.stdout.write(f'Division keys: {list(divisions.keys())}')

        # Create rooms (both classrooms and labs)
        rooms_data = [
            # Classrooms
            ('705', 60, 'class'),
            ('709', 60, 'class'),
            ('801', 60, 'class'),
            ('803', 60, 'class'),
            ('809', 60, 'class'),
            # Lab rooms (stored as Room objects with room_type='lab')
            ('701', 30, 'lab'),
            ('702', 30, 'lab'),
            ('703', 30, 'lab'),
            ('706', 30, 'lab'),
            ('707', 30, 'lab'),
            ('902', 30, 'lab'),
            ('807', 30, 'lab')
        ]

        for room_name, capacity, room_type in rooms_data:
            room, created = Room.objects.get_or_create(
                name=room_name,
                defaults={
                    'capacity': capacity,
                    'room_type': room_type
                }
            )
            if created:
                self.stdout.write(f'Created {room_type}: {room_name}')

        # Create labs (keeping the Lab model for backward compatibility)
        labs_data = [
            '701', '702', '703', '706', '707', '902', '807'
        ]

        for lab_name in labs_data:
            lab, created = Lab.objects.get_or_create(
                name=lab_name,
                defaults={'capacity': 30}
            )
            if created:
                self.stdout.write(f'Created lab entry: {lab_name}')

        # Create time slots (Monday to Friday, 9 AM to 5 PM, hourly slots)
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
        hours = range(9, 17)  # 9 AM to 5 PM

        for day in days:
            slot_number = 1
            for hour in hours:
                start_time = datetime.time(hour, 0)
                end_time = datetime.time(hour + 1, 0)
                # Determine if it's first half (before 1 PM) or second half
                is_first_half = hour < 13
                
                timeslot, created = TimeSlot.objects.get_or_create(
                    day=day,
                    slot_number=slot_number,
                    defaults={
                        'start_time': start_time,
                        'end_time': end_time,
                        'slot_type': 'lecture',
                        'is_first_half': is_first_half
                    }
                )
                if created:
                    self.stdout.write(f'Created timeslot: {day} slot {slot_number} {start_time}-{end_time}')
                slot_number += 1

        # Create sample subjects for each year and division
        subjects_data = {
            'SE': {
                'A': ['Mathematics', 'Physics', 'Chemistry', 'Programming', 'English'],
                'B': ['Mathematics', 'Physics', 'Chemistry', 'Programming', 'English'],
                'C': ['Mathematics', 'Physics', 'Chemistry', 'Programming', 'English']
            },
            'TE': {
                'A': ['Data Structures', 'Algorithms', 'Database', 'Operating System', 'Computer Networks'],
                'B': ['Data Structures', 'Algorithms', 'Database', 'Operating System', 'Computer Networks']
            },
            'BE': {
                'A': ['Machine Learning', 'Cloud Computing', 'Cybersecurity', 'Project Management', 'Software Testing'],
                'B': ['Machine Learning', 'Cloud Computing', 'Cybersecurity', 'Project Management', 'Software Testing']
            }
        }

        # Create subjects with sessions per week
        for year_name, year_divisions in subjects_data.items():
            year = years[year_name]
            for div_name, subject_names in year_divisions.items():
                division_key = f"{year_name}_{div_name}"
                if division_key in divisions:
                    division = divisions[division_key]
                    for i, subject_name in enumerate(subject_names):
                        # Make every second subject a lab subject
                        requires_lab = i % 2 == 1
                        sessions_per_week = 4 if not requires_lab else 2
                        # Generate a code for the subject
                        subject_code = f"{year_name}_{div_name}_{subject_name[:3].upper()}"
                        
                        subject, created = Subject.objects.get_or_create(
                            code=subject_code,
                            defaults={
                                'name': subject_name,
                                'year': year,
                                'division': division,
                                'sessions_per_week': sessions_per_week,
                                'requires_lab': requires_lab
                            }
                        )
                        if created:
                            self.stdout.write(f'Created subject: {subject_name} ({subject_code}) for {year_name} {div_name}')
                else:
                    self.stdout.write(f'Warning: Division {division_key} not found')

        self.stdout.write(
            self.style.SUCCESS('Successfully seeded all data')
        )