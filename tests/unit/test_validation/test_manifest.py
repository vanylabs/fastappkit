"""
Tests for ManifestValidator and ValidationResult.

Tests focus on:
- ValidationResult behavior (errors, warnings, validity)
- Manifest validation (required fields, format checks)
- Edge cases that would break if implementation changes
"""

from fastappkit.validation.manifest import ManifestValidator, ValidationResult


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_empty_result_is_valid(self) -> None:
        """Empty ValidationResult is valid."""
        result = ValidationResult()

        assert result.is_valid is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert bool(result) is True

    def test_result_with_errors_is_invalid(self) -> None:
        """ValidationResult with errors is invalid."""
        result = ValidationResult()
        result.add_error("Test error")

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert result.errors[0] == "Test error"
        assert bool(result) is False

    def test_result_with_warnings_stays_valid(self) -> None:
        """ValidationResult with only warnings is still valid."""
        result = ValidationResult()
        result.add_warning("Test warning")

        assert result.is_valid is True
        assert len(result.warnings) == 1
        assert result.warnings[0] == "Test warning"
        assert bool(result) is True


class TestManifestValidator:
    """Tests for ManifestValidator class."""

    def test_validate_valid_manifest_passes(self) -> None:
        """validate() passes for valid manifest."""
        validator = ManifestValidator()
        manifest = {
            "name": "test_app",
            "version": "1.0.0",
            "entrypoint": "test_app:register",
        }

        result = validator.validate(manifest, "test_app")

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_missing_required_fields(self) -> None:
        """validate() fails when required fields are missing."""
        validator = ManifestValidator()

        # Missing all fields
        result = validator.validate({}, "test_app")
        assert result.is_valid is False
        assert len(result.errors) == 3  # name, version, entrypoint
        assert any("name" in error.lower() for error in result.errors)
        assert any("version" in error.lower() for error in result.errors)
        assert any("entrypoint" in error.lower() for error in result.errors)

        # Missing one field
        result = validator.validate({"name": "test", "version": "1.0.0"}, "test_app")
        assert result.is_valid is False
        assert any("entrypoint" in error.lower() for error in result.errors)

    def test_validate_version_must_be_string(self) -> None:
        """validate() fails if version is not a string."""
        validator = ManifestValidator()
        manifest = {
            "name": "test_app",
            "version": 1.0,  # Not a string
            "entrypoint": "test_app:register",
        }

        result = validator.validate(manifest, "test_app")

        assert result.is_valid is False
        assert any(
            "version" in error.lower() and "string" in error.lower() for error in result.errors
        )

    def test_validate_version_format_warning(self) -> None:
        """validate() warns about potentially invalid version format."""
        validator = ManifestValidator()
        manifest = {
            "name": "test_app",
            "version": "invalid",  # No digits
            "entrypoint": "test_app:register",
        }

        result = validator.validate(manifest, "test_app")

        assert result.is_valid is True  # Warning doesn't fail validation
        assert len(result.warnings) > 0
        assert any("version" in warning.lower() for warning in result.warnings)

    def test_validate_entrypoint_must_be_string(self) -> None:
        """validate() fails if entrypoint is not a string."""
        validator = ManifestValidator()
        manifest = {
            "name": "test_app",
            "version": "1.0.0",
            "entrypoint": 123,  # Not a string
        }

        result = validator.validate(manifest, "test_app")

        assert result.is_valid is False
        assert any(
            "entrypoint" in error.lower() and "string" in error.lower() for error in result.errors
        )

    def test_validate_entrypoint_format(self) -> None:
        """validate() fails if entrypoint doesn't have ':' separator."""
        validator = ManifestValidator()
        manifest = {
            "name": "test_app",
            "version": "1.0.0",
            "entrypoint": "test_app.register",  # Missing ':'
        }

        result = validator.validate(manifest, "test_app")

        assert result.is_valid is False
        assert any(
            "entrypoint" in error.lower() and "format" in error.lower() for error in result.errors
        )

    def test_validate_unknown_keys_warning(self) -> None:
        """validate() warns about unknown manifest keys."""
        validator = ManifestValidator()
        manifest = {
            "name": "test_app",
            "version": "1.0.0",
            "entrypoint": "test_app:register",
            "unknown_key": "value",
            "another_unknown": 123,
        }

        result = validator.validate(manifest, "test_app")

        assert result.is_valid is True  # Warnings don't fail
        assert len(result.warnings) > 0
        assert any("unknown" in warning.lower() for warning in result.warnings)

    def test_validate_combines_errors_and_warnings(self) -> None:
        """validate() can return both errors and warnings."""
        validator = ManifestValidator()
        manifest = {
            "name": "test_app",
            "version": "invalid",  # Warning
            "entrypoint": "test_app.register",  # Error (missing ':')
            "unknown_key": "value",  # Warning
        }

        result = validator.validate(manifest, "test_app")

        assert result.is_valid is False  # Has errors
        assert len(result.errors) > 0
        assert len(result.warnings) > 0
