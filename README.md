# gym-challenge

**Current Version:** 1.1.0-dev  
**Current Status:** Post-alpha repair and stabilization build preparing for the next 7-day local QA cycle.

gym-challenge is a private Python CLI + Flask UI system for managing a recurring gym challenge with participants, memberships, submissions, corrections, cycles, reports, and system history.

This build is now moving toward **config-driven multi-client readiness**.
Customer-specific values should be configured through `instance/config.py`, not hardcoded into core code.

---

# Current Scope

The system currently includes:

- participant management
- cycle management
- membership management
- participant daily score submission
- admin corrections
- leaderboard report generation
- system archive/restore actions
- history visibility for admin operations

---

# Configuration Model

Customer-specific values are now expected to come from configuration.

Create:

instance/config.py

Use this template:

CHALLENGE_NAME = "Spring Nutrition Challenge"
GYM_NAME = "Example Gym"
ADMIN_NAME = "Jayme"
GYM_TIMEZONE = "America/New_York"
SECRET_KEY = "replace-with-a-long-random-secret"

For a full explanation of what each key does and how to prepare a new client instance, see:

docs/configuration-and-release.md

Runtime and Identity Notes

The repaired build now supports:

configured challenge name
configured gym name
configured admin name
configured gym timezone
config/env-based secret key handling

The runtime timezone is configured, not hardcoded.
New customer instances should always set GYM_TIMEZONE explicitly.

Local Development and QA

Activate the virtual environment:

source .venv/bin/activate

Run the CLI:

python3 -m src.main --help

Run the Flask UI:

python3 run_ui.py

Run the current validation pack:

python3 -m unittest tests.test_ui_alpha_regressions tests.test_ui_app_config tests.test_ui_config_helpers tests.test_submission_ui_service tests.test_runtime_config
Release Direction

The current release sequence is:

local repair and validation
→ local 7-day QA
→ hosted deployment preparation
→ client release

The goal is for future client rollout to require configuration changes, not customer-specific code edits.

Notes for New Client Instances

For a standard new client rollout, do not edit core application logic.

Normal client setup should only require changing:

CHALLENGE_NAME
GYM_NAME
ADMIN_NAME
GYM_TIMEZONE
SECRET_KEY

If scoring rules or challenge behavior need to differ, that should be treated as a product/version decision, not a normal deployment step.

Supporting Documents
docs/configuration-and-release.md
docs/ui-runbook.md
docs/ui-architecture.md
CHANGELOG.md