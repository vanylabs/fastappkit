# Creating Apps

This guide covers creating and managing apps in fastappkit projects.

## Internal Apps

Internal apps are project-specific modules that live in your project's `apps/` directory.

### Create an Internal App

```bash
fastappkit app new <name>
```

This command must be run from the project root directory (where `fastappkit.toml` is located).

### What Gets Created

```
apps/<name>/
├── __init__.py      # register(app: FastAPI) function
├── models.py        # SQLAlchemy models
└── router.py        # FastAPI routers
```

!!! important "Migration Directory"
Internal apps do NOT have their own `migrations/` directory. They use the core's migration directory (`core/db/migrations/`).

### Entrypoint Patterns

fastappkit supports two patterns for registering routers:

#### Pattern 1: Return Router (Recommended)

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
    settings = get_settings()  # Access settings
    # Return router - fastappkit will mount it with prefix from manifest
    return router
```

#### Pattern 2: Mount Router Yourself

```python
# apps/blog/__init__.py
from fastapi import APIRouter, FastAPI
from fastappkit.conf import get_settings

router = APIRouter()

@router.get("/posts")
def list_posts():
    return [{"id": 1, "title": "Hello"}]

def register(app: FastAPI) -> None:
    """Register this app with the FastAPI application."""
    settings = get_settings()  # Access settings
    # Mount router yourself - fastappkit will skip mounting
    app.include_router(router, prefix="/blog")
    # Can also use custom prefix, tags, dependencies, etc.
    # app.include_router(router, prefix="/api/blog", tags=["blog"])
```

### Customization Options

-   **Access Settings:** Use `get_settings()` to access configuration
-   **Custom Prefix:** Override manifest `route_prefix` by mounting yourself
-   **Router Tags:** Add tags when mounting: `app.include_router(router, tags=["blog"])`
-   **Dependencies:** Add dependencies: `app.include_router(router, dependencies=[Depends(...)])`
-   **Startup/Shutdown Events:** Register events: `@app.on_event("startup")`
-   **Middleware:** Add middleware in `register()`: `app.add_middleware(...)`
-   **Background Tasks:** Register background tasks: `app.add_task(...)`
-   **Exception Handlers:** Add exception handlers: `app.add_exception_handler(...)`

## External Apps

External apps are reusable packages that can be installed via pip and plugged into any fastappkit project.

### Create an External App

```bash
fastappkit app new <name> --as-package
```

The `--as-package` flag is required for external apps.

This command must be run from the project root directory (where `fastappkit.toml` is located).

### What Gets Created

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

### External App Manifest

External apps must declare metadata in `fastappkit.toml` located inside the package directory:

**Location:** `<app_name>/<app_name>/fastappkit.toml`

**Example:**

```toml
name = "blog"
version = "0.1.0"
entrypoint = "blog:register"
migrations = "migrations"
models_module = "blog.models"
route_prefix = "/blog"
```

!!! important "Manifest Location"
The manifest is stored in `fastappkit.toml` inside the package directory (`<name>/<name>/fastappkit.toml`), not in `pyproject.toml`. This ensures it's included when the package is published to PyPI. Internal apps do not need a manifest file - their metadata is inferred from the directory structure.

### Required Manifest Fields

-   `name`: App name (string)
-   `version`: Semantic version (string)
-   `entrypoint`: Dotted path to register function (e.g., `"blog:register"`)
-   `migrations`: Path to migrations directory (relative to package directory, typically `"migrations"`)
-   `models_module`: Dotted path to models module (recommended)

### Optional Manifest Fields

-   `route_prefix`: Router prefix (default: `/<appname>`)

See the [Manifest Reference](../reference/manifest-reference.md) for complete details.

## Using External Apps

External apps must be installed via `pip` (editable or non-editable) and then added to `fastappkit.toml`:

### Step 1: Install the External App

```bash
# For published packages
pip install external-app-name

# For local development (editable install)
pip install -e /path/to/external-app

# Or add to requirements.txt/pyproject.toml dependencies
```

### Step 2: Add to `fastappkit.toml`

Edit `fastappkit.toml` and add the app to the `apps` list:

```toml
[tool.fastappkit]
apps = [
  "apps.blog",           # Internal app
  "external_app_name",   # External app (package name)
]
```

### App Resolution

The resolver tries methods in this order:

1. **Internal app pattern**: `"apps.<name>"` - checks if entry starts with `apps.` and resolves to `./apps/<name>/`
2. **Package name** (dotted import): `"external_app_name"` - tries to import as Python module using `importlib.import_module()`

!!! important "Pip Installation Required"
External apps must be pip-installed. Filesystem paths are not supported. For local development, use `pip install -e /path/to/app` to install the package in editable mode.

## Listing Apps

List all apps in your project:

```bash
fastappkit app list [--verbose] [--debug] [--quiet]
```

### Options

-   `--verbose, -v`: Show detailed information (import path, migrations path, etc.)
-   `--debug`: Show debug information
-   `--quiet, -q`: Suppress output

This command must be run from the project root directory.

### Output

Shows all apps (internal and external) with:

-   Name
-   Type (internal/external)
-   Route prefix

**Verbose output includes:**

-   Import path
-   Filesystem path (if applicable)
-   Migrations path
-   Manifest details

## Validating Apps

Validate an app's structure and configuration:

```bash
fastappkit app validate <name> [--json]
```

### Options

-   `--json`: Output results as JSON (CI-friendly)

This command must be run from the project root directory.

### What Gets Validated

-   Manifest presence and correctness (required fields, format)
-   Entrypoint importability and signature
-   Migration folder existence (external apps)
-   Version table configuration (external apps)
-   Isolation rules (external apps cannot import internal apps)
-   Duplicate app names (warns if multiple entries resolve to same name)

### Output

-   Human-readable by default (shows errors and warnings)
-   JSON format with `--json` flag (includes `valid`, `errors`, `warnings` arrays)
-   Exit code 1 if validation fails (useful for CI/CD)

## Learn More

-   [Internal Apps](../topics/internal-apps.md) - Deep dive into internal apps
-   [External Apps](../topics/external-apps.md) - Understanding external apps
-   [App Isolation](../topics/app-isolation.md) - Isolation rules and constraints
-   [Router Mounting](../topics/router-mounting.md) - How routers are mounted
