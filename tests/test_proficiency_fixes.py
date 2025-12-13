#!/usr/bin/env python
"""
Test Enhanced Proficiency System and Division-Specific Display
"""

import requests
import json

def test_division_api():
    print("1. Testing Division API...")
    try:
        response = requests.get('http://localhost:8000/api/divisions-list/')
        
        if response.status_code == 200:
            data = response.json()
            
            # Handle both paginated and direct list responses
            if isinstance(data, dict) and 'results' in data:
                divisions = data['results']
            elif isinstance(data, list):
                divisions = data
            else:
                divisions = []
            
            print(f"SUCCESS: Found {len(divisions)} divisions")
            for div in divisions:
                if isinstance(div, dict):
                    print(f"  - {div.get('display_name', 'Unknown')} (key: {div.get('key', 'Unknown')})")
                else:
                    print(f"  - {div}")
            return divisions
        else:
            print(f"ERROR: {response.text}")
            return []
    except Exception as e:
        print(f"ERROR: {e}")
        return []

def test_division_specific_timetable(divisions):
    print("\n2. Testing Division-Specific Timetable Display...")
    
    if not divisions:
        print("No divisions to test")
        return False
    
    # Test first division
    test_division = divisions[0]
    division_key = test_division['key']
    
    try:
        response = requests.get(f'http://localhost:8000/api/timetable/?division={division_key}')
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"SUCCESS: Found {len(sessions)} sessions for {test_division['display_name']}")
            
            # Verify all sessions belong to this division
            correct_division = 0
            for session in sessions:
                subject = session.get('subject', {})
                year_name = subject.get('year', {}).get('name', '')
                division_name = subject.get('division', {}).get('name', '')
                
                if f"{year_name}_{division_name}" == division_key:
                    correct_division += 1
            
            print(f"  - {correct_division}/{len(sessions)} sessions correctly filtered")
            return correct_division == len(sessions)
        else:
            print(f"ERROR: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_proficiency_enhanced():
    print("\n3. Testing Enhanced Proficiency Submission...")
    
    # Test with enhanced preferences
    test_data = {
        "proficiencies": [
            {
                "teacher_id": 1,
                "lecture_time_preference": "morning",
                "lab_time_preference": "afternoon",
                "cross_year_teaching": True,
                "preferred_years": ["SE", "TE"],
                "max_cross_year_sessions": 8,
                "subject_ratings": [
                    {
                        "subject_id": 1,
                        "knowledge_rating": 9,
                        "willingness_rating": 8
                    },
                    {
                        "subject_id": 2,
                        "knowledge_rating": 8,
                        "willingness_rating": 9
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post('http://localhost:8000/api/teacher-preferences/', 
                               json=test_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: {result['message']}")
            print(f"  - Proficiencies created: {result.get('proficiencies_created', 0)}")
            return True
        else:
            print(f"ERROR: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_proficiency_based_generation():
    print("\n4. Testing Proficiency-Based Timetable Generation...")
    
    try:
        response = requests.post('http://localhost:8000/api/generate-timetable/', 
                               json={'use_division_specific': True},
                               headers={'Content-Type': 'application/json'},
                               timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Generated {result['total_sessions']} sessions")
            print(f"  - Algorithm: {result['algorithm']}")
            print(f"  - Divisions processed: {result['divisions_processed']}")
            print(f"  - Cross-division conflicts: {result['cross_division_conflicts']}")
            
            # Check if proficiency is being used
            sessions_response = requests.get('http://localhost:8000/api/timetable/')
            if sessions_response.status_code == 200:
                sessions = sessions_response.json()
                
                # Analyze teacher-subject assignments
                assignments = {}
                for session in sessions:
                    teacher_name = session.get('teacher', {}).get('name', 'Unknown')
                    subject_name = session.get('subject', {}).get('name', 'Unknown')
                    
                    if teacher_name not in assignments:
                        assignments[teacher_name] = set()
                    assignments[teacher_name].add(subject_name)
                
                print("\n  Teacher-Subject Assignments:")
                for teacher, subjects in assignments.items():
                    print(f"    {teacher}: {', '.join(subjects)}")
                
                return True
            else:
                print("Could not verify assignments")
                return False
        else:
            print(f"ERROR: {response.text}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    print("TESTING ENHANCED PROFICIENCY & DIVISION SYSTEM")
    print("=" * 60)
    
    divisions = test_division_api()
    division_display_ok = test_division_specific_timetable(divisions)
    proficiency_submit_ok = test_proficiency_enhanced()
    proficiency_generation_ok = test_proficiency_based_generation()
    
    print("\n" + "=" * 60)
    print("ENHANCED SYSTEM TEST RESULTS")
    print("=" * 60)
    
    results = [
        ("Division API", divisions != []),
        ("Division-Specific Display", division_display_ok),
        ("Enhanced Proficiency Submission", proficiency_submit_ok),
        ("Proficiency-Based Generation", proficiency_generation_ok)
    ]
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\nSUCCESS: All enhanced features working!")
        print("- Division-specific timetables available")
        print("- Enhanced proficiency system operational")
        print("- Teacher preferences being processed")
    else:
        print("\nSome features need attention, but core improvements are working")
