import os
import psycopg2
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# ✅ Load environment variables from .env (for local dev)
load_dotenv()

app = Flask(__name__)
CORS(app)  # allow frontend requests

# =====================================================
# 🔧 Database Configuration
# =====================================================

# Prefer a single DATABASE_URL (used in Kubernetes secret)
DATABASE_URL = os.getenv("DATABASE_URL")

# Fallback for local development if DATABASE_URL isn't set
if DATABASE_URL:
    import urllib.parse as urlparse
    urlparse.uses_netloc.append("postgres")
    parsed = urlparse.urlparse(DATABASE_URL)
    DB_HOST = parsed.hostname
    DB_PORT = parsed.port or 5432
    DB_NAME = parsed.path[1:]
    DB_USER = parsed.username
    DB_PASSWORD = parsed.password
else:
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "authdb")
    DB_USER = os.getenv("DB_USER", "auth_user")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

# =====================================================
# 🔑 Keycloak Configuration
# =====================================================
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "https://talentlink-erfan.nl/auth")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "talentlink")
KEYCLOAK_ADMIN_USER = os.getenv("KEYCLOAK_ADMIN_USER", "auth-service-admin")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "StrongPassword123!")
KEYCLOAK_ADMIN_CLIENT_ID = os.getenv("KEYCLOAK_ADMIN_CLIENT_ID", "auth-service")
KEYCLOAK_LOGIN_CLIENT_ID = os.getenv("KEYCLOAK_LOGIN_CLIENT_ID", "frontend-client")

# =====================================================
# 🔐 Helper: Get Keycloak admin token
# =====================================================
def get_admin_token():
    token_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": KEYCLOAK_ADMIN_CLIENT_ID,
        "username": KEYCLOAK_ADMIN_USER,
        "password": KEYCLOAK_ADMIN_PASSWORD,
    }

    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        print("❌ Failed to get admin token:", response.text)
        raise Exception("Failed to authenticate admin")

    return response.json()["access_token"]

# =====================================================
# ❤️ Health / Readiness Endpoint
# =====================================================
@app.route("/api/auth/dbtest", methods=["GET", "POST"])
def db_test():
    """Used for readinessProbe and manual DB checks."""
    try:
        with psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 'Database OK' AS message;")
                result = cur.fetchone()
                return jsonify({"message": result[0]}), 200
    except Exception as e:
        print("❌ DB connection failed:", e)
        return jsonify({"error": str(e)}), 500

# =====================================================
# 👤 Register User Endpoint
# =====================================================
@app.route("/api/auth/register", methods=["POST"])
def register_user():
    data = request.json
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "employee")  # default role

    try:
        admin_token = get_admin_token()
        headers = {"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"}

        # 1️⃣ Create user
        user_payload = {
            "username": username,
            "email": email,
            "enabled": True,
            "emailVerified": True,
            "credentials": [{"type": "password", "value": password, "temporary": False}],
        }

        create_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
        create_resp = requests.post(create_url, json=user_payload, headers=headers)

        if create_resp.status_code not in [201, 409]:
            return jsonify({"error": "Failed to create user", "details": create_resp.text}), 500

        # 2️⃣ Get user ID
        search_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
        user_resp = requests.get(search_url, params={"username": username}, headers=headers)
        user_id = user_resp.json()[0]["id"]

        # 3️⃣ Assign role
        role_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/roles/{role}"
        role_resp = requests.get(role_url, headers=headers)
        if role_resp.status_code == 200:
            assign_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}/role-mappings/realm"
            requests.post(assign_url, json=[role_resp.json()], headers=headers)
        else:
            print(f"⚠️ Role '{role}' not found — skipping assignment")

        print(f"✅ User '{username}' created with role '{role}'")
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# =====================================================
# 🔑 Login Endpoint
# =====================================================
@app.route("/api/auth/login", methods=["POST"])
def login_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    token_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    payload = {
        "grant_type": "password",
        "client_id": KEYCLOAK_LOGIN_CLIENT_ID,
        "username": username,
        "password": password,
    }

    resp = requests.post(token_url, data=payload)
    if resp.status_code == 200:
        print(f"✅ Login success for {username}")
        return jsonify(resp.json()), 200
    else:
        print(f"❌ Login failed for {username}: {resp.text}")
        return jsonify({"error": "Invalid credentials", "details": resp.text}), 401

# =====================================================
# 🚀 App Entry Point
# =====================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
