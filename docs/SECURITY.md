# Security Policy

## Supported Versions

We actively support the following versions with security updates:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

We take security vulnerabilities seriously. If you discover a security vulnerability in fastappkit, please report it responsibly.

### How to Report

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via one of the following methods:

1. **Email**: desaiparth971@gmail.com
    - **Subject**: `[FASTAPPKIT SECURITY] <brief description>`
    - This special subject line helps us filter and prioritize security reports
2. **GitHub Security Advisory**: Use GitHub's [private vulnerability reporting](https://github.com/vanylabs/fastappkit/security/advisories/new)

### What to Include

When reporting a vulnerability, please include:

-   **Description** of the vulnerability
-   **Steps to reproduce** the issue
-   **Potential impact** (what could an attacker do?)
-   **Suggested fix** (if you have one)
-   **Affected versions**

### Response Timeline

We aim to:

-   **Acknowledge** your report within 48 hours
-   **Provide initial assessment** within 7 days
-   **Keep you informed** of progress and resolution timeline
-   **Release a fix** as soon as possible (typically within 30 days for critical issues)

### Disclosure Policy

-   We will coordinate with you on disclosure timing
-   We will credit you for the discovery (unless you prefer to remain anonymous)
-   We will not disclose your identity without your permission

## Security Considerations

fastappkit involves several security-sensitive areas:

### Template Rendering

-   **Jinja2 Templates**: fastappkit uses Jinja2 for template rendering
-   **Sandboxing**: Templates should not execute arbitrary code
-   **Input Validation**: All template variables are validated before rendering
-   **File System Access**: Templates only write to designated project directories

### File System Operations

-   **Path Validation**: All file paths are validated to prevent directory traversal attacks
-   **Project Root**: Operations are restricted to the project root directory
-   **Permission Checks**: File operations respect system permissions

### App Loading and Validation

-   **Code Execution**: App loading involves importing Python modules
-   **Isolation**: External apps are validated for isolation before loading
-   **Manifest Validation**: App manifests are validated to prevent malicious configurations
-   **Import Restrictions**: Apps cannot import arbitrary system modules

### Migration Execution

-   **SQL Injection**: Migration scripts are executed through Alembic, which uses parameterized queries
-   **Path Validation**: Migration paths are validated before execution
-   **Database Access**: Migrations only access the configured database

### Configuration Files

-   **TOML Parsing**: `fastappkit.toml` is parsed using `tomlkit` (safe parser)
-   **App Name Validation**: App names are validated to prevent injection
-   **Path Injection**: Configuration paths are sanitized

## Best Practices for Users

When using fastappkit:

1. **Keep fastappkit updated** to the latest version
2. **Review external apps** before installing them
3. **Validate app manifests** before adding apps to your project
4. **Use environment variables** for sensitive configuration (database URLs, API keys)
5. **Restrict file permissions** on your project directory
6. **Audit dependencies** regularly using `poetry audit` or `pip-audit`

## Security Updates

Security updates will be:

-   Released as **patch versions** (e.g., 0.1.0 → 0.1.1)
-   Documented in the [CHANGELOG.md](CHANGELOG.md)
-   Announced via GitHub releases
-   Tagged with the `security` label

## Known Security Issues

Currently, there are no known security vulnerabilities. If you discover one, please report it using the process above.

## Security Audit

We regularly:

-   Review dependencies for known vulnerabilities
-   Run static analysis tools (Bandit) on the codebase
-   Review security-sensitive code paths
-   Update dependencies to patch security issues

### Running Security Checks

You can run security checks locally:

```bash
# Check dependencies
poetry audit
# or
pip-audit

# Static analysis
pip install bandit
bandit -r fastappkit/
```

## Acknowledgments

We thank security researchers who responsibly disclose vulnerabilities. Contributors will be credited in:

-   The [CHANGELOG.md](CHANGELOG.md)
-   GitHub releases
-   Security advisories

---

**Thank you for helping keep fastappkit secure!**
