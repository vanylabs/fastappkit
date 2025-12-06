# fastappkit Test Suite

## Overview

This directory contains the test suite for fastappkit, organized by test type and module.

## Structure

```
tests/
├── fixtures/              # Centralized test data factories
│   ├── app_factory.py    # Factory for creating test apps
│   ├── config_factory.py # Factory for creating test configs
│   └── project_factory.py # Factory for creating test projects
│
├── unit/                  # Unit tests (fast, isolated)
│   └── test_core/         # Core module tests
│       ├── test_registry.py
│       ├── test_kit.py
│       ├── test_loader.py
│       ├── test_router.py
│       └── test_manifest.py
│
├── integration/           # Integration tests (end-to-end)
│   └── test_cli/          # CLI command tests
│
├── conftest.py            # Pytest fixtures
└── README.md              # This file
```

## Test Philosophy

**Quality over Quantity**: We focus on meaningful tests that would catch real bugs if the implementation changes. We don't aim for 100% coverage, but rather comprehensive coverage of critical paths.

**Test Categories**:

-   **Unit Tests**: Fast, isolated tests for individual components
-   **Integration Tests**: End-to-end tests for complete workflows

## Running Tests

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit -m unit

# Run only integration tests
pytest tests/integration -m integration

# Run with coverage
pytest --cov=fastappkit --cov-report=html

# Run specific test file
pytest tests/unit/test_core/test_registry.py
```

## Test Data Management

All test data is centralized in `tests/fixtures/` to ensure:

-   Consistency across tests
-   Easy maintenance
-   Reusability
-   Standard patterns

### Using Factories

```python
from tests.fixtures import ProjectFactory, InternalAppFactory, ConfigFactory

# Create a minimal project
project = ProjectFactory.create_minimal(temp_project)

# Create project with apps
project = ProjectFactory.create_with_apps(temp_project, "blog", "shop")

# Create an internal app
app_path = InternalAppFactory.create_minimal(temp_project, "blog")

# Create configuration
ConfigFactory.create_with_apps(config_path, "apps.blog", "apps.shop")
```

## Current Test Coverage

### ✅ Completed

-   **AppRegistry**: Registration, retrieval, filtering, iteration
-   **FastAppKit**: App creation, settings integration, error handling
-   **AppLoader**: Loading apps, registration execution, error handling
-   **RouterAssembler**: Router mounting, prefix handling, collision detection
-   **ManifestLoader**: Manifest loading for internal/external apps, validation

### 🚧 In Progress

-   Validation tests (isolation, manifest, migrations)
-   CLI integration tests
-   Migration tests with SQLite in-memory

## Dependencies

Test dependencies are defined in `pyproject.toml`:

-   `pytest` - Test framework
-   `pytest-asyncio` - Async test support
-   `pytest-cov` - Coverage reporting
-   `httpx` - Required for FastAPI TestClient

## Notes

-   Tests use temporary directories for file system operations
-   SQLite in-memory database is used for migration tests
-   CLI tests use `typer.testing.CliRunner` for real command execution
