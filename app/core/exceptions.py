class StreamersDoesNotExistException(Exception):
    """Raised when a streamer is not found via the Twitch API."""


class StreamerAlreadyExistsException(Exception):
    """Raised when a streamer with the same username is already stored."""


class UsernameAlreadyExistsException(Exception):
    """Raised when registering with a username that is already taken."""


class InvalidCredentialsException(Exception):
    """Raised when login credentials do not match a stored user."""


class MissingTwitchCredentialsException(Exception):
    """Raised when a user has not set their Twitch client_id/token yet."""


class MissingTwitchAppCredentialsException(Exception):
    """Raised when a user has no Twitch client_id/client_secret configured by an admin."""


class TwitchTokenRefreshException(Exception):
    """Raised when Twitch's OAuth token endpoint fails to return an access token."""
