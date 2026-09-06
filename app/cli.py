import click
from flask import Flask

from .core.auth_usecase import RegisterUser
from .core.api_token_usecase import CreateAPIToken, RevokeAPIToken
from .core.exceptions import APITokenDoesNotExistException, UserDoesNotExistException
from .db.repository import APITokenRepository, UserRepository


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

    @app.cli.command("create-api-token")
    @click.argument("username")
    @click.argument("name")
    def create_api_token(username: str, name: str) -> None:
        """Create a non-expiring API token for a user (never shown again)."""
        try:
            raw_token, api_token = CreateAPIToken(username, name, UserRepository(), APITokenRepository()).create()
        except UserDoesNotExistException as exc:
            raise click.ClickException(str(exc))
        click.echo(f"Token (id={api_token.id}), copy it now, it will not be shown again:")
        click.echo(raw_token)

    @app.cli.command("revoke-api-token")
    @click.argument("token_id", type=int)
    def revoke_api_token(token_id: int) -> None:
        """Revoke an API token by id."""
        try:
            RevokeAPIToken(token_id, APITokenRepository()).revoke()
        except APITokenDoesNotExistException as exc:
            raise click.ClickException(str(exc))
        click.echo(f"Revoked API token (id={token_id}).")

    @app.cli.command("list-api-tokens")
    def list_api_tokens() -> None:
        """List all API tokens."""
        tokens = APITokenRepository().find_all()
        for token in tokens:
            click.echo(
                f"id={token.id} user={token.user.username} name={token.name} "
                f"revoked={token.revoked} created_at={token.created_at} "
                f"last_used_at={token.last_used_at}"
            )

