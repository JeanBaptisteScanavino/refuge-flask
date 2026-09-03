from datetime import datetime, timezone

from flask_login import UserMixin

from ..extensions import db


class User(db.Model, UserMixin):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String, nullable=False)
    twitch_client_id = db.Column(db.String, nullable=True)
    twitch_client_secret = db.Column(db.String, nullable=True)
    twitch_token = db.Column(db.String, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def has_twitch_credentials(self) -> bool:
        return bool(self.twitch_client_id and self.twitch_token)

    def has_twitch_app_credentials(self) -> bool:
        return bool(self.twitch_client_id and self.twitch_client_secret)


class Streamer(db.Model):
    __tablename__ = "streamers"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, nullable=False)
    username_lower = db.Column(db.String, unique=True, index=True, nullable=False)
    broadcaster_id = db.Column(db.String, nullable=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "broadcaster_id": self.broadcaster_id,
        }
