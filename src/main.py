from __future__ import annotations

import argparse
import csv

from datetime import date, datetime
from typing import Any
from src.gymchallenge.runtime_config import get_runtime_timezone, get_runtime_admin_name

from src.gymchallenge.models import Submission, Correction, Membership, MembershipEvent, Cycle
from src.gymchallenge.scoring_engine import compute_daily_scores, build_leaderboard, detect_auto_inactive, apply_auto_inactive, reactivate_member
from src.gymchallenge.storage_json import load_list, save_list
from src.gymchallenge.data_paths import data_path, exports_path
from src.gymchallenge.participant_ops import generate_participant_id
from src.gymchallenge.storage_ops import append_row
from src.gymchallenge.membership_ops import has_membership
from src.gymchallenge.id_ops import new_submission_id, new_correction_id
from src.gymchallenge.membership_store import find_membership_index
from src.gymchallenge.membership_event_ops import append_membership_event
from src.gymchallenge.system_event_ops import append_missing_auto_inactive_events, append_missing_auto_reactivate_events
from src.gymchallenge.reactivation_ops import detect_auto_reactivate
from src.gymchallenge.cycle_ops import build_cycle_id, build_cycle_name, has_active_cycle, has_cycle_id
from src.gymchallenge.cycle_timeline import cycle_status, cycle_overlaps_existing, cycle_window_start, cycle_window_end
from src.gymchallenge.cycle_store import find_cycle_row
from src.gymchallenge.display_names import build_display_name_map
from src.gymchallenge.demo_data_generator import generate_demo_participants, generate_demo_memberships, generate_demo_submissions
from src.gymchallenge.loaders import load_memberships, load_cycles, load_submissions, load_corrections, load_membership_events

RUNTIME_TZ = get_runtime_timezone()
RUNTIME_ADMIN_NAME = get_runtime_admin_name()

def parse_date(s: str) -> date:
    return date.fromisoformat(s)


def cmd_report(args: argparse.Namespace) -> int:
    from_day = parse_date(args.from_day)
    to_day = parse_date(args.to_day)
    include_inactive = args.include_inactive

    memberships = load_memberships(load_list(data_path("memberships.json")))
    membership_events = load_membership_events(load_list(data_path("membership_events.json")))
    submissions = load_submissions(load_list(data_path("submissions.json")))
    corrections = load_corrections(load_list(data_path("corrections.json")))
    participant_rows = load_list(data_path("participants.json"))
    display_name_map = build_display_name_map(participant_rows)

    participant_ids = sorted({m.participant_id for m in memberships})

    cycle_start = from_day
    cycle_end = to_day

    daily = compute_daily_scores(
        participant_ids=participant_ids,
        submissions=submissions,
        tz=RUNTIME_TZ,
        cycle_start=cycle_start,
        cycle_end=cycle_end,
        missing_points=-3,
        corrections=corrections,
    )

    leaderboard = build_leaderboard(
        memberships=memberships,
        membership_events=membership_events,
        tz=RUNTIME_TZ,
        daily=daily,
        from_day=from_day,
        to_day=to_day,
        include_inactive=include_inactive,
    )

    print(f"\nLeaderboard {from_day.isoformat()}..{to_day.isoformat()} (include_inactive={include_inactive})")

    for rank, (pid, total) in enumerate(leaderboard, start=1):
        display_name = display_name_map.get(pid, pid)
        print(f"{rank:>2}. {display_name}: {total}")

    out_name = f"leaderboard_{from_day.isoformat()}_{to_day.isoformat()}.csv"
    out_path = exports_path(out_name)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "participant_id", "display_name", "total_points"])

        for rank, (pid, total) in enumerate(leaderboard, start=1):
            display_name = display_name_map.get(pid, pid)
            writer.writerow([rank, pid, display_name, total])

    print(f"\nCSV export written to: {out_path}")
    return 0

def cmd_participant_add(args: argparse.Namespace) -> int:
    first = args.first.strip()
    last = args.last.strip()

    if not first or not last:
        raise ValueError("first and last are required")

    path = data_path("participants.json")
    existing = load_list(path)

    participant_id = generate_participant_id(first=first, last=last, existing_rows=existing)

    row = {
        "participant_id": participant_id,
        "first_name": first,
        "last_name": last,
        "created_at": datetime.now(RUNTIME_TZ).isoformat(),
        "active": True,
    }

    append_row(path, row)

    print(f"Added participant: {participant_id} ({last}, {first})")
    return 0

def cmd_membership_add(args: argparse.Namespace) -> int:
    cycle_id = args.cycle_id.strip()
    participant_id = args.participant_id.strip()

    if not cycle_id or not participant_id:
        raise ValueError("cycle-id and participant-id are required")

    path = data_path("memberships.json")
    existing = load_list(path)

    if has_membership(existing, cycle_id=cycle_id, participant_id=participant_id):
        print(f"Membership already exists: cycle={cycle_id} participant={participant_id}")
        return 0

    row = {
        "cycle_id": cycle_id,
        "participant_id": participant_id,
        "active_in_cycle": True,
        "joined_at": datetime.now(RUNTIME_TZ).isoformat(),
        "left_at": None,
        "inactive_reason": None,
        "inactive_effective_score_day": None,
    }

    append_row(path, row)
    print(f"Added membership: cycle={cycle_id} participant={participant_id}")
    return 0

def cmd_submission_add(args: argparse.Namespace) -> int:
    cycle_id = args.cycle_id.strip()
    participant_id = args.participant_id.strip()
    points = int(args.points)

    if points < -3 or points > 5:
        raise ValueError("points must be between -3 and 5")

    if args.submitted_at:
        submitted_at = datetime.fromisoformat(args.submitted_at)
    else:
        submitted_at = datetime.now(RUNTIME_TZ)

    row = {
        "submission_id": new_submission_id(),
        "cycle_id": cycle_id,
        "participant_id": participant_id,
        "submitted_at": submitted_at.isoformat(),
        "points": points,
        "source": "manual",
    }

    append_row(data_path("submissions.json"), row)

    print(f"Added submission: {row['submission_id']} participant={participant_id} points={points} at={row['submitted_at']}")
    return 0

def cmd_correction_add(args: argparse.Namespace) -> int:
    cycle_id = args.cycle_id.strip()
    participant_id = args.participant_id.strip()
    score_day = date.fromisoformat(args.score_day)
    points = int(args.points)
    reason = args.reason.strip()

    if points < -3 or points > 5:
        raise ValueError("points must be between -3 and 5")

    if not reason:
        raise ValueError("reason is required")

    row = {
        "correction_id": new_correction_id(),
        "cycle_id": cycle_id,
        "participant_id": participant_id,
        "score_day": score_day.isoformat(),
        "new_points": points,
        "reason": reason,
        "created_at": datetime.now(RUNTIME_TZ).isoformat(),
        "admin": RUNTIME_ADMIN_NAME,
    }

    append_row(data_path("corrections.json"), row)
    print(f"Added correction: {row['correction_id']} participant={participant_id} day={row['score_day']} points={points}")
    return 0

def cmd_membership_reactivate(args: argparse.Namespace) -> int:
    cycle_id = args.cycle_id.strip()
    participant_id = args.participant_id.strip()
    reason = args.reason.strip()
    effective_day = date.fromisoformat(args.effective_day)

    if not reason:
        raise ValueError("reason is required")

    path = data_path("memberships.json")
    rows = load_list(path)

    idx = find_membership_index(rows, cycle_id=cycle_id, participant_id=participant_id)
    if idx is None:
        raise ValueError(f"Membership not found: cycle={cycle_id} participant={participant_id}")

    # Update in place (MVP):
    rows[idx]["active_in_cycle"] = True
    rows[idx]["inactive_effective_score_day"] = None
    # keep inactive_reason as historical metadata
    # NOTE: effective_day is accepted but not stored yet (future scheduling)

    save_list(path, rows)

    append_membership_event(
        path=data_path("membership_events.json"),
        cycle_id=cycle_id,
        participant_id=participant_id,
        event_type="manual_reactivate",
        effective_score_day=effective_day,
        reason=reason,
        created_at=datetime.now(RUNTIME_TZ),
        actor=RUNTIME_ADMIN_NAME,
    )

    print(f"Reactivated membership: cycle={cycle_id} participant={participant_id} effective_day={effective_day.isoformat()}")
    return 0

def cmd_membership_deactivate(args: argparse.Namespace) -> int:
    cycle_id = args.cycle_id.strip()
    participant_id = args.participant_id.strip()
    reason = args.reason.strip()
    effective_day = date.fromisoformat(args.effective_day)

    if not reason:
        raise ValueError("reason is required")

    path = data_path("memberships.json")
    rows = load_list(path)

    idx = find_membership_index(rows, cycle_id=cycle_id, participant_id=participant_id)
    if idx is None:
        raise ValueError(f"Membership not found: cycle={cycle_id} participant={participant_id}")

    rows[idx]["active_in_cycle"] = False
    rows[idx]["inactive_reason"] = "manual"
    rows[idx]["inactive_effective_score_day"] = effective_day.isoformat()

    save_list(path, rows)

    append_membership_event(
        path=data_path("membership_events.json"),
        cycle_id=cycle_id,
        participant_id=participant_id,
        event_type="manual_inactive",
        effective_score_day=effective_day,
        reason=reason,
        created_at=datetime.now(RUNTIME_TZ),
        actor=RUNTIME_ADMIN_NAME,
    )

    print(f"Deactivated membership: cycle={cycle_id} participant={participant_id} effective_day={effective_day.isoformat()}")
    return 0

def cmd_system_apply_auto_inactive(args: argparse.Namespace) -> int:
    cycle_id = args.cycle_id.strip()
    from_day = date.fromisoformat(args.from_day)
    to_day = date.fromisoformat(args.to_day)

    as_of = datetime.now(RUNTIME_TZ)

    memberships_path = data_path("memberships.json")
    events_path = data_path("membership_events.json")

    membership_rows = load_list(memberships_path)
    submissions = load_submissions(load_list(data_path("submissions.json")))
    corrections = load_corrections(load_list(data_path("corrections.json")))
    existing_event_rows = load_list(events_path)

    memberships = load_memberships(membership_rows)

    # Only operate on memberships for the requested cycle
    cycle_memberships = [m for m in memberships if m.cycle_id == cycle_id]
    participant_ids = sorted({m.participant_id for m in cycle_memberships})

    daily = compute_daily_scores(
        participant_ids=participant_ids,
        submissions=submissions,
        tz=RUNTIME_TZ,
        cycle_start=from_day,
        cycle_end=to_day,
        missing_points=-3,
        corrections=corrections,
    )

    updates = detect_auto_inactive(
        daily=daily,
        cycle_start=from_day,
        cycle_end=to_day,
        as_of=as_of,
        tz=RUNTIME_TZ,
        streak_required=4,
    )

    if not updates:
        print(f"No auto-inactive updates for cycle={cycle_id}")
        return 0

    updated_cycle_memberships = apply_auto_inactive(cycle_memberships, updates)

    # Merge updated cycle memberships back into the full membership list
    updated_by_key = {(m.cycle_id, m.participant_id): m for m in updated_cycle_memberships}

    new_membership_rows = []
    for row in membership_rows:
        key = (row["cycle_id"], row["participant_id"])
        if key in updated_by_key:
            m = updated_by_key[key]
            new_membership_rows.append(
                {
                    "cycle_id": m.cycle_id,
                    "participant_id": m.participant_id,
                    "active_in_cycle": m.active_in_cycle,
                    "joined_at": m.joined_at.isoformat(),
                    "left_at": m.left_at.isoformat() if m.left_at else None,
                    "inactive_reason": m.inactive_reason,
                    "inactive_effective_score_day": (
                        m.inactive_effective_score_day.isoformat()
                        if m.inactive_effective_score_day
                        else None
                    ),
                }
            )
        else:
            new_membership_rows.append(row)

    save_list(memberships_path, new_membership_rows)

    written = append_missing_auto_inactive_events(
        path=events_path,
        existing_rows=existing_event_rows,
        cycle_id=cycle_id,
        updates=updates,
        created_at=datetime.now(RUNTIME_TZ),
    )

    print(
        f"Applied auto-inactive for cycle={cycle_id}: "
        f"{len(updates)} membership update(s), {len(written)} new event(s)"
    )
    return 0

def cmd_system_apply_auto_reactivate(args: argparse.Namespace) -> int:
    cycle_id = args.cycle_id.strip()
    from_day = date.fromisoformat(args.from_day)
    to_day = date.fromisoformat(args.to_day)

    memberships_path = data_path("memberships.json")
    events_path = data_path("membership_events.json")

    membership_rows = load_list(memberships_path)
    submissions = load_submissions(load_list(data_path("submissions.json")))
    corrections = load_corrections(load_list(data_path("corrections.json")))
    existing_event_rows = load_list(events_path)

    memberships = load_memberships(membership_rows)

    # Only operate on memberships for the requested cycle
    cycle_memberships = [m for m in memberships if m.cycle_id == cycle_id]
    participant_ids = sorted({m.participant_id for m in cycle_memberships})

    daily = compute_daily_scores(
        participant_ids=participant_ids,
        submissions=submissions,
        tz=RUNTIME_TZ,
        cycle_start=from_day,
        cycle_end=to_day,
        missing_points=-3,
        corrections=corrections,
    )

    updates = detect_auto_reactivate(
        memberships=cycle_memberships,
        daily=daily,
        from_day=from_day,
        to_day=to_day,
    )

    if not updates:
        print(f"No auto-reactivation updates for cycle={cycle_id}")
        return 0

    # Apply reactivation to the matching memberships
    updated_cycle_memberships = cycle_memberships
    for participant_id, effective_day in updates.items():
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
            new_membership_rows.append(
                {
                    "cycle_id": m.cycle_id,
                    "participant_id": m.participant_id,
                    "active_in_cycle": m.active_in_cycle,
                    "joined_at": m.joined_at.isoformat(),
                    "left_at": m.left_at.isoformat() if m.left_at else None,
                    "inactive_reason": m.inactive_reason,
                    "inactive_effective_score_day": (
                        m.inactive_effective_score_day.isoformat()
                        if m.inactive_effective_score_day
                        else None
                    ),
                }
            )
        else:
            new_membership_rows.append(row)

    save_list(memberships_path, new_membership_rows)

    written = append_missing_auto_reactivate_events(
        path=events_path,
        existing_rows=existing_event_rows,
        cycle_id=cycle_id,
        updates=updates,
        created_at=datetime.now(RUNTIME_TZ),
    )

    print(
        f"Applied auto-reactivation for cycle={cycle_id}: "
        f"{len(updates)} membership update(s), {len(written)} new event(s)"
    )
    return 0

def cmd_cycle_create(args: argparse.Namespace) -> int:
    season = args.season.strip()
    year = int(args.year)
    start_day = date.fromisoformat(args.start_day)
    end_day = date.fromisoformat(args.end_day)

    if end_day < start_day:
        raise ValueError("end must be on or after start")

    path = data_path("cycles.json")
    rows = load_list(path)

    cycle_id = build_cycle_id(season, year)
    name = build_cycle_name(season, year)

    new_cycle = Cycle(
        cycle_id=cycle_id,
        name=name,
        start_day=start_day,
        end_day=end_day,
        created_at=datetime.now(RUNTIME_TZ),
        active=True,  # legacy field retained for now
    )

    existing_cycles = load_cycles(rows)

    if cycle_overlaps_existing(new_cycle, existing_cycles, RUNTIME_TZ):
        raise ValueError("new cycle overlaps an existing cycle active window")

    if has_cycle_id(rows, cycle_id):
        raise ValueError(f"cycle already exists: {cycle_id}")

    row = {
        "cycle_id": cycle_id,
        "name": name,
        "start_day": start_day.isoformat(),
        "end_day": end_day.isoformat(),
        "created_at": datetime.now(RUNTIME_TZ).isoformat(),
        "active": True,
    }

    append_row(path, row)
    print(f"Created cycle: {cycle_id} ({name}) {start_day.isoformat()}..{end_day.isoformat()}")
    return 0

def cmd_cycle_list(args: argparse.Namespace) -> int:
    rows = load_list(data_path("cycles.json"))

    if not rows:
        print("No cycles found.")
        return 0

    cycles = load_cycles(rows)
    now = datetime.now(RUNTIME_TZ)

    print("Cycles:")
    for cycle in cycles:
        status = cycle_status(cycle, now, RUNTIME_TZ)
        print(
            f"- {cycle.cycle_id} | {cycle.name} | "
            f"{cycle.start_day.isoformat()}..{cycle.end_day.isoformat()} | {status}"
        )

    return 0

def cmd_cycle_show(args: argparse.Namespace) -> int:
    cycle_id = args.cycle_id.strip()

    cycle_rows = load_list(data_path("cycles.json"))
    row = find_cycle_row(cycle_rows, cycle_id)

    if row is None:
        raise ValueError(f"cycle not found: {cycle_id}")

    cycle = load_cycles([row])[0]
    now = datetime.now(RUNTIME_TZ)
    status = cycle_status(cycle, now, RUNTIME_TZ)
    window_start = cycle_window_start(cycle, RUNTIME_TZ)
    window_end = cycle_window_end(cycle, RUNTIME_TZ)

    memberships_rows = load_list(data_path("memberships.json"))
    submissions_rows = load_list(data_path("submissions.json"))
    corrections_rows = load_list(data_path("corrections.json"))
    membership_event_rows = load_list(data_path("membership_events.json"))

    membership_count = sum(1 for r in memberships_rows if r.get("cycle_id") == cycle_id)
    submission_count = sum(1 for r in submissions_rows if r.get("cycle_id") == cycle_id)
    correction_count = sum(1 for r in corrections_rows if r.get("cycle_id") == cycle_id)
    membership_event_count = sum(1 for r in membership_event_rows if r.get("cycle_id") == cycle_id)

    print(f"Cycle: {cycle.cycle_id}")
    print(f"Name: {cycle.name}")
    print(f"Start Day: {cycle.start_day.isoformat()}")
    print(f"End Day: {cycle.end_day.isoformat()}")
    print(f"Status: {status}")
    print()
    print("Active Window:")
    print(f"  Opens:  {window_start.isoformat()}")
    print(f"  Closes: {window_end.isoformat()}")
    print()
    print("Counts:")
    print(f"  Memberships: {membership_count}")
    print(f"  Submissions: {submission_count}")
    print(f"  Corrections: {correction_count}")
    print(f"  Membership Events: {membership_event_count}")

    return 0

def cmd_system_generate_demo_data(args: argparse.Namespace) -> int:
    cycle_id = args.cycle_id
    participant_count = args.participants
    seed = args.seed
    miss_rate = args.miss_rate

    from_day = date.fromisoformat(args.from_day)
    to_day = date.fromisoformat(args.to_day)

    tz = RUNTIME_TZ

    print("Generating demo dataset...")
    print(f"Participants: {participant_count}")
    print(f"Cycle: {cycle_id}")
    print(f"Range: {from_day} .. {to_day}")
    print(f"Seed: {seed}")

    participants = generate_demo_participants(
        count=participant_count,
        seed=seed,
    )

    memberships = generate_demo_memberships(
        cycle_id=cycle_id,
        participant_rows=participants,
    )

    submissions = generate_demo_submissions(
        cycle_id=cycle_id,
        participant_rows=participants,
        from_day=from_day,
        to_day=to_day,
        seed=seed,
        miss_rate=miss_rate,
        tz=tz,
    )

    # Reset demo-owned data files so each run starts clean
    save_list(data_path("participants.json"), [])
    save_list(data_path("memberships.json"), [])
    save_list(data_path("submissions.json"), [])
    save_list(data_path("corrections.json"), [])
    save_list(data_path("membership_events.json"), [])

    save_list(data_path("participants.json"), participants)
    save_list(data_path("memberships.json"), memberships)
    save_list(data_path("submissions.json"), submissions)

    print("Demo dataset written.")
    print(f"participants: {len(participants)}")
    print(f"memberships: {len(memberships)}")
    print(f"submissions: {len(submissions)}")
    print("corrections: 0")
    print("membership_events: 0")

    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gym-challenge")

    sub = parser.add_subparsers(dest="cmd", required=True)

    # system commands
    p_system = sub.add_parser("system", help="System maintenance commands")
    system_sub = p_system.add_subparsers(dest="system_cmd", required=True)

    s_auto = system_sub.add_parser("apply-auto-inactive", help="Detect and apply auto-inactive updates")
    s_auto.add_argument("--cycle-id", required=True)
    s_auto.add_argument("--from", dest="from_day", required=True, help="YYYY-MM-DD")
    s_auto.add_argument("--to", dest="to_day", required=True, help="YYYY-MM-DD")
    s_auto.set_defaults(func=cmd_system_apply_auto_inactive)

    s_reactivate = system_sub.add_parser("apply-auto-reactivate", help="Detect and apply auto-reactivation updates")
    s_reactivate.add_argument("--cycle-id", required=True)
    s_reactivate.add_argument("--from", dest="from_day", required=True, help="YYYY-MM-DD")
    s_reactivate.add_argument("--to", dest="to_day", required=True, help="YYYY-MM-DD")
    s_reactivate.set_defaults(func=cmd_system_apply_auto_reactivate)

    s_demo = system_sub.add_parser(
        "generate-demo-data",
        help="Generate deterministic demo dataset",
    )

    s_demo.add_argument("--cycle-id", required=True)
    s_demo.add_argument("--participants", type=int, default=30)
    s_demo.add_argument("--from-day", required=True)
    s_demo.add_argument("--to-day", required=True)
    s_demo.add_argument("--seed", type=int, default=42)
    s_demo.add_argument("--miss-rate", type=float, default=0.2)

    s_demo.set_defaults(func=cmd_system_generate_demo_data)

    # cycle commands
    p_cycle = sub.add_parser("cycle", help="Manage challenge cycles")
    cycle_sub = p_cycle.add_subparsers(dest="cycle_cmd", required=True)

    c_create = cycle_sub.add_parser("create", help="Create a new cycle")
    c_create.add_argument("--season", required=True, help="spring|summer|fall|winter")
    c_create.add_argument("--year", required=True, help="YYYY")
    c_create.add_argument("--start", dest="start_day", required=True, help="YYYY-MM-DD")
    c_create.add_argument("--end", dest="end_day", required=True, help="YYYY-MM-DD")
    c_create.set_defaults(func=cmd_cycle_create)

    c_list = cycle_sub.add_parser("list", help="List cycles")
    c_list.set_defaults(func=cmd_cycle_list)

    c_show = cycle_sub.add_parser("show", help="Show detailed information for a cycle")
    c_show.add_argument("--cycle-id", required=True)
    c_show.set_defaults(func=cmd_cycle_show)

    # participant commands
    p_participant = sub.add_parser("participant", help="Manage participants")
    participant_sub = p_participant.add_subparsers(dest="participant_cmd", required=True)

    p_add = participant_sub.add_parser("add", help="Add a participant")
    p_add.add_argument("--first", required=True)
    p_add.add_argument("--last", required=True)
    p_add.set_defaults(func=cmd_participant_add)

    report = sub.add_parser("report", help="Generate leaderboard report")
    report.add_argument("--from", dest="from_day", required=True)
    report.add_argument("--to", dest="to_day", required=True)
    report.add_argument("--include-inactive", action="store_true")

    report.set_defaults(func=cmd_report)

    # membership commands
    p_membership = sub.add_parser("membership", help="Manage cycle memberships")
    membership_sub = p_membership.add_subparsers(dest="membership_cmd", required=True)

    m_add = membership_sub.add_parser("add", help="Add a participant to a cycle")
    m_add.add_argument("--cycle-id", required=True)
    m_add.add_argument("--participant-id", required=True)
    m_add.set_defaults(func=cmd_membership_add)

    m_reactivate = membership_sub.add_parser("reactivate", help="Reactivate a membership (reason required)")
    m_reactivate.add_argument("--cycle-id", required=True)
    m_reactivate.add_argument("--participant-id", required=True)
    m_reactivate.add_argument("--effective-day", required=True, help="YYYY-MM-DD")
    m_reactivate.add_argument("--reason", required=True)
    m_reactivate.set_defaults(func=cmd_membership_reactivate)

    m_deactivate = membership_sub.add_parser("deactivate", help="Deactivate a membership (reason required)")
    m_deactivate.add_argument("--cycle-id", required=True)
    m_deactivate.add_argument("--participant-id", required=True)
    m_deactivate.add_argument("--effective-day", required=True, help="YYYY-MM-DD")
    m_deactivate.add_argument("--reason", required=True)
    m_deactivate.set_defaults(func=cmd_membership_deactivate)

    # submission commands
    p_submission = sub.add_parser("submission", help="Manage submissions")
    submission_sub = p_submission.add_subparsers(dest="submission_cmd", required=True)

    s_add = submission_sub.add_parser("add", help="Add a submission")
    s_add.add_argument("--cycle-id", required=True)
    s_add.add_argument("--participant-id", required=True)
    s_add.add_argument("--points", required=True)
    s_add.add_argument("--submitted-at", required=False, help="ISO8601 timestamp; default now")
    s_add.set_defaults(func=cmd_submission_add)

    # correction commands
    p_correction = sub.add_parser("correction", help="Manage admin corrections")
    correction_sub = p_correction.add_subparsers(dest="correction_cmd", required=True)

    c_add = correction_sub.add_parser("add", help="Add a correction (reason required)")
    c_add.add_argument("--cycle-id", required=True)
    c_add.add_argument("--participant-id", required=True)
    c_add.add_argument("--score-day", required=True, help="YYYY-MM-DD")
    c_add.add_argument("--points", required=True)
    c_add.add_argument("--reason", required=True)
    c_add.set_defaults(func=cmd_correction_add)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"Error: {exc}")
        raise SystemExit(2)
