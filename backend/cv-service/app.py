"""
CV Service - File Upload and Storage
Handles CV uploads (PDF, DOC, DOCX) with text extraction
"""
import os
import sys
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import uuid
from datetime import datetime
import PyPDF2
import docx

sys.path.append('../shared')
from database import Database
from event_bus import RabbitMQEventBus
from monitoring import MetricsMiddleware
from auth import require_auth, get_current_user
from cqrs_base import DomainEvent
from dataclasses import dataclass

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

UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "./uploads")
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

database = Database(os.getenv("DATABASE_URL"), "cvdb")
event_bus = RabbitMQEventBus(os.getenv("RABBITMQ_URL"))

MetricsMiddleware(app, "cv-service")

# ============================================================================
# DATABASE SETUP
# ============================================================================

from sqlalchemy import Column, String, Text, BigInteger, DateTime
from sqlalchemy.dialects.postgresql import UUID
from shared.database import Base

class CV(Base):
    __tablename__ = "cvs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    content_type = Column(String(100), nullable=False)
    extracted_text = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': str(self.id),
            'user_id': self.user_id,
            'file_name': self.file_name,
            'file_size': self.file_size,
            'content_type': self.content_type,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None
        }

try:
    database.init_schema()
    print("✅ Database schema initialized")
except Exception as e:
    print(f"⚠️  Database schema initialization: {e}")


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_path):
    """Extract text from PDF"""
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        return ""


def extract_text_from_docx(file_path):
    """Extract text from DOCX"""
    try:
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
    except Exception as e:
        print(f"Error extracting DOCX text: {e}")
        return ""


def extract_text(file_path, content_type):
    """Extract text based on file type"""
    if 'pdf' in content_type:
        return extract_text_from_pdf(file_path)
    elif 'word' in content_type or 'document' in content_type:
        return extract_text_from_docx(file_path)
    return ""


# ============================================================================
# EVENTS
# ============================================================================

@dataclass
class CVUploadedEvent(DomainEvent):
    cv_id: str
    user_id: str
    file_path: str

    def _payload(self):
        return {
            'cv_id': self.cv_id,
            'user_id': self.user_id,
            'file_path': self.file_path
        }


# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route("/api/cv/health", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "cv-service"}), 200


@app.route("/api/cv/upload", methods=["POST"])
@require_auth
def upload_cv():
    """Upload CV file"""
    try:
        current_user = get_current_user()

        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']

        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": "Invalid file type. Allowed: PDF, DOC, DOCX"}), 400

        # Generate unique filename
        cv_id = str(uuid.uuid4())
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        safe_filename = f"{cv_id}.{file_ext}"
        file_path = os.path.join(UPLOAD_FOLDER, safe_filename)

        # Save file
        file.save(file_path)
        file_size = os.path.getsize(file_path)

        if file_size > MAX_FILE_SIZE:
            os.remove(file_path)
            return jsonify({"error": "File too large (max 10MB)"}), 400

        # Extract text
        extracted_text = extract_text(file_path, file.content_type)

        # Save to database
        with database.get_db_session() as session:
            cv = CV(
                id=uuid.UUID(cv_id),
                user_id=current_user['sub'],
                file_name=secure_filename(file.filename),
                file_path=file_path,
                file_size=file_size,
                content_type=file.content_type,
                extracted_text=extracted_text
            )
            session.add(cv)
            session.flush()

            # Publish event
            import asyncio
            event = CVUploadedEvent(
                aggregate_id=cv_id,
                cv_id=cv_id,
                user_id=current_user['sub'],
                file_path=file_path
            )
            asyncio.run(event_bus.publish(event, routing_key="cv.uploaded"))

            return jsonify(cv.to_dict()), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cv/<cv_id>", methods=["GET"])
@require_auth
def get_cv_metadata(cv_id):
    """Get CV metadata"""
    try:
        with database.get_db_session() as session:
            cv = session.query(CV).filter(CV.id == cv_id).first()
            if not cv:
                return jsonify({"error": "CV not found"}), 404
            return jsonify(cv.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cv/<cv_id>/download", methods=["GET"])
@require_auth
def download_cv(cv_id):
    """Download CV file"""
    try:
        with database.get_db_session() as session:
            cv = session.query(CV).filter(CV.id == cv_id).first()
            if not cv:
                return jsonify({"error": "CV not found"}), 404

            if not os.path.exists(cv.file_path):
                return jsonify({"error": "File not found on disk"}), 404

            return send_file(
                cv.file_path,
                as_attachment=True,
                download_name=cv.file_name,
                mimetype=cv.content_type
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cv/<cv_id>/text", methods=["GET"])
@require_auth
def get_cv_text(cv_id):
    """Get extracted text from CV"""
    try:
        with database.get_db_session() as session:
            cv = session.query(CV).filter(CV.id == cv_id).first()
            if not cv:
                return jsonify({"error": "CV not found"}), 404

            return jsonify({
                "cv_id": str(cv.id),
                "extracted_text": cv.extracted_text or ""
            }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cv/my-cv", methods=["GET"])
@require_auth
def get_my_cv():
    """Get current user's latest CV"""
    try:
        current_user = get_current_user()

        with database.get_db_session() as session:
            cv = session.query(CV).filter(CV.user_id == current_user['sub'])\
                .order_by(CV.uploaded_at.desc()).first()

            if not cv:
                return jsonify({"error": "No CV found"}), 404

            return jsonify(cv.to_dict()), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5003))
    app.run(host="0.0.0.0", port=port, debug=False)
