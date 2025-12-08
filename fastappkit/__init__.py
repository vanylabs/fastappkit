"""
fastappkit - A toolkit for building FastAPI projects with apps.

Similar to Django apps, but supporting both internal and external pluggable apps.
"""

from __future__ import annotations

__version__ = "0.1.6"

from fastappkit.conf import SettingsProtocol, get_settings
from fastappkit.core.kit import FastAppKit

__all__ = [
    "FastAppKit",
    "SettingsProtocol",
    "get_settings",
]
