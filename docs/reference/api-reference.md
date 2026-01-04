# API Reference

Programmatic API documentation for fastappkit.

## FastAppKit Class

Main class that manages settings and app loading.

### `FastAppKit.__init__`

Initialize FastAppKit with settings.

**Signature:**

```python
def __init__(self, settings: SettingsProtocol) -> None
```

**Parameters:**

-   `settings`: Settings instance from project's `core.config` module

**Example:**

```python
from core.config import Settings
from fastappkit.core.kit import FastAppKit

settings = Settings()
kit = FastAppKit(settings=settings)
```

**Notes:**

-   Calls `set_settings()` internally to make settings globally available
-   Settings must implement `SettingsProtocol` (have `database_url` and `debug`)

### `FastAppKit.create_app`

Create and configure FastAPI application.

**Signature:**

```python
def create_app(self) -> FastAPI
```

**Returns:**

-   `FastAPI`: Configured FastAPI application

**Example:**

```python
from core.config import Settings
from fastappkit.core.kit import FastAppKit

settings = Settings()
kit = FastAppKit(settings=settings)
app = kit.create_app()
```

**What it does:**

1. Creates FastAPI app instance
2. Loads apps via `AppLoader`
3. Executes app registrations
4. Mounts routers
5. Returns configured app

## Settings Functions

### `get_settings`

Get the global settings instance.

**Signature:**

```python
def get_settings() -> SettingsProtocol
```

**Returns:**

-   `SettingsProtocol`: Current settings instance

**Example:**

```python
from fastappkit.conf import get_settings

settings = get_settings()
db_url = settings.database_url
is_debug = settings.debug
```

**Notes:**

-   Returns the settings instance set by `FastAppKit.__init__`
-   Raises error if settings not initialized
-   Django-like global accessor pattern

### `set_settings`

Set the global settings instance.

**Signature:**

```python
def set_settings(settings: SettingsProtocol) -> None
```

**Parameters:**

-   `settings`: Settings instance to set globally

**Example:**

```python
from fastappkit.conf import set_settings
from core.config import Settings

settings = Settings()
set_settings(settings)
```

**Notes:**

-   Called automatically by `FastAppKit.__init__`
-   Usually not called directly

## Settings Protocol

Protocol that settings classes must implement.

### `SettingsProtocol`

```python
class SettingsProtocol(Protocol):
    database_url: str
    debug: bool
```

**Required Attributes:**

-   `database_url: str` - Database connection string
-   `debug: bool` - Debug mode flag

**Example Implementation:**

```python
from pydantic_settings import BaseSettings
from fastappkit.conf import SettingsProtocol

class Settings(BaseSettings, SettingsProtocol):
    database_url: str = "sqlite:///./app.db"
    debug: bool = False
```

## App Registration

### Register Function Signature

Apps provide a `register()` function:

**Signature:**

```python
def register(app: FastAPI) -> APIRouter | None:
    """Register this app with the FastAPI application."""
    return router  # or None
```

**Parameters:**

-   `app`: FastAPI application instance

**Returns:**

-   `APIRouter | None`: Return router for auto-mount, or `None` for manual mount

**Example:**

```python
from fastapi import APIRouter, FastAPI
from fastappkit.conf import get_settings

router = APIRouter()

@router.get("/posts")
def list_posts():
    return []

def register(app: FastAPI) -> APIRouter:
    settings = get_settings()
    return router  # Auto-mount
```

## Programmatic Usage Examples

### Basic Usage

```python
# core/app.py
from core.config import Settings
from fastappkit.core.kit import FastAppKit

settings = Settings()
kit = FastAppKit(settings=settings)
app = kit.create_app()
```

### Custom FastAPI App

```python
from core.config import Settings
from fastappkit.core.kit import FastAppKit
from fastapi import FastAPI

settings = Settings()
kit = FastAppKit(settings=settings)
app = kit.create_app()

# Customize app
app.title = "My Custom API"
app.version = "1.0.0"
```

### Subclassing FastAppKit

```python
from fastappkit.core.kit import FastAppKit
from fastapi import FastAPI
from core.config import Settings

class CustomFastAppKit(FastAppKit):
    def create_app(self) -> FastAPI:
        app = super().create_app()
        # Add custom middleware, exception handlers, etc.
        app.title = "My Custom API"
        return app

settings = Settings()
kit = CustomFastAppKit(settings=settings)
app = kit.create_app()
```

### Using Settings in Routes

```python
from fastappkit.conf import get_settings
from fastapi import APIRouter, Depends
from core.config import Settings

router = APIRouter()

@router.get("/config")
def get_config(settings: Settings = Depends(get_settings)):
    return {
        "debug": settings.debug,
        "database": settings.database_url
    }
```

## Learn More

-   [Configuration](../configuration/settings.md) - Settings configuration guide
-   [Creating Apps](../guides/creating-apps.md) - App registration guide
-   [Extending FastAppKit](../advanced/extending-fastappkit.md) - Customization guide
