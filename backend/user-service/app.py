"""
User Service - CQRS Implementation
Handles user profile management for employees and employers
"""
import os
import sys
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
import asyncio

# Add shared library to path
sys.path.append('../shared')
from database import Database
from event_bus import RabbitMQEventBus
from monitoring import MetricsMiddleware
from auth import require_auth, get_current_user
from cqrs_base import CommandBus, QueryBus

# Import commands
from src.commands.create_user import CreateUserCommand, CreateUserHandler
from src.commands.update_user import UpdateUserCommand, UpdateUserHandler

# Import queries
from src.queries.get_user import (
    GetUserByIdQuery, GetUserByIdHandler,
    GetUserByKeycloakIdQuery, GetUserByKeycloakIdHandler,
    GetUserByEmailQuery, GetUserByEmailHandler
)

# Load environment
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize infrastructure
database = Database(os.getenv("DATABASE_URL"), "userdb")
event_bus = RabbitMQEventBus(os.getenv("RABBITMQ_URL"))

# Initialize CQRS buses
command_bus = CommandBus()
query_bus = QueryBus()

# Register command handlers
command_bus.register(CreateUserCommand, CreateUserHandler(database, event_bus))
command_bus.register(UpdateUserCommand, UpdateUserHandler(database, event_bus))

# Register query handlers
query_bus.register(GetUserByIdQuery, GetUserByIdHandler(database))
query_bus.register(GetUserByKeycloakIdQuery, GetUserByKeycloakIdHandler(database))
query_bus.register(GetUserByEmailQuery, GetUserByEmailHandler(database))

# Initialize monitoring
MetricsMiddleware(app, "user-service")

# Initialize database schema
try:
    database.init_schema()
    print("✅ Database schema initialized")
except Exception as e:
    print(f"⚠️  Database schema initialization: {e}")


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route("/api/users/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "service": "user-service"}), 200


@app.route("/api/users", methods=["POST"])
@require_auth
def create_user():
    """Create a new user profile"""
    try:
        data = request.json
        current_user = get_current_user()

        # Create command
        command = CreateUserCommand(
            keycloak_id=current_user['sub'],
            email=data.get('email') or current_user['email'],
            full_name=data.get('full_name'),
            role=data.get('role', 'employee'),
            company_name=data.get('company_name'),
            phone=data.get('phone'),
            location=data.get('location')
        )

        # Execute command
        result = asyncio.run(command_bus.send(command))

        if result.success:
            return jsonify(result.data), 201
        else:
            return jsonify({"error": result.error}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<user_id>", methods=["GET"])
@require_auth
def get_user(user_id):
    """Get user by ID"""
    try:
        query = GetUserByIdQuery(user_id=user_id)
        result = asyncio.run(query_bus.send(query))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/by-keycloak/<keycloak_id>", methods=["GET"])
@require_auth
def get_user_by_keycloak_id(keycloak_id):
    """Get user by Keycloak ID"""
    try:
        query = GetUserByKeycloakIdQuery(keycloak_id=keycloak_id)
        result = asyncio.run(query_bus.send(query))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/by-email/<email>", methods=["GET"])
@require_auth
def get_user_by_email(email):
    """Get user by email"""
    try:
        query = GetUserByEmailQuery(email=email)
        result = asyncio.run(query_bus.send(query))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/me", methods=["GET"])
@require_auth
def get_current_user_profile():
    """Get current authenticated user's profile"""
    try:
        current_user = get_current_user()
        query = GetUserByKeycloakIdQuery(keycloak_id=current_user['sub'])
        result = asyncio.run(query_bus.send(query))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/users/<user_id>", methods=["PUT"])
@require_auth
def update_user(user_id):
    """Update user profile"""
    try:
        data = request.json
        current_user = get_current_user()

        # Users can only update their own profile (unless admin)
        query = GetUserByIdQuery(user_id=user_id)
        user_result = asyncio.run(query_bus.send(query))

        if not user_result.success:
            return jsonify({"error": "User not found"}), 404

        if user_result.data['keycloak_id'] != current_user['sub']:
            if 'admin' not in current_user['roles']:
                return jsonify({"error": "Unauthorized"}), 403

        # Create command
        command = UpdateUserCommand(
            user_id=user_id,
            full_name=data.get('full_name'),
            company_name=data.get('company_name'),
            phone=data.get('phone'),
            location=data.get('location')
        )

        # Execute command
        result = asyncio.run(command_bus.send(command))

        if result.success:
            return jsonify(result.data), 200
        else:
            return jsonify({"error": result.error}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ============================================================================
# RUN APP
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
