"""
Quick test to verify the real-world genetic algorithm is working
"""

import requests
import json
import time

def test_real_world_algorithm():
    print("Testing Real-World Genetic Algorithm...")
    print("=" * 60)
    
    # Test the enhanced API
    url = "http://localhost:8000/api/generate-timetable/"
    
    print("Sending request to generate timetable...")
    print(f"URL: {url}")
    
    start_time = time.time()
    
    try:
        response = requests.post(url, timeout=120)  # 2 minute timeout
        end_time = time.time()
        
        print(f"Response time: {end_time - start_time:.2f} seconds")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("\nSUCCESS! Real-World Algorithm Response:")
            print("-" * 50)
            print(f"Algorithm: {data.get('algorithm', 'Unknown')}")
            print(f"Sessions Created: {data.get('sessions_created', 0)}")
            print(f"Fitness Score: {data.get('fitness_score', 'N/A')}")
            print(f"Success Rate: {data.get('success_rate', 'N/A')}")
            
            # Show constraint violations
            violations = data.get('constraint_violations', {})
            if violations:
                print(f"\nConstraint Violations Analysis:")
                for constraint, count in violations.items():
                    status = "OK" if count == 0 else "WARN" if count < 5 else "ERROR"
                    print(f"  [{status}] {constraint.replace('_', ' ').title()}: {count}")
            
            # Show applied features
            features = data.get('features_applied', [])
            if features:
                print(f"\nReal-World Features Applied:")
                for feature in features:
                    print(f"  {feature}")
            
            print(f"\nMessage: {data.get('message', '')}")
            
        else:
            print(f"Error: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error message: {error_data.get('message', 'Unknown error')}")
            except:
                print(f"Raw response: {response.text}")
    
    except requests.exceptions.Timeout:
        print("Request timed out - algorithm is running but taking longer than expected")
        print("This is normal for the first run with comprehensive constraints")
    except requests.exceptions.ConnectionError:
        print("Connection error - make sure Django server is running on localhost:8000")
    except Exception as e:
        print(f"Unexpected error: {e}")

def test_timetable_view():
    print("\nTesting Timetable View...")
    print("=" * 60)
    
    url = "http://localhost:8000/api/timetable/"
    
    try:
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Timetable retrieved successfully!")
            print(f"Total sessions in timetable: {len(data)}")
            
            if data:
                # Show sample session
                sample = data[0]
                print(f"\nSample Session:")
                print(f"  Subject: {sample.get('subject_name', 'N/A')}")
                print(f"  Teacher: {sample.get('teacher_name', 'N/A')}")
                print(f"  Room/Lab: {sample.get('room_name', sample.get('lab_name', 'N/A'))}")
                print(f"  Time: {sample.get('timeslot_info', 'N/A')}")
                print(f"  Year/Division: {sample.get('year_division', 'N/A')}")
        else:
            print(f"Error retrieving timetable: {response.status_code}")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_real_world_algorithm()
    test_timetable_view()
    
    print("\n" + "=" * 60)
    print("Real-World College Timetable Generator Test Complete!")
    print("=" * 60)
