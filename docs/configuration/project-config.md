# Project Configuration

Complete reference for `fastappkit.toml` project configuration.

## File Location

**Location**: Project root (where you run `fastappkit` commands)

The file must be named `fastappkit.toml` and located in the project root directory. fastappkit looks for this file when running commands.

## Basic Structure

```toml
[tool.fastappkit]
apps = [
  "apps.blog",           # Internal app
  "apps.auth",           # Internal app
  "fastapi_payments",    # External app (pip-installed package)
]
```

## Configuration Options

### `apps` Array (Required)

List of apps to load. This is the only required configuration.

**Type**: `array[string]`
**Required**: Yes
**Default**: `[]` (empty array)

#### Internal App Format

Internal apps use the `apps.<name>` pattern:

```toml
[tool.fastappkit]
apps = [
  "apps.blog",
  "apps.auth",
]
```

-   Resolves to `./apps/<name>/` directory
-   Must exist in project's `apps/` directory
-   Must have `__init__.py` file
-   Automatically added by CLI when creating apps

#### External App Format

External apps use the package name:

```toml
[tool.fastappkit]
apps = [
  "fastapi_payments",
  "my_custom_app",
]
```

-   Must be pip-installed (importable via `importlib`)
-   **CRITICAL**: Cannot use filesystem paths
-   For local development: `pip install -e /path/to/app`
-   Package name must match what you can `import` in Python

#### App Resolution Order

fastappkit resolves apps in this order:

1. **Check `apps.*` pattern first** - If entry starts with `apps.`, treat as internal app
2. **Try as package import** - Otherwise, try to import as Python package

This means `apps.blog` will always be treated as an internal app, even if a package named `apps.blog` exists.

#### Examples

```toml
[tool.fastappkit]
apps = [
  # Internal apps
  "apps.blog",
  "apps.auth",
  "apps.payments",

  # External apps (pip-installed)
  "fastapi_admin",
  "fastapi_cache",
]
```

### `migration.order` (Optional)

Override the order in which internal app migrations are applied.

**Type**: `array[string]`
**Required**: No
**Default**: Order from `apps` array

```toml
[tool.fastappkit.migration]
order = ["core", "auth", "blog"]
```

**Important Notes:**

-   Only affects **internal apps** (core always runs first)
-   External apps are not included (they run after internal apps, in `apps` order)
-   If not specified, uses order from `apps` array
-   `"core"` is a special value for core migrations (always first)

**When to Use:**

-   Internal apps have dependencies (e.g., `blog` depends on `auth`)
-   You want explicit control over migration order
-   App order in `apps` array doesn't match dependency order

**Example:**

```toml
[tool.fastappkit]
apps = [
  "apps.blog",
  "apps.auth",  # blog depends on auth, but listed first
]

[tool.fastappkit.migration]
order = ["core", "auth", "blog"]  # Override: auth before blog
```

## Complete Example

```toml
[tool.fastappkit]
apps = [
  # Internal apps (project-specific)
  "apps.blog",
  "apps.auth",
  "apps.payments",

  # External apps (pip-installed packages)
  "fastapi_admin",
  "fastapi_cache",
]

[tool.fastappkit.migration]
order = ["core", "auth", "blog", "payments"]
```

## Validation Rules

### App Entry Validation

-   **Internal apps**: Must exist in `./apps/<name>/` with `__init__.py`
-   **External apps**: Must be importable (pip-installed)
-   **No duplicates**: Duplicate app names are detected and warned

### Common Mistakes

#### ❌ Using Filesystem Path for External App

```toml
# WRONG
apps = [
  "/path/to/external/app",  # Not supported
]
```

**Fix**: Install package first, then use package name:
```bash
pip install -e /path/to/external/app
```

```toml
# CORRECT
apps = [
  "external_app_name",  # Package name
]
```

#### ❌ Duplicate App Names

```toml
# WARNING: Both resolve to same name "blog"
apps = [
  "apps.blog",
  "myproject.blog",  # If this package exists, both resolve to "blog"
]
```

**Fix**: Rename one of the apps or use different names.

#### ❌ Missing `apps` Array

```toml
[tool.fastappkit]
# Missing apps array - will error
```

**Fix**: Always include `apps` array (can be empty `[]`).

#### ❌ Incorrect App Entry Format

```toml
# WRONG
apps = [
  "blog",  # Missing "apps." prefix for internal app
]

# CORRECT for internal app
apps = [
  "apps.blog",
]

# CORRECT for external app (if package is named "blog")
apps = [
  "blog",  # OK if it's an external package
]
```

## Best Practices

1. **Keep apps list organized**: Group internal apps together, then external apps
2. **Use migration.order when needed**: Only if internal apps have dependencies
3. **Validate apps**: Run `fastappkit app list` to verify all apps are resolved
4. **Document external apps**: Note which external apps are used and their versions
5. **Version control**: Commit `fastappkit.toml` to version control

## Troubleshooting

### App Not Found

**Error**: `AppLoadError: Could not resolve app entry`

**Solutions:**
-   For internal apps: Check `apps/<name>/` exists with `__init__.py`
-   For external apps: Ensure package is pip-installed (`pip install -e .`)
-   Verify app entry format matches app type

### Duplicate App Names

**Warning**: `Duplicate app names detected`

**Solutions:**
-   Rename one of the apps
-   Check if multiple entries resolve to same name
-   Use `fastappkit app list` to see resolved names

### Migration Order Issues

**Problem**: Migrations fail due to dependency order

**Solutions:**
-   Use `[tool.fastappkit.migration.order]` to specify order
-   Ensure dependencies are listed before dependents
-   Core always runs first (no need to specify)

## Next Steps

-   [Settings Configuration](settings.md) - Configure application settings
-   [External App Manifest](external-app-manifest.md) - External app configuration
-   [Creating Projects](../guides/creating-projects.md) - Project setup guide
