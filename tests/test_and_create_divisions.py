#!/usr/bin/env python3

import requests
import json

def test_api_directly():
    """Test the divisions API directly and create data if needed"""
    
    print("=== TESTING DIVISIONS API ===")
    
    try:
        # Test the divisions API
        url = 'http://localhost:8000/api/divisions-list/'
        print(f"Testing: {url}")
        
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"✓ Valid JSON response!")
                print(f"Number of divisions: {len(data) if isinstance(data, list) else 'Not a list'}")
                
                if isinstance(data, list):
                    for i, div in enumerate(data):
                        print(f"  Division {i+1}: {div}")
                else:
                    print(f"Response: {data}")
                    
                return True
                
            except json.JSONDecodeError as e:
                print(f"✗ JSON Parse Error: {e}")
                print(f"Raw response: {repr(response.text[:200])}")
                return False
        else:
            print(f"✗ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to Django backend on localhost:8000")
        print("Make sure Django server is running with: python manage.py runserver")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def test_other_endpoints():
    """Test other API endpoints to verify backend is working"""
    
    print("\n=== TESTING OTHER ENDPOINTS ===")
    
    endpoints = [
        'http://localhost:8000/api/teachers/',
        'http://localhost:8000/api/years/',
        'http://localhost:8000/api/divisions/',
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(endpoint)
            print(f"{endpoint}: Status {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    count = len(data) if isinstance(data, list) else "non-list"
                    print(f"  ✓ Valid JSON with {count} items")
                except:
                    print(f"  ✗ Invalid JSON")
            else:
                print(f"  ✗ Error: {response.status_code}")
                
        except Exception as e:
            print(f"{endpoint}: ✗ Error - {e}")

def create_test_data():
    """Create test data using the Django API"""
    
    print("\n=== CREATING TEST DATA ===")
    
    # First, let's check if we can create years
    years_to_create = [
        {"name": "SE", "description": "Second Year Engineering"},
        {"name": "TE", "description": "Third Year Engineering"},
        {"name": "BE", "description": "Final Year Engineering"}
    ]
    
    for year_data in years_to_create:
        try:
            response = requests.post('http://localhost:8000/api/years/', json=year_data)
            if response.status_code in [200, 201]:
                print(f"✓ Created/Found year: {year_data['name']}")
            else:
                print(f"- Year {year_data['name']}: Status {response.status_code}")
        except Exception as e:
            print(f"✗ Error creating year {year_data['name']}: {e}")
    
    # Get the created years
    try:
        years_response = requests.get('http://localhost:8000/api/years/')
        if years_response.status_code == 200:
            years = years_response.json()
            print(f"Available years: {len(years)}")
            
            # Create divisions for each year
            for year in years:
                if year['name'] in ['SE', 'TE', 'BE']:
                    for div_name in ['A', 'B']:
                        division_data = {
                            "year": year['id'],
                            "name": div_name,
                            "num_batches": 3
                        }
                        
                        try:
                            div_response = requests.post('http://localhost:8000/api/divisions/', json=division_data)
                            if div_response.status_code in [200, 201]:
                                print(f"✓ Created division: {year['name']} {div_name}")
                            else:
                                print(f"- Division {year['name']} {div_name}: Status {div_response.status_code}")
                        except Exception as e:
                            print(f"✗ Error creating division {year['name']} {div_name}: {e}")
                            
    except Exception as e:
        print(f"✗ Error fetching years: {e}")

if __name__ == "__main__":
    print("DIVISION API DEBUGGING AND SETUP")
    print("=" * 50)
    
    # Test current API
    api_working = test_api_directly()
    
    # Test other endpoints
    test_other_endpoints()
    
    # If divisions API is not working or empty, try to create data
    if not api_working:
        print("\nAPI not working properly, attempting to create test data...")
        create_test_data()
        
        # Test again
        print("\n=== RETESTING AFTER DATA CREATION ===")
        test_api_directly()
    
    print("\n" + "=" * 50)
    print("DEBUGGING COMPLETE")
    print("If divisions API is still not working, check Django server logs for errors.")
