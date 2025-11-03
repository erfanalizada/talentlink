from flask import Flask, jsonify
from sqlalchemy import create_engine, text
import os

app = Flask(__name__)

# ✅ Read DATABASE_URL from environment variable (Kubernetes secret)
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Create SQLAlchemy engine once at startup
engine = create_engine(DATABASE_URL)

@app.route("/api/jobs")
def list_jobs():
    return jsonify([
        {"id": 1, "title": "Internship (hardcoded)"},
        {"id": 2, "title": "Software Engineer (hardcoded)"}
    ])

@app.route("/api/jobs/health")
def health():
    return {"status": "job-service ok"}

# ✅ Add DB connectivity test endpoint
@app.route("/api/jobs/test-db", methods=["POST"])
def test_db():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW()")).fetchone()
            return {"message": "Database OK", "time": str(result[0])}, 200
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
