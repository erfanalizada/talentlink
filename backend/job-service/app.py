"""
Job Service - CQRS Implementation
Handles job posting and search for ICT positions
"""
import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import asyncio
from dataclasses import dataclass
from typing import Optional, List
import uuid

# Add shared library to path
sys.path.append('../shared')
from database import Database
from event_bus import RabbitMQEventBus
from monitoring import MetricsMiddleware
from auth import require_auth, require_role, get_current_user
from cqrs_base import Command, CommandHandler, Query, QueryHandler, Result, DomainEvent

from src.models.job import Job, JobStatus, EmploymentType

# Load environment
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://talentlink-erfan.nl", "http://localhost:*"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "expose_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Initialize infrastructure
database = Database(os.getenv("DATABASE_URL"), "jobsdb")
event_bus = RabbitMQEventBus(os.getenv("RABBITMQ_URL"))

# Initialize monitoring
MetricsMiddleware(app, "job-service")

# Initialize database schema
try:
    database.init_schema()
    print("✅ Database schema initialized")
except Exception as e:
    print(f"⚠️  Database schema initialization: {e}")


# ============================================================================
# COMMANDS
# ============================================================================

@dataclass
class CreateJobCommand(Command):
    employer_id: str
    title: str
    description: str
    company_name: str
    required_skills: List[str]
    required_technologies: List[str]
    experience_years: int
    location: str
    employment_type: str


@dataclass
class UpdateJobCommand(Command):
    job_id: str
    employer_id: str  # For authorization
    title: Optional[str] = None
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    required_technologies: Optional[List[str]] = None
    experience_years: Optional[int] = None
    location: Optional[str] = None
    employment_type: Optional[str] = None
    status: Optional[str] = None


@dataclass
class DeleteJobCommand(Command):
    job_id: str
    employer_id: str  # For authorization


# Command Handlers
class CreateJobHandler(CommandHandler[CreateJobCommand, Result]):
    def __init__(self, db: Database, event_bus: RabbitMQEventBus):
        self.db = db
        self.event_bus = event_bus

    async def handle(self, command: CreateJobCommand) -> Result:
        try:
            with self.db.get_db_session() as session:
                job = Job(
                    id=uuid.uuid4(),
                    employer_id=command.employer_id,
                    title=command.title,
                    description=command.description,
                    company_name=command.company_name,
                    required_skills=command.required_skills,
                    required_technologies=command.required_technologies,
                    experience_years=command.experience_years,
                    location=command.location,
                    employment_type=EmploymentType(command.employment_type),
                    status=JobStatus.ACTIVE
                )
                session.add(job)
                session.flush()

                # Publish event
                @dataclass
                class JobCreatedEvent(DomainEvent):
                    job_id: str
                    employer_id: str
                    title: str
                    def _payload(self):
                        return {'job_id': self.job_id, 'employer_id': self.employer_id, 'title': self.title}

                event = JobCreatedEvent(aggregate_id=str(job.id), job_id=str(job.id), employer_id=str(job.employer_id), title=job.title)
                await self.event_bus.publish(event, routing_key="job.created")

                return Result.ok(job.to_dict())
        except Exception as e:
            return Result.fail(f"Failed to create job: {str(e)}")


class UpdateJobHandler(CommandHandler[UpdateJobCommand, Result]):
    def __init__(self, db: Database, event_bus: RabbitMQEventBus):
        self.db = db
        self.event_bus = event_bus

    async def handle(self, command: UpdateJobCommand) -> Result:
        try:
            with self.db.get_db_session() as session:
                job = session.query(Job).filter(Job.id == command.job_id).first()
                if not job:
                    return Result.fail("Job not found")

                if str(job.employer_id) != command.employer_id:
                    return Result.fail("Unauthorized")

                if command.title: job.title = command.title
                if command.description: job.description = command.description
                if command.required_skills: job.required_skills = command.required_skills
                if command.required_technologies: job.required_technologies = command.required_technologies
                if command.experience_years is not None: job.experience_years = command.experience_years
                if command.location: job.location = command.location
                if command.employment_type: job.employment_type = EmploymentType(command.employment_type)
                if command.status: job.status = JobStatus(command.status)

                session.flush()
                return Result.ok(job.to_dict())
        except Exception as e:
            return Result.fail(f"Failed to update job: {str(e)}")


class DeleteJobHandler(CommandHandler[DeleteJobCommand, Result]):
    def __init__(self, db: Database):
        self.db = db

    async def handle(self, command: DeleteJobCommand) -> Result:
        try:
            with self.db.get_db_session() as session:
                job = session.query(Job).filter(Job.id == command.job_id).first()
                if not job:
                    return Result.fail("Job not found")

                if str(job.employer_id) != command.employer_id:
                    return Result.fail("Unauthorized")

                job.status = JobStatus.CLOSED
                session.flush()
                return Result.ok({"message": "Job closed successfully"})
        except Exception as e:
            return Result.fail(f"Failed to close job: {str(e)}")


# ============================================================================
# QUERIES
# ============================================================================

@dataclass
class GetJobQuery(Query):
    job_id: str


@dataclass
class ListActiveJobsQuery(Query):
    limit: int = 100
    offset: int = 0


@dataclass
class GetEmployerJobsQuery(Query):
    employer_id: str


class GetJobHandler(QueryHandler[GetJobQuery, Result]):
    def __init__(self, db: Database):
        self.db = db

    async def handle(self, query: GetJobQuery) -> Result:
        try:
            with self.db.get_db_session() as session:
                job = session.query(Job).filter(Job.id == query.job_id).first()
                if not job:
                    return Result.fail("Job not found")
                return Result.ok(job.to_dict())
        except Exception as e:
            return Result.fail(f"Failed to get job: {str(e)}")


class ListActiveJobsHandler(QueryHandler[ListActiveJobsQuery, Result]):
    def __init__(self, db: Database):
        self.db = db

    async def handle(self, query: ListActiveJobsQuery) -> Result:
        try:
            with self.db.get_db_session() as session:
                jobs = session.query(Job).filter(Job.status == JobStatus.ACTIVE)\
                    .order_by(Job.created_at.desc())\
                    .limit(query.limit).offset(query.offset).all()
                return Result.ok([job.to_dict() for job in jobs])
        except Exception as e:
            return Result.fail(f"Failed to list jobs: {str(e)}")


class GetEmployerJobsHandler(QueryHandler[GetEmployerJobsQuery, Result]):
    def __init__(self, db: Database):
        self.db = db

    async def handle(self, query: GetEmployerJobsQuery) -> Result:
        try:
            with self.db.get_db_session() as session:
                jobs = session.query(Job).filter(Job.employer_id == query.employer_id)\
                    .order_by(Job.created_at.desc()).all()
                return Result.ok([job.to_dict() for job in jobs])
        except Exception as e:
            return Result.fail(f"Failed to get employer jobs: {str(e)}")


# Register handlers
from cqrs_base import CommandBus, QueryBus
command_bus = CommandBus()
query_bus = QueryBus()

command_bus.register(CreateJobCommand, CreateJobHandler(database, event_bus))
command_bus.register(UpdateJobCommand, UpdateJobHandler(database, event_bus))
command_bus.register(DeleteJobCommand, DeleteJobHandler(database))

query_bus.register(GetJobQuery, GetJobHandler(database))
query_bus.register(ListActiveJobsQuery, ListActiveJobsHandler(database))
query_bus.register(GetEmployerJobsQuery, GetEmployerJobsHandler(database))


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route("/api/jobs/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "job-service"}), 200


@app.route("/api/jobs", methods=["GET"])
def list_jobs():
    """List all active jobs (public endpoint for employees)"""
    try:
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        query = ListActiveJobsQuery(limit=limit, offset=offset)
        result = asyncio.run(query_bus.send(query))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/jobs/<job_id>", methods=["GET"])
def get_job(job_id):
    """Get specific job details"""
    try:
        query = GetJobQuery(job_id=job_id)
        result = asyncio.run(query_bus.send(query))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/jobs", methods=["POST"])
@require_role("employer")
def create_job():
    """Create new job posting (employers only)"""
    try:
        data = request.json
        current_user = get_current_user()

        # Get employer_id from user service (for now, use keycloak sub)
        employer_id = current_user['sub']

        command = CreateJobCommand(
            employer_id=employer_id,
            title=data['title'],
            description=data['description'],
            company_name=data['company_name'],
            required_skills=data.get('required_skills', []),
            required_technologies=data.get('required_technologies', []),
            experience_years=data.get('experience_years', 0),
            location=data['location'],
            employment_type=data.get('employment_type', 'full-time')
        )

        result = asyncio.run(command_bus.send(command))

        if result.success:
            return jsonify(result.data), 201
        else:
            return jsonify({"error": result.error}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/jobs/<job_id>", methods=["PUT"])
@require_role("employer")
def update_job(job_id):
    """Update job posting"""
    try:
        data = request.json
        current_user = get_current_user()

        command = UpdateJobCommand(
            job_id=job_id,
            employer_id=current_user['sub'],
            **data
        )

        result = asyncio.run(command_bus.send(command))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/jobs/<job_id>", methods=["DELETE"])
@require_role("employer")
def delete_job(job_id):
    """Close job posting"""
    try:
        current_user = get_current_user()

        command = DeleteJobCommand(job_id=job_id, employer_id=current_user['sub'])
        result = asyncio.run(command_bus.send(command))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/jobs/my-jobs", methods=["GET"])
@require_role("employer")
def get_my_jobs():
    """Get all jobs posted by current employer"""
    try:
        current_user = get_current_user()
        query = GetEmployerJobsQuery(employer_id=current_user['sub'])
        result = asyncio.run(query_bus.send(query))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    app.run(host="0.0.0.0", port=port, debug=False)
