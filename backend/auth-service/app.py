import os
import requests
import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables (optional in container, but safe)
load_dotenv()

app = Flask(__name__)
CORS(app)  # allow Flutter web frontend requests

# === Database (Keycloak PostgreSQL) config ===
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# === Keycloak config ===
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "https://talentlink-erfan.nl/auth")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "talentlink")
KEYCLOAK_ADMIN = os.getenv("KEYCLOAK_ADMIN", "admin")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "admin123")

# === Derived URLs ===
TOKEN_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
ADMIN_BASE_URL = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}"

# ---------------------------------------------------------------------
# HEALTHCHECK / DB TEST
# ---------------------------------------------------------------------
@app.route("/api/auth/dbtest")
def db_test():
    """Simple PostgreSQL test to verify DB connectivity"""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
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


# ---------------------------------------------------------------------
# REGISTER (Create user in Keycloak)
# ---------------------------------------------------------------------
@app.route("/api/auth/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    role = data.get("role", "employee")  # default role

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    # Step 1: get admin token
    token_payload = {
        "client_id": "admin-cli",
        "grant_type": "password",
        "username": KEYCLOAK_ADMIN,
        "password": KEYCLOAK_ADMIN_PASSWORD,
    }
    token_resp = requests.post(TOKEN_URL, data=token_payload)
    if token_resp.status_code != 200:
        return jsonify({"error": "Failed to authenticate admin", "details": token_resp.text}), 500
    admin_token = token_resp.json()["access_token"]

    # Step 2: create user
    user_data = {
        "username": username,
        "email": email,
        "enabled": True,
        "credentials": [{"type": "password", "value": password, "temporary": False}],
    }

    create_user_resp = requests.post(
        f"{ADMIN_BASE_URL}/users",
        headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
        json=user_data,
    )

    if create_user_resp.status_code not in [201, 409]:  # 409 if user already exists
        return jsonify({"error": "Failed to create user", "details": create_user_resp.text}), 500

    # Step 3: fetch user ID (needed to assign role)
    users_resp = requests.get(
        f"{ADMIN_BASE_URL}/users",
        headers={"Authorization": f"Bearer {admin_token}"},
        params={"username": username},
    )
    user_list = users_resp.json()
    if not user_list:
        return jsonify({"error": "User created but not found"}), 500
    user_id = user_list[0]["id"]

    # Step 4: get role details
    roles_resp = requests.get(
        f"{ADMIN_BASE_URL}/roles",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    roles = roles_resp.json()
    target_role = next((r for r in roles if r["name"] == role), None)
    if not target_role:
        return jsonify({"error": f"Role '{role}' not found in Keycloak"}), 400

    # Step 5: assign role to user
    assign_resp = requests.post(
        f"{ADMIN_BASE_URL}/users/{user_id}/role-mappings/realm",
        headers={"Authorization": f"Bearer {admin_token}", "Content-Type": "application/json"},
        json=[{"id": target_role["id"], "name": target_role["name"]}],
    )
    if assign_resp.status_code not in [204, 200]:
        return jsonify({"error": "Failed to assign role", "details": assign_resp.text}), 500

    return jsonify({"message": "User registered successfully"}), 201


# ---------------------------------------------------------------------
# LOGIN (Get token from Keycloak)
# ---------------------------------------------------------------------
@app.route("/api/auth/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    payload = {
        "client_id": "frontend-client",
        "grant_type": "password",
        "username": username,
        "password": password,
    }

    resp = requests.post(TOKEN_URL, data=payload)
    if resp.status_code == 200:
        token_data = resp.json()
        return jsonify({
            "access_token": token_data["access_token"],
            "refresh_token": token_data.get("refresh_token"),
            "expires_in": token_data["expires_in"],
        }), 200
    else:
        return jsonify({"error": "Invalid credentials", "details": resp.text}), 401


# ---------------------------------------------------------------------
# MAIN ENTRY POINT
# ---------------------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
