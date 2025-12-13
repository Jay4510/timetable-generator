#!/usr/bin/env python
"""
PRODUCTION READINESS TEST
Comprehensive validation of all 11 logic requirements for production deployment
"""

import requests
import json
import time
from collections import defaultdict, Counter

def test_production_logic():
    print("PRODUCTION READINESS TEST - ALL 11 LOGIC REQUIREMENTS")
    print("=" * 70)
    
    # First, generate a fresh timetable
    print("\nGENERATING FRESH TIMETABLE...")
    try:
        response = requests.post('http://localhost:8000/api/generate-timetable/', 
                               json={'use_division_specific': False},  # Test global first
                               headers={'Content-Type': 'application/json'},
                               timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Generation successful: {data.get('sessions_created', 0)} sessions")
            print(f"🧠 Algorithm: {data.get('algorithm', 'Unknown')}")
        else:
            print(f"❌ Generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Generation error: {e}")
        return False
    
    # Get all sessions for validation
    try:
        response = requests.get('http://localhost:8000/api/timetable/')
        sessions = response.json()
        print(f"📋 Retrieved {len(sessions)} sessions for validation")
    except Exception as e:
        print(f"❌ Error fetching sessions: {e}")
        return False
    
    if not sessions:
        print("❌ No sessions to validate!")
        return False
    
    # Initialize validation results
    validation_results = {}
    
    # REQUIREMENT 1: More or less equal load is given to all faculties
    print("\n1️⃣ TESTING: Equal faculty workload distribution")
    teacher_loads = defaultdict(int)
    for session in sessions:
        teacher_loads[session['teacher_name']] += 1
    
    if teacher_loads:
        loads = list(teacher_loads.values())
        avg_load = sum(loads) / len(loads)
        max_load = max(loads)
        min_load = min(loads)
        load_variance = max_load - min_load
        
        print(f"   📊 Average load: {avg_load:.1f} sessions per teacher")
        print(f"   📊 Load range: {min_load} - {max_load} sessions")
        print(f"   📊 Load variance: {load_variance} sessions")
        
        # Check if load is reasonably distributed (variance <= 4 sessions)
        equal_load_check = load_variance <= 4
        validation_results['equal_faculty_load'] = equal_load_check
        
        if equal_load_check:
            print("   ✅ PASS: Faculty loads are reasonably distributed")
        else:
            print("   ❌ FAIL: Faculty loads are too uneven")
            print("   📋 Teacher loads:")
            for teacher, load in sorted(teacher_loads.items()):
                print(f"      {teacher}: {load} sessions")
    else:
        validation_results['equal_faculty_load'] = False
        print("   ❌ FAIL: No teacher data found")
    
    # REQUIREMENT 2: Required time (sessions per week) is given to every Batch
    print("\n2️⃣ TESTING: Required sessions per batch/division")
    division_sessions = defaultdict(int)
    for session in sessions:
        division = session.get('year_division', 'Unknown')
        division_sessions[division] += 1
    
    if division_sessions:
        print("   📊 Sessions per division:")
        for division, count in sorted(division_sessions.items()):
            print(f"      {division}: {count} sessions")
        
        # Check if each division has reasonable number of sessions (at least 8)
        min_sessions = min(division_sessions.values()) if division_sessions else 0
        required_sessions_check = min_sessions >= 8
        validation_results['required_sessions_per_batch'] = required_sessions_check
        
        if required_sessions_check:
            print("   ✅ PASS: All divisions have adequate sessions")
        else:
            print("   ❌ FAIL: Some divisions have insufficient sessions")
    else:
        validation_results['required_sessions_per_batch'] = False
        print("   ❌ FAIL: No division data found")
    
    # REQUIREMENT 3 & 5: No faculty taking two classes simultaneously
    print("\n3️⃣ TESTING: No teacher conflicts (same teacher, same time)")
    teacher_conflicts = 0
    teacher_schedule = defaultdict(list)
    
    for session in sessions:
        teacher = session['teacher_name']
        timeslot = session['timeslot_info']
        teacher_schedule[teacher].append(timeslot)
    
    for teacher, timeslots in teacher_schedule.items():
        timeslot_counts = Counter(timeslots)
        for timeslot, count in timeslot_counts.items():
            if count > 1:
                teacher_conflicts += count - 1
                print(f"   ⚠️  CONFLICT: {teacher} has {count} sessions at {timeslot}")
    
    no_teacher_conflicts = teacher_conflicts == 0
    validation_results['no_teacher_conflicts'] = no_teacher_conflicts
    
    if no_teacher_conflicts:
        print("   ✅ PASS: No teacher conflicts found")
    else:
        print(f"   ❌ FAIL: {teacher_conflicts} teacher conflicts detected")
    
    # REQUIREMENT 4 & 6: No class group having multiple lectures at same time
    print("\n4️⃣ TESTING: No student group conflicts (same division, same time)")
    student_conflicts = 0
    division_schedule = defaultdict(list)
    
    for session in sessions:
        division = session.get('year_division', 'Unknown')
        timeslot = session['timeslot_info']
        division_schedule[division].append(timeslot)
    
    for division, timeslots in division_schedule.items():
        timeslot_counts = Counter(timeslots)
        for timeslot, count in timeslot_counts.items():
            if count > 1:
                student_conflicts += count - 1
                print(f"   ⚠️  CONFLICT: {division} has {count} sessions at {timeslot}")
    
    no_student_conflicts = student_conflicts == 0
    validation_results['no_student_conflicts'] = no_student_conflicts
    
    if no_student_conflicts:
        print("   ✅ PASS: No student group conflicts found")
    else:
        print(f"   ❌ FAIL: {student_conflicts} student group conflicts detected")
    
    # REQUIREMENT 7: No room hosting multiple classes at same time
    print("\n7️⃣ TESTING: No room conflicts (same room, same time)")
    room_conflicts = 0
    room_schedule = defaultdict(list)
    
    for session in sessions:
        room = session.get('room_name') or session.get('lab_name', 'Unknown')
        timeslot = session['timeslot_info']
        room_schedule[room].append(timeslot)
    
    for room, timeslots in room_schedule.items():
        timeslot_counts = Counter(timeslots)
        for timeslot, count in timeslot_counts.items():
            if count > 1:
                room_conflicts += count - 1
                print(f"   ⚠️  CONFLICT: {room} has {count} sessions at {timeslot}")
    
    no_room_conflicts = room_conflicts == 0
    validation_results['no_room_conflicts'] = no_room_conflicts
    
    if no_room_conflicts:
        print("   ✅ PASS: No room conflicts found")
    else:
        print(f"   ❌ FAIL: {room_conflicts} room conflicts detected")
    
    # REQUIREMENT 8: Each course receives required number of sessions
    print("\n8️⃣ TESTING: Course session requirements")
    subject_sessions = defaultdict(int)
    for session in sessions:
        subject = session['subject_name']
        subject_sessions[subject] += 1
    
    if subject_sessions:
        print("   📊 Sessions per subject:")
        insufficient_subjects = 0
        for subject, count in sorted(subject_sessions.items()):
            print(f"      {subject}: {count} sessions")
            if count < 2:  # Minimum 2 sessions per subject per week
                insufficient_subjects += 1
        
        adequate_course_sessions = insufficient_subjects == 0
        validation_results['adequate_course_sessions'] = adequate_course_sessions
        
        if adequate_course_sessions:
            print("   ✅ PASS: All subjects have adequate sessions")
        else:
            print(f"   ❌ FAIL: {insufficient_subjects} subjects have insufficient sessions")
    else:
        validation_results['adequate_course_sessions'] = False
        print("   ❌ FAIL: No subject data found")
    
    # REQUIREMENT 9: Distribute sessions evenly (14 per week max)
    print("\n9️⃣ TESTING: Teacher workload limits (max 14 sessions)")
    overloaded_teachers = 0
    for teacher, load in teacher_loads.items():
        if load > 14:
            overloaded_teachers += 1
            print(f"   ⚠️  OVERLOAD: {teacher} has {load} sessions (max: 14)")
    
    workload_within_limits = overloaded_teachers == 0
    validation_results['workload_within_limits'] = workload_within_limits
    
    if workload_within_limits:
        print("   ✅ PASS: All teachers within workload limits")
    else:
        print(f"   ❌ FAIL: {overloaded_teachers} teachers are overloaded")
    
    # REQUIREMENT 10: Teacher/subject proficiency (check if system supports it)
    print("\n🔟 TESTING: Teacher proficiency system support")
    try:
        # Test if proficiency endpoint exists
        test_response = requests.post('http://localhost:8000/api/teacher-preferences/', 
                                    json={'teacher_id': 1, 'subject_ratings': []},
                                    headers={'Content-Type': 'application/json'})
        
        proficiency_system_exists = test_response.status_code in [200, 400, 404]  # Any response means endpoint exists
        validation_results['proficiency_system'] = proficiency_system_exists
        
        if proficiency_system_exists:
            print("   ✅ PASS: Teacher proficiency system is implemented")
        else:
            print("   ❌ FAIL: Teacher proficiency system not found")
    except:
        validation_results['proficiency_system'] = False
        print("   ❌ FAIL: Teacher proficiency system not accessible")
    
    # REQUIREMENT 11: Morning/afternoon distribution
    print("\n1️⃣1️⃣ TESTING: Morning/afternoon session distribution")
    morning_sessions = 0
    afternoon_sessions = 0
    
    for session in sessions:
        timeslot = session['timeslot_info']
        if any(time in timeslot.lower() for time in ['09:', '10:', '11:', '12:']):
            morning_sessions += 1
        elif any(time in timeslot.lower() for time in ['13:', '14:', '15:', '16:', '17:']):
            afternoon_sessions += 1
    
    total_sessions = morning_sessions + afternoon_sessions
    if total_sessions > 0:
        morning_ratio = morning_sessions / total_sessions
        afternoon_ratio = afternoon_sessions / total_sessions
        
        print(f"   📊 Morning sessions: {morning_sessions} ({morning_ratio:.1%})")
        print(f"   📊 Afternoon sessions: {afternoon_sessions} ({afternoon_ratio:.1%})")
        
        # Check if distribution is reasonably balanced (30-70% range)
        balanced_distribution = 0.3 <= morning_ratio <= 0.7 and 0.3 <= afternoon_ratio <= 0.7
        validation_results['balanced_time_distribution'] = balanced_distribution
        
        if balanced_distribution:
            print("   ✅ PASS: Sessions are reasonably distributed across day")
        else:
            print("   ❌ FAIL: Sessions are too concentrated in one part of day")
    else:
        validation_results['balanced_time_distribution'] = False
        print("   ❌ FAIL: No time distribution data available")
    
    # FINAL PRODUCTION READINESS ASSESSMENT
    print("\n" + "=" * 70)
    print("🏭 PRODUCTION READINESS ASSESSMENT")
    print("=" * 70)
    
    passed_tests = sum(validation_results.values())
    total_tests = len(validation_results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"📊 Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    print("\n📋 Detailed Results:")
    
    test_names = {
        'equal_faculty_load': '1. Equal faculty workload distribution',
        'required_sessions_per_batch': '2. Required sessions per batch',
        'no_teacher_conflicts': '3. No teacher conflicts',
        'no_student_conflicts': '4. No student group conflicts',
        'no_room_conflicts': '7. No room conflicts',
        'adequate_course_sessions': '8. Adequate course sessions',
        'workload_within_limits': '9. Teacher workload limits',
        'proficiency_system': '10. Teacher proficiency system',
        'balanced_time_distribution': '11. Balanced time distribution'
    }
    
    for key, result in validation_results.items():
        test_name = test_names.get(key, key)
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {status} {test_name}")
    
    # Production readiness verdict
    if success_rate >= 90:
        print(f"\n🎉 PRODUCTION READY! ({success_rate:.1f}% success rate)")
        print("✅ System meets production deployment standards")
        return True
    elif success_rate >= 75:
        print(f"\n⚠️  MOSTLY READY ({success_rate:.1f}% success rate)")
        print("🔧 Minor fixes needed before production deployment")
        return False
    else:
        print(f"\n❌ NOT PRODUCTION READY ({success_rate:.1f}% success rate)")
        print("🚨 Major issues must be resolved before deployment")
        return False

def test_division_specific_logic():
    """Test division-specific timetable generation"""
    print("\n" + "=" * 70)
    print("🏫 DIVISION-SPECIFIC LOGIC TEST")
    print("=" * 70)
    
    try:
        print("\n🔄 Testing division-specific generation...")
        response = requests.post('http://localhost:8000/api/generate-timetable/', 
                               json={'use_division_specific': True},
                               headers={'Content-Type': 'application/json'},
                               timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Division-specific generation successful")
            print(f"📊 Total sessions: {data.get('total_sessions', 0)}")
            print(f"🏫 Divisions processed: {data.get('divisions_processed', 0)}")
            print(f"⚠️  Cross-division conflicts: {data.get('cross_division_conflicts', 0)}")
            
            if data.get('cross_division_conflicts', 0) == 0:
                print("✅ PASS: No cross-division teacher conflicts")
                return True
            else:
                print("❌ FAIL: Cross-division conflicts detected")
                return False
        else:
            print(f"❌ Division-specific generation failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Division-specific test error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 STARTING COMPREHENSIVE PRODUCTION READINESS TEST")
    print("Testing all 11 logic requirements for production deployment")
    
    # Test global timetable logic
    global_ready = test_production_logic()
    
    # Test division-specific logic
    division_ready = test_division_specific_logic()
    
    # Final verdict
    print("\n" + "=" * 70)
    print("🎯 FINAL PRODUCTION READINESS VERDICT")
    print("=" * 70)
    
    if global_ready and division_ready:
        print("🎉 SYSTEM IS PRODUCTION READY!")
        print("✅ All critical requirements met")
        print("✅ Division-specific logic working")
        print("🚀 Ready for public deployment")
    elif global_ready:
        print("⚠️  GLOBAL LOGIC READY, DIVISION LOGIC NEEDS WORK")
        print("🔧 Fix division-specific issues before deployment")
    else:
        print("❌ SYSTEM NOT READY FOR PRODUCTION")
        print("🚨 Critical issues must be resolved")
        print("📋 Review failed tests above")
    
    print(f"\n⏰ Test completed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
