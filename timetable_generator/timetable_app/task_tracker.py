from django.http import JsonResponse
from celery.result import AsyncResult
from celery import current_app
import json

# In-memory task progress storage
task_progress = {}

def update_task_progress(task_id: str, progress: int, status: str):
    """Update the progress of a task"""
    task_progress[task_id] = {
        'progress': progress,
        'status': status,
        'complete': progress >= 100
    }

def get_task_progress(request):
    """API endpoint to get the progress of a task"""
    task_id = request.GET.get('task_id')
    if not task_id:
        return JsonResponse({'error': 'No task_id provided'}, status=400)
    
    task = AsyncResult(task_id)
    response_data = {
        'task_id': task_id,
        'status': task.status,
        'progress': task_progress.get(task_id, {}).get('progress', 0),
        'status_text': task_progress.get(task_id, {}).get('status', 'Pending')
    }
    
    if task.ready():
        response_data['progress'] = 100
        response_data['status_text'] = 'Complete'
        
    return JsonResponse(response_data)
