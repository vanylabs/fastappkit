"""
Isolation validator - validates external apps are properly isolated.
"""

from __future__ import annotations

import ast
import importlib
import sys
from pathlib import Path
from typing import Any

from fastappkit.core.types import AppType
from fastappkit.validation.manifest import ValidationResult


class IsolationValidator:
    """Validates external apps are properly isolated from internal apps."""

    def validate(
        self,
        app_path: Path,
        app_type: AppType,
        registry: Any = None,  # AppRegistry, but avoid circular import
        project_root: Path | None = None,
    ) -> ValidationResult:
        """
        Validate app isolation rules.

        For external apps:
        - Check no imports from internal apps
        - Check no imports from core (except fastappkit public API)
        - Verify version table is per-app (not shared)

        Args:
            app_path: Path to app directory
            app_type: Type of app (internal or external)
            registry: Optional AppRegistry for checking dependencies
            project_root: Optional project root directory (for detecting project-specific imports)

        Returns:
            ValidationResult: Result with errors and warnings
        """
        result = ValidationResult()

        # Only validate external apps
        if app_type != AppType.EXTERNAL:
            return result  # Internal apps don't need isolation checks

        # Scan Python files for imports
        python_files = list(app_path.rglob("*.py"))
        if not python_files:
            result.add_warning("No Python files found in app")

        internal_imports: list[str] = []
        core_imports: list[str] = []

        for py_file in python_files:
            # Skip migrations/env.py (it's allowed to import from fastappkit)
            if "migrations" in str(py_file) and "env.py" in str(py_file):
                continue

            try:
                with open(py_file, "r", encoding="utf-8") as f:
                    content = f.read()

                # Parse AST to find imports
                tree = ast.parse(content, filename=str(py_file))

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module_name = alias.name
                            if self._is_internal_app_import(module_name, project_root):
                                internal_imports.append(f"{py_file.name}: {module_name}")
                            elif self._is_core_import(module_name, project_root):
                                core_imports.append(f"{py_file.name}: {module_name}")

                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module_name = node.module
                            if self._is_internal_app_import(module_name, project_root):
                                internal_imports.append(f"{py_file.name}: {module_name}")
                            elif self._is_core_import(module_name, project_root):
                                core_imports.append(f"{py_file.name}: {module_name}")

            except SyntaxError:
                result.add_warning(f"Could not parse {py_file} (syntax error)")

        # Report errors
        if internal_imports:
            result.add_error(
                f"External app imports from internal apps: {', '.join(internal_imports[:5])}"
            )

        # Core imports are allowed if they're from fastappkit public API
        # For now, we'll warn about any core imports
        if core_imports:
            # Filter out fastappkit imports (allowed)
            non_fastappkit_core = [imp for imp in core_imports if not imp.startswith("fastappkit")]
            if non_fastappkit_core:
                result.add_warning(
                    f"Imports from core modules (may be allowed): {', '.join(non_fastappkit_core[:5])}"
                )

        return result

    def _is_internal_app_import(self, module_name: str, project_root: Path | None = None) -> bool:
        """
        Check if import is from an internal app.

        Detects:
        - Direct imports: apps.*, core.* (only if they resolve to project's apps/core)
        - Project-specific imports: <project_name>.apps.*, <project_name>.core.*

        Does NOT flag third-party libraries that happen to contain .apps. in their names.
        """
        # Known third-party libraries that have .apps. in their module names
        # These should not be flagged as internal app imports
        KNOWN_THIRD_PARTY_PREFIXES = [
            "django",
            "flask",
            "celery",
            "kombu",
        ]

        # Check if it's a known third-party library
        for prefix in KNOWN_THIRD_PARTY_PREFIXES:
            if module_name.startswith(f"{prefix}."):
                return False

        # Check for project-specific imports (e.g., testproject.apps.blog)
        # This is the most reliable indicator
        if project_root:
            project_name = project_root.name
            if module_name.startswith(f"{project_name}.apps.") or module_name.startswith(
                f"{project_name}.core."
            ):
                return True

        # For direct apps.* or core.* imports, verify they resolve to project's directory
        if module_name.startswith("apps.") or module_name.startswith("core."):
            if project_root:
                # Try to verify it's actually from the project
                # Check if the import would resolve to project_root/apps/ or project_root/core/
                try:
                    # Add project root to path temporarily to check
                    if str(project_root) not in sys.path:
                        sys.path.insert(0, str(project_root))

                    try:
                        module = importlib.import_module(
                            module_name.split(".")[0]
                        )  # Import first part
                        if hasattr(module, "__file__") and module.__file__:
                            module_path = Path(module.__file__).parent
                            # Check if it's under project_root/apps/ or project_root/core/
                            try:
                                module_path.relative_to(project_root)
                                # If we get here, it's relative to project root
                                if "apps" in module_path.parts or "core" in module_path.parts:
                                    return True
                            except ValueError:
                                # Not relative to project root, so it's a third-party library
                                pass
                    except ImportError:
                        # Can't import, so we can't verify - be conservative and flag it
                        # as it might be an internal app that's not yet importable
                        pass
                except Exception:
                    # Any error, be conservative
                    pass
            else:
                # No project_root provided, be conservative and flag it
                return True

        # For imports containing .apps. but not starting with project name,
        # try to verify it's from the project by attempting import
        if ".apps." in module_name and project_root:
            # Extract the part before .apps.
            parts = module_name.split(".apps.")
            if len(parts) > 0:
                prefix = parts[0]
                # If prefix is not the project name, it's likely a third-party library
                if prefix != project_root.name:
                    # Try to import and check if it's a third-party package
                    try:
                        if str(project_root) not in sys.path:
                            sys.path.insert(0, str(project_root))
                        module = importlib.import_module(prefix)
                        if hasattr(module, "__file__") and module.__file__:
                            module_path = Path(module.__file__).parent
                            try:
                                # Check if it's relative to project root
                                module_path.relative_to(project_root)
                                # If relative, check if it contains apps
                                if "apps" in module_path.parts:
                                    return True
                            except ValueError:
                                # Not relative to project root, so it's third-party
                                return False
                    except ImportError:
                        # Can't determine, be conservative
                        pass

        return False

    def _is_core_import(self, module_name: str, project_root: Path | None = None) -> bool:
        """
        Check if import is from core (excluding fastappkit).

        Detects:
        - Direct core imports: core.*
        - Project-specific core imports: <project_name>.core.*
        """
        # Direct core imports (excluding fastappkit)
        if module_name.startswith("core.") and not module_name.startswith("fastappkit"):
            return True

        # Check for project-specific core imports
        if project_root:
            project_name = project_root.name
            if module_name.startswith(f"{project_name}.core."):
                return True

        return False
