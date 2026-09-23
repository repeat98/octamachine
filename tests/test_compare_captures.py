import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "compare_captures.py"
FIXTURES = ROOT / "tests" / "fixtures" / "wp-03"
sys.path.insert(0, str(ROOT / "scripts"))
from compare_captures import validate_manifest


class CompareCapturesTests(unittest.TestCase):
    def compare(self, candidate_manifest: Path) -> tuple[subprocess.CompletedProcess[str], dict]:
        process = subprocess.run(
            [sys.executable, str(SCRIPT), str(FIXTURES / "reference.json"), str(candidate_manifest)],
            check=False,
            capture_output=True,
            text=True,
        )
        return process, json.loads(process.stdout)

    def temporary_candidate(
        self,
        capture_changes: dict | None = None,
        event_lines: list[str] | None = None,
        terminated: bool = True,
    ) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        directory = Path(temp_dir.name)
        manifest = json.loads((FIXTURES / "candidate.json").read_text(encoding="utf-8"))
        manifest["capture"]["trace_file"] = "candidate.events.jsonl"
        if capture_changes:
            manifest["capture"].update(capture_changes)
        (directory / "candidate.json").write_text(json.dumps(manifest), encoding="utf-8")
        if event_lines is None:
            event_lines = (FIXTURES / "candidate.events.jsonl").read_text(encoding="utf-8").splitlines()
        if manifest["capture"]["status"] != "failed":
            text = "\n".join(event_lines) + ("\n" if terminated else "")
            (directory / "candidate.events.jsonl").write_text(text, encoding="utf-8")
        return directory / "candidate.json"

    def test_equivalent_values_within_declared_tolerance(self) -> None:
        process = subprocess.run(
            [sys.executable, str(SCRIPT), str(FIXTURES / "reference.json"), str(FIXTURES / "candidate.json")],
            check=False,
            capture_output=True,
            text=True,
        )
        result = json.loads(process.stdout)
        self.assertEqual(process.returncode, 0)
        self.assertEqual(result["result"], "equivalent")
        self.assertEqual(result["events_compared"], 3)
        self.assertIsNone(result["first_divergence"])

    def test_all_initial_state_modes_are_valid_and_distinct(self) -> None:
        modes = {"cold_boot", "warm_restart", "cached_initialization", "restored_state"}
        manifest = json.loads((FIXTURES / "reference.json").read_text(encoding="utf-8"))
        for mode in modes:
            with self.subTest(mode=mode):
                manifest["run"]["initial_state"]["kind"] = mode
                validate_manifest(manifest, "synthetic")

    def test_divergence_reports_first_event_and_field(self) -> None:
        lines = (FIXTURES / "candidate.events.jsonl").read_text(encoding="utf-8").splitlines()
        event = json.loads(lines[1])
        event["value"] = 2.3
        lines[1] = json.dumps(event, separators=(",", ":"))
        process, result = self.compare(self.temporary_candidate(event_lines=lines))
        self.assertEqual(process.returncode, 1)
        self.assertEqual(result["result"], "divergent")
        self.assertEqual(result["first_divergence"]["event_index"], 1)
        self.assertEqual(result["first_divergence"]["field"], "value")

    def test_missing_trace_is_not_a_pass(self) -> None:
        process, result = self.compare(self.temporary_candidate({"trace_file": "absent.events.jsonl"}))
        self.assertEqual(process.returncode, 2)
        self.assertEqual(result["result"], "missing_input")

    def test_truncated_trace_is_incomplete(self) -> None:
        lines = (FIXTURES / "candidate.events.jsonl").read_text(encoding="utf-8").splitlines()
        incomplete = lines[:2] + ['{"sequence":2']
        process, result = self.compare(
            self.temporary_candidate(
                {
                    "status": "incomplete",
                    "expected_records": 3,
                    "recorded_records": 2,
                    "trace_limit": 3,
                    "dropped_events": 1,
                    "stop_reason": "output_error",
                },
                event_lines=incomplete,
                terminated=False,
            )
        )
        self.assertEqual(process.returncode, 4)
        self.assertEqual(result["result"], "incomplete_trace")

    def test_trace_cap_is_incomplete(self) -> None:
        process, result = self.compare(
            self.temporary_candidate(
                {
                    "status": "incomplete",
                    "expected_records": 4,
                    "recorded_records": 3,
                    "trace_limit": 3,
                    "dropped_events": 1,
                    "stop_reason": "trace_limit",
                }
            )
        )
        self.assertEqual(process.returncode, 4)
        self.assertEqual(result["result"], "incomplete_trace")

    def test_failed_capture_has_distinct_outcome(self) -> None:
        process, result = self.compare(
            self.temporary_candidate({"status": "failed", "failure_reason": "synthetic_launch_error"})
        )
        self.assertEqual(process.returncode, 5)
        self.assertEqual(result["result"], "capture_failed")

    def test_missing_manifest_is_distinct_from_invalid_manifest(self) -> None:
        missing = FIXTURES / "does-not-exist.json"
        process = subprocess.run(
            [sys.executable, str(SCRIPT), str(FIXTURES / "reference.json"), str(missing)],
            check=False,
            capture_output=True,
            text=True,
        )
        result = json.loads(process.stdout)
        self.assertEqual(process.returncode, 2)
        self.assertEqual(result["result"], "missing_input")

    def test_duplicate_manifest_key_is_invalid_input(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        invalid_manifest = Path(temp_dir.name) / "duplicate.json"
        invalid_manifest.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        process = subprocess.run(
            [sys.executable, str(SCRIPT), str(FIXTURES / "reference.json"), str(invalid_manifest)],
            check=False,
            capture_output=True,
            text=True,
        )
        result = json.loads(process.stdout)
        self.assertEqual(process.returncode, 3)
        self.assertEqual(result["result"], "invalid_input")

    def test_real_firmware_profile_requires_public_identity(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        directory = Path(temp_dir.name)
        manifest = json.loads((FIXTURES / "candidate.json").read_text(encoding="utf-8"))
        manifest["run"]["origin"] = "reference_emulator"
        manifest["run"]["firmware"]["profile_id"] = "machinedrum-sps1uw-os1.63"
        manifest["run"]["firmware"]["revision"] = "1.63"
        candidate_manifest = directory / "candidate.json"
        candidate_manifest.write_text(json.dumps(manifest), encoding="utf-8")
        process, result = self.compare(candidate_manifest)
        self.assertEqual(process.returncode, 3)
        self.assertEqual(result["result"], "invalid_input")


if __name__ == "__main__":
    unittest.main()
