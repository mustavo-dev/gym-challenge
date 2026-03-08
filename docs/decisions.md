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
