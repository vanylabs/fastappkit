# Router Mounting

fastappkit automatically mounts app routers with configurable prefixes.

## Architecture

```
┌───────────────────── FastAPI app ───────────────────────┐
│                                                         │
│   /core/...                                             │
│                                                         │
│   /blog/...              <-- internal apps              │
│   /account/...                                          │
│                                                         │
│   /fastapi_blog/...      <-- external apps              │
│   /fastapi_store/...                                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

## Default Prefix

The default prefix is `/<appname>`:

- `apps.blog` → `/blog`
- `fastapi_payments` → `/fastapi_payments`

## Override Methods

### Via Manifest

```toml
# In fastappkit.toml (external apps) or inferred (internal apps)
route_prefix = "/api/blog"
```

### Via Register Function

```python
def register(app: FastAPI) -> None:
    # Mount with custom prefix, tags, dependencies
    app.include_router(
        router,
        prefix="/api/v1/blog",
        tags=["blog", "content"],
        dependencies=[Depends(require_auth)]
    )
```

### Empty Prefix

```toml
route_prefix = ""  # Mounts at root level
```

## Customization Options

- **Tags:** Add OpenAPI tags: `tags=["blog", "content"]`
- **Dependencies:** Add route dependencies: `dependencies=[Depends(...)]`
- **Response Class:** Customize response: `response_class=CustomResponse`
- **Prefix Override:** Override manifest prefix in `register()`
- **Multiple Routers:** Mount multiple routers from same app
- **Sub-applications:** Mount sub-applications: `app.mount("/static", StaticFiles(...))`

## Route Collision Detection

fastappkit automatically detects overlapping routes (same path + method):

- Emits warnings (not fatal) - startup continues
- Shows which apps have conflicting routes
- Provides suggestions for resolution
- Developer responsibility to fix collisions

### Example Collision

If two apps use the same prefix:

```
ROUTE COLLISIONS DETECTED
🔴 Collision between apps: blog, news
   App 'blog' uses prefix: /api
   App 'news' uses prefix: /api

   Conflicting routes (2 found):
     • GET    /api/posts
     • POST   /api/posts
```

## Entrypoint Patterns

### Function-based

```python
def register(app: FastAPI) -> APIRouter | None:
    """Register app with FastAPI application.

    Can return APIRouter (fastappkit mounts it) or None (mount yourself).
    """
    settings = get_settings()
    # Option 1: Return router
    return router
    # Option 2: Mount yourself
    # app.include_router(router, prefix="/blog")
    # return None
```

### Class-based

```python
class App:
    def register(self, app: FastAPI) -> APIRouter | None:
        """Register app with FastAPI application."""
        settings = get_settings()
        app.include_router(router, prefix="/blog")
        return None  # Or return router
```

### Entrypoint String Formats

- `"blog:register"` - Function in module
- `"blog:App"` - Class (must have `register` method)
- `"blog"` - Defaults to `"blog:register"`
- `"blog.main:register"` - Function in submodule

The loader instantiates class-based apps with no constructor arguments.

## What `register()` Can Do

- Return `APIRouter` - fastappkit mounts it with prefix
- Mount routers yourself - fastappkit skips mounting
- Register startup/shutdown events: `@app.on_event("startup")`
- Add middleware: `app.add_middleware(...)`
- Add exception handlers: `app.add_exception_handler(...)`
- Add background tasks: `app.add_task(...)`
- Access settings via `get_settings()`
- Mount sub-applications: `app.mount(...)`
- Add dependencies, tags, etc. when mounting routers

## What `register()` Must Not Do

- Modify global FastAPI state outside its namespace
- Perform blocking operations at import time
- Connect to DB directly (use startup events instead)
- Access settings via global variables (use `get_settings()`)
- Raise exceptions that prevent other apps from loading

## Learn More

- [Creating Apps](../guides/creating-apps.md) - How to create apps with routers
- [Internal Apps](internal-apps.md) - Internal app router patterns
- [External Apps](external-apps.md) - External app router patterns
