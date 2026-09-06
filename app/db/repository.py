from abc import ABC, abstractmethod
from typing import List, Optional

from ..extensions import db
from .models import APIToken, Streamer, User


class AbstractUserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def find_by_username(self, username: str) -> Optional[User]:
        pass


class UserRepository(AbstractUserRepository):
    def save(self, user: User) -> User:
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        return user

    def find_by_username(self, username: str) -> Optional[User]:
        return db.session.query(User).filter(User.username == username).first()


class AbstractStreamersRepository(ABC):
    @abstractmethod
    def save(self, streamer: Streamer) -> Streamer:
        pass

    @abstractmethod
    def find_by_username(self, username_lower: str) -> Optional[Streamer]:
        pass

    @abstractmethod
    def find_all(self) -> List[Streamer]:
        pass


class StreamersRepository(AbstractStreamersRepository):
    def save(self, streamer: Streamer) -> Streamer:
        db.session.add(streamer)
        db.session.commit()
        db.session.refresh(streamer)
        return streamer

    def find_by_username(self, username_lower: str) -> Optional[Streamer]:
        return db.session.query(Streamer).filter(Streamer.username_lower == username_lower.lower()).first()

    def find_all(self) -> List[Streamer]:
        return db.session.query(Streamer).order_by(Streamer.username_lower).all()


class AbstractAPITokenRepository(ABC):
    @abstractmethod
    def save(self, token: APIToken) -> APIToken:
        pass

    @abstractmethod
    def find_by_hash(self, token_hash: str) -> Optional[APIToken]:
        pass

    @abstractmethod
    def find_by_id(self, token_id: int) -> Optional[APIToken]:
        pass

    @abstractmethod
    def find_all(self) -> List[APIToken]:
        pass


class APITokenRepository(AbstractAPITokenRepository):
    def save(self, token: APIToken) -> APIToken:
        db.session.add(token)
        db.session.commit()
        db.session.refresh(token)
        return token

    def find_by_hash(self, token_hash: str) -> Optional[APIToken]:
        return db.session.query(APIToken).filter(APIToken.token_hash == token_hash).first()

    def find_by_id(self, token_id: int) -> Optional[APIToken]:
        return db.session.get(APIToken, token_id)

    def find_all(self) -> List[APIToken]:
        return db.session.query(APIToken).order_by(APIToken.created_at).all()
