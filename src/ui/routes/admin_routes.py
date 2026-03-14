"""Admin-facing UI routes."""

from flask import Blueprint, render_template
from src.ui.services.participant_admin_service import get_participants_for_list
from src.ui.services.membership_ui_service import get_memberships_for_list

admin_bp = Blueprint(
    "admin",
    __name__,
)


@admin_bp.get("/admin")
def admin_dashboard():
    """Render the admin dashboard."""
    return render_template(
        "admin/dashboard.html",
        page_title="Admin Dashboard",
    )


@admin_bp.get("/admin/participants")
def participants_page():
    """Render the admin participant list page."""
    participants = get_participants_for_list()
    return render_template(
        "admin/participants.html",
        page_title="Participants",
        participants=participants,
    )


@admin_bp.get("/admin/memberships")
def memberships_page():
    """Render the admin memberships page."""
    memberships = get_memberships_for_list()
    return render_template(
        "admin/memberships.html",
        page_title="Memberships",
        memberships=memberships,
    )


@admin_bp.get("/admin/submissions")
def submissions_page():
    return render_template(
        "admin/submissions.html",
        page_title="Submissions",
    )


@admin_bp.get("/admin/corrections")
def corrections_page():
    return render_template(
        "admin/corrections.html",
        page_title="Corrections",
    )


@admin_bp.get("/admin/cycles")
def cycles_page():
    return render_template(
        "admin/cycles.html",
        page_title="Cycles",
    )


@admin_bp.get("/admin/reports")
def reports_page():
    return render_template(
        "admin/reports.html",
        page_title="Reports",
    )


@admin_bp.get("/admin/system")
def system_page():
    return render_template(
        "admin/system.html",
        page_title="System",
    )


@admin_bp.get("/admin/history")
def history_page():
    return render_template(
        "admin/history.html",
        page_title="History",
    )
