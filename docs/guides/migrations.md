# Migrations

Complete migration workflow guide for fastappkit.

## Migration System Overview

fastappkit provides unified migration management across core, internal apps, and external apps.

### Core Migrations

-   **Location**: `core/db/migrations/`
-   **Purpose**: Core-level schema changes
-   **Version Table**: `alembic_version` (shared)

### Internal App Migrations

-   **Location**: `core/db/migrations/` (shared with core)
-   **Purpose**: Internal app schema changes
-   **Version Table**: `alembic_version` (shared with core)
-   **Autogenerate**: Sees all internal app models + core models

### External App Migrations

-   **Location**: `<app>/<app>/migrations/` (isolated per app)
-   **Purpose**: External app schema changes
-   **Version Table**: `alembic_version_<appname>` (per-app)
-   **Autogenerate**: Sees only that app's models

## Core Migrations

### Create Migration

```bash
fastappkit migrate core -m "message"
```

**IMPORTANT**: Must be run from project root.

**When to Use:**
-   Core-level schema changes
-   Shared infrastructure tables (sessions, logs, etc.)

**Uses**: Core project's `DATABASE_URL` from `.env`.

## Internal App Migrations

### Create Migration

```bash
fastappkit migrate app <name> makemigrations -m "message"
```

**IMPORTANT**: Must be run from project root.

**CRITICAL**: Shared migration directory with core (`core/db/migrations/`).

**Migration Order:**
-   From `fastappkit.toml` apps order, or
-   From `[tool.fastappkit.migration.order]` if specified

**Autogenerate Behavior:**
-   Sees all internal app models
-   Sees all core models
-   Can detect cross-app relationships

**Cannot Use Per-App Commands:**
-   `upgrade`/`downgrade` per-app not supported
-   Use unified commands: `fastappkit migrate upgrade`

## External App Migrations

### Creating Migrations

**CRITICAL**: External apps cannot create migrations from core project. Use Alembic directly:

```bash
cd <external-app>
alembic revision --autogenerate -m "message"
```

**Uses**: External app's `.env` and `DATABASE_URL` when developing independently.

### Applying from Core

```bash
fastappkit migrate app <name> upgrade
```

**Uses**: Core project's `DATABASE_URL` when integrated.

**IMPORTANT**:
-   External apps cannot create migrations from core project
-   Must have `migrations/env.py` with correct version table (`alembic_version_<appname>`)

## Unified Commands

### Apply All Migrations

```bash
fastappkit migrate all
```

**IMPORTANT**: Must be run from project root.

**Execution Order:**
1. Core migrations (always first)
2. Internal apps (skipped - already included in core migrations)
3. External apps (in `fastappkit.toml` order)

**Recommended**: Use this command for normal workflows.

### Upgrade Core + Internal

```bash
fastappkit migrate upgrade [--revision <rev>]
```

**IMPORTANT**: Must be run from project root.

Applies core and internal app migrations (shared directory).

### Downgrade

```bash
fastappkit migrate downgrade <revision>
```

Downgrades core and internal app migrations.

### Preview SQL

```bash
fastappkit migrate preview [--revision <rev>]
```

Shows SQL that would be executed without applying.

## Migration Workflow Examples

### Adding a New Model

1. **Add model to `apps/blog/models.py`:**
   ```python
   from core.models import Base
   from sqlalchemy import Column, Integer, String

   class Post(Base):
       __tablename__ = "posts"
       id = Column(Integer, primary_key=True)
       title = Column(String)
   ```

2. **Create migration:**
   ```bash
   fastappkit migrate app blog makemigrations -m "Add post model"
   ```

3. **Review migration** (optional):
   ```bash
   fastappkit migrate preview
   ```

4. **Apply migration:**
   ```bash
   fastappkit migrate all
   ```

### Modifying Existing Model

1. **Modify model:**
   ```python
   class Post(Base):
       __tablename__ = "posts"
       id = Column(Integer, primary_key=True)
       title = Column(String)
       content = Column(String)  # Added field
   ```

2. **Create migration:**
   ```bash
   fastappkit migrate app blog makemigrations -m "Add content to post"
   ```

3. **Apply:**
   ```bash
   fastappkit migrate all
   ```

### Adding Relationships

1. **Add relationship:**
   ```python
   from sqlalchemy import ForeignKey
   from sqlalchemy.orm import relationship
   from apps.auth.models import User

   class Post(Base):
       __tablename__ = "posts"
       id = Column(Integer, primary_key=True)
       author_id = Column(Integer, ForeignKey("users.id"))
       author = relationship("User", back_populates="posts")
   ```

2. **Create migration:**
   ```bash
   fastappkit migrate app blog makemigrations -m "Add author relationship"
   ```

3. **Apply:**
   ```bash
   fastappkit migrate all
   ```

## Migration Commands Quick Reference

| Command | Purpose | Applies To |
|---------|---------|------------|
| `fastappkit migrate core -m "msg"` | Create core migration | Core only |
| `fastappkit migrate app <name> makemigrations -m "msg"` | Create app migration | Internal only |
| `fastappkit migrate all` | Apply all migrations | All |
| `fastappkit migrate upgrade` | Apply core + internal | Core + Internal |
| `fastappkit migrate app <name> upgrade` | Apply app migration | External |
| `fastappkit migrate preview` | Preview SQL | Core + Internal |
| `fastappkit migrate downgrade <rev>` | Downgrade | Core + Internal |

## Troubleshooting

### Migration Conflicts

**Problem**: Multiple migrations modify same table

**Solution**:
-   Review migration files
-   Merge changes if needed
-   Ensure migrations are in correct order

### Downgrade Issues

**Problem**: Downgrade fails or causes data loss

**Solution**:
-   Review downgrade SQL: `fastappkit migrate preview`
-   Backup database before downgrading
-   Test downgrades in development first

### External App Migration Problems

#### Revision Not Found

**Error**: `Can't locate revision identified by '...'`

**Solution**:
-   Check migration files exist in external app's `migrations/versions/`
-   Verify external app was developed independently
-   Ensure migrations are included in package

#### Wrong Version Table

**Error**: Version table conflicts

**Solution**:
-   Check `migrations/env.py` has `alembic_version_<appname>`
-   Should NOT use shared `alembic_version` table

#### Database Connection Fails

**Error**: Connection errors when applying migrations

**Solution**:
-   Check `DATABASE_URL` (uses core's when integrated)
-   Verify database is running and accessible
-   Check connection string format

### Migration Directory Not Found

**Error**: `Core migrations directory not found`

**Solution**:
-   Verify project structure
-   Ensure project was created correctly
-   Check `core/db/migrations/` exists

### All Commands Must Run from Project Root

**CRITICAL**: All migration commands must be run from project root (where `fastappkit.toml` is located).

**Error**: `Configuration file not found`

**Solution**: `cd` to project root before running commands.

## Next Steps

-   [Development Workflow](development-workflow.md) - Day-to-day development
-   [Migration System](../topics/migration-system.md) - Deep dive into migrations
-   [CLI Reference](../reference/cli-reference.md) - Complete command reference
