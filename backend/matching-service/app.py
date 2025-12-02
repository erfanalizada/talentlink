"""
Matching Service - AI-powered Job Matching
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
import asyncio

sys.path.append('../shared')
from shared.database import Database
from shared.event_bus import RabbitMQEventBus
from shared.monitoring import MetricsMiddleware
from shared.auth import require_auth, require_role, get_current_user
from shared.cqrs_base import Command, CommandHandler, Query, QueryHandler, Result, DomainEvent

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

database = Database(os.getenv("DATABASE_URL"), "matchingdb")
event_bus = RabbitMQEventBus(os.getenv("RABBITMQ_URL"))

MetricsMiddleware(app, "matching-service")

engine = MatchingEngine(database)

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route("/api/matching/health", methods=["GET"])
def matching_health():  # ✅ Unique function name to avoid collision
    return jsonify({"status": "healthy", "service": "matching-service"}), 200


@app.route("/api/matching/run", methods=["POST"])
@require_role("employer")
def run_matching():
    """Run AI matching for job and CV"""
    try:
        body = request.json
        job_id = body.get("job_id")
        cv_id = body.get("cv_id")

        if not job_id or not cv_id:
            return jsonify({"error": "job_id and cv_id are required"}), 400

        score, summary = engine.match(job_id, cv_id)
        
        return jsonify({
            "score": score,
            "summary": summary
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5004))
    app.run(host="0.0.0.0", port=port, debug=False)