from flask import Blueprint, jsonify, request
from flask_login import login_required, login_user, logout_user

from ..core.auth_usecase import AuthenticateUser
from ..core.exceptions import InvalidCredentialsException
from ..db.repository import UserRepository

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "username and password are required"}), 400

    try:
        user = AuthenticateUser(username, password, UserRepository()).authenticate()
    except InvalidCredentialsException as exc:
        return jsonify({"error": str(exc)}), 401

    login_user(user)
    return jsonify({"id": user.id, "username": user.username}), 200


@auth_bp.post("/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "logged out"}), 200
