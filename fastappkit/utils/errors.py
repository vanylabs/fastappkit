"""
Error message formatter - provides developer-friendly error messages.
"""

from __future__ import annotations

import traceback
from typing import Any


class ErrorFormatter:
    """Formats error messages for better developer experience."""

    def format_app_load_error(
        self,
        app_name: str,
        stage: str,
        error: Exception,
        manifest: dict[str, Any] | None = None,
        original_error: Exception | None = None,
    ) -> str:
        """
        Format a detailed error message for app loading failures.

        Args:
            app_name: Name or identifier of the app
            stage: Stage where failure occurred (resolve, manifest, entrypoint, register)
            error: The error that occurred
            manifest: Optional manifest dictionary (if available)
            original_error: Optional original exception

        Returns:
            Formatted error message string
        """
        lines = [
            f"❌ Failed to load app: {app_name}",
            f"   Stage: {stage}",
            "",
        ]

        # Add stage-specific context
        stage_context = self._get_stage_context(stage, app_name, manifest)
        if stage_context:
            lines.extend(stage_context)
            lines.append("")

        # Add error message
        error_msg = str(error)
        if error_msg:
            lines.append(f"Error: {error_msg}")
        else:
            lines.append(f"Error: {type(error).__name__}")

        # Add manifest snapshot if available
        if manifest:
            lines.append("")
            lines.append("Manifest snapshot:")
            for key, value in manifest.items():
                if key in [
                    "name",
                    "version",
                    "entrypoint",
                    "migrations",
                    "route_prefix",
                ]:
                    lines.append(f"  {key}: {value}")

        # Add traceback excerpt for debugging
        if original_error:
            lines.append("")
            lines.append("Traceback (most recent call last):")
            tb_lines = traceback.format_exception(
                type(original_error),
                original_error,
                original_error.__traceback__,
                limit=3,
            )
            lines.extend(["  " + line.rstrip() for line in tb_lines[-3:]])

        # Add suggested fixes
        suggestions = self._get_suggestions(stage, error, manifest)
        if suggestions:
            lines.append("")
            lines.append("Suggested fixes:")
            for suggestion in suggestions:
                lines.append(f"  • {suggestion}")

        return "\n".join(lines)

    def _get_stage_context(
        self, stage: str, app_name: str, manifest: dict[str, Any] | None
    ) -> list[str]:
        """Get context-specific information for each stage."""
        context = []

        if stage == "resolve":
            context.append(f"Could not resolve app '{app_name}'")
            context.append("Check:")
            context.append("  • Is the app path correct?")
            context.append("  • Is it a valid Python package?")
            context.append("  • Is it installed (for external apps)?")

        elif stage == "manifest":
            context.append(f"Could not load manifest for '{app_name}'")
            context.append("Check:")
            context.append("  • Does pyproject.toml exist?")
            context.append("  • Does it have [tool.fastappkit] section?")
            if manifest:
                context.append("  • Are required fields present?")

        elif stage == "entrypoint":
            entrypoint = manifest.get("entrypoint", "unknown") if manifest else "unknown"
            context.append(f"Could not load entrypoint: {entrypoint}")
            context.append("Check:")
            context.append("  • Is the entrypoint format correct? (module:function)")
            context.append("  • Does the module exist?")
            context.append("  • Does the function/class exist?")

        elif stage == "register":
            context.append(f"Could not execute registration for '{app_name}'")
            context.append("Check:")
            context.append("  • Does register() function exist?")
            context.append("  • Does it accept FastAPI app as parameter?")
            context.append("  • Are there any import errors in the app?")

        elif stage == "router":
            context.append(f"Could not mount router for '{app_name}'")
            context.append("Check:")
            context.append("  • Does register() return an APIRouter?")
            context.append("  • Is the route_prefix valid?")

        return context

    def _get_suggestions(
        self,
        stage: str,
        error: Exception,
        manifest: dict[str, Any] | None,
    ) -> list[str]:
        """Get suggested fixes based on error type and stage."""
        suggestions = []

        error_str = str(error).lower()
        error_type = type(error).__name__

        # Import errors
        if "import" in error_str or "ModuleNotFoundError" in error_type:
            suggestions.append("Check that all dependencies are installed")
            suggestions.append("Verify Python path includes the app directory")

        # File not found errors
        if "not found" in error_str or "FileNotFoundError" in error_type:
            if stage == "manifest":
                suggestions.append("Create pyproject.toml with [tool.fastappkit] section")
            elif stage == "resolve":
                suggestions.append("Verify the app path in fastappkit.toml")

        # Attribute errors
        if "AttributeError" in error_type:
            if stage == "entrypoint":
                suggestions.append("Verify the entrypoint function/class name is correct")
            elif stage == "register":
                suggestions.append("Check that register() function exists and is callable")

        # Type errors
        if "TypeError" in error_type:
            if stage == "register":
                suggestions.append("Ensure register() accepts exactly one parameter (FastAPI app)")

        # Missing migrations (for external apps)
        if "migrations" in error_str and stage == "manifest":
            suggestions.append("External apps must have a migrations/ folder")
            suggestions.append("Create migrations/env.py with proper configuration")

        # Generic suggestions
        if not suggestions:
            suggestions.append("Check the app's documentation")
            suggestions.append("Run 'fastappkit app validate <name>' for detailed validation")

        return suggestions

    def print_app_load_error(
        self,
        app_name: str,
        stage: str,
        error: Exception,
        manifest: dict[str, Any] | None = None,
        original_error: Exception | None = None,
    ) -> None:
        """
        Format and print an app load error using the output system.

        Args:
            app_name: Name or identifier of the app
            stage: Stage where failure occurred
            error: The error that occurred
            manifest: Optional manifest dictionary
            original_error: Optional original exception
        """
        # Lazy import to avoid circular dependency
        from fastappkit.cli.output import get_output

        output = get_output()
        formatted = self.format_app_load_error(app_name, stage, error, manifest, original_error)
        output.error(formatted)
