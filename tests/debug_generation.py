#!/usr/bin/env python
"""
Debug timetable generation
"""

import requests
import json

def debug_generation():
    print("DEBUGGING TIMETABLE GENERATION")
    print("=" * 50)
    
    try:
        print("Sending generation request...")
        response = requests.post('http://localhost:8000/api/generate-timetable/', 
                               json={'use_division_specific': False},
                               headers={'Content-Type': 'application/json'},
                               timeout=120)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print("Response data:")
            for key, value in data.items():
                print(f"  {key}: {value}")
        else:
            print(f"Error response: {response.text}")
            
    except Exception as e:
        print(f"Request error: {e}")

if __name__ == "__main__":
    debug_generation()
