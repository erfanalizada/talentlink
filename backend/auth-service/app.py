import os
import oracledb
from flask import Flask, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Read from .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_DSN = os.getenv("DB_DSN")

@app.route("/api/auth/dbtest")
def db_test():
    try:
        print("🔄 Connecting to Oracle Autonomous Database (TLS, no wallet)...")
        with oracledb.connect(
            user=DB_USER,
            password=DB_PASSWORD,
            dsn=DB_DSN
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 'DB connection OK' FROM dual")
                result = cursor.fetchone()
                print("✅ Oracle connection success:", result[0])
                return jsonify({"db": result[0]}), 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
