
import os
from flask import Flask, jsonify, request
import psycopg2
from psycopg2.extras import RealDictCursor

app = Flask(__name__)

def get_db():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        database=os.getenv("POSTGRES_DB", "festpass"),
        user=os.getenv("POSTGRES_USER", "festpass"),
        password=os.getenv("POSTGRES_PASSWORD", "festpass_dev_password"),
        cursor_factory=RealDictCursor
    )

@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "FestPass API"})

@app.get("/registrations")
def registrations():
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, email FROM registrations ORDER BY id"
            )
            rows = cur.fetchall()
    return jsonify(rows)

@app.post("/registrations")
def create_registration():
    data = request.get_json(silent=True) or {}
    name = data.get("name")
    email = data.get("email")

    if not name or not email:
        return jsonify({"error": "name and email are required"}), 400

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO registrations (name, email) VALUES (%s, %s) "
                "RETURNING id, name, email",
                (name, email)
            )
            row = cur.fetchone()

    return jsonify(row), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
