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


@streamers_bp.post("/bulk")
@login_required
def create_streamers_bulk():
    """
    Bulk create streamers from a list of usernames.
    
    Request body:
    {
        "usernames": ["username1", "username2", "username3"]
    }
    
    Response:
    {
        "created": 2,
        "failed": 1,
        "already_exists": 0,
        "results": [
            {"username": "username1", "status": "created", "id": 123},
            {"username": "username2", "status": "error", "message": "Not found on Twitch"},
            {"username": "username3", "status": "already_exists"}
        ]
    }
    """
    data = request.get_json(silent=True) or {}
    usernames = data.get("usernames", [])
    
    if not usernames or not isinstance(usernames, list):
        return jsonify({"error": "usernames list is required"}), 400
    
    if len(usernames) > 100:
        return jsonify({"error": "Maximum 100 streamers per request"}), 400
    
    try:
        twitch_client = build_twitch_client_for_user(current_user)
    except MissingTwitchCredentialsException as exc:
        return jsonify({"error": str(exc)}), 400
    
    results = []
    created_count = 0
    failed_count = 0
    already_exists_count = 0
    
    for username in usernames:
        username = username.strip()
        if not username:
            continue
        
        try:
            streamer = CreateStreamer(username, StreamersRepository(), twitch_client).create()
            results.append({
                "username": username,
                "status": "created",
                "id": streamer.id,
                "broadcaster_id": streamer.broadcaster_id
            })
            created_count += 1
        except StreamerAlreadyExistsException:
            results.append({
                "username": username,
                "status": "already_exists"
            })
            already_exists_count += 1
        except StreamersDoesNotExistException as exc:
            results.append({
                "username": username,
                "status": "error",
                "message": "Not found on Twitch"
            })
            failed_count += 1
        except Exception as exc:
            results.append({
                "username": username,
                "status": "error",
                "message": str(exc)[:100]
            })
            failed_count += 1
    
    return jsonify({
        "created": created_count,
        "failed": failed_count,
        "already_exists": already_exists_count,
        "total": len(results),
        "results": results
    }), 201


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
