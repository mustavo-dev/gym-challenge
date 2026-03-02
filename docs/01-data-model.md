# Data Model (M0)

## Entities

### Participant
- participant_id (internal stable ID)
- first_name
- last_name
- created_at
- active (global directory)

### Cycle
- cycle_id (string, unique)
- name
- timezone (Europe/Berlin)
- start_dt
- end_dt
- status: planned|active|closed

### Membership
Links Participant ↔ Cycle
- cycle_id
- participant_id
- active_in_cycle
- joined_at
- left_at (optional)

### Submission (raw event)
- submission_id
- cycle_id
- participant_id
- submitted_at (tz-aware)
- points (-3..5)
- source (manual|import|future:google)

### Correction (admin overlay)
- correction_id
- cycle_id
- participant_id
- score_day (YYYY-MM-DD label)
- new_points
- reason
- created_at
- admin (e.g., Jayme)

## Derived Concepts

### Score Day
A "score day" is determined from submitted_at using the 20:00 boundary.
- If submitted_at time is 20:00–23:59 → score_day = that date
- If submitted_at time is 00:00–11:59 → score_day = previous date
- If submitted_at time is 12:00–19:59 → invalid submission

### Final Daily Score
For each (participant, score_day) in a given cycle:
1) Take earliest valid submission (if any)
2) If no valid submission → missing penalty (-3)
3) If an admin correction exists for that (participant, score_day) → override to correction points
