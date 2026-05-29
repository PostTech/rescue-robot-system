"""TC-MOD-009/011: Adapter module boundary tests."""

from __future__ import annotations

import ast
from pathlib import Path

ADAPTERS_ROOT = Path(__file__).resolve().parents[2] / "src" / "adapters"


class TestAdapterModuleBoundaries:
    def test_tc_mod_009_no_ui_imports(self) -> None:
        """TC-MOD-009: Adapters do not import UI modules."""
        violations: list[str] = []
        for py_file in ADAPTERS_ROOT.rglob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith("ui"):
                        violations.append(f"{py_file.name}: {node.module}")
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith("ui"):
                            violations.append(f"{py_file.name}: {alias.name}")
        assert violations == [], f"Adapter imports UI: {violations}"

    def test_tc_mod_011_no_rclpy_import(self) -> None:
        """TC-MOD-011: Adapters do not import rclpy in dev profile."""
        violations: list[str] = []
        for py_file in ADAPTERS_ROOT.rglob("*.py"):
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "rclpy":
                            violations.append(f"{py_file.name}: rclpy")
                elif isinstance(node, ast.ImportFrom) and node.module:
                    if node.module.startswith("rclpy"):
                        violations.append(f"{py_file.name}: {node.module}")
        assert violations == [], f"Adapter imports rclpy: {violations}"
