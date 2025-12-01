"""
User Domain Events
"""
from dataclasses import dataclass
from typing import Dict, Any

import sys
sys.path.append('../../shared')
from cqrs_base import DomainEvent


@dataclass
class UserCreatedEvent(DomainEvent):
    """Event raised when a user is created"""
    user_id: str
    email: str
    role: str
    full_name: str

    def _payload(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'email': self.email,
            'role': self.role,
            'full_name': self.full_name
        }


@dataclass
class UserUpdatedEvent(DomainEvent):
    """Event raised when a user profile is updated"""
    user_id: str
    updated_fields: Dict[str, Any]

    def _payload(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'updated_fields': self.updated_fields
        }


@dataclass
class UserDeletedEvent(DomainEvent):
    """Event raised when a user is deleted"""
    user_id: str

    def _payload(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id
        }
