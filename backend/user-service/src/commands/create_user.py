"""
Create User Command and Handler
"""
from dataclasses import dataclass
from typing import Optional
import uuid

import sys
sys.path.append('../../shared')
from cqrs_base import Command, CommandHandler, Result
from database import Database
from event_bus import RabbitMQEventBus

from ..models.user import User, UserRole
from ..events.user_events import UserCreatedEvent


@dataclass
class CreateUserCommand(Command):
    """Command to create a new user"""
    keycloak_id: str
    email: str
    full_name: str
    role: str
    company_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None


class CreateUserHandler(CommandHandler[CreateUserCommand, Result]):
    """Handler for CreateUserCommand"""

    def __init__(self, db: Database, event_bus: RabbitMQEventBus):
        self.db = db
        self.event_bus = event_bus

    async def handle(self, command: CreateUserCommand) -> Result:
        """Create a new user"""
        try:
            with self.db.get_db_session() as session:
                # Check if user already exists
                existing = session.query(User).filter(
                    (User.keycloak_id == command.keycloak_id) |
                    (User.email == command.email)
                ).first()

                if existing:
                    return Result.fail(f"User already exists with email: {command.email}")

                # Create user
                user = User(
                    id=uuid.uuid4(),
                    keycloak_id=command.keycloak_id,
                    email=command.email,
                    full_name=command.full_name,
                    role=UserRole(command.role),
                    company_name=command.company_name,
                    phone=command.phone,
                    location=command.location
                )

                session.add(user)
                session.flush()

                user_dict = user.to_dict()

                # Publish event
                event = UserCreatedEvent(
                    aggregate_id=str(user.id),
                    user_id=str(user.id),
                    email=user.email,
                    role=command.role,
                    full_name=user.full_name
                )
                await self.event_bus.publish(event, routing_key="user.created")

                return Result.ok(user_dict)

        except Exception as e:
            return Result.fail(f"Failed to create user: {str(e)}")
