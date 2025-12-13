#!/usr/bin/env python3

import requests
import json

def test_divisions_api():
    """Simple test of divisions API"""
    
    print("TESTING DIVISIONS API")
    print("=" * 30)
    
    try:
        url = 'http://localhost:8000/api/divisions-list/'
        print(f"URL: {url}")
        
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Content-Length: {len(response.text)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print("SUCCESS: Valid JSON response!")
                print(f"Data type: {type(data)}")
                
                if isinstance(data, list):
                    print(f"Number of divisions: {len(data)}")
                    for i, div in enumerate(data):
                        print(f"Division {i+1}: {div}")
                else:
                    print(f"Response data: {data}")
                    
                return True, data
                
            except json.JSONDecodeError as e:
                print(f"ERROR: JSON Parse failed - {e}")
                print(f"Raw response (first 200 chars): {repr(response.text[:200])}")
                return False, None
        else:
            print(f"ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text[:200]}")
            return False, None
            
    except requests.exceptions.ConnectionError:
        print("ERROR: Cannot connect to Django backend")
        return False, None
    except Exception as e:
        print(f"ERROR: {e}")
        return False, None

def test_basic_endpoints():
    """Test basic API endpoints"""
    
    print("\nTESTING BASIC ENDPOINTS")
    print("=" * 30)
    
    endpoints = {
        'teachers': 'http://localhost:8000/api/teachers/',
        'years': 'http://localhost:8000/api/years/',
        'divisions': 'http://localhost:8000/api/divisions/',
    }
    
    results = {}
    
    for name, url in endpoints.items():
        try:
            response = requests.get(url)
            print(f"{name}: Status {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else "non-list"
                    print(f"  -> Valid JSON, {count} items")
                    results[name] = data
                except:
                    print(f"  -> Invalid JSON")
                    results[name] = None
            else:
                print(f"  -> Error {response.status_code}")
                results[name] = None
                
        except Exception as e:
            print(f"{name}: Error - {e}")
            results[name] = None
    
    return results

if __name__ == "__main__":
    print("DIVISION API SIMPLE TEST")
    print("=" * 40)
    
    # Test divisions API
    success, divisions_data = test_divisions_api()
    
    # Test other endpoints
    endpoint_results = test_basic_endpoints()
    
    print("\nSUMMARY")
    print("=" * 20)
    print(f"Divisions API working: {success}")
    
    if success and divisions_data:
        print(f"Divisions found: {len(divisions_data) if isinstance(divisions_data, list) else 0}")
    
    for name, data in endpoint_results.items():
        count = len(data) if data and isinstance(data, list) else 0
        print(f"{name.capitalize()}: {count} items")
    
    if not success:
        print("\nRECOMMENDATIONS:")
        print("1. Check Django server is running: python manage.py runserver")
        print("2. Check database has divisions data")
        print("3. Check views.py get_divisions function")
        print("4. Check URL routing in urls.py")
