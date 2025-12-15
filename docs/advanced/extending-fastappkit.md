# Extending fastappkit

This guide covers extending fastappkit functionality.

## Customizing FastAppKit

### Subclassing FastAppKit

You can subclass `FastAppKit` to customize app creation:

```python
from fastappkit.core.kit import FastAppKit
from fastapi import FastAPI
from core.config import Settings

class CustomFastAppKit(FastAppKit):
    def create_app(self) -> FastAPI:
        app = super().create_app()

        # Add custom middleware
        app.add_middleware(...)

        # Customize app metadata
        app.title = "My Custom API"
        app.version = "1.0.0"
        app.description = "Custom API description"

        # Add exception handlers
        app.add_exception_handler(...)

        return app

settings = Settings()
kit = CustomFastAppKit(settings=settings)
app = kit.create_app()
```

### Custom App Loaders

You can create custom app loaders:

```python
from fastappkit.core.loader import AppLoader
from fastappkit.core.registry import AppRegistry

class CustomAppLoader(AppLoader):
    def load_all(self) -> AppRegistry:
        registry = super().load_all()

        # Custom processing
        # ...

        return registry
```

## Custom Validation

### Custom Validators

Create custom validators:

```python
from fastappkit.validation.manifest import ValidationResult

class CustomValidator:
    def validate(self, manifest: dict) -> ValidationResult:
        result = ValidationResult()

        # Custom validation logic
        if not manifest.get("custom_field"):
            result.add_error("custom_field is required")

        return result
```

## Custom Migration Handlers

### Custom Migration Runner

Extend the migration runner:

```python
from fastappkit.migrations.runner import MigrationRunner

class CustomMigrationRunner(MigrationRunner):
    def upgrade_all(self) -> None:
        # Custom pre-upgrade logic
        self.before_upgrade()

        # Run standard upgrade
        super().upgrade_all()

        # Custom post-upgrade logic
        self.after_upgrade()

    def before_upgrade(self) -> None:
        # Custom logic
        pass

    def after_upgrade(self) -> None:
        # Custom logic
        pass
```

## Plugin System

While fastappkit doesn't have a formal plugin system yet, you can:

1. Create external apps that extend functionality
2. Use the settings system for configuration
3. Hook into app loading via custom loaders
4. Extend migration system via custom runners

## Best Practices

1. **Follow Isolation Rules:** Ensure your extensions respect app isolation
2. **Validate Inputs:** Always validate configuration and inputs
3. **Error Handling:** Provide clear error messages
4. **Documentation:** Document your extensions thoroughly
5. **Testing:** Test extensions thoroughly

## Learn More

- [Architecture](architecture.md) - Understanding the system
- [Best Practices](best-practices.md) - Development best practices
