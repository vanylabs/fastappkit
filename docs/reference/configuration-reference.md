# Configuration Reference

Quick lookup for all fastappkit configuration options.

## Project Configuration (`fastappkit.toml`)

### Location

Project root (where you run `fastappkit` commands).

### Schema

```toml
[tool.fastappkit]
apps = [
  "apps.blog",        # Internal app
  "fastapi_payments", # External app
]

[tool.fastappkit.migration]
order = ["core", "auth", "blog"]  # Optional: override internal app order
```

### Options

| Option | Type | Required | Default | Description |
|--------|------|----------|---------|-------------|
| `apps` | `array[string]` | Yes | `[]` | List of app entries |
| `migration.order` | `array[string]` | No | apps order | Migration execution order (internal apps only) |

### App Entry Formats

-   **Internal app**: `apps.<name>` (resolves to `./apps/<name>/`)
-   **External app**: `<package_name>` (must be pip-installed, importable)

## Settings Configuration (`core/config.py`)

### Required Settings

| Setting | Type | Required | Default | Env Var | Description |
|---------|------|----------|---------|---------|-------------|
| `database_url` | `str` | Yes | `sqlite:///./app.db` | `DATABASE_URL` | Database connection string |
| `debug` | `bool` | Yes | `False` | `DEBUG` | Debug mode flag |

### Settings Class Structure

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./app.db", alias="DATABASE_URL")
    debug: bool = Field(default=False, alias="DEBUG")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True
    )
```

### Common Custom Settings

-   `secret_key: str` - Secret key for encryption/signing
-   `host: str` - Server host
-   `port: int` - Server port
-   `redis_url: str` - Redis connection string
-   `email_settings: EmailConfig` - Nested email configuration
-   `logging_level: str` - Logging verbosity

### Environment Variables

-   **Location**: `.env` file in project root
-   **Format**: `KEY=value` (uppercase with underscores)
-   **Precedence**: Environment variables > `.env` file > defaults

## External App Manifest (`<app>/<app>/fastappkit.toml`)

### Location

Package directory (`<app_name>/<app_name>/fastappkit.toml`).

### Schema

```toml
[tool.fastappkit]
name = "payments"
version = "0.1.0"
entrypoint = "payments:register"
migrations = "migrations"
models_module = "payments.models"
route_prefix = "/payments"
```

### Fields

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `name` | `string` | Yes | - | App name (must match package) |
| `version` | `string` | Yes | - | Semantic version |
| `entrypoint` | `string` | Yes | - | Dotted path to register function |
| `migrations` | `string` | Yes | - | Path to migrations directory |
| `models_module` | `string` | Recommended | - | Dotted path to models module |
| `route_prefix` | `string` | No | `/<appname>` | Router mount prefix |

### Entrypoint Formats

-   `"module:function"` - Function in module (e.g., `"payments:register"`)
-   `"module:Class"` - Class with `register` method (e.g., `"payments:App"`)
-   Defaults to `"module:register"` if just module name

## Quick Reference Tables

### Project Configuration Options

| Section | Option | Type | Required | Description |
|---------|--------|------|----------|-------------|
| `[tool.fastappkit]` | `apps` | `array[string]` | Yes | List of apps |
| `[tool.fastappkit.migration]` | `order` | `array[string]` | No | Internal app migration order |

### Settings Options

| Setting | Type | Required | Default | Env Var |
|---------|------|----------|---------|---------|
| `database_url` | `str` | Yes | `sqlite:///./app.db` | `DATABASE_URL` |
| `debug` | `bool` | Yes | `False` | `DEBUG` |

### Manifest Fields

| Field | Type | Required | Default |
|-------|------|----------|---------|
| `name` | `string` | Yes | - |
| `version` | `string` | Yes | - |
| `entrypoint` | `string` | Yes | - |
| `migrations` | `string` | Yes | - |
| `models_module` | `string` | Recommended | - |
| `route_prefix` | `string` | No | `/<appname>` |

## Examples

### Complete Project Configuration

```toml
[tool.fastappkit]
apps = [
  "apps.blog",
  "apps.auth",
  "fastapi_payments",
]

[tool.fastappkit.migration]
order = ["core", "auth", "blog"]
```

### Complete Settings Configuration

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./app.db", alias="DATABASE_URL")
    debug: bool = Field(default=False, alias="DEBUG")

    secret_key: str = Field(default="", alias="SECRET_KEY")
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True
    )
```

### Complete Manifest Configuration

```toml
[tool.fastappkit]
name = "payments"
version = "0.1.0"
entrypoint = "payments:register"
migrations = "migrations"
models_module = "payments.models"
route_prefix = "/api/payments"
```

## Learn More

-   [Project Configuration](../configuration/project-config.md) - Complete `fastappkit.toml` reference
-   [Settings Configuration](../configuration/settings.md) - Complete `core/config.py` guide
-   [External App Manifest](../configuration/external-app-manifest.md) - Manifest format reference
