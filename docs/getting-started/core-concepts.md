# Core Concepts

This document explains the fundamental concepts of fastappkit.

## App Types

fastappkit distinguishes apps by **origin**, not behavior:

### Internal Apps

-   Located in `./apps/<name>/`
-   Part of your project's codebase
-   Share the project's migration timeline
-   Can depend on other internal apps
-   Use shared `alembic_version` table
-   Not meant for packaging (unless explicitly opted in)

### External Apps

-   Installed via `pip install <package>` (must be pip-installed, no filesystem paths)
-   Independent Python packages
-   Must be schema-independent
-   Cannot depend on internal apps
-   Use per-app version tables (`alembic_version_<appname>`)
-   Perfect for reusable plugins

## Project Structure

A typical fastappkit project has this structure:

```
myproject/
├── core/                    # Core project code
│   ├── config.py           # Settings (BaseSettings from .env)
│   ├── app.py              # create_app() factory
│   ├── models.py           # Core models (optional - for shared infrastructure)
│   ├── db/
│   │   └── migrations/     # Core migrations (shared with internal apps)
│   │       ├── env.py
│   │       └── versions/
│   └── ...
├── apps/                    # Internal apps (flat structure)
│   ├── blog/
│   │   ├── __init__.py     # register() function
│   │   ├── models.py       # SQLAlchemy models (app-specific)
│   │   └── router.py       # FastAPI routers
│   └── auth/
│       └── ...
├── fastappkit.toml         # Project config (apps list)
├── .env                    # Environment variables
└── main.py                 # Entry point
```

!!! note "Core Models"
    Core models are optional and separate from apps. They don't require creating an app. Place all your core models in `core/models.py`. Core models are for shared infrastructure tables (sessions, logs, queues, etc.) that are used across the entire project, not app-specific features (use internal apps for those).

## How Apps Are Discovered and Loaded

1. **Configuration**: Apps are listed in `fastappkit.toml`:
   ```toml
   [tool.fastappkit]
   apps = [
     "apps.blog",        # Internal app
     "fastapi_payments", # External app (pip-installed)
   ]
   ```

2. **Resolution**: fastappkit resolves each entry:
   - `apps.*` pattern → Internal app (checks `./apps/<name>/`)
   - Package name → External app (imports via `importlib`)

3. **Loading**: For each app:
   - Load manifest (external apps only)
   - Validate structure and isolation
   - Execute `register()` function
   - Mount router (if returned)

4. **Registration**: Apps provide a `register(app: FastAPI)` function that:
   - Can return `APIRouter` (auto-mounted)
   - Can return `None` (manual mount)
   - Receives the FastAPI app instance

## Migration System Overview

fastappkit provides unified migration management:

### Core Migrations

-   Located in `core/db/migrations/`
-   For core-level schema changes
-   Uses `alembic_version` table

### Internal App Migrations

-   **Shared** with core migrations (same directory: `core/db/migrations/`)
-   All internal apps use the same migration timeline
-   Autogenerate sees all internal app models + core models
-   Uses shared `alembic_version` table

### External App Migrations

-   **Isolated** in each app's package directory (`<app>/<app>/migrations/`)
-   Each external app has its own migration timeline
-   Autogenerate sees only that app's models
-   Uses per-app version table (`alembic_version_<appname>`)

### Migration Order

Migrations run in this order:

1. **Core** (always first)
2. **Internal apps** (order from `fastappkit.toml` or `[tool.fastappkit.migration.order]`)
3. **External apps** (order from `fastappkit.toml`)

## Router Mounting Basics

Apps can provide routers in two ways:

1. **Auto-mount**: Return `APIRouter` from `register()` function
   - fastappkit mounts it with prefix from manifest (`route_prefix`)
   - Default prefix: `/<appname>`
   - Can be empty string `""` to mount at root

2. **Manual mount**: Return `None` from `register()` function
   - App handles mounting itself in `register()`
   - More control over mounting logic

Route collisions are detected and warnings emitted (not fatal).

## Settings System Basics

Settings are defined in `core/config.py` using Pydantic's `BaseSettings`:

-   **Required settings**: `database_url` and `debug` (from `SettingsProtocol`)
-   **Custom settings**: Add any fields you need
-   **Environment variables**: Loaded from `.env` file automatically
-   **Global access**: Use `get_settings()` function (Django-like)
-   **Initialization**: Settings are initialized in `core/app.py` when `FastAppKit` is created

Settings are loaded in this order:

1. Environment variables (highest priority)
2. `.env` file
3. Default values in `Field()` (lowest priority)

## Key Differences: Internal vs External Apps

| Feature | Internal Apps | External Apps |
|---------|---------------|---------------|
| **Location** | `./apps/<name>/` | Pip-installed package |
| **Base Class** | `core.models.Base` | Own `Base` (DeclarativeBase) |
| **Migrations** | Shared with core | Isolated per app |
| **Dependencies** | Can import from core/internal | Cannot import from core/internal |
| **Manifest** | Not required | Required (`fastappkit.toml`) |
| **Development** | Part of project | Independent (can be separate repo) |
| **Publishing** | Not meant for PyPI | Can publish to PyPI |

## Next Steps

-   [Usage Scenarios](../usage/index.md) - Choose your development approach
-   [Creating Projects](../guides/creating-projects.md) - Detailed project setup
-   [Creating Apps](../guides/creating-apps.md) - Detailed app creation
-   [Configuration](../configuration/index.md) - All configuration options
