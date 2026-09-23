#!/usr/bin/env python3
"""Apply the opt-in Machinedrum bus trace patch to the pinned Gearmulator fork."""

import subprocess
import sys
from pathlib import Path

from references import REFERENCES, ROOT


GEARMULATOR = ROOT / "vendor" / "gearmulator-md-mm"
PATCH = ROOT / "patches" / "gearmulator-md-mm" / "0001-opt-in-md-bus-trace.patch"
PIN = next(repo["commit"] for repo in REFERENCES if repo["name"] == "gearmulator-md-mm")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)


def main() -> int:
    if not GEARMULATOR.is_dir():
        print("Missing vendor/gearmulator-md-mm; run 'make refs' first", file=sys.stderr)
        return 1
    head = run("-C", str(GEARMULATOR), "rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != PIN:
        print(f"Gearmulator MD/MM must be at pinned commit {PIN}", file=sys.stderr)
        return 1
    args = ("-C", str(GEARMULATOR), "apply")
    if run(*args, "--reverse", "--check", str(PATCH)).returncode == 0:
        print("Gearmulator bus trace patch already applied")
        return 0
    check = run(*args, "--check", str(PATCH))
    if check.returncode:
        print(check.stderr or check.stdout, file=sys.stderr)
        print("Gearmulator has other changes or the patch no longer matches", file=sys.stderr)
        return 1
    applied = run(*args, str(PATCH))
    if applied.returncode:
        print(applied.stderr or applied.stdout, file=sys.stderr)
        return 1
    print("Applied optional Machinedrum SIM/DSP/unmapped bus tracing")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
