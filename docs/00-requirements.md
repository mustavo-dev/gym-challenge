# gym-challenge — Requirements (M0)

## Goal

Build a local-first Python automation system for a recurring gym nutrition/participation challenge.
Must support 3-month cycles, cycle restarts, and concurrent cycles.

## Time / Window

* Timezone: Europe/Berlin (authoritative)
* Daily check-in window: 20:00 → 12:00 next day (Berlin)
* Submissions outside window are invalid (ignored)
* Missing submission for a score day = -3

## Points

* Integer points range: -3 to 5

## Submission rules

* One submission per participant per score day
* If duplicates happen: keep earliest valid submission, ignore the rest
* No retroactive submissions by participants
* Admin corrections allowed (Jayme), not advertised
* Correction reason is required

## Participation Status Tracking

Participants can transition between active and inactive states during a cycle.

A participant becomes **automatically inactive** after **four consecutive days with no submission**.

Inactive participants:

- remain visible in leaderboards (unless explicitly excluded)
- stop accumulating score changes until they become active again

### Reactivation

A participant can become active again in two ways:

1. **Automatic Reactivation**

   - If an inactive participant submits a valid daily score, they are automatically reactivated.
   - Reactivation is effective on the **same score day** as the valid submission.
   - That day's score counts normally.

2. **Manual Reactivation**

   - Jayme may manually reactivate a participant through the CLI.
   - This requires specifying an effective score day and reason.

### Important Rule

Administrative **corrections do not reactivate participants**.

Only a valid participant submission or manual admin action can reactivate someone.

## Cycle rules

* A cycle has: cycle\_id, start\_score\_day, end\_score\_day, timezone, status
* Cycles may run:

  * sequentially (restart every ~3 months)
  * concurrently (overlap)

* Participant membership is per-cycle
* Cycle end includes final submission window until 12:00 next day

## Cycle Lifecycle Rules

Cycles are date-driven and use the Berlin scoring window.

Each cycle has:
- cycle_id
- name
- start_day
- end_day
- created_at

Cycle states are:

- planned
- active
- closed

These states are automatically derived from the current time and scoring window.

### Scoring Window

- A score day opens at 20:00 Europe/Berlin
- A score day closes at 12:00 Europe/Berlin on the next day

### State Rules

A cycle is:

- **planned** before `start_day` at 20:00 Berlin
- **active** from `start_day` at 20:00 Berlin until `end_day + 1 day` at 12:00 Berlin
- **closed** after `end_day + 1 day` at 12:00 Berlin

### Business Rules

- Only one cycle may be active at a time
- Future cycles may be created in advance
- Future cycles remain planned until their start window opens
- Active cycles automatically become closed after their final scoring window ends
- Closed cycles remain available for historical reporting
- No two cycles may have overlapping active windows

## Reporting (v1)

* Console leaderboard summary
* CSV export
* Display format: Last, First
* Internals store first + last separately

## Reporting Policies

* Inactive handling models: historical vs exclude

## Auto-inactive rule

* 4 Consecutive missed score days → auto-inactive in that cycle
* Auto-inactive is based on participant submissions, not corrections
* Admin can reactivate an inactive member in a cycle with:

  * required reason
  * optional effective score day (defaults to next score day if not provided)

* If valid submission is added after participant becomes automatically inactive they will automatically be reactivated for doing the correct thing

## Persistence (v1)

* JSON files stored locally in data/ (gitignored)
* Upgrade path: SQLite later

## Non-goals (for MVP)

* WhatsApp API automation
* Google Forms / Sheets integration
* Web UI
