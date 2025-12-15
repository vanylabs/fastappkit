# CI/CD & Release Process

Quick reference for understanding CI workflows and release process.

---

## Branch Strategy

**Structure:**

```
main (production-ready)
  ↑
  └── feature/*, fix/*, docs/*, refactor/*
```

**Workflow:**

1. Create feature branch → Make changes → Create PR to `main`
2. CI runs automatically (tests, lint, type check)
3. Code review → Merge to `main`
4. Release: Bump version → Create changelog → Tag → Auto-publish to PyPI

---

## GitHub Actions Workflows

### 1. **CI Workflow** (`.github/workflows/ci.yml`)

**Triggers:**

-   `pull_request` (all branches)
-   `push` to `main`

**Jobs:**

1. **Test Matrix** (Python 3.11, 3.12 - tested versions)

    - Install Poetry & dependencies
    - Run tests with coverage
    - Upload coverage (optional)

2. **Lint** (single Python version)
    - Black (format check)
    - Ruff (linting)
    - mypy (type checking)

---

### 2. **Publish to PyPI** (`.github/workflows/publish.yml`)

**Trigger:** `push` with tag matching `v*.*.*` (e.g., `v0.1.0`)

**Process:**

1. Checkout code
2. Set up Python & Poetry
3. Install dependencies
4. Build package (`poetry build`)
5. Check package (`twine check`)
6. Publish to PyPI (Trusted Publishing - OIDC)

**Security:**

-   Uses PyPI Trusted Publishing (no API tokens)
-   Only runs on version tags

---

## Version Management

**Files to keep in sync:**

-   `pyproject.toml` - Updated via `poetry version`
-   `fastappkit/__init__.py` - Manual update to match
-   `docs/changelog/X.X.X.md` - Create new changelog file
-   `CHANGELOG.md` (repo root) - Add version to Version History
-   `mkdocs.yml` - Add version to Changelog navigation
-   `docs/community/index.md` - Add version to Changelog section

**Process:**

```bash
poetry version patch  # or minor/major
# Manually update fastappkit/__init__.py to match
# Create docs/changelog/X.X.X.md
# Update CHANGELOG.md (repo root)
# Update mkdocs.yml navigation
# Update docs/community/index.md
```

---

## Release Process

### Step-by-Step Checklist

1. **Ensure all changes merged to `main`**

    ```bash
    git checkout main
    git pull origin main
    ```

2. **Bump version**

    ```bash
    poetry version patch  # or minor/major
    ```

3. **Sync version in `fastappkit/__init__.py`**

    ```bash
    # Update __version__ = "0.1.1" to match pyproject.toml
    ```

4. **Create changelog entry**

    Create the changelog entry and update all references:

    a. **Create changelog file:**

    ```bash
    # Create docs/changelog/0.1.1.md with release notes
    # Follow the format from existing changelog files
    ```

    b. **Update `CHANGELOG.md` in repo root:**

    ```bash
    # Add new version to the Version History section at the top:
    # -   **[0.1.1](docs/changelog/0.1.1.md)** - Brief description
    ```

    c. **Update `mkdocs.yml` navigation:**

    ```bash
    # Add to Changelog section in nav (place newest version first):
    # - Version 0.1.1: changelog/0.1.1.md
    ```

    d. **Update `docs/community/index.md`:**

    ```bash
    # Add to the Changelog section (place newest version first):
    # -   [Version 0.1.1](changelog/0.1.1.md) - Brief description
    ```

5. **Commit changes**

    ```bash
    git add pyproject.toml fastappkit/__init__.py \
            docs/changelog/ CHANGELOG.md mkdocs.yml docs/community/index.md
    git commit -m "chore: prepare release v0.1.1"
    ```

6. **Create and push tag**

    ```bash
    git tag -a v0.1.1 -m "Release v0.1.1"
    git push origin main --tags
    ```

7. **GitHub Action automatically:**
    - Detects tag
    - Builds package
    - Publishes to PyPI

---

## Workflow Triggers

| Workflow    | Trigger             | When          |
| ----------- | ------------------- | ------------- |
| **CI**      | `pull_request`      | Every PR      |
| **CI**      | `push` to `main`    | After merge   |
| **Publish** | `push` tag `v*.*.*` | After tagging |

---

## Security

-   **PyPI Publishing:** Trusted Publishing (OIDC) - no tokens stored
-   **Branch Protection:** Require PR reviews, CI must pass before merge
-   **Secrets:** No secrets needed (Trusted Publishing handles auth)

---

## PyPI Setup (One-Time)

Set up PyPI Trusted Publishing to enable automatic publishing from GitHub Actions:

1. **Go to:** https://pypi.org/manage/account/publishing/
2. **Click:** "Add a new pending publisher"
3. **Fill in:**
    - PyPI project name: `fastappkit`
    - Owner: `vanylabs`
    - Repository name: `fastappkit`
    - Workflow filename: `publish.yml`
    - Environment name: `pypi`
4. **Click:** "Add"

**Optional:** Create GitHub environment `pypi` in Settings → Environments (auto-created if skipped).

**Done!** The workflow is already configured. First publish activates the pending publisher.

---

## Key Decisions

-   **Branch Strategy:** Feature branches → `main` (no `develop` branch)
-   **Version Bumping:** Manual (`poetry version`)
-   **Changelog:** Maintainer creates entries manually
-   **Release Frequency:** Flexible (patch: weekly/bi-weekly, minor: monthly, major: as needed)

---

**Workflow Files:**

-   `.github/workflows/ci.yml` - Required
-   `.github/workflows/publish.yml` - Required
