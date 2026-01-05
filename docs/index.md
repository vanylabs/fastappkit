# fastappkit

**fastappkit** is an open-source toolkit that brings Django-like app architecture to FastAPI. If you've ever wished FastAPI had a modular app system similar to Django, this is for you.

## What is fastappkit?

fastappkit enables you to organize your FastAPI code into logical, reusable components—both within your project and as installable packages. It provides:

-   **Internal apps**: Project-specific modules (like Django apps) that live in your `apps/` directory
-   **External apps**: Reusable packages you can install via pip and plug into any fastappkit project

Both types get automatic router mounting, unified migration management, and validation to prevent conflicts.

## Key Features

-   **Modular Architecture**: Organize code into apps (internal and external)
-   **Automatic Router Mounting**: Apps register routes automatically
-   **Unified Migrations**: Coordinated database schema management
-   **App Isolation**: Validation ensures apps don't conflict
-   **CLI Tools**: Simple commands for project and app management
-   **Settings Management**: Django-like settings system with environment variables

## Quick Start

Get started in minutes:

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

Your FastAPI app is now running at `http://127.0.0.1:8000` with routes mounted at `/blog/`.

## Examples

See fastappkit in action with real-world examples:

-   **[Modular Tasks Platform](https://github.com/vanylabs/modular-task-manager)** - A complete example showcasing internal and external apps working together. Features authentication, task management, and notes modules, demonstrating how to build modular FastAPI applications with fastappkit.

## Documentation Overview

### Getting Started

-   [Installation](getting-started/installation.md) - Install fastappkit and verify your setup
-   [Quick Start](getting-started/quickstart.md) - Create your first project
-   [Core Concepts](getting-started/core-concepts.md) - Understand internal and external apps

### Usage Scenarios

-   [Usage Overview](usage/index.md) - Choose your development path
-   [Scaffolding Only](usage/scaffolding-only.md) - Just project structure
-   [Internal Apps](usage/internal-apps.md) - Build with internal apps
-   [Full Ecosystem](usage/full-ecosystem.md) - Internal + external apps

### Configuration

-   [Configuration Overview](configuration/index.md) - All configuration options
-   [Project Configuration](configuration/project-config.md) - `fastappkit.toml` reference
-   [Settings](configuration/settings.md) - `core/config.py` guide
-   [External App Manifest](configuration/external-app-manifest.md) - Manifest format

### Guides

-   [Creating Projects](guides/creating-projects.md) - Set up new fastappkit projects
-   [Creating Apps](guides/creating-apps.md) - Build internal and external apps
-   [Migrations](guides/migrations.md) - Manage database schema changes
-   [Development Workflow](guides/development-workflow.md) - Day-to-day development
-   [Deployment](guides/deployment.md) - Deploy fastappkit applications

### Reference

-   [CLI Reference](reference/cli-reference.md) - All available commands
-   [Configuration Reference](reference/configuration-reference.md) - Complete config options
-   [API Reference](reference/api-reference.md) - Programmatic API

### Topics

-   [Internal Apps](topics/internal-apps.md) - Project-specific modules
-   [External Apps](topics/external-apps.md) - Reusable pluggable packages
-   [Migration System](topics/migration-system.md) - How migrations work
-   [App Isolation](topics/app-isolation.md) - Ensuring apps don't conflict
-   [Router Mounting](topics/router-mounting.md) - Automatic route integration

### Advanced

-   [Architecture](advanced/architecture.md) - How fastappkit works internally
-   [Extending fastappkit](advanced/extending-fastappkit.md) - Customize and extend
-   [Best Practices](advanced/best-practices.md) - Recommended patterns

### Troubleshooting

-   [Common Issues](troubleshooting/common-issues.md) - Solutions to frequent problems
-   [Debugging](troubleshooting/debugging.md) - Debugging techniques

## Who is this for?

-   **FastAPI developers** building applications that are outgrowing a single-file structure
-   **Teams** that need consistent project organization across multiple developers
-   **Developers** creating reusable FastAPI components they want to share
-   **Anyone** who appreciates Django's app system but prefers FastAPI's performance and modern Python features

## Community

-   [Contributing](community/index.md#contributing) - How to contribute
-   [Code of Conduct](community/index.md#code-of-conduct) - Community standards
-   [Security Policy](community/index.md#security-policy) - Reporting vulnerabilities
-   [Changelog](changelog/0.2.1.md) - Version history (see [Changelog section](changelog/0.2.1.md) for all versions)

## Support

-   [Documentation](getting-started/installation.md)
-   [Issue Tracker](https://github.com/vanylabs/fastappkit/issues)
-   [Discussions](https://github.com/vanylabs/fastappkit/discussions)

## Acknowledgments

Inspired by Django's app system. Built with [FastAPI](https://fastapi.tiangolo.com/), [SQLAlchemy](https://www.sqlalchemy.org/), [Alembic](https://alembic.sqlalchemy.org/), and [Typer](https://typer.tiangolo.com/).
