# Debugging

Techniques for debugging fastappkit applications.

## Verbose and Debug Output

### Enable Verbose Output

```bash
fastappkit app list --verbose
fastappkit core dev --verbose
```

Shows detailed information about operations.

### Enable Debug Output

```bash
fastappkit app list --debug
fastappkit core dev --debug
```

Shows debug information including stack traces.

## App Validation

Validate apps to check for issues:

```bash
fastappkit app validate <name>
```

For JSON output (useful for CI/CD):

```bash
fastappkit app validate <name> --json
```

## Migration Preview

Preview SQL before applying migrations:

```bash
# Core + internal apps
fastappkit migrate preview

# External app
fastappkit migrate app <name> preview
```

## Database Inspection

Check database state:

```sql
-- Core & internal apps version
SELECT * FROM alembic_version;

-- External app version
SELECT * FROM alembic_version_<appname>;

-- Check tables
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public';
```

## App Registry Inspection

Start dev server with debug to see app loading details:

```bash
fastappkit core dev --debug
```

Check logs for:

- App resolution steps
- App registration steps
- Router mounting details
- Validation results

## Python Debugger

Use Python debugger for code inspection:

```python
import pdb; pdb.set_trace()
```

Or use breakpoints in your IDE.

## Logging

Configure logging for detailed output:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Common Debugging Scenarios

### App Not Loading

1. Check app exists: `fastappkit app list`
2. Validate app: `fastappkit app validate <name>`
3. Check logs: `fastappkit core dev --debug`
4. Verify manifest (external apps)
5. Check entrypoint import

### Migration Issues

1. Preview SQL: `fastappkit migrate preview`
2. Check database state (SQL queries above)
3. Verify migration files exist
4. Check migration order in config

### Router Not Mounted

1. Check app is loaded: `fastappkit app list`
2. Verify route prefix
3. Check for route collisions
4. Inspect app registry with debug output

## Learn More

- [Common Issues](common-issues.md) - Common problems and solutions
- [CLI Reference](../reference/cli-reference.md) - Command options
