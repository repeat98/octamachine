#!/usr/bin/env python3
"""Apply the Machinedrum trace, baseline-driver, and CPU-summary patches."""

import subprocess
import sys
from pathlib import Path

from references import REFERENCES, ROOT


GEARMULATOR = ROOT / "vendor" / "gearmulator-md-mm"
PATCHES = (
    ROOT / "patches" / "gearmulator-md-mm" / "0001-opt-in-md-bus-trace.patch",
    ROOT / "patches" / "gearmulator-md-mm" / "0002-md-baseline-checkpoints.patch",
    ROOT / "patches" / "gearmulator-md-mm" / "0003-opt-in-coldfire-execution-summary.patch",
)
PIN = next(repo["commit"] for repo in REFERENCES if repo["name"] == "gearmulator-md-mm")


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True)


def is_applied(patch: Path) -> bool:
    return run("-C", str(GEARMULATOR), "apply", "--reverse", "--check", str(patch)).returncode == 0


def main() -> int:
    if not GEARMULATOR.is_dir():
        print("Missing vendor/gearmulator-md-mm; run 'make refs' first", file=sys.stderr)
        return 1
    head = run("-C", str(GEARMULATOR), "rev-parse", "HEAD")
    if head.returncode or head.stdout.strip() != PIN:
        print(f"Gearmulator MD/MM must be at pinned commit {PIN}", file=sys.stderr)
        return 1
    args = ("-C", str(GEARMULATOR), "apply")
    # Patch 0002 edits the same callbacks as 0001, so its reverse check is the
    # sentinel for the original pair. Patch 0003 is independent; apply it
    # separately when that pair is already present.
    if is_applied(PATCHES[1]):
        if is_applied(PATCHES[2]):
            print("Gearmulator Machinedrum trace, baseline, and CPU-summary patches already applied")
            return 0
        check = run(*args, "--check", str(PATCHES[2]))
        if check.returncode:
            print(check.stderr or check.stdout, file=sys.stderr)
            print(f"Gearmulator has other changes or {PATCHES[2].name} no longer matches", file=sys.stderr)
            return 1
        applied = run(*args, str(PATCHES[2]))
        if applied.returncode:
            print(applied.stderr or applied.stdout, file=sys.stderr)
            return 1
        print("Applied Gearmulator patch: " + PATCHES[2].name)
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
