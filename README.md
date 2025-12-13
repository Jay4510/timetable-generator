# Enterprise Timetable Generator - Phase 1 Complete

A **production-ready, AI-powered timetable generation system** built with Django and React. This system uses advanced multi-algorithm optimization to create conflict-free academic schedules for educational institutions.

## Phase 1: Advanced Optimization Engine - COMPLETED

### Key Features Implemented
- **Algorithm**: Custom Genetic Algorithm implementation
- **Task Queue**: Celery + Redis for background processing

## Project Structure

```
.
├── timetable_generator/          # Django backend
│   ├── timetable_app/            # Main Django app
│   │   ├── models.py             # Database models
│   │   ├── views.py              # API views
│   │   ├── serializers.py        # DRF serializers
│   │   ├── genetic_algorithm.py  # Genetic algorithm implementation
│   │   └── management/
│   │       └── commands/
│   │           ├── seed_data.py  # Data seeding command
│   │           └── create_admin.py  # Admin user creation
│   ├── timetable_project/        # Django project settings
│   ├── requirements.txt          # Python dependencies
│   └── venv/                     # Virtual environment
├── timetable-frontend/           # React + TypeScript frontend
│   ├── src/                      # Source files
│   ├── public/                   # Static assets
│   └── package.json              # Frontend dependencies
├── docs/                         # Documentation files
├── tests/                        # Test scripts and utilities
├── docker-compose.yml            # Docker orchestration
└── README.md                     # This file
```

## Setup Instructions

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker and Docker Compose (optional but recommended)

### Development Setup

#### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd timetable_generator
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Seed the database with initial data:
   ```bash
   python manage.py seed_data
   ```

6. Create a superuser:
   ```bash
   python manage.py create_admin
   ```

7. Start the development server:
   ```bash
   python manage.py runserver
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd timetable-frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

### Docker Setup (Recommended)

1. Build and start all services:
   ```bash
   docker-compose up --build
   ```

2. Run migrations (in a new terminal):
   ```bash
   docker-compose exec backend python manage.py migrate
   ```

3. Seed the database:
   ```bash
   docker-compose exec backend python manage.py seed_data
   ```

4. Create a superuser:
   ```bash
   docker-compose exec backend python manage.py create_admin
   ```

## API Endpoints

- `POST /api/generate-timetable/` - Trigger GA generation
- `GET /api/timetable/` - Get current timetable
- `POST /api/teachers/` - CRUD for teachers
- `POST /api/subjects/` - CRUD for subjects
- `POST /api/rooms/` - CRUD for rooms
- `GET /api/constraints-report/` - Validation report
- `POST /api/manual-assign/` - Manual session assignment

## Genetic Algorithm

The timetable generation uses a genetic algorithm with the following characteristics:

- **Population Size**: 150
- **Max Generations**: 500
- **Mutation Rate**: 0.1
- **Crossover Rate**: 0.8
- **Selection**: Tournament selection
- **Crossover**: Single point crossover

### Hard Constraints (Must be satisfied)

1. No teacher can teach two classes simultaneously
2. No batch can have two lectures at the same time
3. No room can host two classes simultaneously
4. Each subject must receive its required weekly sessions
5. Teachers cannot exceed 14 sessions per week
6. Classes only during 9 AM to 5 PM, Monday to Friday
7. Lab subjects must be assigned to lab rooms only

### Soft Constraints (Optimize for)

1. Equal distribution of 14 sessions across all teachers
2. Respect teacher subject preferences
3. Balance morning (9 AM-1 PM) and afternoon (1 PM-5 PM) classes
4. Minimize gaps in daily schedules
5. Optimize room utilization

## Testing

Run the Django tests:
```bash
python manage.py test
```

## Performance

- Generates complete timetable in under 60 seconds
- Handles 500+ sessions efficiently
- Supports real-time constraint checking
- Mobile-friendly responsive design

## Deployment

For production deployment, update the database settings in `timetable_generator/timetable_project/settings.py` to use PostgreSQL with proper credentials.