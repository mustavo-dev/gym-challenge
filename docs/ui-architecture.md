# Gym Challenge UI Architecture

This document describes the architecture used by the Flask UI layer.

The UI is designed to stay thin while the backend logic remains authoritative.
Customer-specific identity and runtime environment values are now handled through configuration rather than hardcoded route or template values.

---

# Architecture Overview

The UI follows a layered design:

Flask Route  
↓  
UI Service / Config Helper  
↓  
Backend Loaders / Domain Logic  
↓  
JSON Storage

Example request path:

GET /admin/submissions  
↓  
`admin_routes.py`  
↓  
`submission_ui_service.py`  
↓  
backend loaders / display shaping  
↓  
template rendering

Example runtime-config path:

POST /submit  
↓  
`participant_routes.py`  
↓  
`src/ui/config.py` (`get_ui_timezone`)  
↓  
score-day and submission logic  
↓  
JSON storage append

---

# Design Principles

## 1. Backend Logic Remains Authoritative

The backend/domain layer defines the real rules for:

- cycle rules
- score-day logic
- scoring rules
- membership status
- correction behavior
- leaderboard behavior
- auto-inactive / reactivation behavior

The UI must not invent alternate business rules.

---

## 2. Routes Stay Thin

Routes should coordinate request handling and page rendering, not own large amounts of business logic.

Routes are responsible for:

- accepting request input
- validating required request fields
- delegating to UI services and backend helpers
- coordinating redirects / flashes / template rendering

Routes should not hardcode customer identity or environment-specific assumptions.

---

## 3. UI Services Shape Display Data

UI services are responsible for:

- resolving display names
- formatting timestamps
- preparing rows for templates
- filtering and sorting list views
- exposing auditability fields needed by admin pages

Examples:
- `src/ui/services/submission_ui_service.py`
- `src/ui/services/membership_ui_service.py`
- `src/ui/services/cycle_ui_service.py`
- `src/ui/services/history_ui_service.py`

---

## 4. UI Config Helpers Supply Flask-Context Runtime Values

The UI layer now includes:

src/ui/config.py

This is used for Flask-context configuration access such as:

configured gym timezone
configured admin actor name

Examples:

get_ui_timezone()
get_admin_actor_name()

These helpers are used in Flask routes/services where current app config is available.

5. Non-Flask Runtime Config Uses Shared Runtime Helpers

Non-Flask code now includes:

src/gymchallenge/runtime_config.py

This supports runtime configuration access outside Flask app context, including:

configured runtime timezone
configured admin name

Examples:

CLI runtime
demo data generation
future non-Flask operational tooling
Customer-Specific Configuration Rule

Customer-specific values must come from configuration, not from hardcoded route/service/template logic.

Current customer-configurable values include:

CHALLENGE_NAME
GYM_NAME
ADMIN_NAME
GYM_TIMEZONE
SECRET_KEY

The standard source is:

instance/config.py

For hosted deployment, environment override is preferred where appropriate, especially for SECRET_KEY.

Current UI Routes
Admin routes
/admin
/admin/participants
/admin/memberships
/admin/submissions
/admin/corrections
/admin/cycles
/admin/reports
/admin/system
/admin/history
Participant routes
/submit

Current Repaired Behavior Highlights
The post-alpha repair cycle introduced important UI/runtime changes:

invalid submission-window protection in the submit route
corrections restricted to valid cycle members
corrections page score-day filtering flow
archived participants excluded from normal leaderboard export paths
active-cycle leaderboard reporting limited to elapsed days
submit success feedback includes recorded timestamp
admin submissions now expose score day and better timestamp sorting
runtime timezone behavior is configured, not hardcoded
admin/runtime actor identity is now config-driven

Storage Model
The current build still uses local JSON runtime storage.

Examples include:
participants.json
memberships.json
membership_events.json
submissions.json
corrections.json
cycles.json
system_events.json

This remains a local-runtime data model for current QA and repair validation.

Future Hosting Direction
The current architecture is still compatible with a future migration path such as:

Flask UI
↓
API / service layer
↓
database-backed persistence

The repaired build is being prepared first as a config-driven, production-ready local/hostable application, with hosted deployment expected after the next successful local QA cycle.

Guardrails Going Forward

For future changes:
do not hardcode customer identity in route/template logic
do not hardcode runtime timezone assumptions
prefer config-first design for reusable client products
keep routes thin
keep display shaping in services
keep core rules in backend/domain logic
add regression tests for live request paths when UI behavior is repaired