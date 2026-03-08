# Decisions Log

## Locked
- Timezone: Europe/Berlin
- Window: 20:00 → 12:00 next day
- Missing = -3
- Points: -3..5 integer
- One submission per score day; duplicates keep earliest valid
- No participant retroactive submissions
- Admin corrections allowed (overlay approach)
- Cycles first-class; membership per-cycle
- Persistence v1: JSON (data/ gitignored), upgrade to SQLite later
- Output v1: console + CSV
- inactive_behavior configuration exists (historical|exclude)
- auto-inactive after 4 consecutive misses is based on valid participant submissions; corrections do not reset the streak
- auto-inactive becomes effective the day after the 4th consecutive miss (the 4th miss still gets -3)
- Admin reactivate exists; reason required; if --effective-day is omitted, default is next score day
- Valid participant submission auto-reactivates an auto-inactive member on the same score day; corrections do not reactivate.

### Membership Status Tracking

Participants may transition between active and inactive states multiple times within a cycle.

To preserve a full history, the system records **membership events** rather than overwriting status fields.

This allows Jayme to see:

- why someone became inactive
- whether inactivity was automatic or manual
- when someone resumed participation
- how many members were active at any point during the cycle

## Cycle Lifecycle Decisions

- Cycle IDs use seasonal naming:
  - spring26
  - summer26
  - fall26
  - winter26

- Cycle names use human-readable seasonal labels:
  - Spring 2026
  - Fall 2027

- Jayme may create future cycles in advance

- Cycle status is automatically derived from:
  - start_day
  - end_day
  - Berlin scoring window

- Derived cycle states are:
  - planned
  - active
  - closed

- A cycle becomes active at:
  - start_day 20:00 Europe/Berlin

- A cycle becomes closed at:
  - end_day + 1 day at 12:00 Europe/Berlin

- No two cycles may have overlapping active windows

- Only one cycle may be active at a time
