# Router Mounting

How routers are automatically mounted in fastappkit applications.

## Automatic Mounting

If `register()` returns `APIRouter`, it's automatically mounted by fastappkit:

```python
def register(app: FastAPI) -> APIRouter:
    return router  # Auto-mounted with prefix
```

The prefix comes from:
1. Manifest `route_prefix` (if specified)
2. Default `/<appname>` (if not specified)

## Route Prefixes

### Default Prefix

If not specified in manifest, default is `/<appname>`:

```python
# App name: "blog"
# Default prefix: "/blog"
```

### Custom Prefix

Specify in manifest:

```toml
# fastappkit.toml (external app)
route_prefix = "/api/blog"
```

Or in internal app, you can mount manually:

```python
def register(app: FastAPI) -> None:
    app.include_router(router, prefix="/api/blog")
    return None  # Manual mount
```

### Empty Prefix (Root Mount)

Use empty string to mount at root level:

```toml
route_prefix = ""  # Mounts at root level
```

**Use with caution**: Can cause route collisions.

## Registration Function

### Auto-Mount

Return `APIRouter` from `register()`:

```python
def register(app: FastAPI) -> APIRouter:
    """Register this app with the FastAPI application."""
    return router  # Auto-mounted with prefix from manifest
```

### Manual Mount

Return `None` and mount yourself:

```python
def register(app: FastAPI) -> None:
    """Register this app with the FastAPI application."""
    app.include_router(router, prefix="/custom/prefix")
    return None  # Manual mount, fastappkit skips
```

## Mount Order

Apps are mounted in order from `fastappkit.toml`:

```toml
[tool.fastappkit]
apps = [
  "apps.blog",      # Mounted first
  "apps.auth",      # Mounted second
  "payments",        # Mounted third
]
```

Route collision detection runs **after** all mounts.

## Route Collision Detection

fastappkit detects route collisions and emits warnings (not fatal):

```
⚠️  ROUTE COLLISIONS DETECTED

   Route '/api' used by multiple apps:
   - blog (prefix: /api)
   - auth (prefix: /api)

   💡 Fix: Change route_prefix for one of the apps
```

**Detection:**
-   Checks for overlapping route paths
-   Warns but doesn't fail
-   Developer responsibility to fix

## Examples

### Auto-Mount with Default Prefix

```python
# apps/blog/__init__.py
router = APIRouter()

@router.get("/posts")
def list_posts():
    return []

def register(app: FastAPI) -> APIRouter:
    return router  # Auto-mounted at "/blog"
```

### Auto-Mount with Custom Prefix

```toml
# External app manifest
route_prefix = "/api/blog"
```

```python
def register(app: FastAPI) -> APIRouter:
    return router  # Auto-mounted at "/api/blog"
```

### Manual Mount

```python
def register(app: FastAPI) -> None:
    app.include_router(router, prefix="/custom/prefix", tags=["blog"])
    return None  # Manual mount
```

## Common Issues

### Route Collisions

**Warning**: `Route collision detected`

**Solution**: Check `route_prefix` in manifests:
```toml
# Change one app's prefix
route_prefix = "/api/blog"  # Instead of "/blog"
```

### Duplicate App Names

**Warning**: `Duplicate app names detected`

**Problem**: May cause route conflicts

**Solution**: Rename one of the apps.

### Router Not Mounting

**Problem**: Routes not accessible

**Solution**:
-   Check `register()` returns `APIRouter` (for auto-mount)
-   Or verify manual mount in `register()` function
-   Check app is in `fastappkit.toml`

## Learn More

-   [Creating Apps](../guides/creating-apps.md) - App creation guide
-   [CLI Reference](../reference/cli-reference.md) - Command reference
