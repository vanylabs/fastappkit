# Extending FastAppKit

How to customize and extend fastappkit for your needs.

## Subclassing FastAppKit

Customize the FastAPI app creation:

```python
from fastappkit.core.kit import FastAppKit
from fastapi import FastAPI
from core.config import Settings

class CustomFastAppKit(FastAppKit):
    def create_app(self) -> FastAPI:
        app = super().create_app()

        # Add custom middleware
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Customize app metadata
        app.title = "My Custom API"
        app.version = "1.0.0"
        app.description = "Custom API description"

        # Add exception handlers
        @app.exception_handler(ValueError)
        async def value_error_handler(request, exc):
            return {"error": str(exc)}

        return app

# Use custom class
settings = Settings()
kit = CustomFastAppKit(settings=settings)
app = kit.create_app()
```

## Custom App Loading

Override app loading behavior:

```python
from fastappkit.core.loader import AppLoader
from fastappkit.core.registry import AppRegistry

class CustomAppLoader(AppLoader):
    def load_all(self) -> AppRegistry:
        registry = super().load_all()

        # Custom logic: filter apps, modify metadata, etc.
        # ...

        return registry
```

## Custom Router Assembly

Customize router mounting:

```python
from fastappkit.core.router import RouterAssembler
from fastappkit.core.registry import AppRegistry
from fastapi import FastAPI

class CustomRouterAssembler(RouterAssembler):
    def assemble(self, app: FastAPI, registry: AppRegistry) -> None:
        # Custom mounting logic
        for app_metadata in registry.list():
            if app_metadata.router:
                # Custom prefix logic
                prefix = self._custom_prefix(app_metadata)
                app.include_router(app_metadata.router, prefix=prefix)
```

## Middleware and Exception Handlers

Add middleware and exception handlers in `core/app.py`:

```python
from core.config import Settings
from fastappkit.core.kit import FastAppKit
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import time

settings = Settings()
kit = FastAppKit(settings=settings)
app = kit.create_app()

# Add middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Add exception handlers
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)}
    )
```

## Custom Settings Access

Create custom settings accessors:

```python
from fastappkit.conf import get_settings
from core.config import Settings

def get_database_url() -> str:
    """Custom accessor for database URL."""
    settings = get_settings()
    return settings.database_url

# Use in routes
from fastapi import APIRouter

router = APIRouter()

@router.get("/db-info")
def db_info():
    db_url = get_database_url()
    return {"database": db_url}
```

## Learn More

-   [Best Practices](best-practices.md) - Recommended patterns
-   [Architecture](architecture.md) - Internal architecture
