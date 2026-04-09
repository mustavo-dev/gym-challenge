"""Shared runtime configuration helpers for non-Flask code."""

from __future__ import annotations

import os
from runpy import run_path
from zoneinfo import ZoneInfo


def get_runtime_timezone(instance_path: str | None = None) -> ZoneInfo:
    """Return the configured runtime timezone from instance/config.py or UTC by default."""
    tz_name = "UTC"

    if instance_path is None:
        instance_path = os.path.join(os.getcwd(), "instance")

    config_path = os.path.join(instance_path, "config.py")

    if os.path.exists(config_path):
        config_values = run_path(config_path)
        tz_name = config_values.get("GYM_TIMEZONE", tz_name)

    return ZoneInfo(tz_name)

def get_runtime_admin_name(instance_path: str | None = None) -> str:
    """Return the configured admin name from instance/config.py or Admin by default."""
    admin_name = "Admin"

    if instance_path is None:
        instance_path = os.path.join(os.getcwd(), "instance")

    config_path = os.path.join(instance_path, "config.py")

    if os.path.exists(config_path):
        config_values = run_path(config_path)
        admin_name = config_values.get("ADMIN_NAME", admin_name)

    return admin_name