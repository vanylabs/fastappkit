# External Apps

Deep dive into external apps - reusable packages that can be installed via pip and plugged into any fastappkit project.

## Characteristics

-   Installed via `pip install <package>` (must be pip-installed, no filesystem paths)
-   Independent Python packages
-   Must be schema-independent
-   Cannot depend on internal apps
-   Use per-app version tables (`alembic_version_<appname>`)
-   Perfect for reusable plugins

## Structure

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

## Manifest

External apps must declare metadata in `fastappkit.toml` located inside the package directory.

**Location**: `<app_name>/<app_name>/fastappkit.toml`

**Example:**

```toml
[tool.fastappkit]
name = "blog"
version = "0.1.0"
entrypoint = "blog:register"
migrations = "migrations"
models_module = "blog.models"
route_prefix = "/blog"
```

See the [Manifest Reference](../reference/configuration-reference.md) for complete details.

## Models

External apps must use their own `Base` class (isolated metadata):

```python
# <name>/<name>/models.py
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String

class Base(DeclarativeBase):
    pass

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String)
```

!!! warning "Isolation"
    External apps cannot import models from core or internal apps. This is enforced by isolation validation.

## Registration

External apps register with the FastAPI application via a `register()` function:

```python
# <name>/<name>/__init__.py
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

**Signature**: Same as internal apps: `register(app: FastAPI) -> APIRouter | None`

## Installation

External apps must be pip-installed:

```bash
# For published packages
pip install external-app-name

# For local development (editable install)
pip install -e /path/to/external-app
```

Then add to `fastappkit.toml`:

```toml
[tool.fastappkit]
apps = [
  "external_app_name",
]
```

!!! important "Pip Installation Required"
    External apps must be pip-installed. Filesystem paths are not supported. For local development, use `pip install -e /path/to/app` to install the package in editable mode.

## Migrations

External apps have isolated migrations in their own directory. They cannot create migrations from the core project - migrations must be created when developing the external app itself:

```bash
cd <external-app>/
alembic revision --autogenerate -m "message"
```

From the core project, you can apply existing migrations:

```bash
fastappkit migrate app <name> upgrade
```

**Version Table**: Each external app uses `alembic_version_<appname>` (isolated).

## Publishing

External apps can be published to PyPI. The `fastappkit.toml` manifest is included in the package, ensuring it's available when installed.

**Requirements:**
-   Manifest must be in package directory
-   Migrations must be included in package
-   `__init__.py` must exist in package directory

## Best Practices

1. **Design for reusability**
   -   Keep dependencies minimal
   -   Avoid project-specific code
   -   Document requirements clearly

2. **Isolation**
   -   Use own Base class
   -   Don't import from core or internal apps
   -   Keep migrations isolated

3. **Versioning**
   -   Use semantic versioning
   -   Document breaking changes
   -   Match dependency versions with core project

4. **Documentation**
   -   Clear README
   -   Installation instructions
   -   Usage examples

## Limitations

-   **Must be pip-installed** (no filesystem paths)
-   **Cannot depend on internal apps** (isolation rule)
-   **Isolated migrations** (cannot share with core)
-   **Independent development** (migrations created separately)

## Learn More

-   [Creating Apps](../guides/creating-apps.md) - How to create external apps
-   [Migration System](migration-system.md) - How migrations work for external apps
-   [App Isolation](app-isolation.md) - Isolation rules and constraints
-   [Manifest Reference](../configuration/external-app-manifest.md) - Complete manifest schema
