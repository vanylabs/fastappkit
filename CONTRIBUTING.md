# Contributing to fastappkit

Thank you for your interest in contributing to fastappkit! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

### Development Environment Setup

fastappkit uses Poetry for dependency management. Follow these steps to set up your development environment:

1. **Clone the repository**

    ```bash
    git clone https://github.com/vanylabs/fastappkit.git
    cd fastappkit
    ```

2. **Install Poetry** (if not already installed)

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

3. **Install dependencies**

    ```bash
    poetry install
    ```

4. **Activate the virtual environment**

    ```bash
    poetry shell
    ```

5. **Verify installation**
    ```bash
    fastappkit --version
    ```

## 📝 Code Style

fastappkit follows strict code style guidelines to maintain consistency.

### Formatting

We use **Black** for code formatting:

```bash
poetry run black fastappkit/ tests/
```

### Linting

We use **Ruff** for linting:

```bash
poetry run ruff check fastappkit/ tests/
poetry run ruff check --fix fastappkit/ tests/  # Auto-fix issues
```

### Type Hints

All public APIs must have type hints. We use **mypy** for type checking:

```bash
poetry run mypy fastappkit/
```

### Pre-commit Hooks

We use pre-commit hooks to ensure code quality. The hooks run Black, Ruff, and mypy automatically before each commit.

**Setup:**

```bash
# Install dependencies (includes pre-commit)
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

**Manual run (optional):**

```bash
# Run hooks on all files
poetry run pre-commit run --all-files
```

## 🧪 Testing

### Running Tests

Run all tests:

```bash
poetry run pytest
```

Run with coverage:

```bash
poetry run pytest --cov=fastappkit --cov-report=html
```

Run specific test file:

```bash
poetry run pytest tests/unit/test_core/test_kit.py
```

### Writing Tests

-   All tests should be in the `tests/` directory
-   Use pytest fixtures (see `tests/conftest.py` and `tests/fixtures/`)
-   Follow the existing test structure:
    -   `tests/unit/` - Unit tests for individual modules
    -   `tests/integration/` - Integration tests for CLI commands and workflows

Example test structure:

```python
import pytest
from fastappkit.core.kit import FastAppKit

def test_kit_creation(settings):
    """Test that FastAppKit can be instantiated."""
    kit = FastAppKit(settings=settings)
    assert kit.settings == settings
```

### Test Coverage

We aim for **70-80% minimum** test coverage. Check coverage with:

```bash
poetry run pytest --cov=fastappkit --cov-report=html
open htmlcov/index.html  # View coverage report
```

## 📦 Building and Distributing

### Local Build

Build the package locally:

```bash
poetry build
```

Check the built package:

```bash
twine check dist/*
```

### Testing Installation

Test installation from the built package:

```bash
pip install dist/fastappkit-*.whl
```

## 🔀 Git Workflow

### Branch Naming

-   `feature/description` - New features
-   `fix/description` - Bug fixes
-   `docs/description` - Documentation updates
-   `refactor/description` - Code refactoring

### Commit Messages

Follow conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

Types:

-   `feat`: New feature
-   `fix`: Bug fix
-   `docs`: Documentation changes
-   `style`: Code style changes (formatting, etc.)
-   `refactor`: Code refactoring
-   `test`: Adding or updating tests
-   `chore`: Maintenance tasks

Examples:

```
feat(cli): add app validate command

Adds a new command to validate app structure and manifest.

Closes #123
```

```
fix(migrations): handle missing migration path gracefully

Previously, missing migration paths would raise an exception.
Now they are handled with a clear error message.
```

### Pull Request Process

1. **Create a branch** from `main`

    ```bash
    git checkout -b feature/my-feature
    ```

2. **Make your changes** and commit them

3. **Run tests and linting**

    ```bash
    poetry run pytest
    poetry run black fastappkit/ tests/
    poetry run ruff check fastappkit/ tests/
    poetry run mypy fastappkit/
    ```

4. **Push to your fork**

    ```bash
    git push origin feature/my-feature
    ```

5. **Create a Pull Request** on GitHub

6. **Ensure CI passes** - All checks must pass before merge

## 📋 Pull Request Checklist

Before submitting a PR, ensure:

-   [ ] Code follows the style guidelines (Black, Ruff)
-   [ ] All tests pass (`poetry run pytest`)
-   [ ] New tests are added for new features
-   [ ] Type hints are added for all public APIs
-   [ ] Documentation is updated (if needed)
-   [ ] Commit messages follow conventional format
-   [ ] PR description explains the changes and why

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description** of the bug
2. **Steps to reproduce**
3. **Expected behavior**
4. **Actual behavior**
5. **Environment**:
    - Python version
    - fastappkit version
    - OS and version
6. **Error messages** or logs (if any)

Use the [bug report template](.github/ISSUE_TEMPLATE/bug.yml) if available.

## 💡 Feature Requests

When requesting features, please include:

1. **Use case** - Why is this feature needed?
2. **Proposed solution** - How should it work?
3. **Alternatives considered** - Other approaches you've thought about

Use the [feature request template](.github/ISSUE_TEMPLATE/feature.yml) if available.

## 📚 Documentation

### Code Documentation

-   All public functions and classes should have docstrings
-   Use Google-style docstrings:

```python
def create_app(settings: SettingsProtocol) -> FastAPI:
    """
    Create and configure FastAPI application.

    Args:
        settings: Settings instance from project's core.config module

    Returns:
        FastAPI: Configured FastAPI application
    """
```

### User Documentation

-   Update `docs/Usage.md` for user-facing changes
-   Update README.md if needed
-   Add examples for new features

## 🎯 Areas for Contribution

We welcome contributions in these areas:

-   **Bug fixes** - Check open issues
-   **New features** - Discuss in issues first
-   **Documentation** - Always welcome!
-   **Tests** - Improve coverage
-   **Performance** - Optimize app loading, migrations, etc.
-   **Examples** - Add example projects or apps

## ❓ Questions?

-   Open a [GitHub Discussion](https://github.com/vanylabs/fastappkit/discussions)
-   Check existing [Issues](https://github.com/vanylabs/fastappkit/issues)
-   Review [Documentation](docs/Usage.md)

## 📜 Code of Conduct

Please note that this project follows a [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

---

Thank you for contributing to fastappkit! 🎉
