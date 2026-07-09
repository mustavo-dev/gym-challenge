# Gym Challenge UI Runbook

This document explains how to configure, run, and validate the gym-challenge UI locally.

The UI is now **config-driven** for customer-specific values.
Do not hardcode customer identity or timezone into runtime code.

For the full configuration model and release process, see:

docs/configuration-and-release.md

Purpose
Use this runbook when:

preparing a local QA instance
validating a repaired build
smoke testing UI behavior
preparing a customer-specific local instance before hosted deployment

Prerequisites
From the repository root:
Activate the virtual environment:
source .venv/bin/activate

Required Local Configuration
Create this file before running the UI:
instance/config.py

Example template:
CHALLENGE_NAME = "Spring Nutrition Challenge"
GYM_NAME = "Example Gym"
ADMIN_NAME = "Example Admin"
GYM_TIMEZONE = "America/New_York"
SECRET_KEY = "replace-with-a-long-random-secret"

Notes:
CHALLENGE_NAME controls challenge identity in the UI
GYM_NAME controls gym identity shown in admin views
ADMIN_NAME controls admin-facing identity and persisted admin metadata
GYM_TIMEZONE controls scoring window logic, score-day calculation, report elapsed-day cutoff logic, and runtime timestamps
SECRET_KEY is required for proper Flask session/flash behavior

For hosted deployment later, environment-provided SECRET_KEY is preferred.

Start the UI
Run:
python3 run_ui.py

Expected local address:
http://127.0.0.1:5000

Start the CLI
Run:
python3 -m src.main --help

Use the CLI for direct data operations, setup tasks, and validation support.

UI Entry Points
Participant page
/submit

Use this page for participant daily score submission.

Admin dashboard
/admin

Use this page for admin navigation and access to system operations.

Admin Sections
Current admin pages:
/admin
/admin/participants
/admin/memberships
/admin/submissions
/admin/corrections
/admin/cycles
/admin/reports
/admin/system
/admin/history

Current Runtime Behavior Notes
Config-driven identity

The UI now reads challenge, gym, admin, and timezone values from config.

Customer-specific rollout should be performed through instance/config.py, not by editing route or template code.

Configured timezone behavior

The gym timezone is now configured through:
GYM_TIMEZONE = "America/New_York"

The configured timezone affects:
submission window evaluation
score-day calculation
elapsed-day cutoff for active-cycle reports
displayed submission timestamps
runtime-generated timestamps in the UI layer
Submit success feedback

The submit page now shows a human-readable recorded timestamp after successful submission.

Admin submissions visibility
The admin submissions page now exposes score day and uses improved timestamp sorting.

Corrections flow
The corrections page now has a score-day filter flow:
select/load a score day
eligible participants are filtered to the relevant cycle
add the correction

The backend also rejects corrections for non-members of the relevant cycle.

Reports behavior
Leaderboard report generation now:
exports display name only
excludes archived participants
limits active-cycle scoring to elapsed days so far

Local Data Files
The UI uses the same local JSON runtime files as the CLI.

Primary runtime files include:
data/participants.json
data/memberships.json
data/membership_events.json
data/submissions.json
data/corrections.json
data/cycles.json
data/system_events.json

These files represent runtime state and are not the configuration mechanism for client identity.

Customer-specific identity belongs in instance/config.py.

Local Smoke Test Checklist
Before a larger QA cycle, verify at least:
UI starts successfully
configured challenge name appears in the UI
configured gym name appears on the admin dashboard
configured admin name appears on the admin dashboard and reports page
submit page accepts valid submissions
invalid-window submission is rejected
successful submission shows recorded timestamp
corrections page filters eligible participants by score day
reports export successfully
archived participants do not appear in normal leaderboard export paths
Automated Validation

Run the current focused validation pack:
python3 -m unittest tests.test_ui_alpha_regressions tests.test_ui_app_config tests.test_ui_config_helpers tests.test_submission_ui_service tests.test_runtime_config

Run broader test packs as needed before the next 7-day QA cycle.

QA Sequence
Current intended sequence:
configure local instance through instance/config.py
run automated validation
run local smoke test
run full 7-day local QA
review findings
only after QA passes, prepare hosted deployment

Hosted Deployment Note

The UI is still validated locally first.

Do not treat a local development server run as production deployment.

Hosted deployment comes after:
config verification
automated tests
local smoke testing
7-day local QA