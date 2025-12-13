import requests
import json

try:
    # Test the get timetable endpoint
    response = requests.get('http://localhost:8000/api/timetable/', 
                           headers={'Content-Type': 'application/json'},
                           timeout=10)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Number of sessions: {len(data)}")
        if data:
            print("Sample session:")
            print(json.dumps(data[0], indent=2))
    else:
        print(f"Error: {response.status_code}")
        print(f"Response Content: {response.text}")
            
except requests.exceptions.ConnectionError as e:
    print(f"Connection error: {e}")
except requests.exceptions.Timeout as e:
    print(f"Timeout error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
