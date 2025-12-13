"""
Division-Specific Timetable Generator
Generates separate timetables for each division (SE A, SE B, TE A, TE B, BE A, BE B)
while ensuring no teacher conflicts across divisions
"""

from collections import defaultdict
from .models import Teacher, Subject, Room, Lab, TimeSlot, Year, Division, Session
from .division_genetic_algorithm import DivisionGeneticAlgorithm
import random

class DivisionTimetableGenerator:
    def __init__(self):
        self.global_teacher_schedule = defaultdict(set)  # Track teacher assignments across all divisions
        self.division_timetables = {}
        
    def generate_all_division_timetables(self):
        """
        Generate timetables for all divisions ensuring no teacher conflicts
        """
        print("Starting Division-Specific Timetable Generation...")
        
        # Clear existing sessions
        Session.objects.all().delete()
        
        # Get all divisions
        divisions = Division.objects.all().order_by('year__name', 'name')
        
        total_sessions = 0
        generation_results = {}
        
        for division in divisions:
            print(f"\nGenerating timetable for {division.year.name} {division.name}...")
            
            # Generate timetable for this specific division
            sessions_created = self._generate_division_timetable(division)
            total_sessions += sessions_created
            
            generation_results[f"{division.year.name}_{division.name}"] = {
                'sessions_created': sessions_created,
                'division': str(division)
            }
            
            print(f"   {sessions_created} sessions created for {division}")
        
        print(f"\nTotal sessions created across all divisions: {total_sessions}")
        
        # Validate no teacher conflicts across divisions
        conflicts = self._validate_cross_division_conflicts()
        
        return {
            'status': 'success',
            'total_sessions': total_sessions,
            'divisions_processed': len(divisions),
            'division_results': generation_results,
            'cross_division_conflicts': conflicts,
            'algorithm': 'Division-Specific Genetic Algorithm'
        }
    
    def _generate_division_timetable(self, division):
        """
        Generate timetable for a specific division
        """
        # Get subjects for this division
        subjects = Subject.objects.filter(division=division)
        
        if not subjects.exists():
            print(f"   WARNING: No subjects found for {division}")
            return 0
        
        print(f"   Found {subjects.count()} subjects for {division}")
        
        # Create division-specific genetic algorithm
        algorithm = DivisionGeneticAlgorithm(
            division=division,
            global_teacher_schedule=self.global_teacher_schedule,
            population_size=10,
            generations=15
        )
        
        # Run algorithm
        best_solution = algorithm.run()
        
        if best_solution and best_solution.genes:
            # Create sessions from solution
            sessions_created = self._create_sessions_from_solution(best_solution, division)
            
            # Update global teacher schedule
            self._update_global_teacher_schedule(best_solution)
            
            return sessions_created
        
        print(f"   WARNING: No solution found for {division}")
        return 0
    
    def _create_sessions_from_solution(self, solution, division):
        """
        Create Session objects from genetic algorithm solution
        """
        sessions_created = 0
        
        for gene in solution.genes:
            try:
                subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
                
                subject = Subject.objects.get(id=subject_id)
                teacher = Teacher.objects.get(id=teacher_id)
                timeslot = TimeSlot.objects.get(id=timeslot_id)
                
                # Determine if it's a room or lab
                room = None
                lab = None
                
                try:
                    room = Room.objects.get(id=location_id)
                except Room.DoesNotExist:
                    try:
                        lab = Lab.objects.get(id=location_id)
                    except Lab.DoesNotExist:
                        continue
                
                # Create session
                session = Session.objects.create(
                    subject=subject,
                    teacher=teacher,
                    room=room,
                    lab=lab,
                    timeslot=timeslot,
                    batch_number=batch_num
                )
                
                sessions_created += 1
                
            except Exception as e:
                print(f"   WARNING: Error creating session: {e}")
                continue
        
        return sessions_created
    
    def _update_global_teacher_schedule(self, solution):
        """
        Update global teacher schedule to prevent conflicts
        """
        for gene in solution.genes:
            subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
            self.global_teacher_schedule[teacher_id].add(timeslot_id)
    
    def _validate_cross_division_conflicts(self):
        """
        Validate that no teacher has conflicts across divisions
        """
        conflicts = 0
        teacher_timeslot_count = defaultdict(lambda: defaultdict(int))
        
        # Count teacher assignments per timeslot across all sessions
        sessions = Session.objects.all()
        
        for session in sessions:
            teacher_id = session.teacher.id
            timeslot_id = session.timeslot.id
            teacher_timeslot_count[teacher_id][timeslot_id] += 1
        
        # Check for conflicts
        for teacher_id, timeslots in teacher_timeslot_count.items():
            for timeslot_id, count in timeslots.items():
                if count > 1:
                    conflicts += count - 1
                    teacher = Teacher.objects.get(id=teacher_id)
                    timeslot = TimeSlot.objects.get(id=timeslot_id)
                    print(f"   WARNING: Conflict: {teacher.name} has {count} sessions at {timeslot}")
        
        return conflicts
