# Gym Challenge — Developer Architecture

This document describes the internal structure of the project for developers.


## Architectural Principles

The project follows a layered structure.

**CLI Layer**

Handles command parsing and user interaction.

**Domain Logic Layer**

Contains all business rules:

- scoring
- participation rules
- cycle logic
- membership timelines
- automation rules

**Storage Layer**

Handles reading and writing JSON data.

**Data Layer**

Local JSON files provide persistence.

## UI Integration Rule

Future UI components must interact with the **domain logic layer**, not directly with the storage layer.

This prevents duplication of business rules and ensures consistent behavior across CLI and UI systems.

┌─────────────────────────────────────────────────────────────┐
│                        CLI ENTRYPOINT                       │
│                         src/main.py                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     COMMAND FUNCTIONS                       │
│ participant / membership / submission / correction / cycle │
│ report / system apply-auto-inactive / auto-reactivate      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                     DOMAIN / RULES LAYER                    │
├─────────────────────────────────────────────────────────────┤
│ scoring_engine.py                                           │
│   - compute_daily_scores                                    │
│   - build_leaderboard                                       │
│   - detect_auto_inactive                                    │
│   - apply_auto_inactive                                     │
│   - reactivate_member                                       │
│                                                             │
│ membership_timeline.py                                      │
│   - build_active_day_map                                    │
│                                                             │
│ reactivation_ops.py                                         │
│   - detect_auto_reactivate                                  │
│                                                             │
│ cycle_timeline.py                                           │
│   - cycle_window_start / cycle_window_end                   │
│   - cycle_status                                            │
│   - cycle_overlaps_existing                                 │
│                                                             │
│ cycle_rules.py / scoring_time.py                            │
│   - score_day rules                                         │
│   - check-in window rules                                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      STORAGE HELPERS                        │
├─────────────────────────────────────────────────────────────┤
│ storage_json.py                                             │
│ storage_ops.py                                              │
│ participant_ops.py                                          │
│ cycle_ops.py                                                │
│ cycle_store.py                                              │
│ membership_store.py                                         │
│ membership_event_ops.py                                     │
│ membership_event_store.py                                   │
│ system_event_ops.py                                         │
│ id_ops.py                                                   │
│ data_paths.py                                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                         DATA FILES                          │
├─────────────────────────────────────────────────────────────┤
│ data/participants.json                                      │
│ data/memberships.json                                       │
│ data/submissions.json                                       │
│ data/corrections.json                                       │
│ data/membership_events.json                                 │
│ data/cycles.json                                            │
│ exports/*.csv                                               │
└─────────────────────────────────────────────────────────────┘
