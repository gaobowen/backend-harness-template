#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.main import app  # noqa: E402


def rendered_openapi() -> str:
    return json.dumps(app.openapi(), indent=2, sort_keys=True, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate or verify the committed FastAPI OpenAPI document.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    output_path = ROOT / "docs" / "openapi.json"
    expected = rendered_openapi()
    if args.write:
        output_path.write_text(expected, encoding="utf-8")
        print(f"Wrote {output_path.relative_to(ROOT)}")
        return 0

    if not output_path.exists():
        print("docs/openapi.json is missing; run make openapi-generate", file=sys.stderr)
        return 1
    if output_path.read_text(encoding="utf-8") != expected:
        print("OpenAPI drift detected; review the contract and run make openapi-generate", file=sys.stderr)
        return 1
    print("OpenAPI verification passed (committed schema matches application routes).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
