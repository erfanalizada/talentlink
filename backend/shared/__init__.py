"""
Shared CQRS and Infrastructure Components

This package provides shared functionality for all TalentLink microservices.
"""
from .cqrs_base import (
    Command, CommandHandler, CommandBus,
    Query, QueryHandler, QueryBus,
    DomainEvent, EventBus, Result
)
from .event_bus import RabbitMQEventBus
from .database import Database, parse_database_url
from .monitoring import MetricsMiddleware, track_command, track_query, track_event
from .auth import require_auth, require_role, get_current_user, decode_token

__all__ = [
    # CQRS
    'Command', 'CommandHandler', 'CommandBus',
    'Query', 'QueryHandler', 'QueryBus',
    'DomainEvent', 'EventBus', 'Result',
    # Event Bus
    'RabbitMQEventBus',
    # Database
    'Database', 'parse_database_url',
    # Monitoring
    'MetricsMiddleware', 'track_command', 'track_query', 'track_event',
    # Auth
    'require_auth', 'require_role', 'get_current_user', 'decode_token'
]
