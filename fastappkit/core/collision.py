"""
Route collision detector - detects overlapping routes and emits warnings.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from fastapi import FastAPI
from fastapi.routing import APIRoute

from fastappkit.cli.output import get_output
from fastappkit.core.registry import AppRegistry


class RouteCollisionDetector:
    """Detects route collisions in mounted routers."""

    def detect_collisions(self, app: FastAPI, registry: AppRegistry) -> list[dict[str, Any]]:
        """
        Detect route collisions in the FastAPI application.

        Scenarios detected:
        - Same path + method from multiple apps: Two apps define GET /posts
        - Overlapping prefixes: App1 has /api, App2 has /api/v1 (both match /api/v1/posts)
        - Empty prefix conflicts: Multiple apps with prefix="" mounting at root
        - Root prefix conflicts: Multiple apps with prefix="/" mounting at root
        - Manual mounting: Apps that mount routes in register() are still detected

        Detection method:
        1. Iterates through all routes in app.routes
        2. For each APIRoute, determines which app it belongs to via _find_app_for_route()
        3. Groups routes by (path, method) tuple
        4. Identifies collisions where same (path, method) appears from multiple apps

        Limitations:
        - Routes marked as "unknown" are still checked for collisions
        - Cannot detect collisions between routes mounted outside fastappkit
        - Prefix matching is less reliable than module path matching

        Args:
            app: FastAPI application instance
            registry: AppRegistry with loaded apps

        Returns:
            List of collision dictionaries with details:
            {
                "path": "/path/to/route",
                "method": "GET",
                "apps": ["app1", "app2"],  # List of app names
                "suggestion": "Change route_prefix for one of the apps"
            }
        """
        collisions: list[dict[str, str]] = []

        # Extract all routes from the app
        route_map: dict[tuple[str, str], list[str]] = defaultdict(list)

        # Walk through all routes in the app
        for route in app.routes:
            if isinstance(route, APIRoute):
                # Get the full path (including prefix)
                path = route.path
                # Get HTTP methods
                methods = route.methods if hasattr(route, "methods") else {"GET"}

                # Find which app this route belongs to
                app_name = self._find_app_for_route(route, registry)

                # Record this route
                for method in methods:
                    key = (path, method)
                    route_map[key].append(app_name)

        # Check for collisions (same path + method from multiple apps)
        for (path, method), apps in route_map.items():
            # Remove duplicates while preserving order
            unique_apps = list(dict.fromkeys(apps))
            if len(unique_apps) > 1:
                collision_dict: dict[str, Any] = {
                    "path": path,
                    "method": method,
                    "apps": unique_apps,
                    "suggestion": self._generate_suggestion(unique_apps, registry),
                }
                collisions.append(collision_dict)

        return collisions

    def _find_app_for_route(self, route: APIRoute, registry: AppRegistry) -> str:
        """
        Find which app a route belongs to by checking route endpoint location.

        Uses two methods in order:
        1. Module path matching (most reliable): Matches endpoint's __module__ to app's import_path
        2. Prefix matching (fallback): Matches route.path to app's route_prefix

        Scenarios handled:
        - Internal apps: "apps.blog.router" endpoint matches "apps.blog" import_path
        - External apps: "payments.router" endpoint matches "payments" import_path
        - Nested modules: "apps.blog.api.v1" matches "apps.blog" (longest match wins)
        - Prefix conflicts: "/api/v1" matches before "/api" (longest prefix wins)
        - Empty prefix (""): Apps with empty prefix are matched via module path only
        - Root prefix ("/"): Apps with root prefix are matched via module path only
        - Apps that mount themselves: Routes mounted manually in register() are detected via module path
        - False positive prevention: "app2.router" won't match "app" import_path (uses dot boundary check)

        Args:
            route: APIRoute instance
            registry: AppRegistry with loaded apps

        Returns:
            App name or "unknown" if cannot determine
        """
        # Method 1: Check route endpoint's module path (most reliable)
        if hasattr(route, "endpoint"):
            endpoint = route.endpoint
            if endpoint is not None:
                # Get the module where the endpoint function is defined
                if hasattr(endpoint, "__module__"):
                    module_path = endpoint.__module__
                    # Sort apps by longest import_path first to avoid false matches
                    # e.g., "app2" should match before "app" to avoid "app2.router" matching "app"
                    apps_sorted = sorted(
                        registry.list(),
                        key=lambda a: len(a.import_path) if a.import_path else 0,
                        reverse=True,
                    )
                    for app_metadata in apps_sorted:
                        if app_metadata.import_path:
                            # Check if module path starts with app's import path
                            # Use exact match or ensure dot boundary to avoid false matches
                            if module_path == app_metadata.import_path:
                                return app_metadata.name
                            elif module_path.startswith(app_metadata.import_path + "."):
                                return app_metadata.name

        # Method 2: Fallback to prefix matching (less reliable)
        # Sort by longest prefix first to handle nested prefixes correctly
        # e.g., "/api/v1" should match before "/api"
        # Skip empty prefix "" and root prefix "/" as they're too ambiguous
        apps_with_prefix = [
            app for app in registry.list() if app.prefix and app.prefix != "/" and app.prefix != ""
        ]
        apps_sorted = sorted(
            apps_with_prefix,
            key=lambda a: len(a.prefix),
            reverse=True,
        )

        for app_metadata in apps_sorted:
            # Check if route path starts with app prefix
            # For exact prefix match, also check next character is / or end of string
            prefix = app_metadata.prefix
            if route.path == prefix or route.path.startswith(prefix + "/"):
                return app_metadata.name

        return "unknown"

    def _generate_suggestion(self, apps: list[str], registry: AppRegistry) -> str:
        """
        Generate a suggestion for resolving the collision.

        Args:
            apps: List of app names with collision
            registry: AppRegistry with loaded apps

        Returns:
            Suggestion string
        """
        if len(apps) == 2:
            app1, app2 = apps
            app1_metadata = registry.get(app1)
            app2_metadata = registry.get(app2)

            if app1_metadata and app2_metadata:
                return (
                    f"Change route_prefix for '{app1}' (current: {app1_metadata.prefix}) "
                    f"or '{app2}' (current: {app2_metadata.prefix}) in their manifests"
                )

        return "Review route_prefix settings in app manifests to avoid conflicts"

    def check_and_warn(
        self, app: FastAPI, registry: AppRegistry, warn: bool = True
    ) -> list[dict[str, str]]:
        """
        Check for collisions and emit warnings if found.

        Args:
            app: FastAPI application instance
            registry: AppRegistry with loaded apps
            warn: If True, emit warnings to output. If False, return silently.

        Returns:
            List of collision dictionaries
        """
        collisions = self.detect_collisions(app, registry)

        if collisions and warn:
            output = get_output()

            # Group collisions by app pairs for better readability
            app_collisions: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
            for collision in collisions:
                apps_tuple = tuple(sorted(collision["apps"]))
                app_collisions[apps_tuple].append(collision)

            output.warning("\n" + "=" * 70)
            output.warning("⚠️  ROUTE COLLISIONS DETECTED")
            output.warning("=" * 70)

            for apps_tuple, app_collisions_list in app_collisions.items():
                apps_str = " and ".join(f"'{app}'" for app in apps_tuple)
                output.warning(f"\n🔴 Collision between apps: {apps_str}")

                # Get app metadata for better suggestions
                app1_metadata = registry.get(apps_tuple[0])
                app2_metadata = registry.get(apps_tuple[1]) if len(apps_tuple) > 1 else None

                if app1_metadata and app2_metadata:
                    output.warning(f"   App '{apps_tuple[0]}' uses prefix: {app1_metadata.prefix}")
                    output.warning(f"   App '{apps_tuple[1]}' uses prefix: {app2_metadata.prefix}")

                # Show all conflicting routes
                output.warning(f"\n   Conflicting routes ({len(app_collisions_list)} found):")
                for collision in app_collisions_list:
                    output.warning(f"     • {collision['method']:6s} {collision['path']}")

                # Show suggestion
                if app1_metadata and app2_metadata:
                    output.warning("\n   💡 Fix: Change route_prefix for one of the apps:")
                    output.warning(
                        f"      - Update '{apps_tuple[0]}' manifest: route_prefix = \"/{apps_tuple[0]}\""
                    )
                    output.warning(
                        f"      - Or update '{apps_tuple[1]}' manifest: route_prefix = \"/{apps_tuple[1]}\""
                    )
                else:
                    if app_collisions_list:
                        output.warning(f"\n   💡 Fix: {app_collisions_list[0]['suggestion']}")

            output.warning("\n" + "-" * 70)
            output.warning("⚠️  Note: FastAPI will use the first matching route.")
            output.warning("   Route collisions are developer responsibility.")
            output.warning("=" * 70 + "\n")

        return collisions
