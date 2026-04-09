"""Admin-facing UI routes."""

from flask import Blueprint, render_template, request, redirect, url_for, flash

from src.ui.services.participant_admin_service import get_participants_for_list, get_participant_choices, filter_participants_for_view, get_all_participant_choices_for_system
from src.ui.services.membership_ui_service import get_memberships_for_list, filter_memberships_for_view
from src.ui.services.cycle_ui_service import get_cycles_for_list, find_cycle_id_for_score_day
from src.ui.services.submission_ui_service import get_submissions_for_list, filter_and_sort_submissions_for_view
from src.ui.services.correction_ui_service import get_corrections_for_list
from src.ui.services.history_ui_service import get_history_for_list, filter_and_sort_history_for_view

from src.ui.config import get_ui_timezone, get_admin_actor_name

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

        ui_tz = get_ui_timezone()

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
            "created_at": datetime.now(ui_tz).isoformat(),
            "active": True,
            "archived": False,
        }

        append_row(path, row)

        flash(f"Added participant: {participant_id}", "success")
        return redirect(url_for("admin.participants_page"))

    search_value = request.args.get("search", "").strip()

    participants = get_participants_for_list()
    participants = filter_participants_for_view(participants, search_value)

    return render_template(
        "admin/participants.html",
        page_title="Participants",
        participants=participants,
        search_value=search_value,
        total=len(participants),
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

        from src.gymchallenge.data_paths import data_path
        from src.gymchallenge.storage_json import load_list
        from src.gymchallenge.storage_ops import append_row
        from src.gymchallenge.membership_store import find_membership_index

        ui_tz = get_ui_timezone()

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
            "joined_at": datetime.now(ui_tz).isoformat(),
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
    participant_id = request.args.get("participant_id", "").strip()
    points_value = request.args.get("points", "").strip()
    sort_value = request.args.get("sort", "newest").strip()

    submissions = get_submissions_for_list()
    submissions = filter_and_sort_submissions_for_view(
        submissions=submissions,
        participant_id=participant_id,
        points_value=points_value,
        sort_value=sort_value,
    )

    participant_choices = get_participant_choices()

    return render_template(
        "admin/submissions.html",
        page_title="Submissions",
        submissions=submissions,
        participant_choices=participant_choices,
        participant_id=participant_id,
        points_value=points_value,
        sort_value=sort_value,
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

        from src.gymchallenge.id_ops import new_correction_id
        from src.gymchallenge.storage_json import load_list
        from src.gymchallenge.storage_ops import append_row
        from src.gymchallenge.data_paths import data_path
        from src.gymchallenge.membership_store import find_membership_index

        ui_tz = get_ui_timezone()

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

        membership_rows = load_list(data_path("memberships.json"))
        membership_index = find_membership_index(
            membership_rows,
            cycle_id=cycle_id,
            participant_id=participant_id,
        )
        if membership_index is None:
            flash("Selected participant is not a member of the relevant cycle.", "error")
            return redirect(url_for("admin.corrections_page"))

        correction_id = new_correction_id()

        row = {
            "correction_id": correction_id,
            "cycle_id": cycle_id,
            "participant_id": participant_id,
            "score_day": score_day_date.isoformat(),
            "new_points": new_points,
            "reason": reason,
            "created_at": datetime.now(ui_tz).isoformat(),
            "admin": get_admin_actor_name(),
        }

        append_row(data_path("corrections.json"), row)

        flash(f"Correction added for participant.", "success")
        return redirect(url_for("admin.corrections_page"))

    corrections = get_corrections_for_list()

    score_day_value = request.args.get("score_day", "").strip()
    participant_choices = get_participant_choices()

    if score_day_value:
        from datetime import date

        from src.gymchallenge.data_paths import data_path
        from src.gymchallenge.storage_json import load_list

        try:
            score_day_date = date.fromisoformat(score_day_value)
        except ValueError:
            score_day_date = None

        if score_day_date is not None:
            cycle_id = find_cycle_id_for_score_day(score_day_date)
            if cycle_id is not None:
                membership_rows = load_list(data_path("memberships.json"))
                allowed_participant_ids = {
                    row["participant_id"]
                    for row in membership_rows
                    if row.get("cycle_id") == cycle_id
                }
                participant_choices = [
                    choice
                    for choice in participant_choices
                    if choice["participant_id"] in allowed_participant_ids
                ]

    return render_template(
        "admin/corrections.html",
        page_title="Corrections",
        corrections=corrections,
        participant_choices=participant_choices,
        total=len(corrections),
        score_day_value=score_day_value,
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

        from src.gymchallenge.cycle_ops import build_cycle_id, build_cycle_name, has_cycle_id
        from src.gymchallenge.cycle_timeline import cycle_overlaps_existing
        from src.gymchallenge.data_paths import data_path
        from src.gymchallenge.loaders import load_cycles
        from src.gymchallenge.storage_json import load_list
        from src.gymchallenge.storage_ops import append_row
        from src.gymchallenge.models import Cycle

        ui_tz = get_ui_timezone()

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
            created_at=datetime.now(ui_tz),
            active=True,
        )

        if cycle_overlaps_existing(new_cycle, existing_cycles, ui_tz):
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

@admin_bp.route("/admin/reports", methods=["GET", "POST"])
def reports_page():
    """Render and process the admin reports page."""
    cycle_choices = get_cycles_for_list()

    if request.method == "POST":
        cycle_id = request.form.get("cycle_id", "").strip()
        report_type = request.form.get("report_type", "").strip()
        include_inactive = request.form.get("include_inactive") == "1"

        if not cycle_id:
            flash("Cycle is required.", "error")
            return redirect(url_for("admin.reports_page"))

        if report_type != "leaderboard":
            flash("Unsupported report type.", "error")
            return redirect(url_for("admin.reports_page"))

        import csv
        from io import StringIO
        from datetime import datetime, timedelta
        from flask import Response

        from src.gymchallenge.data_paths import data_path
        from src.gymchallenge.storage_json import load_list
        from src.gymchallenge.loaders import (
            load_cycles,
            load_memberships,
            load_submissions,
            load_corrections,
            load_membership_events,
        )
        from src.gymchallenge.display_names import build_display_name_map
        from src.gymchallenge.scoring_engine import compute_daily_scores, build_leaderboard
        from src.gymchallenge.scoring_time import score_day_for_timestamp

        ui_tz = get_ui_timezone()

        cycle_rows = load_list(data_path("cycles.json"))
        membership_rows = load_list(data_path("memberships.json"))
        membership_event_rows = load_list(data_path("membership_events.json"))
        submission_rows = load_list(data_path("submissions.json"))
        correction_rows = load_list(data_path("corrections.json"))
        participant_rows = load_list(data_path("participants.json"))

        cycles = load_cycles(cycle_rows)
        memberships = load_memberships(membership_rows)
        membership_events = load_membership_events(membership_event_rows)
        submissions = load_submissions(submission_rows)
        corrections = load_corrections(correction_rows)

        selected_cycle = next((c for c in cycles if c.cycle_id == cycle_id), None)
        if selected_cycle is None:
            flash("Selected cycle was not found.", "error")
            return redirect(url_for("admin.reports_page"))

        display_name_map = build_display_name_map(participant_rows)
        archived_participant_ids = {
            row["participant_id"]
            for row in participant_rows
            if row.get("archived", False)
        }

        report_to_day = selected_cycle.end_day
        now = datetime.now(ui_tz)

        if selected_cycle.start_day <= now.date() <= selected_cycle.end_day:
            current_score_day = score_day_for_timestamp(now, ui_tz)
            if current_score_day is None:
                current_score_day = now.date() - timedelta(days=1)

            report_to_day = min(selected_cycle.end_day, current_score_day)

        cycle_memberships = [m for m in memberships if m.cycle_id == cycle_id]
        participant_ids = sorted(
            {
                m.participant_id
                for m in cycle_memberships
                if m.participant_id not in archived_participant_ids
            }
        )

        daily = compute_daily_scores(
            participant_ids=participant_ids,
            submissions=submissions,
            tz=ui_tz,
            cycle_start=selected_cycle.start_day,
            cycle_end=report_to_day,
            missing_points=-3,
            corrections=corrections,
        )

        leaderboard = build_leaderboard(
            memberships=cycle_memberships,
            membership_events=[e for e in membership_events if e.cycle_id == cycle_id],
            tz=ui_tz,
            daily=daily,
            from_day=selected_cycle.start_day,
            to_day=report_to_day,
            include_inactive=include_inactive,
        )

        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(["rank", "display_name", "total_points"])

        visible_leaderboard = [
            (participant_id, total_points)
            for participant_id, total_points in leaderboard
            if participant_id not in archived_participant_ids
        ]

        for rank, (participant_id, total_points) in enumerate(visible_leaderboard, start=1):
            writer.writerow(
                [
                    rank,
                    display_name_map.get(participant_id, participant_id),
                    total_points,
                ]
            )

        csv_data = output.getvalue()
        filename = f"leaderboard_{cycle_id}.csv"

        return Response(
            csv_data,
            mimetype="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            },
        )

    return render_template(
        "admin/reports.html",
        page_title="Reports",
        cycle_choices=cycle_choices,
    )

@admin_bp.route("/admin/system", methods=["GET", "POST"])
def system_page():
    """Render and process the admin system page."""
    from datetime import datetime
    from src.gymchallenge.data_paths import data_path
    from src.gymchallenge.storage_json import load_list, save_list
    from src.gymchallenge.id_ops import new_system_event_id
    from src.gymchallenge.storage_ops import append_row
    from src.gymchallenge.participant_store import (
        archive_participant_row,
        restore_participant_row,
    )

    action = request.form.get("action", "").strip()

    if action == "reset_dataset":
        reset_confirmation = request.form.get("reset_confirmation", "").strip()

        if reset_confirmation != "RESET":
            flash("Dataset reset cancelled. Type RESET exactly to confirm.", "error")
            return redirect(url_for("admin.system_page"))

        from datetime import datetime
        from src.gymchallenge.id_ops import new_system_event_id
        from src.gymchallenge.storage_json import save_list

        timestamp = datetime.now().astimezone().isoformat()

        save_list(data_path("participants.json"), [])
        save_list(data_path("memberships.json"), [])
        save_list(data_path("membership_events.json"), [])
        save_list(data_path("submissions.json"), [])
        save_list(data_path("corrections.json"), [])
        save_list(data_path("cycles.json"), [])

        save_list(
            data_path("system_events.json"),
            [
                {
                    "event_id": new_system_event_id(),
                    "event_type": "dataset_reset",
                    "participant_id": None,
                    "reason": "system reset via admin UI",
                    "created_at": timestamp,
                    "actor": get_admin_actor_name(),
                }
            ],
        )

        flash("Dataset reset successfully.", "success")
        return redirect(url_for("admin.system_page"))

    if request.method == "POST":
        participant_id = request.form.get("participant_id", "").strip()
        action = request.form.get("action", "").strip()
        confirm_archive = request.form.get("confirm_archive", "").strip()

        if not participant_id:
            flash("Participant selection is required.", "error")
            return redirect(url_for("admin.system_page"))

        participant_rows = load_list(data_path("participants.json"))

        if action == "archive":
            if confirm_archive != "yes":
                flash("Archive cancelled. Confirmation was not accepted.", "error")
                return redirect(url_for("admin.system_page"))

            changed = archive_participant_row(participant_rows, participant_id)
            if not changed:
                flash("Participant was not found.", "error")
                return redirect(url_for("admin.system_page"))

            save_list(data_path("participants.json"), participant_rows)

            append_row(
                data_path("system_events.json"),
                {
                    "event_id": new_system_event_id(),
                    "event_type": "participant_archived",
                    "participant_id": participant_id,
                    "reason": "archived via system page",
                    "created_at": datetime.now().astimezone().isoformat(),
                    "actor": get_admin_actor_name(),
                },
            )

            flash("Participant archived successfully.", "success")
            return redirect(url_for("admin.system_page"))

        if action == "restore":
            changed = restore_participant_row(participant_rows, participant_id)
            if not changed:
                flash("Participant was not found.", "error")
                return redirect(url_for("admin.system_page"))

            save_list(data_path("participants.json"), participant_rows)

            append_row(
                data_path("system_events.json"),
                {
                    "event_id": new_system_event_id(),
                    "event_type": "participant_restored",
                    "participant_id": participant_id,
                    "reason": "restored via system page",
                    "created_at": datetime.now().astimezone().isoformat(),
                    "actor": get_admin_actor_name(),
                },
            )

            flash("Participant restored successfully.", "success")
            return redirect(url_for("admin.system_page"))

        flash("Unsupported system action.", "error")
        return redirect(url_for("admin.system_page"))

    participant_choices = get_all_participant_choices_for_system()

    return render_template(
        "admin/system.html",
        page_title="System",
        participant_choices=participant_choices,
    )


@admin_bp.get("/admin/history")
def history_page():
    """Render the admin history page."""
    entry_type = request.args.get("entry_type", "all").strip()
    participant_id = request.args.get("participant_id", "").strip()
    sort_value = request.args.get("sort", "newest").strip()

    history_entries = get_history_for_list()
    history_entries = filter_and_sort_history_for_view(
        history_entries=history_entries,
        entry_type=entry_type,
        participant_id=participant_id,
        sort_value=sort_value,
    )

    participant_choices = get_participant_choices()

    return render_template(
        "admin/history.html",
        page_title="History",
        history_entries=history_entries,
        participant_choices=participant_choices,
        entry_type=entry_type,
        participant_id=participant_id,
        sort_value=sort_value,
        total=len(history_entries),
    )
