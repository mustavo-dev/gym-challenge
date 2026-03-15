"""UI application entrypoint for the gym-challenge web interface."""

from flask import Flask, render_template

from src.ui.routes.participant_routes import participant_bp
from src.ui.routes.admin_routes import admin_bp


def create_app() -> Flask:
    """Create and configure the Flask application for the UI layer."""
    app = Flask(__name__)
    app.secret_key = "dev-secret-key"

    app.register_blueprint(participant_bp)
    app.register_blueprint(admin_bp)

    @app.get("/")
    def home() -> str:
        """Render the shared base template."""
        return render_template("base.html", page_title="gym-challenge UI")

    return app
