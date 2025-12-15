# Migrations

This guide covers working with database migrations in fastappkit.

## Migration Architecture

fastappkit uses a **unified migration runner** that handles:

1. **Core migrations** — shared infrastructure (sessions, logs, etc.)
2. **Internal app migrations** — project-wide schema changes
3. **External app migrations** — isolated plugin schemas

## Version Tables

-   **Core & Internal Apps:** Use shared `alembic_version` table
-   **External Apps:** Use per-app tables (`alembic_version_<appname>`)

## Core Migrations

Core migrations are for project-level schema changes and shared infrastructure.

### Generate Core Migration

```bash
fastappkit migrate core -m "message"
```

**Options:**

-   `-m, --message`: Migration message (required)

!!! note "Unified Operations"
Core migrations are generated separately, but preview/upgrade/downgrade operations use unified commands (see below) since core and internal app migrations share the same directory and version table.

### Core Models

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

1. Tries to import `core.models` (looks for `Base` or `metadata` attribute)
2. If not found, uses empty `MetaData` (you can still create manual migrations)

!!! important "Core Models Location"
Core models must be in `core/models.py` — this is the only supported location. Core migrations are located in `core/db/migrations/`. Uses shared `alembic_version` table (same as internal apps). Core models are **optional** — core migrations work without them. Core models are for **shared infrastructure**, not app-specific features (use internal apps for those).

## Internal App Migrations

Internal app migrations share the project's migration timeline with core migrations.

### Generate Internal App Migration

```bash
fastappkit migrate app <name> makemigrations -m "message"
```

**Options:**

-   `-m, --message`: Migration message (required)

This command must be run from the project root directory.

!!! important "Migration Location"
Internal app migrations are created in `core/db/migrations/versions/`, NOT in `apps/<name>/migrations/`. Internal apps share the project's migration timeline with core migrations. **Internal apps can only create migrations** - they cannot use `preview`, `upgrade`, or `downgrade` actions. For preview/upgrade/downgrade operations, use the unified commands below (which operate on all core + internal app migrations together).

**Autogenerate Behavior:**

-   Uses full project metadata (all internal apps + core models)
-   Good for cross-app relationships and shared schema
-   Migration files are shared across all internal apps and core

## Unified Migration Operations

Since core and internal app migrations share the same directory (`core/db/migrations/`) and version table, use these unified commands for preview, upgrade, and downgrade:

### Preview SQL

```bash
fastappkit migrate preview [--revision <rev>]
```

### Apply Migrations

```bash
fastappkit migrate upgrade [--revision <rev>]
```

### Downgrade

```bash
fastappkit migrate downgrade <revision>
```

**Options:**

-   `--revision, -r`: Specific revision (default: `head` for upgrade/preview)

!!! note "Project Root Required"
These commands must be run from the project root directory. They operate on all migrations in `core/db/migrations/versions/`, which includes both core migrations and internal app migrations.

## External App Migrations

External apps have isolated migrations that are developed independently.

### Development (in external app directory)

```bash
cd <external-app>/
alembic revision --autogenerate -m "message"
alembic upgrade head
```

### From Core Project

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

This command must be run from the project root directory.

!!! important "External App Limitations"
External apps **cannot create migrations** from the core project (`makemigrations` is not supported for external apps). They must be developed independently in their own directory using standard Alembic commands. External apps can only use `upgrade`, `downgrade`, and `preview` actions from the core project.

**Error Handling:**

-   If no migration files found, shows helpful error with instructions
-   If revision not found, provides tips for independent development
-   Uses core project's `DATABASE_URL` (not external app's `alembic.ini`)

## Apply All Migrations

Apply all migrations in the correct order:

```bash
fastappkit migrate all
```

This command must be run from the project root directory.

**Execution Order:**

1. Core migrations (always first)
2. Internal apps (in config order) - skipped (already included in core migrations)
3. External apps (in config order)

!!! tip "Recommended Command"
This is the **recommended command** for normal workflows. Internal apps are skipped because they share core's migration directory. Shows progress for each step. Fails fast if any migration fails.

## Migration Safety

### Downgrades

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

## Migration Ordering

Migrations run in this order:

1. **Core** (always first)
2. **Internal apps** (order from `fastappkit.toml`)
3. **External apps** (order from `fastappkit.toml`)

You can override internal app order in config:

```toml
[tool.fastappkit.migration]
order = ["core", "auth", "blog"]
```

## Autogenerate Behavior

### Internal Apps

Autogenerate sees:

-   All internal app models
-   All core models
-   Cross-app relations

Good for teams working on shared schema.

### External Apps

Autogenerate sees:

-   Only that app's own models
-   No internal app models
-   No other external apps' models
-   No core models

If an external app tries to import foreign models → validation error.

## Best Practices

1. Keep migration files in VCS and package them with external apps
2. Run `makemigrations` locally and test upgrades in staging
3. Use per-app version tables for external apps (automatic)
4. Prefer explicit `models_module` in manifest
5. Avoid cross-app model imports in external apps
6. Review SQL via `preview` before applying migrations
7. Test downgrades to ensure migrations are reversible

## Learn More

-   [Migration System](../topics/migration-system.md) - Deep dive into migration architecture
-   [CLI Reference](../reference/cli-reference.md) - Complete migration command reference
