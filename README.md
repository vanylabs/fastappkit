# fastappkit

> A toolkit for building FastAPI projects with apps — internal and external pluggable apps

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

**fastappkit** brings Django-like app architecture to FastAPI, enabling modular development with both project-specific internal apps and reusable external pluggable apps.

## What is fastappkit?

**fastappkit** is a toolkit for building FastAPI projects with a modular app architecture. It enables:

-   **Internal apps** — project-specific feature modules (like Django apps)
-   **External apps** — reusable, pluggable packages (like WordPress plugins)
-   **Unified migrations** — coordinated database schema management
-   **Automatic router mounting** — seamless integration of app routes
-   **App validation and isolation** — ensure apps don't conflict with each other

## ✨ Key Features

-   ✅ **Clean project structure** with automatic app discovery
-   ✅ **Shared migrations** for internal apps, isolated migrations for external apps
-   ✅ **Automatic router mounting** with configurable prefixes
-   ✅ **Fail-fast validation** and error handling
-   ✅ **Support for both monorepo and multi-repo workflows**
-   ✅ **Simple CLI** for project and app management

## 📦 Installation

Install fastappkit using pip or poetry:

```bash
pip install fastappkit
```

or

```bash
poetry add fastappkit
```

## 🏃 Quick Start

### 1. Create a new project

```bash
fastappkit core new myproject
cd myproject
```

This creates a complete FastAPI project structure with:

-   Core application setup
-   Database configuration
-   Migration system
-   App directory structure

### 2. Create an internal app

```bash
fastappkit app new blog
```

This creates a new internal app in `apps/blog/` with models, router, and registers it in `fastappkit.toml`.

### 3. Run migrations

```bash
fastappkit migrate all
```

This runs all migrations in the correct order: core → internal apps → external apps.

### 4. Start the development server

```bash
fastappkit core dev
```

Your FastAPI application is now running at `http://127.0.0.1:8000`!

## 📚 Documentation

Comprehensive documentation is available at [Read the Docs](https://fastappkit.readthedocs.io/) (coming soon).

For now, see [docs/Usage.md](docs/Usage.md) for detailed usage instructions.

## 🎯 Core Concepts

### Internal Apps

Internal apps are project-specific modules that live in your project's `apps/` directory. They share the same migration system and database connection.

```bash
fastappkit app new blog
# Creates apps/blog/ with models, router, etc.
```

### External Apps

External apps are reusable packages that can be installed via pip and plugged into any fastappkit project.

```bash
fastappkit app new payments --as-package
# Creates a standalone package structure
```

### Migrations

fastappkit provides unified migration management:

-   **Core migrations**: Project-level schema changes
-   **Internal app migrations**: Shared migration directory for all internal apps
-   **External app migrations**: Isolated migrations per external app

```bash
# Create migrations for an internal app
fastappkit migrate app blog makemigrations -m "Add post model"

# Run all migrations
fastappkit migrate all

# Preview SQL before applying
fastappkit migrate preview
```

## 🛠️ CLI Commands

### Project Management

```bash
fastappkit core new <name>          # Create a new project
fastappkit core dev                  # Run development server
```

### App Management

```bash
fastappkit app new <name>            # Create an internal app
fastappkit app new <name> --as-package  # Create an external app
fastappkit app list                  # List all apps
fastappkit app validate <name>       # Validate an app
```

### Migration Management

```bash
fastappkit migrate core -m "message"           # Create core migration
fastappkit migrate app <name> makemigrations   # Create app migration
fastappkit migrate app <name> upgrade         # Upgrade app migrations
fastappkit migrate app <name> downgrade -r <rev>  # Downgrade app migrations
fastappkit migrate all                        # Run all migrations
fastappkit migrate preview                    # Preview SQL for all migrations
```

## 📖 Example Project Structure

```
myproject/
├── core/
│   ├── config.py          # Settings (loads from .env)
│   ├── app.py             # create_app() factory
│   └── db/
│       └── migrations/    # Core migrations
├── apps/                   # Internal apps directory
│   └── blog/
│       ├── models.py
│       └── router.py
├── fastappkit.toml        # Project configuration
├── .env                   # Environment variables
└── main.py                # Entry point
```

## 🔧 Configuration

fastappkit uses `fastappkit.toml` for project configuration:

```toml
[tool.fastappkit]
apps = [
    "apps.blog",
    "apps.users",
    "external_package_name"
]
```

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

-   Inspired by Django's app system
-   Built with [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/), and [Typer](https://typer.tiangolo.com/)

## 📞 Support

-   📖 [Documentation](docs/Usage.md)
-   🐛 [Issue Tracker](https://github.com/vanylabs/fastappkit/issues)
-   💬 [Discussions](https://github.com/vanylabs/fastappkit/discussions)

---

**Made with ❤️ for the FastAPI community**
