#!/usr/bin/env python
"""
Test Division-Specific Timetable Generation
"""

import requests
import json

def test_division_generation():
    print("TESTING DIVISION-SPECIFIC TIMETABLE GENERATION")
    print("=" * 60)
    
    try:
        # Test with division-specific enabled
        print("1. Testing with division-specific generation enabled...")
        response = requests.post('http://localhost:8000/api/generate-timetable/', 
                               json={'use_division_specific': True},
                               headers={'Content-Type': 'application/json'},
                               timeout=120)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Division-specific generation response:")
            for key, value in data.items():
                if key == 'division_results':
                    print(f"  {key}:")
                    for div_key, div_data in value.items():
                        print(f"    {div_key}: {div_data}")
                else:
                    print(f"  {key}: {value}")
            
            # Check if it's actually division-specific
            if 'division_results' in data:
                print("\n✅ DIVISION-SPECIFIC GENERATION IS WORKING!")
                return True
            else:
                print("\n❌ Not using division-specific generation")
                return False
        else:
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Request error: {e}")
        return False

def test_sessions_by_division():
    print("\n2. Testing session distribution by division...")
    
    try:
        response = requests.get('http://localhost:8000/api/timetable/', 
                              headers={'Content-Type': 'application/json'})
        
        if response.status_code == 200:
            sessions = response.json()
            print(f"Total sessions retrieved: {len(sessions)}")
            
            # Group by division
            division_sessions = {}
            for session in sessions:
                subject_name = session.get('subject', {}).get('name', 'Unknown')
                year_name = session.get('subject', {}).get('year', {}).get('name', 'Unknown')
                division_name = session.get('subject', {}).get('division', {}).get('name', 'Unknown')
                
                division_key = f"{year_name} {division_name}"
                
                if division_key not in division_sessions:
                    division_sessions[division_key] = []
                division_sessions[division_key].append(session)
            
            print("\nSessions by division:")
            for division, sessions in division_sessions.items():
                print(f"  {division}: {len(sessions)} sessions")
                
                # Check for conflicts within division
                timeslots = [s.get('timeslot', {}).get('id') for s in sessions]
                conflicts = len(timeslots) - len(set(timeslots))
                if conflicts > 0:
                    print(f"    ⚠️  {conflicts} time conflicts in {division}")
                else:
                    print(f"    ✅ No conflicts in {division}")
            
            return len(division_sessions) > 1
        else:
            print(f"Error getting sessions: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    division_working = test_division_generation()
    sessions_distributed = test_sessions_by_division()
    
    print("\n" + "=" * 60)
    print("DIVISION GENERATION TEST RESULTS")
    print("=" * 60)
    
    if division_working and sessions_distributed:
        print("✅ DIVISION-SPECIFIC GENERATION IS WORKING CORRECTLY!")
    else:
        print("❌ DIVISION-SPECIFIC GENERATION NEEDS FIXES")
        if not division_working:
            print("   - Division-specific API not responding correctly")
        if not sessions_distributed:
            print("   - Sessions not properly distributed across divisions")
