#!/usr/bin/env python3
import ast
import sys
from pathlib import Path
from typing import Any

RevisionValue = tuple[str, ...] | None


def assignment_value(tree: ast.AST, name: str) -> Any:
    for node in getattr(tree, "body", []):
        if isinstance(node, ast.Assign):
            if any(isinstance(target, ast.Name) and target.id == name for target in node.targets):
                return ast.literal_eval(node.value)
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == name:
            if node.value is None:
                raise ValueError(f"missing value for {name}")
            return ast.literal_eval(node.value)
    raise ValueError(f"missing {name}")


def normalize_parents(value: object) -> RevisionValue:
    if value is None:
        return None
    if isinstance(value, str):
        return (value,)
    if isinstance(value, (tuple, list)) and all(isinstance(item, str) for item in value):
        return tuple(value)
    raise ValueError("down_revision must be a string, string sequence, or None")


def load_revisions(root: Path) -> tuple[dict[str, RevisionValue], list[str]]:
    revisions = {}
    failures = []
    for path in sorted((root / "migrations" / "versions").glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            revision = assignment_value(tree, "revision")
            parents = normalize_parents(assignment_value(tree, "down_revision"))
        except (SyntaxError, ValueError) as exc:
            failures.append(f"{path.relative_to(root)}: {exc}")
            continue
        if not isinstance(revision, str) or not revision:
            failures.append(f"{path.relative_to(root)}: revision must be a non-empty string")
            continue
        if revision in revisions:
            failures.append(f"duplicate revision: {revision}")
            continue
        revisions[revision] = parents
    return revisions, failures


def check_graph(revisions: dict[str, RevisionValue]) -> list[str]:
    failures = []
    if not revisions:
        return ["no Alembic revisions found"]

    referenced = set()
    roots = []
    for revision, parents in revisions.items():
        if parents is None:
            roots.append(revision)
            continue
        for parent in parents:
            referenced.add(parent)
            if parent not in revisions:
                failures.append(f"revision {revision} references missing parent {parent}")

    heads = sorted(set(revisions) - referenced)
    if len(roots) != 1:
        failures.append(f"expected exactly one migration root, found {len(roots)}: {sorted(roots)}")
    if len(heads) != 1:
        failures.append(f"expected exactly one migration head, found {len(heads)}: {heads}")

    visiting = set()
    visited = set()

    def visit(revision: str) -> None:
        if revision in visited or revision not in revisions:
            return
        if revision in visiting:
            failures.append(f"migration cycle detected at {revision}")
            return
        visiting.add(revision)
        for parent in revisions[revision] or ():
            visit(parent)
        visiting.remove(revision)
        visited.add(revision)

    for revision in revisions:
        visit(revision)
    return failures


def run(root: Path) -> list[str]:
    revisions, failures = load_revisions(root)
    failures.extend(check_graph(revisions))
    return failures


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = run(root)
    if failures:
        print("Migration verification failed:\n", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("Migration verification passed (single root, single head, complete chain).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
