#!/usr/bin/env python3
"""Manage ignored vendor checkouts. No firmware is downloaded."""

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REFERENCES = json.loads((ROOT / "references.json").read_text())["repositories"]
VENDOR = ROOT / "vendor"


def git(*args: str, cwd: Path | None = None) -> str:
    result = subprocess.run(
        ["git", *args], cwd=cwd, check=True, text=True, capture_output=True
    )
    return result.stdout.strip()


def list_references() -> None:
    for repo in REFERENCES:
        mode = "sparse" if "sparse" in repo else "checkout"
        print(f'{repo["name"]:22} {mode:9} {repo["url"]} ({repo["ref"]})')


def validate() -> int:
    names = set()
    for repo in REFERENCES:
        name = repo.get("name", "")
        if not name or name in names or name in (".", "..") or "/" in name or "\\" in name:
            print(f"Invalid or duplicate repository name: {name!r}", file=sys.stderr)
            return 1
        names.add(name)
        if not repo.get("url", "").startswith("https://") or not repo.get("ref"):
            print(f"Missing HTTPS URL or ref for {name}", file=sys.stderr)
            return 1
        sparse = repo.get("sparse")
        if sparse and (Path(sparse).is_absolute() or ".." in Path(sparse).parts):
            print(f"Invalid sparse path for {name}", file=sys.stderr)
            return 1
    print(f"Validated {len(names)} reference repositories")
    return 0


def status() -> int:
    for repo in REFERENCES:
        path = VENDOR / repo["name"]
        if not path.is_dir():
            print(f'{repo["name"]:20} not fetched')
            continue
        try:
            commit = git("rev-parse", "HEAD", cwd=path)
            dirty = bool(git("status", "--porcelain", cwd=path))
            origin = git("remote", "get-url", "origin", cwd=path)
        except (OSError, subprocess.CalledProcessError):
            print(f'{repo["name"]:20} directory exists but is not a usable Git checkout')
            return 1
        suffix = " dirty" if dirty else ""
        pin = repo.get("commit")
        if pin and commit != pin:
            suffix += f" PIN MISMATCH (expected {pin})"
        expected = repo["url"].removesuffix(".git")
        mismatch = " URL MISMATCH" if origin.removesuffix(".git") != expected else ""
        print(f'{repo["name"]:20} {commit}{suffix}{mismatch}')
    return 0


def fetch() -> int:
    if validate():
        return 1
    VENDOR.mkdir(exist_ok=True)
    for repo in REFERENCES:
        path = VENDOR / repo["name"]
        if path.exists():
            print(f'{repo["name"]}: already exists; leaving it untouched')
            continue
        if repo["name"] == "octemu":
            print("Initializing pinned octemu submodule...", flush=True)
            try:
                git("submodule", "update", "--init", "--", "vendor/octemu", cwd=ROOT)
            except (OSError, subprocess.CalledProcessError) as exc:
                print(f"Could not initialize octemu: {exc}", file=sys.stderr)
                return 1
            continue
        print(f'Cloning {repo["name"]} ({repo["ref"]})...', flush=True)
        try:
            args = ["clone", "--depth", "1", "--filter=blob:none"]
            if "sparse" in repo:
                args.append("--sparse")
            args.extend(("--branch", repo["ref"], repo["url"], str(path)))
            git(*args)
            if repo.get("commit"):
                git("fetch", "--depth", "1", "origin", repo["commit"], cwd=path)
                git("checkout", "--detach", repo["commit"], cwd=path)
            if "sparse" in repo:
                git("sparse-checkout", "set", "--no-cone", "/" + repo["sparse"], cwd=path)
        except (OSError, subprocess.CalledProcessError) as exc:
            print(f'Could not clone {repo["name"]}: {exc}', file=sys.stderr)
            return 1
    return status()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("list", "status", "fetch", "validate"))
    args = parser.parse_args()
    if args.command == "list":
        list_references()
        return 0
    if args.command == "status":
        return status()
    if args.command == "validate":
        return validate()
    return fetch()


if __name__ == "__main__":
    raise SystemExit(main())
