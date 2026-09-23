import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "md_reference"))
from md_extract import dsp_map, dsp_records


def image(words: list[int]) -> bytes:
    """A synthetic DSP load image: little-endian 24-bit words."""
    return b"".join(w.to_bytes(3, "little") for w in words)


HEADER = [3, 0x24, 4, 0]
TRAILER = [3, 0x24]


class DspLoadImageTests(unittest.TestCase):
    """Synthetic words only; no firmware is read."""

    def parse(self, words: list[int]):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "synthetic.bin"
            path.write_bytes(image(words))
            return dsp_records(path)

    def test_records_and_contiguous_runs(self):
        recs = self.parse(HEADER
                          + [0, 0x100, 2, 0xAAAAAA, 0xBBBBBB]
                          + [0, 0x102, 1, 0xCCCCCC]
                          + [1, 0x40, 1, 0x123456]
                          + [2, 0x800, 3, 1, 2, 3]
                          + TRAILER)
        self.assertEqual(recs, [
            (0, 0x100, [0xAAAAAA, 0xBBBBBB]),
            (0, 0x102, [0xCCCCCC]),
            (1, 0x40, [0x123456]),
            (2, 0x800, [1, 2, 3]),
        ])
        self.assertEqual(dsp_map(recs), [
            {"space": "P", "start": 0x100, "end": 0x102, "words": 3},
            {"space": "X", "start": 0x40, "end": 0x40, "words": 1},
            {"space": "Y", "start": 0x800, "end": 0x802, "words": 3},
        ])

    def test_truncated_record_is_refused(self):
        with self.assertRaises(SystemExit):
            self.parse(HEADER + [0, 0x100, 4, 1, 2])

    def test_missing_trailer_is_refused(self):
        with self.assertRaises(SystemExit):
            self.parse(HEADER + [0, 0x100, 1, 7])

    def test_wrong_header_is_refused(self):
        with self.assertRaises(SystemExit):
            self.parse([3, 0x24, 5, 0] + [0, 0x100, 1, 7] + TRAILER)


if __name__ == "__main__":
    unittest.main()
