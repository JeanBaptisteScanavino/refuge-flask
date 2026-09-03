from ..db.repository import AbstractStreamersRepository
from ..utils.twitch_client import AbstractTwitchClient, TwitchTrackerClient


class GetStreamerInfos:
    def __init__(
        self,
        username: str,
        streamers_repository: AbstractStreamersRepository,
        twitch_client: AbstractTwitchClient,
        tracker_client: TwitchTrackerClient,
    ):
        self.username_lower = username.lower()
        self.streamers_repository = streamers_repository
        self.twitch_client = twitch_client
        self.tracker_client = tracker_client

    def get_infos(self) -> dict:
        streamer = self.streamers_repository.find_by_username(self.username_lower)
        result = self.tracker_client.retrieve_summary(self.username_lower)

        if streamer and streamer.broadcaster_id:
            data = self.twitch_client.retrieve_followers_by_broadcaster_id(streamer.broadcaster_id)
            result["followers_total_twitch"] = data.get("total", 0)

        return result
