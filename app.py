import secrets
from functools import wraps

from flask import Flask, jsonify, request

from models import User, get_session

app = Flask(__name__)
HARDCODED_PASSWORD = "password123"
active_tokens = {}

def require_token(view):
    @wraps(view)
    def authenticated_view(*args, **kwargs):
        authorization = request.headers.get("Authorization", "")
        scheme, _, token = authorization.partition(" ")
        email = active_tokens.get(token) if scheme.lower() == "bearer" else None
        if email is None:
            return jsonify({"message": "Authentication required"}), 401

        return view(email, *args, **kwargs)

    return authenticated_view

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email") if isinstance(data, dict) else None
    password = data.get("password") if isinstance(data, dict) else None
    if not email or password != HARDCODED_PASSWORD:
        return jsonify({"message": "Invalid email or password"}), 400

    session = get_session()

    try:
        user = session.query(User).filter_by(email=email).one_or_none()
        if user is None or user.logged_in:
            return jsonify({"message": "User is already logged in or does not exist"}), 400

        user.logged_in = True
        session.commit()
        token = secrets.token_urlsafe(32)
        active_tokens[token] = user.email
        return jsonify({"message": "Login successful", "token": token}), 200
    except Exception:
        session.rollback()
        return jsonify({"message": "Login failed"}), 400
    finally:
        session.close()

@app.route("/get_areas", methods=["GET"])
@require_token
def get_areas(email):

    session = get_session()
    
    try:
        user = session.query(User).filter_by(email=email).one_or_none()
        if user is None:
            return jsonify({"message": "User does not exist"}), 400

        areas = [
            {"id": area.id, "name": area.name}
            for area in user.areas
        ]
        return jsonify({"areas": areas}), 200
    except Exception:
        return jsonify({"message": "Failed to fetch areas"}), 400
    finally:
        session.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
