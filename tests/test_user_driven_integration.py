#!/usr/bin/env python
"""
Test script for User-Driven Algorithm Integration
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'timetable_generator.settings')
django.setup()

def test_user_driven_import():
    """Test if User-Driven Algorithm can be imported"""
    try:
        from timetable_app.user_driven_timetable_algorithm import UserDrivenTimetableAlgorithm
        print("✅ User-Driven Algorithm import successful")
        return True
    except ImportError as e:
        print(f"❌ User-Driven Algorithm import failed: {e}")
        return False

def test_views_import():
    """Test if new views can be imported"""
    try:
        from timetable_app.views import (
            UserDrivenConfigurationView,
            UserDrivenGenerationView,
            ProficiencyManagementView
        )
        print("✅ New views import successful")
        return True
    except ImportError as e:
        print(f"❌ Views import failed: {e}")
        return False

def test_default_config_generation():
    """Test default configuration generation"""
    try:
        from timetable_app.views import GenerateTimetableView
        
        view = GenerateTimetableView()
        config = view._get_default_user_config()
        
        required_keys = [
            'college_start_time', 'college_end_time', 'recess_start', 'recess_end',
            'professor_year_assignments', 'proficiency_data', 'room_assignments'
        ]
        
        missing_keys = [key for key in required_keys if key not in config]
        
        if not missing_keys:
            print("✅ Default configuration generation successful")
            print(f"   Generated config with {len(config)} keys")
            return True
        else:
            print(f"❌ Default configuration missing keys: {missing_keys}")
            return False
            
    except Exception as e:
        print(f"❌ Default configuration generation failed: {e}")
        return False

def test_algorithm_initialization():
    """Test User-Driven Algorithm initialization"""
    try:
        from timetable_app.user_driven_timetable_algorithm import UserDrivenTimetableAlgorithm
        from timetable_app.views import GenerateTimetableView
        from datetime import time
        
        # Get default config
        view = GenerateTimetableView()
        config_data = view._get_default_user_config()
        
        # Initialize algorithm
        algorithm = UserDrivenTimetableAlgorithm(
            config_data=config_data,
            target_years=['FE', 'SE']
        )
        
        print("✅ User-Driven Algorithm initialization successful")
        print(f"   Target years: {algorithm.target_years}")
        print(f"   Population size: {algorithm.population_size}")
        print(f"   Generations: {algorithm.generations}")
        return True
        
    except Exception as e:
        print(f"❌ Algorithm initialization failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing User-Driven Algorithm Integration")
    print("=" * 50)
    
    tests = [
        test_user_driven_import,
        test_views_import,
        test_default_config_generation,
        test_algorithm_initialization
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Backend integration is ready.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    main()
