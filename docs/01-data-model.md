# Data Model (M0)

## Entities

### Participant

* participant\_id (internal stable ID)
* first\_name
* last\_name
* created\_at
* active (global directory)

### Cycle

* cycle\_id (string, unique)
* name
* timezone: str (Europe/Berlin)
* start_score_day: date
* end_score_day: date
* status: planned|active|closed
* Cycle includes score days up to end\_score\_day; last window closes at 12:00 following day

### Membership

Links Participant ↔ Cycle

* cycle\_id
* participant\_id
* active_in_cycle = True
* joined\_at
* left\_at (optional)
* auto_inactive: bool
* inactive_reason: "manual"|"auto"
* inactive_effective_score_day: date | None

#### Membership state transitions (MVP)

Reactivation is represented by updating Membership fields (no separate event log in MVP):

- When a member becomes inactive (manual or auto):
  - active_in_cycle = False
  - inactive_reason = "manual" or "auto"
  - inactive_effective_score_day = the first score day they are considered inactive

- When an admin reactivates a member:
  - active_in_cycle = True
  - inactive_reason remains as historical info (last known reason), or may be set to "manual" if preferred
  - inactive_effective_score_day = None
  - The reactivate command may specify an effective score day; if provided, the member is treated as active starting on that score day (otherwise defaults to next score day).
- Auto-reactivation by submission (MVP):
  - If a participant is inactive due to auto-inactive status and later makes a valid submission, the system treats them as active again starting on that same score day.
  - The submission counts normally.
  - Admin corrections do not trigger reactivation.

### Submission (raw event)

* submission\_id
* cycle\_id
* participant\_id
* submitted\_at (tz-aware)
* points (-3..5)
* source (manual|import|future:google)

### Correction (admin overlay)

* correction\_id
* cycle\_id
* participant\_id
* score\_day (YYYY-MM-DD label)
* new\_points
* reason required
* created\_at
* admin (e.g., Jayme)

## Derived Concepts

### Score Day

A "score day" is determined from submitted\_at using the 20:00 boundary.

* If submitted\_at time is 20:00–23:59 → score\_day = that date
* If submitted\_at time is 00:00–11:59 → score\_day = previous date
* If submitted\_at time is 12:00–19:59 → invalid submission

### Final Daily Score

For each (participant, score\_day) in a given cycle:

1. Take earliest valid submission (if any)
2. If no valid submission → missing penalty (-3)
3. If an admin correction exists for that (participant, score\_day) → override to correction points
