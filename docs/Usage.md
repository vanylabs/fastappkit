# 📚 fastappkit — Complete Usage Guide

_A comprehensive guide for developers, project creators, app authors, and maintainers._

---

## Table of Contents

1. [Introduction](#introduction)
2. [Quick Start](#quick-start)
3. [Core Concepts](#core-concepts)
4. [Project Management](#project-management)
5. [App Development](#app-development)
6. [Migrations](#migrations)
7. [Configuration](#configuration)
8. [CLI Reference](#cli-reference)
9. [Architecture & Behavior](#architecture--behavior)
10. [Troubleshooting](#troubleshooting)

---

## Introduction

**fastappkit** is a toolkit for building FastAPI projects with a modular app architecture. It enables:

-   **Internal apps** — project-specific feature modules (like Django apps)
-   **External apps** — reusable, pluggable packages (like WordPress plugins)
-   **Unified migrations** — coordinated database schema management
-   **Simple CLI** — streamlined development workflows

### Key Features

-   ✅ Clean project structure with automatic app discovery
-   ✅ Shared migrations for internal apps, isolated migrations for external apps
-   ✅ Automatic router mounting with configurable prefixes
-   ✅ Fail-fast validation and error handling
-   ✅ Support for both monorepo and multi-repo workflows

---

## Quick Start

### 1. Create a Project

```bash
fastappkit core new myproject
cd myproject
```

This creates:

```
myproject/
├── core/
│   ├── config.py          # Settings (loads from .env)
│   ├── app.py             # create_app() factory
│   └── db/
│       └── migrations/    # Core migrations
├── apps/                   # Internal apps directory
├── fastappkit.toml        # Project configuration
├── .env                   # Environment variables
└── main.py                # Entry point
```

### 2. Create an Internal App

```bash
fastappkit app new blog
```

This creates `apps/blog/` with models, router, and registers it in `fastappkit.toml`.

### 3. Run Migrations

```bash
# Generate migration
fastappkit migrate app blog makemigrations -m "initial"

# Apply all migrations (core → internal → external)
fastappkit migrate all
```

### 4. Start Development Server

```bash
fastappkit core dev
```

Your API is now running at `http://127.0.0.1:8000` with routes mounted at `/blog/`.

---

## Core Concepts

### App Types

fastappkit distinguishes apps by **origin**, not behavior:

#### Internal Apps

-   Located in `./apps/<name>/`
-   Part of your project's codebase
-   Share the project's migration timeline
-   Can depend on other internal apps
-   Use shared `alembic_version` table
-   **Not** meant for packaging (unless explicitly opted in)

#### External Apps

-   Installed via `pip install <package>` (must be pip-installed, no filesystem paths)
-   Independent Python packages
-   Must be schema-independent
-   Cannot depend on internal apps
-   Use per-app version tables (`alembic_version_<appname>`)
-   Perfect for reusable plugins

### Project Structure

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

**Note:** Core models are optional and separate from apps. They don't require creating an app. Place all your core models in `core/models.py`. Core models are for shared infrastructure tables (sessions, logs, queues, etc.) that are used across the entire project, not app-specific features (use internal apps for those).

### App Loading Flow

```
                        APP LOADING FLOW
               (internal + external resolution steps)

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

**Important:** If ANY app fails to load, the entire application startup aborts (fail-fast).

---

## Project Management

### Creating a Project

```bash
fastappkit core new <name> [--project-root <path>] [--description <text>]
```

**Options:**

-   `--project-root`: Directory to create project in (default: current working directory)
-   `--description`: Project description

**Note:** If `--project-root` is not specified, the project is created in the current working directory. The project name becomes a subdirectory.

**What it creates:**

-   Project directory structure
-   `fastappkit.toml` configuration file
-   `.env` file with `DATABASE_URL` placeholder
-   Core application files (`core/app.py`, `core/config.py`, etc.)
-   `main.py` entry point

### Running Development Server

```bash
fastappkit core dev [--host <host>] [--port <port>] [--reload] [--verbose] [--debug] [--quiet]
```

**Options:**

-   `--host, -h`: Host to bind to (default: `127.0.0.1`)
-   `--port, -p`: Port to bind to (default: `8000`)
-   `--reload`: Enable auto-reload on code changes
-   `--verbose, -v`: Enable verbose output (overrides global setting)
-   `--debug`: Enable debug output (overrides global setting, includes stack traces)
-   `--quiet, -q`: Suppress output (overrides global setting)

**Note:** This command must be run from the project root directory (where `fastappkit.toml` is located).

**Behavior:**

-   Loads all apps from `fastappkit.toml`
-   Mounts routers with automatic prefixes
-   Starts uvicorn server
-   Hot-reloads on code changes (if `--reload` is set)
-   With `--reload`, uses import string (`main:app`) for proper reloading
-   Without `--reload`, creates app object directly for faster startup

---

## App Development

### Creating Internal Apps

```bash
fastappkit app new <name> [--as-package]
```

**Options:**

-   `--as-package`: Create as external package (for external apps)

**Note:** This command must be run from the project root directory (where `fastappkit.toml` is located).

**What it creates:**

```
apps/<name>/
├── __init__.py      # register(app: FastAPI) function
├── models.py        # SQLAlchemy models
└── router.py        # FastAPI routers
```

**Important:** Internal apps do NOT have their own `migrations/` directory. They use the core's migration directory (`core/db/migrations/`).

**Entrypoint Patterns:**

fastappkit supports two patterns for registering routers:

**Pattern 1: Return Router (Recommended)**

```python
# apps/blog/__init__.py
from fastapi import APIRouter, FastAPI
from fastappkit.conf import get_settings

router = APIRouter()

@router.get("/posts")
def list_posts():
    return [{"id": 1, "title": "Hello"}]

def register(app: FastAPI) -> APIRouter:
    """Register this app with the FastAPI application."""
    settings = get_settings()  # Access settings
    # Return router - fastappkit will mount it with prefix from manifest
    return router
```

**Pattern 2: Mount Router Yourself**

```python
# apps/blog/__init__.py
from fastapi import APIRouter, FastAPI
from fastappkit.conf import get_settings

router = APIRouter()

@router.get("/posts")
def list_posts():
    return [{"id": 1, "title": "Hello"}]

def register(app: FastAPI) -> None:
    """Register this app with the FastAPI application."""
    settings = get_settings()  # Access settings
    # Mount router yourself - fastappkit will skip mounting
    app.include_router(router, prefix="/blog")
    # Can also use custom prefix, tags, dependencies, etc.
    # app.include_router(router, prefix="/api/blog", tags=["blog"])
```

**Customization Options:**

-   **Access Settings:** Use `get_settings()` to access configuration
-   **Custom Prefix:** Override manifest `route_prefix` by mounting yourself
-   **Router Tags:** Add tags when mounting: `app.include_router(router, tags=["blog"])`
-   **Dependencies:** Add dependencies: `app.include_router(router, dependencies=[Depends(...)])`
-   **Startup/Shutdown Events:** Register events: `@app.on_event("startup")`
-   **Middleware:** Add middleware in `register()`: `app.add_middleware(...)`
-   **Background Tasks:** Register background tasks: `app.add_task(...)`
-   **Exception Handlers:** Add exception handlers: `app.add_exception_handler(...)`

### Creating External Apps

```bash
fastappkit app new <name> --as-package
```

**Options:**

-   `--as-package`: Create as external package (required for external apps)

**Note:** This command must be run from the project root directory (where `fastappkit.toml` is located).

**What it creates:**

```
<name>/
├── <name>/              # Package directory (nested structure)
│   ├── __init__.py
│   ├── models.py
│   ├── router.py
│   ├── fastappkit.toml  # Manifest (in package directory)
│   └── migrations/      # Migrations (in package directory)
│       ├── env.py       # Alembic env (isolated)
│       ├── script.py.mako
│       └── versions/
├── pyproject.toml       # Package metadata (Poetry/pip)
├── alembic.ini         # For independent development
└── README.md
```

**External App Manifest (`<name>/<name>/fastappkit.toml`):**

```toml
name = "blog"
version = "0.1.0"
entrypoint = "blog:register"
migrations = "migrations"
models_module = "blog.models"
route_prefix = "/blog"
```

**Note:** The manifest is stored in `fastappkit.toml` inside the package directory (`<name>/<name>/fastappkit.toml`), not in `pyproject.toml`. This ensures it's included when the package is published to PyPI. Internal apps do not need a manifest file - their metadata is inferred from the directory structure.

**Required Fields:**

-   `name`: App name (string)
-   `version`: Semantic version (string)
-   `entrypoint`: Dotted path to register function (e.g., `"blog:register"`)
-   `migrations`: Path to migrations directory (relative to package directory, typically `"migrations"`)
-   `models_module`: Dotted path to models module (recommended)

**Optional Fields:**

-   `route_prefix`: Router prefix (default: `/<appname>`)

**Manifest Location:**

-   External apps use `fastappkit.toml` located at `<name>/<name>/fastappkit.toml` (inside the package directory)
-   This file is included when the package is published to PyPI
-   No fallback to `pyproject.toml` or `plugin.json` - `fastappkit.toml` is required

### Using External Apps

External apps must be installed via `pip` (editable or non-editable) and then added to `fastappkit.toml`:

**Step 1: Install the external app**

```bash
# For published packages
pip install external-app-name

# For local development (editable install)
pip install -e /path/to/external-app

# Or add to requirements.txt/pyproject.toml dependencies
```

**Step 2: Add to `fastappkit.toml`**

Edit `fastappkit.toml` and add the app to the `apps` list:

```toml
[tool.fastappkit]
apps = [
  "apps.blog",           # Internal app
  "external_app_name",   # External app (package name)
]
```

**How App Resolution Works:**

The resolver tries methods in this order:

1. **Internal app pattern**: `"apps.<name>"` - checks if entry starts with `apps.` and resolves to `./apps/<name>/`
2. **Package name** (dotted import): `"external_app_name"` - tries to import as Python module using `importlib.import_module()`

**Important:** External apps must be pip-installed. Filesystem paths are not supported. For local development, use `pip install -e /path/to/app` to install the package in editable mode.

### Listing Apps

```bash
fastappkit app list [--verbose] [--debug] [--quiet]
```

**Options:**

-   `--verbose, -v`: Show detailed information (import path, migrations path, etc.)
-   `--debug`: Show debug information
-   `--quiet, -q`: Suppress output

**Note:** This command must be run from the project root directory (where `fastappkit.toml` is located).

Shows all apps (internal and external) with:

-   Name
-   Type (internal/external)
-   Route prefix

**Verbose output includes:**

-   Import path
-   Filesystem path (if applicable)
-   Migrations path
-   Manifest details

### Validating Apps

```bash
fastappkit app validate <name> [--json]
```

**Options:**

-   `--json`: Output results as JSON (CI-friendly)

**Note:** This command must be run from the project root directory (where `fastappkit.toml` is located).

**Validates:**

-   Manifest presence and correctness (required fields, format)
-   Entrypoint importability and signature
-   Migration folder existence (external apps)
-   Version table configuration (external apps)
-   Isolation rules (external apps cannot import internal apps)
-   Duplicate app names (warns if multiple entries resolve to same name)

**Output:**

-   Human-readable by default (shows errors and warnings)
-   JSON format with `--json` flag (includes `valid`, `errors`, `warnings` arrays)
-   Exit code 1 if validation fails (useful for CI/CD)

---

## Migrations

### Migration Architecture

fastappkit uses a **unified migration runner** that handles:

1. **Core migrations** — shared infrastructure (sessions, logs, etc.)
2. **Internal app migrations** — project-wide schema changes
3. **External app migrations** — isolated plugin schemas

### Version Tables

-   **Core & Internal Apps:** Use shared `alembic_version` table
-   **External Apps:** Use per-app tables (`alembic_version_<appname>`)

### Migration Commands

#### Core Migrations

```bash
# Generate migration (for core models)
fastappkit migrate core -m "message"
```

**Options:**

-   `-m, --message`: Migration message (required)

**Note:** This command must be run from the project root directory. Core migrations are generated separately, but preview/upgrade/downgrade operations use unified commands (see below) since core and internal app migrations share the same directory and version table.

**Core Models (Optional):**

Core migrations can work with or without models. Core models are **separate from apps** — you don't need to create an app to use them. They're for shared infrastructure tables (sessions, logs, job queues, etc.) that are used across your entire project.

**Where to Place Core Models:**

Place all your core models in `core/models.py`:

```python
# core/models.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True)
    session_key = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ApiLog(Base):
    __tablename__ = "api_logs"

    id = Column(Integer, primary_key=True)
    endpoint = Column(String)
    method = Column(String)
```

**How Core Models Are Discovered:**

The migration system looks for core models in `core/models.py`:

1.  Tries to import `core.models` (looks for `Base` or `metadata` attribute)
2.  If not found, uses empty `MetaData` (you can still create manual migrations)

**Important Notes:**

-   **Core models must be in `core/models.py`** — this is the only supported location
-   Core migrations are located in `core/db/migrations/`
-   Uses shared `alembic_version` table (same as internal apps)
-   Core models are **optional** — core migrations work without them
-   Core models are for **shared infrastructure**, not app-specific features (use internal apps for those)

#### Internal App Migrations

```bash
# Generate migration (creates in core/db/migrations/versions/)
fastappkit migrate app <name> makemigrations -m "message"
```

**Options:**

-   `-m, --message`: Migration message (required)

**Note:** This command must be run from the project root directory.

**Important:**

-   Internal app migrations are created in `core/db/migrations/versions/`, NOT in `apps/<name>/migrations/`
-   Internal apps share the project's migration timeline with core migrations
-   **Internal apps can only create migrations** - they cannot use `preview`, `upgrade`, or `downgrade` actions
-   For preview/upgrade/downgrade operations, use the unified commands below (which operate on all core + internal app migrations together)

**Autogenerate Behavior:**

-   Uses full project metadata (all internal apps + core models)
-   Good for cross-app relationships and shared schema
-   Migration files are shared across all internal apps and core

#### Unified Migration Operations (Core + Internal Apps)

Since core and internal app migrations share the same directory (`core/db/migrations/`) and version table, use these unified commands for preview, upgrade, and downgrade:

```bash
# Preview SQL
fastappkit migrate preview [--revision <rev>]

# Apply migrations
fastappkit migrate upgrade [--revision <rev>]

# Downgrade
fastappkit migrate downgrade <revision>
```

**Options:**

-   `--revision, -r`: Specific revision (default: `head` for upgrade/preview)

**Note:** These commands must be run from the project root directory. They operate on all migrations in `core/db/migrations/versions/`, which includes both core migrations and internal app migrations.

#### External App Migrations

**Development (in external app directory):**

```bash
cd <external-app>/
alembic revision --autogenerate -m "message"
alembic upgrade head
```

**From Core Project:**

```bash
# Apply existing migrations (migrations must exist in external app)
fastappkit migrate app <name> upgrade [--revision <rev>]

# Preview SQL
fastappkit migrate app <name> preview [--revision <rev>]

# Downgrade
fastappkit migrate app <name> downgrade <revision>
```

**Options:**

-   `--revision, -r`: Specific revision (default: `head` for upgrade/preview)

**Note:** This command must be run from the project root directory.

**Important:**

-   External apps **cannot create migrations** from the core project (`makemigrations` is not supported for external apps)
-   They must be developed independently in their own directory using standard Alembic commands
-   External apps can only use `upgrade`, `downgrade`, and `preview` actions from the core project

**Error Handling:**

-   If no migration files found, shows helpful error with instructions
-   If revision not found, provides tips for independent development
-   Uses core project's `DATABASE_URL` (not external app's `alembic.ini`)

#### Apply All Migrations

```bash
fastappkit migrate all
```

**Note:** This command must be run from the project root directory.

**Execution Order:**

1. Core migrations (always first)
2. Internal apps (in config order) - skipped (already included in core migrations)
3. External apps (in config order)

**Notes:**

-   This is the **recommended command** for normal workflows
-   Internal apps are skipped because they share core's migration directory
-   Shows progress for each step
-   Fails fast if any migration fails

### Migration Safety

#### Downgrades

Downgrades are explicit operations:

```bash
# For core + internal apps (unified command)
fastappkit migrate downgrade <revision>

# For external apps
fastappkit migrate app <name> downgrade <revision>
```

**Safety checks:**

-   Dry-run inspection
-   Foreign key dependency validation
-   External apps can only revert their own schema

### Migration Ordering

Migrations run in this order:

1. **Core** (always first)
2. **Internal apps** (order from `fastappkit.toml`)
3. **External apps** (order from `fastappkit.toml`)

You can override internal app order in config:

```toml
[tool.fastappkit.migration]
order = ["core", "auth", "blog"]
```

### Autogenerate Behavior

#### Internal Apps

Autogenerate sees:

-   ✅ All internal app models
-   ✅ All core models
-   ✅ Cross-app relations

Good for teams working on shared schema.

#### External Apps

Autogenerate sees:

-   ✅ Only that app's own models
-   ❌ No internal app models
-   ❌ No other external apps' models
-   ❌ No core models

If an external app tries to import foreign models → validation error.

---

## Configuration

### Project Configuration: `fastappkit.toml`

**Primary configuration file** (separate from `pyproject.toml`):

```toml
[tool.fastappkit]
apps = [
  "apps.blog",           # Internal app
  "apps.auth",           # Internal app
  "fastapi_payments",    # External app (pip-installed package)
]

[tool.fastappkit.migration]
order = ["core", "auth", "blog"]  # Optional: override internal app order
```

**App Entry Formats:**

-   `apps.<name>` → Internal app (located in `./apps/<name>/`)
-   `<package_name>` → External app (pip-installed package, must be importable)

### Settings: `core/config.py`

Settings are defined in `core/config.py` using Pydantic's `BaseSettings`:

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings.

    Loads from .env file automatically.
    """

    DATABASE_URL: str = "sqlite:///./app.db"
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
```

**Note:** The scaffolded code includes minimal settings. You can extend it by adding more fields as needed:

```python
class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"
    DEBUG: bool = False

    # Add your custom settings here
    SECRET_KEY: str = "change-me-in-production"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields from .env
    )
```

**Customization:**

-   **Add Custom Settings:** Add fields to `Settings` class
-   **Validation:** Use Pydantic validators: `@field_validator('DATABASE_URL')`
-   **Default Values:** Set defaults in class definition
-   **Nested Settings:** Use Pydantic models for nested configuration
-   **Environment-Specific:** Override in `.env` or via environment variables

**Accessing Settings:**

```python
# Runtime accessor (Django-like)
from fastappkit.conf import get_settings

settings = get_settings()
db_url = settings.DATABASE_URL

# FastAPI dependency injection
from fastappkit.conf import get_settings
from fastapi import Depends

def handler(settings: Settings = Depends(get_settings)):
    return settings.DEBUG
```

**Environment Variables:**

The `.env` file is auto-scaffolded and automatically loaded:

```bash
DATABASE_URL=sqlite:///./myproject.db
DEBUG=false
```

You can add additional environment variables as needed for your custom settings.

**Settings Initialization:**

Settings are initialized in `core/app.py` when the module is imported:

```python
# core/app.py (generated by fastappkit)
from core.config import Settings
from fastappkit.core.kit import FastAppKit

# Initialize FastAppKit with project's Settings
# This sets settings globally via set_settings() in FastAppKit.__init__
settings = Settings()  # Loads from .env automatically via BaseSettings
kit = FastAppKit(settings=settings)
app = kit.create_app()
```

The `Settings()` class automatically loads from `.env` via Pydantic's `BaseSettings`. When `FastAppKit` is initialized, it calls `set_settings()` which makes the settings globally available via `get_settings()`.

**For CLI/Migration Commands:**

CLI commands use `ensure_settings_loaded(project_root)` which imports `core.app`, causing the settings to be initialized automatically.

**FastAPI App Customization:**

You can customize the FastAPI app by modifying `core/app.py` or by subclassing `FastAppKit`:

```python
# Option 1: Modify core/app.py directly
# core/app.py
from core.config import Settings
from fastappkit.core.kit import FastAppKit

settings = Settings()
kit = FastAppKit(settings=settings)
app = kit.create_app()

# Customize FastAPI app
app.title = "My Custom API"
app.version = "1.0.0"
app.description = "Custom API description"

# Option 2: Subclass FastAppKit
from fastappkit.core.kit import FastAppKit
from fastapi import FastAPI
from core.config import Settings

class CustomFastAppKit(FastAppKit):
    def create_app(self) -> FastAPI:
        app = super().create_app()
        # Add custom middleware, exception handlers, etc.
        app.add_middleware(...)
        app.title = "My Custom API"
        return app

settings = Settings()
kit = CustomFastAppKit(settings=settings)
app = kit.create_app()
```

### App Manifest: `fastappkit.toml` (External Apps)

External apps must declare metadata in `fastappkit.toml` located inside the package directory:

**Location:** `<app_name>/<app_name>/fastappkit.toml`

**Example:**

```toml
name = "blog"
version = "0.1.0"
entrypoint = "blog:register"
migrations = "migrations"
models_module = "blog.models"
route_prefix = "/blog"
```

**Important:**

-   The manifest file is `fastappkit.toml`, not `pyproject.toml`
-   It must be located in the package directory (where `__init__.py` is)
-   This ensures it's included when the package is published to PyPI
-   No fallback - `fastappkit.toml` is required for external apps

---

## CLI Reference

### Global Options

All commands support:

-   `--verbose, -v`: Enable verbose output
-   `--debug`: Enable debug output (includes stack traces)
-   `--quiet, -q`: Suppress output
-   `--version, -V`: Show version and exit (global flag)

**Show Version:**

```bash
fastappkit --version
# Or use short form:
fastappkit -V
```

Shows the installed fastappkit version.

### Project Commands

| Command                      | Description            | Options                                                           |
| ---------------------------- | ---------------------- | ----------------------------------------------------------------- |
| `fastappkit core new <name>` | Create new project     | `--project-root`, `--description`                                 |
| `fastappkit core dev`        | Run development server | `--host`, `--port`, `--reload`, `--verbose`, `--debug`, `--quiet` |

### App Commands

| Command                          | Description         | Options                           |
| -------------------------------- | ------------------- | --------------------------------- |
| `fastappkit app new <name>`      | Create internal app | `--as-package`                    |
| `fastappkit app list`            | List all apps       | `--verbose`, `--debug`, `--quiet` |
| `fastappkit app validate <name>` | Validate app        | `--json`                          |

### Migration Commands

| Command                                        | Description          | Options                                                                           |
| ---------------------------------------------- | -------------------- | --------------------------------------------------------------------------------- |
| `fastappkit migrate core`                      | Core migrations      | `makemigrations` only (use unified commands for preview/upgrade/downgrade)        |
| `fastappkit migrate app <name>`                | App migrations       | `makemigrations` (internal only), `upgrade`/`downgrade`/`preview` (external only) |
| `fastappkit migrate preview/upgrade/downgrade` | Unified operations   | Core + internal app migrations                                                    |
| `fastappkit migrate all`                       | Apply all migrations | (no options)                                                                      |

**Migration Flags:**

-   `-m, --message`: Migration message (required for `makemigrations`)
-   `--revision, -r`: Specific revision (default: `head` for upgrade/preview)

**Note:** All migration commands must be run from the project root directory (where `fastappkit.toml` is located).

**Migration Actions:**

-   `makemigrations`: Generate new migration (autogenerate)
-   `upgrade`: Apply migrations (default: to `head`)
-   `downgrade`: Revert migrations (requires revision as argument)
-   `preview`: Show SQL without executing (dry-run)

---

## Architecture & Behavior

### System Overview

```
┌───────────────────────────────────────────────────────────────┐
│                           fastappkit                          │
│                     (Framework + CLI + Runtime)               │
└───────────────────────────────────────────────────────────────┘
                │                       │
                │                       │
     ┌──────────▼──────────┐   ┌────────▼──────────┐
     │     Developer       │   │   fastappkit CLI  │
     │   (project author)  │   │ (codegen + mgmt)  │
     └──────────┬──────────┘   └────────┬──────────┘
                │                       │
                ▼                       ▼
      ┌───────────────────┐     ┌───────────────────┐
      │ Internal Apps     │     │ External Apps     │
      │ ./apps/<name>     │     │ pip-installed     │
      │ shared timeline   │     │ isolated timeline │
      └──────────┬────────┘     └─────────┬─────────┘
                 │                        │
                 ▼                        ▼
          ┌─────────────┐         ┌──────────────┐
          │   FastAPI   │         │  Alembic     │
          │   router    │         │  per-app env │
          └──────┬──────┘         └──────┬───────┘
                 │                       │
                 └──────────┬────────────┘
                            ▼
                ┌──────────────────────────┐
                │      Runtime Engine      │
                │ (loader + registry + db) │
                └──────────────────────────┘
```

### App Resolution

The loader resolves apps in this order:

1. **Check `apps.*` pattern** (Internal apps)

    - Example: `apps.blog` → Internal app
    - Located in `./apps/blog/`
    - Must have `__init__.py` in the directory

2. **Try as dotted import** (Python package name - External apps)

    - Example: `fastapi_blog` → `import fastapi_blog` using `importlib.import_module()`
    - If successful → External app (pip-installed)
    - Must have `fastappkit.toml` manifest in package directory

3. **Fail if:**
    - Folder missing (internal apps)
    - No Python package root (missing `__init__.py`)
    - Cannot import module (external apps)
    - No manifest (external apps only)
    - Cannot determine app type

**Important:** External apps must be pip-installed. Filesystem paths are not supported. For local development, use `pip install -e /path/to/app`.

### App Loading (Fail-Fast)

**If ANY app fails to load, startup aborts.**

Error details include:

-   App identifier (path or name)
-   Stage where failure occurred (resolve/load/register)
-   Manifest snapshot
-   Python traceback excerpt
-   Suggested fixes

**There is no "skip this app and continue."**

### Router Mounting

**Router Mounting Architecture:**

```
┌───────────────────── FastAPI app ───────────────────────┐
│                                                         │
│   /core/...                                             │
│                                                         │
│   /blog/...              <-- internal apps              │
│   /account/...                                          │
│                                                         │
│   /fastapi_blog/...      <-- external apps              │
│   /fastapi_store/...                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Default Prefix:**

```
/<appname>
```

**Examples:**

-   `apps.blog` → `/blog`
-   `fastapi_payments` → `/fastapi_payments`

**Override Methods:**

1. **Via Manifest:**

    ```toml
    # In fastappkit.toml (external apps) or inferred (internal apps)
    route_prefix = "/api/blog"
    ```

2. **Via Register Function (Full Control):**

    ```python
    def register(app: FastAPI) -> None:
        # Mount with custom prefix, tags, dependencies
        app.include_router(
            router,
            prefix="/api/v1/blog",
            tags=["blog", "content"],
            dependencies=[Depends(require_auth)]
        )
    ```

3. **Empty Prefix (Mount at Root):**
    ```toml
    route_prefix = ""  # Mounts at root level
    ```

**Customization Options:**

-   **Tags:** Add OpenAPI tags: `tags=["blog", "content"]`
-   **Dependencies:** Add route dependencies: `dependencies=[Depends(...)]`
-   **Response Class:** Customize response: `response_class=CustomResponse`
-   **Prefix Override:** Override manifest prefix in `register()`
-   **Multiple Routers:** Mount multiple routers from same app
-   **Sub-applications:** Mount sub-applications: `app.mount("/static", StaticFiles(...))`

**Route Collision Detection:**

-   Automatically detects overlapping routes (same path + method)
-   Emits warnings (not fatal) - startup continues
-   Shows which apps have conflicting routes
-   Provides suggestions for resolution
-   Developer responsibility to fix collisions

### Entrypoint Contract

**Function-based:**

```python
def register(app: FastAPI) -> APIRouter | None:
    """Register app with FastAPI application.

    Can return APIRouter (fastappkit mounts it) or None (mount yourself).
    """
    settings = get_settings()  # Access settings
    # Option 1: Return router
    return router
    # Option 2: Mount yourself
    # app.include_router(router, prefix="/blog")
    # return None
```

**Class-based:**

```python
class App:
    def register(self, app: FastAPI) -> APIRouter | None:
        """Register app with FastAPI application."""
        settings = get_settings()  # Access settings
        app.include_router(router, prefix="/blog")
        return None  # Or return router
```

**Entrypoint String Formats:**

-   `"blog:register"` - Function in module
-   `"blog:App"` - Class (must have `register` method)
-   `"blog"` - Defaults to `"blog:register"`
-   `"blog.main:register"` - Function in submodule

**Loader instantiates class-based apps with no constructor arguments.**

**What `register()` CAN do:**

-   ✅ Return `APIRouter` - fastappkit mounts it with prefix
-   ✅ Mount routers yourself - fastappkit skips mounting
-   ✅ Register startup/shutdown events: `@app.on_event("startup")`
-   ✅ Add middleware: `app.add_middleware(...)`
-   ✅ Add exception handlers: `app.add_exception_handler(...)`
-   ✅ Add background tasks: `app.add_task(...)`
-   ✅ Access settings via `get_settings()`
-   ✅ Mount sub-applications: `app.mount(...)`
-   ✅ Add dependencies, tags, etc. when mounting routers

**What `register()` MUST NOT do:**

-   ❌ Modify global FastAPI state outside its namespace
-   ❌ Perform blocking operations at import time
-   ❌ Connect to DB directly (use startup events instead)
-   ❌ Access settings via global variables (use `get_settings()`)
-   ❌ Raise exceptions that prevent other apps from loading

### Isolation Rules

**Isolation Rules Visualization:**

```
                    ISOLATION RULES

┌──────────────┐    cannot depend    ┌──────────────┐
│ Internal App │ ───────────────────>│ External App │
└──────────────┘                     └──────────────┘
       ▲                                     │
       │ can depend                          │ cannot touch
       │                                     ▼
┌──────────────┐                     ┌──────────────┐
│    Core      │     cannot touch    │ Internal App │
└──────────────┘                     └──────────────┘
```

**Internal Apps:**

-   ✅ Can depend on other internal apps
-   ✅ Can modify shared tables
-   ✅ Participate in shared migration timeline (use core's migration directory)
-   ✅ No manifest file required (metadata inferred from structure)
-   ❌ Cannot depend on external apps

**External Apps:**

-   ✅ Independent schema evolution (isolated migrations)
-   ✅ Can be published to PyPI
-   ✅ Must be pip-installed (no filesystem path support)
-   ✅ Must have `fastappkit.toml` manifest in package directory
-   ❌ Cannot depend on internal apps
-   ❌ Cannot touch other apps' tables
-   ❌ Cannot modify core or internal tables
-   ❌ Cannot create migrations from core project (must use Alembic directly)

### Migration Engine Architecture

```
┌─────────────────────────────────────────────┐
│         Unified Migration Runner            │
└─────────────────────────────────────────────┘
              │
   ┌──────────┴──────────┐
   ▼                     ▼
CORE MIGRATIONS     APP MIGRATIONS
                     (per app)
                     internal → external
                     shared    → isolated
   │                     │
   └──────────┬──────────┘
              ▼
    ┌───────────────────────┐
    │ Alembic Multi-Env API │
    └───────────────────────┘
              │
              ▼
         DATABASE
```

### Migration Execution Flow

**For External App Upgrade:**

1. **App Resolution & Validation**

    - Resolve app from `fastappkit.toml`
    - Load manifest
    - Validate app exists and is external type
    - Get `migrations_path` from manifest

2. **Build Alembic Config**

    - Set `script_location` = external app's migrations directory
    - Set `version_table` = `alembic_version_<appname>`
    - Set `sqlalchemy.url` = core project's `DATABASE_URL` (from settings)
    - Set `config_file_name = None` (don't read external app's `alembic.ini`)

3. **Load Migration Scripts**

    - Create `ScriptDirectory` from migration folder
    - Scan `migrations/versions/` for `.py` files
    - Parse revision IDs and build revision graph
    - Determine `head` revision

4. **Check Database State**

    - Connect to core project's database
    - Check if `alembic_version_<appname>` table exists
    - Read current revision (or `None` if first time)

5. **Determine Upgrade Path**

    - Compare current revision with `head`
    - Build list of migrations to apply (in order)

6. **Execute Migrations**
    - For each migration: execute `upgrade()`, update version table, commit
    - Create version table if it doesn't exist (first migration)

**Edge Cases:**

-   Database has revision `X` but migration file doesn't exist → Error
-   Migration file references non-existent `down_revision` → Error
-   Empty migration directory → Error (external apps must have migrations)

### Settings System

**Settings System:**

1. **Settings Definition** (in `core/config.py`):

    ```python
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        """
        Application settings.

        Loads from .env file automatically.
        """

        DATABASE_URL: str = "sqlite:///./app.db"
        DEBUG: bool = False

        model_config = SettingsConfigDict(
            env_file=".env",
            env_file_encoding="utf-8"
        )
    ```

2. **Settings Initialization** (in `core/app.py`):

    ```python
    from core.config import Settings
    from fastappkit.core.kit import FastAppKit

    settings = Settings()  # Automatically loads from .env
    kit = FastAppKit(settings=settings)  # Sets global settings via set_settings()
    app = kit.create_app()
    ```

3. **Runtime Accessor** (Django-like convenience):

    ```python
    from fastappkit.conf import get_settings

    settings = get_settings()
    db_url = settings.DATABASE_URL
    ```

4. **FastAPI Dependency Injection**:

    ```python
    from fastappkit.conf import get_settings
    from fastapi import Depends
    from core.config import Settings

    def handler(settings: Settings = Depends(get_settings)):
        return settings.DEBUG
    ```

**Settings Location:**

-   Defined in `core/config.py`
-   Loaded from `.env` via `BaseSettings`
-   Auto-scaffolded when creating project

**Customization:**

-   **Extend Settings:** Add fields to `Settings` class in `core/config.py`
-   **Validation:** Use Pydantic validators for custom validation
-   **Environment-Specific:** Use different `.env` files per environment
-   **Override Programmatically:** Pass `Settings` instance to `create_app(settings=...)`
-   **Thread-Safe:** Settings are stored in thread-safe singleton

### Dependency Versions

**Important:** When creating a new project or external app, dependency versions in `pyproject.toml` are set to `*` (any version) by default. This provides maximum flexibility but may lead to compatibility issues.

**Recommendations:**

1. **For Production Projects:**

    - Update dependency versions to specific ranges (e.g., `>=0.120.0,<0.130`)
    - Pin exact versions for critical dependencies
    - Test thoroughly after updating versions

2. **For External Apps:**

    - Match dependency versions with the core project for compatibility
    - Use compatible version ranges that work with the core project's versions
    - Document minimum required versions in your app's README

3. **Example:**
    ```toml
    [tool.poetry.dependencies]
    python = "^3.11"
    fastapi = ">=0.120.0,<0.130"  # Specific range instead of *
    sqlalchemy = ">=2.0,<3.0"
    alembic = ">=1.17.2,<1.18"
    ```

**Note:** The CLI will display a warning message when creating projects or external apps, reminding you to update dependency versions according to your needs.

---

## Troubleshooting

### Common Issues

#### App Fails to Load

**Error:** `AppLoadError: Failed to load app 'blog'`

**Check:**

1. App exists in filesystem or is pip-installed
2. Manifest is present and valid (external apps)
3. Entrypoint is importable and has correct signature
4. Migration folder exists (external apps)

**Solution:**

-   Run `fastappkit app validate <name>` for detailed diagnostics
-   Check error message for specific stage (resolve/load/register)

#### Migration Revision Not Found

**Error:** `Can't locate revision identified by '0d037769d7fb'`

**Possible Causes:**

1. Database has revision stored but migration file doesn't exist
2. Migration file references non-existent `down_revision`
3. Wrong database being used (external app using its own DB instead of core's)

**Solution:**

-   Check what's in database: `SELECT * FROM alembic_version_<appname>`
-   Verify migration files exist in `migrations/versions/`
-   Ensure using core project's `DATABASE_URL` (not external app's)

#### Route Collisions

**Warning:** `Route collision detected: /api used by multiple apps`

**Solution:**

-   Change `route_prefix` in manifest or register function
-   Ensure each app has unique prefix

#### External App Cannot Create Migrations

**Error:** `Cannot create migrations for external app`

**Explanation:**

-   External apps must be developed independently
-   Migrations created in external app's own directory using `alembic`
-   Core project only applies existing migrations

**Solution:**

```bash
cd <external-app>/
alembic revision --autogenerate -m "message"
# Then from core project:
fastappkit migrate app <name> upgrade
```

### Debugging Tips

1. **Use verbose/debug flags:**

    ```bash
    fastappkit app list --verbose
    fastappkit core dev --debug
    ```

2. **Validate apps:**

    ```bash
    fastappkit app validate <name>
    ```

3. **Preview migrations:**

    ```bash
    fastappkit migrate app <name> preview
    ```

4. **Check database state:**

    ```sql
    SELECT * FROM alembic_version;  -- Core & internal apps
    SELECT * FROM alembic_version_<appname>;  -- External apps
    ```

5. **Check app registry:**
    - Start dev server with `--debug` to see app loading details
    - Check logs for app resolution and registration steps

### Best Practices

1. **Keep migration files in VCS** and package them with external apps
2. **Run `makemigrations` locally** and test upgrades in staging
3. **Use per-app version tables** for external apps (automatic)
4. **Prefer explicit `models_module`** in manifest
5. **Avoid cross-app model imports** in external apps
6. **Review SQL via `preview`** before applying migrations
7. **Test downgrades** to ensure migrations are reversible

---

## Summary

fastappkit provides:

-   ✅ **Clear boundaries:** Internal apps vs external plugins
-   ✅ **Predictable migrations:** Shared timeline for internal, isolated for external
-   ✅ **Simple workflows:** CLI-first development
-   ✅ **Strict safety:** Fail-fast startup, validation checks
-   ✅ **Automatic routing:** Prefix-based router mounting
-   ✅ **Simple integration:** Install via `pip` and add to `fastappkit.toml`
-   ✅ **Full extensibility:** Ready for admin UI, marketplaces, signing (future)

**After reading this guide, you should:**

-   Understand the difference between internal and external apps
-   Know how to create projects and apps
-   Understand migration behavior and safety
-   Be able to configure and troubleshoot issues
-   Know how the system works behind the scenes

---

**Happy coding with fastappkit! 🚀**
