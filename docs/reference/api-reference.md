# API Reference

Programmatic API reference for fastappkit.

## Core API

### FastAppKit

Main class for creating FastAPI applications.

```python
from fastappkit.core.kit import FastAppKit
from core.config import Settings

settings = Settings()
kit = FastAppKit(settings=settings)
app = kit.create_app()
```

#### Methods

**`create_app() -> FastAPI`**

Create and configure FastAPI application.

- Loads all apps from `fastappkit.toml`
- Validates app manifests
- Mounts routers with automatic prefixes
- Returns configured FastAPI application

## Settings API

### get_settings()

Get the current settings instance.

```python
from fastappkit.conf import get_settings

settings = get_settings()
db_url = settings.database_url
```

### set_settings()

Set the global settings instance.

```python
from fastappkit.conf import set_settings
from core.config import Settings

settings = Settings()
set_settings(settings)
```

### ensure_settings_loaded()

Ensure settings are loaded from project.

```python
from fastappkit.conf import ensure_settings_loaded
from pathlib import Path

project_root = Path.cwd()
ensure_settings_loaded(project_root)
```

## App Loading API

### AppLoader

Load and register apps from configuration.

```python
from fastappkit.core.loader import AppLoader
from pathlib import Path

project_root = Path.cwd()
loader = AppLoader(project_root)
registry = loader.load_all()
```

#### Methods

**`load_all() -> AppRegistry`**

Load all apps from `fastappkit.toml` and return registry.

### AppRegistry

Registry of loaded apps.

```python
from fastappkit.core.registry import AppRegistry, AppMetadata

registry: AppRegistry = loader.load_all()

# Get app metadata
app_metadata: AppMetadata = registry.get("blog")

# Check if app exists
if "blog" in registry:
    ...

# Iterate over apps
for name, metadata in registry.items():
    ...
```

## Manifest API

### ManifestLoader

Load app manifests.

```python
from fastappkit.core.manifest import ManifestLoader

loader = ManifestLoader()
manifest = loader.load("blog")
```

## Validation API

### ManifestValidator

Validate app manifests.

```python
from fastappkit.validation.manifest import ManifestValidator, ValidationResult

validator = ManifestValidator()
result: ValidationResult = validator.validate(manifest_data)

if result.is_valid:
    print("Manifest is valid")
else:
    for error in result.errors:
        print(f"Error: {error}")
```

### IsolationValidator

Validate app isolation rules.

```python
from fastappkit.validation.isolation import IsolationValidator, ValidationResult

validator = IsolationValidator()
result: ValidationResult = validator.validate(app_metadata)

if not result.is_valid:
    for error in result.errors:
        print(f"Isolation violation: {error}")
```

### MigrationValidator

Validate migration configuration.

```python
from fastappkit.validation.migrations import MigrationValidator, ValidationResult

validator = MigrationValidator()
result: ValidationResult = validator.validate(app_metadata)

if not result.is_valid:
    for error in result.errors:
        print(f"Migration error: {error}")
```

## Migration API

### MigrationRunner

Run migrations.

```python
from fastappkit.migrations.runner import MigrationRunner
from fastappkit.core.registry import AppMetadata

runner = MigrationRunner()
runner.upgrade_all()  # Run all migrations
runner.upgrade_app(app_metadata)  # Run app migrations
```

### MigrationPreview

Preview migration SQL.

```python
from fastappkit.migrations.preview import MigrationPreview

preview = MigrationPreview()
sql = preview.preview(app_metadata, revision="head")
print(sql)
```

## Learn More

- [Architecture](../advanced/architecture.md) - System architecture
- [Extending fastappkit](../advanced/extending-fastappkit.md) - Extension guide
