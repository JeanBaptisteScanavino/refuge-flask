from functools import wraps

from flask import g, jsonify, request
from flask_login import current_user

from ..core.api_token_usecase import ValidateAPIToken
from ..db.repository import APITokenRepository


def get_current_user():
    return getattr(g, "api_user", None) or current_user


def token_or_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            raw_token = auth_header[len("Bearer "):]
            user = ValidateAPIToken(raw_token, APITokenRepository()).validate()
            if not user:
                return jsonify({"error": "Invalid or revoked token"}), 401
            g.api_user = user
            return f(*args, **kwargs)

        if current_user.is_authenticated:
            return f(*args, **kwargs)

        return jsonify({"error": "Authentication required"}), 401

    return decorated_function
