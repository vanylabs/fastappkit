# Configuration Overview

fastappkit has three main configuration areas. This section provides complete references for each.

## Configuration Areas

### 1. Project Configuration (`fastappkit.toml`)

Project-level configuration that defines which apps are loaded and migration order.

**Location**: Project root (where you run `fastappkit` commands)

**Key Options:**
-   `apps` array - List of apps (internal and external)
-   `migration.order` - Override internal app migration order

[→ Project Configuration Reference](project-config.md)

### 2. Settings (`core/config.py`)

Application settings using Pydantic's `BaseSettings`.

**Location**: `core/config.py` in your project

**Key Features:**
-   Required settings: `database_url`, `debug`
-   Custom settings: Add any fields you need
-   Environment variables: Loaded from `.env` automatically
-   Global access: Use `get_settings()` function

[→ Settings Configuration Guide](settings.md)

### 3. External App Manifest (`<app>/<app>/fastappkit.toml`)

Metadata for external apps (pip-installable packages).

**Location**: Package directory (`<app_name>/<app_name>/fastappkit.toml`)

**Key Fields:**
-   `name`, `version`, `entrypoint` (required)
-   `migrations`, `models_module` (required/recommended)
-   `route_prefix` (optional)

[→ External App Manifest Reference](external-app-manifest.md)

## Quick Reference

| Configuration | File | Location | Purpose |
|---------------|------|----------|---------|
| **Project Config** | `fastappkit.toml` | Project root | App list, migration order |
| **Settings** | `core/config.py` | Project root | Application settings |
| **External Manifest** | `fastappkit.toml` | Package directory | External app metadata |

## Configuration Flow

```
1. Project loads fastappkit.toml
   └─> Reads apps list
       ├─> Resolves internal apps (apps.*)
       └─> Resolves external apps (package import)

2. Each app loads its configuration
   ├─> Internal apps: No manifest needed
   └─> External apps: Load fastappkit.toml from package

3. Settings loaded from core/config.py
   └─> Reads .env file
       └─> Environment variables override .env
```

## Common Configuration Tasks

### Adding an Internal App

Edit `fastappkit.toml`:
```toml
[tool.fastappkit]
apps = [
  "apps.blog",  # Added automatically by CLI, or add manually
]
```

### Adding an External App

1. Install package: `pip install -e /path/to/app`
2. Edit `fastappkit.toml`:
```toml
[tool.fastappkit]
apps = [
  "external_app_name",  # Package name, not path
]
```

### Adding Custom Settings

Edit `core/config.py`:
```python
class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./app.db")
    debug: bool = Field(default=False)

    # Add custom settings
    secret_key: str = Field(default="", alias="SECRET_KEY")
```

### Overriding Migration Order

Edit `fastappkit.toml`:
```toml
[tool.fastappkit.migration]
order = ["core", "auth", "blog"]  # Override internal app order
```

## Next Steps

-   [Project Configuration](project-config.md) - Complete `fastappkit.toml` reference
-   [Settings Configuration](settings.md) - Complete `core/config.py` guide
-   [External App Manifest](external-app-manifest.md) - Manifest format reference
