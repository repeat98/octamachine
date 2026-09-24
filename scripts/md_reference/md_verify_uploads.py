#!/usr/bin/env python3
"""Compare private Gearmulator HI08 traces with extracted DSP load records.

Reads raw trace values and local decoded sections, but prints only stream
identity, counts, offsets, cycles, and equality results. It never prints or
writes DSP words or copies the raw trace.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import md_extract


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_IMAGES = ROOT / "out/machinedrum/os163"
TRACE_RE = re.compile(
    rb"^mdbus instance=(\d+) label=([a-z_]+) cycle=(\d+) "
    rb"pc=([0-9a-fA-F]+) ([RW])(\d+) addr=([0-9a-fA-F]+) "
    rb"value=([0-9a-fA-F]+)$"
)
DSP_WINDOWS = {
    0x00500000: ("DSP1", "section_2_DSP.bin"),
    0x00600000: ("DSP2", "section_1_DSP.bin"),
}
HLEND = 1 << 5


@dataclass
class PortStream:
    instance: int
    label: str
    dsp: str
    icr: int = 0
    icr_writes: int = 0
    tx: list[int] = field(default_factory=lambda: [0, 0, 0])
    words: bytearray = field(default_factory=bytearray)
    cycles: list[int] = field(default_factory=list)
    little_endian: list[bool] = field(default_factory=list)

    def _emit(self, cycle: int) -> None:
        high, middle, low = self.tx
        little = bool(self.icr & HLEND)
        word = (low << 16 | middle << 8 | high) if little else (high << 16 | middle << 8 | low)
        self.words.extend(word.to_bytes(3, "big"))
        self.cycles.append(cycle)
        self.little_endian.append(little)
        self.tx[:] = [0, 0, 0]

    def write(self, offset: int, width: int, value: int, cycle: int) -> None:
        if offset == 0:
            self.icr = (value >> 8) & 0xff if width == 2 else value & 0xff
            self.icr_writes += 1
        elif offset == 4 and width == 2:
            self.tx[0] = value & 0xff
        elif offset == 5 and width == 1:
            self.tx[0] = value & 0xff
        elif offset == 6 and width == 2:
            self.tx[1] = (value >> 8) & 0xff
            self.tx[2] = value & 0xff
            self._emit(cycle)
        elif offset == 6 and width == 1:
            self.tx[1] = value & 0xff
        elif offset == 7 and width == 1:
            self.tx[2] = value & 0xff
            self._emit(cycle)


def expected_record_stream(image_dir: Path, filename: str) -> tuple[bytes, int, int]:
    md_extract.OUT = image_dir
    records = md_extract.dsp_records(filename)
    words: list[int] = []
    for space, address, values in records:
        words.extend((space, address, len(values)))
        words.extend(values)
    try:
        stream = b"".join(word.to_bytes(3, "big") for word in words)
    except OverflowError as exc:
        raise ValueError("decoded record contains a word outside the 24-bit range") from exc
    return stream, len(records), len(words)


def read_port_streams(path: Path) -> dict[tuple[int, str, str], PortStream]:
    streams: dict[tuple[int, str, str], PortStream] = {}
    try:
        source = path.open("rb")
    except OSError as exc:
        raise ValueError(f"cannot open trace: {path.name}") from exc

    with source:
        for line_number, raw in enumerate(source, 1):
            if b"truncated" in raw.lower():
                raise ValueError(f"trace reports truncation near line {line_number}")
            clean = raw.rstrip(b"\r\n")
            row = TRACE_RE.match(clean)
            if row is None:
                if clean.startswith(b"mdbus instance="):
                    raise ValueError(f"malformed bus event near line {line_number}")
                continue
            instance_b, label_b, cycle_b, _, direction_b, width_b, address_b, value_b = row.groups()
            if direction_b != b"W":
                continue
            address = int(address_b, 16)
            window = next((base for base in DSP_WINDOWS if base <= address < base + 8), None)
            if window is None:
                continue
            instance = int(instance_b)
            label = label_b.decode("ascii")
            dsp = DSP_WINDOWS[window][0]
            key = (instance, label, dsp)
            stream = streams.setdefault(key, PortStream(instance, label, dsp))
            stream.write(address - window, int(width_b), int(value_b, 16), int(cycle_b))
    return streams


def find_unique(stream: bytes, expected: bytes) -> int:
    start = stream.find(expected)
    if start < 0:
        return -1
    if stream.find(expected, start + 1) >= 0:
        return -2
    return start // 3 if start % 3 == 0 else -1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("traces", nargs="+", type=Path,
                    help="private, full Gearmulator bus-trace files")
    ap.add_argument("--images", type=Path, default=DEFAULT_IMAGES,
                    help="local md_extract output directory")
    args = ap.parse_args()

    expected: dict[str, tuple[bytes, int, int]] = {}
    try:
        for dsp, filename in (("DSP1", "section_2_DSP.bin"),
                              ("DSP2", "section_1_DSP.bin")):
            expected[dsp] = expected_record_stream(args.images, filename)
        all_matches = 0
        for trace_path in args.traces:
            streams = read_port_streams(trace_path)
            if not streams:
                raise ValueError(f"no DSP HI08 write events found in {trace_path.name}")
            by_instance: dict[tuple[int, str], set[str]] = {}
            for instance, label, dsp in streams:
                by_instance.setdefault((instance, label), set()).add(dsp)
            for (instance, label), dsps in by_instance.items():
                if dsps != {"DSP1", "DSP2"}:
                    raise ValueError(
                        f"incomplete DSP pair: {trace_path.name} {label} instance={instance}"
                    )
            for (instance, label, dsp), observed in sorted(streams.items()):
                record_stream, record_count, word_count = expected[dsp]
                word_count_observed = len(observed.cycles)
                offset = find_unique(bytes(observed.words), record_stream)
                other_dsp = "DSP2" if dsp == "DSP1" else "DSP1"
                wrong_stream = find_unique(bytes(observed.words), expected[other_dsp][0])
                if offset == -2:
                    raise ValueError(f"ambiguous repeated load stream: {trace_path.name} {label} {dsp}")
                if offset < 0:
                    raise ValueError(f"load stream did not match: {trace_path.name} {label} {dsp}")
                if wrong_stream != -1:
                    raise ValueError(f"load stream matched the opposite DSP image: {trace_path.name} {label} {dsp}")

                first_word = int.from_bytes(observed.words[:3], "big") if len(observed.words) >= 3 else 0
                boot_pc = int.from_bytes(observed.words[3:6], "big") if len(observed.words) >= 6 else 0
                boot_words = first_word + 2
                if offset < boot_words:
                    raise ValueError(f"load stream overlaps boot block: {trace_path.name} {label} {dsp}")
                suffix_at = offset + word_count
                if suffix_at > word_count_observed:
                    raise ValueError(f"invalid matched stream bounds: {trace_path.name} {label} {dsp}")
                modes = set(observed.little_endian[offset:suffix_at])
                if modes != {False}:
                    raise ValueError(f"unexpected HI08 transmit byte order: {trace_path.name} {label} {dsp}")
                mode = "little" if modes == {True} else "big" if modes == {False} else "mixed"
                start_cycle = observed.cycles[offset]
                end_cycle = observed.cycles[suffix_at - 1]
                window_base, image_name = next(
                    (base, filename) for base, (name, filename) in DSP_WINDOWS.items()
                    if name == dsp
                )
                print(
                    f"{trace_path.name}: instance={instance} label={label} {dsp} "
                    f"window={window_base:08x} image={image_name} "
                    f"records={record_count} words={word_count} exact_match=yes "
                    f"start_word={offset} prefix_words={offset} "
                    f"dsp_boot_prefix_words={boot_words} dsp_boot_pc={boot_pc:06x} "
                    f"pre_record_words={offset-boot_words} "
                    f"trailing_words={word_count_observed-suffix_at} "
                    f"icr_writes={observed.icr_writes} tx_order={mode} "
                    f"record_cycles={start_cycle}..{end_cycle}"
                )
                all_matches += 1
        if all_matches == 0:
            raise ValueError("no upload streams were verified")
    except (OSError, ValueError, SystemExit) as exc:
        message = str(exc)
        if message:
            print(message, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
