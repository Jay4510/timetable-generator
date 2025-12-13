from django.urls import path
from . import views
from . import task_tracker

urlpatterns = [
    # Teacher URLs
    path('teachers/', views.TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('teachers/<int:pk>/', views.TeacherDetailView.as_view(), name='teacher-detail'),
    
    # Year URLs
    path('years/', views.YearListCreateView.as_view(), name='year-list-create'),
    path('years/<int:pk>/', views.YearDetailView.as_view(), name='year-detail'),
    
    # Division URLs
    path('divisions/', views.DivisionListCreateView.as_view(), name='division-list-create'),
    path('divisions/<int:pk>/', views.DivisionDetailView.as_view(), name='division-detail'),
    
    # Room URLs
    path('rooms/', views.RoomListCreateView.as_view(), name='room-list-create'),
    path('rooms/<int:pk>/', views.RoomDetailView.as_view(), name='room-detail'),
    
    # Lab URLs
    path('labs/', views.LabListCreateView.as_view(), name='lab-list-create'),
    path('labs/<int:pk>/', views.LabDetailView.as_view(), name='lab-detail'),
    
    # Subject URLs
    path('subjects/', views.SubjectListCreateView.as_view(), name='subject-list-create'),
    path('subjects/<int:pk>/', views.SubjectDetailView.as_view(), name='subject-detail'),
    
    # TimeSlot URLs
    path('timeslots/', views.TimeSlotListCreateView.as_view(), name='timeslot-list-create'),
    path('timeslots/<int:pk>/', views.TimeSlotDetailView.as_view(), name='timeslot-detail'),
    
    # Session URLs
    path('sessions/', views.SessionListCreateView.as_view(), name='session-list-create'),
    path('sessions/<int:pk>/', views.SessionDetailView.as_view(), name='session-detail'),
    
    # Timetable Version URLs
    path('timetable-versions/', views.TimetableVersionListCreateView.as_view(), name='timetable-version-list-create'),
    path('timetable-versions/<int:pk>/', views.TimetableVersionDetailView.as_view(), name='timetable-version-detail'),
    
    # Custom API endpoints
    path('generate-timetable/', views.GenerateTimetableView.as_view(), name='generate-timetable'),
    path('timetable/', views.TimetableView.as_view(), name='get-current-timetable'),
    path('constraints-report/', views.get_constraints_report, name='constraints-report'),
    path('manual-assign/', views.manual_assign, name='manual-assign'),
    
    # Enhanced endpoints for real-world functionality
    path('api/divisions-list/', views.get_divisions, name='divisions-list'),
    path('api/system-configuration/', views.system_configuration, name='system-configuration'),
    path('api/remedial-lectures/', views.remedial_lectures, name='remedial-lectures'),
    path('teacher-preferences/', views.submit_teacher_preferences, name='teacher-preferences'),
    path('teacher-replacement/', views.handle_teacher_replacement, name='teacher-replacement'),
    path('timetable-analytics/', views.get_timetable_analytics, name='timetable-analytics'),
    
    # New improved endpoints
    path('teacher-resignation/', views.TeacherResignationView.as_view(), name='teacher-resignation'),
    path('timetable-config/', views.TimetableConfigurationView.as_view(), name='timetable-config'),
    
    # Task progress tracking
    path('task-progress/', task_tracker.get_task_progress, name='task-progress'),
    
    # Data reset endpoints
    path('reset-teachers/', views.reset_teachers, name='reset-teachers'),
    path('reset-subjects/', views.reset_subjects, name='reset-subjects'),
    path('reset-rooms/', views.reset_rooms, name='reset-rooms'),
    path('reset-timetable/', views.reset_timetable, name='reset-timetable'),
    
    # Division-specific timetable endpoints
    path('division-timetable/', views.DivisionTimetableView.as_view(), name='division-timetable-all'),
    path('division-timetable/<str:year_name>/<str:division_name>/', views.DivisionTimetableView.as_view(), name='division-timetable-specific'),
    
    # User-Driven Algorithm endpoints
    path('user-driven/test/', views.test_user_driven_import, name='user-driven-test'),
    path('user-driven/init/', views.initialize_basic_data, name='user-driven-init'),
    path('user-driven/config/', views.UserDrivenConfigurationView.as_view(), name='user-driven-config'),
    path('user-driven/generate/', views.UserDrivenGenerationView.as_view(), name='user-driven-generate'),
    path('user-driven/proficiency/', views.ProficiencyManagementView.as_view(), name='proficiency-management'),
    path('division-results/<int:division_id>/', views.DivisionTimetableResultsView.as_view(), name='division-results'),
]