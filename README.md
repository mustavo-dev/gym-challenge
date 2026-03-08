# gym-challenge

Private Python CLI system for managing a recurring gym nutrition / participation challenge.

The system tracks participants, submissions, corrections, memberships, and membership events across seasonal challenge cycles. It enforces participation rules automatically, maintains historical state transitions, and generates leaderboard reports.

The current version is a CLI-first backend foundation. A future UI will provide a simpler interface for Jayme and participants.

---

## Project Goals

- Run recurring seasonal challenge cycles
- Track participant submissions and scores
- Enforce participation rules automatically
- Maintain a full historical audit trail
- Export leaderboard reports
- Remain portable across development machines

Design priorities:

- deterministic behavior
- simple local data storage
- reproducible workflows
- strong test coverage

---

## Challenge Cycle Model

Challenges run as **seasonal cycles**.

Examples:

fall26
winter26
spring27
summer27

Each cycle contains:

cycle_id
name
start_day
end_day
created_at

Cycle status is derived automatically from the current time and the Berlin scoring window.

Cycle statuses:

planned
active
closed

Only one active cycle is allowed at a time.
Future cycles may be created in advnace, but active windows may not overlap.


## Scoring Window

Each challenge day runs on a delayed scoring window.

Day opens: 20:00 local time
Day closes: 12:00 the following day

This allows late submissions the next morning while keeping a consistent daily boundary.

## Core Entities

- Participant: represents a person in the system
Fields:
participant_id
first_name
last_name
created_at
active

Participant IDs are collision safe:
smith-john-01
smith-john-02

Example command:
python3 src/main.py participant add --first John --last Smith

## Membership
Represents a participant's involvement in a cycle
Fields:
cycle_id
participant_id
joined_at
left_at
active_in_cycle
inactive_reason
inactive_effective_score_day

Example command:
python3 src/main.py membership add --cycle-id fall26 --participant-id smith-john-01

## Submission
Daily activity submission
Fields:
submission_id
cycle_id
participant_id
points
submitted_at

Example command:
python3 src/main.py submission add --cycle-id fall26 --participant-id smith-john-01 --points 3

## Correction
Administrative score adjustment
Corrections override points only, not participation status
Fields:
correction_id
cycle_id
participant_id
score_day
points
reason
created_at

Example command:
correction_id
cycle_id
participant_id
score_day
points
reason
created_at

## Membership Events
All membership state changes are logged
Fields:
event_id
cycle_id
participant_id
event_type
effective_score_day
reason
created_at
actor

Event types currently used:
manual_inactive
manual_reactivate
auto_inactive
auto_reactivate_submission

This allows full historical reconstruction of membership timelines.

## Participation Rules
- Missed Day Penalty
If a participant does not submit for a scoring day:
points = -1

- Auto-inactive Rule
If a participant misses 4 consecutive days membership automatically becomes inactive
An auto_inactive event is recorded

- Auto-reactivation Rule
If an inactive participant submits a valid submission membership automatically reactivates
An auto_reactivate_submission event is recorded

Corrections alone do not trigger reactivation

## CLI Commands
- Participants: Add participant
python3 src/main.py participant add --first John --last Smith

- Membership: Add participant to cycle
python3 src/main.py membership add \
  --cycle-id fall26 \
  --participant-id smith-john-01

Deactivate membership:
python3 src/main.py membership deactivate \
  --cycle-id fall26 \
  --participant-id smith-john-01 \
  --effective-day 2026-09-10 \
  --reason "Manual deactivation"

Reactivate membership:
python3 src/main.py membership reactivate \
  --cycle-id fall26 \
  --participant-id smith-john-01 \
  --effective-day 2026-09-12 \
  --reason "Back participating"

- Submissions
python3 src/main.py submission add \
  --cycle-id fall26 \
  --participant-id smith-john-01 \
  --points 3

- Corrections
python3 src/main.py correction add \
  --cycle-id fall26 \
  --participant-id smith-john-01 \
  --score-day 2026-09-03 \
  --points 2 \
  --reason "Admin fix"

- Reports
Generate leaderboard report
python3 src/main.py report \
  --from 2026-09-01 \
  --to 2026-09-07

Include inactive members:
python3 src/main.py report \
  --from 2026-09-01 \
  --to 2026-09-07 \
  --include-inactive

Reports export CSV files to
exports/

Example export path:
python3 src/main.py report \
  --from 2026-09-01 \
  --to 2026-09-07 \
  --include-inactive

## Cycle Management
- Create a cycle
python3 src/main.py cycle create \
  --season fall \
  --year 2026 \
  --start 2026-09-01 \
  --end 2026-11-30

- List cycles
python3 src/main.py cycle list

- Show cycle details
python3 src/main.py cycle show --cycle-id fall26

Example output
Cycle: fall26
Name: Fall 2026
Start Day: 2026-09-01
End Day: 2026-11-30
Status: planned

## System Commands
- Apply auto-inactive detection
python3 src/main.py system apply-auto-inactive \
  --cycle-id fall26 \
  --from 2026-09-01 \
  --to 2026-09-30

- Apply auto-reactivation detection
python3 src/main.py system apply-auto-reactivate \
  --cycle-id fall26 \
  --from 2026-09-01 \
  --to 2026-09-30

These commands update membership state and generate event history

## Data Storage
Local JSON storage
data/
  participants.json
  memberships.json
  submissions.json
  corrections.json
  membership_events.json
  cycles.json

Leaderboard exports
exports/

## Development Workflow
This project is designed for portable development across devices

- Rules
* No secrets committed
* Portable across HQ and travel laptop
* GitHub used as development handoff
* Deterministic Behavior
* Test coverage enforced

## Future Development
- Planned expansions
* Web UI for administrators
* Participant submission interface
* Messaging automation
* Google Sheets integration
* Deterministic stress-test dataset generator
