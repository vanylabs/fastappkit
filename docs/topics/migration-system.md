# Migration System

fastappkit uses a unified migration runner that coordinates database schema management across core, internal apps, and external apps.

## Architecture

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

- **Core & Internal Apps:** Use shared `alembic_version` table
- **External Apps:** Use per-app tables (`alembic_version_<appname>`)

## Migration Execution Flow

### For External App Upgrade

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

### Edge Cases

- Database has revision `X` but migration file doesn't exist → Error
- Migration file references non-existent `down_revision` → Error
- Empty migration directory → Error (external apps must have migrations)

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

- All internal app models
- All core models
- Cross-app relations

Good for teams working on shared schema.

### External Apps

Autogenerate sees:

- Only that app's own models
- No internal app models
- No other external apps' models
- No core models

If an external app tries to import foreign models → validation error.

## Learn More

- [Migrations Guide](../guides/migrations.md) - How to work with migrations
- [CLI Reference](../reference/cli-reference.md) - Migration commands
