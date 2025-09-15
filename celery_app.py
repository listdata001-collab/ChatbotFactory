"""
Celery configuration for async task processing
Handles AI responses and heavy operations to improve performance
"""
import os
from celery import Celery

def make_celery(app=None):
    """Create Celery instance for async tasks"""
    # Use Redis as broker and result backend
    redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
    
    celery = Celery(
        'botfactory',
        broker=redis_url,
        backend=redis_url,
        include=['tasks']  # Import task modules
    )
    
    # Configure Celery for optimal performance
    celery.conf.update(
        # Task routing and execution
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Tashkent',
        enable_utc=True,
        
        # Performance optimization
        task_acks_late=True,              # Acknowledge after completion
        worker_prefetch_multiplier=4,     # Prefetch 4 tasks per worker
        task_routes={
            'tasks.generate_ai_response': {'queue': 'ai_responses'},
            'tasks.process_audio': {'queue': 'media_processing'},
            'tasks.send_telegram_message': {'queue': 'notifications'},
        },
        
        # Retry configuration
        task_default_retry_delay=60,      # Retry after 60 seconds
        task_max_retries=3,               # Max 3 retries
        
        # Result expiration
        result_expires=3600,              # Results expire after 1 hour
        
        # Worker configuration
        worker_hijack_root_logger=False,  # Don't hijack logging
        worker_log_color=False,           # Disable colors in production
    )
    
    if app:
        # Update task base classes on application context
        class ContextTask(celery.Task):
            """Make celery tasks work with Flask app context."""
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)
        
        celery.Task = ContextTask
    
    return celery

# Create Celery instance
celery = make_celery()