# Best Practices

Guidelines for developing with fastappkit.

## Project Organization

### Directory Structure

Follow the standard fastappkit project structure:

```
myproject/
├── core/                    # Core project code
│   ├── config.py           # Settings
│   ├── app.py              # App factory
│   ├── models.py           # Core models (optional)
│   └── db/
│       └── migrations/     # Core migrations
├── apps/                    # Internal apps
│   ├── blog/
│   └── auth/
├── fastappkit.toml         # Project config
├── .env                    # Environment variables
└── main.py                 # Entry point
```

### App Organization

- Keep apps focused on a single domain
- Use clear, descriptive app names
- Follow consistent naming conventions
- Keep app code organized (models, routers, etc.)

## Settings Management

### Environment Variables

- Never commit `.env` files with sensitive data
- Use environment variables for production
- Document required environment variables
- Use different `.env` files for different environments

### Settings Validation

- Use Pydantic validators for custom validation
- Provide sensible defaults
- Validate required settings at startup

## Migrations

### Migration Best Practices

1. **Keep migrations in VCS:** Always commit migration files
2. **Test migrations:** Test upgrades and downgrades
3. **Review SQL:** Use `preview` to review SQL before applying
4. **Small migrations:** Keep migrations focused and small
5. **Reversible:** Ensure migrations can be reversed

### Migration Naming

Use descriptive migration messages:

```bash
fastappkit migrate app blog makemigrations -m "Add post model with title and content"
```

## App Development

### Internal Apps

- Use internal apps for project-specific features
- Share models between internal apps when appropriate
- Keep apps loosely coupled

### External Apps

- Keep external apps truly independent
- Document dependencies clearly
- Test external apps in isolation
- Follow semantic versioning

## Security

### Secrets Management

- Never hardcode secrets
- Use environment variables for sensitive data
- Use secure secret management in production

### Input Validation

- Validate all inputs
- Use Pydantic models for request validation
- Sanitize user inputs

## Performance

### Database Queries

- Use proper indexing
- Avoid N+1 queries
- Use eager loading when appropriate

### Caching

- Cache expensive operations
- Use appropriate cache invalidation strategies

## Testing

### Test Organization

- Keep tests organized by app
- Use fixtures for common setup
- Test both unit and integration scenarios

### Migration Testing

- Test migrations in both directions
- Test with sample data
- Test edge cases

## Documentation

### Code Documentation

- Document public APIs
- Use type hints
- Write clear docstrings

### User Documentation

- Keep documentation up to date
- Provide examples
- Document edge cases

## Learn More

- [Creating Apps](../guides/creating-apps.md) - App development guide
- [Migrations](../guides/migrations.md) - Migration workflows
- [Configuration](../guides/configuration.md) - Configuration guide
