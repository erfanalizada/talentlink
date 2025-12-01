"""
Application Domain Model
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import enum

import sys
sys.path.append('../../shared')
from database import Base


class ApplicationStatus(str, enum.Enum):
    PENDING = "pending"
    REVIEWED = "reviewed"
    INVITED = "invited"
    REJECTED = "rejected"


class Application(Base):
    """Job Application entity"""
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    cv_id = Column(UUID(as_uuid=True), nullable=True)
    status = Column(Enum(ApplicationStatus), nullable=False, default=ApplicationStatus.PENDING)
    match_score = Column(Integer, nullable=True)  # 0-100
    match_summary = Column(Text, nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'job_id': str(self.job_id),
            'employee_id': str(self.employee_id),
            'cv_id': str(self.cv_id) if self.cv_id else None,
            'status': self.status.value if isinstance(self.status, ApplicationStatus) else self.status,
            'match_score': self.match_score,
            'match_summary': self.match_summary,
            'applied_at': self.applied_at.isoformat() if self.applied_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
