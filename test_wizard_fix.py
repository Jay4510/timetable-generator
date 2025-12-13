#!/usr/bin/env python
"""
Test script to verify wizard data preparation works
"""
import os
import django
import sys

# Setup Django
sys.path.insert(0, '/Users/adityaa/Downloads/Django_using_book/timetable_generator')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timetable_project.settings')
django.setup()

from timetable_app.models import Teacher, Subject, Year, Division

print("=" * 80)
print("🧪 TESTING WIZARD DATA PREPARATION")
print("=" * 80)

# Simulate wizard data
test_config = {
    'teachers': [
        {
            'id': 'T1',
            'name': 'Dr. Test Smith',
            'designation': 'Professor',
            'experience': 10,
            'assignedYears': ['BE']
        },
        {
            'id': 'T2',
            'name': 'Dr. Test Jones',
            'designation': 'Assistant Professor',
            'experience': 5,
            'assignedYears': ['BE']
        }
    ],
    'subjects': [
        {
            'id': 'SUBJ1',
            'code': 'TEST-DS',
            'name': 'Test Data Structures',
            'year': 'BE',
            'sessionsPerWeek': 3,
            'requiresLab': False
        },
        {
            'id': 'SUBJ2',
            'code': 'TEST-DBMS',
            'name': 'Test Database Systems',
            'year': 'BE',
            'sessionsPerWeek': 4,
            'requiresLab': True
        }
    ],
    'professor_year_assignments': {
        'BE': ['T1', 'T2']
    }
}

print("\n📤 Input Data:")
print(f"  Teachers: {len(test_config['teachers'])}")
print(f"  Subjects: {len(test_config['subjects'])}")

# Import the view
from timetable_app.views import UserDrivenGenerationView

view = UserDrivenGenerationView()

print("\n🔧 Running _prepare_wizard_data_for_algorithm...")

try:
    result_config = view._prepare_wizard_data_for_algorithm(test_config, ['BE'])
    
    print("\n✅ SUCCESS!")
    print(f"\n📊 Results:")
    print(f"  professor_year_assignments: {result_config.get('professor_year_assignments')}")
    
    # Check database
    print(f"\n💾 Database Check:")
    teachers_count = Teacher.objects.filter(name__startswith='Dr. Test').count()
    subjects_count = Subject.objects.filter(code__startswith='TEST-').count()
    
    print(f"  Teachers in DB: {teachers_count}")
    print(f"  Subjects in DB: {subjects_count}")
    
    if teachers_count >= 2 and subjects_count >= 2:
        print("\n🎉 TEST PASSED! Wizard data was saved to database!")
    else:
        print("\n❌ TEST FAILED! Data not saved properly")
        
    # Cleanup
    print(f"\n🧹 Cleaning up test data...")
    Teacher.objects.filter(name__startswith='Dr. Test').delete()
    Subject.objects.filter(code__startswith='TEST-').delete()
    print("  Done!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
