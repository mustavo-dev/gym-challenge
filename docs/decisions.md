# Decisions

This document records important architectural and product decisions for gym-challenge.

---

# 2026-04-09 — Config-first customer model

## Decision

gym-challenge is no longer treated as a one-gym, one-admin build.

Customer-specific identity and environment values must be handled through configuration, not through hardcoded route, service, template, or runtime logic.

## Rationale

The alpha repair cycle made it clear that retrofitting customer-specific values late creates unnecessary deployment friction and refactor work.

For a reusable client product, values such as challenge name, gym name, admin name, timezone, and secret key must be configurable from the beginning.

## Result

Customer-specific values are now expected to come from:

```python
instance/config.py

Current config-driven values include:
CHALLENGE_NAME
GYM_NAME
ADMIN_NAME
GYM_TIMEZONE
SECRET_KEY

Carry-forward rule

Future reusable client products should be designed config-first from the beginning.

If a project is likely to be reused across multiple customers, customer-specific values should go into configuration up front rather than being refactored later.

2026-04-09 — Runtime timezone must be configured
Decision

Runtime timezone behavior must be configuration-driven and must not be hardcoded to a specific real-world timezone.

Rationale

Scoring windows, score-day calculation, report elapsed-day cutoffs, and timestamp generation depend on timezone behavior. Hardcoding a timezone makes the product brittle and customer-specific.

Result

Runtime code now uses configured timezone access through:

src/ui/config.py
src/gymchallenge/runtime_config.py

Default timezone is now UTC, but real customer instances should always set GYM_TIMEZONE explicitly.

Carry-forward rule

Do not hardcode customer timezones in runtime code for reusable products.

2026-04-09 — Admin identity must be configured
Decision

Persisted admin identity must be configuration-driven and must not be hardcoded to a specific operator name.

Rationale

Corrections, system events, reports, and admin-facing text should reflect the configured customer/operator identity, not a one-off build assumption.

Result

Admin identity is now expected to come from:

ADMIN_NAME

Flask-context access uses:

src/ui/config.py

Non-Flask runtime access uses:

src/gymchallenge/runtime_config.py

Carry-forward rule

Do not hardcode operator/admin identity in reusable products.

2026-04-09 — Import standardization on src package paths
Decision

The project standard import style is now src... package imports.

Rationale

Mixed import styles created brittle execution behavior and required special handling in tests and command usage. Standardizing the import model reduces ambiguity and makes runtime behavior more predictable.

Result

Project imports were standardized on src... package paths.

CLI usage is now expected to use module form:

python3 -m src.main --help

Carry-forward rule

Keep import style consistent across the repo. Avoid mixed package import styles in reusable products.

2026-04-09 — Secret key precedence model
Decision

Flask secret key handling uses a clear precedence order:

environment variable
instance config
dev fallback
Rationale

Hosted deployment should prefer environment-provided secrets, while local QA and customer-specific local instances still need a practical configuration path.

Result

SECRET_KEY now supports:

environment override for hosted deployment
instance config for local/client instance setup
dev fallback for local development only

Carry-forward rule

Secrets should not be permanently hardcoded for hosted deployment.

2026-04-09 — Local QA remains the gate before hosted deployment
Decision

Hosted deployment is not the next step until the repaired config-driven build passes the next 7-day local QA cycle.

Rationale

The alpha test exposed real failures that were not caught by earlier testing. The repaired build must earn trust under another controlled local QA cycle before being treated as a hosted release candidate.

Result

Current release sequence remains:

local repair and validation
→ docs/configuration alignment
→ next 7-day local QA
→ hosted deployment preparation
→ client release

Carry-forward rule

Do not skip the second full QA cycle after meaningful correctness and runtime-configuration repairs.