# 🧪 TESTING GUIDE - FIXED ALGORITHM v2.0

## ✅ Setup Complete!

**Backend Server:** Running at http://127.0.0.1:8000/
**Algorithm Version:** FIXED v2.0 (user_driven_timetable_algorithm_FIXED.py)
**Status:** Ready for testing

---

## 🎯 WHAT TO TEST

### **Test #1: Project Work Teacher Assignment** (CRITICAL)

**What to check:**
- Generate a timetable with Mini Project or Major Project enabled
- Verify that NO teacher is assigned to project time slots
- Check that teachers are available during project hours

**Steps:**
1. Open frontend: http://localhost:5173 (or your frontend URL)
2. Go through the wizard
3. In "Teacher Time Preferences" step, enable Mini/Major Project
4. Generate timetable
5. Check the generated sessions

**Expected Result:**
```json
// Project work sessions should have:
{
  "subject": "Mini Project",
  "teacher": null,  // ✅ Should be NULL or "No Teacher"
  "room": "Room 101",
  "time_slot": "14:00-15:00"
}
```

**How to verify in database:**
```bash
# In Django shell:
python manage.py shell

from timetable_app.models import Session, Subject

# Find project work sessions
project_sessions = Session.objects.filter(subject__name__icontains='project')
for session in project_sessions:
    print(f"Subject: {session.subject.name}, Teacher: {session.teacher}, Time: {session.timeslot}")
    # Teacher should be None for project work
```

---

### **Test #2: Success Rate Visibility**

**What to check:**
- After generation, success metrics should be displayed
- Should see: success_rate, fitness_score, total_violations

**Steps:**
1. Generate timetable via API or frontend
2. Check the response/display

**Expected Response:**
```json
{
  "status": "success",
  "algorithm": "User-Driven Timetable Algorithm (FIXED v2.0)",
  "success_metrics": {
    "total_divisions": 6,
    "successful_divisions": 6,
    "success_rate": 100.0,  // ✅ Should be visible!
    "average_fitness_score": -25.5,
    "total_violations": 153,
    "conflict_free": false
  },
  "results": {
    "SE": {
      "A": {
        "success": true,
        "fitness_score": -25,  // ✅ Should be visible!
        "total_violations": 25,
        "violations": {
          "teacher_conflicts": 0,
          "room_conflicts": 0,
          "student_conflicts": 0,
          "workload_violations": 10,
          "gap_violations": 15
        }
      }
    }
  }
}
```

**How to test via API:**
```bash
curl -X POST http://127.0.0.1:8000/api/generate-timetable/ \
  -H "Content-Type: application/json" \
  -d '{
    "use_user_driven": true,
    "target_years": ["SE", "TE"]
  }'
```

---

### **Test #3: Workload Balance**

**What to check:**
- Teachers should have similar number of sessions
- No teacher should have 20 sessions while another has 5

**Steps:**
1. Generate timetable
2. Check teacher session counts

**How to verify:**
```bash
# In Django shell:
from timetable_app.models import Session, Teacher
from collections import Counter

# Count sessions per teacher
teacher_loads = Counter()
for session in Session.objects.all():
    if session.teacher:  # Skip project work (null teachers)
        teacher_loads[session.teacher.name] += 1

# Display workload
for teacher, count in teacher_loads.most_common():
    print(f"{teacher}: {count} sessions")

# Check balance
loads = list(teacher_loads.values())
if loads:
    avg = sum(loads) / len(loads)
    min_load = min(loads)
    max_load = max(loads)
    print(f"\nAverage: {avg:.1f}")
    print(f"Range: {min_load} - {max_load}")
    print(f"Deviation: {max_load - min_load}")
    
    # ✅ Should be within 3-6 sessions of each other
    if max_load - min_load <= 6:
        print("✅ BALANCED!")
    else:
        print("⚠️ UNBALANCED")
```

---

### **Test #4: Schedule Gaps**

**What to check:**
- Teachers should have fewer gaps in their schedules
- Students should have more continuous blocks

**How to verify:**
```bash
# In Django shell:
from timetable_app.models import Session, Teacher
from collections import defaultdict

# Check teacher schedule gaps
for teacher in Teacher.objects.all()[:3]:  # Check first 3 teachers
    sessions = Session.objects.filter(teacher=teacher).order_by('timeslot__slot_number')
    
    if sessions:
        slots = [s.timeslot.slot_number for s in sessions]
        gaps = 0
        for i in range(len(slots) - 1):
            gap = slots[i+1] - slots[i]
            if gap > 1:
                gaps += (gap - 1)
        
        print(f"{teacher.name}: {len(slots)} sessions, {gaps} gap slots")
        # ✅ Should have minimal gaps (0-2 is good)
```

---

### **Test #5: Teacher Preferences**

**What to check:**
- Teachers with morning preference should have more morning classes
- Teachers with afternoon preference should have more afternoon classes

**How to verify:**
```bash
# In Django shell:
from timetable_app.models import Session, Teacher
from datetime import time

for teacher in Teacher.objects.all()[:5]:
    sessions = Session.objects.filter(teacher=teacher)
    
    morning_count = 0
    afternoon_count = 0
    
    for session in sessions:
        slot_time = session.timeslot.start_time
        if slot_time < time(13, 0):
            morning_count += 1
        else:
            afternoon_count += 1
    
    print(f"{teacher.name} (Pref: {teacher.time_preference})")
    print(f"  Morning: {morning_count}, Afternoon: {afternoon_count}")
    
    # ✅ Should align with preference
```

---

### **Test #6: Room Capacity**

**What to check:**
- No room should be assigned more students than its capacity

**How to verify:**
```bash
# In Django shell:
from timetable_app.models import Session, Division

violations = []
for session in Session.objects.all():
    if session.room:
        division = session.subject.division
        student_count = division.student_count
        room_capacity = session.room.capacity
        
        if student_count > room_capacity:
            violations.append({
                'session': str(session),
                'students': student_count,
                'capacity': room_capacity,
                'overflow': student_count - room_capacity
            })

if violations:
    print(f"⚠️ Found {len(violations)} capacity violations:")
    for v in violations[:5]:
        print(f"  {v['session']}: {v['students']} students in {v['capacity']} capacity room")
else:
    print("✅ No capacity violations!")
```

---

## 📊 QUICK TEST CHECKLIST

Run through this checklist after generating a timetable:

- [ ] **Project Work**: No teacher assigned to project sessions
- [ ] **Success Rate**: Visible in response (e.g., "95.5%")
- [ ] **Fitness Score**: Visible per division (e.g., "-25")
- [ ] **Violations Breakdown**: Shows individual constraint violations
- [ ] **Workload Balance**: All teachers within 6 sessions of each other
- [ ] **Schedule Gaps**: Minimal gaps (0-2 per teacher)
- [ ] **Preferences**: Teachers mostly in their preferred time slots
- [ ] **Room Capacity**: No overcrowding
- [ ] **No Conflicts**: Zero teacher/room/student double-bookings

---

## 🐛 IF SOMETHING GOES WRONG

### **Revert to Original Algorithm:**

1. **Edit views.py** (3 locations):
```python
# Change from:
from .user_driven_timetable_algorithm_FIXED import UserDrivenTimetableAlgorithm

# Back to:
from .user_driven_timetable_algorithm import UserDrivenTimetableAlgorithm
```

2. **Restart server:**
```bash
# Kill current server
lsof -ti:8000 | xargs kill -9

# Start again
source venv/bin/activate
python manage.py runserver
```

### **Check Logs:**
```bash
# Server logs will show any errors
# Look for lines with "ERROR" or "WARNING"
```

### **Common Issues:**

**Issue:** ImportError for FIXED algorithm
**Solution:** Make sure `user_driven_timetable_algorithm_FIXED.py` exists in `timetable_app/` directory

**Issue:** No success_metrics in response
**Solution:** Check that algorithm is returning `_success_metrics` in results

**Issue:** Teachers still assigned to project work
**Solution:** Clear existing sessions first:
```python
from timetable_app.models import Session
Session.objects.all().delete()
# Then regenerate
```

---

## 📈 EXPECTED IMPROVEMENTS

### **Before (Original Algorithm):**
- ❌ Teachers blocked during project time (4 hours wasted)
- ❌ No success metrics visible
- ❌ Workload range: 5-20 sessions (very unbalanced)
- ❌ Many schedule gaps (3-5 per teacher)
- ❌ Weak preference enforcement (often ignored)

### **After (FIXED Algorithm):**
- ✅ Teachers available during project time
- ✅ Success rate: 95-100% visible
- ✅ Workload range: 11-14 sessions (balanced)
- ✅ Fewer gaps (0-2 per teacher)
- ✅ Strong preference enforcement (mostly respected)

---

## 🎯 COMPARISON TEST

Want to compare old vs new? Here's how:

1. **Generate with FIXED version** (current setup)
   - Note the metrics
   - Export results

2. **Switch to original** (edit views.py imports)
   - Clear sessions: `Session.objects.all().delete()`
   - Generate again
   - Compare metrics

3. **Document differences**
   - Success rate
   - Workload balance
   - Schedule gaps
   - Preference compliance

---

## ✅ SUCCESS CRITERIA

**The fixed algorithm is working correctly if:**

1. ✅ Project work has NO teacher assigned
2. ✅ Success rate is displayed (any percentage)
3. ✅ Fitness scores are visible (negative numbers)
4. ✅ Workload deviation < 6 sessions
5. ✅ Average gaps < 2 per teacher
6. ✅ No capacity violations
7. ✅ No double-booking conflicts

**If all 7 criteria pass → Algorithm is working perfectly!** 🎉

---

## 📞 NEED HELP?

If you encounter issues:
1. Check the server logs for errors
2. Verify the import statements in views.py
3. Make sure FIXED file exists
4. Try clearing sessions and regenerating
5. Compare with original algorithm behavior

**Ready to test!** Open your frontend and generate a timetable! 🚀
