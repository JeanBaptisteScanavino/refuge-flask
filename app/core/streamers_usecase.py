from ..db.models import Streamer
from ..db.repository import AbstractStreamersRepository
from ..utils.twitch_client import AbstractTwitchClient
from .exceptions import StreamerAlreadyExistsException, StreamersDoesNotExistException


class CreateStreamer:
    def __init__(
        self, username: str, repository: AbstractStreamersRepository, twitch_client: AbstractTwitchClient
    ) -> None:
        self.username = username
        self.repository = repository
        self.twitch_client = twitch_client

    def create(self) -> Streamer:
        username_lower = self.username.lower()
        if self.repository.find_by_username(username_lower):
            raise StreamerAlreadyExistsException(f"Streamer with username '{self.username}' already exists.")

        streamer_infos = self.twitch_client.retrieve_user_infos_by_username(username=self.username)
        if not streamer_infos:
            raise StreamersDoesNotExistException(f"Streamer with username '{self.username}' does not exist.")

        streamer = Streamer(
            username=self.username,
            username_lower=username_lower,
            broadcaster_id=streamer_infos["id"],
        )
        return self.repository.save(streamer)
