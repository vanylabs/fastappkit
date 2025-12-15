# Installation

fastappkit requires Python 3.11 or higher. It is tested with Python 3.11 and 3.12.

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

This should display the installed version number.

## Requirements

fastappkit has the following dependencies:

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
