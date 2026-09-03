import click
from flask import Flask

from .core.auth_usecase import RegisterUser
from .db.repository import UserRepository


def register_cli(app: Flask) -> None:
    @app.cli.command("create-user")
    @click.argument("username")
    @click.argument("client_id")
    @click.argument("client_secret")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_user(username: str, client_id: str, client_secret: str, password: str) -> None:
        """Create a user with Twitch app credentials (self-registration is disabled)."""
        user = RegisterUser(username, password, UserRepository()).register()
        user.twitch_client_id = client_id
        user.twitch_client_secret = client_secret
        UserRepository().save(user)
        click.echo(f"Created user '{user.username}' (id={user.id}).")
