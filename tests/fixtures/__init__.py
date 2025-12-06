"""
Centralized test fixtures and factories for fastappkit tests.

This module provides structured, reusable test data builders to avoid
duplication and ensure consistency across tests.
"""

from tests.fixtures.app_factory import (
    AppFactory,
    InternalAppFactory,
    ExternalAppFactory,
)
from tests.fixtures.config_factory import ConfigFactory
from tests.fixtures.project_factory import ProjectFactory

__all__ = [
    "AppFactory",
    "InternalAppFactory",
    "ExternalAppFactory",
    "ConfigFactory",
    "ProjectFactory",
]
