"""
User Domain Model
"""
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

import sys
sys.path.append('../../shared')
from database import Base


class UserRole(str, enum.Enum):
    EMPLOYEE = "employee"
    EMPLOYER = "employer"


class User(Base):
    """User entity"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    keycloak_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    full_name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    company_name = Column(String(255), nullable=True)  # For employers
    phone = Column(String(50), nullable=True)
    location = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'keycloak_id': self.keycloak_id,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role.value if isinstance(self.role, UserRole) else self.role,
            'company_name': self.company_name,
            'phone': self.phone,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
