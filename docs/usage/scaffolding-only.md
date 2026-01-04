# Scenario 1: Scaffolding Only

This guide is for users who just want the project structure without using fastappkit's app system.

## When to Use This Approach

Use scaffolding only when:

-   You want a clean FastAPI project structure
-   You prefer manual organization over the app system
-   You don't need modular apps or plugin architecture
-   You want full control over project organization

## Step-by-Step Guide

### 1. Create Project

```bash
fastappkit core new myproject
cd myproject
```

This creates a complete project structure with:
-   `core/` directory (config, app, models)
-   `apps/` directory (empty, for manual use)
-   `fastappkit.toml` (project configuration)
-   `.env` file (environment variables)
-   `main.py` (entry point)

### 2. Install Dependencies

```bash
poetry install
# or
pip install -e .
```

### 3. Update Dependency Versions

**IMPORTANT**: Dependency versions in `pyproject.toml` default to `*` (any version). Update them for production:

```toml
[tool.poetry.dependencies]
python = ">=3.11,<4.0"
fastapi = ">=0.120.0,<0.130"  # Specific range instead of *
sqlalchemy = ">=2.0,<3.0"
alembic = ">=1.17.2,<1.18"
```

### 4. Configure Environment

Edit `.env` file:

```bash
DATABASE_URL=sqlite:///./myproject.db
DEBUG=false
```

Add any custom settings you need.

### 5. Customize Settings (Optional)

Edit `core/config.py` to add custom settings:

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./myproject.db")
    debug: bool = Field(default=False)

    # Add your custom settings
    secret_key: str = Field(default="change-me", alias="SECRET_KEY")
    api_key: str = Field(default="", alias="API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True
    )
```

### 6. Customize FastAPI App (Optional)

Edit `core/app.py` to add middleware, exception handlers, etc.:

```python
from core.config import Settings
from fastappkit.core.kit import FastAppKit
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

settings = Settings()
kit = FastAppKit(settings=settings)
app = kit.create_app()

# Customize FastAPI app
app.title = "My Custom API"
app.version = "1.0.0"
app.description = "Custom API description"

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 7. Run Manually

Since you're not using the app system, run the server manually:

```bash
uvicorn main:app --reload
```

Or use Python directly:

```bash
python main.py
```

## What You Can Customize

-   **Settings**: Add any custom settings in `core/config.py`
-   **FastAPI App**: Modify `core/app.py` to add middleware, exception handlers, etc.
-   **Models**: Add models to `core/models.py` (for shared infrastructure)
-   **Routes**: Add routes directly to `main.py` or create your own router modules
-   **Migrations**: Use `fastappkit migrate core -m "message"` for core migrations

## What You Can Skip

-   Creating apps (you can organize code manually)
-   Using `fastappkit app` commands
-   App validation
-   Automatic router mounting (mount manually if needed)

## Manual Testing Approach

Since you're running manually, you can:

1. **Test with uvicorn directly:**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Use FastAPI's interactive docs:**
   - Visit `http://127.0.0.1:8000/docs` for Swagger UI
   - Visit `http://127.0.0.1:8000/redoc` for ReDoc

3. **Test with curl or httpx:**
   ```bash
   curl http://127.0.0.1:8000/
   ```

## Quick Commands Reference

```bash
# Create project
fastappkit core new myproject

# Install dependencies
cd myproject && poetry install

# Update dependency versions in pyproject.toml (IMPORTANT!)

# Configure .env file

# Run manually
uvicorn main:app --reload
```

## Critical Manual Steps

-   ✅ Update dependency versions from `*` to specific ranges
-   ✅ Configure `.env` file with `DATABASE_URL` and other settings
-   ✅ Ensure `core/app.py` initializes Settings and FastAppKit correctly

## Next Steps

If you later decide you want modular organization:

-   [Internal Apps](internal-apps.md) - Add internal apps to your project
-   [Full Ecosystem](full-ecosystem.md) - Add external apps for reusable components

Or continue with manual organization and use fastappkit only for:
-   Project structure
-   Settings management
-   Core migrations
