"""
Update User Command and Handler
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any

import sys
sys.path.append('../../shared')
from cqrs_base import Command, CommandHandler, Result
from database import Database
from event_bus import RabbitMQEventBus

from ..models.user import User
from ..events.user_events import UserUpdatedEvent


@dataclass
class UpdateUserCommand(Command):
    """Command to update user profile"""
    user_id: str
    full_name: Optional[str] = None
    company_name: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None


class UpdateUserHandler(CommandHandler[UpdateUserCommand, Result]):
    """Handler for UpdateUserCommand"""

    def __init__(self, db: Database, event_bus: RabbitMQEventBus):
        self.db = db
        self.event_bus = event_bus

    async def handle(self, command: UpdateUserCommand) -> Result:
        """Update user profile"""
        try:
            with self.db.get_db_session() as session:
                user = session.query(User).filter(User.id == command.user_id).first()

                if not user:
                    return Result.fail(f"User not found: {command.user_id}")

                # Track updated fields
                updated_fields = {}

                if command.full_name is not None:
                    user.full_name = command.full_name
                    updated_fields['full_name'] = command.full_name

                if command.company_name is not None:
                    user.company_name = command.company_name
                    updated_fields['company_name'] = command.company_name

                if command.phone is not None:
                    user.phone = command.phone
                    updated_fields['phone'] = command.phone

                if command.location is not None:
                    user.location = command.location
                    updated_fields['location'] = command.location

                session.flush()

                # Publish event
                if updated_fields:
                    event = UserUpdatedEvent(
                        aggregate_id=str(user.id),
                        user_id=str(user.id),
                        updated_fields=updated_fields
                    )
                    await self.event_bus.publish(event, routing_key="user.updated")

                return Result.ok(user.to_dict())

        except Exception as e:
            return Result.fail(f"Failed to update user: {str(e)}")
