# Settings Configuration

Complete guide to configuring application settings in `core/config.py`.

## Overview

Settings are defined in `core/config.py` using Pydantic's `BaseSettings`. They automatically load from `.env` files and environment variables.

## Settings Class Structure

### Basic Settings

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application settings.

    Loads from .env file automatically.
    """

    database_url: str = Field(default="sqlite:///./app.db")
    debug: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True
    )
```

## Required Settings

Settings must implement `SettingsProtocol`, which requires:

### `database_url: str`

Database connection string.

**Type**: `str`
**Required**: Yes (by protocol)
**Default**: `"sqlite:///./app.db"` (in scaffolded code)
**Environment Variable**: `DATABASE_URL`

**Examples:**
```python
# SQLite
database_url: str = Field(default="sqlite:///./app.db")

# PostgreSQL
database_url: str = Field(default="postgresql://user:password@localhost:5432/mydb")

# MySQL
database_url: str = Field(default="mysql://user:password@localhost:3306/mydb")
```

### `debug: bool`

Debug mode flag.

**Type**: `bool`
**Required**: Yes (by protocol)
**Default**: `False`
**Environment Variable**: `DEBUG`

**Examples:**
```python
debug: bool = Field(default=False)
```

## Adding Custom Settings

### Basic Fields

Add any fields you need:

```python
class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./app.db")
    debug: bool = Field(default=False)

    # Custom settings
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    api_key: str = Field(default="", alias="API_KEY")
    max_upload_size: int = Field(default=10485760, alias="MAX_UPLOAD_SIZE")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True
    )
```

### Field Validation

Use Pydantic validators:

```python
from pydantic import Field, field_validator

class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./app.db")
    debug: bool = Field(default=False)

    port: int = Field(default=8000, alias="PORT")

    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError('Port must be between 1 and 65535')
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True
    )
```

### Nested Settings

Use Pydantic models for nested configuration:

```python
from pydantic import BaseModel, Field

class DatabaseConfig(BaseSettings):
    host: str = "localhost"
    port: int = 5432
    name: str = "mydb"
    user: str = "postgres"
    password: str = ""

class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./app.db")
    debug: bool = Field(default=False)

    # Nested settings
    database: DatabaseConfig = DatabaseConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True
    )
```

### Environment Variable Aliases

Use `alias` parameter to map to environment variables:

```python
class Settings(BaseSettings):
    database_url: str = Field(
        default="sqlite:///./app.db",
        alias="DATABASE_URL"  # Maps to DATABASE_URL env var
    )
    debug: bool = Field(
        default=False,
        alias="DEBUG"  # Maps to DEBUG env var
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        populate_by_name=True  # Allows both field name and alias
    )
```

With `populate_by_name=True`, you can use either:
- Field name: `database_url` or `DATABASE_URL` in `.env`
- Alias: `DATABASE_URL` in environment variables

## `.env` File

### Location

The `.env` file should be in the **project root** (same directory as `fastappkit.toml`).

### Format

```bash
# Database Configuration
DATABASE_URL=sqlite:///./myproject.db

# Development Settings
DEBUG=false

# Custom Settings
SECRET_KEY=your-secret-key-here
API_KEY=your-api-key
MAX_UPLOAD_SIZE=10485760
```

### Variable Naming

-   Use **uppercase with underscores** (e.g., `DATABASE_URL`)
-   Match the `alias` in Field definitions
-   No spaces around `=`

### Precedence

Settings are loaded in this order (highest to lowest priority):

1. **Environment variables** (highest priority)
2. **`.env` file**
3. **Default values** in `Field()` (lowest priority)

**Example:**
```bash
# .env file
DATABASE_URL=sqlite:///./app.db

# Environment variable (overrides .env)
export DATABASE_URL=postgresql://localhost/mydb
```

## Accessing Settings

### Global Accessor (Django-like)

Use `get_settings()` function:

```python
from fastappkit.conf import get_settings

settings = get_settings()
db_url = settings.database_url
is_debug = settings.debug
```

### FastAPI Dependency Injection

Use as a dependency:

```python
from fastappkit.conf import get_settings
from fastapi import Depends
from core.config import Settings

@app.get("/config")
def get_config(settings: Settings = Depends(get_settings)):
    return {
        "debug": settings.debug,
        "database": settings.database_url
    }
```

## Settings Initialization

### When Settings Are Loaded

Settings are initialized in `core/app.py` when the module is imported:

```python
# core/app.py
from core.config import Settings
from fastappkit.core.kit import FastAppKit

# Initialize FastAppKit with project's Settings
settings = Settings()  # Loads from .env automatically
kit = FastAppKit(settings=settings)
app = kit.create_app()
```

### How FastAppKit Uses Settings

When `FastAppKit` is initialized, it calls `set_settings()` which makes settings globally available via `get_settings()`.

### CLI Commands and Settings

CLI commands use `ensure_settings_loaded(project_root)` which imports `core.app`, causing settings to be initialized automatically.

**CRITICAL**: Settings must be initialized in `core/app.py` before using `FastAppKit`. Without this, `get_settings()` will fail at runtime.

## Complete Examples

### Minimal Settings

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./app.db")
    debug: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True
    )
```

### Extended Settings with Validation

```python
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./app.db")
    debug: bool = Field(default=False)

    # Custom settings
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    host: str = Field(default="127.0.0.1", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    redis_url: str = Field(default="redis://localhost:6379", alias="REDIS_URL")

    @field_validator('port')
    @classmethod
    def validate_port(cls, v: int) -> int:
        if not (1 <= v <= 65535):
            raise ValueError('Port must be between 1 and 65535')
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",  # Ignore extra fields from .env
    )
```

### Nested Settings

```python
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class EmailConfig(BaseModel):
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@example.com"

class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./app.db")
    debug: bool = Field(default=False)

    # Nested settings
    email: EmailConfig = EmailConfig()

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True
    )
```

## Settings Options Reference

| Setting | Type | Required | Default | Env Var | Description |
|---------|------|----------|---------|---------|-------------|
| `database_url` | str | Yes | `sqlite:///./app.db` | `DATABASE_URL` | Database connection string |
| `debug` | bool | Yes | `False` | `DEBUG` | Debug mode flag |

## Common Custom Settings Examples

-   **`secret_key`**: Secret key for encryption/signing
-   **`host` / `port`**: Server host and port
-   **`redis_url`**: Redis connection string
-   **`email_settings`**: Nested email configuration
-   **`logging_level`**: Logging verbosity
-   **`cors_origins`**: CORS allowed origins
-   **`api_rate_limit`**: Rate limiting configuration

## Common Issues

### Settings Not Initialized

**Error**: Runtime errors when calling `get_settings()`

**Solution**: Ensure `core/app.py` initializes Settings and FastAppKit:
```python
settings = Settings()
kit = FastAppKit(settings=settings)
app = kit.create_app()
```

### Missing `.env` File

**Problem**: Settings use defaults, may fail if no default for required field

**Solution**: Create `.env` file in project root with required settings

### Wrong `DATABASE_URL`

**Error**: Database connection errors

**Solution**:
-   Verify `DATABASE_URL` in `.env` file
-   Check database is running and accessible
-   Verify connection string format

### External App Using Wrong `DATABASE_URL`

**Problem**: External app uses its own `.env` when developing independently, but should use core's when integrated

**Solution**:
-   When developing independently: Use external app's `.env`
-   When integrated: External app uses core project's `DATABASE_URL` (from core's `.env`)

## Next Steps

-   [Project Configuration](project-config.md) - `fastappkit.toml` reference
-   [External App Manifest](external-app-manifest.md) - External app configuration
-   [Creating Projects](../guides/creating-projects.md) - Project setup guide
