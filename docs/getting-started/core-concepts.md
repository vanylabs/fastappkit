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

## App Loading Flow

The app loading process follows these steps:

```
┌──────────────────────────────────────────────┐
│            fastappkit Runtime                │
└──────────────────────────────────────────────┘
                │
                ▼
       ┌────────────────┐
       │ Read config    │  from fastappkit.toml
       └────────────────┘
                │
                ▼
      ┌───────────────────┐
      │ Discover apps     │
      │ - internal dirs   │
      │ - pip pkgs        │
      └───────────────────┘
                │
                ▼
      ┌────────────────────┐
      │ Validate manifests │
      │ + isolation rules  │
      └────────────────────┘
                │
                ▼
      ┌──────────────────────────┐
      │ Build App Registry       │
      │ - name                   │
      │ - type (internal/ext)    │
      │ - metadata               │
      │ - routes/models/etc      │
      └──────────────────────────┘
                │
                ▼
      ┌──────────────────────────┐
      │ Mount routers            │
      └──────────────────────────┘
```

!!! warning "Fail-Fast Behavior"
If ANY app fails to load, the entire application startup aborts. This ensures that configuration errors are caught early rather than causing runtime issues.

## Key Features

-   **Clean project structure** with automatic app discovery
-   **Shared migrations** for internal apps, isolated migrations for external apps
-   **Automatic router mounting** with configurable prefixes
-   **Fail-fast validation** and error handling
-   **Support for both monorepo and multi-repo workflows**

## Learn More

-   [Internal Apps](../topics/internal-apps.md) - Deep dive into internal apps
-   [External Apps](../topics/external-apps.md) - Understanding external apps
-   [Migration System](../topics/migration-system.md) - How migrations work
-   [App Isolation](../topics/app-isolation.md) - Isolation rules and constraints
