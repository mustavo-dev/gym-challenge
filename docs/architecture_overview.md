# Gym Challenge — System Architecture (Overview)

This diagram shows the high-level structure of the gym-challenge system.

## Summary

The system is organized into four logical layers:

1. CLI command interface
2. domain logic and rules
3. storage helpers
4. JSON data files

The CLI interacts only with domain logic.  
Domain logic handles all business rules before data is written to storage.

This structure ensures consistent behavior across CLI commands and future UI integrations.

                    gym-challenge
                         │
                         ▼
                  CLI Command Layer
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
     ▼                   ▼                   ▼
 Participant        Cycle Commands      Report / System
 Commands                                Automation
     │                   │                   │
     └──────────────┬────┴────┬─────────────┘
                    ▼         ▼
              Domain Logic / Rules Engine
                    │
    ┌───────────────┼─────────────────────────────────────┐
    │               │                 │                   │
    ▼               ▼                 ▼                   ▼
 Scoring Engine   Membership       Cycle Timeline     Reactivation /
                  Timeline         + Status Logic     Auto-Inactive Logic
    │               │                 │                   │
    └───────────────┴─────────────────┴───────────────────┘
                            │
                            ▼
                     Storage / JSON Layer
                            │
    ┌───────────────┬───────────────┬───────────────┬───────────────┐
    │               │               │               │               │
    ▼               ▼               ▼               ▼               ▼
participants   memberships     submissions    corrections    membership_events
.json          .json           .json          .json          .json
                            │
                            ▼
                         cycles.json
                            │
                            ▼
                         exports/
                    leaderboard CSV files
