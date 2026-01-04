# Common Issues

Solutions to frequent problems when using fastappkit.

## App Fails to Load

**Error**: `AppLoadError: Failed to load app 'blog'`

### Check List

1. App exists in filesystem or is pip-installed
2. Manifest is present and valid (external apps)
3. Entrypoint is importable and has correct signature
4. Migration folder exists (external apps)

### Solution

Run validation for detailed diagnostics:

```bash
fastappkit app validate blog
```

Check error message for specific stage (resolve/load/register).

### Common Causes

-   Missing `__init__.py` in app directory
-   Incorrect entrypoint path in manifest
-   Import errors in app code
-   Missing dependencies

## Migration Revision Not Found

**Error**: `Can't locate revision identified by '0d037769d7fb'`

### Possible Causes

1. Database has revision stored but migration file doesn't exist
2. Migration file references non-existent `down_revision`
3. Wrong database being used (external app using its own DB instead of core's)

### Solution

Check database state:

```sql
SELECT * FROM alembic_version;  -- Core & internal apps
SELECT * FROM alembic_version_<appname>;  -- External apps
```

Verify migration files exist in `migrations/versions/`.

Ensure using core project's `DATABASE_URL` (not external app's).

## Route Collisions

**Warning**: `Route collision detected: /api used by multiple apps`

### Solution

Change `route_prefix` in manifest or register function:

```toml
# fastappkit.toml (external app)
route_prefix = "/api/blog"
```

Or in register function:

```python
def register(app: FastAPI) -> None:
    app.include_router(router, prefix="/api/blog")
```

Ensure each app has unique prefix.

## External App Cannot Create Migrations

**Error**: `Cannot create migrations for external app`

### Explanation

External apps must be developed independently. Migrations created in external app's own directory using `alembic`. Core project only applies existing migrations.

### Solution

```bash
cd <external-app>/
alembic revision --autogenerate -m "message"
# Then from core project:
fastappkit migrate app <name> upgrade
```

## Settings Not Loaded

**Error**: Settings-related errors at runtime

### Solution

Ensure settings are initialized:

```python
# core/app.py
from core.config import Settings
from fastappkit.core.kit import FastAppKit

settings = Settings()
kit = FastAppKit(settings=settings)
app = kit.create_app()
```

For CLI commands, ensure you're in the project root directory.

## Import Errors

**Error**: `ModuleNotFoundError` or import-related errors

### Common Causes

-   Missing `__init__.py` files
-   Incorrect Python path
-   Missing dependencies

### Solution

-   Ensure all app directories have `__init__.py`
-   Check that dependencies are installed
-   Verify Python path includes project root

## Database Connection Errors

**Error**: Database connection failures

### Solution

Check `DATABASE_URL` in `.env`:

```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Verify database is running and accessible.

## Project Creation Errors

**Error**: `Directory already exists`

### Solution

Choose a different project name or remove the existing directory:

```bash
rm -rf existing-project
fastappkit core new myproject
```

## Settings Not Found

**Error**: Settings-related errors when running CLI commands

### Solution

Ensure you're in the project root directory (where `fastappkit.toml` is located):

```bash
cd /path/to/project
fastappkit migrate all
```

Verify `core/config.py` exists and contains a `Settings` class.

## App Not Found in Registry

**Error**: `App 'blog' not found in registry`

### Solution

1. Verify app exists: `fastappkit app list`
2. Check `fastappkit.toml` includes the app
3. For external apps, ensure they're pip-installed
4. Validate app: `fastappkit app validate <name>`

## Migration Directory Not Found

**Error**: `Core migrations directory not found`

### Solution

Ensure the project was created correctly:

```bash
ls -la core/db/migrations/
```

If missing, recreate the project or manually create the directory structure.

## External App Not Pip-Installed

**Error**: `AppLoadError: Could not resolve app entry`

### Solution

External apps must be pip-installed (even for local development):

```bash
pip install -e /path/to/external/app
```

Then add to `fastappkit.toml` as package name (not path).

## Duplicate App Names

**Warning**: `Duplicate app names detected`

### Solution

Rename one of the apps or check if multiple entries resolve to same name:

```bash
fastappkit app list  # Check resolved names
```

## Route Not Accessible

**Problem**: Routes return 404

### Solution

1. Check app is in `fastappkit.toml`
2. Verify `register()` returns `APIRouter` (for auto-mount)
3. Check `route_prefix` in manifest
4. Verify app loaded: `fastappkit app list`

## Learn More

-   [Debugging](debugging.md) - Debugging techniques
-   [CLI Reference](../reference/cli-reference.md) - All commands
