# Scenario 2: Scaffolding + Internal Apps

This guide covers building a project with internal apps (like Django apps).

## When to Use This Approach

Use internal apps when:

-   You're building a single project
-   You want modular organization within the project
-   You need shared migrations across features
-   You want to organize code into logical components
-   You don't need reusable components across projects

## Step-by-Step Guide

### 1. Create Project

```bash
fastappkit core new myproject
cd myproject
```

### 2. Update Dependency Versions

**IMPORTANT**: Update dependency versions in `pyproject.toml` from `*` to specific ranges:

```toml
[tool.poetry.dependencies]
python = ">=3.11,<4.0"
fastapi = ">=0.120.0,<0.130"
sqlalchemy = ">=2.0,<3.0"
alembic = ">=1.17.2,<1.18"
```

### 3. Configure Environment

Edit `.env` file:

```bash
DATABASE_URL=sqlite:///./myproject.db
DEBUG=false
```

### 4. Create Internal App

```bash
fastappkit app new blog
```

This creates:
-   `apps/blog/__init__.py` (with `register()` function)
-   `apps/blog/models.py` (imports `Base` from `core.models`)
-   `apps/blog/router.py` (FastAPI router)
-   Automatically adds `"apps.blog"` to `fastappkit.toml`

### 5. Add Models

Edit `apps/blog/models.py`:

```python
from core.models import Base
from sqlalchemy import Column, Integer, String

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    content = Column(String)
```

**IMPORTANT**: Internal apps must import `Base` from `core.models`, not create their own.

### 6. Create Migration

```bash
fastappkit migrate app blog makemigrations -m "initial"
```

This creates a migration in `core/db/migrations/versions/` (shared with core).

### 7. Apply Migrations

```bash
fastappkit migrate all
```

This applies all migrations (core + internal apps) in the correct order.

### 8. Start Development Server

```bash
fastappkit core dev
```

Your API is now running at `http://127.0.0.1:8000` with routes mounted at `/blog/`.

## Development Workflow

### Adding More Internal Apps

```bash
fastappkit app new auth
fastappkit app new payments
```

Each app is automatically added to `fastappkit.toml`.

### Creating Migrations

```bash
# For a specific app
fastappkit migrate app blog makemigrations -m "Add post model"

# For core (if you have core models)
fastappkit migrate core -m "Add session table"
```

### Applying Migrations

```bash
# Apply all migrations (recommended)
fastappkit migrate all

# Or apply core + internal apps only
fastappkit migrate upgrade
```

### Testing Internal Apps

1. **Manual testing:**
   ```bash
   fastappkit core dev
   # Visit http://127.0.0.1:8000/docs
   ```

2. **Test specific endpoints:**
   ```bash
   curl http://127.0.0.1:8000/blog/posts
   ```

## Migration Workflow for Internal Apps

Internal apps share the migration directory with core (`core/db/migrations/`):

1. **Create migration:**
   ```bash
   fastappkit migrate app <name> makemigrations -m "message"
   ```

2. **Review migration:**
   ```bash
   # Preview SQL
   fastappkit migrate preview
   ```

3. **Apply migration:**
   ```bash
   fastappkit migrate all
   ```

4. **If needed, downgrade:**
   ```bash
   fastappkit migrate downgrade <revision>
   ```

## Important Notes

-   **All commands must be run from project root** (where `fastappkit.toml` is located)
-   Internal apps share migration directory with core (`core/db/migrations/`)
-   Internal apps can import from `core.models` and other internal apps
-   Internal apps are automatically added to `fastappkit.toml` by CLI
-   Ensure `apps/<name>/__init__.py` exists (created by CLI, but verify if manual)

## Quick Commands Reference

```bash
# Create project
fastappkit core new myproject && cd myproject

# Create internal app
fastappkit app new blog

# Create migration
fastappkit migrate app blog makemigrations -m "Add post model"

# Apply all migrations
fastappkit migrate all

# Start development server
fastappkit core dev
```

## Common Patterns

### App Dependencies

Internal apps can depend on other internal apps:

```python
# apps/blog/models.py
from apps.auth.models import User
from core.models import Base
from sqlalchemy import Column, Integer, ForeignKey

class Post(Base):
    __tablename__ = "posts"
    author_id = Column(Integer, ForeignKey("users.id"))
```

### Cross-App Relationships

Since all internal apps share the same Base and migration directory, you can create relationships between apps:

```python
# apps/blog/models.py
from apps.auth.models import User

class Post(Base):
    author = relationship("User", back_populates="posts")
```

## Next Steps

-   [Full Ecosystem](full-ecosystem.md) - Add external apps for reusable components
-   [Creating Apps](../guides/creating-apps.md) - Detailed app creation guide
-   [Migrations](../guides/migrations.md) - Complete migration workflow
