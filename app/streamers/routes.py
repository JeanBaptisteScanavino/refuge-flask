from flask import Blueprint, jsonify, request
from datetime import datetime
from flask_login import current_user, login_required

from ..core.exceptions import (
    MissingTwitchCredentialsException,
    StreamerAlreadyExistsException,
    StreamersDoesNotExistException,
)
from ..core.infos_usecase import GetStreamerInfos
from ..core.streamers_usecase import CreateStreamer
from ..db.repository import StreamersRepository
from ..utils.twitch_client import TwitchTrackerClient, build_twitch_client_for_user

streamers_bp = Blueprint("streamers", __name__, url_prefix="/streamers")


@streamers_bp.post("/")
@login_required
def create_streamer():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    if not username:
        return jsonify({"error": "username is required"}), 400

    try:
        twitch_client = build_twitch_client_for_user(current_user)
        streamer = CreateStreamer(username, StreamersRepository(), twitch_client).create()
    except MissingTwitchCredentialsException as exc:
        return jsonify({"error": str(exc)}), 400
    except StreamerAlreadyExistsException as exc:
        return jsonify({"error": str(exc)}), 409
    except StreamersDoesNotExistException as exc:
        return jsonify({"error": str(exc)}), 404

    return jsonify(streamer.to_dict()), 201


@streamers_bp.get("/<username>")
@login_required
def get_streamer_infos(username):
    try:
        twitch_client = build_twitch_client_for_user(current_user)
    except MissingTwitchCredentialsException as exc:
        return jsonify({"error": str(exc)}), 400

    infos = GetStreamerInfos(username, StreamersRepository(), twitch_client, TwitchTrackerClient()).get_infos()
    return jsonify(infos), 200

@streamers_bp.get("/all")
@login_required
def get_streamers_list():
    streamers = StreamersRepository().find_all()
    markdown_content = "**Liste des membres au {}**".format(datetime.now().strftime("%d/%m/%Y"))
    markdown_content += "\n" + "\n".join(
        f"https://www.twitch.tv/{streamer.username}"
        for streamer in streamers
    )
    return markdown_content, 200, {"Content-Type": "text/markdown"}

