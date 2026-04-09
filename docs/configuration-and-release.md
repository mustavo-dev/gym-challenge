# Configuration and Release Guide

This document explains exactly what must be configured before running or releasing a customer instance of gym-challenge.

The system is now designed to be **config-driven** for customer-specific values.
New client instances should be created by changing configuration, not by editing core code.

---

# Configuration File Location

Create this file:

instance/config.py

This file is not for source control.
It should contain the customer-specific settings for the local instance or hosted deployment.

Required Configuration Keys

Use this template as the starting point:

CHALLENGE_NAME = "Spring Nutrition Challenge"
GYM_NAME = "Example Gym"
ADMIN_NAME = "Jayme"
GYM_TIMEZONE = "America/New_York"
SECRET_KEY = "replace-with-a-long-random-secret"

What Each Key Does
CHALLENGE_NAME
Used for:
main UI header
browser title
overall challenge identity in the UI

Example:
CHALLENGE_NAME = "Spring Nutrition Challenge"

GYM_NAME
Used for:
admin dashboard gym label
customer-specific gym identity in the UI

Example:
GYM_NAME = "CrossFit Example"

ADMIN_NAME
Used for:
admin dashboard label
admin-facing report text
persisted admin actor/admin metadata in runtime operations

Example:
ADMIN_NAME = "Jayme"

GYM_TIMEZONE
Used for:
submission scoring window logic
score day calculation
report elapsed-day cutoff logic
displayed runtime timestamps
CLI/runtime timestamp generation

This value must be a valid IANA timezone name.

Examples:
GYM_TIMEZONE = "America/New_York"
GYM_TIMEZONE = "Europe/Berlin"
GYM_TIMEZONE = "America/Chicago"

The system default is UTC, but real client instances should always set this explicitly.

SECRET_KEY
Used for:
Flask session handling
flash messages
secure hosted deployment behavior

For local customer instances, this may be stored in instance/config.py.

For hosted deployment, environment variable override is preferred.

Environment takes precedence over instance config.

Example local value:
SECRET_KEY = "replace-with-a-long-random-secret"

Secret Key Precedence

The UI app resolves SECRET_KEY in this order:

SECRET_KEY from environment
SECRET_KEY from instance/config.py
development fallback inside the app factory

For hosted deployment, use an environment variable whenever possible.

Local Run Commands

From the repository root:

Activate the virtual environment:
source .venv/bin/activate

Run the CLI:
python3 -m src.main --help

Run the Flask UI:
python3 run_ui.py

Local Validation Commands

Run the current validation pack from the repository root:
python3 -m unittest tests.test_ui_alpha_regressions tests.test_ui_app_config tests.test_ui_config_helpers tests.test_submission_ui_service tests.test_runtime_config

You may also run the full test suite as needed.

New Client Release Process

For a new client instance:
Prepare a clean repo checkout.
Create instance/config.py.
Set:
CHALLENGE_NAME
GYM_NAME
ADMIN_NAME
GYM_TIMEZONE
SECRET_KEY
Activate the virtual environment.
Run automated tests.
Run local smoke tests.
Run the full 7-day QA cycle locally.
Only after QA passes, prepare hosted deployment.

What Should Change Per Client

These values should change per client:
challenge name
gym name
admin name
gym timezone
secret key

These should not normally require code changes.

What Should Not Change Per Client
Do not edit core application logic for a standard client rollout.

Do not change:
scoring rules
submission window rules
auto-inactive logic
correction precedence rules
membership timeline rules

If those rules must differ for a future client, that should be treated as a product/version decision, not a normal deployment step.

Hosted Deployment Note
This project is still validated locally first.

The intended sequence is:
local repair and validation
→ local 7-day QA
→ hosted deployment preparation
→ client release

Hosted deployment should use:
environment-provided SECRET_KEY
a customer-specific instance/config.py
the same configured runtime timezone as local QA

Release Checklist
Before handing the system to a client or moving to hosted deployment, confirm:
instance/config.py exists
all customer-specific values are set
GYM_TIMEZONE is explicitly configured
SECRET_KEY is configured
automated tests pass
local smoke testing passes
7-day QA passes
no customer-specific values remain hardcoded in runtime code