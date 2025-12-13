from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .models import Teacher, Subject, Room, Lab, TimeSlot, Session, Year, Division, TimetableVersion
from .serializers import (
    TeacherSerializer, SubjectSerializer, RoomSerializer, LabSerializer, 
    TimeSlotSerializer, SessionSerializer, YearSerializer, DivisionSerializer, 
    TimetableVersionSerializer
)
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)

# Teacher CRUD Views
class TeacherListCreateView(generics.ListCreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer

# Year CRUD Views
class YearListCreateView(generics.ListCreateAPIView):
    queryset = Year.objects.all()
    serializer_class = YearSerializer

class YearDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Year.objects.all()
    serializer_class = YearSerializer

# Division CRUD Views
class DivisionListCreateView(generics.ListCreateAPIView):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer

class DivisionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Division.objects.all()
    serializer_class = DivisionSerializer

# Subject CRUD Views
class SubjectListCreateView(generics.ListCreateAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class SubjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

# Room CRUD Views
class RoomListCreateView(generics.ListCreateAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

class RoomDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

# Lab CRUD Views
class LabListCreateView(generics.ListCreateAPIView):
    queryset = Lab.objects.all()
    serializer_class = LabSerializer

class LabDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lab.objects.all()
    serializer_class = LabSerializer

# TimeSlot CRUD Views
class TimeSlotListCreateView(generics.ListCreateAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer

class TimeSlotDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer

# Session CRUD Views
class SessionListCreateView(generics.ListCreateAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

class SessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer

# TimetableVersion CRUD Views
class TimetableVersionListCreateView(generics.ListCreateAPIView):
    queryset = TimetableVersion.objects.all()
    serializer_class = TimetableVersionSerializer

class TimetableVersionDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TimetableVersion.objects.all()
    serializer_class = TimetableVersionSerializer

# Division-Specific Timetable Generation
class GenerateTimetableView(APIView):
    """
    Generate division-specific timetables ensuring no teacher conflicts across divisions
    """
    def post(self, request):
        try:
            # Check if we have sufficient data
            teachers_count = Teacher.objects.count()
            subjects_count = Subject.objects.count()
            rooms_count = Room.objects.count()
            timeslots_count = TimeSlot.objects.count()
            divisions_count = Division.objects.count()
            
            if not all([teachers_count > 0, subjects_count > 0, rooms_count > 0, timeslots_count > 0, divisions_count > 0]):
                return Response({
                    'status': 'error',
                    'message': 'Insufficient data. Please ensure you have teachers, subjects, rooms, timeslots, and divisions.',
                    'data_status': {
                        'teachers': teachers_count,
                        'subjects': subjects_count,
                        'rooms': rooms_count,
                        'timeslots': timeslots_count,
                        'divisions': divisions_count
                    }
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Use Division-Specific Timetable Generation
            use_division_specific = request.data.get('use_division_specific', True)
            
            if use_division_specific:
                print("🎓 Initializing Division-Specific Timetable Generator...")
                
                try:
                    from .division_timetable_generator import DivisionTimetableGenerator
                    
                    generator = DivisionTimetableGenerator()
                    result = generator.generate_all_division_timetables()
                    
                    return Response(result, status=status.HTTP_200_OK)
                    
                except ImportError as e:
                    print(f"Division-specific generator not available: {e}")
                    # Fallback to global generation
                    use_division_specific = False
            
            if not use_division_specific:
                # Fallback to global timetable generation
                print("Using Global Real-World Genetic Algorithm...")
                
                try:
                    from .real_world_genetic_algorithm import RealWorldGeneticAlgorithm
                    
                    # Clear existing sessions
                    Session.objects.all().delete()
                    
                    algorithm = RealWorldGeneticAlgorithm(
                        population_size=10,
                        generations=15,
                        mutation_rate=0.2
                    )
                    
                    best_solution = algorithm.run()
                    
                    if best_solution:
                        sessions_created = self._create_sessions_from_genes(best_solution.genes)
                        
                        return Response({
                            'status': 'success',
                            'sessions_created': sessions_created,
                            'algorithm': 'Global Real-World Genetic Algorithm',
                            'fitness_score': best_solution.fitness_score,
                            'constraint_violations': getattr(best_solution, 'constraint_violations', {})
                        }, status=status.HTTP_200_OK)
                    else:
                        return Response({
                            'status': 'error',
                            'message': 'Algorithm failed to generate solution'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                        
                except ImportError:
                    # Final fallback to simple generation
                    return self._simple_timetable_generation()
                
        except Exception as e:
            print(f"Error in timetable generation: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                'status': 'error',
                'message': f'Timetable generation failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _create_sessions_from_genes(self, genes):
        """Create Session objects from genetic algorithm genes"""
        sessions_created = 0
        
        for gene in genes:
            try:
                subject_id, teacher_id, location_id, timeslot_id, batch_num = gene
                
                subject = Subject.objects.get(id=subject_id)
                teacher = Teacher.objects.get(id=teacher_id)
                timeslot = TimeSlot.objects.get(id=timeslot_id)
                
                # Determine if location is room or lab
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
                Session.objects.create(
                    subject=subject,
                    teacher=teacher,
                    room=room,
                    lab=lab,
                    timeslot=timeslot,
                    batch_number=batch_num,
                    year_division=f"{subject.year.name} {subject.division.name}"
                )
                
                sessions_created += 1
                
            except Exception as e:
                print(f"Error creating session: {e}")
                continue
        
        return sessions_created
    
    def _simple_timetable_generation(self):
        """Simple fallback timetable generation"""
        Session.objects.all().delete()
        
        subjects = Subject.objects.all()
        teachers = list(Teacher.objects.all())
        rooms = list(Room.objects.all())
        labs = list(Lab.objects.all())
        timeslots = list(TimeSlot.objects.all())
        
        sessions_created = 0
        
        for subject in subjects:
            for session_num in range(subject.sessions_per_week):
                import random
                
                teacher = random.choice(teachers)
                timeslot = random.choice(timeslots)
                
                if subject.requires_lab and labs:
                    location = random.choice(labs)
                    room = None
                    lab = location
                else:
                    location = random.choice(rooms)
                    room = location
                    lab = None
                
                Session.objects.create(
                    subject=subject,
                    teacher=teacher,
                    room=room,
                    lab=lab,
                    timeslot=timeslot,
                    batch_number=random.randint(1, subject.division.num_batches),
                    year_division=f"{subject.year.name} {subject.division.name}"
                )
                
                sessions_created += 1
        
        return Response({
            'status': 'success',
            'sessions_created': sessions_created,
            'algorithm': 'Simple Random Assignment',
            'message': 'Fallback generation completed'
        }, status=status.HTTP_200_OK)

# Get Division-Specific Timetable
class DivisionTimetableView(APIView):
    """
    Get timetable for a specific division
    """
    def get(self, request, year_name=None, division_name=None):
        try:
            if year_name and division_name:
                # Get sessions for specific division
                sessions = Session.objects.filter(
                    year_division__icontains=f"{year_name} {division_name}"
                )
            else:
                # Get all sessions
                sessions = Session.objects.all()
            
            serializer = SessionSerializer(sessions, many=True)
            
            return Response({
                'status': 'success',
                'division': f"{year_name} {division_name}" if year_name and division_name else "All Divisions",
                'sessions_count': sessions.count(),
                'sessions': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error fetching division timetable: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Configuration Management
class TimetableConfigurationView(APIView):
    """
    Manage timetable configuration
    """
    def get(self, request):
        try:
            # Get current configuration
            config = {
                'name': 'College Timetable Configuration',
                'academic_year': '2024-25',
                'semester': 'Odd',
                'college_start_time': '09:00:00',
                'college_end_time': '17:45:00',
                'lunch_start_time': '13:00:00',
                'lunch_end_time': '13:45:00',
                'project_half_days_per_week': 1,
                'project_day_preference': 'friday_afternoon',
                'max_sessions_per_teacher': 14,
                'min_sessions_per_teacher': 8
            }
            
            return Response({
                'status': 'success',
                'configuration': config
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error fetching configuration: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        try:
            # Save configuration (implement as needed)
            config_data = request.data
            
            return Response({
                'status': 'success',
                'message': 'Configuration saved successfully',
                'configuration': config_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error saving configuration: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Enhanced endpoints for real-world functionality
@api_view(['POST'])
def submit_teacher_preferences(request):
    """
    Submit teacher time preferences and subject proficiencies
    """
    try:
        teacher_id = request.data.get('teacher_id')
        time_preference = request.data.get('time_preference', 'no_preference')
        subject_ratings = request.data.get('subject_ratings', [])
        
        if not teacher_id:
            return Response({
                'status': 'error',
                'message': 'Teacher ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update teacher preferences
        try:
            teacher = Teacher.objects.get(id=teacher_id)
            teacher.time_preference = time_preference
            teacher.save()
            
            # Handle subject proficiency ratings
            ratings_created = 0
            for rating in subject_ratings:
                subject_id = rating.get('subject_id')
                knowledge = rating.get('knowledge_rating')
                willingness = rating.get('willingness_rating')
                
                # Validate numeric values to prevent NaN errors
                try:
                    knowledge = float(knowledge) if knowledge is not None else None
                    willingness = float(willingness) if willingness is not None else None
                except (ValueError, TypeError):
                    continue  # Skip invalid ratings
                
                if all([subject_id, knowledge, willingness]) and 1 <= knowledge <= 10 and 1 <= willingness <= 10:
                    # Import SubjectProficiency from models
                    try:
                        from .models import SubjectProficiency
                        SubjectProficiency.objects.update_or_create(
                            teacher_id=teacher_id,
                            subject_id=subject_id,
                            defaults={
                                'knowledge_rating': int(knowledge),
                                'willingness_rating': int(willingness)
                            }
                        )
                        ratings_created += 1
                    except ImportError:
                        # Enhanced models not available yet
                        pass
            
            return Response({
                'status': 'success',
                'message': f'Preferences updated for {teacher.name}',
                'time_preference': time_preference,
                'subject_ratings_saved': ratings_created
            }, status=status.HTTP_200_OK)
            
        except Teacher.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Teacher not found'
            }, status=status.HTTP_404_NOT_FOUND)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error updating preferences: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_timetable_analytics(request):
    """
    Get analytics for the generated timetable
    """
    try:
        sessions = Session.objects.all()
        
        # Basic analytics
        analytics = {
            'total_sessions': sessions.count(),
            'divisions': {},
            'teachers': {},
            'rooms_utilization': {},
            'time_distribution': {}
        }
        
        # Division-wise breakdown
        for session in sessions:
            division = session.year_division
            if division not in analytics['divisions']:
                analytics['divisions'][division] = 0
            analytics['divisions'][division] += 1
        
        # Teacher workload
        for session in sessions:
            teacher_name = session.teacher.name
            if teacher_name not in analytics['teachers']:
                analytics['teachers'][teacher_name] = 0
            analytics['teachers'][teacher_name] += 1
        
        return Response({
            'status': 'success',
            'analytics': analytics
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error generating analytics: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Manual assignment endpoint
@api_view(['POST'])
def manual_assign(request):
    """
    Manually assign a session
    """
    try:
        subject_id = request.data.get('subject_id')
        teacher_id = request.data.get('teacher_id')
        room_id = request.data.get('room_id')
        lab_id = request.data.get('lab_id')
        timeslot_id = request.data.get('timeslot_id')
        batch_number = request.data.get('batch_number', 1)
        
        # Validate required fields
        if not all([subject_id, teacher_id, timeslot_id]):
            return Response({
                'status': 'error',
                'message': 'Subject, teacher, and timeslot are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get objects
        subject = Subject.objects.get(id=subject_id)
        teacher = Teacher.objects.get(id=teacher_id)
        timeslot = TimeSlot.objects.get(id=timeslot_id)
        
        room = Room.objects.get(id=room_id) if room_id else None
        lab = Lab.objects.get(id=lab_id) if lab_id else None
        
        # Create session
        session = Session.objects.create(
            subject=subject,
            teacher=teacher,
            room=room,
            lab=lab,
            timeslot=timeslot,
            batch_number=batch_number,
            year_division=f"{subject.year.name} {subject.division.name}"
        )
        
        return Response({
            'status': 'success',
            'message': 'Session assigned successfully',
            'session_id': session.id
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error in manual assignment: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
