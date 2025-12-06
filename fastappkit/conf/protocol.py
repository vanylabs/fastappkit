"""
Settings protocol - defines the interface for project settings.

Projects must define their own Settings class that implements this protocol.
"""

from __future__ import annotations

from typing import Protocol


class SettingsProtocol(Protocol):
    """
    Protocol defining required settings attributes.

    Projects should define their Settings class in core/config.py
    that has these attributes (typically using pydantic-settings BaseSettings).
    """

    # Database configuration
    DATABASE_URL: str

    # Application settings
    DEBUG: bool
