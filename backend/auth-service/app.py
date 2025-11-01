import os
import psycopg2
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # allow frontend requests

# --- Database Config ---
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# --- Keycloak Config ---
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "https://talentlink-erfan.nl/auth")
KEYCLOAK_REALM = os.getenv("KEYCLOAK_REALM", "talentlink")
KEYCLOAK_ADMIN_USER = os.getenv("KEYCLOAK_ADMIN_USER", "auth-service-admin")
KEYCLOAK_ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "StrongPassword123!")
KEYCLOAK_CLIENT_ID = "admin-cli"


# --- Helper: Get admin access token ---
def get_admin_token():
    token_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": KEYCLOAK_CLIENT_ID,
        "username": KEYCLOAK_ADMIN_USER,
        "password": KEYCLOAK_ADMIN_PASSWORD,
    }

    response = requests.post(token_url, data=data)
    if response.status_code != 200:
        print("❌ Failed to get admin token:", response.text)
        raise Exception("Failed to authenticate admin")

    token = response.json()["access_token"]
    return token


# --- Health check endpoint ---
@app.route("/api/auth/dbtest")
def db_test():
    try:
        with psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        ) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 'DB connection OK' AS message;")
                result = cur.fetchone()
                return jsonify({"db": result[0]}), 200
    except Exception as e:
        print("❌ DB connection failed:", e)
        return jsonify({"error": str(e)}), 500


# --- Register endpoint ---
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

        # 1️⃣ Create the user
        user_payload = {
            "username": username,
            "email": email,
            "enabled": True,
            "emailVerified": True,
            "credentials": [{"type": "password", "value": password, "temporary": False}],
        }

        create_user_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
        create_resp = requests.post(create_user_url, json=user_payload, headers=headers)

        if create_resp.status_code not in [201, 409]:
            return jsonify({
                "error": "Failed to create user",
                "details": create_resp.text
            }), 500

        # 2️⃣ Get the user ID
        user_search_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users"
        user_id_resp = requests.get(
            user_search_url, params={"username": username}, headers=headers
        )
        user_id = user_id_resp.json()[0]["id"]

        # 3️⃣ Assign role (realm-level)
        role_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/roles/{role}"
        role_resp = requests.get(role_url, headers=headers)

        if role_resp.status_code == 200:
            role_info = role_resp.json()
            assign_url = f"{KEYCLOAK_URL}/admin/realms/{KEYCLOAK_REALM}/users/{user_id}/role-mappings/realm"
            requests.post(assign_url, json=[role_info], headers=headers)
        else:
            print(f"⚠️ Role '{role}' not found, skipping role assignment")

        print(f"✅ User '{username}' created successfully with role '{role}'")
        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# --- Login endpoint ---
@app.route("/api/auth/login", methods=["POST"])
def login_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    token_url = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/token"
    login_data = {
        "grant_type": "password",
        "client_id": "frontend-client",  # the Keycloak client your frontend uses
        "username": username,
        "password": password,
    }

    resp = requests.post(token_url, data=login_data)

    if resp.status_code == 200:
        print(f"✅ Login success for {username}")
        return jsonify(resp.json()), 200
    else:
        print(f"❌ Login failed for {username}: {resp.text}")
        return jsonify({"error": "Invalid credentials", "details": resp.text}), 401


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
