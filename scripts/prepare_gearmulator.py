#!/usr/bin/env python3
"""Apply the Machinedrum trace and baseline-driver patches to Gearmulator."""

import subprocess
import sys
from pathlib import Path

from references import REFERENCES, ROOT


GEARMULATOR = ROOT / "vendor" / "gearmulator-md-mm"
PATCHES = (
    ROOT / "patches" / "gearmulator-md-mm" / "0001-opt-in-md-bus-trace.patch",
    ROOT / "patches" / "gearmulator-md-mm" / "0002-md-baseline-checkpoints.patch",
)
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
    # Patch 0002 edits the same trace callback as 0001, so checking the
    # patches independently in forward order makes 0001 appear absent once
    # both are applied. Patch 0002 depends on 0001; its reverse check therefore
    # proves that the complete stack is already present.
    if run(*args, "--reverse", "--check", str(PATCHES[-1])).returncode == 0:
        print("Gearmulator Machinedrum trace and baseline patches already applied")
        return 0
    applied_patches = []
    for patch in PATCHES:
        if run(*args, "--reverse", "--check", str(patch)).returncode == 0:
            continue
        check = run(*args, "--check", str(patch))
        if check.returncode:
            print(check.stderr or check.stdout, file=sys.stderr)
            print(f"Gearmulator has other changes or {patch.name} no longer matches", file=sys.stderr)
            return 1
        applied = run(*args, str(patch))
        if applied.returncode:
            print(applied.stderr or applied.stdout, file=sys.stderr)
            return 1
        applied_patches.append(patch.name)
    if applied_patches:
        print("Applied Gearmulator patches: " + ", ".join(applied_patches))
    else:
        print("Gearmulator Machinedrum trace and baseline patches already applied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
