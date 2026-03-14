"""Participant-facing UI routes."""

from flask import Blueprint, render_template

participant_bp = Blueprint(
    "participant",
    __name__,
)

@participant_bp.get("/submit")
def submit_page():
    """Render the participant submission page."""
    return render_template(
        "participant/submit.html",
        page_title="Submit Daily Score",
    )
