#!/usr/bin/env python3
import ast
import sys
from pathlib import Path

FORBIDDEN_CALLS = {"add", "commit", "delete", "execute", "flush", "rollback", "scalar", "scalars"}


def check_route_file(path: Path, root: Path) -> list[str]:
    failures = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    project_path = path.relative_to(root)
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            modules = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif node.module:
                modules = [node.module]
            for module in modules:
                if module == "sqlalchemy" or module.startswith("sqlalchemy."):
                    failures.append(f"{project_path}:{node.lineno} imports SQLAlchemy directly")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            if node.func.attr in FORBIDDEN_CALLS:
                failures.append(
                    f"{project_path}:{node.lineno} calls .{node.func.attr}(); route modules must delegate persistence"
                )
    return failures


def run(root: Path) -> list[str]:
    failures = []
    for path in sorted((root / "app" / "api" / "routes").glob("*.py")):
        failures.extend(check_route_file(path, root))
    return failures


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = run(root)
    if failures:
        print("Database boundary verification failed:\n", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("Database boundary verification passed (routes delegate persistence).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
