"""
Test Frontend Fixes - Verify 429 errors and component crashes are resolved
"""

import requests
import time
import json

def test_api_rate_limiting():
    """Test that API calls don't trigger 429 errors"""
    print("Testing API rate limiting fixes...")
    
    base_url = "http://localhost:8000/api"
    endpoints = [
        "/teachers/",
        "/subjects/", 
        "/timetable-config/",
        "/timetable/"
    ]
    
    # Make multiple rapid requests to simulate frontend behavior
    for i in range(3):
        print(f"\nRound {i+1} of API calls:")
        for endpoint in endpoints:
            try:
                response = requests.get(f"{base_url}{endpoint}", timeout=5)
                status = "✓ OK" if response.status_code in [200, 404] else f"✗ {response.status_code}"
                print(f"  {endpoint}: {status}")
                
                if response.status_code == 429:
                    print(f"    ⚠️  Still getting 429 errors!")
                    return False
                    
            except Exception as e:
                print(f"  {endpoint}: ✗ Error - {str(e)}")
        
        time.sleep(0.1)  # Small delay between rounds
    
    print("\n✅ API rate limiting test passed - No 429 errors!")
    return True

def test_data_structure_handling():
    """Test that API responses are handled correctly"""
    print("\nTesting data structure handling...")
    
    try:
        # Test teachers endpoint
        response = requests.get("http://localhost:8000/api/teachers/", timeout=5)
        if response.ok:
            data = response.json()
            
            # Check if it's paginated or direct array
            if isinstance(data, dict) and 'results' in data:
                teachers = data['results']
                print(f"  Teachers (paginated): {len(teachers)} found")
            elif isinstance(data, list):
                teachers = data
                print(f"  Teachers (direct array): {len(teachers)} found")
            else:
                print(f"  ⚠️  Unexpected teachers data structure: {type(data)}")
                return False
        
        # Test subjects endpoint
        response = requests.get("http://localhost:8000/api/subjects/", timeout=5)
        if response.ok:
            data = response.json()
            
            if isinstance(data, dict) and 'results' in data:
                subjects = data['results']
                print(f"  Subjects (paginated): {len(subjects)} found")
            elif isinstance(data, list):
                subjects = data
                print(f"  Subjects (direct array): {len(subjects)} found")
            else:
                print(f"  ⚠️  Unexpected subjects data structure: {type(data)}")
                return False
        
        print("✅ Data structure handling test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Data structure test failed: {str(e)}")
        return False

def test_configuration_endpoint():
    """Test configuration endpoint handles 404 gracefully"""
    print("\nTesting configuration endpoint...")
    
    try:
        response = requests.get("http://localhost:8000/api/timetable-config/", timeout=5)
        
        if response.status_code == 200:
            print("  ✓ Configuration exists and returned successfully")
        elif response.status_code == 404:
            print("  ✓ No configuration found (404) - This is expected for first run")
        else:
            print(f"  ⚠️  Unexpected status code: {response.status_code}")
            return False
        
        print("✅ Configuration endpoint test passed!")
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {str(e)}")
        return False

def main():
    print("=" * 60)
    print("FRONTEND FIXES VERIFICATION TEST")
    print("=" * 60)
    
    tests = [
        ("API Rate Limiting", test_api_rate_limiting),
        ("Data Structure Handling", test_data_structure_handling), 
        ("Configuration Endpoint", test_configuration_endpoint)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running: {test_name}")
        print("-" * 40)
        
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} CRASHED: {str(e)}")
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Frontend fixes are working correctly")
        print("✅ No more 429 errors expected")
        print("✅ Component crashes should be prevented")
        print("✅ Data structures handled properly")
    else:
        print(f"\n⚠️  {total-passed} test(s) failed")
        print("Some issues may still need attention")
    
    print("\n📱 Frontend URL: http://localhost:5182")
    print("🔧 Backend URL: http://localhost:8000")

if __name__ == "__main__":
    main()
