"""
Router assembly - mounts app routers to FastAPI application.
"""

from __future__ import annotations

from fastapi import FastAPI

from fastappkit.core.collision import RouteCollisionDetector
from fastappkit.core.registry import AppRegistry
from fastappkit.exceptions import AppLoadError


class RouterAssembler:
    """Assembles and mounts routers from apps."""

    def assemble(self, app: FastAPI, registry: AppRegistry) -> None:
        """
        Mount all app routers to FastAPI application.

        Args:
            app: FastAPI application instance
            registry: AppRegistry with loaded apps

        Note:
            Apps can provide routers in two ways:
            1. Return APIRouter from register() - mounted here with prefix
            2. Mount routers themselves in register() - skipped here

            If an app returns a router, it will be mounted with the prefix
            from manifest (route_prefix) or default /<appname>.
            Empty prefix (route_prefix = "") is supported.

            After mounting, route collisions are detected and warnings emitted.
        """
        for app_metadata in registry.list():
            # Only mount routers that were returned from register()
            # If router is None, assume app mounted itself
            if app_metadata.router:
                prefix = app_metadata.prefix
                try:
                    app.include_router(app_metadata.router, prefix=prefix)
                except Exception as e:
                    raise AppLoadError(
                        app_metadata.name,
                        "router",
                        f"Failed to mount router with prefix '{prefix}': {e}",
                        original_error=e,
                    ) from e

        # Check for route collisions (warnings only, not fatal)
        detector = RouteCollisionDetector()
        detector.check_and_warn(app, registry, warn=True)
