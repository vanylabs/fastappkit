"""
App factory for creating test apps (internal and external).

Provides structured builders for creating test app structures
with consistent patterns.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter


class AppFactory:
    """Base factory for creating test apps."""

    @staticmethod
    def create_register_function(
        router: APIRouter | None = None,
        prefix: str = "",
        return_router: bool = True,
    ) -> str:
        """
        Generate register function code.

        Args:
            router: Optional router to include
            prefix: Route prefix
            return_router: Whether register() should return router

        Returns:
            Python code string for register function
        """
        if router is None:
            router_code = "router = APIRouter()"
        else:
            router_code = f"router = {router}"

        if return_router:
            return_code = "return router"
        else:
            return_code = "pass"

        return f'''"""Test app register function."""
from fastapi import APIRouter, FastAPI

{router_code}

@router.get("/")
def hello():
    return {{"message": "Hello from test app"}}

def register(app: FastAPI):
    """Register the app."""
    app.include_router(router, prefix="{prefix}")
    {return_code}
'''

    @staticmethod
    def create_models_code() -> str:
        """Generate models.py code."""
        return '''"""Test models."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TestModel(Base):
    __tablename__ = "test"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
'''


class InternalAppFactory(AppFactory):
    """Factory for creating internal test apps."""

    @staticmethod
    def create(
        project_root: Path,
        app_name: str,
        with_models: bool = True,
        with_migrations: bool = False,
        router_prefix: str = "",
        return_router: bool = True,
    ) -> Path:
        """
        Create an internal app structure.

        Args:
            project_root: Project root directory
            app_name: Name of the app
            with_models: Whether to create models.py
            with_migrations: Whether to create migrations directory
            router_prefix: Prefix for router
            return_router: Whether register() returns router

        Returns:
            Path to created app directory
        """
        app_path = project_root / "apps" / app_name
        app_path.mkdir(parents=True, exist_ok=True)

        # Create __init__.py with register function
        init_content = AppFactory.create_register_function(
            prefix=router_prefix,
            return_router=return_router,
        )
        (app_path / "__init__.py").write_text(init_content)

        # Create models.py if requested
        if with_models:
            models_content = AppFactory.create_models_code()
            (app_path / "models.py").write_text(models_content)

        # Create migrations directory if requested
        if with_migrations:
            migrations_path = app_path / "migrations"
            migrations_path.mkdir(exist_ok=True)
            (migrations_path / "versions").mkdir(exist_ok=True)

        return app_path

    @staticmethod
    def create_minimal(project_root: Path, app_name: str) -> Path:
        """Create minimal internal app (just __init__.py)."""
        return InternalAppFactory.create(
            project_root=project_root,
            app_name=app_name,
            with_models=False,
            with_migrations=False,
        )


class ExternalAppFactory(AppFactory):
    """Factory for creating external test apps."""

    @staticmethod
    def create(
        base_path: Path,
        package_name: str,
        app_name: str | None = None,
        version: str = "0.1.0",
        entrypoint: str | None = None,
        migrations: str | None = "migrations",
        with_models: bool = True,
        with_migrations: bool = False,
        route_prefix: str | None = None,
    ) -> Path:
        """
        Create an external app package structure.

        Args:
            base_path: Base directory for the package
            package_name: Python package name
            app_name: App name (defaults to package_name)
            version: App version
            entrypoint: Entrypoint string (defaults to package_name:register)
            migrations: Migrations path in manifest
            with_models: Whether to create models.py
            with_migrations: Whether to create migrations directory
            route_prefix: Route prefix in manifest

        Returns:
            Path to created package directory
        """
        if app_name is None:
            app_name = package_name

        if entrypoint is None:
            entrypoint = f"{package_name}:register"

        package_path = base_path / package_name
        package_path.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        init_content = AppFactory.create_register_function()
        (package_path / "__init__.py").write_text(init_content)

        # Create models.py if requested
        if with_models:
            models_content = AppFactory.create_models_code()
            (package_path / "models.py").write_text(models_content)

        # Create migrations directory if requested
        if with_migrations and migrations:
            migrations_path = package_path / migrations
            migrations_path.mkdir(parents=True, exist_ok=True)
            (migrations_path / "versions").mkdir(exist_ok=True)

        # Create fastappkit.toml
        manifest: dict[str, Any] = {
            "name": app_name,
            "version": version,
            "entrypoint": entrypoint,
        }
        if migrations:
            manifest["migrations"] = migrations
        if route_prefix is not None:
            manifest["route_prefix"] = route_prefix

        toml_content = "[tool.fastappkit]\n"
        for key, value in manifest.items():
            if isinstance(value, str):
                toml_content += f'{key} = "{value}"\n'
            else:
                toml_content += f"{key} = {value}\n"

        (package_path / "fastappkit.toml").write_text(toml_content)

        # Create pyproject.toml
        pyproject_content = f"""[tool.poetry]
name = "{package_name}"
version = "{version}"

[tool.fastappkit]
name = "{app_name}"
version = "{version}"
entrypoint = "{entrypoint}"
"""
        if migrations:
            pyproject_content += f'migrations = "{migrations}"\n'

        (base_path / "pyproject.toml").write_text(pyproject_content)

        return package_path
