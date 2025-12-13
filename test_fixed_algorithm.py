#!/usr/bin/env python3
"""
Quick test script to verify the FIXED algorithm is working
Run this after starting the Django server
"""

import requests
import json
from datetime import datetime

# API endpoint
BASE_URL = "http://127.0.0.1:8000"
GENERATE_URL = f"{BASE_URL}/api/generate-timetable/"

def test_algorithm():
    """Test the fixed algorithm"""
    
    print("=" * 80)
    print("🧪 TESTING FIXED ALGORITHM v2.0")
    print("=" * 80)
    print()
    
    # Test data
    test_data = {
        "use_user_driven": True,
        "target_years": ["SE", "TE"],
        "config_data": {
            "college_start_time": "09:00",
            "college_end_time": "17:45",
            "recess_start": "13:00",
            "recess_end": "13:45"
        }
    }
    
    print("📤 Sending request to generate timetable...")
    print(f"   URL: {GENERATE_URL}")
    print(f"   Years: {test_data['target_years']}")
    print()
    
    try:
        response = requests.post(
            GENERATE_URL,
            json=test_data,
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ SUCCESS! Timetable generated")
            print()
            
            # Check for algorithm version
            algorithm = result.get('algorithm', 'Unknown')
            print(f"📊 Algorithm: {algorithm}")
            
            if "FIXED" in algorithm or "v2.0" in algorithm:
                print("   ✅ Using FIXED version!")
            else:
                print("   ⚠️  Not using FIXED version")
            print()
            
            # Check for success metrics (FIX #2)
            success_metrics = result.get('success_metrics', {})
            if success_metrics:
                print("✅ FIX #2 VERIFIED: Success metrics are visible!")
                print(f"   Success Rate: {success_metrics.get('success_rate', 0)}%")
                print(f"   Total Divisions: {success_metrics.get('total_divisions', 0)}")
                print(f"   Successful: {success_metrics.get('successful_divisions', 0)}")
                print(f"   Avg Fitness: {success_metrics.get('average_fitness_score', 0)}")
                print(f"   Total Violations: {success_metrics.get('total_violations', 0)}")
                print(f"   Conflict Free: {success_metrics.get('conflict_free', False)}")
            else:
                print("❌ FIX #2 FAILED: No success metrics found")
            print()
            
            # Check individual division results
            print("📋 Division Results:")
            results_data = result.get('results', {})
            
            for year, year_data in results_data.items():
                if year.startswith('_'):  # Skip metadata
                    continue
                
                print(f"\n   Year: {year}")
                if isinstance(year_data, dict):
                    for division, div_data in year_data.items():
                        if isinstance(div_data, dict):
                            success = div_data.get('success', False)
                            fitness = div_data.get('fitness_score', 'N/A')
                            violations = div_data.get('total_violations', 'N/A')
                            sessions = div_data.get('sessions_count', 0)
                            
                            status_icon = "✅" if success else "❌"
                            print(f"      {status_icon} Division {division}:")
                            print(f"         Sessions: {sessions}")
                            print(f"         Fitness: {fitness}")
                            print(f"         Violations: {violations}")
                            
                            # Check violations breakdown
                            if 'violations' in div_data and isinstance(div_data['violations'], dict):
                                print(f"         Breakdown:")
                                for v_type, v_count in div_data['violations'].items():
                                    if v_type != 'note' and isinstance(v_count, (int, float)):
                                        print(f"            - {v_type}: {v_count}")
            
            print()
            
            # Check conflicts report
            conflicts = result.get('conflicts_report', {})
            teacher_conflicts = conflicts.get('teacher_conflicts', [])
            room_conflicts = conflicts.get('room_conflicts', [])
            
            print("🔍 Conflicts Report:")
            print(f"   Teacher Conflicts: {len(teacher_conflicts)}")
            print(f"   Room Conflicts: {len(room_conflicts)}")
            
            if len(teacher_conflicts) == 0 and len(room_conflicts) == 0:
                print("   ✅ No conflicts detected!")
            else:
                print("   ⚠️  Conflicts found (may need investigation)")
                if teacher_conflicts:
                    print(f"\n   Teacher Conflicts (showing first 3):")
                    for conflict in teacher_conflicts[:3]:
                        print(f"      - {conflict}")
            
            print()
            print("=" * 80)
            print("🎯 TEST SUMMARY")
            print("=" * 80)
            
            # Summary checklist
            checks = {
                "Algorithm is FIXED version": "FIXED" in algorithm or "v2.0" in algorithm,
                "Success metrics visible": bool(success_metrics),
                "Fitness scores present": any(
                    div_data.get('fitness_score') is not None 
                    for year_data in results_data.values() 
                    if isinstance(year_data, dict)
                    for div_data in year_data.values()
                    if isinstance(div_data, dict)
                ),
                "No conflicts": len(teacher_conflicts) == 0 and len(room_conflicts) == 0
            }
            
            for check, passed in checks.items():
                icon = "✅" if passed else "❌"
                print(f"{icon} {check}")
            
            print()
            
            # Overall result
            if all(checks.values()):
                print("🎉 ALL CHECKS PASSED! Fixed algorithm is working correctly!")
            else:
                print("⚠️  Some checks failed. Review the output above.")
            
            print()
            print("💡 Next steps:")
            print("   1. Check project work sessions (should have NO teacher)")
            print("   2. Verify workload balance in database")
            print("   3. Test via frontend wizard")
            print("   4. Review TESTING_GUIDE.md for detailed tests")
            
        else:
            print(f"❌ ERROR: Request failed with status {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to Django server")
        print("   Make sure the server is running at http://127.0.0.1:8000")
        print("   Run: python manage.py runserver")
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out (took more than 60 seconds)")
        print("   The algorithm might be taking too long")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
    
    print()
    print("=" * 80)

if __name__ == "__main__":
    test_algorithm()
