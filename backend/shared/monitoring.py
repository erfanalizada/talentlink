"""
Monitoring and Metrics with Prometheus
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST, REGISTRY
from flask import Response, request
import time
from functools import wraps
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# GLOBAL SINGLETON METRICS - PREVENTS DUPLICATE REGISTRATION
# ============================================================================

# Use a module-level flag to prevent re-registration
_METRICS_INITIALIZED = False

def _initialize_metrics():
    """Initialize metrics only once globally"""
    global _METRICS_INITIALIZED
    global http_requests_total, http_request_duration_seconds, http_requests_in_progress
    global command_total, query_total, event_published_total, database_connections
    
    if _METRICS_INITIALIZED:
        logger.debug("Metrics already initialized, skipping...")
        return
    
    try:
        http_requests_total = Counter(
            "http_requests_total",
            "Total HTTP requests",
            ["method", "endpoint", "status"]
        )
        
        http_request_duration_seconds = Histogram(
            "http_request_duration_seconds",
            "HTTP request latency",
            ["method", "endpoint"]
        )
        
        http_requests_in_progress = Gauge(
            "http_requests_in_progress",
            "HTTP requests in progress",
            ["method", "endpoint"]
        )
        
        command_total = Counter(
            "cqrs_commands_total",
            "Total CQRS commands",
            ["command_type", "status"]
        )
        
        query_total = Counter(
            "cqrs_queries_total",
            "Total CQRS queries",
            ["query_type", "status"]
        )
        
        event_published_total = Counter(
            "events_published_total",
            "Total events published",
            ["event_type"]
        )
        
        database_connections = Gauge(
            "database_connections_active",
            "Active database connections"
        )
        
        _METRICS_INITIALIZED = True
        logger.info("✅ Prometheus metrics initialized successfully")
        
    except ValueError as e:
        # Metrics already registered (shouldn't happen with flag, but safety net)
        logger.warning(f"Metrics already registered: {e}")
        _METRICS_INITIALIZED = True


# Initialize metrics on module import
_initialize_metrics()


class MetricsMiddleware:
    """Flask middleware for Prometheus metrics"""
    
    def __init__(self, app, service_name: str):
        self.app = app
        self.service_name = service_name
        
        @app.route("/metrics")
        def metrics():
            """Expose Prometheus metrics endpoint"""
            return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
        
        # Register request hooks
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        
        logger.info(f"✅ Metrics middleware initialized for {service_name}")
    
    def _before_request(self):
        """Track request start time and in-progress requests"""
        request.start_time = time.time()
        http_requests_in_progress.labels(
            method=request.method,
            endpoint=request.path
        ).inc()
    
    def _after_request(self, response):
        """Track request completion metrics"""
        # Decrement in-progress counter
        http_requests_in_progress.labels(
            method=request.method,
            endpoint=request.path
        ).dec()
        
        # Increment total requests counter
        http_requests_total.labels(
            method=request.method,
            endpoint=request.path,
            status=response.status_code
        ).inc()
        
        # Record request duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.path
            ).observe(duration)
        
        return response


# ============================================================================
# CQRS TRACKING DECORATORS
# ============================================================================

def track_command(command_type: str):
    """Decorator to track CQRS command execution"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                command_total.labels(
                    command_type=command_type,
                    status="success"
                ).inc()
                return result
            except Exception as e:
                command_total.labels(
                    command_type=command_type,
                    status="error"
                ).inc()
                raise
        return wrapper
    return decorator


def track_query(query_type: str):
    """Decorator to track CQRS query execution"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)
                query_total.labels(
                    query_type=query_type,
                    status="success"
                ).inc()
                return result
            except Exception as e:
                query_total.labels(
                    query_type=query_type,
                    status="error"
                ).inc()
                raise
        return wrapper
    return decorator


def track_event(event_type: str):
    """Track event publication"""
    event_published_total.labels(event_type=event_type).inc()