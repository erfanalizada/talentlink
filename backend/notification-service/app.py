from flask import Flask, jsonify
from sqlalchemy import create_engine, text
import os

app = Flask(__name__)

# ✅ Read DATABASE_URL from environment variable (injected by Kubernetes secret)
DATABASE_URL = os.getenv("DATABASE_URL")

# ✅ Create SQLAlchemy engine once at startup
engine = create_engine(DATABASE_URL)

@app.route("/api/notifications/send", methods=["POST"])
def send_notification():
    return jsonify({"message": "Notification sent (hardcoded)"})

@app.route("/api/notifications/health")
def health():
    return {"status": "notification-service ok"}

# ✅ Add DB connectivity test endpoint (accepts GET + POST)
@app.route("/api/notifications/test-db", methods=["GET", "POST"])
def test_db():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW()")).fetchone()
            return {"message": "Database OK", "time": str(result[0])}, 200
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
