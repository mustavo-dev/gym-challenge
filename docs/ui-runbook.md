# Gym Challenge UI Runbook

This document explains how to run and test the UI locally.

---

# Start the UI

Activate the virtual environment.

source .venv/bin/activate

Run the server.

python run_ui.py

Expected output:

Running on http://127.0.0.1:5000

---

# Admin Navigation

Admin pages:
/admin
/admin/participants
/admin/memberships
/admin/cycles
/admin/submissions
/admin/corrections
/admin/history

---

# Participant Submission

Participant score submission page:
/submit

---

# Local Data Files

The UI reads from the same JSON files used by the CLI.
data/
participants.json
memberships.json
membership_events.json
submissions.json
corrections.json
cycles.json

These files represent **runtime state** and are ignored by git.

---

# Creating Test Data

Example CLI commands:

Create a cycle:
python src/main.py cycle create
--season fall
--year 2026
--start 2026-09-01
--end 2026-11-30

Add a correction:
python src/main.py correction add
--cycle-id fall26
--participant-id lopez-sarah-01
--score-day 2026-10-30
--points 2
--reason demo_ui_test

These actions immediately appear in the UI.

---

# Development Server Warning

Flask's built-in server is for development only.

Do not use it for production.

Production deployment will occur after the API/server migration phase.
