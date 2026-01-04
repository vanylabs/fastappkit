# Best Practices

Recommended patterns and practices for fastappkit projects.

## Project Organization

### App Design

1. **One app per feature/domain**
   -   Keep apps focused on a single responsibility
   -   Group related functionality together
   -   Use clear, descriptive names

2. **Clear boundaries**
   -   Keep app boundaries clear
   -   Minimize cross-app dependencies
   -   Use internal apps for tightly coupled features

3. **External apps for reusability**
   -   Design external apps to be reusable
   -   Keep dependencies minimal
   -   Document requirements clearly

## Migration Strategies

### Internal Apps

1. **Keep migrations focused**
   -   One migration per logical change
   -   Clear migration messages
   -   Review migrations before applying

2. **Use migration order when needed**
   -   Only if internal apps have dependencies
   -   Document dependencies clearly

3. **Test migrations**
   -   Test upgrades in development
   -   Test downgrades to ensure reversibility
   -   Review SQL with `fastappkit migrate preview`

### External Apps

1. **Version migrations**
   -   Include migrations in package
   -   Version migrations with app version
   -   Document migration requirements

2. **Test independently**
   -   Test migrations in external app project
   -   Test integration with core project
   -   Ensure compatibility

## Settings Management

1. **Use environment variables**
   -   Never hardcode sensitive values
   -   Use `.env` for development
   -   Use environment variables in production

2. **Validate settings**
   -   Use Pydantic validators
   -   Provide clear error messages
   -   Set appropriate defaults

3. **Document custom settings**
   -   Document all custom settings
   -   Explain purpose and usage
   -   Provide examples

## Testing Strategies

1. **Test apps independently**
   -   Test external apps in isolation
   -   Test internal apps with core
   -   Test integration

2. **Use validation**
   -   Run `fastappkit app validate` regularly
   -   Fix validation errors immediately
   -   Review warnings

3. **Test migrations**
   -   Test upgrades and downgrades
   -   Test in development first
   -   Backup before production migrations

## Performance Considerations

1. **Lazy loading**
   -   Apps are loaded on startup
   -   Minimize startup overhead
   -   Use async where appropriate

2. **Database connections**
   -   Use connection pooling
   -   Configure appropriately for your database
   -   Monitor connection usage

3. **Route organization**
   -   Keep routes organized
   -   Use appropriate prefixes
   -   Avoid deep nesting

## Security

1. **Settings security**
   -   Never commit `.env` files
   -   Use secure secret management
   -   Rotate secrets regularly

2. **Dependency management**
   -   Update dependency versions regularly
   -   Pin versions for production
   -   Review security advisories

3. **Input validation**
   -   Validate all inputs
   -   Use Pydantic models
   -   Sanitize user input

## Learn More

-   [Architecture](architecture.md) - Internal architecture
-   [Extending FastAppKit](extending-fastappkit.md) - Customization guide
