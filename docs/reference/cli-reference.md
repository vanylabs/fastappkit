# CLI Reference

Complete reference for all fastappkit CLI commands.

## Global Options

All commands support these global options:

- `--verbose, -v`: Enable verbose output
- `--debug`: Enable debug output (includes stack traces)
- `--quiet, -q`: Suppress output
- `--version, -V`: Show version and exit

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

- `<name>`: Project name (required)

**Options:**

- `--project-root <path>`: Directory to create project in (default: current working directory)
- `--description <text>`: Project description

**Examples:**

```bash
fastappkit core new myproject
fastappkit core new myproject --project-root /path/to/projects
fastappkit core new myproject --description "My API project"
```

### `fastappkit core dev`

Run the development server.

**Syntax:**

```bash
fastappkit core dev [--host <host>] [--port <port>] [--reload] [--verbose] [--debug] [--quiet]
```

**Options:**

- `--host, -h <host>`: Host to bind to (default: `127.0.0.1`)
- `--port, -p <port>`: Port to bind to (default: `8000`)
- `--reload`: Enable auto-reload on code changes
- `--verbose, -v`: Enable verbose output (overrides global setting)
- `--debug`: Enable debug output (overrides global setting, includes stack traces)
- `--quiet, -q`: Suppress output (overrides global setting)

**Note:** This command must be run from the project root directory (where `fastappkit.toml` is located).

**Examples:**

```bash
fastappkit core dev
fastappkit core dev --host 0.0.0.0 --port 8080
fastappkit core dev --reload
```

## App Commands

### `fastappkit app new`

Create a new app (internal or external).

**Syntax:**

```bash
fastappkit app new <name> [--as-package]
```

**Arguments:**

- `<name>`: App name (required)

**Options:**

- `--as-package`: Create as external package (required for external apps)

**Note:** This command must be run from the project root directory (where `fastappkit.toml` is located).

**Examples:**

```bash
fastappkit app new blog
fastappkit app new payments --as-package
```

### `fastappkit app list`

List all apps in the project.

**Syntax:**

```bash
fastappkit app list [--verbose] [--debug] [--quiet]
```

**Options:**

- `--verbose, -v`: Show detailed information (import path, migrations path, etc.)
- `--debug`: Show debug information
- `--quiet, -q`: Suppress output

**Note:** This command must be run from the project root directory.

**Examples:**

```bash
fastappkit app list
fastappkit app list --verbose
```

### `fastappkit app validate`

Validate an app's structure and configuration.

**Syntax:**

```bash
fastappkit app validate <name> [--json]
```

**Arguments:**

- `<name>`: App name (required)

**Options:**

- `--json`: Output results as JSON (CI-friendly)

**Note:** This command must be run from the project root directory.

**Examples:**

```bash
fastappkit app validate blog
fastappkit app validate payments --json
```

## Migration Commands

### `fastappkit migrate core`

Generate core migrations.

**Syntax:**

```bash
fastappkit migrate core -m <message>
```

**Options:**

- `-m, --message <message>`: Migration message (required)

**Note:** This command must be run from the project root directory.

**Examples:**

```bash
fastappkit migrate core -m "Add session table"
```

### `fastappkit migrate app`

Manage app migrations.

**Syntax:**

```bash
fastappkit migrate app <name> <action> [options]
```

**Arguments:**

- `<name>`: App name (required)
- `<action>`: Migration action (required)

**Actions:**

- `makemigrations`: Generate new migration (internal apps only)
- `upgrade`: Apply migrations (external apps only)
- `downgrade`: Revert migrations (external apps only)
- `preview`: Show SQL without executing (external apps only)

**Options:**

- `-m, --message <message>`: Migration message (required for `makemigrations`)
- `--revision, -r <rev>`: Specific revision (default: `head` for upgrade/preview)

**Note:** This command must be run from the project root directory.

**Limitations:**

- Internal apps can only use `makemigrations` action. For preview/upgrade/downgrade, use unified commands (`fastappkit migrate preview/upgrade/downgrade`).
- External apps cannot use `makemigrations` from the core project. Migrations must be created in the external app's own directory using `alembic` directly.

**Error Scenarios:**

- If external app has no migration files, the command will fail with instructions on how to create migrations independently.
- If revision is not found, the command will fail with helpful error messages.
- If app is not found in registry, the command will fail with app name error.

**Examples:**

```bash
# Internal app - create migration
fastappkit migrate app blog makemigrations -m "Add post model"

# External app - upgrade
fastappkit migrate app payments upgrade

# External app - upgrade to specific revision
fastappkit migrate app payments upgrade --revision abc123

# External app - preview SQL
fastappkit migrate app payments preview

# External app - downgrade (revision required)
fastappkit migrate app payments downgrade abc123
```

### `fastappkit migrate preview`

Preview SQL for core + internal app migrations (dry-run).

**Syntax:**

```bash
fastappkit migrate preview [--revision <rev>]
```

**Options:**

- `--revision, -r <rev>`: Specific revision (default: `head`)

**Note:** This command must be run from the project root directory.

**Examples:**

```bash
fastappkit migrate preview
fastappkit migrate preview --revision abc123
```

### `fastappkit migrate upgrade`

Apply core + internal app migrations.

**Syntax:**

```bash
fastappkit migrate upgrade [--revision <rev>]
```

**Options:**

- `--revision, -r <rev>`: Specific revision (default: `head`)

**Note:** This command must be run from the project root directory.

**Examples:**

```bash
fastappkit migrate upgrade
fastappkit migrate upgrade --revision abc123
```

### `fastappkit migrate downgrade`

Revert core + internal app migrations.

**Syntax:**

```bash
fastappkit migrate downgrade <revision>
```

**Arguments:**

- `<revision>`: Revision to downgrade to (required)

**Note:** This command must be run from the project root directory.

**Examples:**

```bash
fastappkit migrate downgrade abc123
```

### `fastappkit migrate all`

Apply all migrations in the correct order.

**Syntax:**

```bash
fastappkit migrate all
```

**Note:** This command must be run from the project root directory.

**Execution Order:**

1. Core migrations (always first)
2. Internal apps (in config order) - skipped (already included in core migrations)
3. External apps (in config order)

**Examples:**

```bash
fastappkit migrate all
```

## Command Reference Table

| Command | Description | Options |
|---------|-------------|---------|
| `fastappkit core new <name>` | Create new project | `--project-root`, `--description` |
| `fastappkit core dev` | Run development server | `--host`, `--port`, `--reload`, `--verbose`, `--debug`, `--quiet` |
| `fastappkit app new <name>` | Create internal app | `--as-package` |
| `fastappkit app list` | List all apps | `--verbose`, `--debug`, `--quiet` |
| `fastappkit app validate <name>` | Validate app | `--json` |
| `fastappkit migrate core` | Core migrations | `-m, --message` |
| `fastappkit migrate app <name>` | App migrations | `makemigrations`, `upgrade`, `downgrade`, `preview` |
| `fastappkit migrate preview` | Preview SQL | `--revision` |
| `fastappkit migrate upgrade` | Upgrade migrations | `--revision` |
| `fastappkit migrate downgrade <rev>` | Downgrade migrations | (revision required) |
| `fastappkit migrate all` | Apply all migrations | (no options) |

## Learn More

- [Creating Projects](../guides/creating-projects.md) - Project creation guide
- [Creating Apps](../guides/creating-apps.md) - App creation guide
- [Migrations](../guides/migrations.md) - Migration workflows
