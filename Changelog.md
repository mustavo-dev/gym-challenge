# Changelog

## [1.2.0-dev] - 2026-06-08

Bug: Participants never went inactive during UI operation, even after 4 consecutive missed days. The -3 penalty kept accumulating indefinitely instead of stopping after day 4.
Root cause: detect_auto_inactive and detect_auto_reactivate only existed as manual CLI commands. The Flask UI never called them.
Fix: Added _run_auto_inactive_and_reactivate() to src/ui/routes/participant_routes.py, triggered after every successful submission save. Runs the inactive pass first, reloads membership state, then runs the reactivation pass.
Test fix: Three SimpleNamespace mocks in tests/test_ui_alpha_regressions.py updated to include start_day and end_day.
Beta data backfill: Ran python3 -m src.main system apply-auto-inactive --cycle-id spring26 --from 2026-04-20 --to 2026-04-26 once to correct P5's stale membership record.
Result: 95/97 tests passing. 2 pre-existing failures in test_demo_data_generator.py are unrelated and deferred.

### Acceptance trial outcome — 2026-06-28

The seven-day v1.2 acceptance trial validated the repaired inactive/reactivation workflow under sustained use.

The trial confirmed that participant reactivation could occur through normal UI submission flow, but it also exposed additional scoring and membership-state inconsistencies. By Day 6, membership state and leaderboard output were no longer aligned for multiple participants.

Known issues from the trial include:

- Membership state displayed inconsistently between admin views.
- Multiple participants were shown inactive unexpectedly.
- Leaderboard scoring became incorrect for several participants.
- Participant status visibility remained insufficient for admin troubleshooting.

The v1.2 build remains in development and is not ready for hosted deployment or release. Defects discovered during the acceptance trial remain pending investigation and repair.

## [1.1.0-dev] - 2026-04-09

### Status
Post-alpha repair and stabilization build preparing for the next 7-day local QA cycle.

### Included work

#### Alpha repair coverage
- Added live UI regression coverage for alpha-discovered failures
- Added UI/config/runtime helper test coverage
- Expanded service-level validation for submissions/admin visibility behavior

#### Correctness repairs
- Reject invalid-window submissions before write
- Reject corrections for non-members of the relevant cycle
- Filter correction participant choices by score day / relevant cycle
- Exclude archived participants from normal leaderboard export paths
- Export leaderboard report with display names only
- Limit active-cycle leaderboard reporting to elapsed days only
- Repair membership timeline inactive-state handling
- Repair same-day inactive/reactivate ordering behavior
- Restore correct leaderboard reactivation scoring behavior

#### Admin visibility and auditability
- Expose score day in admin submissions service
- Show score day on admin submissions page
- Improve submission timestamp sorting support
- Show recorded submit timestamp after successful participant submission
- Add corrections page score-day filter flow

#### Configuration and production-readiness groundwork
- Add config-driven challenge name support
- Add config-driven gym name support
- Add config-driven admin name support
- Add config-driven gym timezone support
- Add instance-config loading in the Flask app factory
- Add shared runtime config helpers for non-Flask code
- Remove hardcoded runtime timezone usage from UI and runtime code
- Remove hardcoded admin name usage from runtime code
- Standardize imports on `src...` package paths
- Add environment-over-instance precedence for `SECRET_KEY`

#### Current release direction
- Continue local validation first
- Complete documentation/configuration alignment
- Run next 7-day local QA cycle
- Prepare hosted deployment only after QA passes

---

## [1.0.0] - Alpha baseline

### Status
Initial CLI + local Flask UI build used for the first full alpha / acceptance trial.

### Notes
- Preserved as the pre-repair baseline
- Multiple issues were discovered during alpha and are being addressed in v1.1
