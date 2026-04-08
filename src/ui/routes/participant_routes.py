"""Participant-facing UI routes."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.ui.services.submit_ui_service import get_submit_page_context

participant_bp = Blueprint(
    "participant",
    __name__,
)

@participant_bp.route("/submit", methods=["GET", "POST"])
def submit_page():
    context = get_submit_page_context()

    if request.method == "POST":
        if not context["submit_enabled"] or context["active_cycle"] is None:
            flash("No active cycle is currently accepting submissions.", "error")
            return redirect(url_for(".submit_page"))

        participant_id = request.form.get("participant_id", "").strip()
        points_raw = request.form.get("points", "").strip()

        if not participant_id or not points_raw:
            flash("Participant and daily score are required.", "error")
            return redirect(url_for(".submit_page"))

        valid_participant_ids = {
            row["participant_id"] for row in context["participant_choices"]
        }
        if participant_id not in valid_participant_ids:
            flash("Selected participant is not eligible to submit for the active cycle.", "error")
            return redirect(url_for(".submit_page"))

        try:
            points = int(points_raw)
        except ValueError:
            flash("Daily score must be a valid number.", "error")
            return redirect(url_for(".submit_page"))

        if points < -3 or points > 5:
            flash("Daily score must be between -3 and 5.", "error")
            return redirect(url_for(".submit_page"))

        from datetime import datetime
        from zoneinfo import ZoneInfo

        from src.gymchallenge.data_paths import data_path
        from src.gymchallenge.id_ops import new_submission_id
        from src.gymchallenge.loaders import load_submissions
        from src.gymchallenge.scoring_time import score_day_for_timestamp
        from src.gymchallenge.storage_json import load_list
        from src.gymchallenge.storage_ops import append_row

        BERLIN = ZoneInfo("Europe/Berlin")
        now = datetime.now(BERLIN)

        active_cycle = context["active_cycle"]
        score_day = score_day_for_timestamp(now, BERLIN)

        if score_day is None:
            flash("Submissions are only accepted during the active scoring window.", "error")
            return redirect(url_for(".submit_page"))

        existing_rows = load_list(data_path("submissions.json"))
        existing_submissions = load_submissions(existing_rows)

        duplicate_exists = any(
            submission.cycle_id == active_cycle.cycle_id
            and submission.participant_id == participant_id
            and score_day_for_timestamp(submission.submitted_at, BERLIN) == score_day
            for submission in existing_submissions
        )

        if duplicate_exists:
            flash("A submission for this participant has already been recorded for the current score day.", "error")
            return redirect(url_for(".submit_page"))

        row = {
            "submission_id": new_submission_id(),
            "cycle_id": active_cycle.cycle_id,
            "participant_id": participant_id,
            "submitted_at": now.isoformat(),
            "points": points,
            "source": "ui",
        }

        append_row(data_path("submissions.json"), row)

        recorded_display = now.strftime("%Y-%m-%d %H:%M %Z")
        flash(
            f"Score submitted successfully. Recorded at: {recorded_display}",
            "success",
        )
        return redirect(url_for(".submit_page", success="1"))

    auto_reset_success = request.args.get("success") == "1"

    return render_template(
        "participant/submit.html",
        active_cycle=context["active_cycle"],
        participant_choices=context["participant_choices"],
        submit_enabled=context["submit_enabled"],
        submit_message=context["submit_message"],
        auto_reset_success=auto_reset_success,
    )
