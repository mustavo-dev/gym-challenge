# Gym Challenge — System Design Summary

gym-challenge is structured in four layers:

1. CLI Layer
2. Domain Logic Layer
3. Storage Layer
4. Data Layer

## CLI Layer

The CLI entry point is located in:
src/main.py


It provides command interfaces for:

- participants
- memberships
- submissions
- corrections
- reports
- cycles
- system automation commands

## Domain Logic Layer

The domain logic layer implements the rules of the gym challenge.

Examples include:

- scoring rules
- missed-day penalties
- automatic inactivity detection
- automatic reactivation
- cycle timeline rules
- leaderboard generation

These rules must remain centralized in this layer.

## Storage Layer

Storage helpers manage JSON persistence.

They are responsible only for reading and writing data, not enforcing rules.

## Data Layer

All system data is stored locally in JSON files:

It provides command interfaces for:

- participants
- memberships
- submissions
- corrections
- reports
- cycles
- system automation commands

## Domain Logic Layer

The domain logic layer implements the rules of the gym challenge.

Examples include:

- scoring rules
- missed-day penalties
- automatic inactivity detection
- automatic reactivation
- cycle timeline rules
- leaderboard generation

These rules must remain centralized in this layer.

## Storage Layer

Storage helpers manage JSON persistence.

They are responsible only for reading and writing data, not enforcing rules.

## Data Layer

All system data is stored locally in JSON files:
data/
participants.json
memberships.json
submissions.json
corrections.json
membership_events.json
cycles.json


Exports are written to:
exports/


## Future UI Development

The future UI must call the same domain logic used by the CLI rather than reimplementing system rules.

Recommended architecture for the UI:
UI
 │
 ▼
Command / service layer
 │
 ▼
Domain logic
 │
 ▼
Storage


This ensures consistent behavior across all interfaces.
