"""UI configuration helpers."""

from flask import current_app, has_app_context
from zoneinfo import ZoneInfo


def get_ui_timezone() -> ZoneInfo:
    """Return the configured UI timezone."""
    tz_name = "UTC"

    if has_app_context():
        tz_name = current_app.config.get("GYM_TIMEZONE", "UTC")

    return ZoneInfo(tz_name)

def get_admin_actor_name() -> str:
    """Return the configured admin actor name."""
    if has_app_context():
        return current_app.config.get("ADMIN_NAME", "Admin")

    return "Admin"