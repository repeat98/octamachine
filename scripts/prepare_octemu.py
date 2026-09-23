#!/usr/bin/env python3
"""Initialize the pinned octemu source and apply this project's local patch."""

import subprocess
import sys
from pathlib import Path

from references import REFERENCES, ROOT


OCTEMU = ROOT / "vendor" / "octemu"
PATCH = ROOT / "patches" / "octemu" / "0001-sdram-alias-and-interactive-pace.patch"
PIN = next(repo["commit"] for repo in REFERENCES if repo["name"] == "octemu")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)


def main() -> int:
    result = run("submodule", "update", "--init", "--", "vendor/octemu")
    if result.returncode:
        print(result.stderr or result.stdout, file=sys.stderr)
        return result.returncode
    head = run("-C", str(OCTEMU), "rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != PIN:
        print(f"octemu must be at pinned commit {PIN}; found {head.stdout.strip()}", file=sys.stderr)
        return 1
    args = ("-C", str(OCTEMU), "apply")
    if run(*args, "--reverse", "--check", str(PATCH)).returncode == 0:
        print("octemu patch already applied")
        return 0
    check = run(*args, "--check", str(PATCH))
    if check.returncode:
        print(check.stderr or check.stdout, file=sys.stderr)
        print("octemu has other changes or the patch no longer matches", file=sys.stderr)
        return 1
    applied = run(*args, str(PATCH))
    if applied.returncode:
        print(applied.stderr or applied.stdout, file=sys.stderr)
        return 1
    print("Applied octemu SDRAM alias and interactive pacing patch")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
