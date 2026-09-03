from flask import Blueprint, jsonify
from flask_login import current_user, login_required

from ..core.auth_usecase import RefreshTwitchToken
from ..core.exceptions import MissingTwitchAppCredentialsException, TwitchTokenRefreshException
from ..db.repository import UserRepository
from ..utils.twitch_client import TwitchOAuthClient

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.post("/me/token/refresh")
@login_required
def refresh_token():
    try:
        user = RefreshTwitchToken(current_user, UserRepository(), TwitchOAuthClient()).refresh()
    except MissingTwitchAppCredentialsException as exc:
        return jsonify({"error": str(exc)}), 400
    except TwitchTokenRefreshException as exc:
        return jsonify({"error": str(exc)}), 502

    return jsonify(
        {"id": user.id, "username": user.username, "has_twitch_credentials": user.has_twitch_credentials()}
    ), 200
