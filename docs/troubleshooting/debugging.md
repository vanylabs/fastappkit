# Debugging

Debugging techniques for fastappkit applications.

## Using `--debug` Flag

Enable debug output to see detailed error information:

```bash
fastappkit core dev --debug
fastappkit app validate <name> --debug
fastappkit migrate all --debug
```

**What you get:**
-   Stack traces
-   Detailed error messages
-   Full exception information
-   Internal state information

## Logging Configuration

Configure logging in `core/app.py`:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
```

### Log Levels

-   **DEBUG**: Detailed information for debugging
-   **INFO**: General information
-   **WARNING**: Warning messages
-   **ERROR**: Error messages
-   **CRITICAL**: Critical errors

## Common Error Messages

### `AppLoadError`

**Format**: `AppLoadError: Failed to load app '<name>' at stage '<stage>'`

**Stages:**
-   `resolve`: App entry couldn't be resolved
-   `manifest`: Manifest loading failed
-   `entrypoint`: Entrypoint loading failed
-   `register`: Registration execution failed
-   `router`: Router mounting failed

**Debugging:**
1. Run `fastappkit app validate <name> --debug`
2. Check specific stage mentioned in error
3. Verify app structure matches requirements

### `ConfigError`

**Format**: `ConfigError: <message>`

**Common causes:**
-   `fastappkit.toml` not found
-   Invalid TOML syntax
-   Missing `[tool.fastappkit]` section

**Debugging:**
1. Verify you're in project root
2. Check `fastappkit.toml` exists
3. Validate TOML syntax

### `ImportError`

**Format**: `ImportError: <module>`

**Common causes:**
-   Missing `__init__.py`
-   Package not installed
-   Incorrect import path

**Debugging:**
1. Check `__init__.py` files exist
2. Verify package is installed: `pip list`
3. Check import path is correct

## Stack Trace Analysis

### Reading Stack Traces

1. **Top of trace**: Most recent call (where error occurred)
2. **Bottom of trace**: Original call site
3. **Look for**: Your code (not library code) for clues

### Common Patterns

**Settings not initialized:**
```
AttributeError: 'NoneType' object has no attribute 'database_url'
```
→ Settings not initialized in `core/app.py`

**App not found:**
```
AppLoadError: Could not resolve app entry
```
→ App not pip-installed or path incorrect

**Migration error:**
```
alembic.util.exc.CommandError: Can't locate revision
```
→ Migration file missing or database out of sync

## Validation Debugging

### Run Validation

```bash
fastappkit app validate <name> --debug
```

### Check Each Stage

1. **Manifest validation**: Required fields, format
2. **Isolation validation**: Import analysis
3. **Migration validation**: Directory structure, version table

### JSON Output

For CI/CD integration:

```bash
fastappkit app validate <name> --json
```

Returns structured JSON with errors and warnings.

## Migration Debugging

### Preview SQL

Before applying migrations:

```bash
fastappkit migrate preview
```

Shows SQL that would be executed.

### Check Database State

```sql
-- Core + internal apps
SELECT * FROM alembic_version;

-- External apps
SELECT * FROM alembic_version_<appname>;
```

### Check Migration Files

```bash
# Core + internal
ls -la core/db/migrations/versions/

# External app
ls -la <app>/<app>/migrations/versions/
```

### Common Migration Issues

**Revision not found:**
-   Check migration files exist
-   Verify database state matches files
-   Check `down_revision` references

**Version table mismatch:**
-   External apps: Check `migrations/env.py` uses `alembic_version_<appname>`
-   Core/internal: Check uses `alembic_version`

## App Loading Debugging

### Check App Resolution

```bash
fastappkit app list --verbose
```

Shows:
-   Import path
-   Filesystem path
-   Migrations path
-   Route prefix

### Verify App Structure

**Internal app:**
```bash
ls -la apps/<name>/
# Should have: __init__.py, models.py, router.py
```

**External app:**
```bash
ls -la <app>/<app>/
# Should have: __init__.py, models.py, router.py, fastappkit.toml
```

### Check Imports

```python
# Test import manually
python -c "import apps.blog"
python -c "import payments"
```

## Settings Debugging

### Verify Settings Loaded

```python
from fastappkit.conf import get_settings

try:
    settings = get_settings()
    print(f"Database URL: {settings.database_url}")
except Exception as e:
    print(f"Settings not loaded: {e}")
```

### Check Environment Variables

```bash
# Check .env file
cat .env

# Check environment variables
env | grep DATABASE_URL
```

### Verify Settings Initialization

Check `core/app.py`:

```python
# Must have this
settings = Settings()
kit = FastAppKit(settings=settings)
app = kit.create_app()
```

## Route Debugging

### Check Route Collisions

```bash
fastappkit core dev --debug
# Look for route collision warnings
```

### Verify Router Mounting

```python
# In core/app.py, after kit.create_app()
for route in app.routes:
    print(f"{route.path} - {route.methods}")
```

### Check Route Prefixes

```bash
fastappkit app list --verbose
# Shows route prefix for each app
```

## Learn More

-   [Common Issues](common-issues.md) - Solutions to frequent problems
-   [CLI Reference](../reference/cli-reference.md) - All commands
