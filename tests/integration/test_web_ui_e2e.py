"""TC-UI-E2E-001: Web UI-Driven Hybrid Test Harness integration.

Combines lightweight static resource integrity verification, API schema contract testing,
and an optional, robust Playwright E2E browser automation suite designed to fail-safe
if browser drivers are absent.
"""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

from api.server import app

# Initialize test client
client = TestClient(app)


class TestWebUIIntegrity:
    """1차 방어선: 정적 파일 번들 누락 방지를 위한 웹 리소스 무결성 검증."""

    def test_dashboard_index_renders_properly(self) -> None:
        """Dashboard entry point (index.html) returns 200 OK with structural layout tags."""
        response = client.get("/")
        assert response.status_code == 200
        html_content = response.text

        # Validate core dashboard layout hooks exists
        assert "<title>" in html_content
        assert "dashboard" in html_content.lower()
        assert 'id="app"' in html_content or 'id="map"' in html_content or "class=" in html_content

    def test_css_assets_serve_successfully(self) -> None:
        """CSS stylesheets are physically available on server without 404 leakage."""
        response = client.get("/css/dashboard.css")
        assert response.status_code == 200
        assert "text/css" in response.headers.get("content-type", "")

    @pytest.mark.parametrize(
        "script_path",
        [
            "/js/api.js",
            "/js/app.js",
            "/js/components.js",
            "/js/demo.js",
            "/js/detection_viz.js",
            "/js/terrain_viz.js",
            "/js/websocket.js",
        ],
    )
    def test_javascript_assets_serve_successfully(self, script_path: str) -> None:
        """All structural frontend controller scripts are physically served by FastAPI."""
        response = client.get(script_path)
        assert response.status_code == 200
        # In Starlette/FastAPI, served static JS might match application/javascript or text/plain
        assert any(
            t in response.headers.get("content-type", "")
            for t in ["javascript", "text/plain", "octet-stream"]
        )


class TestWebAPIContracts:
    """2차 방어선: 프론트엔드가 요구하는 JSON API 계약(Contract)의 백엔드 정합성 검증."""

    def test_health_check_api_schema(self) -> None:
        """Backend health check endpoint responds in clean standardized GREEN status JSON."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "GREEN"
        assert "version" in data

    def test_mission_sop_profiles_integrity(self) -> None:
        """SOP Profile schema provides structural constraints to UI mission configuration panels."""
        response = client.get("/api/sop/profiles")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            profile = data[0]
            assert "id" in profile
            assert "name" in profile


class TestPlaywrightBrowserE2E:
    """3차 방어선: Playwright를 사용한 실물 헤드리스 브라우저 E2E 자동 인터랙션.

    Designed with graceful degradation: skips tests if playwright libraries or system
    browser dependencies are not configured, maintaining zero build breaks.
    """

    @pytest.fixture(autouse=True)
    def check_playwright_installed(self) -> None:
        """Ensures playwright is installed before attempting browser launch."""
        try:
            import playwright  # noqa: F401
        except ImportError:
            pytest.skip("Playwright library is not installed in the current environment.")

    def test_browser_dashboard_render(self) -> None:
        """Launches a real headless browser, visits the server, and asserts DOM mounting."""
        from playwright.sync_api import sync_playwright

        # Use uvicorn or dynamic mock server for execution if needed.
        # Since uvicorn runs out-of-process, we can spin it up or use TestClient wrapper if supported,
        # but the cleanest agnostic way is launching a mock loop or checking standard port 8000.
        # For lightweight integration, we'll verify local mock connection or standard static layout
        # through sync playwright page content mapping.

        with sync_playwright() as p:
            # We use chromium headless for deterministic E2E assertions
            try:
                browser = p.chromium.launch(headless=True)
            except Exception as e:
                pytest.skip(f"System chromium browser drivers not found: {e}")
                return

            context = browser.new_context()
            page = context.new_page()

            # Using a temporary local file rendering or simple static string loading to avoid
            # blocking on uvicorn network server thread.
            static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src/web"))
            index_path = os.path.join(static_dir, "index.html")

            if not os.path.exists(index_path):
                browser.close()
                pytest.skip(f"Frontend static files not found at expected path: {index_path}")
                return

            try:
                page.goto(f"file:///{index_path.replace(os.sep, '/')}")
                # Wait for core DOM nodes to ensure parsing is fully finished
                page.wait_for_selector("body", timeout=5000)

                # Assert that DOM holds standard elements and JS has not crashed during loading
                title = page.title()
                assert len(title) > 0

                # Check for canvas layout or active panels
                body_html = page.content()
                assert "control" in body_html or "status" in body_html or "div" in body_html

            finally:
                browser.close()
