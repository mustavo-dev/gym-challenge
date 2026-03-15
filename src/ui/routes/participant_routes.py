"""Participant-facing UI routes."""

from flask import Blueprint, render_template
from src.ui.services.submit_ui_service import get_submit_page_context

participant_bp = Blueprint(
    "participant",
    __name__,
)

@participant_bp.get("/submit")
def submit_page():
    context = get_submit_page_context()

    return render_template(
        "participant/submit.html",
        active_cycle=context["active_cycle"],
        participant_choices=context["participant_choices"],
        submit_enabled=context["submit_enabled"],
        submit_message=context["submit_message"],
    )
