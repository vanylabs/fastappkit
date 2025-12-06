"""
Entrypoint loader - loads and executes app registration functions.
"""

from __future__ import annotations

import importlib
import inspect
from typing import Callable, cast

from fastappkit.exceptions import AppLoadError


class EntrypointLoader:
    """Loads app entrypoints (register functions or App classes)."""

    def load_entrypoint(self, entrypoint: str, app_module_name: str) -> Callable[..., object]:
        """
        Load entrypoint function or class from app.

        Args:
            entrypoint: Entrypoint string (e.g., "blog:register" or "blog:App")
            app_module_name: Module name where entrypoint is located

        Returns:
            Callable: Entrypoint function or class instance

        Raises:
            AppLoadError: If entrypoint cannot be loaded
        """
        try:
            # Import the module
            module = importlib.import_module(app_module_name)
        except ImportError as e:
            raise AppLoadError(
                app_module_name,
                "entrypoint",
                f"Failed to import module '{app_module_name}': {e}",
            ) from e

        # Parse entrypoint string (format: "module:function" or "module:Class")
        if ":" not in entrypoint:
            # If no colon, assume it's just the module name and look for "register" function
            entrypoint = f"{app_module_name}:register"

        module_path, attr_name = entrypoint.rsplit(":", 1)

        # If module_path is different from app_module_name, import that module
        if module_path != app_module_name:
            try:
                module = importlib.import_module(module_path)
            except ImportError as e:
                raise AppLoadError(
                    app_module_name,
                    "entrypoint",
                    f"Failed to import entrypoint module '{module_path}': {e}",
                ) from e

        # Get the attribute (function or class)
        if not hasattr(module, attr_name):
            raise AppLoadError(
                app_module_name,
                "entrypoint",
                f"Entrypoint '{attr_name}' not found in module '{module_path}'",
            )

        attr = getattr(module, attr_name)

        # If it's a class, instantiate it (with no args)
        if isinstance(attr, type):
            try:
                instance = attr()
                if not hasattr(instance, "register"):
                    raise AppLoadError(
                        app_module_name,
                        "entrypoint",
                        f"Class '{attr_name}' does not have a 'register' method",
                    )
                register_method = instance.register
                return cast(Callable[..., object], register_method)
            except Exception as e:
                raise AppLoadError(
                    app_module_name,
                    "entrypoint",
                    f"Failed to instantiate class '{attr_name}': {e}",
                ) from e

        # If it's a function, validate signature
        if not callable(attr):
            raise AppLoadError(
                app_module_name,
                "entrypoint",
                f"'{attr_name}' is not callable",
            )

        # Basic signature validation (should accept FastAPI app)
        try:
            sig = inspect.signature(attr)
            params = list(sig.parameters.keys())
            if len(params) < 1:
                raise AppLoadError(
                    app_module_name,
                    "entrypoint",
                    f"Entrypoint '{attr_name}' must accept at least one parameter (FastAPI app)",
                )
        except (ValueError, TypeError):
            # Can't inspect signature, but it's callable so assume it's OK
            pass

        return cast(Callable[..., object], attr)
