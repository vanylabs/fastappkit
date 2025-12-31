# Configuration Reference

Complete reference for fastappkit configuration options.

## Project Configuration

fastappkit uses `fastappkit.toml` for project configuration. This file is separate from `pyproject.toml`.

### Basic Structure

```toml
[tool.fastappkit]
apps = [
  "apps.blog",           # Internal app
  "apps.auth",           # Internal app
  "fastapi_payments",    # External app (pip-installed package)
]
```

### App Entry Formats

-   `apps.<name>` → Internal app (located in `./apps/<name>/`)
-   `<package_name>` → External app (pip-installed package, must be importable)

### Migration Order

Override the order in which internal app migrations are applied:

```toml
[tool.fastappkit.migration]
order = ["core", "auth", "blog"]
```

If not specified, internal apps are processed in the order they appear in the `apps` list.

## Settings Configuration

Settings are defined in `core/config.py` using Pydantic's `BaseSettings`.

### Basic Settings

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./app.db",
        alias="DATABASE_URL"
    )
    debug: bool = Field(
        default=False,
        alias="DEBUG"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True
    )
```

### Extended Settings

```python
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./app.db",
        alias="DATABASE_URL"
    )
    debug: bool = Field(
        default=False,
        alias="DEBUG"
    )

    # Custom settings
    secret_key: str = Field(
        default="change-me-in-production",
        alias="SECRET_KEY"
    )
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8000, alias="PORT")

    # Nested settings
    class DatabaseConfig(BaseSettings):
        host: str = "localhost"
        port: int = 5432
        name: str = "mydb"

    database: DatabaseConfig = DatabaseConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )
```

### Settings Options

**BaseSettings Configuration:**

-   `env_file`: Path to `.env` file (default: `.env`)
-   `env_file_encoding`: Encoding for `.env` file (default: `utf-8`)
-   `case_sensitive`: Whether environment variable names are case-sensitive (default: `False`)
-   `extra`: How to handle extra fields (`"ignore"`, `"forbid"`, `"allow"`)

### Environment Variables

Settings are loaded from `.env` file and environment variables:

```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
DEBUG=false
SECRET_KEY=your-secret-key-here
```

Environment variables take precedence over `.env` file values.

## External App Manifest

External apps must declare metadata in `fastappkit.toml` located inside the package directory.

**Location:** `<app_name>/<app_name>/fastappkit.toml`

See the [Manifest Reference](manifest-reference.md) for complete details.

## Learn More

-   [Configuration Guide](../guides/configuration.md) - Configuration guide
-   [Manifest Reference](manifest-reference.md) - External app manifest schema
