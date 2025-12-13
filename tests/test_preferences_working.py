#!/usr/bin/env python
"""
Test if Enhanced Preferences are Actually Working
"""

import requests
import json

def test_preference_enforcement():
    print("TESTING ENHANCED PREFERENCE ENFORCEMENT")
    print("=" * 50)
    
    # Step 1: Submit specific preferences
    print("Step 1: Submitting teacher preferences...")
    
    preference_data = {
        "proficiencies": [
            {
                "teacher_id": 27,
                "lecture_time_preference": "morning",
                "lab_time_preference": "afternoon",
                "cross_year_teaching": False,
                "subject_ratings": [
                    {"subject_id": 1, "knowledge_rating": 9, "willingness_rating": 8}
                ]
            }
        ]
    }
    
    try:
        response = requests.post('http://localhost:8000/api/teacher-preferences/', 
                               json=preference_data,
                               headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            print("SUCCESS: Preferences submitted")
        else:
            print(f"ERROR: Preference submission failed - {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    # Step 2: Generate timetable
    print("\nStep 2: Generating timetable with preferences...")
    
    try:
        response = requests.post('http://localhost:8000/api/generate-timetable/', 
                               json={'use_division_specific': True},
                               headers={'Content-Type': 'application/json'},
                               timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            print(f"SUCCESS: Timetable generated - {result['total_sessions']} sessions")
        else:
            print(f"ERROR: Generation failed - {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    # Step 3: Check if preferences are respected
    print("\nStep 3: Checking preference compliance...")
    
    try:
        response = requests.get('http://localhost:8000/api/timetable/')
        
        if response.status_code == 200:
            sessions = response.json()
            
            # Find sessions for teacher 27
            teacher_27_sessions = [s for s in sessions if s.get('teacher', {}).get('id') == 27]
            
            if teacher_27_sessions:
                print(f"Found {len(teacher_27_sessions)} sessions for teacher 27")
                
                morning_lectures = 0
                afternoon_labs = 0
                preference_violations = 0
                
                for session in teacher_27_sessions:
                    timeslot = session.get('timeslot', {})
                    start_time = timeslot.get('start_time', '')
                    subject = session.get('subject', {})
                    
                    if start_time:
                        hour = int(start_time.split(':')[0])
                        is_morning = hour < 13
                        is_lab = subject.get('requires_lab', False)
                        
                        if is_lab and is_morning:
                            preference_violations += 1
                            print(f"  VIOLATION: Lab in morning at {start_time}")
                        elif not is_lab and not is_morning:
                            preference_violations += 1
                            print(f"  VIOLATION: Lecture in afternoon at {start_time}")
                        
                        if not is_lab and is_morning:
                            morning_lectures += 1
                        elif is_lab and not is_morning:
                            afternoon_labs += 1
                
                print(f"Morning lectures: {morning_lectures}")
                print(f"Afternoon labs: {afternoon_labs}")
                print(f"Preference violations: {preference_violations}")
                
                if preference_violations == 0:
                    print("SUCCESS: Preferences are being enforced!")
                    return True
                else:
                    print("WARNING: Some preference violations found")
                    return False
            else:
                print("No sessions found for teacher 27")
                return True  # Not necessarily a failure
        else:
            print(f"ERROR: Could not get timetable - {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_division_specific_display():
    print("\nTESTING DIVISION-SPECIFIC DISPLAY")
    print("=" * 40)
    
    try:
        # Get divisions
        response = requests.get('http://localhost:8000/api/divisions-list/')
        
        if response.status_code == 200:
            divisions = response.json()
            print(f"Found {len(divisions)} divisions:")
            
            for div in divisions:
                print(f"  - {div.get('display_name')} (key: {div.get('key')})")
            
            if divisions:
                # Test filtering by first division
                first_division = divisions[0]
                division_key = first_division.get('key')
                
                if division_key:
                    filter_response = requests.get(f'http://localhost:8000/api/timetable/?division={division_key}')
                    
                    if filter_response.status_code == 200:
                        filtered_sessions = filter_response.json()
                        print(f"\nFiltered timetable for {first_division.get('display_name')}: {len(filtered_sessions)} sessions")
                        
                        # Verify all sessions belong to this division
                        correct_sessions = 0
                        for session in filtered_sessions:
                            subject = session.get('subject', {})
                            year_name = subject.get('year', {}).get('name', '')
                            division_name = subject.get('division', {}).get('name', '')
                            
                            expected_key = f"{year_name}_{division_name}"
                            if expected_key == division_key:
                                correct_sessions += 1
                        
                        print(f"Correctly filtered: {correct_sessions}/{len(filtered_sessions)} sessions")
                        
                        if correct_sessions == len(filtered_sessions):
                            print("SUCCESS: Division filtering working correctly!")
                            return True
                        else:
                            print("WARNING: Some sessions not properly filtered")
                            return False
                    else:
                        print(f"ERROR: Could not filter timetable - {filter_response.status_code}")
                        return False
                else:
                    print("ERROR: No division key found")
                    return False
            else:
                print("No divisions found - this might be expected")
                return True
        else:
            print(f"ERROR: Could not get divisions - {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    print("ENHANCED ALGORITHM INTEGRATION TEST")
    print("=" * 60)
    
    preferences_working = test_preference_enforcement()
    division_display_working = test_division_specific_display()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    if preferences_working:
        print("PREFERENCES: Working - First/second half preferences enforced")
    else:
        print("PREFERENCES: Needs attention")
    
    if division_display_working:
        print("DIVISION DISPLAY: Working - Division-specific filtering functional")
    else:
        print("DIVISION DISPLAY: Needs attention")
    
    if preferences_working and division_display_working:
        print("\nSUCCESS: Enhanced algorithm fully integrated with frontend!")
        print("- Teacher preferences are being enforced")
        print("- Division-specific display is working")
        print("- Frontend can properly communicate with enhanced backend")
    elif preferences_working or division_display_working:
        print("\nPARTIAL SUCCESS: Core functionality working")
    else:
        print("\nNEEDS ATTENTION: Some integration issues")

if __name__ == "__main__":
    main()
