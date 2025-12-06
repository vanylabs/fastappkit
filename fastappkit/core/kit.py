"""
FastAppKit main class - orchestrates app loading and FastAPI app creation.
"""

from __future__ import annotations

from fastapi import FastAPI

from fastappkit.conf import SettingsProtocol, set_settings
from fastappkit.core.loader import AppLoader
from fastappkit.core.router import RouterAssembler


class FastAppKit:
    """
    Main FastAppKit class that manages settings and app loading.

    Usage:
        from core.config import Settings

        settings = Settings()
        kit = FastAppKit(settings=settings)
        app = kit.create_app()
    """

    def __init__(self, settings: SettingsProtocol):
        """
        Initialize FastAppKit with settings.

        Args:
            settings: Settings instance from project's core.config module
        """
        self.settings = settings
        # Set global settings accessor
        set_settings(settings)

    def create_app(self) -> FastAPI:
        """
        Create and configure FastAPI application.

        This will:
        1. Create FastAPI app instance
        2. Load apps via AppLoader
        3. Execute app registrations
        4. Mount routers
        5. Return configured app

        Returns:
            FastAPI: Configured FastAPI application
        """
        app = FastAPI(
            title="FastAppKit Application",
            debug=self.settings.DEBUG,
        )

        # Load apps
        loader = AppLoader()
        registry = loader.load_all()

        # Execute registrations (this calls register() functions which create routers)
        loader.execute_registrations(app)

        # Mount routers
        assembler = RouterAssembler()
        assembler.assemble(app, registry)

        return app
