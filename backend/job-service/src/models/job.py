"""
Job Domain Model
"""
from sqlalchemy import Column, String, Text, Integer, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
import enum

import sys
sys.path.append('../../shared')
from database import Base


class JobStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    DRAFT = "draft"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


class Job(Base):
    """Job entity"""
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employer_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    company_name = Column(String(255), nullable=False)
    required_skills = Column(JSONB, nullable=False, default=[])  # ["Python", "React", ...]
    required_technologies = Column(JSONB, nullable=False, default=[])  # ["AWS", "Docker", ...]
    experience_years = Column(Integer, default=0)
    location = Column(String(255), nullable=False)
    employment_type = Column(Enum(EmploymentType), nullable=False, default=EmploymentType.FULL_TIME)
    status = Column(Enum(JobStatus), nullable=False, default=JobStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': str(self.id),
            'employer_id': str(self.employer_id),
            'title': self.title,
            'description': self.description,
            'company_name': self.company_name,
            'required_skills': self.required_skills,
            'required_technologies': self.required_technologies,
            'experience_years': self.experience_years,
            'location': self.location,
            'employment_type': self.employment_type.value if isinstance(self.employment_type, EmploymentType) else self.employment_type,
            'status': self.status.value if isinstance(self.status, JobStatus) else self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
