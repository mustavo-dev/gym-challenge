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
- auto-inactive after 4 consecutive misses (based on submissions, not corrections unless also active status changed to active following admin correction
