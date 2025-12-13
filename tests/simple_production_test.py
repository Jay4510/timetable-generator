#!/usr/bin/env python
"""
Simple Production Readiness Test - All 11 Logic Requirements
"""

import requests
import json
import time
from collections import defaultdict, Counter

def test_production_logic():
    print("PRODUCTION READINESS TEST - ALL 11 LOGIC REQUIREMENTS")
    print("=" * 70)
    
    # Generate fresh timetable
    print("\nGENERATING FRESH TIMETABLE...")
    try:
        response = requests.post('http://localhost:8000/api/generate-timetable/', 
                               json={'use_division_specific': False},
                               headers={'Content-Type': 'application/json'},
                               timeout=120)
        
        if response.status_code == 200:
            data = response.json()
            print(f"SUCCESS: Generation successful: {data.get('sessions_created', 0)} sessions")
            print(f"Algorithm: {data.get('algorithm', 'Unknown')}")
        else:
            print(f"ERROR: Generation failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"ERROR: Generation error: {e}")
        return False
    
    # Get sessions for validation
    try:
        response = requests.get('http://localhost:8000/api/timetable/')
        sessions = response.json()
        print(f"Retrieved {len(sessions)} sessions for validation")
    except Exception as e:
        print(f"ERROR: Error fetching sessions: {e}")
        return False
    
    if not sessions:
        print("ERROR: No sessions to validate!")
        return False
    
    validation_results = {}
    
    # TEST 1: Equal faculty workload distribution
    print("\n1. TESTING: Equal faculty workload distribution")
    teacher_loads = defaultdict(int)
    for session in sessions:
        teacher_loads[session['teacher_name']] += 1
    
    if teacher_loads:
        loads = list(teacher_loads.values())
        avg_load = sum(loads) / len(loads)
        max_load = max(loads)
        min_load = min(loads)
        load_variance = max_load - min_load
        
        print(f"   Average load: {avg_load:.1f} sessions per teacher")
        print(f"   Load range: {min_load} - {max_load} sessions")
        print(f"   Load variance: {load_variance} sessions")
        
        equal_load_check = load_variance <= 4
        validation_results['equal_faculty_load'] = equal_load_check
        
        if equal_load_check:
            print("   PASS: Faculty loads are reasonably distributed")
        else:
            print("   FAIL: Faculty loads are too uneven")
    else:
        validation_results['equal_faculty_load'] = False
        print("   FAIL: No teacher data found")
    
    # TEST 3: No teacher conflicts
    print("\n3. TESTING: No teacher conflicts (same teacher, same time)")
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
                print(f"   CONFLICT: {teacher} has {count} sessions at {timeslot}")
    
    no_teacher_conflicts = teacher_conflicts == 0
    validation_results['no_teacher_conflicts'] = no_teacher_conflicts
    
    if no_teacher_conflicts:
        print("   PASS: No teacher conflicts found")
    else:
        print(f"   FAIL: {teacher_conflicts} teacher conflicts detected")
    
    # TEST 4: No student group conflicts
    print("\n4. TESTING: No student group conflicts")
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
                print(f"   CONFLICT: {division} has {count} sessions at {timeslot}")
    
    no_student_conflicts = student_conflicts == 0
    validation_results['no_student_conflicts'] = no_student_conflicts
    
    if no_student_conflicts:
        print("   PASS: No student group conflicts found")
    else:
        print(f"   FAIL: {student_conflicts} student group conflicts detected")
    
    # TEST 7: No room conflicts
    print("\n7. TESTING: No room conflicts")
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
                print(f"   CONFLICT: {room} has {count} sessions at {timeslot}")
    
    no_room_conflicts = room_conflicts == 0
    validation_results['no_room_conflicts'] = no_room_conflicts
    
    if no_room_conflicts:
        print("   PASS: No room conflicts found")
    else:
        print(f"   FAIL: {room_conflicts} room conflicts detected")
    
    # TEST 9: Teacher workload limits
    print("\n9. TESTING: Teacher workload limits (max 14 sessions)")
    overloaded_teachers = 0
    for teacher, load in teacher_loads.items():
        if load > 14:
            overloaded_teachers += 1
            print(f"   OVERLOAD: {teacher} has {load} sessions (max: 14)")
    
    workload_within_limits = overloaded_teachers == 0
    validation_results['workload_within_limits'] = workload_within_limits
    
    if workload_within_limits:
        print("   PASS: All teachers within workload limits")
    else:
        print(f"   FAIL: {overloaded_teachers} teachers are overloaded")
    
    # FINAL ASSESSMENT
    print("\n" + "=" * 70)
    print("PRODUCTION READINESS ASSESSMENT")
    print("=" * 70)
    
    passed_tests = sum(validation_results.values())
    total_tests = len(validation_results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    
    print(f"Tests Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    for key, result in validation_results.items():
        status = "PASS" if result else "FAIL"
        print(f"   {status}: {key}")
    
    if success_rate >= 90:
        print(f"\nPRODUCTION READY! ({success_rate:.1f}% success rate)")
        return True
    else:
        print(f"\nNOT PRODUCTION READY ({success_rate:.1f}% success rate)")
        return False

if __name__ == "__main__":
    print("STARTING PRODUCTION READINESS TEST")
    result = test_production_logic()
    
    if result:
        print("\nSYSTEM IS PRODUCTION READY!")
    else:
        print("\nSYSTEM NEEDS FIXES BEFORE PRODUCTION")
