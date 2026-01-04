# Scenario 3: Full Ecosystem

This guide covers using both internal and external apps together - the full fastappkit ecosystem.

## When to Use This Approach

Use the full ecosystem when:

-   You're building reusable components
-   You want to share apps across projects
-   You need isolated migrations for plugins
-   You're building a plugin ecosystem
-   You want both project-specific (internal) and reusable (external) apps

## Two Development Modes

You can develop external apps in two ways:

-   **Mode A**: Develop external app separately, then integrate
-   **Mode B**: Develop everything together (monorepo style)

Choose based on your workflow preferences.

---

## Mode A: Separate Development

Develop external apps independently, then integrate with the core project.

### Part 1: Create External App (Independent)

#### Step 1: Create External App

```bash
fastappkit app new payments --as-package
cd payments
```

This creates a complete external app structure:
-   `payments/payments/` (package directory)
-   `payments/payments/fastappkit.toml` (manifest)
-   `payments/payments/migrations/` (isolated migrations)
-   `payments/pyproject.toml`
-   `payments/alembic.ini` (for independent development)

#### Step 2: Install the Package

**CRITICAL**: External apps MUST be pip-installed (no filesystem paths):

```bash
pip install -e .
```

This makes the package importable, which is required for fastappkit to resolve it.

#### Step 3: Update Dependency Versions

**IMPORTANT**: Update dependency versions in `pyproject.toml` to match core project:

```toml
[tool.poetry.dependencies]
python = ">=3.11,<4.0"
fastapi = ">=0.120.0,<0.130"  # Match core project
sqlalchemy = ">=2.0,<3.0"
alembic = ">=1.17.2,<1.18"
```

#### Step 4: Configure Environment

Edit `.env` file in external app directory (for independent development):

```bash
DATABASE_URL=sqlite:///./payments.db
DEBUG=false
```

#### Step 5: Develop Independently

**Add models** to `payments/payments/models.py`:

```python
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String

# CRITICAL: External apps must use own Base class
class Base(DeclarativeBase):
    pass

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    amount = Column(Integer)
    status = Column(String)
```

**IMPORTANT**: External apps must use their own `Base` class (DeclarativeBase), NOT `core.models.Base`.

**Create migrations** using Alembic directly (NOT `fastappkit migrate`):

```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

**Test independently:**

```bash
uvicorn main:app --reload
```

This uses the external app's `.env` and `DATABASE_URL`.

#### Step 6: Publish or Use Locally

When ready:
-   Publish to PyPI, or
-   Use locally with `pip install -e /path/to/payments`

### Part 2: Integrate with Core Project

#### Step 1: Install in Core Project

In your core project directory:

```bash
pip install -e /path/to/payments
# or from PyPI:
pip install payments-app
```

**CRITICAL**: Must be pip-installed, cannot use filesystem path directly in `fastappkit.toml`.

#### Step 2: Add to Configuration

Edit `fastappkit.toml` in core project:

```toml
[tool.fastappkit]
apps = [
  "apps.blog",      # Internal app
  "payments",       # External app (package name, not path)
]
```

**IMPORTANT**: Use package name, not filesystem path.

#### Step 3: Apply Migrations

**IMPORTANT**: External app will use core project's `DATABASE_URL` when integrated:

```bash
fastappkit migrate app payments upgrade
```

This applies the external app's migrations to the core project's database.

#### Step 4: Start Core Server

```bash
fastappkit core dev
```

The external app is now integrated and routes are mounted automatically.

---

## Mode B: Monorepo Development

Develop core project and external apps together in the same repository.

#### Step 1: Create Core Project

```bash
fastappkit core new myproject
cd myproject
```

#### Step 2: Update Dependency Versions

**IMPORTANT**: Update dependency versions in core project's `pyproject.toml`:

```toml
[tool.poetry.dependencies]
python = ">=3.11,<4.0"
fastapi = ">=0.120.0,<0.130"
sqlalchemy = ">=2.0,<3.0"
alembic = ">=1.17.2,<1.18"
```

#### Step 3: Create External App in Same Repo

```bash
fastappkit app new payments --as-package
```

This creates `payments/` directory in the same repo.

#### Step 4: Install External App

**CRITICAL**: Install external app (must be pip-installed even in monorepo):

```bash
pip install -e ./payments
```

#### Step 5: Match Dependency Versions

Ensure external app's dependency versions match core project (edit `payments/pyproject.toml`).

#### Step 6: Add to Configuration

Edit `fastappkit.toml`:

```toml
[tool.fastappkit]
apps = [
  "apps.blog",
  "payments",  # Package name
]
```

#### Step 7: Develop Both Together

You can now:
-   Edit core project code
-   Edit external app code
-   Test both together

#### Step 8: Test External App Independently

```bash
cd payments
uvicorn main:app --reload
```

Uses external app's `.env` and `DATABASE_URL`.

#### Step 9: Test Integrated

```bash
cd ..
fastappkit core dev
```

Uses core project's `DATABASE_URL`.

---

## Critical Gotchas

### External Apps MUST be Pip-Installed

-   External apps **MUST** be pip-installed (even for local dev: `pip install -e .`)
-   Filesystem paths are NOT supported in `fastappkit.toml`
-   This is enforced by the resolver (uses `importlib.import_module()`)

### Database URL Differences

-   **Independent development**: External app uses its own `.env` and `DATABASE_URL`
-   **Integrated**: External app uses core project's `DATABASE_URL` (from core's `.env`)

### Migration Creation

-   External apps **cannot** create migrations from core project
-   Must use `alembic` directly: `alembic revision --autogenerate -m "message"`
-   From core project, you can only apply existing migrations: `fastappkit migrate app <name> upgrade`

### Manifest Location

-   External apps must have `fastappkit.toml` manifest in package directory (`<app>/<app>/fastappkit.toml`)
-   NOT in project root, NOT in `pyproject.toml`
-   Must be included when package is published to PyPI

### Version Table

-   External apps must have correct version table in `migrations/env.py`
-   Should be `alembic_version_<appname>`, NOT `alembic_version`
-   Check the generated `migrations/env.py` file

### Base Class

-   External apps must use own `Base` class (DeclarativeBase)
-   Cannot import `Base` from `core.models`
-   Isolation validation enforces this

## Quick Commands Reference

```bash
# Create external app
fastappkit app new payments --as-package
cd payments
pip install -e .

# Develop independently
alembic revision --autogenerate -m "initial"
uvicorn main:app --reload

# Integrate with core project
cd /path/to/core/project
pip install -e /path/to/payments
# Add "payments" to fastappkit.toml
fastappkit migrate app payments upgrade
fastappkit core dev
```

## Development Workflow

### Independent Development (External App)

1. Make changes to external app code
2. Create migration: `alembic revision --autogenerate -m "message"`
3. Test: `uvicorn main:app --reload`
4. When ready, publish or use locally

### Integrated Development (Core Project)

1. Install external app: `pip install -e /path/to/app`
2. Add to `fastappkit.toml`: `"app_name"`
3. Apply migrations: `fastappkit migrate app app_name upgrade`
4. Test: `fastappkit core dev`

## Testing Approaches

### Test External App Independently

```bash
cd <external-app>
uvicorn main:app --reload
# Uses external app's .env and DATABASE_URL
```

### Test Integrated

```bash
cd <core-project>
fastappkit core dev
# Uses core project's DATABASE_URL
```

### Manual Testing

```bash
# Test external app endpoints
curl http://127.0.0.1:8000/payments/

# Test integrated endpoints
curl http://127.0.0.1:8000/blog/posts
curl http://127.0.0.1:8000/payments/transactions
```

## Next Steps

-   [Creating Apps](../guides/creating-apps.md) - Detailed app creation guide
-   [Configuration](../configuration/index.md) - All configuration options
-   [External App Manifest](../configuration/external-app-manifest.md) - Manifest format reference
