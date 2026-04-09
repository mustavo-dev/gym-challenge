# Changelog

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