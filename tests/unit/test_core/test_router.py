"""
Tests for RouterAssembler.

Tests focus on:
- Mounting routers with correct prefixes
- Handling apps that mount routers themselves
- Route collision detection
- Error handling during router mounting
"""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import APIRouter, FastAPI

from fastappkit.core.registry import AppMetadata, AppRegistry
from fastappkit.core.router import RouterAssembler
from fastappkit.core.types import AppType
from fastappkit.exceptions import AppLoadError


class TestRouterAssembler:
    """Tests for RouterAssembler class."""

    def test_assemble_mounts_router_with_prefix(self) -> None:
        """assemble() mounts router with correct prefix."""
        app = FastAPI()
        registry = AppRegistry()

        router = APIRouter()

        @router.get("/hello")
        def hello() -> dict[str, str]:
            return {"message": "hello"}

        metadata = AppMetadata(
            name="blog",
            app_type=AppType.INTERNAL,
            import_path="apps.blog",
            router=router,
            prefix="/blog",
        )

        registry.register(metadata)

        assembler = RouterAssembler()
        assembler.assemble(app, registry)

        # Check that router was mounted
        routes = [r for r in app.routes if hasattr(r, "path")]
        paths = [r.path for r in routes]
        assert any("/blog/hello" in path or path == "/blog/hello" for path in paths)

    def test_assemble_handles_empty_prefix(self) -> None:
        """assemble() handles apps with empty prefix."""
        app = FastAPI()
        registry = AppRegistry()

        router = APIRouter()

        @router.get("/root")
        def root() -> dict[str, str]:
            return {"message": "root"}

        metadata = AppMetadata(
            name="root_app",
            app_type=AppType.INTERNAL,
            import_path="apps.root_app",
            router=router,
            prefix="",  # Empty prefix
        )

        registry.register(metadata)

        assembler = RouterAssembler()
        assembler.assemble(app, registry)

        # Should mount at root
        routes = [r for r in app.routes if hasattr(r, "path")]
        paths = [r.path for r in routes]
        assert any("/root" in path or path == "/root" for path in paths)

    def test_assemble_mounts_multiple_apps(self) -> None:
        """assemble() mounts routers from multiple apps."""
        app = FastAPI()
        registry = AppRegistry()

        router1 = APIRouter()

        @router1.get("/posts")
        def posts() -> dict[str, list[dict[str, str]]]:
            return {"posts": []}

        router2 = APIRouter()

        @router2.get("/products")
        def products() -> dict[str, list[dict[str, str]]]:
            return {"products": []}

        metadata1 = AppMetadata(
            name="blog",
            app_type=AppType.INTERNAL,
            import_path="apps.blog",
            router=router1,
            prefix="/blog",
        )

        metadata2 = AppMetadata(
            name="shop",
            app_type=AppType.INTERNAL,
            import_path="apps.shop",
            router=router2,
            prefix="/shop",
        )

        registry.register(metadata1)
        registry.register(metadata2)

        assembler = RouterAssembler()
        assembler.assemble(app, registry)

        # Both routers should be mounted
        routes = [r for r in app.routes if hasattr(r, "path")]
        paths = [r.path for r in routes]
        assert any("/blog" in path for path in paths)
        assert any("/shop" in path for path in paths)

    def test_assemble_raises_error_on_mount_failure(self) -> None:
        """assemble() raises AppLoadError if router mounting fails."""
        app = FastAPI()
        registry = AppRegistry()

        # Create a router that will cause an error when mounted
        router = APIRouter()

        metadata = AppMetadata(
            name="blog",
            app_type=AppType.INTERNAL,
            import_path="apps.blog",
            router=router,
            prefix="/blog",
        )

        registry.register(metadata)

        assembler = RouterAssembler()

        # Mock app.include_router to raise an error
        with patch.object(app, "include_router", side_effect=Exception("Mount failed")):
            with pytest.raises(AppLoadError) as exc_info:
                assembler.assemble(app, registry)

            assert exc_info.value.stage == "router"
            assert "blog" in str(exc_info.value)

    @patch("fastappkit.core.router.RouteCollisionDetector")
    def test_assemble_checks_for_collisions(self, mock_detector_class: MagicMock) -> None:
        """assemble() checks for route collisions after mounting."""
        app = FastAPI()
        registry = AppRegistry()

        router = APIRouter()

        @router.get("/hello")
        def hello() -> dict[str, str]:
            return {"message": "hello"}

        metadata = AppMetadata(
            name="blog",
            app_type=AppType.INTERNAL,
            import_path="apps.blog",
            router=router,
            prefix="/blog",
        )

        registry.register(metadata)

        mock_detector = MagicMock()
        mock_detector_class.return_value = mock_detector

        assembler = RouterAssembler()
        assembler.assemble(app, registry)

        # Verify collision detector was called
        mock_detector.check_and_warn.assert_called_once_with(app, registry, warn=True)
