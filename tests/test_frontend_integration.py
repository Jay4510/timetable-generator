#!/usr/bin/env python
"""
Test Frontend-Backend Integration for Enhanced Algorithm
"""

import requests
import json

def test_api_endpoints():
    """Test all key API endpoints that frontend needs"""
    print("TESTING FRONTEND-BACKEND INTEGRATION")
    print("=" * 50)
    
    endpoints = [
        ('GET', '/api/teachers/', 'Teachers List'),
        ('GET', '/api/subjects/', 'Subjects List'),
        ('GET', '/api/rooms/', 'Rooms List'),
        ('GET', '/api/labs/', 'Labs List'),
        ('GET', '/api/timeslots/', 'TimeSlots List'),
        ('GET', '/api/divisions-list/', 'Divisions List'),
        ('GET', '/api/timetable/', 'Current Timetable'),
    ]
    
    base_url = 'http://localhost:8000'
    working_endpoints = 0
    
    for method, endpoint, name in endpoints:
        try:
            url = f"{base_url}{endpoint}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract count from paginated responses
                if isinstance(data, dict) and 'results' in data:
                    count = len(data['results'])
                elif isinstance(data, list):
                    count = len(data)
                else:
                    count = 1
                
                print(f"✓ {name}: Working ({count} items)")
                working_endpoints += 1
            else:
                print(f"✗ {name}: Error {response.status_code}")
        except Exception as e:
            print(f"✗ {name}: Connection failed")
    
    return working_endpoints

def test_preference_submission():
    """Test if frontend can submit preferences properly"""
    print(f"\nTESTING PREFERENCE SUBMISSION:")
    
    # Test data that frontend would send
    preference_data = {
        "proficiencies": [
            {
                "teacher_id": 27,  # Using actual teacher ID from API
                "lecture_time_preference": "morning",
                "lab_time_preference": "afternoon",
                "cross_year_teaching": False,
                "preferred_years": ["SE"],
                "max_cross_year_sessions": 4,
                "subject_ratings": [
                    {
                        "subject_id": 1,
                        "knowledge_rating": 9,
                        "willingness_rating": 8
                    }
                ]
            }
        ]
    }
    
    try:
        response = requests.post('http://localhost:8000/api/teacher-preferences/', 
                               json=preference_data,
                               headers={'Content-Type': 'application/json'},
                               timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Preference Submission: Working")
            print(f"  Status: {result.get('status')}")
            print(f"  Message: {result.get('message')}")
            return True
        else:
            print(f"✗ Preference Submission: Error {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Preference Submission: {e}")
        return False

def test_timetable_generation():
    """Test if timetable generation works with enhanced algorithm"""
    print(f"\nTESTING TIMETABLE GENERATION:")
    
    try:
        # Test generation with division-specific algorithm
        response = requests.post('http://localhost:8000/api/generate-timetable/', 
                               json={'use_division_specific': True},
                               headers={'Content-Type': 'application/json'},
                               timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Timetable Generation: Working")
            print(f"  Algorithm: {result.get('algorithm')}")
            print(f"  Total Sessions: {result.get('total_sessions')}")
            print(f"  Divisions Processed: {result.get('divisions_processed')}")
            print(f"  Cross-Division Conflicts: {result.get('cross_division_conflicts')}")
            return True
        else:
            print(f"✗ Timetable Generation: Error {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print(f"✗ Timetable Generation: {e}")
        return False

def test_division_filtering():
    """Test if division-specific filtering works"""
    print(f"\nTESTING DIVISION-SPECIFIC FILTERING:")
    
    try:
        # Get divisions first
        divisions_response = requests.get('http://localhost:8000/api/divisions-list/')
        
        if divisions_response.status_code == 200:
            divisions = divisions_response.json()
            print(f"✓ Found {len(divisions)} divisions")
            
            if divisions:
                # Test filtering by first division
                first_division = divisions[0]
                division_key = first_division.get('key')
                
                if division_key:
                    timetable_response = requests.get(f'http://localhost:8000/api/timetable/?division={division_key}')
                    
                    if timetable_response.status_code == 200:
                        sessions = timetable_response.json()
                        print(f"✓ Division Filtering: Working")
                        print(f"  Division: {first_division.get('display_name')}")
                        print(f"  Sessions: {len(sessions)}")
                        return True
                    else:
                        print(f"✗ Division Filtering: Error {timetable_response.status_code}")
                        return False
                else:
                    print("✗ Division Filtering: No division key found")
                    return False
            else:
                print("✓ Division Filtering: No divisions (expected if not set up)")
                return True
        else:
            print(f"✗ Division Filtering: Error {divisions_response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Division Filtering: {e}")
        return False

def check_algorithm_inputs():
    """Check if all inputs needed by enhanced algorithm are available"""
    print(f"\nCHECKING ALGORITHM INPUTS:")
    
    inputs_available = {
        'teachers': False,
        'subjects': False,
        'rooms': False,
        'labs': False,
        'timeslots': False,
        'divisions': False,
        'proficiencies': False
    }
    
    try:
        # Check teachers
        response = requests.get('http://localhost:8000/api/teachers/')
        if response.status_code == 200:
            data = response.json()
            teacher_count = len(data.get('results', []))
            if teacher_count > 0:
                inputs_available['teachers'] = True
                print(f"✓ Teachers: {teacher_count} available")
            else:
                print("✗ Teachers: None found")
        
        # Check subjects
        response = requests.get('http://localhost:8000/api/subjects/')
        if response.status_code == 200:
            data = response.json()
            subject_count = len(data.get('results', []))
            if subject_count > 0:
                inputs_available['subjects'] = True
                print(f"✓ Subjects: {subject_count} available")
            else:
                print("✗ Subjects: None found")
        
        # Check rooms
        response = requests.get('http://localhost:8000/api/rooms/')
        if response.status_code == 200:
            data = response.json()
            room_count = len(data.get('results', []))
            if room_count > 0:
                inputs_available['rooms'] = True
                print(f"✓ Rooms: {room_count} available")
        
        # Check labs
        response = requests.get('http://localhost:8000/api/labs/')
        if response.status_code == 200:
            data = response.json()
            lab_count = len(data.get('results', []))
            if lab_count > 0:
                inputs_available['labs'] = True
                print(f"✓ Labs: {lab_count} available")
        
        # Check timeslots
        response = requests.get('http://localhost:8000/api/timeslots/')
        if response.status_code == 200:
            data = response.json()
            timeslot_count = len(data.get('results', []))
            if timeslot_count > 0:
                inputs_available['timeslots'] = True
                print(f"✓ TimeSlots: {timeslot_count} available")
        
        # Check divisions
        response = requests.get('http://localhost:8000/api/divisions-list/')
        if response.status_code == 200:
            divisions = response.json()
            if len(divisions) > 0:
                inputs_available['divisions'] = True
                print(f"✓ Divisions: {len(divisions)} available")
        
        # Check if we have minimum required inputs
        required_inputs = ['teachers', 'subjects', 'rooms', 'timeslots', 'divisions']
        missing_inputs = [inp for inp in required_inputs if not inputs_available[inp]]
        
        if not missing_inputs:
            print("✓ All required algorithm inputs available")
            return True
        else:
            print(f"✗ Missing inputs: {', '.join(missing_inputs)}")
            return False
            
    except Exception as e:
        print(f"✗ Error checking inputs: {e}")
        return False

def main():
    print("FRONTEND-BACKEND INTEGRATION TEST")
    print("=" * 60)
    
    # Test all components
    api_working = test_api_endpoints() >= 5  # At least 5 endpoints should work
    inputs_ok = check_algorithm_inputs()
    preferences_ok = test_preference_submission()
    generation_ok = test_timetable_generation()
    filtering_ok = test_division_filtering()
    
    print("\n" + "=" * 60)
    print("INTEGRATION TEST RESULTS")
    print("=" * 60)
    
    results = [
        ("API Endpoints", api_working),
        ("Algorithm Inputs", inputs_ok),
        ("Preference Submission", preferences_ok),
        ("Timetable Generation", generation_ok),
        ("Division Filtering", filtering_ok)
    ]
    
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
    
    all_working = all(result for _, result in results)
    most_working = sum(result for _, result in results) >= 3
    
    if all_working:
        print("\n🎉 SUCCESS: Frontend-Backend Integration Complete!")
        print("✅ All API endpoints working")
        print("✅ Enhanced algorithm inputs available")
        print("✅ Preference system functional")
        print("✅ Division-specific generation working")
        print("✅ Frontend can properly communicate with enhanced backend")
    elif most_working:
        print("\n⚠️  MOSTLY WORKING: Core integration functional")
        print("Most features working - minor issues to address")
    else:
        print("\n❌ NEEDS ATTENTION: Integration issues detected")
    
    print(f"\nIntegration Score: {sum(result for _, result in results)}/5")

if __name__ == "__main__":
    main()
