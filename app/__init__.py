from dotenv import load_dotenv
from flask import Flask

load_dotenv()

from . import extensions
from .config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    extensions.db.init_app(app)
    extensions.migrate.init_app(app, extensions.db)
    extensions.login_manager.init_app(app)

    # Import after extensions.db.init_app to avoid the `db` submodule shadowing
    # the `extensions.db` SQLAlchemy instance on this package's namespace.
    from .db.models import User

    @extensions.login_manager.user_loader
    def load_user(user_id):
        return extensions.db.session.get(User, int(user_id))

    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .streamers.routes import streamers_bp
    from .users.routes import users_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(streamers_bp)

    from .cli import register_cli

    register_cli(app)

    return app
