"""
Tests for ManifestLoader.

Tests focus on:
- Loading manifests for internal vs external apps
- Manifest validation
- Error handling for missing/invalid manifests
- Edge cases that would break if implementation changes
"""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from fastappkit.core.manifest import ManifestLoader
from fastappkit.core.resolver import AppInfo
from fastappkit.core.types import AppType
from fastappkit.exceptions import AppLoadError


class TestManifestLoader:
    """Tests for ManifestLoader class."""

    def test_load_manifest_for_internal_app_returns_inferred(self, temp_project: Path) -> None:
        """load_manifest() for internal app returns inferred manifest."""
        from tests.fixtures import InternalAppFactory

        app_path = InternalAppFactory.create_minimal(temp_project, "blog")

        app_info = AppInfo(
            name="blog",
            entry="apps.blog",
            app_type=AppType.INTERNAL,
            import_path="apps.blog",
            filesystem_path=app_path,
        )

        loader = ManifestLoader()
        manifest = loader.load_manifest(app_info)

        assert manifest["name"] == "blog"
        assert manifest["version"] == "0.1.0"
        assert manifest["entrypoint"] == "apps.blog:register"

    def test_load_manifest_for_external_app_loads_from_fastappkit_toml(
        self, temp_project: Path
    ) -> None:
        """load_manifest() for external app loads from fastappkit.toml."""
        from tests.fixtures import ExternalAppFactory

        package_path = ExternalAppFactory.create(
            temp_project.parent, "external_blog", with_migrations=False
        )

        app_info = AppInfo(
            name="external_blog",
            entry="external_blog",
            app_type=AppType.EXTERNAL,
            import_path="external_blog",
            filesystem_path=package_path,
        )

        loader = ManifestLoader()
        manifest = loader.load_manifest(app_info)

        assert manifest["name"] == "external_blog"
        assert manifest["version"] == "0.1.0"
        assert manifest["entrypoint"] == "external_blog:register"

    def test_load_manifest_for_external_app_without_toml_raises_error(
        self, temp_project: Path
    ) -> None:
        """load_manifest() raises error if external app has no fastappkit.toml."""
        # Create package directory without fastappkit.toml
        package_path = temp_project.parent / "external_app"
        package_path.mkdir()
        (package_path / "__init__.py").write_text('"""External app."""')

        app_info = AppInfo(
            name="external_app",
            entry="external_app",
            app_type=AppType.EXTERNAL,
            import_path="external_app",
            filesystem_path=package_path,
        )

        loader = ManifestLoader()

        with pytest.raises(AppLoadError) as exc_info:
            loader.load_manifest(app_info)

        assert exc_info.value.stage == "manifest"
        assert "fastappkit.toml not found" in str(exc_info.value)

    def test_load_manifest_validates_required_fields(self, temp_project: Path) -> None:
        """load_manifest() validates required fields in manifest."""
        from tests.fixtures import ExternalAppFactory

        package_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=False
        )

        # Create invalid manifest (missing required fields)
        toml_content = """[tool.fastappkit]
# Missing name, version, entrypoint
"""
        (package_path / "fastappkit.toml").write_text(toml_content)

        app_info = AppInfo(
            name="external_app",
            entry="external_app",
            app_type=AppType.EXTERNAL,
            import_path="external_app",
            filesystem_path=package_path,
        )

        loader = ManifestLoader()

        # ValidationError is wrapped in AppLoadError
        with pytest.raises(AppLoadError) as exc_info:
            loader.load_manifest(app_info)

        # Check error message contains validation error
        assert "Missing required field" in str(exc_info.value)
        assert exc_info.value.stage == "manifest"

    def test_load_manifest_validates_version_format(self, temp_project: Path) -> None:
        """load_manifest() validates version format."""
        from tests.fixtures import ExternalAppFactory

        package_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=False
        )

        # Create manifest with invalid version
        toml_content = """[tool.fastappkit]
name = "external_app"
version = "invalid"
entrypoint = "external_app:register"
"""
        (package_path / "fastappkit.toml").write_text(toml_content)

        app_info = AppInfo(
            name="external_app",
            entry="external_app",
            app_type=AppType.EXTERNAL,
            import_path="external_app",
            filesystem_path=package_path,
        )

        loader = ManifestLoader()

        # ValidationError is wrapped in AppLoadError
        with pytest.raises(AppLoadError) as exc_info:
            loader.load_manifest(app_info)

        assert "Invalid version format" in str(exc_info.value)

    def test_load_manifest_validates_entrypoint_format(self, temp_project: Path) -> None:
        """load_manifest() validates entrypoint format."""
        from tests.fixtures import ExternalAppFactory

        package_path = ExternalAppFactory.create(
            temp_project.parent, "external_app", with_migrations=False
        )

        # Create manifest with invalid entrypoint
        toml_content = """[tool.fastappkit]
name = "external_app"
version = "1.0.0"
entrypoint = "invalid_format"
"""
        (package_path / "fastappkit.toml").write_text(toml_content)

        app_info = AppInfo(
            name="external_app",
            entry="external_app",
            app_type=AppType.EXTERNAL,
            import_path="external_app",
            filesystem_path=package_path,
        )

        loader = ManifestLoader()

        # ValidationError is wrapped in AppLoadError
        with pytest.raises(AppLoadError) as exc_info:
            loader.load_manifest(app_info)

        assert "Invalid entrypoint format" in str(exc_info.value)

    def test_load_manifest_for_pip_installed_app(self, temp_project: Path) -> None:
        """load_manifest() can load manifest for pip-installed app via module location."""
        import tempfile

        # Create a temporary package structure that simulates pip-installed package
        with tempfile.TemporaryDirectory() as tmpdir:
            package_dir = Path(tmpdir) / "external_app"
            package_dir.mkdir()

            # Create __init__.py
            (package_dir / "__init__.py").write_text('"""External app."""')

            # Create fastappkit.toml
            toml_path = package_dir / "fastappkit.toml"
            toml_path.write_text(
                """[tool.fastappkit]
name = "external_app"
version = "1.0.0"
entrypoint = "external_app:register"
"""
            )

            app_info = AppInfo(
                name="external_app",
                entry="external_app",
                app_type=AppType.EXTERNAL,
                import_path="external_app",
                filesystem_path=None,  # No filesystem path (pip-installed)
            )

            loader = ManifestLoader()

            # Mock import_module to return module with __file__ pointing to our temp package
            with patch("fastappkit.core.manifest.importlib.import_module") as mock_import:
                mock_module = MagicMock()
                mock_module.__file__ = str(package_dir / "__init__.py")
                mock_import.return_value = mock_module

                manifest = loader.load_manifest(app_info)

                assert manifest["name"] == "external_app"
                assert manifest["version"] == "1.0.0"
