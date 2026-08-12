#!/usr/bin/env python3
import ast
import sys
from collections.abc import Iterable
from pathlib import Path

ALLOWED_METHODS = {"get", "post"}
KNOWN_METHODS = ALLOWED_METHODS | {"delete", "head", "options", "patch", "put", "trace"}


def route_files(root: Path) -> Iterable[Path]:
    return sorted((root / "app" / "api" / "routes").glob("*.py"))


def check_file(path: Path, root: Path) -> list[str]:
    failures = []
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Attribute):
                continue
            method = decorator.func.attr.lower()
            project_path = path.relative_to(root)
            if method in KNOWN_METHODS and method not in ALLOWED_METHODS:
                failures.append(f"{project_path}:{decorator.lineno} uses forbidden @{method} route")
            if method == "api_route":
                failures.extend(check_api_route_methods(decorator, project_path))
    return failures


def check_api_route_methods(decorator: ast.Call, project_path: Path) -> list[str]:
    failures = []
    methods_node = next((keyword.value for keyword in decorator.keywords if keyword.arg == "methods"), None)
    if methods_node is None:
        return [f"{project_path}:{decorator.lineno} uses api_route without explicit methods"]
    try:
        values = ast.literal_eval(methods_node)
    except (ValueError, TypeError):
        return [f"{project_path}:{decorator.lineno} has non-literal api_route methods"]
    methods = {str(value).lower() for value in values}
    forbidden = sorted(methods - ALLOWED_METHODS)
    if forbidden:
        failures.append(f"{project_path}:{decorator.lineno} uses forbidden methods: {', '.join(forbidden)}")
    return failures


def run(root: Path) -> list[str]:
    failures = []
    files = list(route_files(root))
    if not files:
        return ["no route modules found under app/api/routes"]
    for path in files:
        failures.extend(check_file(path, root))

    main_source = (root / "app" / "main.py").read_text(encoding="utf-8")
    if 'allow_methods=["GET", "POST"]' not in main_source:
        failures.append('app/main.py must constrain CORS allow_methods to ["GET", "POST"]')
    return failures


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = run(root)
    if failures:
        print("API policy verification failed:\n", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("API policy verification passed (GET/POST only).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
