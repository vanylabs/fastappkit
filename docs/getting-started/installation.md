# Installation

fastappkit requires Python 3.11 or higher. It is tested with Python 3.11 and 3.12.

## Prerequisites

-   Python 3.11 or higher
-   pip or Poetry for package management

## Install with pip

```bash
pip install fastappkit
```

## Install with Poetry

```bash
poetry add fastappkit
```

## Verify Installation

After installation, verify that fastappkit is correctly installed:

```bash
fastappkit --version
```

This should display the installed version number (e.g., `fastappkit 0.2.1`).

## Requirements

fastappkit has the following dependencies (automatically installed):

-   Python 3.11+ (tested with Python 3.11 and 3.12)
-   FastAPI 0.120.0+
-   SQLAlchemy 2.0+
-   Alembic 1.17.2+
-   Pydantic Settings 2.10.0+
-   Typer 0.20.0+

These dependencies are automatically installed when you install fastappkit.

## Development Installation

If you want to contribute to fastappkit or run it from source:

```bash
git clone https://github.com/vanylabs/fastappkit.git
cd fastappkit
poetry install
poetry shell
fastappkit --version
```

See the [Contributing Guide](../community/index.md#contributing) for more details on setting up a development environment.

## Troubleshooting

### Installation Fails

If installation fails, check:

-   Python version: `python --version` (must be 3.11+)
-   pip/poetry is up to date: `pip install --upgrade pip` or `poetry self update`
-   Virtual environment is activated (if using one)

### Command Not Found

If `fastappkit` command is not found after installation:

-   Ensure the Python environment where fastappkit was installed is in your PATH
-   If using a virtual environment, activate it: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
-   If using Poetry, use `poetry run fastappkit` or activate the Poetry shell: `poetry shell`

### Version Check Fails

If `fastappkit --version` shows an error:

-   Verify installation: `pip show fastappkit` or `poetry show fastappkit`
-   Reinstall if needed: `pip install --upgrade fastappkit`

## Next Steps

Once installed, proceed to:

-   [Quick Start](quickstart.md) - Create your first project
-   [Core Concepts](core-concepts.md) - Understand how fastappkit works
