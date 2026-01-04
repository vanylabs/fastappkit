# Creating Projects

Detailed guide to creating new fastappkit projects.

## Command

```bash
fastappkit core new <name> [--project-root <path>] [--description <text>]
```

## Options

### `--project-root <path>`

Directory to create project in.

**Default**: Current working directory

**Example:**
```bash
fastappkit core new myproject --project-root /path/to/projects
```

### `--description <text>`

Project description.

**Example:**
```bash
fastappkit core new myproject --description "My API project"
```

## What Gets Created

### Directory Structure

```
myproject/
├── core/
│   ├── __init__.py
│   ├── config.py          # Settings (BaseSettings from .env)
│   ├── models.py          # SQLAlchemy Base class
│   ├── app.py             # create_app() factory
│   └── db/
│       └── migrations/    # Core migrations
│           ├── env.py
│           ├── script.py.mako
│           └── versions/
├── apps/                  # Internal apps directory (empty)
├── fastappkit.toml        # Project configuration
├── .env                   # Environment variables
├── .gitignore
├── main.py                # Entry point
├── pyproject.toml         # Package metadata
└── README.md
```

### File Descriptions

#### `core/config.py`

Settings class using Pydantic's `BaseSettings`:
-   Loads from `.env` file automatically
-   Required: `database_url`, `debug`
-   Can be extended with custom settings

#### `core/models.py`

SQLAlchemy Base class (DeclarativeBase):
-   Used by internal apps for models
-   Can add core models here (shared infrastructure)

#### `core/app.py`

FastAPI app factory:
-   Initializes `Settings` and `FastAppKit`
-   Creates and configures FastAPI app
-   Can be customized (middleware, exception handlers, etc.)

#### `core/db/migrations/`

Alembic migration directory:
-   Shared by core and internal apps
-   Contains `env.py` (Alembic configuration)
-   `versions/` directory for migration files

#### `fastappkit.toml`

Project configuration:
-   Lists apps (internal and external)
-   Optional migration order override
-   Initially empty `apps` array

#### `.env`

Environment variables:
-   Auto-created with defaults
-   `DATABASE_URL` and `DEBUG` settings
-   Add custom settings as needed

#### `main.py`

Application entry point:
-   Imports `app` from `core.app`
-   Can be run directly: `python main.py`
-   Or with uvicorn: `uvicorn main:app --reload`

## Post-Creation Steps

### 1. Install Dependencies

```bash
cd myproject
poetry install
# or
pip install -e .
```

### 2. Update Dependency Versions

**IMPORTANT**: Dependency versions in `pyproject.toml` default to `*`. Update them:

```toml
[tool.poetry.dependencies]
python = ">=3.11,<4.0"
fastapi = ">=0.120.0,<0.130"  # Specific range instead of *
sqlalchemy = ">=2.0,<3.0"
alembic = ">=1.17.2,<1.18"
```

### 3. Configure Settings

Edit `.env` file:

```bash
DATABASE_URL=sqlite:///./myproject.db
DEBUG=false
```

Add any custom settings to `core/config.py` if needed.

### 4. First Migration (Optional)

If you have core models, create a migration:

```bash
fastappkit migrate core -m "initial"
fastappkit migrate all
```

## Customization

### Modifying `core/app.py`

Add middleware, exception handlers, etc.:

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

### Adding Custom Settings

Edit `core/config.py`:

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = Field(default="sqlite:///./app.db")
    debug: bool = Field(default=False)

    # Add custom settings
    secret_key: str = Field(default="", alias="SECRET_KEY")
    api_key: str = Field(default="", alias="API_KEY")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True
    )
```

### Custom FastAPI App Settings

Modify `core/app.py` to customize the FastAPI app instance:

```python
app = kit.create_app()

# Customize app metadata
app.title = "My API"
app.version = "1.0.0"
app.description = "API description"
app.terms_of_service = "https://example.com/terms"
app.contact = {
    "name": "API Support",
    "email": "support@example.com",
}

# Add custom OpenAPI tags
app.openapi_tags = [
    {
        "name": "users",
        "description": "User management operations",
    },
]
```

## Next Steps

-   [Creating Apps](creating-apps.md) - Create your first app
-   [Migrations](migrations.md) - Manage database schema
-   [Configuration](../configuration/index.md) - Configure your project
