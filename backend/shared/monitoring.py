"""
Prometheus Monitoring Middleware
Lightweight metrics collection for all services
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import Response, request
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests in progress',
    ['method', 'endpoint']
)

command_total = Counter(
    'cqrs_commands_total',
    'Total CQRS commands executed',
    ['command_type', 'status']
)

query_total = Counter(
    'cqrs_queries_total',
    'Total CQRS queries executed',
    ['query_type', 'status']
)

event_published_total = Counter(
    'events_published_total',
    'Total events published',
    ['event_type']
)

database_connections = Gauge(
    'database_connections_active',
    'Active database connections'
)


class MetricsMiddleware:
    """Flask middleware for automatic metrics collection"""

    def __init__(self, app, service_name: str):
        self.app = app
        self.service_name = service_name

        # Register metrics endpoint
        @app.route('/metrics')
        def metrics():
            return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

        # Register health endpoint
        @app.route('/health')
        def health():
            return {'status': 'healthy', 'service': service_name}, 200

        # Apply middleware
        app.before_request(self._before_request)
        app.after_request(self._after_request)

        logger.info(f"Metrics middleware initialized for {service_name}")

    def _before_request(self):
        """Track request start"""
        request.start_time = time.time()
        endpoint = request.endpoint or 'unknown'
        http_requests_in_progress.labels(method=request.method, endpoint=endpoint).inc()

    def _after_request(self, response):
        """Track request completion"""
        endpoint = request.endpoint or 'unknown'

        # Decrement in-progress
        http_requests_in_progress.labels(method=request.method, endpoint=endpoint).dec()

        # Increment total
        http_requests_total.labels(
            method=request.method,
            endpoint=endpoint,
            status=response.status_code
        ).inc()

        # Record duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)

        return response


def track_command(command_type: str):
    """Decorator to track CQRS commands"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                command_total.labels(command_type=command_type, status='success').inc()
                return result
            except Exception as e:
                command_total.labels(command_type=command_type, status='error').inc()
                raise
        return wrapper
    return decorator


def track_query(query_type: str):
    """Decorator to track CQRS queries"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                query_total.labels(query_type=query_type, status='success').inc()
                return result
            except Exception as e:
                query_total.labels(query_type=query_type, status='error').inc()
                raise
        return wrapper
    return decorator


def track_event(event_type: str):
    """Track event publication"""
    event_published_total.labels(event_type=event_type).inc()
