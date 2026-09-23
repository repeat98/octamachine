#!/usr/bin/env python3
"""Inspect a locally supplied Machinedrum flash image without modifying it."""

import argparse
import hashlib
import json
import struct
import sys
import zlib
from pathlib import Path


ROM_SIZE = 0x800000
MD163_FNV64 = 0x33B7C1A9E29F43FD
MD163_MAME_CRC32 = 0x3D552C99
MD163_MAME_SHA1 = "a872a2f3527063673d6ea6d3080c4c62ef0cadc1"
FNV_OFFSET = 14695981039346656037
FNV_PRIME = 1099511628211
MASK64 = (1 << 64) - 1


def mapped_rom(address: int) -> str | None:
    if 0 <= address < 0x00100000:
        return "bootstrap flash window"
    if 0x10000000 <= address < 0x10800000:
        return "full flash window"
    return None


def mapped_ram(address: int) -> str | None:
    if 0x00100000 <= address < 0x00300000:
        return "patch/main RAM range"
    if 0x01000000 <= address < 0x01002000:
        return "ColdFire internal SRAM range"
    return None


def inspect(path: Path) -> dict[str, object]:
    sha256 = hashlib.sha256()
    sha1 = hashlib.sha1()
    crc32 = 0
    fnv64 = FNV_OFFSET
    size = 0
    reset_bytes = bytearray()

    with path.open("rb") as image:
        while chunk := image.read(1024 * 1024):
            if len(reset_bytes) < 8:
                reset_bytes.extend(chunk[: 8 - len(reset_bytes)])
            size += len(chunk)
            sha256.update(chunk)
            sha1.update(chunk)
            crc32 = zlib.crc32(chunk, crc32)
            for byte in chunk:
                fnv64 = ((fnv64 ^ byte) * FNV_PRIME) & MASK64

    result: dict[str, object] = {
        "path": str(path),
        "size_bytes": size,
        "expected_size_bytes": ROM_SIZE,
        "sha256": sha256.hexdigest(),
        "sha1": sha1.hexdigest(),
        "crc32": f"{crc32 & 0xffffffff:08x}",
        "gearmulator_fnv64": f"{fnv64:016x}",
        "matches_md_os_1_63_size": size == ROM_SIZE,
        "matches_mame_md_os_1_63_sha1": size == ROM_SIZE and sha1.hexdigest() == MD163_MAME_SHA1,
        "matches_mame_md_os_1_63_crc32": size == ROM_SIZE and (crc32 & 0xffffffff) == MD163_MAME_CRC32,
        "matches_gearmulator_md_os_1_63_fingerprint": size == ROM_SIZE and fnv64 == MD163_FNV64,
    }
    if len(reset_bytes) == 8:
        initial_sp, reset_pc = struct.unpack(">II", reset_bytes)
        result["reset_vectors"] = {
            "initial_sp": f"0x{initial_sp:08x}",
            "initial_sp_mapping_candidate": mapped_ram(initial_sp),
            "reset_pc": f"0x{reset_pc:08x}",
            "reset_pc_mapping_candidate": mapped_rom(reset_pc),
        }
    else:
        result["reset_vectors"] = None
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path, help="user-supplied 8 MiB Machinedrum flash dump")
    parser.add_argument("--json", action="store_true", help="print the report as JSON")
    args = parser.parse_args()

    try:
        report = inspect(args.image)
    except OSError as exc:
        print(f"Cannot read image: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"Image: {report['path']}")
        print(f"Size: {report['size_bytes']} bytes (expected {ROM_SIZE})")
        print(f"SHA-256: {report['sha256']}")
        print(f"SHA-1: {report['sha1']}")
        print(f"CRC-32: {report['crc32']}")
        print(f"Gearmulator FNV-64: {report['gearmulator_fnv64']}")
        print(f"Exact Gearmulator OS 1.63 image: {report['matches_gearmulator_md_os_1_63_fingerprint']}")
        vectors = report["reset_vectors"]
        if vectors is not None:
            print(f"Initial SP: {vectors['initial_sp']} ({vectors['initial_sp_mapping_candidate'] or 'outside known RAM ranges'})")
            print(f"Reset PC: {vectors['reset_pc']} ({vectors['reset_pc_mapping_candidate'] or 'outside known flash ranges'})")
        print("This is a read-only format/fingerprint report, not a bootability verdict.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
