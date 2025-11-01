import os
import psycopg2
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables (useful for local dev; in Kubernetes, envs are injected automatically)
load_dotenv()

app = Flask(__name__)

# Database configuration
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# --- Health Check Endpoint (for Kubernetes readiness/liveness) ---
@app.route("/api/auth/health")
def health():
    return jsonify({"status": "ok"}), 200


# --- Database Connection Test Endpoint ---
@app.route("/api/auth/dbtest")
def db_test():
    try:
        print("🔄 Connecting to PostgreSQL (Keycloak DB)...")
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            connect_timeout=5
        )
        cur = conn.cursor()
        cur.execute("SELECT 'DB connection OK' AS message;")
        result = cur.fetchone()
        cur.close()
        conn.close()
        print("✅ PostgreSQL connection success:", result[0])
        return jsonify({"db": result[0]}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# --- Main Entry Point ---
if __name__ == "__main__":
    # Important: Use a production WSGI server like Gunicorn in Dockerfile
    app.run(host="0.0.0.0", port=5000)
