from __future__ import annotations

import secrets

def new_submission_id() -> str:
    # short + unique enough for local use
    return f"sub_{secrets.token_hex(4)}"

def new_correction_id() -> str:
    return f"corr_{secrets.token_hex(4)}"

def new_membership_event_id() -> str:
    return f"evt_{secrets.token_hex(4)}"
