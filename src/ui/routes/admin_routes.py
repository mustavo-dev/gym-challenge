"""Admin-facing UI routes."""

from flask import Blueprint, render_template, request, redirect, url_for, flash

from src.ui.services.participant_admin_service import get_participants_for_list, get_participant_choices
from src.ui.services.membership_ui_service import get_memberships_for_list, filter_memberships_for_view
from src.ui.services.cycle_ui_service import get_cycles_for_list, find_cycle_id_for_score_day
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

        if not first or not last:
            flash("First name and last name are required.", "error")
            return redirect(url_for("admin.participants_page"))

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

        flash(f"Added participant: {participant_id}", "success")
        return redirect(url_for("admin.participants_page"))

    participants = get_participants_for_list()

    return render_template(
        "admin/participants.html",
        participants=participants,
    )


@admin_bp.route("/admin/memberships", methods=["GET", "POST"])
def memberships_page():
    if request.method == "POST":
        cycle_id = request.form.get("cycle_id", "").strip()
        participant_id = request.form.get("participant_id", "").strip()

        if not (cycle_id and participant_id):
            flash("Cycle and participant are required.", "error")
            return redirect(url_for("admin.memberships_page"))

        from datetime import datetime
        from zoneinfo import ZoneInfo

        from src.gymchallenge.data_paths import data_path
        from src.gymchallenge.storage_json import load_list
        from src.gymchallenge.storage_ops import append_row
        from src.gymchallenge.membership_store import find_membership_index

        BERLIN = ZoneInfo("Europe/Berlin")

        path = data_path("memberships.json")
        rows = load_list(path)

        existing_index = find_membership_index(
            rows,
            cycle_id=cycle_id,
            participant_id=participant_id,
        )
        if existing_index is not None:
            flash("Participant is already a member of that cycle.", "error")
            return redirect(url_for("admin.memberships_page"))

        row = {
            "cycle_id": cycle_id,
            "participant_id": participant_id,
            "active_in_cycle": True,
            "joined_at": datetime.now(BERLIN).isoformat(),
            "left_at": None,
            "inactive_reason": None,
            "inactive_effective_score_day": None,
        }

        append_row(path, row)

        flash("Member successfully added to cycle.", "success")
        return redirect(url_for("admin.memberships_page"))

    membership_filter = request.args.get("membership_filter", "all").strip()

    memberships = get_memberships_for_list()
    memberships = filter_memberships_for_view(memberships, membership_filter)

    participant_choices = get_participant_choices()
    cycle_choices = get_cycles_for_list()

    return render_template(
        "admin/memberships.html",
        page_title="Memberships",
        memberships=memberships,
        participant_choices=participant_choices,
        cycle_choices=cycle_choices,
        membership_filter=membership_filter,
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


@admin_bp.route("/admin/corrections", methods=["GET", "POST"])
def corrections_page():
    if request.method == "POST":
        participant_id = request.form.get("participant_id", "").strip()
        score_day = request.form.get("score_day", "").strip()
        new_points_raw = request.form.get("new_points", "").strip()
        reason = request.form.get("reason", "").strip()

        if not (participant_id and score_day and new_points_raw and reason):
            flash("All correction fields are required.", "error")
            return redirect(url_for("admin.corrections_page"))

        from datetime import date, datetime
        from zoneinfo import ZoneInfo

        from src.gymchallenge.id_ops import new_correction_id
        from src.gymchallenge.storage_json import load_list
        from src.gymchallenge.storage_ops import append_row
        from src.gymchallenge.data_paths import data_path

        BERLIN = ZoneInfo("Europe/Berlin")

        try:
            new_points = int(new_points_raw)
        except ValueError:
            flash("Points must be a number.", "error")
            return redirect(url_for("admin.corrections_page"))

        try:
            score_day_date = date.fromisoformat(score_day)
        except ValueError:
            flash("Score day must be a valid date.", "error")
            return redirect(url_for("admin.corrections_page"))

        cycle_id = find_cycle_id_for_score_day(score_day_date)
        if cycle_id is None:
            flash("No matching cycle found for that score day.", "error")
            return redirect(url_for("admin.corrections_page"))

        correction_id = new_correction_id()

        row = {
            "correction_id": correction_id,
            "cycle_id": cycle_id,
            "participant_id": participant_id,
            "score_day": score_day_date.isoformat(),
            "new_points": new_points,
            "reason": reason,
            "created_at": datetime.now(BERLIN).isoformat(),
            "admin": "jayme",
        }

        append_row(data_path("corrections.json"), row)

        flash(f"Correction added for participant.", "success")
        return redirect(url_for("admin.corrections_page"))

    corrections = get_corrections_for_list()
    participant_choices = get_participant_choices()

    return render_template(
        "admin/corrections.html",
        page_title="Corrections",
        corrections=corrections,
        participant_choices=participant_choices,
        total=len(corrections),
    )


@admin_bp.route("/admin/cycles", methods=["GET", "POST"])
def cycles_page():
    if request.method == "POST":
        season = request.form.get("season", "").strip().lower()
        year_raw = request.form.get("year", "").strip()
        start_day = request.form.get("start_day", "").strip()
        end_day = request.form.get("end_day", "").strip()

        if not (season and year_raw and start_day and end_day):
            flash("All cycle fields are required.", "error")
            return redirect(url_for("admin.cycles_page"))

        from datetime import date, datetime
        from zoneinfo import ZoneInfo

        from src.gymchallenge.cycle_ops import build_cycle_id, build_cycle_name, has_cycle_id
        from src.gymchallenge.cycle_timeline import cycle_overlaps_existing
        from src.gymchallenge.data_paths import data_path
        from src.gymchallenge.loaders import load_cycles
        from src.gymchallenge.storage_json import load_list
        from src.gymchallenge.storage_ops import append_row
        from src.gymchallenge.models import Cycle

        BERLIN = ZoneInfo("Europe/Berlin")

        year = int(year_raw)
        rows = load_list(data_path("cycles.json"))
        existing_cycles = load_cycles(rows)

        cycle_id = build_cycle_id(season, year)
        cycle_name = build_cycle_name(season, year)

        if has_cycle_id(rows, cycle_id):
            flash(f"Cycle already exists: {cycle_id}", "error")
            return redirect(url_for("admin.cycles_page"))

        new_cycle = Cycle(
            cycle_id=cycle_id,
            name=cycle_name,
            start_day=date.fromisoformat(start_day),
            end_day=date.fromisoformat(end_day),
            created_at=datetime.now(BERLIN),
            active=True,
        )

        if cycle_overlaps_existing(new_cycle, existing_cycles, BERLIN):
            flash("Cycle window overlaps an existing cycle.", "error")
            return redirect(url_for("admin.cycles_page"))

        row = {
            "cycle_id": new_cycle.cycle_id,
            "name": new_cycle.name,
            "start_day": new_cycle.start_day.isoformat(),
            "end_day": new_cycle.end_day.isoformat(),
            "created_at": new_cycle.created_at.isoformat(),
            "active": new_cycle.active,
        }
        append_row(data_path("cycles.json"), row)

        flash(f"Created cycle: {new_cycle.cycle_id}", "success")
        return redirect(url_for("admin.cycles_page"))

    cycles = get_cycles_for_list()
    return render_template(
        "admin/cycles.html",
        page_title="Cycles",
        cycles=cycles,
    )


@admin_bp.get("/admin/reports")
def reports_page():
    """Render the admin reports page."""
    cycle_choices = get_cycles_for_list()

    return render_template(
        "admin/reports.html",
        page_title="Reports",
        cycle_choices=cycle_choices,
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
