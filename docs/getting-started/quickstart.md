# Quick Start

This guide will help you create your first fastappkit project in minutes.

## Create a Project

Start by creating a new fastappkit project:

```bash
fastappkit core new myproject
cd myproject
```

This creates a complete FastAPI project structure:

```
myproject/
├── core/
│   ├── config.py          # Settings (loads from .env)
│   ├── app.py             # create_app() factory
│   └── db/
│       └── migrations/    # Core migrations
├── apps/                  # Internal apps directory
├── fastappkit.toml        # Project configuration
├── .env                   # Environment variables
└── main.py                # Entry point
```

## Create an Internal App

Create your first app:

```bash
fastappkit app new blog
```

This creates `apps/blog/` with models, router, and registers it in `fastappkit.toml`.

## Run Migrations

Generate and apply migrations:

```bash
# Generate migration
fastappkit migrate app blog makemigrations -m "initial"

# Apply all migrations
fastappkit migrate all
```

## Start Development Server

Run the development server:

```bash
fastappkit core dev
```

Your API is now running at `http://127.0.0.1:8000` with routes mounted at `/blog/`.

## Next Steps

-   Read the [Core Concepts](core-concepts.md) to understand how fastappkit works
-   Follow the [Creating Apps Guide](../guides/creating-apps.md) for detailed app development
-   Explore the [Migration System](../topics/migration-system.md) for database management
-   Check the [CLI Reference](../reference/cli-reference.md) for all available commands
