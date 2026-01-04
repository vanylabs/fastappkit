# External App Manifest

Complete reference for external app `fastappkit.toml` manifest files.

## File Location

**CRITICAL**: The manifest file must be in the **package directory**, not the project root.

**Path**: `<app_name>/<app_name>/fastappkit.toml`

**Example Structure:**

```
payments/
├── payments/              # Package directory
│   ├── __init__.py
│   ├── models.py
│   ├── fastappkit.toml    # Manifest here (in package directory)
│   └── migrations/
├── pyproject.toml
└── README.md
```

**Important Notes:**

-   **NOT** in project root
-   **NOT** in `pyproject.toml` (separate file)
-   Must be included when package is published to PyPI
-   This ensures the manifest is available when the package is installed

## Required Fields

### `name`

App name (must match package name).

**Type**: `string`
**Required**: Yes
**Example**: `"payments"`

```toml
name = "payments"
```

### `version`

Semantic version of the app.

**Type**: `string`
**Required**: Yes
**Example**: `"0.1.0"`

```toml
version = "0.1.0"
```

### `entrypoint`

Dotted path to the register function.

**Type**: `string`
**Required**: Yes
**Formats**:

-   `"module:function"` - Function in module (e.g., `"payments:register"`)
-   `"module:Class"` - Class with `register` method (e.g., `"payments:App"`)
-   Defaults to `"module:register"` if just module name

**Examples:**

```toml
entrypoint = "payments:register"           # Function in __init__.py
entrypoint = "payments.main:register"      # Function in submodule
entrypoint = "payments:App"                # Class with register method
```

**Function Signature:**

```python
def register(app: FastAPI) -> APIRouter | None:
    """Register this app with the FastAPI application."""
    return router  # or None for manual mount
```

### `migrations`

Path to migrations directory (relative to package directory).

**Type**: `string`
**Required**: Yes
**Example**: `"migrations"`

```toml
migrations = "migrations"
```

This should point to the migrations directory inside the package:

```
payments/
└── payments/
    └── migrations/    # This directory
        ├── env.py
        └── versions/
```

### `models_module`

Dotted path to models module (recommended).

**Type**: `string`
**Required**: Recommended (not strictly required, but highly recommended)
**Example**: `"payments.models"`

```toml
models_module = "payments.models"
```

This helps fastappkit locate models for autogenerate and validation.

## Optional Fields

### `route_prefix`

Router mount prefix.

**Type**: `string`
**Required**: No
**Default**: `"/<appname>"` (e.g., `"/payments"`)

**Examples:**

```toml
route_prefix = "/payments"        # Default behavior
route_prefix = "/api/payments"    # Custom prefix
route_prefix = ""                 # Mount at root level
```

**Special Values:**

-   Empty string `""` mounts at root level
-   Default is `"/<appname>"` if not specified

## Complete Example

```toml
[tool.fastappkit]
name = "payments"
version = "0.1.0"
entrypoint = "payments:register"
migrations = "migrations"
models_module = "payments.models"
route_prefix = "/payments"
```

## Validation Rules

### Required Fields Check

All required fields must be present:

-   `name`
-   `version`
-   `entrypoint`
-   `migrations`

### Entrypoint Validation

-   Entrypoint must be importable (module exists)
-   Entrypoint must have correct signature: `register(app: FastAPI) -> APIRouter | None`
-   Function/class must exist in the specified module

### Migrations Directory

-   Migrations directory must exist at the specified path
-   Must contain `env.py` file
-   Should contain `versions/` directory

### Models Module

-   Models module must be importable (if specified)
-   Should contain SQLAlchemy models

### Version Table Check

-   `migrations/env.py` must use correct version table: `alembic_version_<appname>`
-   Should NOT use shared `alembic_version` table

## Common Mistakes

### ❌ Manifest in Wrong Location

**Wrong:**

```
myproject/
├── fastappkit.toml        # WRONG: Project config, not manifest
└── payments/
    └── payments/
        └── (no manifest)
```

**Correct:**

```
payments/
└── payments/
    └── fastappkit.toml    # CORRECT: In package directory
```

### ❌ Missing Required Fields

```toml
# WRONG: Missing entrypoint
[tool.fastappkit]
name = "payments"
version = "0.1.0"
migrations = "migrations"
```

**Fix**: Add all required fields.

### ❌ Incorrect Entrypoint Format

```toml
# WRONG: Missing colon
entrypoint = "payments.register"

# CORRECT
entrypoint = "payments:register"
```

### ❌ Wrong Migrations Path

```toml
# WRONG: Absolute path or wrong relative path
migrations = "/path/to/migrations"
migrations = "../migrations"

# CORRECT: Relative to package directory
migrations = "migrations"
```

### ❌ Version Table Mismatch

In `migrations/env.py`, ensure:

```python
# CORRECT for external app
version_table = "alembic_version_payments"

# WRONG: Using shared table
version_table = "alembic_version"
```

## Manifest Fields Reference

| Field           | Type   | Required    | Default      | Description                      |
| --------------- | ------ | ----------- | ------------ | -------------------------------- |
| `name`          | string | Yes         | -            | App name (must match package)    |
| `version`       | string | Yes         | -            | Semantic version                 |
| `entrypoint`    | string | Yes         | -            | Dotted path to register function |
| `migrations`    | string | Yes         | -            | Path to migrations directory     |
| `models_module` | string | Recommended | -            | Dotted path to models module     |
| `route_prefix`  | string | No          | `/<appname>` | Router mount prefix              |

## Publishing Considerations

When publishing an external app to PyPI:

1. **Manifest must be in package directory** - This ensures it's included in the package
2. **Migrations must be included** - Package migrations directory with the package
3. **`__init__.py` must exist** - Package directory must be a Python package

**Package Structure for PyPI:**

```
payments/
├── payments/
│   ├── __init__.py
│   ├── models.py
│   ├── fastappkit.toml    # Included in package
│   └── migrations/        # Included in package
│       ├── env.py
│       └── versions/
├── pyproject.toml
└── README.md
```

**Check `pyproject.toml` includes package data:**

```toml
[tool.poetry]
packages = [{include = "payments"}]
# or
[tool.setuptools]
packages = ["payments"]
```

## Validation

Run validation to check your manifest:

```bash
fastappkit app validate <app_name>
```

This checks:

-   Required fields are present
-   Entrypoint is importable
-   Migrations directory exists
-   Models module is importable (if specified)
-   Version table is correct

## Next Steps

-   [Project Configuration](project-config.md) - How to add external apps to project
-   [Creating Apps](../guides/creating-apps.md) - Detailed app creation guide
-   [External Apps](../topics/external-apps.md) - Understanding external apps
