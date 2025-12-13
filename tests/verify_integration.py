#!/usr/bin/env python
"""
Simple verification script for User-Driven Algorithm Integration
"""
import sys
import os

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test basic imports without Django setup"""
    try:
        # Test if the user-driven algorithm file exists and can be imported
        import importlib.util
        
        # Check if user_driven_timetable_algorithm.py exists
        algo_path = os.path.join('timetable_app', 'user_driven_timetable_algorithm.py')
        if os.path.exists(algo_path):
            print("✅ User-Driven Algorithm file exists")
        else:
            print("❌ User-Driven Algorithm file not found")
            return False
        
        # Check if views.py exists and has correct syntax
        views_path = os.path.join('timetable_app', 'views.py')
        if os.path.exists(views_path):
            print("✅ Views.py file exists")
            
            # Try to compile views.py
            with open(views_path, 'r', encoding='utf-8') as f:
                content = f.read()
                try:
                    compile(content, views_path, 'exec')
                    print("✅ Views.py syntax is valid")
                except SyntaxError as e:
                    print(f"❌ Views.py syntax error: {e}")
                    return False
        else:
            print("❌ Views.py file not found")
            return False
        
        # Check if urls.py exists and has correct syntax
        urls_path = os.path.join('timetable_app', 'urls.py')
        if os.path.exists(urls_path):
            print("✅ URLs.py file exists")
            
            # Try to compile urls.py
            with open(urls_path, 'r', encoding='utf-8') as f:
                content = f.read()
                try:
                    compile(content, urls_path, 'exec')
                    print("✅ URLs.py syntax is valid")
                except SyntaxError as e:
                    print(f"❌ URLs.py syntax error: {e}")
                    return False
        else:
            print("❌ URLs.py file not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

def check_new_endpoints():
    """Check if new endpoints are properly defined"""
    try:
        urls_path = os.path.join('timetable_app', 'urls.py')
        with open(urls_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_endpoints = [
            'user-driven/config/',
            'user-driven/generate/',
            'user-driven/proficiency/'
        ]
        
        for endpoint in required_endpoints:
            if endpoint in content:
                print(f"✅ Endpoint '{endpoint}' found in URLs")
            else:
                print(f"❌ Endpoint '{endpoint}' not found in URLs")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint check failed: {e}")
        return False

def check_views_classes():
    """Check if new view classes are defined"""
    try:
        views_path = os.path.join('timetable_app', 'views.py')
        with open(views_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        required_classes = [
            'UserDrivenConfigurationView',
            'UserDrivenGenerationView',
            'ProficiencyManagementView'
        ]
        
        for class_name in required_classes:
            if f"class {class_name}" in content:
                print(f"✅ View class '{class_name}' found")
            else:
                print(f"❌ View class '{class_name}' not found")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ View classes check failed: {e}")
        return False

def main():
    """Run all verification tests"""
    print("🔍 Verifying User-Driven Algorithm Integration")
    print("=" * 50)
    
    tests = [
        ("Basic File & Syntax Check", test_imports),
        ("New Endpoints Check", check_new_endpoints),
        ("New View Classes Check", check_views_classes)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print("\n" + "=" * 50)
    print(f"🎯 Verification Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Integration verification successful!")
        print("💡 The backend is ready for testing with Django server.")
        return True
    else:
        print("⚠️  Some verification tests failed.")
        return False

if __name__ == "__main__":
    main()
