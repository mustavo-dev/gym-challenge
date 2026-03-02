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

## Cycle rules

* A cycle has: cycle\_id, start\_dt, end\_dt, timezone, status
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

## Persistence (v1)

* JSON files stored locally in data/ (gitignored)
* Upgrade path: SQLite later

## Non-goals (for MVP)

* WhatsApp API automation
* Google Forms / Sheets integration
* Web UI
