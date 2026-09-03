from werkzeug.security import check_password_hash, generate_password_hash

from ..db.models import User
from ..db.repository import AbstractUserRepository
from ..utils.twitch_client import AbstractTwitchOAuthClient
from .exceptions import InvalidCredentialsException, MissingTwitchAppCredentialsException, UsernameAlreadyExistsException


class RegisterUser:
    def __init__(self, username: str, password: str, repository: AbstractUserRepository):
        self.username = username
        self.password = password
        self.repository = repository

    def register(self) -> User:
        if self.repository.find_by_username(self.username):
            raise UsernameAlreadyExistsException(f"Username '{self.username}' is already taken.")
        user = User(username=self.username, password_hash=generate_password_hash(self.password))
        return self.repository.save(user)


class AuthenticateUser:
    def __init__(self, username: str, password: str, repository: AbstractUserRepository):
        self.username = username
        self.password = password
        self.repository = repository

    def authenticate(self) -> User:
        user = self.repository.find_by_username(self.username)
        if not user or not check_password_hash(user.password_hash, self.password):
            raise InvalidCredentialsException("Invalid username or password.")
        return user


class RefreshTwitchToken:
    def __init__(self, user: User, repository: AbstractUserRepository, oauth_client: AbstractTwitchOAuthClient):
        self.user = user
        self.repository = repository
        self.oauth_client = oauth_client

    def refresh(self) -> User:
        if not self.user.has_twitch_app_credentials():
            raise MissingTwitchAppCredentialsException(
                "No Twitch client_id/client_secret configured for this user. Ask an admin to set them."
            )
        self.user.twitch_token = self.oauth_client.fetch_app_access_token(
            self.user.twitch_client_id, self.user.twitch_client_secret
        )
        return self.repository.save(self.user)
