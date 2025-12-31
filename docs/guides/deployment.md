# Deployment

This guide covers deploying fastappkit applications to production.

## Production Considerations

### Environment Variables

Ensure all required environment variables are set in your production environment:

```bash
DATABASE_URL=postgresql://user:password@host:5432/dbname
DEBUG=false
# Add your custom settings here
```

!!! warning "Security"
Never commit `.env` files with sensitive data. Use environment variables or secure secret management systems in production.

### Dependency Versions

Update dependency versions in `pyproject.toml` from `*` to specific ranges for production:

```toml
[tool.poetry.dependencies]
python = ">=3.11,<4.0"
fastapi = ">=0.120.0,<0.130"
sqlalchemy = ">=2.0,<3.0"
alembic = ">=1.17.2,<1.18"
```

### Database Migrations

Always run migrations before deploying:

```bash
fastappkit migrate all
```

!!! tip "Migration Strategy"
Run migrations in a separate step before deploying application code. This ensures the database schema is ready before the new code runs.

## Deployment Options

### Docker

Create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy application code
COPY . .

# Run migrations and start server
CMD ["sh", "-c", "fastappkit migrate all && fastappkit core dev --host 0.0.0.0 --port 8000"]
```

### Systemd Service

Create a systemd service file:

```ini
[Unit]
Description=FastAppKit Application
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/your/project
Environment="DATABASE_URL=postgresql://..."
ExecStart=/path/to/venv/bin/fastappkit core dev --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Process Managers

Use process managers like Supervisor or systemd to manage your application process and ensure it restarts on failure.

## Production Server

For production, use a production ASGI server instead of the development server:

```bash
# Using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# Or use gunicorn with uvicorn workers
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

!!! note "Development Server"
The `fastappkit core dev` command is intended for development only. Use a production ASGI server for production deployments.

## Monitoring and Logging

Configure proper logging for production:

```python
# core/config.py
import logging
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = Field(alias="DATABASE_URL")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=".env",
        populate_by_name=True
    )

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Health Checks

Add health check endpoints:

```python
# core/app.py or in an app
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "healthy"}
```

## Learn More

-   [Configuration Guide](configuration.md) - Production configuration
-   [Best Practices](../advanced/best-practices.md) - Production best practices
