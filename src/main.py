from __future__ import annotations

import argparse
import csv
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from gymchallenge.models import Submission, Correction, Membership
from gymchallenge.scoring_engine import compute_daily_scores, build_leaderboard
from gymchallenge.storage_json import load_list
from gymchallenge.data_paths import data_path, exports_path
from gymchallenge.participant_ops import generate_participant_id
from gymchallenge.storage_ops import append_row

BERLIN = ZoneInfo("Europe/Berlin")


def parse_date(s: str) -> date:
    return date.fromisoformat(s)


def load_submissions(rows: list[dict[str, Any]]) -> list[Submission]:
    out: list[Submission] = []
    for r in rows:
        out.append(
            Submission(
                submission_id=r["submission_id"],
                cycle_id=r["cycle_id"],
                participant_id=r["participant_id"],
                submitted_at=datetime.fromisoformat(r["submitted_at"]),
                points=int(r["points"]),
                source=r.get("source", "manual"),
            )
        )
    return out


def load_corrections(rows: list[dict[str, Any]]) -> list[Correction]:
    out: list[Correction] = []
    for r in rows:
        out.append(
            Correction(
                correction_id=r["correction_id"],
                cycle_id=r["cycle_id"],
                participant_id=r["participant_id"],
                score_day=date.fromisoformat(r["score_day"]),
                new_points=int(r["new_points"]),
                reason=r["reason"],
                created_at=datetime.fromisoformat(r["created_at"]),
                admin=r.get("admin", "admin"),
            )
        )
    return out


def load_memberships(rows: list[dict[str, Any]]) -> list[Membership]:
    out: list[Membership] = []
    for r in rows:
        out.append(
            Membership(
                cycle_id=r["cycle_id"],
                participant_id=r["participant_id"],
                active_in_cycle=bool(r["active_in_cycle"]),
                joined_at=datetime.fromisoformat(r["joined_at"]),
                left_at=datetime.fromisoformat(r["left_at"]) if r.get("left_at") else None,
                inactive_reason=r.get("inactive_reason"),
                inactive_effective_score_day=date.fromisoformat(r["inactive_effective_score_day"])
                if r.get("inactive_effective_score_day")
                else None,
            )
        )
    return out


def cmd_report(args: argparse.Namespace) -> int:
    from_day = parse_date(args.from_day)
    to_day = parse_date(args.to_day)
    include_inactive = args.include_inactive

    memberships = load_memberships(load_list(data_path("memberships.json")))
    submissions = load_submissions(load_list(data_path("submissions.json")))
    corrections = load_corrections(load_list(data_path("corrections.json")))

    participant_ids = sorted({m.participant_id for m in memberships})

    cycle_start = from_day
    cycle_end = to_day

    daily = compute_daily_scores(
        participant_ids=participant_ids,
        submissions=submissions,
        tz=BERLIN,
        cycle_start=cycle_start,
        cycle_end=cycle_end,
        missing_points=-3,
        corrections=corrections,
    )

    leaderboard = build_leaderboard(
        memberships=memberships,
        daily=daily,
        from_day=from_day,
        to_day=to_day,
        include_inactive=include_inactive,
    )

    print(f"\nLeaderboard {from_day.isoformat()}..{to_day.isoformat()} (include_inactive={include_inactive})")

    for rank, (pid, total) in enumerate(leaderboard, start=1):
        print(f"{rank:>2}. {pid}: {total}")

    out_name = f"leaderboard_{from_day.isoformat()}_{to_day.isoformat()}.csv"
    out_path = exports_path(out_name)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "participant_id", "total_points"])

        for rank, (pid, total) in enumerate(leaderboard, start=1):
            writer.writerow([rank, pid, total])

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
        "created_at": datetime.now(BERLIN).isoformat(),
        "active": True,
    }

    append_row(path, row)

    print(f"Added participant: {participant_id} ({last}, {first})")
    return 0

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="gym-challenge")

    sub = parser.add_subparsers(dest="cmd", required=True)

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

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
