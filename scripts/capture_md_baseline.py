#!/usr/bin/env python3
"""Run two bounded Machinedrum reference boots and write reviewed metadata.

The private trace files contain local emulator data. The JSON summary omits
MMIO values, PC samples, firmware paths, and the local image's SHA-256.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import subprocess
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from audit_md_image import inspect as inspect_image  # noqa: E402
from references import REFERENCES  # noqa: E402


SCHEMA_VERSION = 1
GEARMULATOR_PIN = next(
    item["commit"] for item in REFERENCES if item["name"] == "gearmulator-md-mm"
)
RECURSIVE_REVISIONS = {
    "source/3rdparty/RmlUi": "97bb5921595a0528bd67d61f328885ac19643623",
    "source/3rdparty/freetype": "828916527ce4f69af722bce46ce54d289001a0bd",
    "source/3rdparty/freetype/subprojects/dlg": "72dfcc858c040c54a6a0b88fcb7e70ee186d3167",
    "source/3rdparty/lunasvg": "f8aabfb444bb37f69df7290790f57e4a27730a93",
    "source/3rdparty/lunasvg/plutovg": "5e4712cf873b0c7829a4a6157763e2ad3ac49164",
    "source/cpp-terminal": "a79a1a1766e0e8f768955d782e1b84ad5a82b843",
    "source/dsp56300": "1378c43074e6ec22f69f14ed55c21e44c5ccadc1",
    "source/dsp56300/source/asmjit": "3577608cab0bc509f856ebf6e41b2f9d9f71acc4",
    "source/mc68k": "ace95b3d0a5a332db147244762dda65a9f010b9f",
}
PATCH_FILES = (
    ROOT / "patches/gearmulator-md-mm/0001-opt-in-md-bus-trace.patch",
    ROOT / "patches/gearmulator-md-mm/0002-md-baseline-checkpoints.patch",
)
EXPECTED_CHECKPOINTS = (
    "cold_reset",
    "cold_dsp1_booted",
    "cold_dsp2_booted",
    "cold_firmware_ready",
    "cold_initialized",
    "cold_idle_no_stimulus",
    "cached_reset",
    "cached_dsp1_booted",
    "cached_dsp2_booted",
    "cached_firmware_ready",
    "cached_ready",
    "cached_idle_no_stimulus",
)
TRACE_RE = re.compile(
    rb"^mdbus instance=(\d+) label=([a-z_]+) cycle=(\d+) "
    rb"pc=([0-9a-fA-F]+) ([RW])(\d+) addr=([0-9a-fA-F]+) "
    rb"value=([0-9a-fA-F]+)$"
)
DSP_SUMMARY_RE = re.compile(
    rb"^mdbus dsp_write_summary instance=(\d+) label=([a-z_]+) "
    rb"dsp=(\d+) count=(\d+) first_cycle=(\d+) last_cycle=(\d+)$"
)
SIM_PORT_SUMMARY_RE = re.compile(
    rb"^mdbus sim_port_write_summary instance=(\d+) label=([a-z_]+) "
    rb"data_writes=(\d+) data_transitions=(\d+) direction_writes=(\d+) "
    rb"direction_transitions=(\d+) first_cycle=(\d+) last_cycle=(\d+)$"
)
INTEGER_CHECKPOINT_FIELDS = {
    "frames",
    "pc_register",
    "sp_register",
    "host_cycles",
    "mcu_cycles",
    "dsp1_cycles",
    "dsp2_cycles",
    "panel_bytes",
    "panel_tiles",
    "panel_lit_pixels",
}
BOOLEAN_CHECKPOINT_FIELDS = {
    "dsp1_booted",
    "dsp2_booted",
    "panel_handshake",
    "midi_ready",
    "factory_cache_ready",
    "factory_init_expected",
    "flash_dirty",
}
PUBLIC_CHECKPOINT_FIELDS = INTEGER_CHECKPOINT_FIELDS | BOOLEAN_CHECKPOINT_FIELDS | {
    "checkpoint",
    "initial_state",
    "schema",
}


def parse_checkpoint(line: str) -> dict[str, Any]:
    """Parse a driver's MDCP key/value checkpoint line."""
    if not line.startswith("MDCP "):
        raise ValueError("not an MDCP checkpoint line")
    fields: dict[str, Any] = {}
    for token in line[5:].split():
        key, separator, value = token.partition("=")
        if not separator:
            raise ValueError("malformed checkpoint field")
        if key not in PUBLIC_CHECKPOINT_FIELDS:
            continue
        if key in INTEGER_CHECKPOINT_FIELDS:
            fields[key] = int(value)
        elif key in BOOLEAN_CHECKPOINT_FIELDS:
            fields[key] = value == "1"
        else:
            fields[key] = value
    if fields.get("schema") != "1" or not fields.get("checkpoint"):
        raise ValueError("unsupported or unnamed checkpoint")
    return fields


def _parse_tokens(line: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for token in line.split()[2:]:
        key, separator, value = token.partition("=")
        if separator:
            result[key] = value
    return result


def _region(address: int) -> str:
    if 0x00300000 <= address < 0x00310000:
        return "SIM"
    if 0x00500000 <= address < 0x00500008:
        return "DSP1_HDI08"
    if 0x00600000 <= address < 0x00600008:
        return "DSP2_HDI08"
    return "other_peripheral"


def parse_trace(path: Path, *, retain_events: bool = True) -> dict[str, Any]:
    """Read a private trace while retaining only redacted event metadata."""
    labels = ("cold_blank_flash", "cached_factory_flash")
    events: dict[str, list[tuple[int, str, int, int, str]]] = {
        label: [] for label in labels
    }
    event_counts = Counter()
    event_digests = {label: hashlib.sha256() for label in labels}
    region_counts: Counter[tuple[str, str, str]] = Counter()
    dsp_summaries: dict[tuple[str, int], dict[str, int]] = {}
    port_summaries: dict[str, dict[str, int]] = {}
    footer: dict[str, str] | None = None
    instance_labels: dict[int, str] = {}
    malformed = 0
    truncated = False

    with path.open("rb") as trace:
        for line in trace:
            line = line.rstrip(b"\r\n")
            if line == b"mdbus trace truncated at configured event limit":
                truncated = True
                continue
            if line.startswith(b"mdbus summary "):
                footer = _parse_tokens(line.decode("ascii", errors="replace"))
                continue
            match = TRACE_RE.match(line)
            if match:
                instance_raw, label_raw, cycle_raw, _pc_raw, direction_raw, width_raw, address_raw, _value_raw = match.groups()
                instance = int(instance_raw)
                label = label_raw.decode("ascii")
                cycle = int(cycle_raw)
                direction = direction_raw.decode("ascii")
                width_bits = int(width_raw) * 8
                address = int(address_raw, 16)
                scope = _region(address)
                previous_label = instance_labels.setdefault(instance, label)
                if previous_label != label or label not in events:
                    malformed += 1
                    continue
                event = (cycle, direction, width_bits, address, scope)
                event_counts[label] += 1
                event_digests[label].update(json.dumps(event, separators=(",", ":")).encode())
                event_digests[label].update(b"\n")
                if retain_events:
                    events[label].append(event)
                region_counts[(label, scope, direction)] += 1
                continue
            match = DSP_SUMMARY_RE.match(line)
            if match:
                _instance, label_raw, dsp_raw, count_raw, first_raw, last_raw = match.groups()
                dsp_summaries[(label_raw.decode("ascii"), int(dsp_raw))] = {
                    "writes": int(count_raw),
                    "first_cycle": int(first_raw),
                    "last_cycle": int(last_raw),
                }
                continue
            match = SIM_PORT_SUMMARY_RE.match(line)
            if match:
                (_instance, label_raw, data_raw, data_transition_raw,
                 direction_raw, direction_transition_raw, first_raw, last_raw) = match.groups()
                port_summaries[label_raw.decode("ascii")] = {
                    "data_writes": int(data_raw),
                    "data_value_transitions": int(data_transition_raw),
                    "direction_writes": int(direction_raw),
                    "direction_value_transitions": int(direction_transition_raw),
                    "first_cycle": int(first_raw),
                    "last_cycle": int(last_raw),
                }
                continue
            if line.startswith(b"mdbus "):
                malformed += 1

    # Full private mode deliberately does not retain event tuples in memory;
    # validate the footer against the streaming count in both modes.
    actual_count = sum(event_counts.values())
    if footer is None:
        status = "incomplete"
    elif truncated or footer.get("status") != "complete":
        status = "incomplete"
    elif malformed or int(footer.get("recorded", -1)) != actual_count:
        status = "invalid"
    else:
        status = "complete"

    counts: dict[str, dict[str, dict[str, int]]] = {}
    for (label, region, direction), count in sorted(region_counts.items()):
        counts.setdefault(label, {}).setdefault(region, {})[direction] = count

    return {
        "status": status,
        "truncated": truncated,
        "malformed_records": malformed,
        "recorded_events": actual_count,
        "events_by_label": events,
        "event_counts_by_label": dict(event_counts),
        "events_by_region": counts,
        "event_order_sha256": {
            label: event_digests[label].hexdigest() for label in labels
        },
        "footer": footer or {},
        "dsp_write_summaries": {
            f"{label}:dsp{dsp}": value
            for (label, dsp), value in sorted(dsp_summaries.items())
        },
        "sim_port_write_summaries": port_summaries,
    }


def _checkpoint_projection(line: str) -> dict[str, Any]:
    parsed = parse_checkpoint(line)
    # The bus trace's pc field is a register sample inside a callback, not a
    # proven executing instruction address. Publish reset PC/SP only, before
    # the first instruction runs; omit later register samples.
    if parsed["checkpoint"] not in {"cold_reset", "cached_reset"}:
        parsed.pop("pc_register", None)
        parsed.pop("sp_register", None)
    return parsed


def validate_checkpoints(checkpoints: list[dict[str, Any]]) -> list[str]:
    by_name = {item["checkpoint"]: item for item in checkpoints}
    if len(checkpoints) != len(EXPECTED_CHECKPOINTS) or len(by_name) != len(checkpoints):
        return ["duplicate_or_extra_checkpoint"]
    errors = [name for name in EXPECTED_CHECKPOINTS if name not in by_name]
    if errors:
        return [f"missing_checkpoint:{name}" for name in errors]

    for name in ("cold_reset", "cached_reset"):
        point = by_name[name]
        if point["pc_register"] != 12 or point["sp_register"] != 0:
            errors.append(f"reset_vector_mismatch:{name}")
    for prefix in ("cold", "cached"):
        for dsp in (1, 2):
            point = by_name[f"{prefix}_dsp{dsp}_booted"]
            if not point[f"dsp{dsp}_booted"]:
                errors.append(f"dsp_not_booted:{prefix}:{dsp}")
        ready = by_name[f"{prefix}_firmware_ready"]
        if not ready["panel_handshake"] or not ready["midi_ready"]:
            errors.append(f"firmware_not_ready:{prefix}")
    cold_init = by_name["cold_initialized"]
    if not cold_init["factory_cache_ready"] or not cold_init["flash_dirty"]:
        errors.append("cold_factory_initialization_not_complete")
    if not by_name["cached_reset"]["factory_cache_ready"]:
        errors.append("cached_start_missing_factory_cache")
    if by_name["cached_reset"]["factory_init_expected"]:
        errors.append("cached_start_repeated_factory_initialization")
    for prefix, ready_name, idle_name in (
        ("cold", "cold_initialized", "cold_idle_no_stimulus"),
        ("cached", "cached_ready", "cached_idle_no_stimulus"),
    ):
        ready = by_name[ready_name]
        idle = by_name[idle_name]
        if not idle["midi_ready"] or not idle["panel_handshake"]:
            errors.append(f"idle_lost_readiness:{prefix}")
        for clock in ("host_cycles", "mcu_cycles", "dsp1_cycles", "dsp2_cycles"):
            if idle[clock] <= ready[clock]:
                errors.append(f"idle_clock_did_not_advance:{prefix}:{clock}")
    for name in ("cold_initialized", "cached_ready"):
        point = by_name[name]
        if point["panel_bytes"] < 20_000 or point["panel_tiles"] < 1_000 or point["panel_lit_pixels"] < 500:
            errors.append(f"panel_checkpoint_incomplete:{name}")
    return errors


def validate_trace(trace: dict[str, Any], *, full_private: bool = False) -> list[str]:
    errors: list[str] = []
    if trace["status"] != "complete":
        errors.append("trace_not_complete")
        return errors
    footer = trace["footer"]
    if footer.get("instances") != "2":
        errors.append("trace_instance_count_mismatch")
    if full_private:
        if footer.get("dsp_writes_aggregated") != "false":
            errors.append("full_trace_aggregated_dsp_writes")
        if footer.get("sim_port_writes_aggregated") != "false":
            errors.append("full_trace_aggregated_sim_port_writes")
        if footer.get("read_filter") != "all":
            errors.append("full_trace_filtered_reads")
        if int(footer.get("observed", "-1")) != trace["recorded_events"]:
            errors.append("full_trace_access_count_mismatch")
    else:
        if footer.get("dsp_writes_aggregated") != "true":
            errors.append("dsp_writes_not_aggregated")
        if footer.get("sim_port_writes_aggregated") != "true":
            errors.append("sim_port_writes_not_aggregated")
        if footer.get("read_filter") != "changed_values":
            errors.append("trace_read_filter_mismatch")
    for label in ("cold_blank_flash", "cached_factory_flash"):
        if trace["event_counts_by_label"].get(label, 0) <= 0:
            errors.append(f"no_trace_events:{label}")
        if full_private:
            for dsp in (1, 2):
                region = f"DSP{dsp}_HDI08"
                if trace["events_by_region"].get(label, {}).get(region, {}).get("W", 0) <= 0:
                    errors.append(f"no_dsp_write_events:{label}:dsp{dsp}")
        else:
            if not trace["sim_port_write_summaries"].get(label):
                errors.append(f"no_sim_port_summary:{label}")
            for dsp in (1, 2):
                item = trace["dsp_write_summaries"].get(f"{label}:dsp{dsp}")
                if not item or item["writes"] <= 0:
                    errors.append(f"no_dsp_write_summary:{label}:dsp{dsp}")
    return errors


def _ignored_if_in_repository(path: Path) -> bool:
    try:
        path.relative_to(ROOT)
    except ValueError:
        return True
    result = subprocess.run(
        ["git", "check-ignore", "--no-index", "-q", str(path)],
        cwd=ROOT,
        check=False,
    )
    return result.returncode == 0


def _write_summary(path: Path, summary: dict[str, Any]) -> None:
    path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _run_once(
    driver: Path,
    firmware: Path,
    output: Path,
    run_id: str,
    timeout_seconds: float,
    trace_limit: int,
    full_private_trace: bool,
) -> dict[str, Any]:
    trace_path = output / f"{run_id}.trace.txt"
    stdout_path = output / f"{run_id}.stdout.log"
    stderr_path = output / f"{run_id}.stderr.log"
    env = os.environ.copy()
    env.update({
        "GEARMULATOR_MD_FIRMWARE_BIN": str(firmware),
        "GEARMULATOR_MD_BUS_TRACE": str(trace_path),
        "GEARMULATOR_MD_BUS_TRACE_LIMIT": str(trace_limit),
    })
    env.pop("GEARMULATOR_MD_BUS_TRACE_ENABLED", None)
    env.pop("GEARMULATOR_MD_TRACE_INSTANCE_LABEL", None)
    env.pop("GEARMULATOR_MD_BUS_TRACE_WRITES_ONLY", None)
    if full_private_trace:
        for variable in (
            "GEARMULATOR_MD_BUS_TRACE_DEDUP_READS",
            "GEARMULATOR_MD_BUS_TRACE_IGNORE_SIM_READS",
            "GEARMULATOR_MD_BUS_TRACE_AGGREGATE_DSP_WRITES",
            "GEARMULATOR_MD_BUS_TRACE_AGGREGATE_SIM_PORT_WRITES",
        ):
            env.pop(variable, None)
    else:
        env.update({
            "GEARMULATOR_MD_BUS_TRACE_DEDUP_READS": "1",
            "GEARMULATOR_MD_BUS_TRACE_IGNORE_SIM_READS": "1",
            "GEARMULATOR_MD_BUS_TRACE_AGGREGATE_DSP_WRITES": "1",
            "GEARMULATOR_MD_BUS_TRACE_AGGREGATE_SIM_PORT_WRITES": "1",
        })

    started_at = _utc_now()
    started = time.monotonic()
    timed_out = False
    with stdout_path.open("w") as stdout, stderr_path.open("w") as stderr:
        try:
            process = subprocess.run(
                [str(driver)],
                env=env,
                stdout=stdout,
                stderr=stderr,
                timeout=timeout_seconds,
                check=False,
            )
            return_code: int | None = process.returncode
        except subprocess.TimeoutExpired:
            return_code = None
            timed_out = True

    trace = parse_trace(trace_path, retain_events=not full_private_trace) if trace_path.exists() else {
        "status": "incomplete", "truncated": False, "recorded_events": 0,
        "event_counts_by_label": {"cold_blank_flash": 0, "cached_factory_flash": 0},
        "events_by_label": {"cold_blank_flash": [], "cached_factory_flash": []},
        "events_by_region": {}, "event_order_sha256": {},
        "footer": {}, "dsp_write_summaries": {}, "sim_port_write_summaries": {},
        "malformed_records": 0,
    }
    trace_errors = validate_trace(trace, full_private=full_private_trace)
    checkpoints: list[dict[str, Any]] = []
    checkpoint_parse_errors = 0
    for line in stdout_path.read_text(errors="replace").splitlines():
        if line.startswith("MDCP "):
            try:
                checkpoints.append(_checkpoint_projection(line))
            except (ValueError, KeyError):
                checkpoint_parse_errors += 1
    checkpoint_errors = validate_checkpoints(checkpoints) if not checkpoint_parse_errors else ["malformed_checkpoint"]

    status = "complete"
    if timed_out:
        status = "incomplete"
        reason = "timeout"
    elif return_code == 77:
        status = "failed"
        reason = "driver_skipped"
    elif return_code != 0:
        status = "failed"
        reason = "driver_failed"
    elif trace_errors:
        status = "incomplete" if trace["status"] == "incomplete" else "failed"
        reason = "trace_cap" if trace["truncated"] else "trace_validation_failed"
    elif checkpoint_errors:
        status = "failed"
        reason = "checkpoint_validation_failed"
    else:
        reason = None

    footer = trace["footer"]
    trace_metadata = {
        "status": trace["status"],
        "recorded_events": trace["recorded_events"],
        "event_counts_by_label": trace["event_counts_by_label"],
        "observed_accesses": int(footer.get("observed", "0")),
        "repeat_reads_suppressed": int(footer.get("repeat_reads_suppressed", "0")),
        "sim_reads_filtered": int(footer.get("sim_reads_filtered", "0")),
        "trace_limit": trace_limit,
        "read_filter": footer.get("read_filter"),
        "dsp_writes_aggregated": footer.get("dsp_writes_aggregated") == "true",
        "sim_port_writes_aggregated": footer.get("sim_port_writes_aggregated") == "true",
        "instance_count": int(footer.get("instances", "0")),
        "events_by_region": trace["events_by_region"],
        "dsp_write_summaries": trace["dsp_write_summaries"],
        "sim_port_write_summaries": trace["sim_port_write_summaries"],
        "event_order_sha256": trace["event_order_sha256"],
        "mode": "full_private" if full_private_trace else "summarized",
    }
    return {
        "run_id": run_id,
        "started_at_utc": started_at,
        "duration_seconds": round(time.monotonic() - started, 3),
        "exit_code": return_code,
        "status": status,
        "reason": reason,
        "trace_file": trace_path.name,
        "stdout_log": stdout_path.name,
        "stderr_log": stderr_path.name,
        "trace": trace_metadata,
        "trace_errors": trace_errors,
        "checkpoints": checkpoints,
        "checkpoint_errors": checkpoint_errors,
    }


def _fingerprint_metadata(image: dict[str, Any]) -> dict[str, Any]:
    return {
        "profile_id": "machinedrum-sps1uw-os1.63",
        "public_fingerprints": {
            "size_bytes": image["size_bytes"],
            "sha1": image["sha1"],
            "crc32": image["crc32"],
            "gearmulator_fnv64": image["gearmulator_fnv64"],
        },
    }


def _load_build_metadata(path: Path) -> dict[str, Any]:
    try:
        metadata = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("build metadata is unreadable or invalid JSON") from exc
    if not isinstance(metadata, dict):
        raise ValueError("build metadata must be a JSON object")
    command = metadata.get("command")
    toolchain = metadata.get("toolchain")
    if not isinstance(command, list) or not command or not all(isinstance(part, str) for part in command):
        raise ValueError("build metadata command must be a non-empty argv list")
    if not isinstance(toolchain, dict) or not toolchain:
        raise ValueError("build metadata toolchain must be a non-empty object")
    return {"command": command, "toolchain": toolchain}


def _contract_events(
    events: list[tuple[int, str, int, int, str]],
    checkpoints: list[dict[str, Any]],
    label: str,
) -> list[dict[str, Any]]:
    phase = "cold" if label == "cold_blank_flash" else "cached"
    timeline: list[tuple[int, int, int, dict[str, Any]]] = []
    last_cycle = -1
    for index, (cycle, direction, width_bits, address, region) in enumerate(events):
        if cycle < last_cycle:
            raise ValueError(f"{label} trace MCU cycle moved backwards")
        last_cycle = cycle
        timeline.append((cycle, 0, index, {
            "kind": "mmio_write" if direction == "W" else "mmio_read",
            "address": f"0x{address:08x}",
            "width_bits": width_bits,
            "endianness": "big",
            "region": region,
        }))
    for index, checkpoint in enumerate(checkpoints):
        if not checkpoint["checkpoint"].startswith(f"{phase}_"):
            continue
        timeline.append((checkpoint["mcu_cycles"], 1, index, {
            "kind": "checkpoint",
            "address": None,
            "width_bits": None,
            "endianness": None,
            "region": None,
            **checkpoint,
        }))
    timeline.sort(key=lambda item: (item[0], item[1], item[2]))

    checkpoint_fields = (
        "checkpoint",
        "initial_state",
        "frames",
        "host_cycles",
        "mcu_cycles",
        "dsp1_cycles",
        "dsp2_cycles",
        "dsp1_booted",
        "dsp2_booted",
        "panel_handshake",
        "midi_ready",
        "panel_bytes",
        "panel_tiles",
        "panel_lit_pixels",
        "factory_cache_ready",
        "factory_init_expected",
        "flash_dirty",
        "pc_register",
        "sp_register",
    )
    result = []
    for sequence, (cycle, _priority, _index, data) in enumerate(timeline):
        record = {
            "sequence": sequence,
            "clock_id": "mcu_cycles",
            "time": cycle,
            "kind": data["kind"],
            "label": label,
            "address": data["address"],
            "width_bits": data["width_bits"],
            "endianness": data["endianness"],
            "region": data["region"],
        }
        record.update({key: data.get(key) for key in checkpoint_fields})
        result.append(record)
    return result


def _write_contract_trace(path: Path, events: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as trace:
        for event in events:
            trace.write(json.dumps(event, separators=(",", ":"), sort_keys=True) + "\n")


def _source_state_for_manifest(patch_hashes: dict[str, str]) -> list[dict[str, Any]]:
    sources = [{
        "repository": "gearmulator-md-mm",
        "revision": GEARMULATOR_PIN,
        "dirty": False,
        "patches": [
            {"id": name, "sha256": digest}
            for name, digest in sorted(patch_hashes.items())
        ],
    }]
    sources.extend({
        "repository": f"gearmulator-md-mm:{path}",
        "revision": revision,
        "dirty": False,
        "patches": [],
    } for path, revision in RECURSIVE_REVISIONS.items())
    return sources


def _write_contract_artifacts(
    output: Path,
    summary: dict[str, Any],
    traces: dict[str, dict[str, Any]],
    build_metadata: dict[str, Any],
    trace_limit: int,
    timeout_seconds: float,
) -> list[dict[str, str]]:
    if not summary.get("firmware"):
        return []
    patch_hashes = summary["source_state"]["patches"]
    public_fingerprints = {
        name: str(value)
        for name, value in summary["firmware"]["public_fingerprints"].items()
    }
    artifacts = []
    comparison_fields = (
        "kind", "label", "time", "address", "width_bits", "endianness", "region",
        "checkpoint", "initial_state", "frames", "host_cycles", "mcu_cycles",
        "dsp1_cycles", "dsp2_cycles", "dsp1_booted", "dsp2_booted",
        "panel_handshake", "midi_ready", "panel_bytes", "panel_tiles",
        "panel_lit_pixels", "factory_cache_ready", "factory_init_expected",
        "flash_dirty", "pc_register", "sp_register",
    )
    for run in summary["runs"]:
        run_id = run["run_id"]
        for label in ("cold_blank_flash", "cached_factory_flash"):
            phase = "cold" if label == "cold_blank_flash" else "cached"
            events = _contract_events(
                traces[run_id]["events_by_label"][label],
                run["checkpoints"],
                label,
            )
            stem = f"{run_id}-{phase}"
            trace_name = f"{stem}.events.jsonl"
            manifest_name = f"{stem}.manifest.json"
            _write_contract_trace(output / trace_name, events)
            initial_state = (
                {
                    "kind": "cold_boot",
                    "description": "Fresh Gearmulator Hardware construction with no caller-supplied flash or factory cache; the model reports factory initialization expected.",
                }
                if phase == "cold" else {
                    "kind": "cached_initialization",
                    "description": "Initialized flash data and factory cache copied from the cold instance in this driver process; the model reports factory initialization not expected.",
                }
            )
            checkpoint = {
                "checkpoint_id": f"md-os163-{phase}-firmware-ready-and-idle-v1",
                "trigger": (
                    "Firmware panel handshake and MIDI readiness become true; "
                    "for cold startup, factory initialization completes and readiness "
                    "persists through one second of no-stimulus idle with host/MCU/DSP clocks advancing."
                    if phase == "cold" else
                    "Firmware panel handshake and MIDI readiness become true from cached initialization; "
                    "readiness persists through one second of no-stimulus idle with host/MCU/DSP clocks advancing."
                ),
                "timeout": {"value": timeout_seconds, "unit": "seconds"},
            }
            manifest = {
                "schema_version": 1,
                "run": {
                    "run_id": f"wp04-{run_id}-{phase}",
                    "scenario_id": f"md-os163-{phase}-startup-v1",
                    "purpose": f"Repeated {phase} Gearmulator startup; JSONL is a redacted MMIO and checkpoint projection with no payload values or PC samples.",
                    "origin": "reference_emulator",
                    "started_at_utc": run["started_at_utc"],
                    "firmware": {
                        "profile_id": summary["firmware"]["profile_id"],
                        "revision": "Machinedrum SPS-1UW OS 1.63",
                        "public_fingerprints": public_fingerprints,
                    },
                    "source_state": _source_state_for_manifest(patch_hashes),
                    "build": build_metadata,
                    "initial_state": initial_state,
                    "clock_domains": {
                        "mcu_cycles": {
                            "unit": "cycles",
                            "origin": "This Hardware instance's MCF5206E cycle counter; reset snapshot is recorded at cycle 4.",
                            "frequency_hz": None,
                        }
                    },
                    "stimuli": [],
                },
                "checkpoint": checkpoint,
                "capture": {
                    "status": "complete",
                    "trace_file": trace_name,
                    "format": "jsonl-v1",
                    "expected_records": None,
                    "recorded_records": len(events),
                    "trace_limit": trace_limit,
                    "dropped_events": 0,
                    "stop_reason": "checkpoint_reached",
                    "record_selection_policy": summary["trace_policy"]["scope"],
                    "raw_trace_values_retained_locally": True,
                },
                "comparison": {
                    "plan_id": f"md-os163-{phase}-event-order-v1",
                    "declared_at_utc": summary["created_at_utc"],
                    "fields": [
                        {"path": field, "mode": "exact"}
                        for field in comparison_fields
                    ],
                },
            }
            (output / manifest_name).write_text(
                json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            artifacts.append({"manifest": manifest_name, "trace": trace_name})
    return artifacts


def capture(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    build_metadata = _load_build_metadata(args.build_metadata)
    output = args.output_dir.expanduser().resolve()
    if output.exists():
        raise ValueError("output directory already exists; choose a new private path")
    if not _ignored_if_in_repository(output):
        raise ValueError("output directory is inside the repository but is not ignored")
    output.mkdir(parents=True)

    summary: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "status": "failed",
        "created_at_utc": _utc_now(),
        "driver_target": "mdPanelReadinessFirmwareTest",
        "timeout_seconds": args.timeout_seconds,
        "trace_limit": args.trace_limit,
        "host": {"system": platform.system(), "machine": platform.machine()},
        "build": build_metadata,
        "firmware": None,
        "source_state": {
            "repository": "gearmulator-md-mm",
            "revision": GEARMULATOR_PIN,
            "recursive_revisions": RECURSIVE_REVISIONS,
            "patches": {
                path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                for path in PATCH_FILES
            },
        },
        "trace_policy": {
            "mode": "full_private" if args.full_private_trace else "summarized",
            "scope": (
                "all SIM/DSP/peripheral reads and writes through firmware readiness"
                if args.full_private_trace else
                "SIM writes except aggregated PPDDR/PPDAT; other MMIO writes and changed-value reads; DSP HI08 writes summarized by instance and core"
            ),
            "sim_reads": "retained" if args.full_private_trace else "filtered",
            "repeated_reads": "retained" if args.full_private_trace else "same address/width/value suppressed",
            "dsp_writes": "raw values local only" if args.full_private_trace else "payload values omitted; per-core count and cycle interval retained",
            "sim_port_writes": "raw values local only" if args.full_private_trace else "PPDDR/PPDAT values omitted; counts and value-transition counts retained",
            "checkpoint_pc": "reset PC/SP are recorded before execution; callback PC samples are omitted from the public summary",
        },
        "runs": [],
        "repeatability": None,
    }

    if not args.driver.is_file() or not os.access(args.driver, os.X_OK):
        summary["failure_reason"] = "driver_missing_or_not_executable"
        _write_summary(output / "summary.json", summary)
        return summary, 2
    try:
        image = inspect_image(args.firmware)
    except OSError:
        summary["failure_reason"] = "firmware_missing_or_unreadable"
        _write_summary(output / "summary.json", summary)
        return summary, 2
    if not all(image[key] for key in (
        "matches_md_os_1_63_size",
        "matches_mame_md_os_1_63_sha1",
        "matches_mame_md_os_1_63_crc32",
        "matches_gearmulator_md_os_1_63_fingerprint",
    )):
        summary["failure_reason"] = "firmware_identity_mismatch"
        _write_summary(output / "summary.json", summary)
        return summary, 3
    summary["firmware"] = _fingerprint_metadata(image)

    for run_id in ("cold-a", "cold-b"):
        run = _run_once(
            args.driver.resolve(),
            args.firmware.resolve(),
            output,
            run_id,
            args.timeout_seconds,
            args.trace_limit,
            args.full_private_trace,
        )
        summary["runs"].append(run)
        if run["status"] != "complete":
            summary["status"] = run["status"]
            summary["failure_reason"] = f"{run_id}:{run['reason']}"
            _write_summary(output / "summary.json", summary)
            return summary, 4 if run["status"] == "incomplete" else 5

    first, second = summary["runs"]
    first_trace = parse_trace(
        output / first["trace_file"], retain_events=not args.full_private_trace
    )
    second_trace = parse_trace(
        output / second["trace_file"], retain_events=not args.full_private_trace
    )
    phases = ("cold_blank_flash", "cached_factory_flash")
    if args.full_private_trace:
        event_order_matches = {
            phase: first_trace["event_counts_by_label"].get(phase)
            == second_trace["event_counts_by_label"].get(phase)
            and first_trace["event_order_sha256"].get(phase)
            == second_trace["event_order_sha256"].get(phase)
            for phase in phases
        }
    else:
        event_order_matches = {
            phase: first_trace["events_by_label"][phase]
            == second_trace["events_by_label"][phase]
            for phase in phases
        }
    checkpoint_metadata_matches = first["checkpoints"] == second["checkpoints"]
    summary["repeatability"] = {
        "cold_boots_use_identical_blank_flash_state": True,
        "cached_starts_are_separately_labeled": True,
        "compared_event_fields": ["machine label", "MCU cycle", "direction", "width", "address"],
        "omitted_event_fields": ["callback PC sample"],
        "payload_values_published": False,
        "event_order_matches": event_order_matches,
        "dsp_write_summaries_match": first["trace"]["dsp_write_summaries"]
        == second["trace"]["dsp_write_summaries"],
        "sim_port_write_summaries_match": first["trace"]["sim_port_write_summaries"]
        == second["trace"]["sim_port_write_summaries"],
        "checkpoint_metadata_matches": checkpoint_metadata_matches,
    }
    if not args.full_private_trace:
        summary["contract_artifacts"] = _write_contract_artifacts(
            output,
            summary,
            {first["run_id"]: first_trace, second["run_id"]: second_trace},
            build_metadata,
            args.trace_limit,
            args.timeout_seconds,
        )
    summary["status"] = "complete"
    _write_summary(output / "summary.json", summary)
    if (
        not all(event_order_matches.values())
        or not summary["repeatability"]["dsp_write_summaries_match"]
        or not summary["repeatability"]["sim_port_write_summaries_match"]
        or not checkpoint_metadata_matches
    ):
        summary["repeatability"]["failure_reason"] = "repeated_runs_diverged"
        _write_summary(output / "summary.json", summary)
        return summary, 1
    return summary, 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--driver", required=True, type=Path, help="built mdPanelReadinessFirmwareTest executable")
    parser.add_argument("--firmware", required=True, type=Path, help="local Machinedrum UW OS 1.63 image")
    parser.add_argument("--output-dir", required=True, type=Path, help="new ignored/local directory for traces and logs")
    parser.add_argument("--build-metadata", required=True, type=Path, help="JSON with the exact build argv and toolchain fields for WP-03 manifests")
    parser.add_argument("--timeout-seconds", type=float, default=180)
    parser.add_argument("--trace-limit", type=int)
    parser.add_argument(
        "--full-private-trace",
        action="store_true",
        help="retain all MMIO values in local trace files; choose a private/ignored output path",
    )
    args = parser.parse_args(argv)
    if args.trace_limit is None:
        args.trace_limit = 12_000_000 if args.full_private_trace else 100_000
    if args.timeout_seconds <= 0 or args.trace_limit <= 0:
        parser.error("timeout and trace limit must be positive")
    try:
        summary, result = capture(args)
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 3
    if result == 0:
        counts = [run["trace"]["recorded_events"] for run in summary["runs"]]
        print(
            "complete: two blank-flash boots and cached restarts; "
            f"trace records={counts}; repeat order matches"
        )
    else:
        print(
            f"{summary['status']}: {summary.get('failure_reason', 'repeatability mismatch')}; "
            f"summary={args.output_dir.resolve() / 'summary.json'}",
            file=sys.stderr,
        )
    return result


if __name__ == "__main__":
    raise SystemExit(main())
