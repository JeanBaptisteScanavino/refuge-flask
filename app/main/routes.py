from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user

from ..core.auth_usecase import AuthenticateUser, RefreshTwitchToken
from ..core.exceptions import (
    InvalidCredentialsException,
    MissingTwitchAppCredentialsException,
    MissingTwitchCredentialsException,
    StreamerAlreadyExistsException,
    StreamersDoesNotExistException,
    TwitchTokenRefreshException,
)
from ..core.streamers_usecase import CreateStreamer
from ..db.repository import StreamersRepository, UserRepository
from ..utils.twitch_client import TwitchOAuthClient, build_twitch_client_for_user

main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def index():
    streamers = StreamersRepository().find_all() if current_user.is_authenticated else None
    return render_template("home.html", streamers=streamers)


@main_bp.post("/login")
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    try:
        user = AuthenticateUser(username, password, UserRepository()).authenticate()
    except InvalidCredentialsException as exc:
        flash(str(exc))
        return redirect(url_for("main.index"))

    login_user(user)
    return redirect(url_for("main.index"))


@main_bp.post("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@main_bp.post("/token")
@login_required
def refresh_token():
    try:
        RefreshTwitchToken(current_user, UserRepository(), TwitchOAuthClient()).refresh()
    except (MissingTwitchAppCredentialsException, TwitchTokenRefreshException) as exc:
        flash(str(exc))
        return redirect(url_for("main.index"))

    flash("Token refreshed.")
    return redirect(url_for("main.index"))


@main_bp.post("/streamers")
@login_required
def create_streamer():
    username = request.form.get("username")
    if not username:
        flash("username is required")
        return redirect(url_for("main.index"))

    try:
        twitch_client = build_twitch_client_for_user(current_user)
        CreateStreamer(username, StreamersRepository(), twitch_client).create()
    except (
        MissingTwitchCredentialsException,
        StreamerAlreadyExistsException,
        StreamersDoesNotExistException,
    ) as exc:
        flash(str(exc))

    return redirect(url_for("main.index"))
