#!/usr/bin/env python
"""
Complete automated test using IT department template
This will test the entire flow without manual intervention
"""
import os
import django
import sys
import json

# Setup Django
sys.path.insert(0, '/Users/adityaa/Downloads/Django_using_book/timetable_generator')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timetable_project.settings')
django.setup()

from timetable_app.models import Teacher, Subject, Year, Division, Room, Lab
from timetable_app.views import UserDrivenGenerationView

print("=" * 100)
print("🧪 COMPLETE AUTOMATED TEST - USING IT DEPARTMENT TEMPLATE")
print("=" * 100)

# Step 1: Check what data exists
print("\n📊 STEP 1: Checking existing data...")
teachers_count = Teacher.objects.count()
subjects_count = Subject.objects.count()
rooms_count = Room.objects.count()
labs_count = Lab.objects.count()

print(f"  Teachers in DB: {teachers_count}")
print(f"  Subjects in DB: {subjects_count}")
print(f"  Rooms in DB: {rooms_count}")
print(f"  Labs in DB: {labs_count}")

if teachers_count < 5:
    print("  ⚠️  Not enough teachers! Need at least 5")
    sys.exit(1)

# Step 2: Prepare test configuration (simulating frontend)
print("\n📤 STEP 2: Preparing test configuration...")

# Get teachers from database
teachers = list(Teacher.objects.all()[:10])
teacher_data = []
for i, teacher in enumerate(teachers):
    teacher_data.append({
        'id': f'T{i+1}',
        'name': teacher.name,
        'designation': 'Professor',
        'experience': teacher.experience_years,
        'assignedYears': ['BE']  # Assign all to BE for testing
    })

print(f"  ✅ Prepared {len(teacher_data)} teachers")

# Get subjects from database (BE subjects)
be_year = Year.objects.get(name='BE')
subjects = list(Subject.objects.filter(year=be_year)[:7])
subject_data = []
for i, subject in enumerate(subjects):
    subject_data.append({
        'id': f'SUBJ{i+1}',
        'code': subject.code,
        'name': subject.name,
        'year': 'BE',
        'sessionsPerWeek': subject.sessions_per_week,
        'requiresLab': subject.requires_lab
    })

print(f"  ✅ Prepared {len(subject_data)} subjects")

# Create config_data matching frontend format
config_data = {
    'department': 'Information Technology',
    'academicYear': '2024-25',
    'yearsManaged': ['BE'],
    'college_start_time': '09:00',
    'college_end_time': '17:45',
    'recess_start': '13:00',
    'recess_end': '13:45',
    
    # Teacher assignments (year -> teacher IDs)
    'professor_year_assignments': {
        'BE': [t['id'] for t in teacher_data]
    },
    
    'proficiency_data': {},
    'room_assignments': {},
    'professor_preferences': {},
    'division_config': {},
    'batch_config': {},
    'project_config': {},
    'remedial_config': {},
    
    # Raw data
    'teachers': teacher_data,
    'subjects': subject_data,
    'rooms': {
        'classrooms': [],
        'labs': []
    }
}

print(f"\n📋 Configuration summary:")
print(f"  Years: {config_data['yearsManaged']}")
print(f"  Teachers: {len(config_data['teachers'])}")
print(f"  Subjects: {len(config_data['subjects'])}")
print(f"  Professor assignments: {config_data['professor_year_assignments']}")

# Step 3: Test the preparation method
print("\n🔧 STEP 3: Testing wizard data preparation...")

view = UserDrivenGenerationView()
try:
    prepared_config = view._prepare_wizard_data_for_algorithm(config_data, ['BE'])
    print("  ✅ Preparation successful!")
    print(f"  Mapped assignments: {prepared_config.get('professor_year_assignments')}")
except Exception as e:
    print(f"  ❌ Preparation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Check if teachers were saved
print("\n💾 STEP 4: Verifying database...")
new_teachers_count = Teacher.objects.count()
new_subjects_count = Subject.objects.count()

print(f"  Teachers now: {new_teachers_count} (was {teachers_count})")
print(f"  Subjects now: {new_subjects_count} (was {subjects_count})")

# Step 5: Test the algorithm
print("\n🚀 STEP 5: Running algorithm...")

from timetable_app.user_driven_timetable_algorithm_FIXED import UserDrivenTimetableAlgorithm

try:
    algorithm = UserDrivenTimetableAlgorithm(
        config_data=prepared_config,
        target_years=['BE']
    )
    
    print("  Algorithm initialized successfully")
    
    # Generate timetables
    result = algorithm.generate_all_timetables()
    
    print("\n📊 STEP 6: Analyzing results...")
    
    if isinstance(result, dict):
        # Check BE results
        be_results = result.get('BE', {})
        success_metrics = result.get('_success_metrics', {})
        
        print(f"\n  Success Metrics:")
        print(f"    Total Divisions: {success_metrics.get('total_divisions', 0)}")
        print(f"    Successful: {success_metrics.get('successful_divisions', 0)}")
        print(f"    Success Rate: {success_metrics.get('success_rate', 0)}%")
        print(f"    Avg Fitness: {success_metrics.get('average_fitness_score', 0)}")
        
        # Check each division
        for div_name, div_result in be_results.items():
            if isinstance(div_result, dict):
                success = div_result.get('success', False)
                fitness = div_result.get('fitness_score', 0)
                error = div_result.get('error', '')
                
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"\n  Division {div_name}: {status}")
                print(f"    Fitness: {fitness}")
                if error:
                    print(f"    Error: {error}")
        
        # Final verdict
        success_rate = success_metrics.get('success_rate', 0)
        if success_rate > 0:
            print("\n" + "=" * 100)
            print(f"🎉 TEST PASSED! Success Rate: {success_rate}%")
            print("=" * 100)
            sys.exit(0)
        else:
            print("\n" + "=" * 100)
            print("❌ TEST FAILED! Success Rate: 0%")
            print("=" * 100)
            print("\n🔍 Debugging info:")
            print(json.dumps(result, indent=2, default=str))
            sys.exit(1)
    else:
        print(f"  ❌ Unexpected result type: {type(result)}")
        print(f"  Result: {result}")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ Algorithm failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
