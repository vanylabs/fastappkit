# Deployment

Production deployment guide for fastappkit applications.

## Pre-Deployment Checklist

### 1. Update Dependency Versions

**CRITICAL**: Update dependency versions in `pyproject.toml` from `*` to specific ranges:

```toml
[tool.poetry.dependencies]
python = ">=3.11,<4.0"
fastapi = ">=0.120.0,<0.130"
sqlalchemy = ">=2.0,<3.0"
alembic = ">=1.17.2,<1.18"
```

### 2. Configure Production Settings

Edit `core/config.py` for production:

```python
class Settings(BaseSettings):
    database_url: str = Field(default="")  # No default in production
    debug: bool = Field(default=False)  # Always False in production

    # Production-specific settings
    secret_key: str = Field(alias="SECRET_KEY")  # Required, no default
    allowed_hosts: list[str] = Field(default=["*"], alias="ALLOWED_HOSTS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        populate_by_name=True
    )
```

### 3. Run Migrations

Always run migrations before deploying:

```bash
fastappkit migrate all
```

### 4. Validate Apps

Validate all apps:

```bash
fastappkit app validate <name>  # For each app
```

## Production Settings

### Database Configuration

Use production database:

```bash
# .env or environment variables
DATABASE_URL=postgresql://user:password@host:5432/production_db
```

### Security Settings

```bash
DEBUG=false
SECRET_KEY=<strong-secret-key>
ALLOWED_HOSTS=api.example.com,www.example.com
```

### Environment Variables

Set all required environment variables in production:
-   `DATABASE_URL`
-   `DEBUG`
-   `SECRET_KEY`
-   Any custom settings

!!! warning "Security"
    Never commit `.env` files with sensitive data. Use environment variables or secure secret management systems in production.

## Running Migrations in Production

### Migration Strategy

Run migrations in a separate step before deploying application code:

```bash
# Step 1: Run migrations
fastappkit migrate all

# Step 2: Deploy application code
# (restart server, etc.)
```

This ensures the database schema is ready before the new code runs.

### Migration Safety

-   **Backup database** before running migrations
-   **Test migrations** in staging first
-   **Review SQL** with `fastappkit migrate preview`
-   **Monitor** migration execution

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

**Better approach** (separate migration step):

```dockerfile
# Run migrations separately
CMD ["fastappkit", "migrate", "all"]

# Then start server
CMD ["fastappkit", "core", "dev", "--host", "0.0.0.0", "--port", "8000"]
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
Environment="DEBUG=false"
ExecStart=/path/to/venv/bin/fastappkit core dev --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### Process Managers

Use process managers like Supervisor or systemd to:
-   Manage application process
-   Ensure restart on failure
-   Handle logging
-   Manage multiple workers

### Cloud Platforms

#### Heroku

```bash
# Procfile
web: fastappkit core dev --host 0.0.0.0 --port $PORT
release: fastappkit migrate all
```

#### AWS/GCP/Azure

-   Use container services (ECS, Cloud Run, Container Instances)
-   Set environment variables in platform settings
-   Run migrations as separate deployment step
-   Use managed databases (RDS, Cloud SQL, etc.)

## Monitoring and Maintenance

### Health Checks

Add health check endpoint:

```python
# core/app.py or in an app
@app.get("/health")
def health_check():
    return {"status": "healthy"}
```

### Logging

Configure production logging:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
```

### Database Maintenance

-   Regular backups
-   Monitor database performance
-   Review migration history
-   Plan for schema changes

## Next Steps

-   [Configuration](../configuration/index.md) - Production configuration
-   [Troubleshooting](../troubleshooting/common-issues.md) - Production issues
-   [Best Practices](../advanced/best-practices.md) - Recommended patterns
