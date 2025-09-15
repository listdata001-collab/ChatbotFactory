#!/usr/bin/env python3
"""
Celery worker startup script for async task processing
Run this in a separate process: python celery_worker.py
"""
import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Celery app
from celery_app import celery
from app import app

# Import all task modules to register them
import tasks

if __name__ == '__main__':
    # Configure Celery worker
    celery.worker_main([
        'worker',
        '--loglevel=info',
        '--concurrency=4',  # Number of worker processes
        '--max-tasks-per-child=1000',  # Restart worker after 1000 tasks
        '--time-limit=300',  # 5 minute task timeout
        '--soft-time-limit=240',  # 4 minute soft timeout
        '--without-heartbeat',  # Disable heartbeat for simplicity
        '--pool=threads',  # Use thread pool for I/O bound tasks
    ])