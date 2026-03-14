"""UI application entrypoint for the gym-challenge web interface."""

from flask import Flask, render_template


def create_app() -> Flask:
    """Create and configure the Flask application for the UI layer."""
    app = Flask(__name__)

    @app.get("/")
    def home() -> str:
        """Render the shared base template as a simple UI smoke test."""
        return render_template("base.html", page_title="gym-challenge UI")

    return app
