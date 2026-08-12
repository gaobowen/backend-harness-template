#!/usr/bin/env python3
import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.init_harness import (  # noqa: E402
    initialize_project,
    normalize_project_name,
    normalize_provider,
    prune_scm_files,
)

EXCLUDED_ROOTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "htmlcov",
}


def ignored(_: str, names: list[str]) -> set[str]:
    return {name for name in names if name in EXCLUDED_ROOTS or name.endswith(".pyc") or name == "coverage.xml"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Copy and initialize a backend harness project.")
    parser.add_argument("--target", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--provider", default="both", choices=("github", "gitlab", "both"))
    parser.add_argument("--description", default="Describe the product, its users, and the outcome it provides.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    source_root = Path(__file__).resolve().parents[1]
    target_root = Path(args.target).expanduser()
    if not target_root.is_absolute():
        target_root = (source_root / target_root).resolve()
    else:
        target_root = target_root.resolve()

    name = normalize_project_name(args.name)
    provider = normalize_provider(args.provider)
    if not name:
        print("A valid --name is required.", file=sys.stderr)
        return 1
    if source_root == target_root or source_root in target_root.parents:
        print("Target must be outside the template directory.", file=sys.stderr)
        return 1
    if target_root.exists():
        print(f"Target already exists: {target_root}", file=sys.stderr)
        return 1

    target_root.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copytree(source_root, target_root, ignore=ignored)
        prune_scm_files(target_root, provider)
        initialize_project(target_root, name, args.description, provider)
    except Exception:
        shutil.rmtree(target_root, ignore_errors=True)
        raise

    print(f"Created {name} at {target_root}.")
    print(f"Next: cd {target_root!s} && uv sync --all-groups && make preflight")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
