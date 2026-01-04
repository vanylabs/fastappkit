# Usage Scenarios

fastappkit supports different development approaches depending on your needs. This guide helps you choose the right path.

## Three Main Scenarios

### 1. Scaffolding Only

Just generate project structure without using fastappkit's app system.

**Use when:**
-   You want a clean FastAPI project structure
-   You prefer manual organization
-   You don't need the app system features

**What you get:**
-   Project structure (`core/`, `apps/`, etc.)
-   Settings system
-   Migration setup
-   Manual control over everything

[→ Go to Scaffolding Only Guide](scaffolding-only.md)

### 2. Scaffolding + Internal Apps

Build a project with internal apps (like Django apps).

**Use when:**
-   You're building a single project
-   You want modular organization within the project
-   You need shared migrations across features
-   You want to organize code into logical components

**What you get:**
-   Everything from Scaffolding Only
-   Internal apps system
-   Shared migration management
-   Automatic router mounting

[→ Go to Internal Apps Guide](internal-apps.md)

### 3. Scaffolding + Internal + External Apps

Full ecosystem with both internal and external (pluggable) apps.

**Use when:**
-   You're building reusable components
-   You want to share apps across projects
-   You need isolated migrations for plugins
-   You're building a plugin ecosystem

**What you get:**
-   Everything from Internal Apps
-   External apps (pip-installable packages)
-   Isolated migrations per external app
-   Plugin architecture

[→ Go to Full Ecosystem Guide](full-ecosystem.md)

## Quick Comparison

| Feature | Scaffolding Only | Internal Apps | Full Ecosystem |
|---------|------------------|---------------|----------------|
| **Project Structure** | ✅ | ✅ | ✅ |
| **Internal Apps** | ❌ | ✅ | ✅ |
| **External Apps** | ❌ | ❌ | ✅ |
| **Shared Migrations** | ✅ (core only) | ✅ (core + internal) | ✅ (core + internal) |
| **Isolated Migrations** | ❌ | ❌ | ✅ (external apps) |
| **CLI Commands** | Limited | Full | Full |
| **App Validation** | ❌ | ✅ | ✅ |
| **Plugin Architecture** | ❌ | ❌ | ✅ |

## Decision Tree

```
Do you need reusable components?
│
├─ No → Do you want modular organization?
│        │
│        ├─ No → Use Scaffolding Only
│        │
│        └─ Yes → Use Internal Apps
│
└─ Yes → Use Full Ecosystem
```

## Common Questions

**Q: Can I start with Scaffolding Only and add apps later?**
A: Yes! You can always add internal apps later. External apps require pip installation, so plan accordingly.

**Q: Can I mix internal and external apps?**
A: Yes, that's the Full Ecosystem scenario. Internal apps for project-specific features, external apps for reusable components.

**Q: Do I need to use all features?**
A: No. Use only what you need. Start simple and add complexity as required.

## Next Steps

Choose your scenario and follow the detailed guide:

-   [Scaffolding Only](scaffolding-only.md) - Just project structure
-   [Internal Apps](internal-apps.md) - Build with internal apps
-   [Full Ecosystem](full-ecosystem.md) - Internal + external apps
