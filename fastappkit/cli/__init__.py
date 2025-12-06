"""CLI module for fastappkit commands."""

from __future__ import annotations

# Import command modules to ensure they're registered
from fastappkit.cli import app, core, migrate  # noqa: F401

__all__ = ["app", "core", "migrate"]
