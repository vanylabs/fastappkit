# Manifest Reference

Complete reference for external app manifest files.

## Location

External apps must declare metadata in `fastappkit.toml` located inside the package directory:

**Path:** `<app_name>/<app_name>/fastappkit.toml`

For example, if your package is named `myapp`, the manifest should be at:

```
myapp/
└── myapp/
    ├── __init__.py
    ├── fastappkit.toml  # Manifest here
    └── ...
```

!!! important "Manifest Requirements"
    The manifest file is `fastappkit.toml`, not `pyproject.toml`. It must be located in the package directory (where `__init__.py` is). This ensures it's included when the package is published to PyPI. No fallback - `fastappkit.toml` is required for external apps.

## Schema

### Required Fields

#### `name`

- **Type:** `string`
- **Description:** App name (must match package name)
- **Example:** `"blog"`

#### `version`

- **Type:** `string`
- **Description:** Semantic version (e.g., `"0.1.0"`)
- **Example:** `"0.1.0"`

#### `entrypoint`

- **Type:** `string`
- **Description:** Dotted path to register function (e.g., `"blog:register"`)
- **Formats:**
  - `"blog:register"` - Function in module
  - `"blog:App"` - Class (must have `register` method)
  - `"blog"` - Defaults to `"blog:register"`
  - `"blog.main:register"` - Function in submodule
- **Example:** `"blog:register"`

#### `migrations`

- **Type:** `string`
- **Description:** Path to migrations directory (relative to package directory, typically `"migrations"`)
- **Example:** `"migrations"`

#### `models_module`

- **Type:** `string`
- **Description:** Dotted path to models module (recommended)
- **Example:** `"blog.models"`

### Optional Fields

#### `route_prefix`

- **Type:** `string`
- **Description:** Router prefix (default: `/<appname>`)
- **Example:** `"/api/blog"`
- **Special:** Use empty string `""` to mount at root level

## Example

```toml
name = "blog"
version = "0.1.0"
entrypoint = "blog:register"
migrations = "migrations"
models_module = "blog.models"
route_prefix = "/blog"
```

## Validation

The manifest is validated when:

- Loading apps at startup
- Running `fastappkit app validate <name>`

### Validation Checks

- Required fields are present
- Field types are correct
- Entrypoint is importable
- Entrypoint has correct signature
- Migrations directory exists
- Models module is importable (if specified)

## Learn More

- [External Apps](../topics/external-apps.md) - Understanding external apps
- [Creating Apps](../guides/creating-apps.md) - How to create external apps
