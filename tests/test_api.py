import requests
import json

try:
    # Test the generate timetable endpoint
    response = requests.post('http://localhost:8000/api/generate-timetable/', 
                           headers={'Content-Type': 'application/json'},
                           timeout=60)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Content: {response.text}")
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error JSON: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Raw error text: {response.text}")
            
except requests.exceptions.ConnectionError as e:
    print(f"Connection error: {e}")
except requests.exceptions.Timeout as e:
    print(f"Timeout error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
