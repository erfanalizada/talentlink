
"""CQRS Base Classes"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar, Dict, List
from datetime import datetime
import uuid

# ============================================================================
# COMMANDS
# ============================================================================

@dataclass
class Command(ABC):
    command_id: str = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.command_id is None:
            self.command_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


TCommand = TypeVar("TCommand", bound=Command)
TCommandResult = TypeVar("TCommandResult")


class CommandHandler(ABC, Generic[TCommand, TCommandResult]):
    @abstractmethod
    async def handle(self, command: TCommand) -> TCommandResult:
        pass


# ============================================================================
# QUERIES
# ============================================================================

@dataclass
class Query(ABC):
    query_id: str = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.query_id is None:
            self.query_id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()


TQuery = TypeVar("TQuery", bound=Query)
TQueryResult = TypeVar("TQueryResult")


class QueryHandler(ABC, Generic[TQuery, TQueryResult]):
    @abstractmethod
    async def handle(self, query: TQuery) -> TQueryResult:
        pass


# ============================================================================
# EVENTS (FIXED)
# ============================================================================

@dataclass
class DomainEvent(ABC):
    aggregate_id: str  # REQUIRED FIRST

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = field(default=None)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.event_type is None:
            self.event_type = self.__class__.__name__

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "aggregate_id": self.aggregate_id,
            "payload": self._payload(),
        }

    @abstractmethod
    def _payload(self) -> Dict[str, Any]:
        pass


# ============================================================================
# EVENT BUS
# ============================================================================

class EventBus(ABC):
    @abstractmethod
    async def publish(self, event: DomainEvent, routing_key: str = None):
        pass

    @abstractmethod
    async def subscribe(self, event_type: str, handler: callable):
        pass


# ============================================================================
# MEDIATOR
# ============================================================================

class CommandBus:
    def __init__(self):
        self._handlers: Dict[type, CommandHandler] = {}

    def register(self, command_type: type, handler: CommandHandler):
        self._handlers[command_type] = handler

    async def send(self, command: Command):
        handler = self._handlers.get(type(command))
        if not handler:
            raise ValueError(f"No handler registered for {type(command).__name__}")
        return await handler.handle(command)


class QueryBus:
    def __init__(self):
        self._handlers: Dict[type, QueryHandler] = {}

    def register(self, query_type: type, handler: QueryHandler):
        self._handlers[query_type] = handler

    async def send(self, query: Query):
        handler = self._handlers.get(type(query))
        if not handler:
            raise ValueError(f"No handler registered for {type(query).__name__}")
        return await handler.handle(query)


# ============================================================================
# RESULT
# ============================================================================

@dataclass
class Result:
    success: bool
    data: Any = None
    error: str = None
    errors: List[str] = None

    @staticmethod
    def ok(data=None):
        return Result(success=True, data=data)

    @staticmethod
    def fail(error, errors=None):
        return Result(success=False, error=error, errors=errors or [])
