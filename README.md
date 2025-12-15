# fastappkit

[![PyPI version](https://img.shields.io/pypi/v/fastappkit.svg)](https://pypi.org/project/fastappkit/)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/vanylabs/fastappkit/blob/main/LICENSE)

**fastappkit** is an open-source toolkit that brings Django-like app architecture to FastAPI. If you've ever wished FastAPI had a modular app system similar to Django, this is for you.

## Why fastappkit?

Building large FastAPI applications often means either cramming everything into a single file or manually organizing modules without clear conventions. fastappkit solves this by introducing a structured app system where you can organize your code into logical, reusable components—both within your project and as installable packages.

Whether you're building a monolith that needs better organization or creating reusable components for multiple projects, fastappkit provides the structure and tooling to make it happen.

## Who is this for?

-   **FastAPI developers** building applications that are outgrowing a single-file structure
-   **Teams** that need consistent project organization across multiple developers
-   **Developers** creating reusable FastAPI components they want to share
-   **Anyone** who appreciates Django's app system but prefers FastAPI's performance and modern Python features

## What it does

fastappkit enables two types of apps:

-   **Internal apps**: Project-specific modules (like Django apps) that live in your `apps/` directory
-   **External apps**: Reusable packages you can install via pip and plug into any fastappkit project

Both types get automatic router mounting, unified migration management, and validation to prevent conflicts. Internal apps share migrations; external apps keep theirs isolated.

## Quick Start

```bash
# Install
pip install fastappkit

# Create a new project
fastappkit core new myproject
cd myproject

# Create an app
fastappkit app new blog

# Run migrations
fastappkit migrate all

# Start development server
fastappkit core dev
```

That's it. Your FastAPI app is running at `http://127.0.0.1:8000` with routes mounted at `/blog/`.

## Documentation

Full documentation is available at **[fastappkit.readthedocs.io](https://fastappkit.readthedocs.io/)**.

## Contributing

This is an open-source project, and contributions are welcome. See [CONTRIBUTING.md](https://github.com/vanylabs/fastappkit/blob/main/CONTRIBUTING.md) for guidelines on how to contribute.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Support

-   [Documentation](https://fastappkit.readthedocs.io/)
-   [Issue Tracker](https://github.com/vanylabs/fastappkit/issues)
-   [Discussions](https://github.com/vanylabs/fastappkit/discussions)

## Acknowledgments

Inspired by Django's app system. Built with [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/), and [Typer](https://typer.tiangolo.com/).
