# App Isolation

Isolation rules and validation that ensure apps don't conflict with each other.

## Isolation Rules

fastappkit enforces isolation rules to ensure apps don't conflict with each other and maintain clear boundaries.

```
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

## Internal Apps

**Allowed:**

-   Can depend on other internal apps
-   Can import from `core.models`
-   Can modify shared tables
-   Participate in shared migration timeline (use core's migration directory)
-   No manifest file required (metadata inferred from structure)

**Restricted:**

-   Cannot depend on external apps

## External Apps

**Allowed:**

-   Independent schema evolution (isolated migrations)
-   Can be published to PyPI
-   Must be pip-installed (no filesystem path support)
-   Must have `fastappkit.toml` manifest in package directory
-   Can import from `fastappkit` public API

**Restricted:**

-   Cannot depend on internal apps
-   Cannot import from `core.*` or `apps.*`
-   Cannot touch other apps' tables
-   Cannot modify core or internal tables
-   Cannot create migrations from core project (must use Alembic directly)
-   Must use own `Base` class (DeclarativeBase), not `core.models.Base`

## Validation

fastappkit validates isolation rules when:

-   Loading apps at startup
-   Running `fastappkit app validate <name>`

### Isolation Checks

The isolation validator checks:

1. **Import Analysis**: Scans Python files for imports
2. **Dependency Detection**: Identifies imports from other apps
3. **Rule Enforcement**: Validates against isolation rules

### What Gets Checked

**Manifest Validation:**
-   Required fields are present
-   Field types are correct
-   Entrypoint is importable
-   Entrypoint has correct signature

**Isolation Validation:**
-   External apps: No imports from `core.*` or `apps.*`
-   External apps: Uses own Base class (not `core.models.Base`)
-   Import analysis of Python files

**Migration Validation:**
-   Migrations directory exists
-   `migrations/env.py` exists (external apps)
-   Version table is correct (`alembic_version_<appname>` for external apps)

### Common Violations

#### External App Importing from Core

```python
# WRONG: External app
from core.models import Base  # Violation!

# CORRECT: External app
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass
```

#### External App Importing from Internal App

```python
# WRONG: External app
from apps.blog.models import Post  # Violation!

# CORRECT: External app
# Don't import from internal apps
```

#### External App Using Shared Base

```python
# WRONG: External app
from core.models import Base  # Violation!

# CORRECT: External app
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):
    pass
```

#### Missing Manifest

**Error**: `AppLoadError: Failed to load manifest`

**Solution**: Ensure `fastappkit.toml` exists in package directory.

#### Wrong Version Table

**Error**: Version table conflicts

**Solution**: External apps must use `alembic_version_<appname>`, not `alembic_version`.

## Why Isolation Matters

### Prevents Schema Conflicts

-   External apps can't modify core/internal tables
-   Each external app has isolated migrations
-   Clear boundaries prevent conflicts

### Enables Independent Development

-   External apps can be developed separately
-   Can be published to PyPI
-   Can be versioned independently

### Allows Publishing to PyPI

-   External apps are self-contained
-   No dependencies on project-specific code
-   Can be shared across projects

### Maintains Clear Boundaries

-   Clear separation of concerns
-   Predictable behavior
-   Easier to reason about

## Breaking Scenarios

### External App Imports from Internal App

**Error**: Isolation validation error

**Fix**: Remove import, redesign if needed.

### External App Uses Shared Base

**Error**: Migration conflicts, version table issues

**Fix**: Use own Base class (DeclarativeBase).

### Missing Isolation Checks

**Problem**: Runtime errors, unexpected behavior

**Fix**: Always run `fastappkit app validate <name>` before using apps.

## Running Validation

```bash
fastappkit app validate <name>
```

**Must be run from project root.**

**Output:**
-   Errors: Must be fixed
-   Warnings: Should be reviewed
-   JSON output: `--json` flag for CI

## Learn More

-   [Creating Apps](../guides/creating-apps.md) - App creation guide
-   [External Apps](external-apps.md) - External app details
-   [Internal Apps](internal-apps.md) - Internal app details
