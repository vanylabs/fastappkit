# Architecture

Internal architecture overview of how fastappkit works.

## Component Overview

fastappkit consists of several key components:

-   **AppLoader**: Discovers and loads apps from configuration
-   **AppResolver**: Resolves app entries to actual locations
-   **ManifestLoader**: Loads external app manifests
-   **EntrypointLoader**: Loads and validates entrypoint functions
-   **RouterAssembler**: Mounts routers to FastAPI app
-   **MigrationRunner**: Executes migrations in correct order
-   **MigrationOrderer**: Determines migration execution order
-   **IsolationValidator**: Validates app isolation rules

## App Loading Process

### 1. Configuration Loading

```python
# Load fastappkit.toml
config = load_config(project_root)
apps_list = config.get("apps", [])
```

### 2. App Resolution

For each app entry:

```python
# Internal app: "apps.blog"
if entry.startswith("apps."):
    app_name = entry.split(".", 1)[1]
    app_path = project_root / "apps" / app_name
    # Verify exists and has __init__.py

# External app: "payments"
else:
    module = importlib.import_module(entry)
    # Verify importable and has manifest
```

### 3. Manifest Loading

For external apps:

```python
# Load fastappkit.toml from package directory
manifest = load_manifest(app_info)
# Validate required fields
```

### 4. Entrypoint Validation

```python
# Validate entrypoint is importable
entrypoint = manifest.get("entrypoint", f"{app_name}:register")
load_entrypoint(entrypoint, app_info.import_path)
```

### 5. App Registration

```python
# Execute register() function
router = register(app)
# Store router for mounting
```

## Registration Execution

When `FastAppKit.create_app()` is called:

1. **Create FastAPI app instance**
2. **Load all apps** via `AppLoader`
3. **Execute registrations** for each app:
   ```python
   for app_metadata in registry.list():
       router = execute_registration(app_metadata, app)
       app_metadata.router = router
   ```
4. **Mount routers** via `RouterAssembler`

## Router Assembly

After all apps are registered:

1. **Mount routers** in order from `fastappkit.toml`
2. **Check for collisions** after all mounts
3. **Emit warnings** if collisions detected (not fatal)

```python
for app_metadata in registry.list():
    if app_metadata.router:
        prefix = app_metadata.prefix  # From manifest or default
        app.include_router(app_metadata.router, prefix=prefix)
```

## Settings Management

### Initialization Flow

1. **Project defines Settings** in `core/config.py`
2. **Settings initialized** in `core/app.py`:
   ```python
   settings = Settings()  # Loads from .env
   ```
3. **FastAppKit created** with settings:
   ```python
   kit = FastAppKit(settings=settings)
   # Calls set_settings() internally
   ```
4. **Global access** via `get_settings()`:
   ```python
   settings = get_settings()  # Returns global instance
   ```

### CLI Commands

CLI commands use `ensure_settings_loaded()`:

```python
def ensure_settings_loaded(project_root: Path) -> None:
    # Imports core.app, which initializes Settings
    import core.app
```

This ensures settings are available for migration commands.

## Migration System Internals

### Migration Ordering

1. **Core** (always first)
2. **Internal apps** (from `fastappkit.toml` or `[tool.fastappkit.migration.order]`)
3. **External apps** (from `fastappkit.toml`)

### Version Tables

-   **Core + Internal**: `alembic_version` (shared)
-   **External**: `alembic_version_<appname>` (per-app)

### Migration Execution

For each app:
1. Build Alembic config
2. Load migration scripts
3. Check database state
4. Determine upgrade path
5. Execute migrations

## Learn More

-   [Extending FastAppKit](extending-fastappkit.md) - Customization guide
-   [Best Practices](best-practices.md) - Recommended patterns
