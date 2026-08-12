#!/usr/bin/env python3
import argparse
import json
import re
import shutil
import sys
from pathlib import Path

VALID_NAME = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def normalize_project_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9._-]+", "-", value.strip().lower()).strip("-")
    return normalized if VALID_NAME.fullmatch(normalized) else ""


def normalize_provider(value: str) -> str:
    normalized = value.strip().lower()
    if normalized not in {"github", "gitlab", "both"}:
        raise ValueError("provider must be github, gitlab, or both")
    return normalized


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def replace_project_name(pyproject_path: Path, name: str) -> None:
    lines = pyproject_path.read_text(encoding="utf-8").splitlines()
    in_project = False
    replaced = False
    for index, line in enumerate(lines):
        if line.strip() == "[project]":
            in_project = True
            continue
        if in_project and line.startswith("["):
            break
        if in_project and re.match(r"^name\s*=", line):
            lines[index] = f'name = "{name}"'
            replaced = True
            break
    if not replaced:
        raise ValueError("pyproject.toml has no [project] name")
    pyproject_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def prune_scm_files(root: Path, provider: str) -> None:
    if provider == "github":
        (root / ".gitlab-ci.yml").unlink(missing_ok=True)
        shutil.rmtree(root / ".gitlab", ignore_errors=True)
        (root / "renovate.json").unlink(missing_ok=True)
    elif provider == "gitlab":
        shutil.rmtree(root / ".github", ignore_errors=True)


def initialize_project(root: Path, name: str, description: str, provider: str) -> None:
    current_project_path = root / "harness" / "project.json"
    current_project = json.loads(current_project_path.read_text(encoding="utf-8"))
    old_name = str(current_project.get("name", "backend-harness-template"))

    replace_project_name(root / "pyproject.toml", name)
    lock_path = root / "uv.lock"
    if lock_path.exists():
        lock_path.write_text(
            lock_path.read_text(encoding="utf-8").replace(f'name = "{old_name}"', f'name = "{name}"'),
            encoding="utf-8",
        )
    write_json(
        current_project_path,
        {"schemaVersion": 2, "name": name, "description": description, "scmProvider": provider},
    )

    context_path = root / "docs" / "project-context.md"
    context = context_path.read_text(encoding="utf-8")
    context = re.sub(r"^- Project name:.*$", f"- Project name: `{name}`", context, flags=re.MULTILINE)
    context = re.sub(r"^- Product summary:.*$", f"- Product summary: {description}", context, flags=re.MULTILINE)
    context_path.write_text(context, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize backend harness metadata in the current copy.")
    parser.add_argument("--name", required=True)
    parser.add_argument("--provider", default="both", choices=("github", "gitlab", "both"))
    parser.add_argument("--description", default="Describe the product, its users, and the outcome it provides.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path.cwd()
    name = normalize_project_name(args.name)
    if not name:
        print("A valid --name is required.", file=sys.stderr)
        return 1
    provider = normalize_provider(args.provider)

    if provider in {"github", "both"} and not (root / ".github" / "workflows" / "ci.yml").exists():
        print("GitHub files are unavailable; create a fresh copy from the template.", file=sys.stderr)
        return 1
    if provider in {"gitlab", "both"} and not (root / ".gitlab-ci.yml").exists():
        print("GitLab files are unavailable; create a fresh copy from the template.", file=sys.stderr)
        return 1

    initialize_project(root, name, args.description, provider)
    prune_scm_files(root, provider)
    print(f"Harness initialized for {name}.")
    print("Next: update docs/project-context.md and docs/architecture.md, then run make preflight.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
