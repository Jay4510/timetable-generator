
from celery import shared_task
from .genetic_algorithm import GeneticAlgorithm, MultiAlgorithmOptimizer, AdvancedConstraintChecker
from .models import Session, Subject, Teacher, Room, TimeSlot
import time
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def generate_timetable_task(self):
    """
    Celery task to run the genetic algorithm and save the result.
    """
    try:
        print("Starting timetable generation...")
        
        # Clear existing sessions
        print("Clearing existing sessions...")
        Session.objects.all().delete()
        
        # Get all required data
        print("Loading data from database...")
        teachers = list(Teacher.objects.all())
        subjects = list(Subject.objects.all())
        rooms = list(Room.objects.all())
        timeslots = list(TimeSlot.objects.all())
        
        if not all([teachers, subjects, rooms, timeslots]):
            raise ValueError("Insufficient data to generate timetable. Please ensure you have added teachers, subjects, rooms, and timeslots.")
            
        print(f"Loaded: {len(teachers)} teachers, {len(subjects)} subjects, {len(rooms)} rooms, {len(timeslots)} timeslots")
        
        # Use Multi-Algorithm Optimizer for better results
        print("Initializing Multi-Algorithm Optimizer...")
        optimizer = MultiAlgorithmOptimizer()
        
        # Run optimization with intelligent algorithm selection
        optimization_result = optimizer.optimize_timetable(
            constraints=None,  # Will be enhanced in Phase 2
            time_limit=180     # 3 minutes max
        )
        
        best_solution = optimization_result['solution']
        
        if not best_solution:
            raise ValueError("No solution found by optimization algorithms")
        
        print("Saving timetable to database...")
        # Batch create sessions for better performance
        sessions_to_create = []
        for session in best_solution.genes:
            subject_id, teacher_id, room_id, timeslot_id, batch_num = session
            sessions_to_create.append(
                Session(
                    subject_id=subject_id,
                    teacher_id=teacher_id,
                    room_id=room_id,
                    timeslot_id=timeslot_id,
                    batch_number=batch_num
                )
            )
            
        # Bulk create all sessions at once
        Session.objects.bulk_create(sessions_to_create)
        
        print("Timetable generation completed successfully!")
        
        # Enhanced result with optimization details
        return {
            "status": "success", 
            "message": "Timetable generated successfully using Multi-Algorithm Optimizer",
            "sessions_created": len(sessions_to_create),
            "optimization_details": {
                "algorithms_used": optimization_result.get('algorithms_used', []),
                "final_fitness": optimization_result.get('fitness', 0),
                "optimization_time": optimization_result.get('optimization_time', 0),
                "complexity_analysis": "Phase 1 implementation complete"
            }
        }
        
    except Exception as e:
        print(f"Error generating timetable: {str(e)}")
        return {
            "status": "error",
            "message": f"Failed to generate timetable: {str(e)}"
        }
