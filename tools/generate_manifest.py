#!/usr/bin/env python3
"""Generate or verify interface_manifest.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))

from jcheng_contracts.manifest import build_manifest, check_manifest, write_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--write", action="store_true", help="write interface_manifest.json")
    group.add_argument("--check", action="store_true", help="verify the committed manifest")
    args = parser.parse_args()

    if args.write:
        path = write_manifest(ROOT)
        manifest = build_manifest(ROOT)
        print(f"wrote {path}")
        print(f"contract_hash {manifest['contract_hash']}")
        return 0

    differences = check_manifest(ROOT)
    if differences:
        print("manifest is stale:", file=sys.stderr)
        for item in differences:
            print(f"  {item}", file=sys.stderr)
        return 1
    manifest = build_manifest(ROOT)
    print(f"manifest OK: {manifest['contract_hash']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
