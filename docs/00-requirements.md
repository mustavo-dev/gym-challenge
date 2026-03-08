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

* A cycle has: cycle\_id, start_score_day, end_score_day, timezone, status
* Cycles may run:

  * sequentially (restart every ~3 months)
  * concurrently (overlap)

* Participant membership is per-cycle
* Cycle end includes final submission window until 12:00 next day

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
* A valid participant submission after auto-inactive status automatically reactivates the participant on that same score day.
* That submission counts normally for that score day.
* Admin corrections do not reactivate a participant.

## Persistence (v1)

* JSON files stored locally in data/ (gitignored)
* Upgrade path: SQLite later

## Non-goals (for MVP)

* WhatsApp API automation
* Google Forms / Sheets integration
* Web UI
