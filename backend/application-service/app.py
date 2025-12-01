"""
Application Service - CQRS Implementation
Handles job applications with event-driven workflow
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

sys.path.append('../shared')
from database import Database
from event_bus import RabbitMQEventBus
from monitoring import MetricsMiddleware
from auth import require_auth, require_role, get_current_user
from cqrs_base import Command, CommandHandler, Query, QueryHandler, Result, DomainEvent

from src.models.application import Application, ApplicationStatus

load_dotenv()

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

database = Database(os.getenv("DATABASE_URL"), "applicationdb")
event_bus = RabbitMQEventBus(os.getenv("RABBITMQ_URL"))

MetricsMiddleware(app, "application-service")

try:
    database.init_schema()
    print("✅ Database schema initialized")
except Exception as e:
    print(f"⚠️  Database schema initialization: {e}")


# ============================================================================
# EVENTS
# ============================================================================

@dataclass
class ApplicationSubmittedEvent(DomainEvent):
    application_id: str
    job_id: str
    employee_id: str
    cv_id: str

    def _payload(self):
        return {
            'application_id': self.application_id,
            'job_id': self.job_id,
            'employee_id': self.employee_id,
            'cv_id': self.cv_id
        }


@dataclass
class ApplicationStatusChangedEvent(DomainEvent):
    application_id: str
    old_status: str
    new_status: str
    changed_by: str

    def _payload(self):
        return {
            'application_id': self.application_id,
            'old_status': self.old_status,
            'new_status': self.new_status,
            'changed_by': self.changed_by
        }


@dataclass
class CandidateInvitedEvent(DomainEvent):
    application_id: str
    employee_id: str
    job_id: str

    def _payload(self):
        return {
            'application_id': self.application_id,
            'employee_id': self.employee_id,
            'job_id': self.job_id
        }


# ============================================================================
# COMMANDS
# ============================================================================

@dataclass
class SubmitApplicationCommand(Command):
    job_id: str
    employee_id: str
    cv_id: Optional[str] = None


@dataclass
class UpdateApplicationStatusCommand(Command):
    application_id: str
    new_status: str
    changed_by: str


@dataclass
class InviteCandidateCommand(Command):
    application_id: str
    employer_id: str


class SubmitApplicationHandler(CommandHandler[SubmitApplicationCommand, Result]):
    def __init__(self, db: Database, event_bus: RabbitMQEventBus):
        self.db = db
        self.event_bus = event_bus

    async def handle(self, command: SubmitApplicationCommand) -> Result:
        try:
            with self.db.get_db_session() as session:
                # Check for duplicate application
                existing = session.query(Application).filter(
                    Application.job_id == command.job_id,
                    Application.employee_id == command.employee_id
                ).first()

                if existing:
                    return Result.fail("You have already applied to this job")

                application = Application(
                    id=uuid.uuid4(),
                    job_id=command.job_id,
                    employee_id=command.employee_id,
                    cv_id=command.cv_id,
                    status=ApplicationStatus.PENDING
                )
                session.add(application)
                session.flush()

                # Publish event (triggers AI matching)
                event = ApplicationSubmittedEvent(
                    aggregate_id=str(application.id),
                    application_id=str(application.id),
                    job_id=str(application.job_id),
                    employee_id=str(application.employee_id),
                    cv_id=str(application.cv_id) if application.cv_id else ""
                )
                await self.event_bus.publish(event, routing_key="application.submitted")

                return Result.ok(application.to_dict())
        except Exception as e:
            return Result.fail(f"Failed to submit application: {str(e)}")


class UpdateApplicationStatusHandler(CommandHandler[UpdateApplicationStatusCommand, Result]):
    def __init__(self, db: Database, event_bus: RabbitMQEventBus):
        self.db = db
        self.event_bus = event_bus

    async def handle(self, command: UpdateApplicationStatusCommand) -> Result:
        try:
            with self.db.get_db_session() as session:
                application = session.query(Application).filter(Application.id == command.application_id).first()
                if not application:
                    return Result.fail("Application not found")

                old_status = application.status.value
                application.status = ApplicationStatus(command.new_status)
                session.flush()

                # Publish event
                event = ApplicationStatusChangedEvent(
                    aggregate_id=str(application.id),
                    application_id=str(application.id),
                    old_status=old_status,
                    new_status=command.new_status,
                    changed_by=command.changed_by
                )
                await self.event_bus.publish(event, routing_key="application.status_changed")

                return Result.ok(application.to_dict())
        except Exception as e:
            return Result.fail(f"Failed to update application: {str(e)}")


class InviteCandidateHandler(CommandHandler[InviteCandidateCommand, Result]):
    def __init__(self, db: Database, event_bus: RabbitMQEventBus):
        self.db = db
        self.event_bus = event_bus

    async def handle(self, command: InviteCandidateCommand) -> Result:
        try:
            with self.db.get_db_session() as session:
                application = session.query(Application).filter(Application.id == command.application_id).first()
                if not application:
                    return Result.fail("Application not found")

                old_status = application.status.value
                application.status = ApplicationStatus.INVITED
                session.flush()

                # Publish events
                await self.event_bus.publish(
                    ApplicationStatusChangedEvent(
                        aggregate_id=str(application.id),
                        application_id=str(application.id),
                        old_status=old_status,
                        new_status="invited",
                        changed_by=command.employer_id
                    ),
                    routing_key="application.status_changed"
                )

                await self.event_bus.publish(
                    CandidateInvitedEvent(
                        aggregate_id=str(application.id),
                        application_id=str(application.id),
                        employee_id=str(application.employee_id),
                        job_id=str(application.job_id)
                    ),
                    routing_key="candidate.invited"
                )

                return Result.ok(application.to_dict())
        except Exception as e:
            return Result.fail(f"Failed to invite candidate: {str(e)}")


# ============================================================================
# QUERIES
# ============================================================================

@dataclass
class GetApplicationQuery(Query):
    application_id: str


@dataclass
class GetEmployeeApplicationsQuery(Query):
    employee_id: str


@dataclass
class GetJobApplicationsQuery(Query):
    job_id: str


class GetApplicationHandler(QueryHandler[GetApplicationQuery, Result]):
    def __init__(self, db: Database):
        self.db = db

    async def handle(self, query: GetApplicationQuery) -> Result:
        try:
            with self.db.get_db_session() as session:
                app = session.query(Application).filter(Application.id == query.application_id).first()
                if not app:
                    return Result.fail("Application not found")
                return Result.ok(app.to_dict())
        except Exception as e:
            return Result.fail(f"Failed to get application: {str(e)}")


class GetEmployeeApplicationsHandler(QueryHandler[GetEmployeeApplicationsQuery, Result]):
    def __init__(self, db: Database):
        self.db = db

    async def handle(self, query: GetEmployeeApplicationsQuery) -> Result:
        try:
            with self.db.get_db_session() as session:
                apps = session.query(Application).filter(Application.employee_id == query.employee_id)\
                    .order_by(Application.applied_at.desc()).all()
                return Result.ok([app.to_dict() for app in apps])
        except Exception as e:
            return Result.fail(f"Failed to get applications: {str(e)}")


class GetJobApplicationsHandler(QueryHandler[GetJobApplicationsQuery, Result]):
    def __init__(self, db: Database):
        self.db = db

    async def handle(self, query: GetJobApplicationsQuery) -> Result:
        try:
            with self.db.get_db_session() as session:
                apps = session.query(Application).filter(Application.job_id == query.job_id)\
                    .order_by(Application.match_score.desc().nullsfirst(), Application.applied_at.desc()).all()
                return Result.ok([app.to_dict() for app in apps])
        except Exception as e:
            return Result.fail(f"Failed to get job applications: {str(e)}")


# Register handlers
from cqrs_base import CommandBus, QueryBus
command_bus = CommandBus()
query_bus = QueryBus()

command_bus.register(SubmitApplicationCommand, SubmitApplicationHandler(database, event_bus))
command_bus.register(UpdateApplicationStatusCommand, UpdateApplicationStatusHandler(database, event_bus))
command_bus.register(InviteCandidateCommand, InviteCandidateHandler(database, event_bus))

query_bus.register(GetApplicationQuery, GetApplicationHandler(database))
query_bus.register(GetEmployeeApplicationsQuery, GetEmployeeApplicationsHandler(database))
query_bus.register(GetJobApplicationsQuery, GetJobApplicationsHandler(database))


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route("/api/applications/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "application-service"}), 200


@app.route("/api/applications", methods=["POST"])
@require_role("employee")
def submit_application():
    """Submit a job application"""
    try:
        data = request.json
        current_user = get_current_user()

        command = SubmitApplicationCommand(
            job_id=data['job_id'],
            employee_id=current_user['sub'],
            cv_id=data.get('cv_id')
        )

        result = asyncio.run(command_bus.send(command))

        if result.success:
            return jsonify(result.data), 201
        else:
            return jsonify({"error": result.error}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/applications/my-applications", methods=["GET"])
@require_role("employee")
def get_my_applications():
    """Get all applications for current employee"""
    try:
        current_user = get_current_user()
        query = GetEmployeeApplicationsQuery(employee_id=current_user['sub'])
        result = asyncio.run(query_bus.send(query))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/applications/job/<job_id>", methods=["GET"])
@require_role("employer")
def get_job_applications(job_id):
    """Get all applications for a specific job"""
    try:
        query = GetJobApplicationsQuery(job_id=job_id)
        result = asyncio.run(query_bus.send(query))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/applications/<application_id>", methods=["GET"])
@require_auth
def get_application(application_id):
    """Get application details"""
    try:
        query = GetApplicationQuery(application_id=application_id)
        result = asyncio.run(query_bus.send(query))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/applications/<application_id>/invite", methods=["POST"])
@require_role("employer")
def invite_candidate(application_id):
    """Invite candidate for interview"""
    try:
        current_user = get_current_user()

        command = InviteCandidateCommand(
            application_id=application_id,
            employer_id=current_user['sub']
        )

        result = asyncio.run(command_bus.send(command))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/applications/<application_id>/status", methods=["PUT"])
@require_role("employer")
def update_application_status(application_id):
    """Update application status"""
    try:
        data = request.json
        current_user = get_current_user()

        command = UpdateApplicationStatusCommand(
            application_id=application_id,
            new_status=data['status'],
            changed_by=current_user['sub']
        )

        result = asyncio.run(command_bus.send(command))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=False)
