#!/usr/bin/env python
"""
Test frontend API connectivity
"""

import requests
import json

def test_frontend_api_calls():
    print("Testing Frontend API Connectivity")
    print("=" * 40)
    
    base_url = "http://localhost:8000/api"
    
    # Test endpoints that the frontend would call
    endpoints = [
        "/teachers/",
        "/subjects/", 
        "/rooms/",
        "/timetable-config/",
        "/timetable/"
    ]
    
    for endpoint in endpoints:
        try:
            print(f"\nTesting {endpoint}...")
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"  SUCCESS: {len(data)} items returned")
                elif isinstance(data, dict):
                    print(f"  SUCCESS: {len(data)} fields returned")
                else:
                    print(f"  SUCCESS: Response received")
            else:
                print(f"  FAILED: Status {response.status_code}")
                print(f"     Response: {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            print(f"  CONNECTION ERROR: Backend not running")
        except Exception as e:
            print(f"  ERROR: {e}")
    
    # Test timetable generation
    print(f"\nTesting timetable generation...")
    try:
        response = requests.post(f"{base_url}/generate-timetable/", 
                               json={}, 
                               headers={'Content-Type': 'application/json'},
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"  GENERATION SUCCESS: {data.get('sessions_created', 0)} sessions")
            print(f"     Algorithm: {data.get('algorithm', 'Unknown')}")
        else:
            print(f"  GENERATION FAILED: Status {response.status_code}")
            
    except Exception as e:
        print(f"  GENERATION ERROR: {e}")

if __name__ == "__main__":
    test_frontend_api_calls()
