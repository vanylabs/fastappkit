# Creating Apps

Detailed guide to creating internal and external apps.

## Internal Apps

### Command

```bash
fastappkit app new <name>
```

**IMPORTANT**: Must be run from project root (where `fastappkit.toml` is located).

### What Gets Created

```
apps/<name>/
├── __init__.py    # register() function
├── models.py      # SQLAlchemy models (imports Base from core.models)
└── router.py      # FastAPI router
```

### Structure Explanation

#### `apps/<name>/__init__.py`

Contains the `register()` function:

```python
from fastapi import APIRouter, FastAPI
from fastappkit.conf import get_settings

router = APIRouter()

@router.get("/posts")
def list_posts():
    return [{"id": 1, "title": "Hello"}]

def register(app: FastAPI) -> APIRouter | None:
    """Register this app with the FastAPI application."""
    settings = get_settings()
    return router  # Return router for auto-mount, or None for manual mount
```

**Signature**: `register(app: FastAPI) -> APIRouter | None`
-   Return `APIRouter` for auto-mount
-   Return `None` for manual mount (app handles mounting itself)

#### `apps/<name>/models.py`

SQLAlchemy models:

```python
from core.models import Base
from sqlalchemy import Column, Integer, String

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
```

**CRITICAL**: Must import `Base` from `core.models`, not create own.

#### `apps/<name>/router.py`

FastAPI router:

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_root():
    return {"message": "Hello from blog app"}
```

### Registration Function

The `register()` function is called by fastappkit when loading apps:

```python
def register(app: FastAPI) -> APIRouter | None:
    """
    Register this app with the FastAPI application.

    Args:
        app: FastAPI application instance

    Returns:
        APIRouter if app should auto-mount router, None for manual mount
    """
    # Access settings if needed
    settings = get_settings()

    # Return router for auto-mount
    return router

    # Or return None for manual mount
    # app.include_router(router, prefix="/custom")
    # return None
```

### Models

**CRITICAL**: Internal apps must import `Base` from `core.models`:

```python
from core.models import Base  # CORRECT
```

**NOT**:
```python
from sqlalchemy.orm import DeclarativeBase
class Base(DeclarativeBase):  # WRONG for internal apps
    pass
```

**Allowed**:
-   Can import models from other internal apps
-   Can import from `core.models`
-   Cannot import from external apps

### Router Creation

Create routes in `router.py`:

```python
from fastapi import APIRouter
from apps.blog.models import Post

router = APIRouter()

@router.get("/posts")
def list_posts():
    return {"posts": []}

@router.post("/posts")
def create_post():
    return {"message": "Post created"}
```

**IMPORTANT**: Automatically added to `fastappkit.toml` by CLI.

## External Apps

### Command

```bash
fastappkit app new <name> --as-package
```

Can be run anywhere (not required to be in project root).

### What Gets Created

```
<name>/
├── <name>/              # Package directory
│   ├── __init__.py      # register() function
│   ├── models.py        # SQLAlchemy models (own Base class)
│   ├── router.py        # FastAPI router
│   ├── config.py        # Settings (for independent development)
│   ├── fastappkit.toml  # Manifest (in package directory)
│   └── migrations/      # Isolated migrations
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
├── pyproject.toml       # Package metadata
├── alembic.ini          # For independent development
├── .env                 # Environment variables (for independent development)
└── README.md
```

### Structure Explanation

#### `<name>/<name>/__init__.py`

Same `register()` function signature as internal apps.

#### `<name>/<name>/models.py`

**CRITICAL**: External apps must use own `Base` class:

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
```

**NOT**:
```python
from core.models import Base  # WRONG for external apps
```

**Restricted**:
-   Cannot import from core or internal apps
-   Isolation enforced by validation

#### `<name>/<name>/fastappkit.toml`

Manifest file (in package directory):

```toml
[tool.fastappkit]
name = "payments"
version = "0.1.0"
entrypoint = "payments:register"
migrations = "migrations"
models_module = "payments.models"
route_prefix = "/payments"
```

**Location**: Must be in package directory, not project root.

#### `<name>/<name>/migrations/`

Isolated migrations directory:
-   Has its own `env.py` with isolated version table
-   Version table: `alembic_version_<appname>`
-   Not shared with core or other apps

### Independent Development Setup

#### 1. Install Package

**CRITICAL**: External apps MUST be pip-installed:

```bash
cd <name>
pip install -e .
```

#### 2. Configure `.env`

Edit `.env` file in external app directory:

```bash
DATABASE_URL=sqlite:///./payments.db
DEBUG=false
```

#### 3. Use Alembic Directly

**CRITICAL**: External apps cannot use `fastappkit migrate`. Use Alembic directly:

```bash
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

#### 4. Test Independently

```bash
uvicorn main:app --reload
```

Uses external app's `.env` and `DATABASE_URL`.

## Best Practices

### Naming Conventions

-   Use lowercase with underscores: `blog`, `user_auth`, `payment_processing`
-   Alphanumeric, hyphens, and underscores only
-   Avoid Python keywords
-   Keep names descriptive but concise

### App Organization

**Internal Apps:**
-   One app per feature/domain
-   Group related functionality together
-   Use clear, descriptive names

**External Apps:**
-   Design for reusability
-   Keep dependencies minimal
-   Document requirements clearly

### When to Use Internal vs External

**Use Internal Apps When:**
-   Feature is project-specific
-   You need shared migrations
-   You want tight integration with core

**Use External Apps When:**
-   Component is reusable across projects
-   You want isolated migrations
-   You plan to publish to PyPI
-   Component should be independent

## Common Issues

### Missing `__init__.py`

**Error**: `AppLoadError: App directory is not a Python package`

**Solution**: Ensure `apps/<name>/__init__.py` exists (created by CLI, but verify if manual).

### External App Not Pip-Installed

**Error**: `ImportError` or `AppLoadError: Could not resolve app entry`

**Solution**: Install package: `pip install -e .` (even for local development).

### Wrong `Base` Class in External App

**Error**: Isolation validation error

**Solution**: External apps must use own `Base` class (DeclarativeBase), not `core.models.Base`.

### Missing Manifest for External App

**Error**: `AppLoadError: Failed to load manifest`

**Solution**: Ensure `fastappkit.toml` exists in package directory (`<app>/<app>/fastappkit.toml`).

### Duplicate App Names

**Warning**: `Duplicate app names detected`

**Solution**: Rename one of the apps or check if multiple entries resolve to same name.

## Next Steps

-   [Migrations](migrations.md) - Create and manage migrations
-   [Development Workflow](development-workflow.md) - Day-to-day development
-   [External App Manifest](../configuration/external-app-manifest.md) - Manifest reference
