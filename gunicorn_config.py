"""
Production-optimized Gunicorn configuration for high load
Designed for Bot Factory AI performance under concurrent users
"""
import multiprocessing
import os

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = min(multiprocessing.cpu_count() * 2 + 1, 8)  # Cap at 8 workers
worker_class = "gthread"  # Use threads for I/O bound tasks
threads = 8  # 8 threads per worker for concurrent request handling
worker_connections = 1000

# Worker behavior
max_requests = 2000  # Restart worker after 2000 requests (prevents memory leaks)
max_requests_jitter = 200  # Add randomness to restart timing
preload_app = True  # Preload Flask app for faster worker startup
timeout = 120  # 2 minute timeout for long AI processing
keepalive = 30  # Keep connections alive for 30 seconds

# Logging
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'
accesslog = "-"  # Log to stdout
errorlog = "-"   # Log errors to stderr
capture_output = True

# SSL (if needed in production)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Performance tuning
worker_tmp_dir = "/dev/shm"  # Use RAM for temporary files (faster)
tmp_upload_dir = None

# Security
limit_request_line = 8192
limit_request_fields = 100
limit_request_field_size = 16384

# Development vs Production
reload = False  # Disable auto-reload in production
enable_stdio_inheritance = True

def when_ready(server):
    """Called just after the server is started"""
    server.log.info("Bot Factory AI server ready for high-load operation")
    server.log.info(f"Workers: {workers}, Threads per worker: {threads}")
    server.log.info(f"Total concurrent capacity: {workers * threads} requests")

def worker_int(worker):
    """Called when a worker receives an INT or QUIT signal"""
    worker.log.info("Worker shutting down gracefully")

def on_exit(server):
    """Called when gunicorn is about to exit"""
    server.log.info("Bot Factory AI server shutting down")

# Environment-specific settings
if os.environ.get("FLASK_ENV") == "development":
    reload = True
    loglevel = "debug"
    workers = 1  # Single worker in development
    
print(f"Gunicorn config loaded: {workers} workers, {threads} threads each")