# Architecture

This document describes the internal architecture of fastappkit.

## System Overview

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

## Components

### CLI

The CLI provides commands for:

- Project creation and management
- App creation and validation
- Migration management
- Development server

### Runtime Engine

The runtime engine handles:

- App discovery and loading
- Manifest validation
- Router mounting
- Migration coordination

### App Loader

Loads apps from configuration:

1. Reads `fastappkit.toml`
2. Resolves app entries (internal vs external)
3. Loads manifests (external apps)
4. Validates apps
5. Builds registry

### App Registry

Stores metadata about loaded apps:

- App name and type
- Import path
- Migrations path
- Route prefix
- Manifest data

### Migration Runner

Coordinates migration execution:

- Core migrations (always first)
- Internal app migrations (shared timeline)
- External app migrations (isolated)

## App Resolution

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

## App Loading (Fail-Fast)

If ANY app fails to load, startup aborts.

Error details include:

- App identifier (path or name)
- Stage where failure occurred (resolve/load/register)
- Manifest snapshot
- Python traceback excerpt
- Suggested fixes

There is no "skip this app and continue."

## Settings System

Settings flow:

1. **Settings Definition** (in `core/config.py`)
   - Uses Pydantic `BaseSettings`
   - Loads from `.env` automatically

2. **Settings Initialization** (in `core/app.py`)
   - `Settings()` instance created
   - `FastAppKit` initialized with settings
   - `set_settings()` called (makes settings globally available)

3. **Runtime Access**
   - `get_settings()` retrieves global settings
   - Available throughout application

## Migration Engine Architecture

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

## Learn More

- [Migration System](../topics/migration-system.md) - Migration architecture details
- [Extending fastappkit](extending-fastappkit.md) - How to extend fastappkit
