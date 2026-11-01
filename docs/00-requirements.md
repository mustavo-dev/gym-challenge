# Requirements

This document defines the current functional expectations for gym-challenge.

The system is intended to support a recurring gym challenge using a Python CLI and Flask UI, with customer-specific identity and runtime values provided through configuration.

---

# Product Scope

gym-challenge must support:

- participant management
- cycle management
- membership management
- participant daily score submission
- admin corrections
- leaderboard report generation
- system archive/restore operations
- history visibility for important admin/runtime events

The system is currently validated locally first and prepared for later hosted deployment after QA.

---

# Configuration Requirements

The system must support customer-specific configuration through:

instance/config.py

The following values must be configurable without changing core code:

CHALLENGE_NAME
GYM_NAME
ADMIN_NAME
GYM_TIMEZONE
SECRET_KEY

The system default timezone may be UTC, but real customer instances must be expected to set GYM_TIMEZONE explicitly.

Customer rollout should be achieved through configuration changes, not customer-specific code edits.

Participant Requirements
Participant records

The system must allow an admin to create participants.

Each participant record must include:

participant ID
first name
last name
created timestamp
active/archive state

Participant IDs must be generated consistently and avoid collisions.

Archived participants

Archived participants must be excluded from normal operational flows.

Archived participants must not appear in:

normal leaderboard export paths
normal correction eligibility paths
normal active participant operational views

Archived participants may still be accessible through the system/archive restore path.

Cycle Requirements

The system must allow an admin to create challenge cycles.

Each cycle must include:

cycle ID
cycle name
start day
end day
created timestamp
active state

Cycle IDs and names must be generated consistently.

The system must reject overlapping cycle windows.

Membership Requirements

The system must allow an admin to add participants to a cycle.

Each membership must include:

cycle ID
participant ID
active-in-cycle state
joined timestamp
optional left timestamp
optional inactive reason
optional inactive effective score day

The system must reject duplicate memberships for the same participant and cycle.

Membership timeline behavior must support:

joined state
inactive state
reactivated state
left state

Submission Requirements
Participant submission page

The system must provide a participant-facing page for daily score submission.

The submit page must:

list eligible participants for the active cycle
reject invalid participant selection
reject invalid score values
reject duplicate submissions for the same participant and score day
reject submissions outside the configured valid scoring window
show a human-readable recorded timestamp after successful submission
Submission timing

Submission behavior must use the configured gym timezone.

The score-day window must be enforced using configured runtime timezone behavior rather than hardcoded timezone assumptions.

Submission visibility

The admin submissions view must provide:

participant display name
submission timestamp
score day
points
source
reliable sort behavior by timestamp and other supported filters

Correction Requirements

The system must allow an admin to create corrections.

Each correction must include:

correction ID
cycle ID
participant ID
score day
new points
reason
created timestamp
admin identity

Corrections must be restricted to participants who are valid members of the relevant cycle.

The corrections page must support filtering eligible participant choices by score day / matching cycle.

Corrections must override base scoring for the relevant participant and score day.

Latest correction should remain the highest-precedence correction where multiple corrections exist for the same score day path.

Scoring Requirements

The system must support daily score computation for cycle members.

The scoring system must support:

valid participation points
missed-day penalty behavior
correction override behavior
score-day calculation based on configured timezone

Scoring behavior must remain backend/domain authoritative.

UI behavior must not silently introduce alternate scoring rules.

Auto-Inactive and Reactivation Requirements

The system must support auto-inactive behavior for members who miss the required threshold of days (4 consecutive days).

The system must support reactivation after a valid submission when applicable.

Membership timeline reconstruction and leaderboard behavior must correctly reflect:

stored inactive state
same-day inactive/reactivate ordering
valid reactivation scoring behavior

Report Requirements

The system must allow leaderboard report export for a selected cycle.

Leaderboard report generation must:

use display name only in export
exclude archived participants from normal export paths
support configured runtime timezone behavior
limit active-cycle scoring to elapsed days only
support inactive inclusion behavior where explicitly requested

Report output must align with operator expectations and remain readable.

System / History Requirements

The system must support system-level maintenance actions including:

dataset reset
participant archive
participant restore

The system must record important system/runtime actions with actor/admin identity.

The system must provide history visibility for important admin/runtime events.

Runtime Requirements
CLI runtime

The CLI must run using module invocation:

python3 -m src.main --help
UI runtime

The Flask UI must be able to run locally using:

python3 run_ui.py
Secret key behavior

The UI secret key must resolve in this order:

environment variable
instance config
dev fallback

Hosted deployment should prefer environment-provided secret values.

Quality and Validation Requirements

Before hosted deployment or client release, the system must pass:

automated validation
local smoke testing
a full 7-day local QA cycle

Meaningful repairs to correctness or runtime behavior must be followed by retesting before release.

Carry-Forward Requirement

Future reusable client products should be designed config-first from the beginning.

If a project is likely to serve multiple customers, customer-specific identity and environment values must be placed in configuration up front instead of being retrofitted later.