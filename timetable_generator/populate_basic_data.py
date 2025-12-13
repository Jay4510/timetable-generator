#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timetable_project.settings')
django.setup()

from timetable_app.models import Teacher, Subject, Room, Lab, TimeSlot, Year, Division

def populate_data():
    print("Populating basic timetable data...")
    
    # Create Years
    years_data = ['SE', 'TE', 'BE']
    
    for year_name in years_data:
        year, created = Year.objects.get_or_create(name=year_name)
        if created:
            print(f"Created year: {year.name}")
    
    # Create Divisions
    divisions_data = [
        {'year_name': 'SE', 'name': 'A', 'num_batches': 3},
        {'year_name': 'SE', 'name': 'B', 'num_batches': 3},
        {'year_name': 'TE', 'name': 'A', 'num_batches': 3},
        {'year_name': 'TE', 'name': 'B', 'num_batches': 3},
        {'year_name': 'BE', 'name': 'A', 'num_batches': 3},
        {'year_name': 'BE', 'name': 'B', 'num_batches': 3},
    ]
    
    for div_data in divisions_data:
        year = Year.objects.get(name=div_data['year_name'])
        division, created = Division.objects.get_or_create(
            year=year,
            name=div_data['name'],
            defaults={'num_batches': div_data['num_batches']}
        )
        if created:
            print(f"Created division: {division}")
    
    # Create Teachers
    teachers_data = [
        {'name': 'Dr. Sharma', 'email': 'sharma@college.edu', 'department': 'Information Technology'},
        {'name': 'Prof. Patel', 'email': 'patel@college.edu', 'department': 'Information Technology'},
        {'name': 'Dr. Kumar', 'email': 'kumar@college.edu', 'department': 'Computer Science'},
        {'name': 'Prof. Singh', 'email': 'singh@college.edu', 'department': 'Information Technology'},
        {'name': 'Dr. Gupta', 'email': 'gupta@college.edu', 'department': 'Electronics'},
        {'name': 'Prof. Verma', 'email': 'verma@college.edu', 'department': 'Information Technology'},
        {'name': 'Dr. Joshi', 'email': 'joshi@college.edu', 'department': 'Computer Science'},
        {'name': 'Prof. Mehta', 'email': 'mehta@college.edu', 'department': 'Information Technology'},
        {'name': 'Dr. Agarwal', 'email': 'agarwal@college.edu', 'department': 'Information Technology'},
        {'name': 'Prof. Rao', 'email': 'rao@college.edu', 'department': 'Electronics'},
        {'name': 'Kirti mam', 'email': 'kirti@college.edu', 'department': 'Physics'},
        {'name': 'Priya mam', 'email': 'priya@college.edu', 'department': 'Mathematics'},
    ]
    
    for teacher_data in teachers_data:
        teacher, created = Teacher.objects.get_or_create(
            email=teacher_data['email'],
            defaults={
                'name': teacher_data['name'],
                'department': teacher_data['department'],
                'max_sessions_per_week': 14
            }
        )
        if created:
            print(f"Created teacher: {teacher.name}")
    
    # Create Subjects
    subjects_data = [
        {'name': 'Data Structures', 'code': 'DS', 'year_name': 'SE', 'division_name': 'A', 'sessions_per_week': 4, 'requires_lab': True},
        {'name': 'Database Management', 'code': 'DBMS', 'year_name': 'SE', 'division_name': 'A', 'sessions_per_week': 4, 'requires_lab': True},
        {'name': 'Computer Networks', 'code': 'CN', 'year_name': 'TE', 'division_name': 'A', 'sessions_per_week': 3, 'requires_lab': False},
        {'name': 'Operating Systems', 'code': 'OS', 'year_name': 'TE', 'division_name': 'A', 'sessions_per_week': 4, 'requires_lab': True},
        {'name': 'Software Engineering', 'code': 'SE-SUB', 'year_name': 'TE', 'division_name': 'B', 'sessions_per_week': 3, 'requires_lab': False},
        {'name': 'Web Technology', 'code': 'WT', 'year_name': 'BE', 'division_name': 'A', 'sessions_per_week': 4, 'requires_lab': True},
        {'name': 'Machine Learning', 'code': 'ML', 'year_name': 'BE', 'division_name': 'A', 'sessions_per_week': 3, 'requires_lab': True},
        {'name': 'Artificial Intelligence', 'code': 'AI', 'year_name': 'BE', 'division_name': 'B', 'sessions_per_week': 3, 'requires_lab': False},
        {'name': 'Physics', 'code': 'PHY', 'year_name': 'SE', 'division_name': 'B', 'sessions_per_week': 3, 'requires_lab': True},
        {'name': 'Mathematics', 'code': 'MATH', 'year_name': 'SE', 'division_name': 'B', 'sessions_per_week': 4, 'requires_lab': False},
        {'name': 'Digital Electronics', 'code': 'DE', 'year_name': 'TE', 'division_name': 'B', 'sessions_per_week': 3, 'requires_lab': True},
        {'name': 'Microprocessors', 'code': 'MP', 'year_name': 'BE', 'division_name': 'B', 'sessions_per_week': 4, 'requires_lab': True},
    ]
    
    for subject_data in subjects_data:
        year = Year.objects.get(name=subject_data['year_name'])
        division = Division.objects.get(year=year, name=subject_data['division_name'])
        
        subject, created = Subject.objects.get_or_create(
            code=subject_data['code'],
            defaults={
                'name': subject_data['name'],
                'year': year,
                'division': division,
                'sessions_per_week': subject_data['sessions_per_week'],
                'requires_lab': subject_data['requires_lab']
            }
        )
        if created:
            print(f"Created subject: {subject.name}")
    
    # Create Rooms
    rooms_data = [
        {'name': '101', 'capacity': 60, 'room_type': 'classroom'},
        {'name': '102', 'capacity': 60, 'room_type': 'classroom'},
        {'name': '103', 'capacity': 60, 'room_type': 'classroom'},
        {'name': '201', 'capacity': 60, 'room_type': 'classroom'},
        {'name': '202', 'capacity': 60, 'room_type': 'classroom'},
        {'name': '203', 'capacity': 60, 'room_type': 'classroom'},
        {'name': '301', 'capacity': 60, 'room_type': 'classroom'},
        {'name': '302', 'capacity': 60, 'room_type': 'classroom'},
        {'name': '701', 'capacity': 30, 'room_type': 'classroom'},
        {'name': '702', 'capacity': 30, 'room_type': 'classroom'},
    ]
    
    for room_data in rooms_data:
        room, created = Room.objects.get_or_create(
            name=room_data['name'],
            defaults={
                'capacity': room_data['capacity'],
                'room_type': room_data['room_type']
            }
        )
        if created:
            print(f"Created room: {room.name}")
    
    # Create Labs
    labs_data = [
        {'name': 'Computer Lab 1', 'capacity': 30, 'lab_type': 'computer'},
        {'name': 'Computer Lab 2', 'capacity': 30, 'lab_type': 'computer'},
        {'name': 'Network Lab', 'capacity': 25, 'lab_type': 'network'},
        {'name': 'Physics Lab', 'capacity': 20, 'lab_type': 'physics'},
        {'name': 'Electronics Lab', 'capacity': 25, 'lab_type': 'electronics'},
    ]
    
    for lab_data in labs_data:
        lab, created = Lab.objects.get_or_create(
            name=lab_data['name'],
            defaults={
                'capacity': lab_data['capacity'],
                'lab_type': lab_data['lab_type']
            }
        )
        if created:
            print(f"Created lab: {lab.name}")
    
    print(f"\nData population completed!")
    print(f"Teachers: {Teacher.objects.count()}")
    print(f"Subjects: {Subject.objects.count()}")
    print(f"Rooms: {Room.objects.count()}")
    print(f"Labs: {Lab.objects.count()}")
    print(f"TimeSlots: {TimeSlot.objects.count()}")
    print(f"Years: {Year.objects.count()}")
    print(f"Divisions: {Division.objects.count()}")

if __name__ == '__main__':
    populate_data()
