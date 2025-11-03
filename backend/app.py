from flask import Flask

app = Flask(__name__)

@app.route("/api/users/test-db", methods=["POST"])
def test_db():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT NOW()")).fetchone()
            return {"message": "Database OK", "time": str(result[0])}, 200
    except Exception as e:
        return {"error": str(e)}, 500


@app.route("/api/hello")
def hello():
    return {"message": "Hello from backend"}

@app.route("/api/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
