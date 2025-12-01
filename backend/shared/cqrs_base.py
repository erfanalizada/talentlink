"""
CQRS Base Classes
Provides foundation for Command Query Responsibility Segregation pattern
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar, Dict, List
from datetime import datetime
import uuid


# ============================================================================
# COMMANDS (Write Operations)
# ============================================================================

@dataclass
class Command(ABC):
    """Base class for all commands"""
    command_id: str = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.command_id is None:
            self.command_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


TCommand = TypeVar('TCommand', bound=Command)
TCommandResult = TypeVar('TCommandResult')


class CommandHandler(ABC, Generic[TCommand, TCommandResult]):
    """Base class for command handlers"""

    @abstractmethod
    async def handle(self, command: TCommand) -> TCommandResult:
        """Execute the command and return result"""
        pass


# ============================================================================
# QUERIES (Read Operations)
# ============================================================================

@dataclass
class Query(ABC):
    """Base class for all queries"""
    query_id: str = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.query_id is None:
            self.query_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


TQuery = TypeVar('TQuery', bound=Query)
TQueryResult = TypeVar('TQueryResult')


class QueryHandler(ABC, Generic[TQuery, TQueryResult]):
    """Base class for query handlers"""

    @abstractmethod
    async def handle(self, query: TQuery) -> TQueryResult:
        """Execute the query and return result"""
        pass


# ============================================================================
# EVENTS (Domain Events)
# ============================================================================

@dataclass
class DomainEvent(ABC):
    """Base class for domain events"""
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = field(default=None)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    aggregate_id: str = field(default=None)

    def __post_init__(self):
        if self.event_type is None:
            self.event_type = self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for serialization"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'timestamp': self.timestamp.isoformat(),
            'aggregate_id': self.aggregate_id,
            'payload': self._payload()
        }

    @abstractmethod
    def _payload(self) -> Dict[str, Any]:
        """Return event-specific payload"""
        pass


# ============================================================================
# EVENT BUS
# ============================================================================

class EventBus(ABC):
    """Abstract event bus for publishing events"""

    @abstractmethod
    async def publish(self, event: DomainEvent, routing_key: str = None):
        """Publish an event to the event bus"""
        pass

    @abstractmethod
    async def subscribe(self, event_type: str, handler: callable):
        """Subscribe to events of a specific type"""
        pass


# ============================================================================
# COMMAND/QUERY BUS (Mediator Pattern)
# ============================================================================

class CommandBus:
    """Mediator for dispatching commands to handlers"""

    def __init__(self):
        self._handlers: Dict[type, CommandHandler] = {}

    def register(self, command_type: type, handler: CommandHandler):
        """Register a command handler"""
        self._handlers[command_type] = handler

    async def send(self, command: Command) -> Any:
        """Send a command to its handler"""
        handler = self._handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for {type(command).__name__}")
        return await handler.handle(command)


class QueryBus:
    """Mediator for dispatching queries to handlers"""

    def __init__(self):
        self._handlers: Dict[type, QueryHandler] = {}

    def register(self, query_type: type, handler: QueryHandler):
        """Register a query handler"""
        self._handlers[query_type] = handler

    async def send(self, query: Query) -> Any:
        """Send a query to its handler"""
        handler = self._handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler registered for {type(query).__name__}")
        return await handler.handle(query)


# ============================================================================
# RESULT WRAPPER
# ============================================================================

@dataclass
class Result:
    """Wrapper for operation results"""
    success: bool
    data: Any = None
    error: str = None
    errors: List[str] = None

    @staticmethod
    def ok(data: Any = None) -> 'Result':
        """Create a successful result"""
        return Result(success=True, data=data)

    @staticmethod
    def fail(error: str, errors: List[str] = None) -> 'Result':
        """Create a failed result"""
        return Result(success=False, error=error, errors=errors or [])
