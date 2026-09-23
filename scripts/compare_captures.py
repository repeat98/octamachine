#!/usr/bin/env python3
"""Validate and compare two version-1 octamachine capture manifests."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any


EXIT_CODES = {
    "equivalent": 0,
    "divergent": 1,
    "missing_input": 2,
    "invalid_input": 3,
    "incomplete_trace": 4,
    "capture_failed": 5,
}

INITIAL_STATES = {"cold_boot", "warm_restart", "cached_initialization", "restored_state"}
ORIGINS = {"reference_emulator", "stock_target_emulator", "port_candidate", "physical_board", "synthetic"}
PC_SEMANTICS = {"current_instruction", "next_instruction", "faulting_instruction", "return_address", "not_applicable"}
COMPLETE_REASONS = {"checkpoint_reached", "normal_exit"}
INCOMPLETE_REASONS = {"timeout", "trace_limit", "user_stop", "device_error", "output_error", "process_exit"}
FIELD_PATH = re.compile(r"^[A-Za-z0-9_.-]+$")


class OutcomeError(Exception):
    def __init__(self, result: str, message: str, **details: Any) -> None:
        super().__init__(message)
        self.result = result
        self.details = details


def invalid(message: str, **details: Any) -> OutcomeError:
    return OutcomeError("invalid_input", message, **details)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise invalid(message)


def is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def reject_json_constant(value: str) -> None:
    raise ValueError(f"non-standard JSON number: {value}")


def parse_utc(value: Any, field: str) -> datetime:
    require(isinstance(value, str) and bool(value), f"{field} must be an ISO-8601 UTC timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise invalid(f"{field} is not a valid ISO-8601 timestamp") from exc
    require(parsed.tzinfo is not None, f"{field} must include a timezone")
    require(parsed.utcoffset() == timezone.utc.utcoffset(parsed), f"{field} must be UTC")
    return parsed


def read_json(path: Path, label: str) -> dict[str, Any]:
    if not path.is_file():
        raise OutcomeError("missing_input", f"{label} manifest is missing", input=label)
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_json_object, parse_constant=reject_json_constant)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise invalid(f"{label} manifest is unreadable, invalid JSON, or contains duplicate keys", input=label) from exc
    require(isinstance(value, dict), f"{label} manifest must contain a JSON object")
    return value


def validate_manifest(manifest: dict[str, Any], label: str) -> None:
    version = manifest.get("schema_version")
    require(isinstance(version, int) and not isinstance(version, bool) and version == 1, f"{label} manifest schema_version must be 1")
    run = manifest.get("run")
    require(isinstance(run, dict), f"{label} manifest must contain run metadata")
    for key in ("run_id", "scenario_id", "purpose"):
        require(isinstance(run.get(key), str) and bool(run[key]), f"{label} run.{key} is required")
    require(isinstance(run.get("origin"), str) and run["origin"] in ORIGINS, f"{label} run.origin is not a supported origin")
    parse_utc(run.get("started_at_utc"), f"{label} run.started_at_utc")

    firmware = run.get("firmware")
    require(isinstance(firmware, dict), f"{label} run.firmware is required")
    for key in ("profile_id", "revision"):
        require(isinstance(firmware.get(key), str) and bool(firmware[key]), f"{label} firmware.{key} is required")
    fingerprints = firmware.get("public_fingerprints")
    require(isinstance(fingerprints, dict), f"{label} firmware.public_fingerprints must be an object")
    require(all(isinstance(key, str) and bool(key) and isinstance(value, str) and bool(value) for key, value in fingerprints.items()), f"{label} firmware fingerprints must be named strings")

    sources = run.get("source_state")
    require(isinstance(sources, list) and bool(sources), f"{label} run.source_state must be a non-empty list")
    for index, source in enumerate(sources):
        require(isinstance(source, dict), f"{label} source_state[{index}] must be an object")
        for key in ("repository", "revision"):
            require(isinstance(source.get(key), str) and bool(source[key]), f"{label} source_state[{index}].{key} is required")
        require(isinstance(source.get("dirty"), bool), f"{label} source_state[{index}].dirty must be boolean")
        patches = source.get("patches")
        require(isinstance(patches, list), f"{label} source_state[{index}].patches must be a list")
        for patch in patches:
            require(isinstance(patch, dict) and isinstance(patch.get("id"), str), f"{label} patch records need an id")
            require(isinstance(patch.get("sha256"), str) and bool(patch["sha256"]), f"{label} patch records need a SHA-256 digest")

    build = run.get("build")
    require(isinstance(build, dict), f"{label} run.build is required")
    require(isinstance(build.get("command"), list) and all(isinstance(part, str) for part in build["command"]), f"{label} build.command must be an argv list")
    require(isinstance(build.get("toolchain"), dict), f"{label} build.toolchain must be an object")

    initial = run.get("initial_state")
    require(isinstance(initial, dict) and isinstance(initial.get("kind"), str) and initial["kind"] in INITIAL_STATES, f"{label} initial_state.kind is unsupported")
    require(isinstance(initial.get("description"), str) and bool(initial["description"]), f"{label} initial_state.description is required")

    clocks = run.get("clock_domains")
    require(isinstance(clocks, dict) and bool(clocks), f"{label} run.clock_domains must be a non-empty object")
    for clock_id, clock in clocks.items():
        require(isinstance(clock_id, str) and bool(clock_id) and isinstance(clock, dict), f"{label} clock domains need named objects")
        require(isinstance(clock.get("unit"), str) and bool(clock["unit"]), f"{label} clock {clock_id}.unit is required")
        require(isinstance(clock.get("origin"), str) and bool(clock["origin"]), f"{label} clock {clock_id}.origin is required")
        frequency = clock.get("frequency_hz")
        require(frequency is None or (is_number(frequency) and frequency > 0), f"{label} clock {clock_id}.frequency_hz must be positive or null")

    stimuli = run.get("stimuli")
    require(isinstance(stimuli, list), f"{label} run.stimuli must be a list")
    last_times: dict[str, float] = {}
    for index, stimulus in enumerate(stimuli):
        sequence = stimulus.get("sequence") if isinstance(stimulus, dict) else None
        require(isinstance(stimulus, dict) and isinstance(sequence, int) and not isinstance(sequence, bool) and sequence == index, f"{label} stimuli must have contiguous sequence numbers")
        for key in ("stimulus_id", "kind"):
            require(isinstance(stimulus.get(key), str) and bool(stimulus[key]), f"{label} stimuli[{index}].{key} is required")
        at = stimulus.get("at")
        require(isinstance(at, dict), f"{label} stimuli[{index}].at is required")
        clock_id = at.get("clock_id")
        value = at.get("value")
        require(isinstance(clock_id, str) and clock_id in clocks and is_number(value) and value >= 0, f"{label} stimuli[{index}] has an unknown clock or invalid time")
        require(value >= last_times.get(clock_id, -math.inf), f"{label} stimulus time moved backwards in clock {clock_id}")
        last_times[clock_id] = value
        require(isinstance(stimulus.get("parameters", {}), dict), f"{label} stimuli[{index}].parameters must be an object")

    checkpoint = manifest.get("checkpoint")
    require(isinstance(checkpoint, dict), f"{label} checkpoint metadata is required")
    for key in ("checkpoint_id", "trigger"):
        require(isinstance(checkpoint.get(key), str) and bool(checkpoint[key]), f"{label} checkpoint.{key} is required")
    timeout = checkpoint.get("timeout")
    require(isinstance(timeout, dict) and is_number(timeout.get("value")) and timeout["value"] > 0, f"{label} checkpoint.timeout must be positive")
    require(isinstance(timeout.get("unit"), str) and bool(timeout["unit"]), f"{label} checkpoint.timeout.unit is required")

    capture = manifest.get("capture")
    require(isinstance(capture, dict), f"{label} capture metadata is required")
    status = capture.get("status")
    require(isinstance(status, str) and status in {"complete", "incomplete", "failed"}, f"{label} capture.status is unsupported")
    if firmware["profile_id"] == "synthetic-no-firmware":
        require(run["origin"] == "synthetic" and not fingerprints, f"{label} synthetic-no-firmware profile is only valid for a synthetic run")
    elif status != "failed":
        require(bool(fingerprints), f"{label} firmware profile needs at least one approved public fingerprint")
    if status == "failed":
        require(isinstance(capture.get("failure_reason"), str) and bool(capture["failure_reason"]), f"{label} failed capture needs failure_reason")
    else:
        require(capture.get("format") == "jsonl-v1", f"{label} capture.format must be jsonl-v1")
        require(isinstance(capture.get("trace_file"), str) and bool(capture["trace_file"]), f"{label} capture.trace_file is required")
        for key in ("recorded_records", "dropped_events"):
            require(isinstance(capture.get(key), int) and not isinstance(capture[key], bool) and capture[key] >= 0, f"{label} capture.{key} must be a non-negative integer")
        expected = capture.get("expected_records")
        require(expected is None or (isinstance(expected, int) and not isinstance(expected, bool) and expected >= 0), f"{label} capture.expected_records must be non-negative or null")
        limit = capture.get("trace_limit")
        require(limit is None or (isinstance(limit, int) and not isinstance(limit, bool) and limit > 0), f"{label} capture.trace_limit must be positive or null")
        reason = capture.get("stop_reason")
        require(isinstance(reason, str), f"{label} capture.stop_reason is required")
        if status == "complete":
            require(reason in COMPLETE_REASONS, f"{label} complete capture needs a completion stop_reason")
            require(capture["dropped_events"] == 0, f"{label} complete capture cannot report dropped events")
            require(expected is None or expected == capture["recorded_records"], f"{label} complete capture count does not match expected_records")
            require(limit is None or capture["recorded_records"] < limit, f"{label} capture reached its trace_limit but is marked complete")
        else:
            require(reason in INCOMPLETE_REASONS, f"{label} incomplete capture needs an incomplete stop_reason")
            require(expected is None or capture["recorded_records"] <= expected, f"{label} incomplete capture has more records than expected")
            require(reason != "trace_limit" or (limit is not None and capture["recorded_records"] >= limit), f"{label} trace_limit stop needs a reached limit")

    comparison = manifest.get("comparison")
    require(isinstance(comparison, dict), f"{label} comparison plan is required")
    require(isinstance(comparison.get("plan_id"), str) and bool(comparison["plan_id"]), f"{label} comparison.plan_id is required")
    parse_utc(comparison.get("declared_at_utc"), f"{label} comparison.declared_at_utc")
    rules = comparison.get("fields")
    require(isinstance(rules, list) and bool(rules), f"{label} comparison.fields must be a non-empty list")
    seen_paths: set[str] = set()
    for rule in rules:
        require(isinstance(rule, dict), f"{label} comparison field rules must be objects")
        path = rule.get("path")
        require(isinstance(path, str) and bool(FIELD_PATH.fullmatch(path)), f"{label} comparison field path is invalid")
        require(path not in seen_paths, f"{label} comparison path {path} is repeated")
        seen_paths.add(path)
        mode = rule.get("mode")
        if mode == "exact":
            require("tolerance" not in rule, f"{label} exact field {path} cannot have a tolerance")
        elif mode == "absolute_tolerance":
            tolerance = rule.get("tolerance")
            require(is_number(tolerance) and tolerance >= 0, f"{label} field {path} needs a non-negative absolute tolerance")
            require(isinstance(rule.get("unit"), str) and bool(rule["unit"]), f"{label} field {path} needs a tolerance unit")
        else:
            raise invalid(f"{label} comparison field {path} has unsupported mode")


def resolve_event_path(event: dict[str, Any], path: str) -> Any:
    value: Any = event
    for segment in path.split("."):
        if isinstance(value, dict) and segment in value:
            value = value[segment]
        elif isinstance(value, list) and segment.isdigit() and int(segment) < len(value):
            value = value[int(segment)]
        else:
            raise invalid(f"comparison field {path} is missing from an event")
    return value


def trace_path(manifest_path: Path, capture: dict[str, Any], label: str) -> Path:
    relative = PurePosixPath(capture["trace_file"])
    require(not relative.is_absolute() and ".." not in relative.parts and "\\" not in capture["trace_file"], f"{label} trace_file must stay inside the manifest directory")
    return manifest_path.parent.joinpath(*relative.parts)


def validate_event(event: Any, expected_sequence: int, clocks: dict[str, Any], label: str) -> dict[str, Any]:
    require(isinstance(event, dict), f"{label} event {expected_sequence} must be an object")
    sequence = event.get("sequence")
    require(isinstance(sequence, int) and not isinstance(sequence, bool) and sequence == expected_sequence, f"{label} event sequence must be contiguous from zero")
    require(isinstance(event.get("kind"), str) and bool(event["kind"]), f"{label} event {expected_sequence}.kind is required")
    clock_id = event.get("clock_id")
    require(isinstance(clock_id, str) and clock_id in clocks, f"{label} event {expected_sequence} has an unknown clock_id")
    require(is_number(event.get("time")) and event["time"] >= 0, f"{label} event {expected_sequence}.time must be non-negative")
    if "pc" in event:
        pc = event["pc"]
        require(isinstance(pc, dict) and "value" in pc, f"{label} event {expected_sequence}.pc needs a value")
        require(isinstance(pc.get("semantics"), str) and pc["semantics"] in PC_SEMANTICS, f"{label} event {expected_sequence}.pc needs explicit semantics")
    if event["kind"] in {"mmio_read", "mmio_write"}:
        width = event.get("width_bits")
        require(isinstance(width, int) and not isinstance(width, bool) and width > 0, f"{label} MMIO event {expected_sequence} needs width_bits")
        require(event.get("endianness") in {"big", "little"}, f"{label} MMIO event {expected_sequence} needs endianness")
    return event


def load_events(manifest_path: Path, manifest: dict[str, Any], label: str) -> tuple[list[dict[str, Any]], bool]:
    capture = manifest["capture"]
    path = trace_path(manifest_path, capture, label)
    if not path.is_file():
        raise OutcomeError("missing_input", f"{label} trace file is missing", input=label, trace_file=capture["trace_file"])
    try:
        raw = path.read_bytes()
        text = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise invalid(f"{label} trace is not readable UTF-8", input=label) from exc

    terminated = not raw or raw.endswith(b"\n")
    lines = text.splitlines()
    events: list[dict[str, Any]] = []
    partial_final_record = False
    clocks = manifest["run"]["clock_domains"]
    last_times: dict[str, float] = {}
    for index, line in enumerate(lines):
        if not line.strip():
            raise invalid(f"{label} trace contains a blank JSONL record", record=index + 1)
        try:
            raw_event = json.loads(line, object_pairs_hook=unique_json_object, parse_constant=reject_json_constant)
        except json.JSONDecodeError as exc:
            if index == len(lines) - 1 and not terminated:
                partial_final_record = True
                break
            raise invalid(f"{label} trace has invalid JSONL", record=index + 1) from exc
        except ValueError as exc:
            raise invalid(f"{label} trace record has duplicate keys or a non-standard JSON number", record=index + 1) from exc
        event = validate_event(raw_event, len(events), clocks, label)
        clock_id = event["clock_id"]
        require(event["time"] >= last_times.get(clock_id, -math.inf), f"{label} event time moved backwards in clock {clock_id}")
        last_times[clock_id] = event["time"]
        events.append(event)

    if len(events) != capture["recorded_records"]:
        if partial_final_record and len(events) < capture["recorded_records"]:
            return events, True
        raise invalid(f"{label} recorded_records does not match the complete JSONL records")
    truncated = partial_final_record or (not terminated and bool(raw))
    if capture["status"] == "complete" and truncated:
        return events, True
    return events, truncated or capture["status"] == "incomplete"


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def base_result(reference: dict[str, Any], candidate: dict[str, Any]) -> dict[str, Any]:
    ref_run = reference["run"]
    candidate_run = candidate["run"]
    return {
        "schema_version": 1,
        "result": "",
        "reference_run_id": ref_run["run_id"],
        "candidate_run_id": candidate_run["run_id"],
        "scenario_id": ref_run["scenario_id"],
        "checkpoint_id": reference["checkpoint"]["checkpoint_id"],
        "reference_origin": ref_run["origin"],
        "candidate_origin": candidate_run["origin"],
        "reference_firmware_profile": ref_run["firmware"]["profile_id"],
        "candidate_firmware_profile": candidate_run["firmware"]["profile_id"],
        "comparison_plan_id": reference["comparison"]["plan_id"],
        "comparison_plan_declared_at_utc": {
            "reference": reference["comparison"]["declared_at_utc"],
            "candidate": candidate["comparison"]["declared_at_utc"],
        },
        "events_compared": 0,
        "first_divergence": None,
    }


def compare_manifests(reference_path: Path, candidate_path: Path) -> tuple[dict[str, Any], int]:
    reference = read_json(reference_path, "reference")
    candidate = read_json(candidate_path, "candidate")
    validate_manifest(reference, "reference")
    validate_manifest(candidate, "candidate")
    result = base_result(reference, candidate)
    ref_run = reference["run"]
    candidate_run = candidate["run"]

    require(ref_run["scenario_id"] == candidate_run["scenario_id"], "captures have different scenario_id values")
    require(ref_run["initial_state"]["kind"] == candidate_run["initial_state"]["kind"], "captures use different initial-state modes")
    require(canonical(ref_run["stimuli"]) == canonical(candidate_run["stimuli"]), "captures do not use the same declared stimulus sequence")
    for index, stimulus in enumerate(ref_run["stimuli"]):
        clock_id = stimulus["at"]["clock_id"]
        require(canonical(ref_run["clock_domains"][clock_id]) == canonical(candidate_run["clock_domains"][clock_id]), f"stimulus {index} uses different clock definitions")
    require(canonical(reference["checkpoint"]) == canonical(candidate["checkpoint"]), "captures use different checkpoint definitions")
    ref_plan = reference["comparison"]
    candidate_plan = candidate["comparison"]
    require(ref_plan["plan_id"] == candidate_plan["plan_id"] and canonical(ref_plan["fields"]) == canonical(candidate_plan["fields"]), "captures do not use the same comparison plan")

    for label, manifest in (("reference", reference), ("candidate", candidate)):
        if manifest["capture"]["status"] == "failed":
            result.update({"result": "capture_failed", "detail": f"{label} capture failed: {manifest['capture']['failure_reason']}"})
            return result, EXIT_CODES["capture_failed"]

    ref_events, ref_incomplete = load_events(reference_path, reference, "reference")
    candidate_events, candidate_incomplete = load_events(candidate_path, candidate, "candidate")
    if ref_incomplete or candidate_incomplete:
        result.update({"result": "incomplete_trace", "detail": "at least one capture is incomplete or has an unterminated/truncated final record"})
        return result, EXIT_CODES["incomplete_trace"]

    compare_time = any(rule["path"] == "time" for rule in ref_plan["fields"])
    if compare_time:
        time_rule = next(rule for rule in ref_plan["fields"] if rule["path"] == "time")
        for index, (ref_event, candidate_event) in enumerate(zip(ref_events, candidate_events)):
            ref_clock_id = ref_event["clock_id"]
            candidate_clock_id = candidate_event["clock_id"]
            require(ref_clock_id == candidate_clock_id, f"event {index} compares time values from different clock domains")
            clock = ref_run["clock_domains"][ref_clock_id]
            require(canonical(clock) == canonical(candidate_run["clock_domains"][candidate_clock_id]), f"event {index} compares time values with different clock definitions")
            if time_rule["mode"] == "absolute_tolerance":
                require(time_rule["unit"] == clock["unit"], f"event {index} time tolerance unit does not match its clock")

    for index, (ref_event, candidate_event) in enumerate(zip(ref_events, candidate_events)):
        for rule in ref_plan["fields"]:
            path = rule["path"]
            ref_value = resolve_event_path(ref_event, path)
            candidate_value = resolve_event_path(candidate_event, path)
            equal = ref_value == candidate_value
            divergence: dict[str, Any] = {
                "event_index": index,
                "sequence": ref_event["sequence"],
                "field": path,
                "reference": ref_value,
                "candidate": candidate_value,
            }
            if rule["mode"] == "absolute_tolerance":
                require(is_number(ref_value) and is_number(candidate_value), f"comparison field {path} must be numeric for absolute_tolerance")
                difference = abs(float(ref_value) - float(candidate_value))
                equal = difference <= rule["tolerance"]
                divergence["absolute_difference"] = difference
                divergence["tolerance"] = rule["tolerance"]
                divergence["tolerance_unit"] = rule["unit"]
            if not equal:
                result.update({"result": "divergent", "events_compared": index + 1, "first_divergence": divergence})
                return result, EXIT_CODES["divergent"]

    result["events_compared"] = min(len(ref_events), len(candidate_events))
    if len(ref_events) != len(candidate_events):
        index = min(len(ref_events), len(candidate_events))
        result.update({
            "result": "divergent",
            "first_divergence": {
                "event_index": index,
                "sequence": index,
                "field": "event_count",
                "reference": len(ref_events),
                "candidate": len(candidate_events),
            },
        })
        return result, EXIT_CODES["divergent"]

    result["result"] = "equivalent"
    result["detail"] = "all declared fields matched for every event"
    return result, EXIT_CODES["equivalent"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("reference", type=Path, help="reference capture manifest JSON")
    parser.add_argument("candidate", type=Path, help="candidate capture manifest JSON")
    args = parser.parse_args(argv)

    try:
        result, exit_code = compare_manifests(args.reference, args.candidate)
    except OutcomeError as exc:
        result = {"schema_version": 1, "result": exc.result, "detail": str(exc)}
        result.update(exc.details)
        exit_code = EXIT_CODES[exc.result]
    except OSError as exc:
        result = {"schema_version": 1, "result": "invalid_input", "detail": f"I/O error: {exc}"}
        exit_code = EXIT_CODES["invalid_input"]

    result["compared_at_utc"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    print(json.dumps(result, indent=2, sort_keys=True))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
