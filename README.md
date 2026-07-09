# gym-challenge

**Current Version:** 1.2.0-dev
**Current Status:** Post-v1.2 acceptance trial. Known scoring and membership lifecycle defects remain under investigation; not ready for release.

`gym-challenge` is a Python CLI and Flask UI application for managing recurring fitness challenges. It handles participants, cycle membership, daily score submissions, missed-day penalties, inactive and reactivation behavior, admin corrections, leaderboard reporting, and system history.

The project began as a way to replace a manual tracking process with a tool built around the actual rules and workflow of the challenge. Development has included multiple week-long acceptance trials used to compare program behavior against expected real-world outcomes, identify defects, and refine requirements before release.

## Current Capabilities

The system currently includes:

* Participant management
* Challenge cycle management
* Cycle membership management
* Daily participant score submission
* Missed-submission penalties
* Inactive and reactivation lifecycle behavior
* Admin corrections
* Leaderboard report generation
* System archive and restore actions
* Administrative history and event visibility
* Configuration-driven challenge, gym, admin, and timezone values

## Current Development State

Version `1.2.0-dev` has completed a seven-day acceptance trial focused primarily on validating inactive and reactivation behavior after repairs made following the v1.1 beta test.

The trial exposed additional scoring and membership-state defects that still need investigation and repair. The project is therefore not ready for real release or hosted deployment.

Current priorities are:

1. Investigate and repair defects discovered during the v1.2 acceptance trial.
2. Improve admin visibility into participant submission and membership state.
3. Complete another validation cycle after repairs.
4. Prepare for hosted deployment and multi-device testing.
5. Complete final documentation and release readiness work.

## Acceptance Testing

Development has included three major acceptance-testing phases:

### v1.0 — Alpha Trial

The first full week-long trial tested the initial CLI and local Flask UI implementation. It exposed multiple issues involving scoring, inactive participants, cycle behavior, corrections, and administrative workflow.

### v1.1 — Beta Trial

The second week-long trial validated repairs made after alpha testing. It exposed a major lifecycle defect: participants were not automatically becoming inactive during normal UI operation because the lifecycle logic existed only as manual CLI commands.

### v1.2 — Release-Candidate Validation Trial

The third seven-day trial tested the repaired inactive and reactivation lifecycle. It confirmed some corrected behavior while exposing additional membership-state and leaderboard inconsistencies that remain under investigation.

Detailed trial plans, exported leaderboards, screenshots, and manual verification documents are preserved under:

* `tests/v1.0_Acceptance_Test_Data/`
* `tests/v1.1_Acceptance_Test_Data/`
* `tests/v1.2_Acceptance_Trial_Data/`

These artifacts are intentionally retained as development and validation evidence.

## Configuration

Customer-specific values are loaded from:

```text
instance/config.py
```

A safe example configuration is provided at:

```text
instance/config.example.py
```

Example:

```python
CHALLENGE_NAME = "Spring Nutrition Challenge"
GYM_NAME = "Example Gym"
ADMIN_NAME = "Example Admin"
GYM_TIMEZONE = "America/New_York"
SECRET_KEY = "replace-with-a-long-random-secret"
```

The real `instance/config.py` file is excluded from Git and should not be committed.

Configuration controls:

* `CHALLENGE_NAME` — challenge identity displayed in the UI
* `GYM_NAME` — gym identity displayed in admin views
* `ADMIN_NAME` — admin-facing identity and persisted admin metadata
* `GYM_TIMEZONE` — scoring-window calculations, score-day logic, report cutoffs, and runtime timestamps
* `SECRET_KEY` — Flask session and flash-message security

For the complete configuration model, see [`docs/configuration-and-release.md`](docs/configuration-and-release.md).

## Local Setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a local configuration file:

```bash
cp instance/config.example.py instance/config.py
```

Then edit `instance/config.py` with the appropriate local values.

## Running the Application

Run the CLI:

```bash
python3 -m src.main --help
```

Run the Flask UI:

```bash
python3 run_ui.py
```

## Testing

The repository includes automated unit and regression tests covering scoring, cycles, memberships, corrections, submissions, configuration, lifecycle behavior, storage, leaderboard generation, and UI services.

A targeted validation pack used during recent repair work can be run with:

```bash
python3 -m unittest \
  tests.test_ui_alpha_regressions \
  tests.test_ui_app_config \
  tests.test_ui_config_helpers \
  tests.test_submission_ui_service \
  tests.test_runtime_config
```

Acceptance-test evidence is preserved separately from the automated test suite so actual observed behavior can be compared against intended requirements.

## Project Structure

```text
gym-challenge/
├── data/                  Runtime JSON data location
├── docs/                  Requirements, architecture, and release documentation
├── exports/               Generated leaderboard exports
├── instance/              Local configuration and safe example template
├── scripts/               Helper scripts
├── src/
│   ├── gymchallenge/      Core domain and scoring logic
│   └── ui/                Flask application, routes, services, templates, and static files
└── tests/                 Automated tests and acceptance-trial evidence
```

Runtime JSON files, generated CSV exports, and the real local configuration are excluded from Git.

## Supporting Documentation

* [`docs/00-requirements.md`](docs/00-requirements.md)
* [`docs/01-data-model.md`](docs/01-data-model.md)
* [`docs/02-cli-spec.md`](docs/02-cli-spec.md)
* [`docs/architecture_overview.md`](docs/architecture_overview.md)
* [`docs/configuration-and-release.md`](docs/configuration-and-release.md)
* [`docs/ui-architecture.md`](docs/ui-architecture.md)
* [`docs/ui-runbook.md`](docs/ui-runbook.md)

## Release Direction

The current development path is:

```text
v1.2 defect investigation and repair
→ local regression validation
→ next acceptance trial
→ hosted deployment preparation
→ multi-device hosted validation
→ release readiness
```

The long-term goal is for standard deployment to require configuration changes rather than customer-specific edits to core application logic.
