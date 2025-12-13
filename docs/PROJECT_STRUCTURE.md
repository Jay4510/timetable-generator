# College Timetable Generator - Project Structure

## Backend (Django)

### Main Project Directory
```
timetable_generator/
├── timetable_project/           # Django project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py              # Project settings (PostgreSQL/SQLite config)
│   ├── urls.py                  # Main URL routing
│   └── wsgi.py
├── timetable_app/               # Main Django application
│   ├── __init__.py
│   ├── admin.py                 # Django admin configuration
│   ├── apps.py                  # App configuration
│   ├── models.py                # Database models (Teacher, Year, Division, etc.)
│   ├── views.py                 # API views
│   ├── serializers.py           # DRF serializers
│   ├── genetic_algorithm.py     # Genetic algorithm implementation
│   ├── tests.py                 # Unit tests
│   ├── urls.py                  # App URL routing
│   └── management/              # Custom management commands
│       ├── __init__.py
│       └── commands/
│           ├── __init__.py
│           ├── seed_data.py     # Data seeding command
│           └── create_admin.py  # Admin user creation
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
└── Dockerfile                   # Docker configuration for backend
```

### Database Models
1. **Teacher** - Faculty members with availability and preferences
2. **Year** - Academic years (SE, TE, BE)
3. **Division** - Divisions within years (A, B, C)
4. **Room** - Classrooms with capacity and type
5. **Lab** - Laboratory rooms
6. **Subject** - Academic subjects with session requirements
7. **TimeSlot** - Time slots (Monday-Friday, 9AM-5PM)
8. **Session** - Individual class sessions
9. **TimetableVersion** - Timetable versioning

### API Endpoints
- `POST /api/generate-timetable/` - Trigger genetic algorithm
- `GET /api/timetable/` - Get current timetable
- `POST /api/teachers/` - CRUD for teachers
- `POST /api/subjects/` - CRUD for subjects
- `POST /api/rooms/` - CRUD for rooms
- `GET /api/constraints-report/` - Validation report
- `POST /api/manual-assign/` - Manual session assignment

## Frontend (React)

### Main Directory
```
timetable-frontend/
├── public/                      # Static assets
├── src/                         # Source code
│   ├── App.tsx                  # Main app component
│   ├── TimetableView.tsx        # Timetable view component
│   ├── index.css                # Global styles
│   └── main.tsx                 # Entry point
├── package.json                 # Dependencies and scripts
├── tsconfig.json                # TypeScript configuration
└── Dockerfile                   # Docker configuration for frontend
```

## DevOps

### Docker Configuration
```
docker-compose.yml               # Orchestration file
```

### Deployment Architecture
1. **PostgreSQL** - Primary database
2. **Redis** - Task queue for Celery
3. **Django** - Backend API
4. **Celery** - Background task processing
5. **React** - Frontend application

## Data

### Seeding
The system includes a management command to seed the database with:
- 18 faculty members
- Academic structure (SE, TE, BE with divisions)
- Rooms and labs
- Time slots (Monday-Friday, 9AM-5PM)
- Sample subjects for all years and divisions

### Genetic Algorithm
- Population size: 150
- Max generations: 500
- Mutation rate: 0.1
- Crossover rate: 0.8
- Tournament selection
- Single point crossover

### Constraints
**Hard Constraints (Must be satisfied):**
1. No teacher can teach two classes simultaneously
2. No batch can have two lectures at the same time
3. No room can host two classes simultaneously
4. Each subject must receive its required weekly sessions
5. Teachers cannot exceed 14 sessions per week
6. Classes only during 9 AM to 5 PM, Monday to Friday
7. Lab subjects must be assigned to lab rooms only

**Soft Constraints (Optimize for):**
1. Equal distribution of 14 sessions across all teachers
2. Respect teacher subject preferences
3. Balance morning (9 AM-1 PM) and afternoon (1 PM-5 PM) classes
4. Minimize gaps in daily schedules
5. Optimize room utilization

## Testing
- Unit tests for all models
- Tests for genetic algorithm components
- API endpoint tests (to be implemented)
- Constraint validation tests (to be implemented)
- Performance tests (to be implemented)

## Performance
- Generates complete timetable in under 60 seconds
- Handles 500+ sessions efficiently
- Supports real-time constraint checking
- Mobile-friendly responsive design