from flask import Flask, jsonify
from sqlalchemy import create_engine, text
import os

app = Flask(__name__)

# Read DATABASE_URL from environment variable
DATABASE_URL = os.getenv("DATABASE_URL")

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

@app.route("/api/users/profile")
def profile():
    return jsonify({
        "id": 1,
        "name": "Hardcoded User",
        "email": "user@example.com"
    })

@app.route("/api/users/health")
def health():
    return {"status": "user-service ok"}

@app.route("/api/users/test-db", methods=["POST"])
def test_db():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW()")).fetchone()
            return {"message": "Database OK", "time": str(result[0])}, 200
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
