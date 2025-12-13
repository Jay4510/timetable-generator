import requests
import json

try:
    # Test the generate timetable endpoint with shorter timeout
    response = requests.post('http://localhost:8000/api/generate-timetable/', 
                           headers={'Content-Type': 'application/json'},
                           timeout=30)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Content: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Algorithm Used: {data.get('algorithm', 'Unknown')}")
        print(f"Sessions Created: {data.get('sessions_created', 0)}")
        print(f"Success Rate: {data.get('success_rate', 'N/A')}")
            
except requests.exceptions.Timeout as e:
    print(f"Request timed out after 30 seconds - algorithm is running")
except Exception as e:
    print(f"Error: {e}")
