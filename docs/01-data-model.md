# Data Model

This document describes the current data model for gym-challenge.

The current build still uses local JSON runtime storage.
Customer-specific identity does **not** belong in these JSON runtime files.
Customer-specific values belong in:

instance/config.py

The runtime JSON files store challenge state, not deployment identity.

Runtime Data Files

The current runtime state is primarily stored in these files:

participants.json
memberships.json
membership_events.json
submissions.json
corrections.json
cycles.json
system_events.json

These files are used by both the CLI and Flask UI.

Participant Model

Participant records represent people who may join one or more challenge cycles.

Fields
participant_id
first_name
last_name
created_at
active
archived
Notes
participant_id is the stable identity used across memberships, submissions, corrections, and events
archived controls whether the participant is excluded from normal operational views
archived participants may still exist in historical records and system restore flows

Cycle Model

Cycle records represent a challenge instance over a fixed date range.

Fields
cycle_id
name
start_day
end_day
created_at
active
Notes
cycles define the valid score-day range for challenge scoring
cycles must not overlap
cycle identity is used by memberships, submissions, corrections, and reporting

Membership Model

Membership records define whether a participant belongs to a specific cycle and what their current membership state is.

Fields
cycle_id
participant_id
active_in_cycle
joined_at
left_at
inactive_reason
inactive_effective_score_day
Notes
membership records are the base cycle-participation relationship
active_in_cycle reflects current state
inactive_effective_score_day is used to represent the score day when inactive status begins
memberships can be further shaped by membership events

Membership Event Model

Membership events represent state transitions that affect cycle participation over time.

Common fields
event_id
cycle_id
participant_id
event_type
effective_score_day
reason
created_at
actor
Typical event types
auto_inactive
manual_inactive
manual_reactivate
auto_reactivate_submission
Notes
membership timeline reconstruction uses both membership rows and membership events
same-day inactive/reactivate ordering matters for correct leaderboard behavior
actor identity should be configuration-driven, not hardcoded

Submission Model

Submission records represent participant daily score entries.

Fields
submission_id
cycle_id
participant_id
submitted_at
points
source
Notes
submitted_at is interpreted using the configured gym timezone for score-day logic
duplicate submissions for the same participant and score day are not allowed
submission timestamps are used for admin visibility and auditability
score day is derived from timestamp plus configured timezone, not stored directly in the raw submission record

Correction Model

Correction records represent admin overrides for a participant’s score on a specific score day.

Fields
correction_id
cycle_id
participant_id
score_day
new_points
reason
created_at
admin
Notes
corrections must only apply to valid members of the relevant cycle
corrections override base scoring for the relevant score day
admin identity should come from configured admin name
correction creation timestamps should use configured runtime timezone behavior

System Event Model

System event records represent important system-level actions.

Common fields
event_id
event_type
participant_id
reason
created_at
actor
Example event types
dataset_reset
participant_archived
participant_restored
Notes
system events support operational auditability
actor identity should be configuration-driven
timestamps should follow configured runtime timezone behavior where applicable

Derived Display/View Models

The UI also produces derived display rows that are not stored directly as raw JSON records.

Examples include:

admin submissions list rows
corrections history rows
membership display rows
cycle display rows
report export rows

These view models may include derived fields such as:

display_name
formatted timestamps
score_day
visibility flags such as archived inclusion/exclusion
sort keys such as raw timestamp fields

These derived fields belong in services/view shaping, not in the raw persistent storage model unless explicitly promoted later.

Identity and Configuration Boundary

Customer-specific identity is not part of the runtime JSON data model.

The following values are configuration-driven and belong in instance/config.py instead:

CHALLENGE_NAME
GYM_NAME
ADMIN_NAME
GYM_TIMEZONE
SECRET_KEY

This separation matters because:

challenge state should remain portable
customer rollout should not require editing stored runtime data
new client instances should be created through config, not code/data rewrites

Relationship Summary
Participant to Membership

One participant may have memberships in multiple cycles.

Cycle to Membership

One cycle may contain many memberships.

Membership to Membership Event

One membership may accumulate many events over time.

Participant/Cycle to Submission

A participant may have multiple submissions within a cycle, but only one valid submission per score day.

Participant/Cycle to Correction

A participant may have corrections tied to score days within a cycle.

Participant to System Event

A participant may have system events such as archive/restore history.

Runtime Behavior Implications

The repaired build now depends on this data model being interpreted with:

configured gym timezone
config-driven admin identity
archive-aware report behavior
correct membership timeline reconstruction
correction precedence over base scoring
elapsed-day-only active-cycle reporting

This means the JSON files alone are not the whole story.
Correct behavior also depends on the current repaired domain logic and config layer.