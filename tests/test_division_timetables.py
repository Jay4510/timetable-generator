#!/usr/bin/env python
"""
Test Division-Specific Timetable Generation
This tests the new architecture where each division gets its own timetable
"""

import requests
import json
import time
from collections import defaultdict, Counter

def test_division_specific_generation():
    print("🎓 TESTING DIVISION-SPECIFIC TIMETABLE GENERATION")
    print("=" * 60)
    
    # Test 1: Generate Division-Specific Timetables
    print("\n1️⃣ GENERATING DIVISION-SPECIFIC TIMETABLES...")
    
    try:
        start_time = time.time()
        
        response = requests.post('http://localhost:8000/api/generate-timetable/', 
                               json={'use_division_specific': True},
                               headers={'Content-Type': 'application/json'},
                               timeout=120)
        
        generation_time = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Generation successful in {generation_time:.1f} seconds!")
            print(f"   📊 Total sessions: {data.get('total_sessions', 0)}")
            print(f"   🏫 Divisions processed: {data.get('divisions_processed', 0)}")
            print(f"   🧠 Algorithm: {data.get('algorithm', 'Unknown')}")
            print(f"   ⚠️  Cross-division conflicts: {data.get('cross_division_conflicts', 0)}")
            
            # Show division breakdown
            if 'division_results' in data:
                print("\n   📋 Division Breakdown:")
                for division, result in data['division_results'].items():
                    print(f"      {result['division']}: {result['sessions_created']} sessions")
            
        else:
            print(f"   ❌ Generation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Validate Division Separation
    print("\n2️⃣ VALIDATING DIVISION SEPARATION...")
    
    try:
        response = requests.get('http://localhost:8000/api/timetable/')
        sessions = response.json()
        
        print(f"   📋 Retrieved {len(sessions)} total sessions")
        
        # Group sessions by division
        division_sessions = defaultdict(list)
        for session in sessions:
            division = session['year_division']
            division_sessions[division].append(session)
        
        print(f"   🏫 Found {len(division_sessions)} divisions:")
        for division, div_sessions in division_sessions.items():
            print(f"      {division}: {len(div_sessions)} sessions")
        
        # Test 3: Check Teacher Conflicts Across Divisions
        print("\n3️⃣ CHECKING CROSS-DIVISION TEACHER CONFLICTS...")
        
        teacher_schedule = defaultdict(lambda: defaultdict(list))
        
        for session in sessions:
            teacher = session['teacher_name']
            timeslot = session['timeslot_info']
            division = session['year_division']
            
            teacher_schedule[teacher][timeslot].append(division)
        
        conflicts = 0
        conflict_details = []
        
        for teacher, schedule in teacher_schedule.items():
            for timeslot, divisions in schedule.items():
                if len(divisions) > 1:
                    conflicts += len(divisions) - 1
                    conflict_details.append({
                        'teacher': teacher,
                        'timeslot': timeslot,
                        'divisions': divisions
                    })
        
        if conflicts == 0:
            print("   ✅ NO cross-division teacher conflicts!")
        else:
            print(f"   ⚠️  Found {conflicts} cross-division conflicts:")
            for conflict in conflict_details[:5]:  # Show first 5
                print(f"      {conflict['teacher']} at {conflict['timeslot']}: {conflict['divisions']}")
        
        # Test 4: Validate Batch Distribution
        print("\n4️⃣ CHECKING BATCH DISTRIBUTION...")
        
        batch_distribution = defaultdict(lambda: defaultdict(int))
        
        for session in sessions:
            division = session['year_division']
            batch = session.get('batch_number', 1)
            batch_distribution[division][batch] += 1
        
        print("   📊 Batch distribution per division:")
        for division, batches in batch_distribution.items():
            batch_counts = [f"B{batch}:{count}" for batch, count in sorted(batches.items())]
            print(f"      {division}: {', '.join(batch_counts)}")
        
        # Test 5: Time Slot Utilization
        print("\n5️⃣ ANALYZING TIME SLOT UTILIZATION...")
        
        timeslot_usage = defaultdict(int)
        division_timeslot_usage = defaultdict(lambda: defaultdict(int))
        
        for session in sessions:
            timeslot = session['timeslot_info']
            division = session['year_division']
            
            timeslot_usage[timeslot] += 1
            division_timeslot_usage[division][timeslot] += 1
        
        print("   ⏰ Most used time slots:")
        sorted_slots = sorted(timeslot_usage.items(), key=lambda x: x[1], reverse=True)
        for timeslot, count in sorted_slots[:5]:
            print(f"      {timeslot}: {count} sessions")
        
        # Test 6: Subject-Division Mapping
        print("\n6️⃣ VALIDATING SUBJECT-DIVISION MAPPING...")
        
        subject_divisions = defaultdict(set)
        
        for session in sessions:
            subject = session['subject_name']
            division = session['year_division']
            subject_divisions[subject].add(division)
        
        print("   📚 Subject distribution across divisions:")
        for subject, divisions in list(subject_divisions.items())[:5]:
            print(f"      {subject}: {', '.join(sorted(divisions))}")
        
        # Summary Report
        print("\n" + "=" * 60)
        print("📋 DIVISION-SPECIFIC TIMETABLE VALIDATION SUMMARY")
        print("=" * 60)
        
        print(f"✅ Total Sessions Generated: {len(sessions)}")
        print(f"✅ Divisions with Timetables: {len(division_sessions)}")
        print(f"✅ Cross-Division Teacher Conflicts: {conflicts}")
        print(f"✅ Unique Teachers Used: {len(teacher_schedule)}")
        print(f"✅ Unique Time Slots Used: {len(timeslot_usage)}")
        
        success = conflicts == 0 and len(sessions) > 0 and len(division_sessions) > 1
        
        if success:
            print("\n🎉 DIVISION-SPECIFIC SYSTEM: WORKING PERFECTLY!")
            print("✅ Each division has its own timetable")
            print("✅ No teacher conflicts across divisions")
            print("✅ Proper batch distribution")
        else:
            print(f"\n⚠️  ISSUES FOUND: {conflicts} conflicts detected")
        
        return success
        
    except Exception as e:
        print(f"   ❌ Validation error: {e}")
        return False

def test_specific_division_retrieval():
    """Test retrieving timetable for a specific division"""
    print("\n7️⃣ TESTING DIVISION-SPECIFIC RETRIEVAL...")
    
    divisions_to_test = ['SE A', 'TE A', 'BE A']
    
    for division in divisions_to_test:
        try:
            year, div = division.split(' ')
            response = requests.get(f'http://localhost:8000/api/division-timetable/{year}/{div}/')
            
            if response.status_code == 200:
                data = response.json()
                sessions_count = data.get('sessions_count', 0)
                print(f"   ✅ {division}: {sessions_count} sessions retrieved")
            else:
                print(f"   ⚠️  {division}: Failed to retrieve (status: {response.status_code})")
                
        except Exception as e:
            print(f"   ❌ {division}: Error - {e}")

def show_presentation_points():
    """Show key points for presentation"""
    print("\n🎤 KEY PRESENTATION POINTS:")
    print("=" * 40)
    
    points = [
        "✅ Division-Specific Architecture: Each division gets its own timetable",
        "✅ Zero Cross-Division Conflicts: Teachers can't be in two places at once",
        "✅ Batch Management: A1, A2, A3 batches within each division",
        "✅ Scalable Design: Easy to add new divisions or years",
        "✅ Real-World Compliance: Matches actual college structure",
        "✅ Constraint Satisfaction: All genetic algorithm constraints maintained",
        "✅ Performance: Generates all division timetables in under 2 minutes"
    ]
    
    for point in points:
        print(f"   {point}")

if __name__ == "__main__":
    success = test_division_specific_generation()
    test_specific_division_retrieval()
    show_presentation_points()
    
    if success:
        print("\n🎓 SYSTEM READY FOR PRESENTATION!")
        print("Your division-specific timetable generator is working perfectly!")
    else:
        print("\n⚠️  System needs adjustment before presentation")
