# Gym Challenge UI Architecture

This document describes the architecture used by the Flask UI layer.

The goal of the UI architecture is to keep the web interface thin while preserving the CLI backend as the authoritative logic engine.

---

# Architecture Overview

The UI follows a layered design:
Flask Route
↓
UI Service
↓
Backend Loaders
↓
JSON Storage

Example request:
GET /admin/corrections

Flow:
admin_routes.py
↓
correction_ui_service.py
↓
load_corrections()
↓
data/corrections.json

---

# Design Principles

## 1. Backend Logic Remains Authoritative

The CLI backend defines all rules including:

- cycle rules
- scoring rules
- membership status
- correction behavior

The UI **never duplicates backend logic**.

---

## 2. UI Services Format Data

UI services are responsible for:

- resolving display names
- formatting timestamps
- merging data for display
- simplifying backend models

Example service files:
src/ui/services/
participant_ui_service.py
membership_ui_service.py
cycle_ui_service.py
submission_ui_service.py
correction_ui_service.py
history_ui_service.py

---

## 3. Routes Stay Minimal

Routes only coordinate page rendering.

Example:
@admin_bp.get("/admin/corrections")
def corrections_page():
corrections = get_corrections_for_list()
return render_template(...)

All transformation logic belongs in services.

---

# Current UI Routes

Admin routes:
/admin
/admin/participants
/admin/memberships
/admin/cycles
/admin/submissions
/admin/corrections
/admin/history

Participant routes:

/submit
/submissions

---

# History Page

The history page combines:

- corrections
- membership events

Submissions are intentionally excluded because they already have their own page.

---

# Future Migration

The current architecture allows the data layer to be replaced with an API without rewriting the UI.

Future architecture:
Flask UI
↓
REST API
↓
Database

UI services will transition from:
load_list(data_path(...))

to

requests.get(API_ENDPOINT)

without changing routes or templates.
