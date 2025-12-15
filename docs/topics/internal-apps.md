# Internal Apps

Internal apps are project-specific modules that live in your project's `apps/` directory.

## Characteristics

- Located in `./apps/<name>/`
- Part of your project's codebase
- Share the project's migration timeline
- Can depend on other internal apps
- Use shared `alembic_version` table
- Not meant for packaging (unless explicitly opted in)

## Structure

```
apps/<name>/
├── __init__.py      # register(app: FastAPI) function
├── models.py        # SQLAlchemy models
└── router.py        # FastAPI routers
```

## Models

Internal apps import `Base` from `core.models` for SQLAlchemy models:

```python
# apps/blog/models.py
from core.models import Base
from sqlalchemy import Column, Integer, String

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
```

## Registration

Internal apps register with the FastAPI application via a `register()` function:

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
    settings = get_settings()
    return router
```

## Migrations

Internal apps share the core's migration directory (`core/db/migrations/`). They do not have their own `migrations/` directory.

When you create a migration for an internal app:

```bash
fastappkit migrate app blog makemigrations -m "Add post model"
```

The migration is created in `core/db/migrations/versions/`, not in `apps/blog/migrations/`.

## Dependencies

Internal apps can depend on other internal apps:

```python
# apps/blog/models.py
from apps.auth.models import User  # OK - internal app can import internal app

class Post(Base):
    __tablename__ = "posts"
    author_id = Column(Integer, ForeignKey("users.id"))
```

!!! warning "External App Dependencies"
    Internal apps cannot depend on external apps. This is enforced by isolation validation.

## Learn More

- [Creating Apps](../guides/creating-apps.md) - How to create internal apps
- [Migration System](migration-system.md) - How migrations work for internal apps
- [App Isolation](app-isolation.md) - Isolation rules and constraints
