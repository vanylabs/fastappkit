# CLI Reference

Complete reference for all fastappkit CLI commands.

## Global Options

All commands support these global options:

-   `--verbose, -v`: Enable verbose output
-   `--debug`: Enable debug output (includes stack traces)
-   `--quiet, -q`: Suppress output
-   `--version, -V`: Show version and exit

### Show Version

```bash
fastappkit --version
# Or use short form:
fastappkit -V
```

Shows the installed fastappkit version.

## Project Commands

### `fastappkit core new`

Create a new fastappkit project.

**Syntax:**

```bash
fastappkit core new <name> [--project-root <path>] [--description <text>]
```

**Arguments:**

-   `<name>`: Project name (required)

**Options:**

-   `--project-root <path>`: Directory to create project in (default: current working directory)
-   `--description <text>`: Project description

**Examples:**

```bash
fastappkit core new myproject
fastappkit core new myproject --project-root /path/to/projects
fastappkit core new myproject --description "My API project"
```

**Notes:**

-   Creates complete project structure
-   Generates `fastappkit.toml`, `core/`, `apps/`, etc.
-   Creates `.env` file with defaults

### `fastappkit core dev`

Run the development server.

**Syntax:**

```bash
fastappkit core dev [--host <host>] [--port <port>] [--reload] [<uvicorn-options>]
```

**Options:**

-   `--host, -h <host>`: Host to bind to (default: `127.0.0.1`)
-   `--port, -p <port>`: Port to bind to (default: `8000`)
-   `--reload`: Enable auto-reload on code changes
-   `<uvicorn-options>`: Additional options are forwarded to uvicorn (e.g., `--workers`, `--log-level`, `--access-log`)

**Examples:**

```bash
fastappkit core dev
fastappkit core dev --host 0.0.0.0 --port 8080
fastappkit core dev --reload
fastappkit core dev --workers 4
fastappkit core dev --log-level debug
fastappkit core dev --access-log
```

**Notes:**

-   Must be run from project root directory (where `fastappkit.toml` is located)
-   All additional arguments are forwarded to uvicorn
-   Uses core project's `DATABASE_URL` from `.env`

## App Commands

### `fastappkit app new`

Create a new app (internal or external).

**Syntax:**

```bash
fastappkit app new <name> [--as-package]
```

**Arguments:**

-   `<name>`: App name (required)

**Options:**

-   `--as-package`: Create as external package (required for external apps)

**Examples:**

```bash
fastappkit app new blog
fastappkit app new payments --as-package
```

**Notes:**

-   Must be run from project root directory (for internal apps)
-   Internal apps are automatically added to `fastappkit.toml`
-   External apps must be pip-installed: `pip install -e .`

### `fastappkit app list`

List all apps in the project.

**Syntax:**

```bash
fastappkit app list [--verbose] [--debug] [--quiet]
```

**Options:**

-   `--verbose, -v`: Show detailed information (import path, migrations path, etc.)
-   `--debug`: Show debug information
-   `--quiet, -q`: Suppress output

**Examples:**

```bash
fastappkit app list
fastappkit app list --verbose
```

**Notes:**

-   Must be run from project root directory
-   Shows app name, type (internal/external), and route prefix

### `fastappkit app validate`

Validate an app's structure and configuration.

**Syntax:**

```bash
fastappkit app validate <name> [--json]
```

**Arguments:**

-   `<name>`: App name (required)

**Options:**

-   `--json`: Output results as JSON (CI-friendly)

**Examples:**

```bash
fastappkit app validate blog
fastappkit app validate payments --json
```

**Notes:**

-   Must be run from project root directory
-   Validates manifest, isolation, and migrations
-   Returns exit code 1 if validation fails

## Migration Commands

### `fastappkit migrate core`

Generate core migrations.

**Syntax:**

```bash
fastappkit migrate core -m <message>
```

**Options:**

-   `-m, --message <message>`: Migration message (required)

**Examples:**

```bash
fastappkit migrate core -m "Add session table"
```

**Notes:**

-   Must be run from project root directory
-   Creates migration in `core/db/migrations/versions/`

### `fastappkit migrate app`

Manage app migrations.

**Syntax:**

```bash
fastappkit migrate app <name> <action> [options]
```

**Arguments:**

-   `<name>`: App name (required)
-   `<action>`: Action to perform (required)
    -   `makemigrations` - Create migration (internal apps only)
    -   `upgrade` - Apply migrations (external apps)
    -   `downgrade` - Downgrade migrations (external apps)
    -   `preview` - Preview SQL (external apps)

**Options:**

-   `--revision, -r <revision>`: Specific revision (for upgrade/downgrade/preview)
-   `-m, --message <message>`: Migration message (for makemigrations)

**Examples:**

```bash
# Internal app: create migration
fastappkit migrate app blog makemigrations -m "Add post model"

# External app: apply migrations
fastappkit migrate app payments upgrade

# External app: preview SQL
fastappkit migrate app payments preview --revision head

# External app: downgrade
fastappkit migrate app payments downgrade --revision abc123
```

**Notes:**

-   Must be run from project root directory
-   `makemigrations` only works for internal apps
-   External apps must create migrations independently using `alembic`

### `fastappkit migrate all`

Apply all migrations in order: core + internal apps → external apps.

**Syntax:**

```bash
fastappkit migrate all
```

**Examples:**

```bash
fastappkit migrate all
```

**Notes:**

-   Must be run from project root directory
-   Execution order: Core → Internal apps (skipped, already in core) → External apps
-   Recommended command for normal workflows

### `fastappkit migrate upgrade`

Apply core + internal app migrations.

**Syntax:**

```bash
fastappkit migrate upgrade [--revision <revision>]
```

**Options:**

-   `--revision, -r <revision>`: Specific revision (default: `head`)

**Examples:**

```bash
fastappkit migrate upgrade
fastappkit migrate upgrade --revision abc123
```

**Notes:**

-   Must be run from project root directory
-   Applies migrations from shared directory (`core/db/migrations/`)

### `fastappkit migrate downgrade`

Downgrade core + internal app migrations.

**Syntax:**

```bash
fastappkit migrate downgrade <revision>
```

**Arguments:**

-   `<revision>`: Revision to downgrade to (required)

**Examples:**

```bash
fastappkit migrate downgrade abc123
```

**Notes:**

-   Must be run from project root directory
-   Downgrades migrations from shared directory

### `fastappkit migrate preview`

Preview SQL for core + internal app migrations.

**Syntax:**

```bash
fastappkit migrate preview [--revision <revision>]
```

**Options:**

-   `--revision, -r <revision>`: Specific revision (default: `head`)

**Examples:**

```bash
fastappkit migrate preview
fastappkit migrate preview --revision abc123
```

**Notes:**

-   Must be run from project root directory
-   Shows SQL without applying migrations
-   Useful for reviewing changes before applying

## Command Summary

| Command | Purpose | Must Run From Project Root |
|---------|---------|----------------------------|
| `fastappkit core new <name>` | Create new project | No |
| `fastappkit core dev` | Run development server | Yes |
| `fastappkit app new <name>` | Create internal app | Yes |
| `fastappkit app new <name> --as-package` | Create external app | No |
| `fastappkit app list` | List all apps | Yes |
| `fastappkit app validate <name>` | Validate app | Yes |
| `fastappkit migrate core -m "msg"` | Create core migration | Yes |
| `fastappkit migrate app <name> makemigrations -m "msg"` | Create app migration | Yes (internal only) |
| `fastappkit migrate app <name> upgrade` | Apply app migration | Yes (external) |
| `fastappkit migrate all` | Apply all migrations | Yes |
| `fastappkit migrate upgrade` | Apply core + internal | Yes |
| `fastappkit migrate downgrade <rev>` | Downgrade | Yes |
| `fastappkit migrate preview` | Preview SQL | Yes |

## Learn More

-   [Creating Projects](../guides/creating-projects.md) - Project creation guide
-   [Creating Apps](../guides/creating-apps.md) - App creation guide
-   [Migrations](../guides/migrations.md) - Migration workflows
