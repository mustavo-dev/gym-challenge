"""UI application entrypoint for the gym-challenge web interface."""

from flask import Flask


def create_app() -> Flask:
    """Create and configure the Flask application for the UI layer."""
    app = Flask(__name__)

    @app.get("/")
    def healthcheck() -> str:
        return "gym-challenge UI app is running"

    return app
