"""Deterministic runtime guard — ensures no forbidden runtime dependencies in src/."""

from __future__ import annotations

import ast
from pathlib import Path

SRC_ROOT = Path(__file__).resolve().parents[2] / "src"

# Forbidden runtime calls that break determinism
FORBIDDEN_CALLS = {
    "datetime.now",
    "datetime.utcnow",
    "time.time",
    "time.monotonic",
    "random.random",
    "random.randint",
    "random.choice",
    "uuid.uuid4",
    "uuid.uuid1",
}

FORBIDDEN_IMPORTS = {"rclpy", "rospy", "psycopg2", "pymongo", "sqlite3"}


def _collect_all_names(file_path: Path) -> tuple[list[str], list[str]]:
    """Collect imports and attribute calls from a Python file."""
    source = file_path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(file_path))
    imports: list[str] = []
    calls: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Attribute):
                if isinstance(node.value.value, ast.Name):
                    calls.append(f"{node.value.value.id}.{node.value.attr}.{node.attr}")
            elif isinstance(node.value, ast.Name):
                calls.append(f"{node.value.id}.{node.attr}")

    return imports, calls


class TestDeterministicRuntimeGuard:
    def test_no_forbidden_runtime_imports(self) -> None:
        """No src/ file imports forbidden runtime modules (adapters can import sqlite3)."""
        violations: list[str] = []
        for py_file in SRC_ROOT.rglob("*.py"):
            imports, _ = _collect_all_names(py_file)
            for imp in imports:
                top = imp.split(".")[0]
                if top in FORBIDDEN_IMPORTS:
                    # Exception: SQLite adapter is allowed to import sqlite3
                    if top == "sqlite3" and "adapters" in py_file.parts:
                        continue
                    violations.append(f"{py_file.relative_to(SRC_ROOT)}: {imp}")
        assert violations == [], "Forbidden runtime imports:\n" + "\n".join(violations)

    def test_no_nondeterministic_calls(self) -> None:
        """No src/ file uses non-deterministic function calls."""
        violations: list[str] = []
        for py_file in SRC_ROOT.rglob("*.py"):
            _, calls = _collect_all_names(py_file)
            for call in calls:
                if call in FORBIDDEN_CALLS:
                    violations.append(f"{py_file.relative_to(SRC_ROOT)}: {call}")
        assert violations == [], "Non-deterministic calls:\n" + "\n".join(violations)
