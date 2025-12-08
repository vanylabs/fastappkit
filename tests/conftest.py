"""
Pytest configuration and fixtures for fastappkit tests.
"""

import os
import tempfile
from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from pydantic_settings import BaseSettings, SettingsConfigDict

from fastappkit.conf import set_settings
from fastappkit.core.kit import FastAppKit


class TestSettings(BaseSettings):
    """Test settings class that implements SettingsProtocol."""

    DATABASE_URL: str = "sqlite:///:memory:"
    DEBUG: bool = True
    SECRET_KEY: str = "test-secret-key"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    RELOAD: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@pytest.fixture
def temp_project() -> Generator[Path, None, None]:
    """
    Create a temporary project directory for testing.

    Yields:
        Path to temporary project directory
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test_project"
        project_path.mkdir()

        # Create basic project structure
        (project_path / "core").mkdir()
        (project_path / "core" / "db").mkdir()
        (project_path / "core" / "db" / "migrations").mkdir()
        (project_path / "core" / "db" / "migrations" / "versions").mkdir()
        (project_path / "apps").mkdir()

        # Create fastappkit.toml
        config_content = """[tool.fastappkit]
apps = []
"""
        (project_path / "fastappkit.toml").write_text(config_content)

        # Create .env
        env_content = """DATABASE_URL=sqlite:///:memory:
DEBUG=true
"""
        (project_path / ".env").write_text(env_content)

        yield project_path


@pytest.fixture
def test_settings() -> TestSettings:
    """
    Create test settings with in-memory SQLite database.

    Returns:
        TestSettings instance for testing
    """
    return TestSettings(
        DATABASE_URL="sqlite:///:memory:",
        DEBUG=True,
    )


@pytest.fixture
def test_db(test_settings: TestSettings) -> Generator[None, None, None]:
    """
    Setup test database connection.

    Args:
        test_settings: Test settings fixture

    Yields:
        None (database is available via get_settings())
    """
    # Set global settings
    set_settings(test_settings)
    yield
    # Cleanup handled by Settings


@pytest.fixture
def sample_app(test_settings: TestSettings, temp_project: Path) -> Generator[Path, None, None]:
    """
    Create a sample internal app for testing.

    Args:
        test_settings: Test settings fixture
        temp_project: Temporary project directory

    Yields:
        Path to sample app directory
    """
    app_path = temp_project / "apps" / "sample"
    app_path.mkdir()

    # Create __init__.py with register function
    init_content = '''"""Sample app for testing."""
from fastapi import APIRouter, FastAPI

router = APIRouter()

@router.get("/")
def hello():
    return {"message": "Hello from sample app"}

def register(app: FastAPI):
    """Register the app."""
    app.include_router(router, prefix="/sample")
    return router
'''
    (app_path / "__init__.py").write_text(init_content)

    # Create models.py
    models_content = '''"""Sample models."""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class SampleModel(Base):
    __tablename__ = "sample"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
'''
    (app_path / "models.py").write_text(models_content)

    # Update fastappkit.toml
    config_path = temp_project / "fastappkit.toml"
    config_content = """[tool.fastappkit]
apps = ["apps.sample"]
"""
    config_path.write_text(config_content)

    yield app_path


@pytest.fixture
def fastapi_app(
    test_settings: TestSettings, temp_project: Path
) -> Generator[TestClient, None, None]:
    """
    Create a FastAPI app instance for testing.

    Args:
        test_settings: Test settings fixture
        temp_project: Temporary project directory

    Yields:
        TestClient for the FastAPI app
    """
    # Change to temp project directory
    original_cwd = os.getcwd()
    try:
        os.chdir(temp_project)
        # Set settings globally
        set_settings(test_settings)
        # Create FastAppKit and app
        kit = FastAppKit(settings=test_settings)
        app = kit.create_app()
        client = TestClient(app)
        yield client
    finally:
        os.chdir(original_cwd)


@pytest.fixture
def external_app_package(temp_project: Path) -> Generator[Path, None, None]:
    """
    Create a sample external app package for testing.

    Args:
        temp_project: Temporary project directory

    Yields:
        Path to external app package directory
    """
    app_path = temp_project.parent / "external_sample"
    app_path.mkdir()

    # Create package structure
    (app_path / "external_sample").mkdir()
    (app_path / "external_sample" / "migrations").mkdir()
    (app_path / "external_sample" / "migrations" / "versions").mkdir()

    # Create __init__.py
    init_content = '''"""External sample app."""
from fastapi import APIRouter, FastAPI

router = APIRouter()

@router.get("/")
def hello():
    return {"message": "Hello from external app"}

def register(app: FastAPI):
    """Register the app."""
    app.include_router(router, prefix="/external")
    return router
'''
    (app_path / "external_sample" / "__init__.py").write_text(init_content)

    # Create pyproject.toml
    pyproject_content = """[tool.poetry]
name = "external-sample"
version = "0.1.0"

[tool.fastappkit]
name = "external_sample"
version = "0.1.0"
entrypoint = "external_sample:register"
migrations = "migrations"
models_module = "external_sample.models"
"""
    (app_path / "pyproject.toml").write_text(pyproject_content)

    yield app_path
