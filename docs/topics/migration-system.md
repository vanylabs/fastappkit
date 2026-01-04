# Migration System

How fastappkit's migration system works internally.

## Migration Architecture

fastappkit uses a unified migration runner that coordinates database schema management across core, internal apps, and external apps.

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

## Version Tables

-   **Core & Internal Apps**: Use shared `alembic_version` table
-   **External Apps**: Use per-app tables (`alembic_version_<appname>`)

This isolation ensures external apps don't conflict with each other or with core/internal migrations.

## Migration Execution Flow

### For Core + Internal Apps

1. **Load Migration Directory**
   -   Location: `core/db/migrations/`
   -   Shared by core and all internal apps

2. **Build Revision Graph**
   -   Scan `versions/` directory for migration files
   -   Parse revision IDs and dependencies
   -   Determine `head` revision

3. **Check Database State**
   -   Connect to database
   -   Check `alembic_version` table
   -   Read current revision

4. **Determine Upgrade Path**
   -   Compare current revision with `head`
   -   Build list of migrations to apply (in order)

5. **Execute Migrations**
   -   For each migration: execute `upgrade()`, update version table, commit

### For External App Upgrade

1. **App Resolution & Validation**
   -   Resolve app from `fastappkit.toml`
   -   Load manifest
   -   Validate app exists and is external type
   -   Get `migrations_path` from manifest

2. **Build Alembic Config**
   -   Set `script_location` = external app's migrations directory
   -   Set `version_table` = `alembic_version_<appname>`
   -   Set `sqlalchemy.url` = core project's `DATABASE_URL` (from settings)
   -   Set `config_file_name = None` (don't read external app's `alembic.ini`)

3. **Load Migration Scripts**
   -   Create `ScriptDirectory` from migration folder
   -   Scan `migrations/versions/` for `.py` files
   -   Parse revision IDs and build revision graph
   -   Determine `head` revision

4. **Check Database State**
   -   Connect to core project's database
   -   Check if `alembic_version_<appname>` table exists
   -   Read current revision (or `None` if first time)

5. **Determine Upgrade Path**
   -   Compare current revision with `head`
   -   Build list of migrations to apply (in order)

6. **Execute Migrations**
   -   For each migration: execute `upgrade()`, update version table, commit
   -   Create version table if it doesn't exist (first migration)

## Migration Ordering

Migrations run in this order:

1. **Core** (always first)
2. **Internal apps** (order from `fastappkit.toml` or `[tool.fastappkit.migration.order]`)
3. **External apps** (order from `fastappkit.toml`)

You can override internal app order in config:

```toml
[tool.fastappkit.migration]
order = ["core", "auth", "blog"]
```

**Note**: `"core"` is a special value (always first). Only affects internal apps.

## Autogenerate Behavior

### Internal Apps

Autogenerate sees:

-   All internal app models
-   All core models
-   Cross-app relationships

**Good for**: Teams working on shared schema.

### External Apps

Autogenerate sees:

-   Only that app's own models
-   No internal app models
-   No other external apps' models
-   No core models

**If an external app tries to import foreign models** → validation error.

## Edge Cases

### Database Has Revision But File Missing

**Error**: `Can't locate revision identified by '...'`

**Cause**: Database has revision stored but migration file doesn't exist.

**Solution**:
-   Check migration files exist
-   Restore missing migration file
-   Or reset version table (if safe)

### Migration File References Non-Existent `down_revision`

**Error**: Migration dependency chain broken

**Solution**:
-   Review migration files
-   Fix `down_revision` references
-   Ensure migration chain is complete

### Empty Migration Directory

**Problem**: External app has no migrations

**Solution**:
-   Create initial migration: `alembic revision --autogenerate -m "initial"`
-   Ensure `migrations/versions/` directory exists

## Learn More

-   [Migrations Guide](../guides/migrations.md) - Migration workflows
-   [CLI Reference](../reference/cli-reference.md) - Migration commands
