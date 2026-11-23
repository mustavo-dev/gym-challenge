"""Participant-facing UI routes."""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from src.ui.services.submit_ui_service import get_submit_page_context
from src.ui.config import get_ui_timezone
from src.gymchallenge.scoring_engine import compute_daily_scores, detect_auto_inactive, apply_auto_inactive, reactivate_member
from src.gymchallenge.reactivation_ops import detect_auto_reactivate
from src.gymchallenge.system_event_ops import append_missing_auto_inactive_events, append_missing_auto_reactivate_events
from src.gymchallenge.storage_json import load_list, save_list
from src.gymchallenge.loaders import load_memberships, load_submissions, load_corrections

def _run_auto_inactive_and_reactivate(active_cycle, ui_tz) -> None:
    """
    After a submission is saved, check and apply auto-inactive and
    auto-reactivate state changes for the active cycle.
    Corrections are intentionally excluded — only valid participant
    submissions affect inactivity and reactivation status.
    """
    from datetime import datetime
    from src.gymchallenge.data_paths import data_path

    cycle_id = active_cycle.cycle_id
    from_day = active_cycle.start_day
    to_day = active_cycle.end_day

    as_of = datetime.now(ui_tz)

    memberships_path = data_path("memberships.json")
    events_path = data_path("membership_events.json")

    membership_rows = load_list(memberships_path)
    submissions = load_submissions(load_list(data_path("submissions.json")))
    corrections = load_corrections(load_list(data_path("corrections.json")))
    existing_event_rows = load_list(events_path)

    memberships = load_memberships(membership_rows)
    cycle_memberships = [m for m in memberships if m.cycle_id == cycle_id]
    participant_ids = sorted({m.participant_id for m in cycle_memberships})

    daily = compute_daily_scores(
        participant_ids=participant_ids,
        submissions=submissions,
        tz=ui_tz,
        cycle_start=from_day,
        cycle_end=to_day,
        missing_points=-3,
        corrections=corrections,
    )

    # --- Auto-inactive pass ---
    inactive_updates = detect_auto_inactive(
        daily=daily,
        cycle_start=from_day,
        cycle_end=to_day,
        as_of=as_of,
        tz=ui_tz,
        streak_required=4,
    )

    if inactive_updates:
        updated_cycle_memberships = apply_auto_inactive(cycle_memberships, inactive_updates)
        updated_by_key = {(m.cycle_id, m.participant_id): m for m in updated_cycle_memberships}
        new_membership_rows = []
        for row in membership_rows:
            key = (row["cycle_id"], row["participant_id"])
            if key in updated_by_key:
                m = updated_by_key[key]
                new_membership_rows.append({
                    "cycle_id": m.cycle_id,
                    "participant_id": m.participant_id,
                    "active_in_cycle": m.active_in_cycle,
                    "joined_at": m.joined_at.isoformat(),
                    "left_at": m.left_at.isoformat() if m.left_at else None,
                    "inactive_reason": m.inactive_reason,
                    "inactive_effective_score_day": (
                        m.inactive_effective_score_day.isoformat()
                        if m.inactive_effective_score_day else None
                    ),
                })
            else:
                new_membership_rows.append(row)
        save_list(memberships_path, new_membership_rows)
        append_missing_auto_inactive_events(
            path=events_path,
            existing_rows=existing_event_rows,
            cycle_id=cycle_id,
            updates=inactive_updates,
            created_at=datetime.now(ui_tz),
        )

        # Reload after writing so reactivation sees the updated membership state
        membership_rows = load_list(memberships_path)
        memberships = load_memberships(membership_rows)
        cycle_memberships = [m for m in memberships if m.cycle_id == cycle_id]
        existing_event_rows = load_list(events_path)

    # --- Auto-reactivate pass ---
    reactivate_updates = detect_auto_reactivate(
        memberships=cycle_memberships,
        daily=daily,
        from_day=from_day,
        to_day=to_day,
    )

    if reactivate_updates:
        updated_cycle_memberships = cycle_memberships
        for participant_id, effective_day in reactivate_updates.items():
            updated_cycle_memberships = reactivate_member(
                memberships=updated_cycle_memberships,
                participant_id=participant_id,
                effective_day=effective_day,
                reason="Auto-reactivated by valid submission",
            )
        updated_by_key = {(m.cycle_id, m.participant_id): m for m in updated_cycle_memberships}
        new_membership_rows = []
        for row in membership_rows:
            key = (row["cycle_id"], row["participant_id"])
            if key in updated_by_key:
                m = updated_by_key[key]
                new_membership_rows.append({
                    "cycle_id": m.cycle_id,
                    "participant_id": m.participant_id,
                    "active_in_cycle": m.active_in_cycle,
                    "joined_at": m.joined_at.isoformat(),
                    "left_at": m.left_at.isoformat() if m.left_at else None,
                    "inactive_reason": m.inactive_reason,
                    "inactive_effective_score_day": (
                        m.inactive_effective_score_day.isoformat()
                        if m.inactive_effective_score_day else None
                    ),
                })
            else:
                new_membership_rows.append(row)
        save_list(memberships_path, new_membership_rows)
        append_missing_auto_reactivate_events(
            path=events_path,
            existing_rows=existing_event_rows,
            cycle_id=cycle_id,
            updates=reactivate_updates,
            created_at=datetime.now(ui_tz),
        )

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

        from src.gymchallenge.data_paths import data_path
        from src.gymchallenge.id_ops import new_submission_id
        from src.gymchallenge.loaders import load_submissions
        from src.gymchallenge.scoring_time import score_day_for_timestamp
        from src.gymchallenge.storage_json import load_list
        from src.gymchallenge.storage_ops import append_row

        ui_tz = get_ui_timezone()
        now = datetime.now(ui_tz)

        active_cycle = context["active_cycle"]
        score_day = score_day_for_timestamp(now, ui_tz)

        if score_day is None:
            flash("Submissions are only accepted during the active scoring window.", "error")
            return redirect(url_for(".submit_page"))

        existing_rows = load_list(data_path("submissions.json"))
        existing_submissions = load_submissions(existing_rows)

        duplicate_exists = any(
            submission.cycle_id == active_cycle.cycle_id
            and submission.participant_id == participant_id
            and score_day_for_timestamp(submission.submitted_at, ui_tz) == score_day
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

        _run_auto_inactive_and_reactivate(active_cycle, ui_tz)


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
