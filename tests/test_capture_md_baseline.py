import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from capture_md_baseline import (
    EXPECTED_CHECKPOINTS,
    _contract_events,
    parse_checkpoint,
    parse_trace,
    validate_checkpoints,
    validate_trace,
)


class MachinedrumBaselineCaptureTests(unittest.TestCase):
    def _trace(self, truncated=False):
        lines = [
            "mdbus instance=1 label=cold_blank_flash cycle=100 pc=00000010 W1 addr=00300003 value=deadbeef",
            "mdbus instance=2 label=cached_factory_flash cycle=100 pc=00000010 W1 addr=00300003 value=cafebabe",
        ]
        if truncated:
            lines.append("mdbus trace truncated at configured event limit")
        status = "truncated" if truncated else "complete"
        lines.extend([
            f"mdbus summary recorded=2 observed=20 repeat_reads_suppressed=3 sim_reads_filtered=4 dsp_writes_aggregated=true sim_port_writes_aggregated=true instances=2 status={status} read_filter=changed_values",
            "mdbus dsp_write_summary instance=1 label=cold_blank_flash dsp=1 count=5 first_cycle=110 last_cycle=120",
            "mdbus dsp_write_summary instance=1 label=cold_blank_flash dsp=2 count=6 first_cycle=111 last_cycle=121",
            "mdbus dsp_write_summary instance=2 label=cached_factory_flash dsp=1 count=5 first_cycle=110 last_cycle=120",
            "mdbus dsp_write_summary instance=2 label=cached_factory_flash dsp=2 count=6 first_cycle=111 last_cycle=121",
            "mdbus sim_port_write_summary instance=1 label=cold_blank_flash data_writes=8 data_transitions=4 direction_writes=9 direction_transitions=2 first_cycle=100 last_cycle=130",
            "mdbus sim_port_write_summary instance=2 label=cached_factory_flash data_writes=8 data_transitions=4 direction_writes=9 direction_transitions=2 first_cycle=100 last_cycle=130",
        ])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "trace.txt"
            path.write_text("\n".join(lines) + "\n")
            return parse_trace(path)

    def _full_trace(self):
        lines = [
            "mdbus instance=1 label=cold_blank_flash cycle=100 pc=00000010 W2 addr=00500004 value=deadbeef",
            "mdbus instance=1 label=cold_blank_flash cycle=101 pc=00000010 W2 addr=00600004 value=cafebabe",
            "mdbus instance=2 label=cached_factory_flash cycle=100 pc=00000010 W2 addr=00500004 value=deadbeef",
            "mdbus instance=2 label=cached_factory_flash cycle=101 pc=00000010 W2 addr=00600004 value=cafebabe",
            "mdbus summary recorded=4 observed=4 repeat_reads_suppressed=0 sim_reads_filtered=0 dsp_writes_aggregated=false sim_port_writes_aggregated=false instances=2 status=complete read_filter=all",
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "full-trace.txt"
            path.write_text("\n".join(lines) + "\n")
            return parse_trace(path, retain_events=False)

    def _checkpoints(self):
        result = []
        for name in EXPECTED_CHECKPOINTS:
            cold = name.startswith("cold_")
            reset = name.endswith("reset")
            boot1 = name.endswith("dsp1_booted")
            boot2 = name.endswith("dsp2_booted")
            ready = name.endswith("firmware_ready") or name in {"cold_initialized", "cold_idle_no_stimulus", "cached_ready", "cached_idle_no_stimulus"}
            result.append({
                "schema": "1",
                "checkpoint": name,
                "initial_state": "blank_flash" if cold else "factory_flash_cache",
                "frames": 0 if reset else 128,
                "pc_register": 12 if reset else 1000,
                "sp_register": 0 if reset else 2000,
                "host_cycles": 100 if name.endswith("idle_no_stimulus") else 10,
                "mcu_cycles": 110 if name.endswith("idle_no_stimulus") else 10,
                "dsp1_cycles": 120 if name.endswith("idle_no_stimulus") else 10,
                "dsp2_cycles": 130 if name.endswith("idle_no_stimulus") else 10,
                "dsp1_booted": boot1 or ready or name.endswith("idle_no_stimulus"),
                "dsp2_booted": boot2 or ready or name.endswith("idle_no_stimulus"),
                "panel_handshake": ready or name.endswith("idle_no_stimulus"),
                "midi_ready": ready or name.endswith("idle_no_stimulus"),
                "panel_bytes": 20_000 if ready else 0,
                "panel_tiles": 1_000 if ready else 0,
                "panel_lit_pixels": 500 if ready else 0,
                "factory_cache_ready": cold and name != "cold_reset" or not cold,
                "factory_init_expected": name == "cold_reset",
                "flash_dirty": name in {"cold_initialized", "cold_idle_no_stimulus", "cached_ready", "cached_idle_no_stimulus"},
            })
        return result

    def test_trace_parser_omits_payload_and_pc(self):
        trace = self._trace()
        self.assertEqual(trace["status"], "complete")
        safe = json.dumps(trace["events_by_label"])
        self.assertNotIn("deadbeef", safe)
        self.assertNotIn("cafebabe", safe)
        self.assertNotIn("value", safe)
        self.assertNotIn("pc", safe)
        self.assertNotIn("address", safe)
        self.assertEqual(validate_trace(trace), [])

    def test_trace_cap_is_incomplete(self):
        trace = self._trace(truncated=True)
        self.assertTrue(trace["truncated"])
        self.assertEqual(trace["status"], "incomplete")
        self.assertIn("trace_not_complete", validate_trace(trace))

    def test_full_private_trace_streams_counts_and_dsp_regions(self):
        trace = self._full_trace()
        self.assertEqual(trace["status"], "complete")
        self.assertEqual(trace["recorded_events"], 4)
        self.assertEqual(trace["events_by_label"]["cold_blank_flash"], [])
        safe = json.dumps(trace)
        self.assertNotIn("deadbeef", safe)
        self.assertNotIn("cafebabe", safe)
        self.assertNotIn("value", safe)
        self.assertNotIn("pc", safe)
        self.assertEqual(validate_trace(trace, full_private=True), [])

    def test_contract_projection_is_ordered_and_omits_values_and_pc(self):
        checkpoint = {
            "checkpoint": "cold_reset",
            "initial_state": "blank_flash",
            "mcu_cycles": 4,
            "pc_register": 12,
            "sp_register": 0,
        }
        events = _contract_events(
            [(10, "W", 16, 0x00500004, "DSP1_HDI08")],
            [checkpoint],
            "cold_blank_flash",
        )
        self.assertEqual([event["kind"] for event in events], ["checkpoint", "mmio_write"])
        self.assertEqual(events[1]["address"], "0x00500004")
        safe = json.dumps(events)
        self.assertNotIn('"value":', safe)
        self.assertNotIn('"pc":', safe)

    def test_checkpoint_parser_keeps_typed_summary_fields(self):
        line = (
            "MDCP schema=1 checkpoint=cold_reset initial_state=blank_flash "
            "frames=0 pc_register=12 sp_register=0 host_cycles=0 mcu_cycles=4 "
            "dsp1_cycles=0 dsp2_cycles=0 dsp1_booted=0 dsp2_booted=0 "
            "panel_handshake=0 midi_ready=0 panel_bytes=0 panel_tiles=0 "
            "panel_lit_pixels=0 factory_cache_ready=0 factory_init_expected=1 "
            "flash_dirty=0"
        )
        checkpoint = parse_checkpoint(line)
        self.assertEqual(checkpoint["pc_register"], 12)
        self.assertEqual(checkpoint["sp_register"], 0)
        self.assertFalse(checkpoint["dsp1_booted"])
        self.assertTrue(checkpoint["factory_init_expected"])

    def test_checkpoint_validation_requires_scheduler_progress(self):
        checkpoints = self._checkpoints()
        self.assertEqual(validate_checkpoints(checkpoints), [])
        cold_init = next(item for item in checkpoints if item["checkpoint"] == "cold_initialized")
        cold_idle = next(item for item in checkpoints if item["checkpoint"] == "cold_idle_no_stimulus")
        cold_idle["dsp2_cycles"] = cold_init["dsp2_cycles"]
        self.assertIn(
            "idle_clock_did_not_advance:cold:dsp2_cycles",
            validate_checkpoints(checkpoints),
        )


if __name__ == "__main__":
    unittest.main()
