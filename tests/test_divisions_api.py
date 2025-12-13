#!/usr/bin/env python3

import requests
import json

def test_divisions_api():
    """Test the divisions API endpoint"""
    try:
        print("Testing divisions API endpoint...")
        
        # Test the divisions-list endpoint
        url = 'http://localhost:8000/api/divisions-list/'
        print(f"Making request to: {url}")
        
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Raw Content: {response.text[:500]}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"JSON Data: {data}")
                print(f"Number of divisions: {len(data) if isinstance(data, list) else 'Not a list'}")
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                print("Response is not valid JSON")
        else:
            print(f"API Error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Django backend. Is it running on localhost:8000?")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_divisions_api()
