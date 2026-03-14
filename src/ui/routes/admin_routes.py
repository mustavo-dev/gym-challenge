"""Admin-facing UI routes."""

from flask import Blueprint, render_template, request, redirect, url_for

from src.ui.services.participant_admin_service import get_participants_for_list
from src.ui.services.membership_ui_service import get_memberships_for_list
from src.ui.services.cycle_ui_service import get_cycles_for_list
from src.ui.services.submission_ui_service import get_submissions_for_list
from src.ui.services.correction_ui_service import get_corrections_for_list
from src.ui.services.history_ui_service import get_history_for_list

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


@admin_bp.route("/admin/participants", methods=["GET", "POST"])
def participants_page():
    if request.method == "POST":
        first = request.form.get("first_name", "").strip()
        last = request.form.get("last_name", "").strip()

        if first and last:
            from src.gymchallenge.participant_ops import generate_participant_id
            from src.gymchallenge.storage_ops import append_row
            from src.gymchallenge.storage_json import load_list
            from src.gymchallenge.data_paths import data_path
            from datetime import datetime
            from zoneinfo import ZoneInfo

            BERLIN = ZoneInfo("Europe/Berlin")

            path = data_path("participants.json")
            existing = load_list(path)

            participant_id = generate_participant_id(
                first=first,
                last=last,
                existing_rows=existing,
            )

            row = {
                "participant_id": participant_id,
                "first_name": first,
                "last_name": last,
                "created_at": datetime.now(BERLIN).isoformat(),
                "active": True,
            }

            append_row(path, row)

        return redirect(url_for("admin.participants_page"))

    participants = get_participants_for_list()

    return render_template(
        "admin/participants.html",
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
    """Render the admin submissions page."""
    submissions = get_submissions_for_list()
    return render_template(
        "admin/submissions.html",
        page_title="Submissions",
        submissions=submissions,
        total=len(submissions),
    )


@admin_bp.get("/admin/corrections")
def corrections_page():
    """Render the admin corrections page."""
    corrections = get_corrections_for_list()
    return render_template(
        "admin/corrections.html",
        page_title="Corrections",
        corrections=corrections,
        total=len(corrections),
    )


@admin_bp.get("/admin/cycles")
def cycles_page():
    """Render the admin cycles page."""
    cycles = get_cycles_for_list()
    return render_template(
        "admin/cycles.html",
        page_title="Cycles",
        cycles=cycles,
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
    """Render the admin history page."""
    history_items = get_history_for_list()
    return render_template(
        "admin/history.html",
        page_title="History",
        history_items=history_items,
        total=len(history_items),
    )
