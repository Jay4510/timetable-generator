import requests
import json

def test_timetable_api():
    try:
        # Test timetable generation
        print("Testing timetable generation...")
        response = requests.post('http://localhost:8000/api/generate-timetable/', 
                               headers={'Content-Type': 'application/json'},
                               timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            print(f"[SUCCESS] Generation successful: {data.get('sessions_created', 0)} sessions created")
            print(f"Algorithm: {data.get('algorithm', 'Unknown')}")
        else:
            print(f"[ERROR] Generation failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        # Test timetable retrieval
        print("\nTesting timetable retrieval...")
        response = requests.get('http://localhost:8000/api/timetable/', timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("[SUCCESS] Retrieval successful")
            print(f"Response type: {type(data)}")
            
            if isinstance(data, list):
                print(f"Sessions count: {len(data)}")
                if len(data) > 0:
                    print(f"Sample session: {json.dumps(data[0], indent=2)}")
            elif isinstance(data, dict):
                print(f"Response keys: {list(data.keys())}")
                if 'results' in data:
                    print(f"Results count: {len(data['results'])}")
                    if len(data['results']) > 0:
                        print(f"Sample session: {json.dumps(data['results'][0], indent=2)}")
        else:
            print(f"[ERROR] Retrieval failed: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print("[TIMEOUT] Request timed out - algorithm may still be running")
    except Exception as e:
        print(f"[ERROR] Error: {e}")

if __name__ == "__main__":
    test_timetable_api()
