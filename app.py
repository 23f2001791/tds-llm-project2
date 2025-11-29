# app.py
import os
import json
from flask import Flask, request, jsonify
from solver import solve_quiz_task

app = Flask(__name__)

# Load expected secret from environment variable
EXPECTED_SECRET = os.environ.get("EXPECTED_SECRET")

@app.route("/", methods=["GET"])
def health_check():
    return "OK", 200

@app.route("/task", methods=["POST"])
def task():
    # Safely parse JSON
    try:
        data = request.get_json(force=True)
    except Exception:
        return jsonify({"error": "invalid_json"}), 400

    # Validate required fields
    if not all(k in data for k in ("email", "secret", "url")):
        return jsonify({"error": "invalid_json"}), 400

    email = data["email"]
    secret = data["secret"]
    url = data["url"]

    # Validate secret
    if secret != EXPECTED_SECRET:
        return jsonify({"error": "forbidden"}), 403

    # Call solver
    try:
        result = solve_quiz_task(email=email, secret=secret, start_url=url, timeout_seconds=170)
    except Exception as e:
        return jsonify({"error": f"solver_failed: {str(e)}"}), 500

    return jsonify(result), 200

if __name__ == "__main__":
    # For local testing
    app.run(host="0.0.0.0", port=7860, debug=True)
