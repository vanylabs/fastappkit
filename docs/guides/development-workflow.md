# Development Workflow

Day-to-day development practices for fastappkit projects.

## Starting Development Server

### Basic Command

```bash
fastappkit core dev
```

**IMPORTANT**: Must be run from project root.

### Options

-   `--host <host>`: Host to bind to (default: `127.0.0.1`)
-   `--port <port>`: Port to bind to (default: `8000`)
-   `--reload`: Enable auto-reload on code changes

### Uvicorn Options Forwarding

All additional arguments are forwarded to uvicorn:

```bash
fastappkit core dev --workers 4
fastappkit core dev --log-level debug
fastappkit core dev --access-log
```

**IMPORTANT**: Server uses core project's `DATABASE_URL` from `.env`.

## Development Cycle

### Typical Workflow

1. **Create/Modify Models**
   ```python
   # apps/blog/models.py
   class Post(Base):
       __tablename__ = "posts"
       title = Column(String)
   ```

2. **Create Migration**
   ```bash
   fastappkit migrate app blog makemigrations -m "Add post model"
   ```

3. **Apply Migration**
   ```bash
   fastappkit migrate all
   ```

4. **Test Endpoints**
   ```bash
   fastappkit core dev
   # Visit http://127.0.0.1:8000/docs
   ```

5. **Iterate**
   -   Make changes
   -   Create migrations
   -   Test
   -   Repeat

## Testing

### Manual Testing with Development Server

```bash
fastappkit core dev
```

-   Visit `http://127.0.0.1:8000/docs` for Swagger UI
-   Visit `http://127.0.0.1:8000/redoc` for ReDoc
-   Test endpoints with curl or httpx

### Testing External Apps Independently

```bash
cd <external-app>
uvicorn main:app --reload
```

-   Uses external app's `.env` and `DATABASE_URL`
-   Test app in isolation before integrating

### Integration Testing

After adding external app to core project:

```bash
cd <core-project>
fastappkit core dev
```

-   Uses core project's `DATABASE_URL`
-   Test all apps together

## Debugging

### Using `--debug` Flag

```bash
fastappkit core dev --debug
```

Shows:
-   Stack traces
-   Detailed error messages
-   Full exception information

### Logging Configuration

Configure logging in `core/app.py`:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
```

### Common Issues

#### App Not Loading

**Error**: `AppLoadError: Failed to load app`

**Solution**: Run validation:
```bash
fastappkit app validate <name>
```

#### Route Collisions

**Warning**: `Route collision detected`

**Solution**: Check `route_prefix` in manifests:
```toml
# fastappkit.toml (external app)
route_prefix = "/api/blog"
```

#### Import Errors

**Error**: `ModuleNotFoundError`

**Solution**:
-   Check `__init__.py` files exist
-   Verify dependencies are installed
-   Check Python path includes project root

#### Settings Not Loaded

**Error**: Runtime errors when calling `get_settings()`

**Solution**: Verify `core/app.py` initializes Settings:
```python
settings = Settings()
kit = FastAppKit(settings=settings)
app = kit.create_app()
```

## Critical Requirements

### All Commands from Project Root

**CRITICAL**: All commands must be run from project root (where `fastappkit.toml` is located).

**Commands affected:**
-   `fastappkit app new`
-   `fastappkit app list`
-   `fastappkit app validate`
-   `fastappkit migrate *`
-   `fastappkit core dev`

### External Apps Must be Pip-Installed

**CRITICAL**: External apps must be pip-installed before use:
```bash
pip install -e /path/to/app
```

### Settings Must be Initialized

**CRITICAL**: Settings must be initialized in `core/app.py`:
```python
settings = Settings()
kit = FastAppKit(settings=settings)
```

### Database Must be Accessible

**CRITICAL**: Check `DATABASE_URL` in `.env`:
```bash
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
```

## Best Practices

1. **Run migrations before starting server**
   ```bash
   fastappkit migrate all
   fastappkit core dev
   ```

2. **Use `--reload` for development**
   ```bash
   fastappkit core dev --reload
   ```

3. **Validate apps regularly**
   ```bash
   fastappkit app validate <name>
   ```

4. **Test external apps independently first**
   ```bash
   cd <external-app>
   uvicorn main:app --reload
   ```

5. **Check for route collisions**
   -   Review `route_prefix` in manifests
   -   Ensure unique prefixes

## Next Steps

-   [Deployment](deployment.md) - Production deployment
-   [Troubleshooting](../troubleshooting/common-issues.md) - Common problems
-   [CLI Reference](../reference/cli-reference.md) - All commands
