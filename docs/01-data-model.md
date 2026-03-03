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
* timezone (Europe/Berlin)
* start\_dt
* end\_dt
* status: planned|active|closed
* Cycle includes score days up to end\_score\_day; last window closes at 12:00 following day

### Membership

Links Participant ↔ Cycle

* cycle\_id
* participant\_id
* active\_in\_cycle
* joined\_at
* left\_at (optional)
* auto_inactive: bool
* inactive_reason: "manual"|"auto"
* inactive_effective_score_day: date | None

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
