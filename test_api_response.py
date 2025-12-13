#!/usr/bin/env python
"""
Test the actual API response structure to verify it matches frontend expectations
"""
import os
import django
import sys
import json

sys.path.insert(0, '/Users/adityaa/Downloads/Django_using_book/timetable_generator')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timetable_project.settings')
django.setup()

from timetable_app.models import Teacher, Subject, Year
from timetable_app.views import UserDrivenGenerationView
from rest_framework.test import APIRequestFactory
from django.http import JsonResponse

print("=" * 100)
print("🧪 TESTING API RESPONSE STRUCTURE")
print("=" * 100)

# Create test data
teachers = list(Teacher.objects.all()[:10])
be_year = Year.objects.get(name='BE')
subjects = list(Subject.objects.filter(year=be_year)[:7])

teacher_data = [{'id': f'T{i+1}', 'name': t.name, 'assignedYears': ['BE']} for i, t in enumerate(teachers)]
subject_data = [{'id': f'S{i+1}', 'code': s.code, 'name': s.name, 'year': 'BE', 'sessionsPerWeek': s.sessions_per_week} for i, s in enumerate(subjects)]

config_data = {
    'yearsManaged': ['BE'],
    'professor_year_assignments': {'BE': [t['id'] for t in teacher_data]},
    'teachers': teacher_data,
    'subjects': subject_data,
    'college_start_time': '09:00',
    'college_end_time': '17:45',
    'recess_start': '13:00',
    'recess_end': '13:45',
}

print("\n📤 Simulating API request...")

# Create mock request with DRF
from rest_framework.request import Request

factory = APIRequestFactory()
django_request = factory.post('/api/user-driven/generate/', {
    'config_data': config_data,
    'target_years': ['BE'],
    'use_user_driven': True
}, format='json')

# Wrap in DRF Request
request = Request(django_request)

# Call the view
view = UserDrivenGenerationView()
response = view.post(request)

print(f"\n📊 Response Status: {response.status_code}")

if response.status_code == 200:
    data = response.data
    
    print("\n✅ Response Structure:")
    print(f"  status: {data.get('status')}")
    print(f"  algorithm: {data.get('algorithm')}")
    print(f"  years_processed: {data.get('years_processed')}")
    print(f"  success_rate: {data.get('success_rate')}")
    print(f"  total_divisions: {data.get('total_divisions')}")
    print(f"  successful_divisions: {data.get('successful_divisions')}")
    print(f"  total_conflicts: {data.get('total_conflicts')}")
    print(f"  conflict_free: {data.get('conflict_free')}")
    
    print("\n📋 Results Structure:")
    results = data.get('results', {})
    for year, year_data in results.items():
        print(f"  {year}:")
        for division, div_data in year_data.items():
            print(f"    {division}:")
            print(f"      success: {div_data.get('success')}")
            print(f"      fitness_score: {div_data.get('fitness_score')}")
            print(f"      sessions_count: {div_data.get('sessions_count')}")
            
            if div_data.get('timetable'):
                tt = div_data['timetable']
                print(f"      timetable.genes: {len(tt.get('genes', []))} genes")
                if tt.get('genes'):
                    print(f"      Sample gene: {tt['genes'][0]}")
    
    print("\n🎯 Frontend Expectations Check:")
    
    # Check what GenerationProcess expects
    checks = {
        'data.algorithm': data.get('algorithm'),
        'data.years_processed': data.get('years_processed'),
        'data.total_divisions': data.get('total_divisions'),
        'data.successful_divisions': data.get('successful_divisions'),
        'data.success_rate': data.get('success_rate'),
        'data.total_conflicts': data.get('total_conflicts'),
        'data.conflict_free': data.get('conflict_free'),
        'data.results': 'Present' if data.get('results') else 'Missing',
        'data.conflicts_report': 'Present' if data.get('conflicts_report') else 'Missing',
    }
    
    all_good = True
    for key, value in checks.items():
        status = "✅" if value else "❌"
        print(f"  {status} {key}: {value}")
        if not value:
            all_good = False
    
    # Check ResultsDownload expectations
    print("\n🎯 ResultsDownload Expectations Check:")
    
    if data.get('results'):
        be_data = data['results'].get('BE', {})
        if be_data:
            div_a = be_data.get('A', {})
            checks2 = {
                'results.BE.A.timetable': 'Present' if div_a.get('timetable') else 'Missing',
                'results.BE.A.timetable.genes': len(div_a.get('timetable', {}).get('genes', [])) if div_a.get('timetable') else 0,
                'results.BE.A.success': div_a.get('success'),
                'results.BE.A.fitness_score': div_a.get('fitness_score'),
            }
            
            for key, value in checks2.items():
                status = "✅" if value else "❌"
                print(f"  {status} {key}: {value}")
                if not value:
                    all_good = False
    
    if all_good:
        print("\n" + "=" * 100)
        print("🎉 ALL CHECKS PASSED! API response matches frontend expectations!")
        print("=" * 100)
    else:
        print("\n" + "=" * 100)
        print("❌ SOME CHECKS FAILED! There are mismatches!")
        print("=" * 100)
        
    # Save response for inspection
    with open('/tmp/api_response.json', 'w') as f:
        # Convert to JSON-serializable format
        json_data = json.loads(json.dumps(data, default=str))
        json.dump(json_data, f, indent=2)
    print("\n📄 Full response saved to: /tmp/api_response.json")
    
else:
    print(f"\n❌ API call failed with status {response.status_code}")
    print(f"Response: {response.data}")
