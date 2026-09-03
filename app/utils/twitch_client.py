from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Dict, Optional

import requests

from ..core.exceptions import MissingTwitchCredentialsException, TwitchTokenRefreshException

if TYPE_CHECKING:
    from ..db.models import User


class AbstractTwitchClient(ABC):
    @abstractmethod
    def retrieve_user_infos_by_username(self, username: str) -> Optional[Dict]:
        pass

    @abstractmethod
    def retrieve_followers_by_broadcaster_id(self, broadcaster_id: str) -> Dict:
        pass


class TwitchClient(AbstractTwitchClient):
    def __init__(self, client_id: str, token: str):
        self.base_url = "https://api.twitch.tv/helix/"
        self.head_data = {"Client-ID": client_id, "Authorization": f"Bearer {token}"}

    def retrieve_user_infos_by_username(self, username: str) -> Optional[Dict]:
        url = f"{self.base_url}users?login={username}"
        response = requests.get(url, headers=self.head_data)
        data = response.json()
        return data["data"][0] if data.get("data") else None

    def retrieve_followers_by_broadcaster_id(self, broadcaster_id: str) -> Dict:
        url = f"{self.base_url}channels/followers?broadcaster_id={broadcaster_id}"
        response = requests.get(url, headers=self.head_data)
        return response.json()


class TwitchTrackerClient:
    def __init__(self):
        self.tracker_url = "https://twitchtracker.com/api/channels/summary/"

    def retrieve_summary(self, username_lower: str) -> Dict:
        response = requests.get(self.tracker_url + username_lower)
        return response.json()


def build_twitch_client_for_user(user: "User") -> TwitchClient:
    if not user.has_twitch_credentials():
        raise MissingTwitchCredentialsException("No Twitch token yet - click 'Refresh token' first.")
    return TwitchClient(user.twitch_client_id, user.twitch_token)


class AbstractTwitchOAuthClient(ABC):
    @abstractmethod
    def fetch_app_access_token(self, client_id: str, client_secret: str) -> str:
        pass


class TwitchOAuthClient(AbstractTwitchOAuthClient):
    def __init__(self):
        self.token_url = "https://id.twitch.tv/oauth2/token"

    def fetch_app_access_token(self, client_id: str, client_secret: str) -> str:
        response = requests.post(
            self.token_url,
            params={"client_id": client_id, "client_secret": client_secret, "grant_type": "client_credentials"},
        )
        data = response.json()
        if "access_token" not in data:
            raise TwitchTokenRefreshException(data.get("message", "Failed to refresh Twitch token."))
        return data["access_token"]
