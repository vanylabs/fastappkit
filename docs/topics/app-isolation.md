# App Isolation

fastappkit enforces isolation rules to ensure apps don't conflict with each other and maintain clear boundaries.

## Isolation Rules

```
┌──────────────┐    cannot depend    ┌──────────────┐
│ Internal App │ ───────────────────>│ External App │
└──────────────┘                     └──────────────┘
       ▲                                     │
       │ can depend                          │ cannot touch
       │                                     ▼
┌──────────────┐                     ┌──────────────┐
│    Core      │     cannot touch    │ Internal App │
└──────────────┘                     └──────────────┘
```

## Internal Apps

**Allowed:**

- Can depend on other internal apps
- Can modify shared tables
- Participate in shared migration timeline (use core's migration directory)
- No manifest file required (metadata inferred from structure)

**Restricted:**

- Cannot depend on external apps

## External Apps

**Allowed:**

- Independent schema evolution (isolated migrations)
- Can be published to PyPI
- Must be pip-installed (no filesystem path support)
- Must have `fastappkit.toml` manifest in package directory

**Restricted:**

- Cannot depend on internal apps
- Cannot touch other apps' tables
- Cannot modify core or internal tables
- Cannot create migrations from core project (must use Alembic directly)

## Validation

fastappkit validates isolation rules when:

- Loading apps at startup
- Running `fastappkit app validate <name>`

### Isolation Checks

The isolation validator checks:

1. **Import Analysis:** Scans Python files for imports
2. **Dependency Detection:** Identifies imports from other apps
3. **Rule Enforcement:** Validates against isolation rules
4. **Error Reporting:** Provides clear error messages for violations

### Example Violation

If an external app tries to import from an internal app:

```python
# external_app/models.py
from apps.blog.models import Post  # Violation: External apps cannot import internal apps

class Comment(Base):
    post_id = Column(Integer, ForeignKey("posts.id"))
```

Validation will fail with:

```
Isolation violation: External app 'external_app' cannot import from internal app 'apps.blog'
```

## Best Practices

1. Keep external apps truly independent
2. Use well-defined interfaces for cross-app communication
3. Validate apps before deploying
4. Document dependencies clearly

## Learn More

- [Internal Apps](internal-apps.md) - Internal app constraints
- [External Apps](external-apps.md) - External app constraints
- [Creating Apps](../guides/creating-apps.md) - App creation guide
