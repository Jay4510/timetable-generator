"""
Real-time collaboration and workflow management system for timetable generation.
Handles multi-user editing, approval workflows, and change management.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from channels.generic.websocket import AsyncWebsocketConsumer
import json
import asyncio
from enum import Enum
from datetime import datetime, timedelta

class UserRole(models.Model):
    """Define user roles and permissions"""
    ROLE_CHOICES = [
        ('admin', 'System Administrator'),
        ('academic_head', 'Academic Head'),
        ('hod', 'Head of Department'),
        ('faculty', 'Faculty Member'),
        ('timetable_coordinator', 'Timetable Coordinator'),
        ('student_representative', 'Student Representative'),
        ('viewer', 'View Only'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    department = models.CharField(max_length=100, blank=True)
    permissions = models.JSONField(default=dict)
    
    # Delegation and temporary permissions
    can_delegate = models.BooleanField(default=False)
    delegated_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='delegated_from')
    delegation_expires = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class TimetableVersion(models.Model):
    """Version control for timetables"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    version_number = models.CharField(max_length=20)
    name = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_versions')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Approval workflow
    submitted_for_review_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_versions')
    approved_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Change tracking
    parent_version = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    change_summary = models.TextField(blank=True)
    
    # Metadata
    semester = models.CharField(max_length=20)
    academic_year = models.CharField(max_length=10)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Version {self.version_number} - {self.name}"

class ChangeRequest(models.Model):
    """Handle change requests and approvals"""
    CHANGE_TYPES = [
        ('add_session', 'Add Session'),
        ('remove_session', 'Remove Session'),
        ('modify_session', 'Modify Session'),
        ('swap_sessions', 'Swap Sessions'),
        ('bulk_change', 'Bulk Change'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    request_id = models.CharField(max_length=20, unique=True)
    change_type = models.CharField(max_length=20, choices=CHANGE_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # Request details
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='change_requests')
    requested_at = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()
    change_details = models.JSONField()
    
    # Approval workflow
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_changes')
    reviewed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='reviewed_changes')
    approved_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_changes')
    
    # Timestamps
    review_started_at = models.DateTimeField(null=True, blank=True)
    decision_made_at = models.DateTimeField(null=True, blank=True)
    implemented_at = models.DateTimeField(null=True, blank=True)
    
    # Impact analysis
    affected_teachers = models.JSONField(default=list)
    affected_students = models.JSONField(default=list)
    affected_rooms = models.JSONField(default=list)
    impact_score = models.FloatField(default=0.0)
    
    # Comments and feedback
    reviewer_comments = models.TextField(blank=True)
    implementation_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.request_id} - {self.change_type} ({self.status})"

class CollaborationSession(models.Model):
    """Track collaborative editing sessions"""
    session_id = models.CharField(max_length=50, unique=True)
    timetable_version = models.ForeignKey(TimetableVersion, on_delete=models.CASCADE)
    
    # Session details
    started_by = models.ForeignKey(User, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Participants
    active_users = models.JSONField(default=list)
    max_concurrent_users = models.IntegerField(default=0)
    
    # Session state
    is_active = models.BooleanField(default=True)
    locked_elements = models.JSONField(default=dict)  # Track locked sessions/rooms/teachers
    
    def __str__(self):
        return f"Collaboration Session {self.session_id}"

class RealTimeEdit(models.Model):
    """Track real-time edits for conflict resolution"""
    collaboration_session = models.ForeignKey(CollaborationSession, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Edit details
    edit_type = models.CharField(max_length=20)
    target_element = models.CharField(max_length=100)  # session_id, room_id, etc.
    old_value = models.JSONField(null=True, blank=True)
    new_value = models.JSONField()
    
    # Timing
    timestamp = models.DateTimeField(auto_now_add=True)
    applied_at = models.DateTimeField(null=True, blank=True)
    
    # Conflict resolution
    conflicts_with = models.ManyToManyField('self', blank=True)
    resolution_strategy = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"Edit by {self.user.username} at {self.timestamp}"

class NotificationSystem(models.Model):
    """Notification system for timetable changes"""
    NOTIFICATION_TYPES = [
        ('change_request', 'Change Request'),
        ('approval_needed', 'Approval Needed'),
        ('change_approved', 'Change Approved'),
        ('change_rejected', 'Change Rejected'),
        ('conflict_detected', 'Conflict Detected'),
        ('deadline_reminder', 'Deadline Reminder'),
        ('system_alert', 'System Alert'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    read_at = models.DateTimeField(null=True, blank=True)
    is_urgent = models.BooleanField(default=False)
    
    # Related objects
    related_change_request = models.ForeignKey(ChangeRequest, null=True, blank=True, on_delete=models.CASCADE)
    related_version = models.ForeignKey(TimetableVersion, null=True, blank=True, on_delete=models.CASCADE)
    
    # Action buttons
    action_buttons = models.JSONField(default=list)
    
    def __str__(self):
        return f"Notification for {self.recipient.username}: {self.title}"

class WorkflowEngine:
    """Manages approval workflows and business rules"""
    
    def __init__(self):
        self.workflow_rules = self.load_workflow_rules()
    
    def process_change_request(self, change_request):
        """Process a change request through the approval workflow"""
        workflow_steps = self.get_workflow_steps(change_request)
        
        for step in workflow_steps:
            result = self.execute_workflow_step(change_request, step)
            if not result['success']:
                return result
        
        return {'success': True, 'message': 'Change request processed successfully'}
    
    def get_workflow_steps(self, change_request):
        """Get required workflow steps based on change type and impact"""
        steps = []
        
        # Determine approval requirements based on impact
        if change_request.impact_score > 0.8:
            steps.extend(['hod_approval', 'academic_head_approval'])
        elif change_request.impact_score > 0.5:
            steps.append('hod_approval')
        else:
            steps.append('coordinator_approval')
        
        # Add notification steps
        steps.append('notify_affected_parties')
        
        return steps
    
    def execute_workflow_step(self, change_request, step):
        """Execute a single workflow step"""
        if step == 'hod_approval':
            return self.request_hod_approval(change_request)
        elif step == 'academic_head_approval':
            return self.request_academic_head_approval(change_request)
        elif step == 'coordinator_approval':
            return self.request_coordinator_approval(change_request)
        elif step == 'notify_affected_parties':
            return self.notify_affected_parties(change_request)
        
        return {'success': False, 'message': f'Unknown workflow step: {step}'}
    
    def load_workflow_rules(self):
        """Load workflow rules from configuration"""
        return {
            'approval_hierarchy': ['coordinator', 'hod', 'academic_head'],
            'auto_approval_threshold': 0.1,
            'urgent_escalation_hours': 24,
            'notification_rules': {
                'high_impact': ['all_affected', 'management'],
                'medium_impact': ['affected_teachers', 'coordinator'],
                'low_impact': ['affected_teachers']
            }
        }

class RealTimeCollaborationConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time collaboration"""
    
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'collaboration_{self.session_id}'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Notify others of new user
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'user': self.scope['user'].username
            }
        )
    
    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
        # Notify others of user leaving
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'user': self.scope['user'].username
            }
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data['type']
        
        if message_type == 'edit_session':
            await self.handle_session_edit(data)
        elif message_type == 'lock_element':
            await self.handle_element_lock(data)
        elif message_type == 'unlock_element':
            await self.handle_element_unlock(data)
        elif message_type == 'cursor_position':
            await self.handle_cursor_update(data)
    
    async def handle_session_edit(self, data):
        """Handle real-time session editing"""
        # Validate edit permissions
        if not await self.check_edit_permission(data):
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Insufficient permissions'
            }))
            return
        
        # Check for conflicts
        conflicts = await self.check_edit_conflicts(data)
        if conflicts:
            await self.send(text_data=json.dumps({
                'type': 'conflict',
                'conflicts': conflicts
            }))
            return
        
        # Apply edit and broadcast to all users
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'session_edited',
                'edit_data': data,
                'user': self.scope['user'].username
            }
        )
    
    async def session_edited(self, event):
        """Send session edit to WebSocket"""
        await self.send(text_data=json.dumps({
            'type': 'session_edited',
            'edit_data': event['edit_data'],
            'user': event['user']
        }))

class ConflictResolver:
    """Handles conflicts in collaborative editing"""
    
    def __init__(self):
        self.resolution_strategies = {
            'last_write_wins': self.last_write_wins,
            'merge_changes': self.merge_changes,
            'manual_resolution': self.manual_resolution,
            'priority_based': self.priority_based_resolution
        }
    
    def resolve_conflict(self, conflict_data):
        """Resolve editing conflicts"""
        strategy = self.determine_resolution_strategy(conflict_data)
        return self.resolution_strategies[strategy](conflict_data)
    
    def determine_resolution_strategy(self, conflict_data):
        """Determine the best resolution strategy for a conflict"""
        # Simple heuristic - can be made more sophisticated
        if conflict_data['conflict_type'] == 'simultaneous_edit':
            return 'priority_based'
        elif conflict_data['conflict_type'] == 'overlapping_changes':
            return 'merge_changes'
        else:
            return 'manual_resolution'
    
    def last_write_wins(self, conflict_data):
        """Simple last-write-wins resolution"""
        return {
            'resolution': 'accepted',
            'final_value': conflict_data['latest_change'],
            'strategy': 'last_write_wins'
        }
    
    def priority_based_resolution(self, conflict_data):
        """Resolve based on user priority/role"""
        user_priorities = self.get_user_priorities(conflict_data['users'])
        highest_priority_user = max(user_priorities, key=user_priorities.get)
        
        return {
            'resolution': 'accepted',
            'final_value': conflict_data['changes'][highest_priority_user],
            'strategy': 'priority_based',
            'winning_user': highest_priority_user
        }

class IntegrationManager:
    """Manages integrations with external systems"""
    
    def __init__(self):
        self.integrations = {
            'student_information_system': self.sis_integration,
            'learning_management_system': self.lms_integration,
            'room_booking_system': self.room_booking_integration,
            'email_system': self.email_integration,
            'mobile_app': self.mobile_app_integration
        }
    
    def sync_with_sis(self, timetable_data):
        """Sync timetable with Student Information System"""
        # Implementation for SIS integration
        pass
    
    def update_lms(self, schedule_changes):
        """Update Learning Management System with schedule changes"""
        # Implementation for LMS integration
        pass
    
    def book_rooms(self, room_requirements):
        """Integrate with room booking system"""
        # Implementation for room booking integration
        pass
    
    def send_notifications(self, notification_data):
        """Send notifications via email/SMS"""
        # Implementation for notification system integration
        pass

# Export main classes
__all__ = [
    'UserRole', 'TimetableVersion', 'ChangeRequest', 'CollaborationSession',
    'WorkflowEngine', 'ConflictResolver', 'IntegrationManager'
]
