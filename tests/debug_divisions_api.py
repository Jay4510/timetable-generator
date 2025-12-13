#!/usr/bin/env python3

import requests
import json

def debug_divisions_api():
    """Debug the divisions API endpoint"""
    try:
        print("=== DEBUGGING DIVISIONS API ===")
        
        # Test the divisions-list endpoint
        url = 'http://localhost:8000/api/divisions-list/'
        print(f"Testing URL: {url}")
        
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type', 'Not set')}")
        print(f"Content-Length: {len(response.text)}")
        print(f"Raw Response: {repr(response.text)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"Successfully parsed JSON!")
                print(f"Data type: {type(data)}")
                print(f"Data content: {json.dumps(data, indent=2)}")
                
                if isinstance(data, list):
                    print(f"Number of divisions: {len(data)}")
                    for i, div in enumerate(data):
                        print(f"Division {i+1}: {div}")
                        
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                print("Response is not valid JSON!")
                
                # Try to find where the JSON becomes invalid
                print("Analyzing response character by character...")
                for i, char in enumerate(response.text[:100]):
                    if not char.isprintable() and char not in ['\n', '\r', '\t']:
                        print(f"Non-printable character at position {i}: {repr(char)}")
                        
        else:
            print(f"HTTP Error: {response.status_code}")
            print(f"Error response: {response.text}")
            
        # Also test other endpoints to see if they work
        print("\n=== TESTING OTHER ENDPOINTS ===")
        
        endpoints = [
            'http://localhost:8000/api/teachers/',
            'http://localhost:8000/api/years/',
            'http://localhost:8000/api/divisions/',
        ]
        
        for endpoint in endpoints:
            try:
                resp = requests.get(endpoint)
                print(f"{endpoint}: Status {resp.status_code}, Length {len(resp.text)}")
                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        print(f"  -> Valid JSON with {len(data) if isinstance(data, list) else 'non-list'} items")
                    except:
                        print(f"  -> Invalid JSON")
            except Exception as e:
                print(f"{endpoint}: Error - {e}")
                
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Django backend. Is it running on localhost:8000?")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_divisions_api()
