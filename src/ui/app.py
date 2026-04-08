"""UI application entrypoint for the gym-challenge web interface."""

from flask import Flask, render_template

from src.ui.routes.participant_routes import participant_bp
from src.ui.routes.admin_routes import admin_bp


def create_app(instance_path: str | None = None) -> Flask:
    """Create and configure the Flask application for the UI layer."""
    if instance_path is None:
        app = Flask(__name__, instance_relative_config=True)
    else:
        app = Flask(
            __name__,
            instance_path=instance_path,
            instance_relative_config=True,
        )

    app.secret_key = "dev-secret-key"
    app.config.setdefault("CHALLENGE_NAME", "gym-challenge")
    app.config.setdefault("GYM_NAME", "Default Gym")
    app.config.setdefault("ADMIN_NAME", "Admin")
    app.config.setdefault("GYM_TIMEZONE", "Europe/Berlin")

    try:
        app.config.from_pyfile("config.py")
    except FileNotFoundError:
        pass

    app.register_blueprint(participant_bp)
    app.register_blueprint(admin_bp)

    @app.get("/")
    def home() -> str:
        """Render the shared base template."""
        return render_template(
            "base.html",
            page_title=f'{app.config["CHALLENGE_NAME"]} UI',
        )

    return app