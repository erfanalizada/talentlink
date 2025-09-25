from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/api/auth/register", methods=["POST"])
def register():
    return jsonify({"message": "User registered (hardcoded)"})

@app.route("/api/auth/login", methods=["POST"])
def login():
    return jsonify({"token": "fake-jwt-token"})

@app.route("/api/auth/health")
def health():
    return {"status": "auth-service ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
