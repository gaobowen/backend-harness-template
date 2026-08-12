#!/usr/bin/env python3
import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path
from typing import Any, cast


def read_json(root: Path, project_path: str) -> dict[str, Any]:
    value = json.loads((root / project_path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{project_path} must contain a JSON object")
    return cast(dict[str, Any], value)


def walk_python(root: Path, source_roots: Iterable[str]) -> Iterable[Path]:
    for source_root in source_roots:
        absolute = root / source_root
        if not absolute.exists():
            continue
        yield from sorted(absolute.rglob("*.py"))


def enabled_providers(value: str, failures: list[str]) -> list[str]:
    if value == "both":
        return ["github", "gitlab"]
    if value in {"github", "gitlab"}:
        return [value]
    failures.append(f"unsupported scmProvider: {value!r}")
    return []


def make_targets(source: str) -> set[str]:
    return set(re.findall(r"^([a-zA-Z0-9_-]+):", source, flags=re.MULTILINE))


def run(root: Path) -> list[str]:
    failures = []
    try:
        config = read_json(root, "harness.config.json")
        policy = read_json(root, "harness/loop-policy.json")
        budget = read_json(root, "harness/loop-budget.json")
        project = read_json(root, "harness/project.json")
    except (OSError, json.JSONDecodeError) as exc:
        return [f"cannot load harness JSON: {exc}"]

    for project_path in config.get("requiredFiles", []):
        if not (root / project_path).exists():
            failures.append(f"missing required file: {project_path}")

    if config.get("schemaVersion") != 2:
        failures.append("harness.config.json must use schemaVersion 2")
    if project.get("schemaVersion") != 2:
        failures.append("harness/project.json must use schemaVersion 2")

    providers = enabled_providers(str(project.get("scmProvider")), failures)
    for provider in providers:
        provider_config = config.get("scmProviders", {}).get(provider)
        if not provider_config:
            failures.append(f"missing SCM configuration: {provider}")
            continue
        for project_path in provider_config.get("requiredFiles", []):
            if not (root / project_path).exists():
                failures.append(f"{provider} is missing required file: {project_path}")
        ci_path = root / provider_config.get("ciFile", "")
        if ci_path.exists():
            ci_source = ci_path.read_text(encoding="utf-8")
            for command in provider_config.get("requiredCommands", []):
                if command not in ci_source:
                    failures.append(f"{provider} CI is missing command: {command}")

    if project.get("scmProvider") != "both":
        for provider, provider_config in config.get("scmProviders", {}).items():
            if provider in providers:
                continue
            for project_path in provider_config.get("requiredFiles", []):
                if (root / project_path).exists():
                    failures.append(
                        f"unexpected {provider} file for {project.get('scmProvider')} project: {project_path}"
                    )

    makefile = (root / "Makefile").read_text(encoding="utf-8")
    targets = make_targets(makefile)
    for target in config.get("requiredMakeTargets", []):
        if target not in targets:
            failures.append(f"Makefile is missing target: {target}")

    max_lines = int(config.get("maxSourceFileLines", 500))
    for path in walk_python(root, config.get("sourceRoots", [])):
        source = path.read_text(encoding="utf-8")
        project_path = path.relative_to(root)
        line_count = len(source.splitlines())
        if line_count > max_lines:
            failures.append(f"{project_path} has {line_count} lines; limit is {max_lines}")
        if re.search(r"#\s*type:\s*ignore\b", source):
            failures.append(f"{project_path} suppresses a type error")
        if re.search(r"@pytest\.mark\.(?:skip|skipif)\b", source):
            failures.append(f"{project_path} contains a skipped test")

    if policy.get("autonomy") != "report-only":
        failures.append("new templates must start in report-only autonomy")
    if int(policy.get("maxAttemptsPerItem", 99)) > 2:
        failures.append("maxAttemptsPerItem must not exceed 2 by default")
    if int(policy.get("maxFilesPerChange", 99)) > 5:
        failures.append("maxFilesPerChange must not exceed 5 by default")
    if any(policy.get(key) for key in ("allowAutoCommit", "allowAutoPush", "allowAutoMerge")):
        failures.append("automatic Git writes must be disabled by default")
    if not policy.get("requireIndependentVerification"):
        failures.append("independent verification must be required")

    if budget.get("maxAttemptsPerItem") != policy.get("maxAttemptsPerItem"):
        failures.append("budget and policy disagree on maxAttemptsPerItem")
    if int(budget.get("maxTokensPerRun", 0)) > int(budget.get("dailyTokenBudget", 0)):
        failures.append("maxTokensPerRun cannot exceed dailyTokenBudget")
    if int(budget.get("maxRunMinutes", 999)) > 60:
        failures.append("default loop run must not exceed 60 minutes")

    config_paths = config.get("protectedPaths", [])
    policy_paths = policy.get("protectedPaths", [])
    if config_paths != policy_paths:
        failures.append("protected paths differ between harness.config.json and loop-policy.json")

    gate = (root / "gate.yaml").read_text(encoding="utf-8")
    for pattern in policy_paths:
        if f'"{pattern}"' not in gate:
            failures.append(f"gate.yaml is missing protected path: {pattern}")
    if not re.search(r"auto_merge:\s*false", gate):
        failures.append("gate.yaml must disable auto merge")

    state = (root / "STATE.md").read_text(encoding="utf-8")
    if not re.search(r"mode:\s*report-only", state):
        failures.append("STATE.md must start in report-only mode")

    pyproject = (root / "pyproject.toml").read_text(encoding="utf-8")
    if 'requires-python = ">=3.12"' not in pyproject:
        failures.append("pyproject.toml must require Python 3.12 or newer")
    if not (root / "uv.lock").exists():
        failures.append("uv.lock is required for reproducible dependency resolution")

    return failures


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = run(root)
    if failures:
        print("Harness verification failed:\n", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    project = read_json(root, "harness/project.json")
    policy = read_json(root, "harness/loop-policy.json")
    print(
        "Harness verification passed "
        f"({project['scmProvider']} SCM, {len(policy['protectedPaths'])} protected paths, report-only)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
