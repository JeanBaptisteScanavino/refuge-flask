import hashlib
import secrets
from datetime import datetime, timezone
from typing import Optional, Tuple

from ..db.models import APIToken, User
from ..db.repository import AbstractAPITokenRepository, AbstractUserRepository
from .exceptions import APITokenDoesNotExistException, UserDoesNotExistException


def _hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


class CreateAPIToken:
    def __init__(self, username: str, name: Optional[str], user_repository: AbstractUserRepository, token_repository: AbstractAPITokenRepository):
        self.username = username
        self.name = name
        self.user_repository = user_repository
        self.token_repository = token_repository

    def create(self) -> Tuple[str, APIToken]:
        user = self.user_repository.find_by_username(self.username)
        if not user:
            raise UserDoesNotExistException(f"Username '{self.username}' does not exist.")

        raw_token = secrets.token_urlsafe(32)
        api_token = APIToken(user_id=user.id, token_hash=_hash_token(raw_token), name=self.name)
        return raw_token, self.token_repository.save(api_token)


class RevokeAPIToken:
    def __init__(self, token_id: int, token_repository: AbstractAPITokenRepository):
        self.token_id = token_id
        self.token_repository = token_repository

    def revoke(self) -> APIToken:
        api_token = self.token_repository.find_by_id(self.token_id)
        if not api_token:
            raise APITokenDoesNotExistException(f"API token with id '{self.token_id}' does not exist.")

        api_token.revoked = True
        api_token.revoked_at = datetime.now(timezone.utc)
        return self.token_repository.save(api_token)


class ValidateAPIToken:
    def __init__(self, raw_token: str, token_repository: AbstractAPITokenRepository):
        self.raw_token = raw_token
        self.token_repository = token_repository

    def validate(self) -> Optional[User]:
        api_token = self.token_repository.find_by_hash(_hash_token(self.raw_token))
        if not api_token or api_token.revoked:
            return None

        api_token.last_used_at = datetime.now(timezone.utc)
        self.token_repository.save(api_token)
        return api_token.user
