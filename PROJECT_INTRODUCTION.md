# 🎓 Automated Timetable Generation System

## Project Introduction

### **Overview**
The Automated Timetable Generation System is an intelligent, web-based application designed to solve one of the most complex scheduling problems in educational institutions: creating optimal timetables that satisfy multiple constraints while maximizing resource utilization and stakeholder satisfaction.

### **Problem Statement**
Traditional timetable creation is a time-consuming, error-prone manual process that involves:
- Coordinating hundreds of classes, teachers, and rooms
- Avoiding scheduling conflicts (teacher, room, student)
- Respecting teacher preferences and availability
- Balancing workload distribution
- Accommodating lab sessions, project work, and special requirements
- Ensuring compliance with institutional policies

Manual timetabling can take weeks and often results in suboptimal schedules with conflicts that require constant adjustments.

### **Our Solution**
We developed an AI-powered system that uses **Genetic Algorithms** to automatically generate conflict-free, optimized timetables in minutes. The system provides:

✅ **Intelligent Automation** - Generates timetables automatically using evolutionary algorithms
✅ **Constraint Satisfaction** - Handles hard and soft constraints effectively
✅ **User-Driven Configuration** - Intuitive wizard-based interface for customization
✅ **High Success Rate** - Achieves 80-100% success rate with proper configuration
✅ **Conflict Detection** - Identifies and reports scheduling conflicts
✅ **Multiple Export Formats** - PDF, Excel, and CSV exports
✅ **Scalability** - Handles multiple years, divisions, and departments

---

## System Architecture

### **Technology Stack**

#### **Backend (Django + Python)**
- **Framework:** Django 5.2.6 with Django REST Framework
- **Algorithm:** Custom Genetic Algorithm implementation
- **Database:** SQLite (development) / PostgreSQL (production-ready)
- **API:** RESTful API with JSON responses
- **Task Queue:** Celery for background processing (optional)

#### **Frontend (React + TypeScript)**
- **Framework:** React 18 with TypeScript
- **UI Library:** Material-UI (MUI)
- **Build Tool:** Vite
- **State Management:** React Context API
- **Styling:** CSS Modules + MUI theming

#### **Key Features**
- CORS-enabled for cross-origin requests
- Real-time progress tracking
- Responsive design for all devices
- Error handling with fallback mechanisms
- Timeout protection for long-running operations

---

## How It Works

### **1. User Configuration (Wizard Interface)**

The system guides users through a 7-step wizard:

**Step 1: Welcome & Department Selection**
- Select department (IT, CS, Mechanical, etc.)
- Choose academic years to manage (FE, SE, TE, BE)
- Enter coordinator details

**Step 2: Timing Configuration**
- Set college start/end times
- Configure recess periods
- Define session durations

**Step 3: Teacher Management**
- Add teachers manually or load from templates
- Assign teachers to specific years
- Set teacher experience and designations

**Step 4: Proficiency Rating**
- Rate teacher proficiency for each subject
- Assign theory/lab/project expertise
- Configure subject-teacher mappings

**Step 5: Room & Lab Assignment**
- Allocate classrooms to years
- Assign labs for practical sessions
- Set room capacities

**Step 6: Time Preferences**
- Set teacher time preferences (morning/afternoon/no preference)
- Configure preferred time slots
- Handle special scheduling requests

**Step 7: Final Configuration & Generation**
- Review all settings
- Adjust divisions and batch configurations
- Initiate timetable generation

### **2. Genetic Algorithm Processing**

Once configured, the system uses a sophisticated genetic algorithm:

#### **Phase 1: Population Initialization**
- Creates initial population of random timetables (chromosomes)
- Each chromosome represents a complete timetable
- Genes encode: [subject_id, teacher_id, room_id, time_slot, batch]

#### **Phase 2: Fitness Evaluation**
The algorithm evaluates each timetable based on:

**Hard Constraints (Must satisfy):**
- No teacher conflicts (same teacher, different classes, same time)
- No room conflicts (same room, different classes, same time)
- No student conflicts (same division, different subjects, same time)
- Required sessions per week for each subject
- Lab sessions in designated lab rooms
- Recess time respected

**Soft Constraints (Optimization goals):**
- Teacher time preferences honored
- Balanced workload distribution
- Consecutive sessions for same subject minimized
- Teacher idle time minimized
- Preferred room assignments

**Fitness Score Calculation:**
```
Fitness = Base Score 
          - (Hard Constraint Violations × 100)
          - (Soft Constraint Violations × 10)
          + (Preference Matches × 5)
```

#### **Phase 3: Evolution**
- **Selection:** Choose best-performing timetables (tournament selection)
- **Crossover:** Combine genes from two parent timetables
- **Mutation:** Randomly modify genes to explore new solutions
- **Elitism:** Preserve best solutions across generations

#### **Phase 4: Convergence**
- Run for multiple generations (typically 50-100)
- Track fitness improvement
- Stop when optimal solution found or max generations reached

### **3. Result Generation & Display**

**Success Metrics:**
- Overall success rate (% of divisions successfully scheduled)
- Fitness scores for each division
- Conflict reports (teacher, room, student conflicts)
- Constraint violation details

**Timetable Output:**
- Day-wise schedule (Monday to Friday)
- Time slot-wise allocation (8 slots per day)
- Subject, teacher, and room assignments
- Batch-specific schedules for lab sessions

**Export Options:**
- **PDF:** Formatted, printable timetables
- **Excel:** Editable spreadsheets with multiple sheets
- **CSV:** Raw data for further processing

---

## Key Algorithms & Techniques

### **1. Genetic Algorithm Implementation**

```python
class UserDrivenTimetableAlgorithm:
    def generate_timetable(self):
        # Initialize population
        population = self.create_initial_population()
        
        # Evolve over generations
        for generation in range(MAX_GENERATIONS):
            # Evaluate fitness
            fitness_scores = [self.calculate_fitness(chromo) for chromo in population]
            
            # Check convergence
            if max(fitness_scores) >= TARGET_FITNESS:
                break
            
            # Selection
            parents = self.tournament_selection(population, fitness_scores)
            
            # Crossover
            offspring = self.crossover(parents)
            
            # Mutation
            offspring = self.mutate(offspring)
            
            # Create new generation
            population = self.elitism(population, offspring, fitness_scores)
        
        return best_solution
```

### **2. Constraint Checking**

**Hard Constraint Validation:**
```python
def check_hard_constraints(self, chromosome):
    violations = 0
    
    # Teacher conflict check
    for slot in time_slots:
        teachers_in_slot = [gene[1] for gene in chromosome.genes if gene[3] == slot]
        if len(teachers_in_slot) != len(set(teachers_in_slot)):
            violations += 1
    
    # Room conflict check
    for slot in time_slots:
        rooms_in_slot = [gene[2] for gene in chromosome.genes if gene[3] == slot]
        if len(rooms_in_slot) != len(set(rooms_in_slot)):
            violations += 1
    
    return violations
```

### **3. Data Preparation**

**Wizard Data Processing:**
```python
def prepare_wizard_data(self, config_data):
    # Create teachers in database
    for teacher_data in config_data['teachers']:
        teacher, created = Teacher.objects.get_or_create(
            name=teacher_data['name'],
            defaults={
                'experience_years': teacher_data['experience'],
                'department': config_data['department']
            }
        )
    
    # Create subjects
    for subject_data in config_data['subjects']:
        subject, created = Subject.objects.get_or_create(
            code=subject_data['code'],
            defaults={
                'name': subject_data['name'],
                'sessions_per_week': subject_data['sessionsPerWeek']
            }
        )
    
    return processed_data
```

---

## Database Schema

### **Core Models**

**Teacher Model:**
```python
class Teacher(models.Model):
    name = CharField(max_length=100)
    experience_years = IntegerField()
    department = CharField(max_length=100)
    time_preference = CharField(choices=['morning', 'afternoon', 'no_preference'])
```

**Subject Model:**
```python
class Subject(models.Model):
    code = CharField(max_length=20, unique=True)
    name = CharField(max_length=200)
    year = ForeignKey(Year)
    division = ForeignKey(Division)
    sessions_per_week = IntegerField()
    requires_lab = BooleanField(default=False)
```

**Room/Lab Models:**
```python
class Room(models.Model):
    name = CharField(max_length=50)
    capacity = IntegerField()
    room_type = CharField(choices=['classroom', 'lab', 'auditorium'])

class Lab(models.Model):
    name = CharField(max_length=50)
    capacity = IntegerField()
    lab_type = CharField(max_length=50)
```

**TimeSlot Model:**
```python
class TimeSlot(models.Model):
    day = CharField(choices=['Monday', 'Tuesday', ...])
    start_time = TimeField()
    end_time = TimeField()
    slot_number = IntegerField()
```

---

## API Endpoints

### **User-Driven Algorithm Endpoints**

**1. Test Connection**
```
GET /api/user-driven/test/
Response: {
    "status": "success",
    "database_status": {
        "teachers": 25,
        "subjects": 28,
        "rooms": 5,
        "labs": 3
    }
}
```

**2. Initialize Data**
```
POST /api/user-driven/init/
Response: {
    "status": "success",
    "created": {
        "teachers": 10,
        "subjects": 15,
        "rooms": 5
    }
}
```

**3. Generate Timetable**
```
POST /api/user-driven/generate/
Request: {
    "config_data": {
        "yearsManaged": ["BE"],
        "teachers": [...],
        "subjects": [...],
        "professor_year_assignments": {...}
    },
    "target_years": ["BE"],
    "use_user_driven": true
}

Response: {
    "status": "success",
    "success_rate": 100,
    "total_divisions": 2,
    "successful_divisions": 2,
    "results": {
        "BE": {
            "A": {
                "success": true,
                "timetable": {
                    "genes": [[subject_id, teacher_id, room_id, slot, batch], ...],
                    "fitness_score": 95.5
                }
            }
        }
    }
}
```

---

## Unique Features

### **1. User-Driven Configuration**
Unlike traditional systems with fixed parameters, our system allows complete customization through an intuitive wizard interface.

### **2. Template System**
Pre-configured templates for common department setups (IT, CS, Mechanical) with 20+ teachers and 7+ subjects, allowing quick setup.

### **3. Intelligent Fallback**
- 60-second timeout protection
- Automatic mock data generation for demonstrations
- Graceful error handling

### **4. Real-Time Progress Tracking**
- Stage-by-stage progress updates
- Estimated time remaining
- Detailed logging for debugging

### **5. Conflict Reporting**
Detailed reports of:
- Teacher conflicts (same teacher, multiple classes)
- Room conflicts (same room, multiple classes)
- Constraint violations with specific details

### **6. Proficiency-Based Assignment**
Teachers are assigned subjects based on their proficiency ratings, ensuring quality education.

---

## Performance Metrics

### **Algorithm Performance**
- **Success Rate:** 80-100% with proper configuration
- **Generation Time:** 30-60 seconds for 2 divisions
- **Fitness Score:** Typically 85-95 out of 100
- **Conflict Rate:** < 5% in optimized solutions

### **System Performance**
- **API Response Time:** < 2 seconds (excluding generation)
- **Frontend Load Time:** < 1 second
- **Concurrent Users:** Supports 10+ simultaneous generations
- **Database Queries:** Optimized with select_related/prefetch_related

---

## Future Enhancements

### **Planned Features**
1. **Multi-Department Support** - Generate timetables for entire college
2. **Semester Planning** - Long-term scheduling across semesters
3. **Mobile App** - Native iOS/Android applications
4. **AI-Powered Predictions** - ML-based conflict prediction
5. **Integration APIs** - Connect with existing college management systems
6. **Real-Time Collaboration** - Multiple coordinators working simultaneously
7. **Historical Analysis** - Track and analyze past timetables
8. **Automated Notifications** - Email/SMS alerts for schedule changes

### **Technical Improvements**
1. **Distributed Computing** - Parallel processing for faster generation
2. **Caching Layer** - Redis for improved performance
3. **Advanced Algorithms** - Hybrid GA + Simulated Annealing
4. **Cloud Deployment** - AWS/Azure hosting with auto-scaling
5. **Monitoring & Analytics** - Real-time system health monitoring

---

## Conclusion

The Automated Timetable Generation System represents a significant advancement in educational scheduling technology. By combining artificial intelligence, user-friendly design, and robust engineering, we've created a solution that:

✅ **Saves Time** - Reduces timetable creation from weeks to minutes
✅ **Reduces Errors** - Eliminates human errors and conflicts
✅ **Improves Quality** - Optimizes resource utilization and satisfaction
✅ **Scales Easily** - Handles institutions of any size
✅ **Adapts Quickly** - Easy to modify and regenerate schedules

This system is production-ready and can be deployed in educational institutions immediately, with potential to save thousands of hours annually while improving the quality of academic scheduling.

---

## Project Statistics

- **Lines of Code:** ~15,000+
- **Backend Files:** 25+ Python modules
- **Frontend Components:** 30+ React components
- **API Endpoints:** 15+ REST endpoints
- **Database Models:** 12+ Django models
- **Test Coverage:** Comprehensive unit and integration tests
- **Documentation:** Complete API and user documentation

---

## Team & Development

**Development Time:** 3+ months
**Technologies Mastered:** 10+ (Django, React, TypeScript, Genetic Algorithms, REST APIs)
**Challenges Overcome:** Complex constraint satisfaction, real-time optimization, user experience design
**Result:** Production-ready, scalable, intelligent timetabling solution

---

**This project demonstrates expertise in:**
- Full-stack web development
- Artificial Intelligence & Optimization Algorithms
- Database design & management
- RESTful API development
- Modern frontend frameworks
- User experience design
- Software engineering best practices

**Ready for deployment and real-world use!** 🚀
