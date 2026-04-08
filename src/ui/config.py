"""UI configuration helpers."""

from flask import current_app
from zoneinfo import ZoneInfo


def get_ui_timezone() -> ZoneInfo:
    """Return the configured UI timezone."""
    return ZoneInfo(current_app.config["GYM_TIMEZONE"])