"""TC-DEP-001/002/003/005/006: Dependency direction enforcement tests.

Scans all source files to verify the strict layering rule:
    Types -> Config -> Service -> UI

No reverse imports are allowed.
"""

from __future__ import annotations

import ast
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"


def _collect_imports(file_path: Path) -> list[str]:
    """Extract all import module names from a Python file."""
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports


def _get_python_files(package_dir: Path) -> list[Path]:
    """Recursively collect all .py files in a package directory."""
    if not package_dir.exists():
        return []
    return list(package_dir.rglob("*.py"))


# ---------------------------------------------------------------------------
# TC-DEP-001: Types 독립성
# ---------------------------------------------------------------------------


class TestTypesDependency:
    """Types 계층은 Config/Service/UI/Adapter를 import하지 않는다."""

    FORBIDDEN = {"config", "service", "ui", "adapters", "rclpy", "rospy", "webrtc"}

    def test_no_forbidden_imports(self) -> None:
        types_dir = SRC_ROOT / "domain_types"
        violations: list[str] = []
        for py_file in _get_python_files(types_dir):
            for imp in _collect_imports(py_file):
                top_module = imp.split(".")[0]
                if top_module in self.FORBIDDEN:
                    violations.append(f"{py_file.name}: {imp}")
        assert violations == [], "TC-DEP-001 FAIL — forbidden imports in Types:\n" + "\n".join(
            violations
        )


# ---------------------------------------------------------------------------
# TC-DEP-002: Config 독립성
# ---------------------------------------------------------------------------


class TestConfigDependency:
    """Config 계층은 Service/UI를 import하지 않는다."""

    FORBIDDEN = {"service", "ui", "rclpy", "rospy"}

    def test_no_forbidden_imports(self) -> None:
        config_dir = SRC_ROOT / "config"
        violations: list[str] = []
        for py_file in _get_python_files(config_dir):
            for imp in _collect_imports(py_file):
                top_module = imp.split(".")[0]
                if top_module in self.FORBIDDEN:
                    violations.append(f"{py_file.name}: {imp}")
        assert violations == [], "TC-DEP-002 FAIL — forbidden imports in Config:\n" + "\n".join(
            violations
        )


# ---------------------------------------------------------------------------
# TC-DEP-003: Service 독립성
# ---------------------------------------------------------------------------


class TestServiceDependency:
    """Service 계층은 UI를 import하지 않는다."""

    FORBIDDEN = {"ui"}

    def test_no_forbidden_imports(self) -> None:
        service_dir = SRC_ROOT / "service"
        violations: list[str] = []
        for py_file in _get_python_files(service_dir):
            for imp in _collect_imports(py_file):
                top_module = imp.split(".")[0]
                if top_module in self.FORBIDDEN:
                    violations.append(f"{py_file.name}: {imp}")
        # Also check for "../ui/" pattern in raw source
        for py_file in _get_python_files(service_dir):
            content = py_file.read_text(encoding="utf-8")
            if "../ui/" in content or "from ui" in content:
                violations.append(f"{py_file.name}: contains '../ui/' or 'from ui' pattern")
        assert violations == [], "TC-DEP-003 FAIL — forbidden imports in Service:\n" + "\n".join(
            violations
        )


# ---------------------------------------------------------------------------
# TC-DEP-005: 순환 의존성 차단
# ---------------------------------------------------------------------------


class TestNoCyclicDependency:
    """Types, Config, Service, UI 간 순환 의존 없음."""

    # Layer order: lower index = lower layer (cannot import higher)
    LAYERS = {
        "domain_types": 0,
        "config": 1,
        "service": 2,
        "ui": 3,
    }

    def test_no_reverse_imports(self) -> None:
        violations: list[str] = []
        for layer_name, layer_level in self.LAYERS.items():
            layer_dir = SRC_ROOT / layer_name
            for py_file in _get_python_files(layer_dir):
                for imp in _collect_imports(py_file):
                    top_module = imp.split(".")[0]
                    if top_module in self.LAYERS:
                        imported_level = self.LAYERS[top_module]
                        if imported_level > layer_level:
                            violations.append(
                                f"{layer_name}/{py_file.name} imports {top_module} "
                                f"(level {layer_level} -> {imported_level})"
                            )
        assert violations == [], "TC-DEP-005 FAIL — reverse imports:\n" + "\n".join(violations)
