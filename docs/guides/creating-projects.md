# Creating Projects

This guide covers creating and managing fastappkit projects.

## Create a New Project

Use the `core new` command to create a new project:

```bash
fastappkit core new <name> [--project-root <path>] [--description <text>]
```

### Options

-   `--project-root`: Directory to create project in (default: current working directory)
-   `--description`: Project description

### Behavior

If `--project-root` is not specified, the project is created in the current working directory. The project name becomes a subdirectory.

### What Gets Created

The command creates:

-   Project directory structure
-   `fastappkit.toml` configuration file
-   `.env` file with `DATABASE_URL` placeholder
-   Core application files (`core/app.py`, `core/config.py`, etc.)
-   `main.py` entry point

### Project Structure

```
myproject/
├── core/
│   ├── config.py          # Settings (loads from .env)
│   ├── app.py             # create_app() factory
│   ├── models.py          # Core models (optional)
│   └── db/
│       └── migrations/    # Core migrations
├── apps/                  # Internal apps directory
├── fastappkit.toml        # Project configuration
├── .env                   # Environment variables
└── main.py                # Entry point
```

## Running Development Server

Start the development server:

```bash
fastappkit core dev [--host <host>] [--port <port>] [--reload] [--verbose] [--debug] [--quiet] [<uvicorn-options>]
```

### Options

-   `--host, -h`: Host to bind to (default: `127.0.0.1`)
-   `--port, -p`: Port to bind to (default: `8000`)
-   Additional uvicorn options: All other arguments are forwarded to uvicorn (e.g., `--workers`, `--log-level`, `--access-log`)
-   `--reload`: Enable auto-reload on code changes
-   `--verbose, -v`: Enable verbose output (overrides global setting)
-   `--debug`: Enable debug output (overrides global setting, includes stack traces)
-   `--quiet, -q`: Suppress output (overrides global setting)

!!! note "Project Root Required"
This command must be run from the project root directory (where `fastappkit.toml` is located).

### Behavior

-   Loads all apps from `fastappkit.toml`
-   Mounts routers with automatic prefixes
-   Starts uvicorn server
-   Hot-reloads on code changes (if `--reload` is set)
-   With `--reload`, uses import string (`main:app`) for proper reloading
-   Without `--reload`, creates app object directly for faster startup

## Project Configuration

Projects are configured via `fastappkit.toml`. See the [Configuration Guide](configuration.md) for details.

## Next Steps

-   [Create your first app](creating-apps.md)
-   [Configure your project](configuration.md)
-   [Set up migrations](../topics/migration-system.md)
