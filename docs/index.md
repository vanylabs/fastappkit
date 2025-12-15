# fastappkit

**fastappkit** is an open-source toolkit that brings Django-like app architecture to FastAPI. If you've ever wished FastAPI had a modular app system similar to Django, this is for you.

## What is fastappkit?

fastappkit is a toolkit for building FastAPI projects with a modular app architecture. It enables:

-   **Internal apps** — project-specific feature modules (like Django apps)
-   **External apps** — reusable, pluggable packages (like WordPress plugins)
-   **Unified migrations** — coordinated database schema management
-   **Automatic router mounting** — seamless integration of app routes
-   **App validation and isolation** — ensure apps don't conflict with each other

## Why fastappkit?

Building large FastAPI applications often means either cramming everything into a single file or manually organizing modules without clear conventions. fastappkit solves this by introducing a structured app system where you can organize your code into logical, reusable components—both within your project and as installable packages.

Whether you're building a monolith that needs better organization or creating reusable components for multiple projects, fastappkit provides the structure and tooling to make it happen.

## Who can use this?

-   **FastAPI developers** building applications that are outgrowing a single-file structure
-   **Teams** that need consistent project organization across multiple developers
-   **Developers** creating reusable FastAPI components they want to share
-   **Anyone** who appreciates Django's app system but prefers FastAPI's performance and modern Python features

## Key Features

fastappkit provides several important capabilities:

**Project Structure**

-   Clean project layout with automatic app discovery
-   Consistent organization that scales as your project grows

**Migration Management**

-   Shared migrations for internal apps
-   Isolated migrations for external apps
-   Coordinated execution order

**Router Integration**

-   Automatic router mounting with configurable prefixes
-   Seamless route integration without manual wiring

**Validation & Safety**

-   Fail-fast validation and error handling
-   App isolation checks to prevent conflicts
-   Manifest validation for external apps

**Workflow Support**

-   Works with both monorepo and multi-repo workflows
-   Simple CLI for project and app management

## Quick Start

Get started with fastappkit in minutes:

### 1. Create a new project

```bash
fastappkit core new myproject
cd myproject
```

This creates a complete FastAPI project structure with core application setup, database configuration, migration system, and app directory structure.

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

For detailed installation instructions, see the [Installation Guide](getting-started/installation.md).

## Documentation Overview

### Getting Started

-   [Installation](getting-started/installation.md) - Install fastappkit and verify your setup
-   [Quick Start](getting-started/quickstart.md) - Create your first project
-   [Core Concepts](getting-started/core-concepts.md) - Understand internal and external apps

### Guides

-   [Creating Projects](guides/creating-projects.md) - Set up new fastappkit projects
-   [Creating Apps](guides/creating-apps.md) - Build internal and external apps
-   [Migrations](guides/migrations.md) - Manage database schema changes
-   [Configuration](guides/configuration.md) - Configure your projects
-   [Deployment](guides/deployment.md) - Deploy fastappkit applications

### Topics

-   [Internal Apps](topics/internal-apps.md) - Project-specific modules
-   [External Apps](topics/external-apps.md) - Reusable pluggable packages
-   [Migration System](topics/migration-system.md) - How migrations work
-   [App Isolation](topics/app-isolation.md) - Ensuring apps don't conflict
-   [Router Mounting](topics/router-mounting.md) - Automatic route integration

### Reference

-   [CLI Reference](reference/cli-reference.md) - All available commands
-   [Configuration Reference](reference/configuration-reference.md) - Configuration options
-   [Manifest Reference](reference/manifest-reference.md) - App manifest format
-   [API Reference](reference/api-reference.md) - Programmatic API

### Advanced

-   [Architecture](advanced/architecture.md) - How fastappkit works internally
-   [Extending fastappkit](advanced/extending-fastappkit.md) - Customize and extend
-   [Best Practices](advanced/best-practices.md) - Recommended patterns

### Troubleshooting

-   [Common Issues](troubleshooting/common-issues.md) - Solutions to frequent problems
-   [Debugging](troubleshooting/debugging.md) - Debugging techniques

## Core Concepts

### Internal Apps

Internal apps are project-specific modules that live in your project's `apps/` directory. They share the same migration system and database connection.

**Key points:**

-   Internal apps import `Base` from `core.models` for SQLAlchemy models
-   The `register()` function can return `Optional[APIRouter]` - return a router for fastappkit to mount, or mount it yourself and return `None`

### External Apps

External apps are reusable packages that can be installed via pip and plugged into any fastappkit project.

**Key points:**

-   External apps must use their own `Base` class (isolated metadata) - cannot import from core
-   The `register()` function can return `Optional[APIRouter]` - return a router for fastappkit to mount, or mount it yourself and return `None`
-   External apps must have `fastappkit.toml` manifest in the package directory

### Migrations

fastappkit provides unified migration management:

-   **Core migrations**: Project-level schema changes
-   **Internal app migrations**: Shared migration directory for all internal apps
-   **External app migrations**: Isolated migrations per external app

## Example Project Structure

```
myproject/
├── core/
│   ├── config.py          # Settings (loads from .env)
│   ├── models.py          # SQLAlchemy Base class (DeclarativeBase)
│   ├── app.py             # create_app() factory
│   └── db/
│       └── migrations/    # Core migrations
├── apps/                  # Internal apps directory
│   └── blog/
│       ├── models.py      # Imports Base from core.models
│       └── router.py
├── fastappkit.toml        # Project configuration
├── .env                   # Environment variables
└── main.py                # Entry point
```

## Community

fastappkit is an open-source project. We welcome contributions and value our community.

-   [Contributing](community/index.md#contributing) - How to contribute
-   [Code of Conduct](community/index.md#code-of-conduct) - Community standards
-   [Security Policy](community/index.md#security-policy) - Reporting vulnerabilities
-   [License](community/index.md#license) - MIT License

## Support

-   [Documentation](getting-started/installation.md)
-   [Issue Tracker](https://github.com/vanylabs/fastappkit/issues)
-   [Discussions](https://github.com/vanylabs/fastappkit/discussions)

## Acknowledgments

-   Inspired by Django's app system
-   Built with [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/), and [Typer](https://typer.tiangolo.com/)
