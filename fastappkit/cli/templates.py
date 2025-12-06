"""
Template system for code generation using Jinja2.

Handles template discovery, loading, and rendering for project/app scaffolding.
"""

from __future__ import annotations

import fnmatch
import os
from importlib import resources
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound


class TemplateEngine:
    """Jinja2-based template engine for code generation."""

    def __init__(self, template_dirs: list[Path] | None = None):
        """
        Initialize template engine.

        Args:
            template_dirs: List of directories to search for templates.
                          If None, uses default template directory from package.
        """
        if template_dirs is None:
            # Try to find templates in the installed package
            try:
                # Use importlib.resources to find templates in installed package
                # templates is a directory, so we access it via the cli package
                cli_package = resources.files("fastappkit.cli")
                templates_dir = cli_package / "templates"
                if templates_dir.is_dir():
                    # Extract the actual filesystem path
                    default_dir = Path(str(templates_dir))
                    if default_dir.exists():
                        template_dirs = [default_dir]
                    else:
                        raise FileNotFoundError("Template directory not found")
                else:
                    raise FileNotFoundError("Templates directory not found in package")
            except (ModuleNotFoundError, AttributeError, TypeError, FileNotFoundError):
                # Fallback: try relative to __file__ (for development)
                default_dir = Path(__file__).parent / "templates"
                if default_dir.exists():
                    template_dirs = [default_dir]
                else:
                    # Last resort: try parent structure
                    package_dir = Path(__file__).parent.parent.parent
                    default_dir = package_dir / "cli" / "templates"
                    template_dirs = [default_dir]

        # Ensure all template dirs exist
        self.template_dirs = [Path(d) for d in template_dirs if Path(d).exists()]

        if not self.template_dirs:
            # Try one more fallback: check if we're in development mode
            dev_template_dir = Path(__file__).parent / "templates"
            if dev_template_dir.exists():
                self.template_dirs = [dev_template_dir]
            else:
                raise ValueError(
                    f"No valid template directories found. Tried: {template_dirs}. "
                    "Make sure fastappkit is properly installed with templates."
                )

        # Create Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader([str(d) for d in self.template_dirs]),
            autoescape=False,  # We're generating code, not HTML
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def get_template(self, template_path: str) -> Template:
        """
        Get a template by path.

        Args:
            template_path: Path to template relative to template directories

        Returns:
            Jinja2 Template object

        Raises:
            TemplateNotFound: If template doesn't exist
        """
        try:
            return self.env.get_template(template_path)
        except TemplateNotFound as e:
            raise TemplateNotFound(
                f"Template '{template_path}' not found in: {[str(d) for d in self.template_dirs]}"
            ) from e

    def render(self, template_path: str, context: dict[str, Any]) -> str:
        """
        Render a template with context.

        Args:
            template_path: Path to template relative to template directories
            context: Dictionary of variables to pass to template

        Returns:
            Rendered template as string
        """
        template = self.get_template(template_path)
        return template.render(**context)

    def render_to_file(
        self,
        template_path: str,
        output_path: Path,
        context: dict[str, Any],
        overwrite: bool = False,
    ) -> None:
        """
        Render a template and write to file.

        Args:
            template_path: Path to template relative to template directories
            output_path: Path where rendered content should be written
            context: Dictionary of variables to pass to template
            overwrite: If False, raises error if file exists

        Raises:
            FileExistsError: If file exists and overwrite=False
        """
        output_path = Path(output_path)

        if output_path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {output_path}")

        # Create parent directories if needed
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Render and write
        content = self.render(template_path, context)
        output_path.write_text(content, encoding="utf-8")

    def list_templates(self, pattern: str | None = None) -> list[str]:
        """
        List available templates.

        Args:
            pattern: Optional glob pattern to filter templates

        Returns:
            List of template paths
        """
        templates = []
        for template_dir in self.template_dirs:
            for root, dirs, files in os.walk(template_dir):
                root_path = Path(root)
                rel_root = root_path.relative_to(template_dir)

                for file in files:
                    if file.endswith((".j2", ".jinja2", ".jinja")):
                        template_path = rel_root / file
                        templates.append(str(template_path))

        if pattern:
            # Simple pattern matching (can be enhanced)
            templates = [t for t in templates if fnmatch.fnmatch(t, pattern)]

        return sorted(templates)


# Global template engine instance
_template_engine: TemplateEngine | None = None


def get_template_engine() -> TemplateEngine:
    """Get the global template engine instance."""
    global _template_engine
    if _template_engine is None:
        _template_engine = TemplateEngine()
    return _template_engine


def set_template_engine(engine: TemplateEngine) -> None:
    """Set the global template engine instance."""
    global _template_engine
    _template_engine = engine


def render_template(template_path: str, context: dict[str, Any]) -> str:
    """Convenience function to render a template."""
    return get_template_engine().render(template_path, context)


def render_template_to_file(
    template_path: str,
    output_path: Path,
    context: dict[str, Any],
    overwrite: bool = False,
) -> None:
    """Convenience function to render template to file."""
    get_template_engine().render_to_file(template_path, output_path, context, overwrite)
