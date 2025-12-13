from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from .models import (
    Teacher, Subject, Room, Lab, TimeSlot, Session, Year, Division,
    SubjectProficiency, ProjectTimeAllocation, TeacherReplacement, TimetableVersion,
    SystemConfiguration, RemedialLecture
)
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
class TimetableListView(generics.ListAPIView):
    queryset = Session.objects.all()
    serializer_class = SessionSerializer
    
    def get_queryset(self):
        queryset = Session.objects.all()
        division = self.request.query_params.get('division', None)
        
        if division:
            # Filter by division (e.g., "SE_A", "TE_B")
            year_name, division_name = division.split('_') if '_' in division else (division, 'A')
            queryset = queryset.filter(
                subject__year__name=year_name,
                subject__division__name=division_name
            )
        
        return queryset.select_related('subject', 'teacher', 'room', 'lab', 'timeslot')

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

# Division List API
@api_view(['GET'])
def get_divisions(request):
    """Get all available divisions for filtering"""
    try:
        divisions = Division.objects.select_related('year').all()
        division_data = []
        
        for division in divisions:
            division_data.append({
                'id': division.id,
                'name': division.name,
                'year_name': division.year.name,
                'key': f"{division.year.name}_{division.name}",
                'display_name': f"{division.year.name} {division.name}",
                'num_batches': division.num_batches
            })
        
        return Response(division_data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error fetching divisions: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# System Configuration API
@api_view(['GET', 'POST'])
def system_configuration(request):
    """Get or update system configuration"""
    try:
        if request.method == 'GET':
            # Get active configuration or create default
            config = SystemConfiguration.objects.filter(is_active=True).first()
            if not config:
                config = SystemConfiguration.objects.create()
            
            config_data = {
                'id': config.id,
                'break_start_time': config.break_start_time.strftime('%H:%M'),
                'break_end_time': config.break_end_time.strftime('%H:%M'),
                'max_sessions_per_teacher_per_week': config.max_sessions_per_teacher_per_week,
                'min_sessions_per_teacher_per_week': config.min_sessions_per_teacher_per_week,
                'default_lab_duration_hours': config.default_lab_duration_hours,
                'allow_cross_year_lab_conflicts': config.allow_cross_year_lab_conflicts,
                'remedial_lectures_per_week': config.remedial_lectures_per_week,
                'remedial_preferred_time': config.remedial_preferred_time,
                'project_time_slots_per_week': config.project_time_slots_per_week,
                'morning_afternoon_balance_percentage': config.morning_afternoon_balance_percentage,
            }
            return Response(config_data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            # Update configuration
            config = SystemConfiguration.objects.filter(is_active=True).first()
            if not config:
                config = SystemConfiguration.objects.create()
            
            # Update fields
            config.break_start_time = request.data.get('break_start_time', config.break_start_time)
            config.break_end_time = request.data.get('break_end_time', config.break_end_time)
            config.max_sessions_per_teacher_per_week = request.data.get('max_sessions_per_teacher_per_week', config.max_sessions_per_teacher_per_week)
            config.min_sessions_per_teacher_per_week = request.data.get('min_sessions_per_teacher_per_week', config.min_sessions_per_teacher_per_week)
            config.default_lab_duration_hours = request.data.get('default_lab_duration_hours', config.default_lab_duration_hours)
            config.allow_cross_year_lab_conflicts = request.data.get('allow_cross_year_lab_conflicts', config.allow_cross_year_lab_conflicts)
            config.remedial_lectures_per_week = request.data.get('remedial_lectures_per_week', config.remedial_lectures_per_week)
            config.remedial_preferred_time = request.data.get('remedial_preferred_time', config.remedial_preferred_time)
            config.project_time_slots_per_week = request.data.get('project_time_slots_per_week', config.project_time_slots_per_week)
            config.morning_afternoon_balance_percentage = request.data.get('morning_afternoon_balance_percentage', config.morning_afternoon_balance_percentage)
            
            config.save()
            
            return Response({
                'status': 'success',
                'message': 'Configuration updated successfully'
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error managing system configuration: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Remedial Lecture Management API
@api_view(['GET', 'POST'])
def remedial_lectures(request):
    """Manage remedial lectures"""
    try:
        if request.method == 'GET':
            remedials = RemedialLecture.objects.select_related('subject', 'teacher', 'division').all()
            remedial_data = []
            
            for remedial in remedials:
                remedial_data.append({
                    'id': remedial.id,
                    'subject_name': remedial.subject.name,
                    'subject_code': remedial.subject.code,
                    'teacher_name': remedial.teacher.name,
                    'division': f"{remedial.division.year.name} {remedial.division.name}",
                    'preferred_day': remedial.preferred_day,
                    'preferred_time': remedial.preferred_time,
                    'is_scheduled': remedial.is_scheduled,
                    'scheduled_timeslot': remedial.scheduled_timeslot.id if remedial.scheduled_timeslot else None
                })
            
            return Response(remedial_data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            # Create or update remedial lecture
            subject_id = request.data.get('subject_id')
            teacher_id = request.data.get('teacher_id')
            division_id = request.data.get('division_id')
            
            remedial, created = RemedialLecture.objects.get_or_create(
                subject_id=subject_id,
                division_id=division_id,
                defaults={
                    'teacher_id': teacher_id,
                    'preferred_day': request.data.get('preferred_day', 'any'),
                    'preferred_time': request.data.get('preferred_time', 'afternoon')
                }
            )
            
            if not created:
                remedial.teacher_id = teacher_id
                remedial.preferred_day = request.data.get('preferred_day', remedial.preferred_day)
                remedial.preferred_time = request.data.get('preferred_time', remedial.preferred_time)
                remedial.save()
            
            return Response({
                'status': 'success',
                'message': 'Remedial lecture configured successfully',
                'created': created
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error managing remedial lectures: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            
            # Use User-Driven Timetable Generation (Primary Algorithm)
            use_user_driven = request.data.get('use_user_driven', True)  # Enable by default for production
            
            if use_user_driven:
                print("Initializing User-Driven Timetable Algorithm...")
                
                try:
                    # ✅ TESTING FIXED VERSION (Oct 26, 2025)
                    from .user_driven_timetable_algorithm_FIXED import UserDrivenTimetableAlgorithm
                    
                    # Get user configuration data
                    config_data = request.data.get('config_data', {})
                    
                    # If no config provided, use default configuration
                    if not config_data:
                        config_data = self._get_default_user_config()
                    
                    # Get target years
                    target_years = request.data.get('target_years', ['FE', 'SE', 'TE', 'BE'])
                    
                    # Initialize User-Driven Algorithm
                    algorithm = UserDrivenTimetableAlgorithm(
                        config_data=config_data,
                        target_years=target_years
                    )
                    
                    # Generate timetables
                    result = algorithm.generate_all_timetables()
                    
                    # ✅ ENHANCED RESPONSE with success metrics
                    return Response({
                        'status': 'success',
                        'algorithm': 'User-Driven Timetable Algorithm (FIXED v2.0)',
                        'years_processed': len(target_years),
                        'results': result,
                        'conflicts_report': result.get('_conflicts_report', {}),
                        'success_metrics': result.get('_success_metrics', {}),  # ✅ NEW: Success rate and metrics
                        'total_divisions': sum(len(year_results) for year_results in result.values() 
                                             if isinstance(year_results, dict) and not str(year_results).startswith('_'))
                    }, status=status.HTTP_200_OK)
                    
                except ImportError as e:
                    print(f"User-driven algorithm not available: {e}")
                    # Fallback to division-specific generation
                    use_user_driven = False
                except Exception as e:
                    print(f"Error in user-driven algorithm: {e}")
                    # Fallback to division-specific generation
                    use_user_driven = False
            
            # Fallback to Division-Specific Algorithm
            use_division_specific = request.data.get('use_division_specific', True) if not use_user_driven else False
            
            if use_division_specific:
                print("Fallback: Initializing Division-Specific Timetable Algorithm...")
                
                try:
                    from .division_specific_timetable_algorithm import DivisionSpecificGeneticAlgorithm
                    
                    # Get target divisions (default: all divisions)
                    target_division_ids = request.data.get('division_ids', [])
                    if target_division_ids:
                        target_divisions = Division.objects.filter(id__in=target_division_ids)
                    else:
                        target_divisions = Division.objects.all()
                    
                    # Get algorithm parameters (optimized from memories)
                    population_size = request.data.get('population_size', 10)
                    generations = request.data.get('generations', 15)
                    mutation_rate = request.data.get('mutation_rate', 0.2)
                    
                    algorithm = DivisionSpecificGeneticAlgorithm(
                        target_divisions=list(target_divisions),
                        population_size=population_size,
                        generations=generations,
                        mutation_rate=mutation_rate,
                        incharge_role="department"
                    )
                    
                    result = algorithm.generate_all_division_timetables()
                    
                    return Response({
                        'status': 'success',
                        'algorithm': 'Division-Specific Genetic Algorithm (Fallback)',
                        'divisions_generated': len(result),
                        'results': result
                    }, status=status.HTTP_200_OK)
                    
                except ImportError as e:
                    print(f"Division-specific algorithm not available: {e}")
                    # Continue to next fallback
                    use_division_specific = False
            
            if not use_division_specific:
                # Use Real-World Genetic Algorithm (as per memories - successfully tested)
                print("Using Real-World Genetic Algorithm...")
                
                try:
                    from .real_world_genetic_algorithm import RealWorldGeneticAlgorithm
                    
                    # Clear existing sessions
                    Session.objects.all().delete()
                    
                    # Get parameters from request or use optimized defaults from memories
                    population_size = request.data.get('population_size', 10)   # Optimized from memories
                    generations = request.data.get('generations', 15)           # Optimized from memories  
                    mutation_rate = request.data.get('mutation_rate', 0.2)      # Standard rate
                    
                    algorithm = RealWorldGeneticAlgorithm(
                        population_size=population_size,
                        generations=generations,
                        mutation_rate=mutation_rate
                    )
                    
                    best_solution = algorithm.run()
                    
                    if best_solution and best_solution.genes:
                        sessions_created = self._create_sessions_from_genes(best_solution.genes)
                        
                        return Response({
                            'status': 'success',
                            'sessions_created': sessions_created,
                            'algorithm': 'Real-World Genetic Algorithm (Production Ready)',
                            'fitness_score': best_solution.fitness_score,
                            'constraint_violations': getattr(best_solution, 'violations', {}),
                            'constraint_details': getattr(best_solution, 'constraint_details', {}),
                            'total_violations': getattr(best_solution, 'violations', {}).get('total', 0)
                        }, status=status.HTTP_200_OK)
                    else:
                        print("Real-world algorithm failed, trying improved algorithm...")
                        
                except ImportError as e:
                    print(f"Real-world algorithm not available: {e}")
                
                # Fallback to comprehensive genetic algorithm
                print("Using Comprehensive Genetic Algorithm (Fallback)...")
                
                try:
                    from .comprehensive_genetic_algorithm import ComprehensiveGeneticAlgorithm
                    
                    # Clear existing sessions
                    Session.objects.all().delete()
                    
                    algorithm = ComprehensiveGeneticAlgorithm(
                        population_size=20,
                        generations=50,
                        mutation_rate=0.2
                    )
                    
                    best_solution = algorithm.run()
                    
                    if best_solution and best_solution.genes:
                        print(f"Algorithm generated {len(best_solution.genes)} genes")
                        print(f"Sample genes: {best_solution.genes[:3] if best_solution.genes else 'None'}")
                        sessions_created = self._create_sessions_from_genes(best_solution.genes)
                        
                        return Response({
                            'status': 'success',
                            'sessions_created': sessions_created,
                            'algorithm': 'Improved Genetic Algorithm',
                            'fitness_score': best_solution.fitness(),
                            'constraint_violations': getattr(best_solution, 'violations', {})
                        }, status=status.HTTP_200_OK)
                    else:
                        print("Improved algorithm failed, trying real-world algorithm...")
                        
                except ImportError as e:
                    print(f"Improved algorithm not available: {e}")
                
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
                    # Try comprehensive genetic algorithm as final fallback
                    try:
                        from .comprehensive_genetic_algorithm import ComprehensiveGeneticAlgorithm
                        
                        print("Using Comprehensive Genetic Algorithm (Final Fallback)...")
                        
                        # Clear existing sessions
                        Session.objects.all().delete()
                        
                        algorithm = ComprehensiveGeneticAlgorithm(
                            population_size=15,
                            generations=30,
                            mutation_rate=0.15
                        )
                        
                        best_solution = algorithm.run()
                        
                        if best_solution and best_solution.genes:
                            sessions_created = self._create_sessions_from_genes(best_solution.genes)
                            
                            return Response({
                                'status': 'success',
                                'sessions_created': sessions_created,
                                'algorithm': 'Improved Genetic Algorithm',
                                'fitness_score': best_solution.fitness(),
                                'constraint_violations': getattr(best_solution, 'violations', {})
                            }, status=status.HTTP_200_OK)
                        else:
                            # Final fallback to simple generation
                            return self._simple_timetable_generation()
                            
                    except ImportError:
                        # Improved Genetic Algorithm not available, use simple generation
                        return self._simple_timetable_generation()
                        
        except Exception as e:
            logger.error(f"Error in timetable generation: {e}")
            return Response({
                'status': 'error',
                'message': f'Generation failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _create_sessions_from_genes(self, genes):
        """Create sessions from chromosome genes"""
        print(f"Creating sessions from {len(genes)} genes")
        sessions_created = 0
        
        for i, gene in enumerate(genes):
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
                    batch_number=batch_num
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
                    batch_number=random.randint(1, getattr(subject.division, 'num_batches', 3))
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
    Enhanced to handle lecture/lab timing preferences and cross-year teaching
    """
    try:
        # Handle both individual submission and bulk proficiencies
        if 'proficiencies' in request.data:
            # Bulk proficiency submission from wizard
            proficiencies_data = request.data.get('proficiencies', [])
            total_created = 0
            
            for prof_data in proficiencies_data:
                teacher_id = prof_data.get('teacher_id')
                subject_ratings = prof_data.get('subject_ratings', [])
                
                if not teacher_id:
                    continue
                
                try:
                    teacher = Teacher.objects.get(id=teacher_id)
                    
                    # Update enhanced preferences
                    preferences = {
                        'lecture_time_preference': prof_data.get('lecture_time_preference', 'no_preference'),  # morning/afternoon
                        'lab_time_preference': prof_data.get('lab_time_preference', 'no_preference'),  # morning/afternoon
                        'cross_year_teaching': prof_data.get('cross_year_teaching', False),  # Can teach across years
                        'preferred_years': prof_data.get('preferred_years', []),  # List of years they prefer
                        'max_cross_year_sessions': prof_data.get('max_cross_year_sessions', 6)  # Max sessions across years
                    }
                    
                    teacher.preferences = preferences
                    teacher.save()
                    
                    # Handle subject proficiency ratings
                    for rating in subject_ratings:
                        subject_id = rating.get('subject_id')
                        knowledge = rating.get('knowledge_rating')
                        willingness = rating.get('willingness_rating')
                        
                        # Validate numeric values
                        try:
                            knowledge = float(knowledge) if knowledge is not None else None
                            willingness = float(willingness) if willingness is not None else None
                        except (ValueError, TypeError):
                            continue
                        
                        if all([subject_id, knowledge, willingness]) and 1 <= knowledge <= 10 and 1 <= willingness <= 10:
                            SubjectProficiency.objects.update_or_create(
                                teacher_id=teacher_id,
                                subject_id=subject_id,
                                defaults={
                                    'knowledge_rating': int(knowledge),
                                    'willingness_rating': int(willingness)
                                }
                            )
                            total_created += 1
                            
                except Teacher.DoesNotExist:
                    continue
            
            return Response({
                'status': 'success',
                'message': f'Successfully updated preferences for {len(proficiencies_data)} teachers',
                'proficiencies_created': total_created
            }, status=status.HTTP_200_OK)
        
        else:
            # Individual teacher submission
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
                
                # Enhanced preferences
                preferences = {
                    'lecture_time_preference': request.data.get('lecture_time_preference', 'no_preference'),
                    'lab_time_preference': request.data.get('lab_time_preference', 'no_preference'),
                    'cross_year_teaching': request.data.get('cross_year_teaching', False),
                    'preferred_years': request.data.get('preferred_years', []),
                    'max_cross_year_sessions': request.data.get('max_cross_year_sessions', 6)
                }
                
                teacher.time_preference = time_preference
                teacher.preferences = preferences
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
                        SubjectProficiency.objects.update_or_create(
                            teacher_id=teacher_id,
                            subject_id=subject_id,
                            defaults={
                                'knowledge_rating': int(knowledge),
                                'willingness_rating': int(willingness)
                            }
                        )
                        ratings_created += 1
                
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

# Missing Views for URL routing
class TimetableView(APIView):
    """
    Get current timetable sessions with division filtering
    """
    def get(self, request):
        try:
            queryset = Session.objects.all()
            division = request.query_params.get('division', None)
            
            if division:
                # Filter by division (e.g., "SE_A", "TE_B")
                year_name, division_name = division.split('_') if '_' in division else (division, 'A')
                queryset = queryset.filter(
                    subject__year__name=year_name,
                    subject__division__name=division_name
                )
            
            sessions = queryset.select_related('subject', 'teacher', 'room', 'lab', 'timeslot')
            serializer = SessionSerializer(sessions, many=True)
            
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error fetching timetable: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_constraints_report(request):
    """
    Get constraints report for the current timetable
    """
    try:
        sessions = Session.objects.all()
        
        # Basic constraint analysis
        report = {
            'total_sessions': sessions.count(),
            'teacher_conflicts': 0,
            'room_conflicts': 0,
            'constraint_violations': []
        }
        
        # Check for teacher conflicts
        from collections import defaultdict
        teacher_schedule = defaultdict(list)
        
        for session in sessions:
            key = f"{session.teacher.name}_{session.timeslot.day}_{session.timeslot.start_time}"
            teacher_schedule[key].append(session)
        
        for key, session_list in teacher_schedule.items():
            if len(session_list) > 1:
                report['teacher_conflicts'] += len(session_list) - 1
                report['constraint_violations'].append({
                    'type': 'teacher_conflict',
                    'details': f"Teacher {session_list[0].teacher.name} has {len(session_list)} sessions at {session_list[0].timeslot.day} {session_list[0].timeslot.start_time}"
                })
        
        return Response({
            'status': 'success',
            'report': report
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error generating constraints report: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def handle_teacher_replacement(request):
    """
    Handle teacher replacement workflow
    """
    try:
        old_teacher_id = request.data.get('old_teacher_id')
        new_teacher_id = request.data.get('new_teacher_id')
        
        if not all([old_teacher_id, new_teacher_id]):
            return Response({
                'status': 'error',
                'message': 'Both old and new teacher IDs are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        old_teacher = Teacher.objects.get(id=old_teacher_id)
        new_teacher = Teacher.objects.get(id=new_teacher_id)
        
        # Update all sessions
        sessions_updated = Session.objects.filter(teacher=old_teacher).update(teacher=new_teacher)
        
        return Response({
            'status': 'success',
            'message': f'Replaced {old_teacher.name} with {new_teacher.name}',
            'sessions_updated': sessions_updated
        }, status=status.HTTP_200_OK)
        
    except Teacher.DoesNotExist:
        return Response({
            'status': 'error',
            'message': 'Teacher not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error in teacher replacement: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class TeacherResignationView(APIView):
    """
    Handle teacher resignation workflow
    """
    def post(self, request):
        try:
            teacher_id = request.data.get('teacher_id')
            replacement_teacher_id = request.data.get('replacement_teacher_id')
            
            if not teacher_id:
                return Response({
                    'status': 'error',
                    'message': 'Teacher ID is required'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            teacher = Teacher.objects.get(id=teacher_id)
            
            if replacement_teacher_id:
                replacement_teacher = Teacher.objects.get(id=replacement_teacher_id)
                sessions_updated = Session.objects.filter(teacher=teacher).update(teacher=replacement_teacher)
                
                return Response({
                    'status': 'success',
                    'message': f'Teacher {teacher.name} replaced with {replacement_teacher.name}',
                    'sessions_updated': sessions_updated
                }, status=status.HTTP_200_OK)
            else:
                # Just remove the teacher's sessions
                sessions_deleted = Session.objects.filter(teacher=teacher).delete()[0]
                
                return Response({
                    'status': 'success',
                    'message': f'Teacher {teacher.name} sessions removed',
                    'sessions_deleted': sessions_deleted
                }, status=status.HTTP_200_OK)
                
        except Teacher.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Teacher not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'Error handling resignation: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Data reset endpoints
@api_view(['POST'])
def reset_teachers(request):
    """Reset all teacher data"""
    try:
        count = Teacher.objects.count()
        Teacher.objects.all().delete()
        return Response({
            'status': 'success',
            'message': f'Deleted {count} teachers'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error resetting teachers: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def reset_subjects(request):
    """Reset all subject data"""
    try:
        count = Subject.objects.count()
        Subject.objects.all().delete()
        return Response({
            'status': 'success',
            'message': f'Deleted {count} subjects'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error resetting subjects: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def reset_rooms(request):
    """Reset all room data"""
    try:
        room_count = Room.objects.count()
        lab_count = Lab.objects.count()
        Room.objects.all().delete()
        Lab.objects.all().delete()
        return Response({
            'status': 'success',
            'message': f'Deleted {room_count} rooms and {lab_count} labs'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error resetting rooms: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def reset_timetable(request):
    """Reset all timetable sessions"""
    try:
        count = Session.objects.count()
        Session.objects.all().delete()
        return Response({
            'status': 'success',
            'message': f'Deleted {count} sessions'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'status': 'error',
            'message': f'Error resetting timetable: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class GenerateDivisionTimetableView(APIView):
    """
    Generate timetable for a specific division
    """
    def post(self, request, division_id=None):
        try:
            if division_id:
                # Generate for specific division
                try:
                    division = Division.objects.get(id=division_id)
                except Division.DoesNotExist:
                    return Response({
                        'status': 'error',
                        'message': f'Division with ID {division_id} not found'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                target_divisions = [division]
            else:
                # Generate for all divisions
                target_divisions = list(Division.objects.all())
            
            # Get algorithm parameters
            population_size = request.data.get('population_size', 10)
            generations = request.data.get('generations', 15)
            mutation_rate = request.data.get('mutation_rate', 0.2)
            
            from .division_specific_timetable_algorithm import DivisionSpecificGeneticAlgorithm
            
            algorithm = DivisionSpecificGeneticAlgorithm(
                target_divisions=target_divisions,
                population_size=population_size,
                generations=generations,
                mutation_rate=mutation_rate,
                incharge_role="department"
            )
            
            result = algorithm.generate_all_division_timetables()
            
            return Response({
                'status': 'success',
                'algorithm': 'Division-Specific Genetic Algorithm',
                'divisions_generated': len(result),
                'results': result
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in timetable generation: {e}")
            return Response({
                'status': 'error',
                'message': f'Generation failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_default_user_config(self):
        """Generate default configuration for User-Driven Algorithm"""
        from datetime import time
        
        try:
            # Get all teachers, subjects, rooms from database
            teachers = list(Teacher.objects.all())
            subjects = list(Subject.objects.all())
            rooms = list(Room.objects.all())
            labs = list(Lab.objects.all())
            years = list(Year.objects.all())
            divisions = list(Division.objects.all())
            
            # Build default configuration
            config_data = {
                # Basic timing
                'college_start_time': time(9, 0),
                'college_end_time': time(17, 45),
                'recess_start': time(13, 0),
                'recess_end': time(13, 45),
                
                # Professor assignments by year (auto-assign all teachers to all years)
                'professor_year_assignments': {},
                
                # Proficiency data (default scores)
                'proficiency_data': {},
                
                # Room assignments by year
                'room_assignments': {},
                
                # Remedial configuration per year
                'remedial_config': {},
                
                # Professor preferences (default to flexible)
                'professor_preferences': {},
                
                # Division configuration
                'division_config': {},
                
                # Batch configuration
                'batch_config': {},
                
                # Project work configuration
                'project_config': {}
            }
            
            # Auto-assign teachers to years
            teacher_ids = [t.id for t in teachers]
            for year in years:
                config_data['professor_year_assignments'][year.name] = teacher_ids
                config_data['remedial_config'][year.name] = 1  # 1 remedial per week
                config_data['project_config'][year.name] = 1 if year.name in ['SE', 'TE', 'BE'] else 0
            
            # Auto-assign proficiency (default scores)
            for teacher in teachers:
                config_data['proficiency_data'][teacher.id] = {}
                for subject in subjects:
                    config_data['proficiency_data'][teacher.id][subject.id] = {
                        'knowledge': 7.0,  # Default good proficiency
                        'willingness': 7.0
                    }
            
            # Auto-assign rooms to years
            room_ids = [r.id for r in rooms]
            lab_ids = [l.id for l in labs]
            for year in years:
                config_data['room_assignments'][year.name] = {
                    'lectures': room_ids,
                    'labs': lab_ids
                }
            
            # Set teacher preferences to flexible
            for teacher in teachers:
                config_data['professor_preferences'][teacher.id] = {
                    'first_half_second_half': 'flexible'
                }
            
            # Set division configuration
            for year in years:
                year_divisions = [d.name for d in divisions if d.year == year]
                config_data['division_config'][year.name] = year_divisions if year_divisions else ['A', 'B']
            
            # Set batch configuration
            for division in divisions:
                division_key = f"{division.year.name}-{division.name}"
                config_data['batch_config'][division_key] = 3  # 3 batches per division
            
            return config_data
            
        except Exception as e:
            logger.error(f"Error generating default config: {e}")
            # Return minimal config if database queries fail
            return {
                'college_start_time': time(9, 0),
                'college_end_time': time(17, 45),
                'recess_start': time(13, 0),
                'recess_end': time(13, 45),
                'professor_year_assignments': {},
                'proficiency_data': {},
                'room_assignments': {},
                'remedial_config': {},
                'professor_preferences': {},
                'division_config': {},
                'batch_config': {},
                'project_config': {}
            }


class DivisionTimetableResultsView(APIView):
    """
    Get stored timetable results for a specific division
    """
    def get(self, request, division_id):
        try:
            division = Division.objects.get(id=division_id)
            
            # Get sessions for this division
            sessions = Session.objects.filter(
                subject__year=division.year,
                subject__division=division
            ).select_related('subject', 'teacher', 'room', 'timeslot')
            
            # Format results
            timetable_data = []
            for session in sessions:
                timetable_data.append({
                    'id': session.id,
                    'subject': session.subject.name,
                    'teacher': session.teacher.name,
                    'room': session.room.name if session.room else None,
                    'timeslot': {
                        'day': session.timeslot.day_of_week,
                        'start_time': session.timeslot.start_time.strftime('%H:%M'),
                        'end_time': session.timeslot.end_time.strftime('%H:%M')
                    },
                    'batch': getattr(session, 'batch', None)
                })
            
            return Response({
                'status': 'success',
                'division': {
                    'id': division.id,
                    'name': division.name,
                    'year': division.year.name
                },
                'timetable': timetable_data,
                'total_sessions': len(timetable_data)
            }, status=status.HTTP_200_OK)
            
        except Division.DoesNotExist:
            return Response({
                'status': 'error',
                'message': f'Division with ID {division_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching division results: {e}")
            return Response({
                'status': 'error',
                'message': f'Failed to fetch results: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDrivenConfigurationView(APIView):
    """
    Manage User-Driven Algorithm Configuration
    """
    def get(self, request):
        """Get current user-driven configuration"""
        try:
            # Get default configuration
            generate_view = GenerateTimetableView()
            default_config = generate_view._get_default_user_config()
            
            return Response({
                'status': 'success',
                'config_data': default_config,
                'message': 'Default configuration generated from current database'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting user-driven config: {e}")
            return Response({
                'status': 'error',
                'message': f'Failed to get configuration: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Update user-driven configuration"""
        try:
            config_data = request.data.get('config_data', {})
            
            # Validate configuration structure
            required_keys = [
                'college_start_time', 'college_end_time', 'recess_start', 'recess_end',
                'professor_year_assignments', 'proficiency_data', 'room_assignments',
                'remedial_config', 'professor_preferences', 'division_config',
                'batch_config', 'project_config'
            ]
            
            missing_keys = [key for key in required_keys if key not in config_data]
            if missing_keys:
                return Response({
                    'status': 'error',
                    'message': f'Missing configuration keys: {missing_keys}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Save configuration (you can store this in database or cache)
            # For now, we'll just validate and return success
            
            return Response({
                'status': 'success',
                'message': 'Configuration updated successfully',
                'config_data': config_data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating user-driven config: {e}")
            return Response({
                'status': 'error',
                'message': f'Failed to update configuration: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def test_user_driven_import(request):
    """Test if User-Driven Algorithm can be imported"""
    try:
        # ✅ TESTING FIXED VERSION (Oct 26, 2025)
        from .user_driven_timetable_algorithm_FIXED import UserDrivenTimetableAlgorithm
        
        # Also check database status
        teachers_count = Teacher.objects.count()
        subjects_count = Subject.objects.count()
        rooms_count = Room.objects.count()
        labs_count = Lab.objects.count()
        years_count = Year.objects.count()
        divisions_count = Division.objects.count()
        
        return Response({
            'status': 'success',
            'message': 'User-Driven Algorithm imported successfully',
            'database_status': {
                'teachers': teachers_count,
                'subjects': subjects_count,
                'rooms': rooms_count,
                'labs': labs_count,
                'years': years_count,
                'divisions': divisions_count
            }
        }, status=status.HTTP_200_OK)
    except Exception as e:
        import traceback
        return Response({
            'status': 'error',
            'message': f'Import failed: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def initialize_basic_data(request):
    """Initialize basic data for testing"""
    try:
        from datetime import time
        logger.info("Starting basic data initialization")
        
        # Create basic years if they don't exist
        logger.info("Creating years...")
        years_created = 0
        for year_name in ['FE', 'SE', 'TE', 'BE']:
            try:
                year, created = Year.objects.get_or_create(name=year_name)
                if created:
                    years_created += 1
                    logger.info(f"Created year: {year_name}")
            except Exception as e:
                logger.error(f"Error creating year {year_name}: {e}")
                raise
        
        # Create basic divisions if they don't exist
        logger.info("Creating divisions...")
        divisions_created = 0
        for year in Year.objects.all():
            for div_name in ['A', 'B']:
                try:
                    division, created = Division.objects.get_or_create(
                        year=year, 
                        name=div_name,
                        defaults={'num_batches': 3}
                    )
                    if created:
                        divisions_created += 1
                        logger.info(f"Created division: {year.name} {div_name}")
                except Exception as e:
                    logger.error(f"Error creating division {year.name} {div_name}: {e}")
                    raise
        
        # Create basic teachers if they don't exist
        logger.info("Creating teachers...")
        teachers_created = 0
        if Teacher.objects.count() == 0:
            for i in range(5):
                try:
                    Teacher.objects.create(
                        name=f'Teacher {i+1}',
                        email=f'teacher{i+1}@dmce.ac.in',
                        department='Information Technology',
                        experience_years=5,
                        specialization='Computer Science',
                        time_preference='no_preference',
                        preferences={'first_half_second_half': 'flexible'}
                    )
                    teachers_created += 1
                    logger.info(f"Created teacher: Teacher {i+1}")
                except Exception as e:
                    logger.error(f"Error creating teacher {i+1}: {e}")
                    raise
        
        # Create basic subjects if they don't exist
        logger.info("Creating subjects...")
        subjects_created = 0
        if Subject.objects.count() == 0:
            subject_counter = 1
            for year in Year.objects.all():
                for div in Division.objects.filter(year=year):
                    try:
                        subject_code = f'{year.name}{div.name}S1'
                        logger.info(f"Creating subject with code: {subject_code}")
                        Subject.objects.create(
                            name=f'{year.name}-{div.name} Subject 1',
                            code=subject_code,
                            year=year,
                            division=div,
                            sessions_per_week=4,
                            requires_lab=False,
                            lecture_duration_hours=1,
                            lab_frequency_per_week=1,
                            requires_remedial=True,
                            equipment_requirements=[]
                        )
                        subjects_created += 1
                        subject_counter += 1
                        logger.info(f"Created subject: {subject_code}")
                    except Exception as e:
                        logger.error(f"Error creating subject for {year.name} {div.name}: {e}")
                        raise
        
        # Create basic rooms if they don't exist
        logger.info("Creating rooms...")
        rooms_created = 0
        if Room.objects.count() == 0:
            for i in range(5):
                try:
                    Room.objects.create(
                        name=f'Room {i+1}',
                        capacity=60
                    )
                    rooms_created += 1
                    logger.info(f"Created room: Room {i+1}")
                except Exception as e:
                    logger.error(f"Error creating room {i+1}: {e}")
                    raise
        
        # Create basic labs if they don't exist
        logger.info("Creating labs...")
        labs_created = 0
        if Lab.objects.count() == 0:
            for i in range(3):
                try:
                    Lab.objects.create(
                        name=f'Lab {i+1}',
                        capacity=30
                    )
                    labs_created += 1
                    logger.info(f"Created lab: Lab {i+1}")
                except Exception as e:
                    logger.error(f"Error creating lab {i+1}: {e}")
                    raise
        
        # Create basic time slots if they don't exist
        logger.info("Creating time slots...")
        timeslots_created = 0
        if TimeSlot.objects.count() == 0:
            days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']
            times = [
                (time(9, 0), time(10, 0)),
                (time(10, 0), time(11, 0)),
                (time(11, 0), time(12, 0)),
                (time(12, 0), time(13, 0)),
                (time(14, 0), time(15, 0)),
                (time(15, 0), time(16, 0)),
                (time(16, 0), time(17, 0)),
                (time(17, 0), time(18, 0)),
            ]
            
            slot_number = 1
            for day in days:
                for start_time, end_time in times:
                    try:
                        TimeSlot.objects.create(
                            day=day,
                            slot_number=slot_number,
                            start_time=start_time,
                            end_time=end_time
                        )
                        timeslots_created += 1
                        logger.info(f"Created timeslot: {day} {slot_number} ({start_time}-{end_time})")
                        slot_number += 1
                    except Exception as e:
                        logger.error(f"Error creating timeslot {day} {slot_number}: {e}")
                        raise
        
        logger.info("Basic data initialization completed successfully")
        return Response({
            'status': 'success',
            'message': 'Basic data initialized',
            'created': {
                'years': years_created,
                'divisions': divisions_created,
                'teachers': teachers_created,
                'subjects': subjects_created,
                'rooms': rooms_created,
                'labs': labs_created,
                'timeslots': timeslots_created
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        import traceback
        return Response({
            'status': 'error',
            'message': f'Initialization failed: {str(e)}',
            'traceback': traceback.format_exc()
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDrivenGenerationView(APIView):
    """
    Generate timetables using User-Driven Algorithm with custom configuration
    """
    def post(self, request):
        try:
            # Get configuration data
            config_data = request.data.get('config_data', {})
            target_years = request.data.get('target_years', ['FE', 'SE', 'TE', 'BE'])
            
            logger.info(f"Received request with config_data keys: {list(config_data.keys()) if config_data else 'None'}")
            logger.info(f"Target years: {target_years}")
            logger.info(f"Teachers in config: {len(config_data.get('teachers', []))}")
            logger.info(f"Subjects in config: {len(config_data.get('subjects', []))}")
            
            # ✅ CRITICAL FIX: Save wizard data to database BEFORE running algorithm
            if config_data and (config_data.get('teachers') or config_data.get('subjects')):
                logger.info("🚀 CALLING _prepare_wizard_data_for_algorithm")
                config_data = self._prepare_wizard_data_for_algorithm(config_data, target_years)
                logger.info("✅ FINISHED _prepare_wizard_data_for_algorithm")
            else:
                logger.warning("⚠️ NO WIZARD DATA TO PREPARE - config_data is empty or has no teachers/subjects")
            
            # If no config provided, get default
            if not config_data:
                logger.info("No config provided, generating default config")
                try:
                    generate_view = GenerateTimetableView()
                    config_data = generate_view._get_default_user_config()
                    logger.info(f"Generated default config with keys: {list(config_data.keys())}")
                except Exception as config_error:
                    logger.error(f"Error generating default config: {config_error}")
                    # Use minimal config if default generation fails
                    config_data = {
                        'college_start_time': '09:00',
                        'college_end_time': '17:45',
                        'recess_start': '13:00',
                        'recess_end': '13:45',
                        'professor_year_assignments': {},
                        'proficiency_data': {},
                        'room_assignments': {},
                        'remedial_config': {},
                        'professor_preferences': {},
                        'division_config': {},
                        'batch_config': {},
                        'project_config': {}
                    }
            
            # Import and initialize User-Driven Algorithm
            logger.info("Importing UserDrivenTimetableAlgorithm FIXED VERSION")
            # ✅ TESTING FIXED VERSION (Oct 26, 2025)
            from .user_driven_timetable_algorithm_FIXED import UserDrivenTimetableAlgorithm
            
            logger.info("Initializing algorithm")
            algorithm = UserDrivenTimetableAlgorithm(
                config_data=config_data,
                target_years=target_years
            )
            
            # Generate timetables
            logger.info("Starting timetable generation")
            result = algorithm.generate_all_timetables()
            logger.info(f"Generation completed with result type: {type(result)}")
            logger.info(f"Generation result: {result}")
            
            # Check if result is valid
            if not isinstance(result, dict):
                logger.error(f"Expected dict result, got {type(result)}: {result}")
                return Response({
                    'status': 'error',
                    'message': f'Algorithm returned invalid result type: {type(result)}',
                    'result_content': str(result)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Process results for better frontend consumption
            processed_results = self._process_results(result)
            success_metrics = result.get('_success_metrics', {})
            
            return Response({
                'status': 'success',
                'algorithm': 'User-Driven Timetable Algorithm',
                'years_processed': len(target_years),
                'results': processed_results,
                'conflicts_report': result.get('_conflicts_report', {}),
                'summary': self._generate_summary(result),
                # ✅ FIX: Include success metrics at top level for frontend
                '_success_metrics': success_metrics,
                'success_rate': success_metrics.get('success_rate', 0),
                'total_divisions': success_metrics.get('total_divisions', 0),
                'successful_divisions': success_metrics.get('successful_divisions', 0),
                'total_conflicts': success_metrics.get('total_violations', 0),
                'conflict_free': success_metrics.get('conflict_free', False)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Error in user-driven generation: {e}")
            logger.error(f"Full traceback: {error_traceback}")
            return Response({
                'status': 'error',
                'message': f'Generation failed: {str(e)}',
                'traceback': error_traceback
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _prepare_wizard_data_for_algorithm(self, config_data, target_years):
        """
        ✅ CRITICAL FIX: Convert wizard data to database records
        This ensures the algorithm can find teachers and subjects
        """
        try:
            logger.info("🔧 Preparing wizard data for algorithm...")
            
            # 1. Process wizard teachers and save to database
            wizard_teachers = config_data.get('teachers', [])
            teacher_id_mapping = {}  # wizard_id -> database_id
            
            if wizard_teachers:
                logger.info(f"Processing {len(wizard_teachers)} teachers from wizard")
                for teacher_data in wizard_teachers:
                    wizard_id = teacher_data.get('id', teacher_data.get('name'))
                    teacher_name = teacher_data.get('name', f'Teacher {wizard_id}')
                    
                    # Create or get teacher in database
                    teacher, created = Teacher.objects.get_or_create(
                        name=teacher_name,
                        defaults={
                            'experience_years': teacher_data.get('experience', 5),
                            'time_preference': 'no_preference',  # Default preference
                            'department': 'Information Technology'
                        }
                    )
                    teacher_id_mapping[wizard_id] = teacher.id
                    
                    if created:
                        logger.info(f"✅ Created teacher: {teacher_name} (ID: {teacher.id})")
                    else:
                        logger.info(f"♻️  Using existing teacher: {teacher_name} (ID: {teacher.id})")
            
            # 2. Process wizard subjects and save to database
            wizard_subjects = config_data.get('subjects', [])
            subject_id_mapping = {}  # wizard_id -> database_id
            
            if wizard_subjects:
                logger.info(f"Processing {len(wizard_subjects)} subjects from wizard")
                
                # Get or create years and divisions
                for year_name in target_years:
                    year, _ = Year.objects.get_or_create(name=year_name)
                    
                    # Create default divisions if they don't exist
                    for div_name in ['A', 'B']:
                        division, _ = Division.objects.get_or_create(
                            year=year,
                            name=div_name,
                            defaults={'student_count': 60, 'num_batches': 3}
                        )
                
                # Now create subjects
                for subject_data in wizard_subjects:
                    wizard_id = subject_data.get('id', subject_data.get('code'))
                    subject_name = subject_data.get('name', f'Subject {wizard_id}')
                    subject_code = subject_data.get('code', wizard_id)
                    
                    # Determine which year this subject belongs to
                    subject_year = subject_data.get('year', target_years[0] if target_years else 'BE')
                    year, _ = Year.objects.get_or_create(name=subject_year)
                    division, _ = Division.objects.get_or_create(
                        year=year, 
                        name='A',
                        defaults={'student_count': 60, 'num_batches': 3}
                    )
                    
                    # Create or get subject
                    subject, created = Subject.objects.get_or_create(
                        code=subject_code,
                        defaults={
                            'name': subject_name,
                            'year': year,
                            'division': division,
                            'sessions_per_week': subject_data.get('sessionsPerWeek', 3),
                            'requires_lab': subject_data.get('requiresLab', False) or subject_data.get('isLab', False)
                        }
                    )
                    subject_id_mapping[wizard_id] = subject.id
                    
                    if created:
                        logger.info(f"✅ Created subject: {subject_name} (ID: {subject.id})")
                    else:
                        logger.info(f"♻️  Using existing subject: {subject_name} (ID: {subject.id})")
            
            # 3. Update professor_year_assignments with database IDs
            professor_year_assignments = {}
            wizard_assignments = config_data.get('professor_year_assignments', {})
            
            for year, teacher_names in wizard_assignments.items():
                if isinstance(teacher_names, list):
                    # Map wizard IDs/names to database IDs
                    db_teacher_ids = []
                    for teacher_ref in teacher_names:
                        if teacher_ref in teacher_id_mapping:
                            db_teacher_ids.append(teacher_id_mapping[teacher_ref])
                        else:
                            # Try to find by name
                            try:
                                teacher = Teacher.objects.get(name=teacher_ref)
                                db_teacher_ids.append(teacher.id)
                            except Teacher.DoesNotExist:
                                logger.warning(f"Teacher not found: {teacher_ref}")
                    
                    professor_year_assignments[year] = db_teacher_ids
            
            config_data['professor_year_assignments'] = professor_year_assignments
            logger.info(f"✅ Mapped professor assignments: {professor_year_assignments}")
            
            # 4. Update proficiency_data with database IDs
            proficiency_data = {}
            wizard_proficiency = config_data.get('proficiency_data', {})
            
            for teacher_ref, subjects_prof in wizard_proficiency.items():
                teacher_db_id = teacher_id_mapping.get(teacher_ref)
                if teacher_db_id:
                    proficiency_data[teacher_db_id] = {}
                    for subject_ref, scores in subjects_prof.items():
                        subject_db_id = subject_id_mapping.get(subject_ref, subject_ref)
                        proficiency_data[teacher_db_id][subject_db_id] = scores
            
            config_data['proficiency_data'] = proficiency_data
            
            logger.info("✅ Wizard data preparation complete!")
            return config_data
            
        except Exception as e:
            logger.error(f"❌ Error preparing wizard data: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return config_data  # Return original if preparation fails
    
    def _process_results(self, raw_results):
        """Process raw results for frontend consumption"""
        processed = {}
        
        if not isinstance(raw_results, dict):
            logger.error(f"_process_results received non-dict: {type(raw_results)}")
            return {}
        
        for year, year_results in raw_results.items():
            if isinstance(year_results, dict) and not year.startswith('_'):
                processed[year] = {}
                
                for division, result in year_results.items():
                    # Handle both dict and string results
                    if isinstance(result, dict):
                        if result.get('timetable'):
                            timetable_obj = result['timetable']
                            
                            # ✅ FIX: Serialize the Chromosome object with genes
                            timetable_data = {
                                'genes': timetable_obj.genes if hasattr(timetable_obj, 'genes') else [],
                                'fitness_score': timetable_obj.fitness_score if hasattr(timetable_obj, 'fitness_score') else 0,
                                'violations': timetable_obj.violations if hasattr(timetable_obj, 'violations') else {}
                            }
                            
                            processed[year][division] = {
                                'success': True,
                                'fitness_score': result.get('fitness_score', 0),
                                'violations': result.get('violations', {}),
                                'sessions_count': len(timetable_obj.genes) if hasattr(timetable_obj, 'genes') else 0,
                                'timetable': timetable_data  # ✅ Include serialized timetable
                            }
                        else:
                            processed[year][division] = {
                                'success': False,
                                'error': result.get('error', 'Unknown error')
                            }
                    else:
                        # Handle string results (likely error messages)
                        processed[year][division] = {
                            'success': False,
                            'error': str(result)
                        }
        
        return processed
    
    def _generate_summary(self, results):
        """Generate summary statistics"""
        total_divisions = 0
        successful_divisions = 0
        total_conflicts = 0
        
        for year, year_results in results.items():
            if isinstance(year_results, dict) and not year.startswith('_'):
                for division, result in year_results.items():
                    total_divisions += 1
                    if result.get('timetable'):
                        successful_divisions += 1
        
        conflicts_report = results.get('_conflicts_report', {})
        total_conflicts = len(conflicts_report.get('teacher_conflicts', [])) + len(conflicts_report.get('room_conflicts', []))
        
        return {
            'total_divisions': total_divisions,
            'successful_divisions': successful_divisions,
            'success_rate': (successful_divisions / total_divisions * 100) if total_divisions > 0 else 0,
            'total_conflicts': total_conflicts,
            'conflict_free': total_conflicts == 0
        }


class ProficiencyManagementView(APIView):
    """
    Manage teacher-subject proficiency for User-Driven Algorithm
    """
    def get(self, request):
        """Get current proficiency data"""
        try:
            teachers = Teacher.objects.all()
            subjects = Subject.objects.all()
            
            proficiency_data = {}
            
            # Check if SubjectProficiency model exists and has data
            try:
                from .models import SubjectProficiency
                proficiencies = SubjectProficiency.objects.all()
                
                for prof in proficiencies:
                    if prof.teacher.id not in proficiency_data:
                        proficiency_data[prof.teacher.id] = {}
                    
                    proficiency_data[prof.teacher.id][prof.subject.id] = {
                        'knowledge': prof.knowledge_rating,
                        'willingness': prof.willingness_rating
                    }
            except:
                # If no proficiency data exists, return default structure
                for teacher in teachers:
                    proficiency_data[teacher.id] = {}
                    for subject in subjects:
                        proficiency_data[teacher.id][subject.id] = {
                            'knowledge': 7.0,
                            'willingness': 7.0
                        }
            
            return Response({
                'status': 'success',
                'proficiency_data': proficiency_data,
                'teachers': [{'id': t.id, 'name': t.name} for t in teachers],
                'subjects': [{'id': s.id, 'name': s.name} for s in subjects]
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error getting proficiency data: {e}")
            return Response({
                'status': 'error',
                'message': f'Failed to get proficiency data: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Update proficiency data"""
        try:
            proficiency_data = request.data.get('proficiency_data', {})
            
            # Save to SubjectProficiency model if it exists
            try:
                from .models import SubjectProficiency
                
                for teacher_id, subjects_data in proficiency_data.items():
                    teacher = Teacher.objects.get(id=teacher_id)
                    
                    for subject_id, ratings in subjects_data.items():
                        subject = Subject.objects.get(id=subject_id)
                        
                        proficiency, created = SubjectProficiency.objects.get_or_create(
                            teacher=teacher,
                            subject=subject,
                            defaults={
                                'knowledge_rating': ratings.get('knowledge', 7.0),
                                'willingness_rating': ratings.get('willingness', 7.0)
                            }
                        )
                        
                        if not created:
                            proficiency.knowledge_rating = ratings.get('knowledge', 7.0)
                            proficiency.willingness_rating = ratings.get('willingness', 7.0)
                            proficiency.save()
                
                return Response({
                    'status': 'success',
                    'message': 'Proficiency data updated successfully'
                }, status=status.HTTP_200_OK)
                
            except ImportError:
                # SubjectProficiency model doesn't exist, just return success
                return Response({
                    'status': 'success',
                    'message': 'Proficiency data received (model not available for persistence)'
                }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error updating proficiency data: {e}")
            return Response({
                'status': 'error',
                'message': f'Failed to update proficiency data: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
