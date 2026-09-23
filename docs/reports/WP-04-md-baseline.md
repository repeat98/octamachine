# WP-04 — Machinedrum startup baseline

Date: 2026-09-23
Scope: the pinned Gearmulator MD/MM model running the local Machinedrum SPS-1UW OS 1.63 image. This is emulator evidence, not an Octatrack or hardware boot.

## Result

The bounded headless driver reached firmware-ready, factory-initialized, and no-stimulus idle checkpoints from a blank flash, then reached the corresponding cached-start and idle checkpoints from the exact flash image and factory cache produced by the cold run. Two fresh driver processes produced matching checkpoint metadata and full MMIO event order. Both DSP HI08 write streams, all SIM reads/writes, and reset state were captured in private local traces. The summarized capture also produced four WP-03 version-1 manifests and redacted JSONL event projections. The WP-03 comparator found the repeated cold pair and cached pair equivalent across all 5,630 declared records in each comparison. These projections omit MMIO payload values and callback PC samples; raw trace values remain outside the repository.

## Reproduction

The run used Gearmulator MD/MM `8cea0524a75435122c20b669ca114c9ac6509ba2` with the recursive revisions recorded in [WP-01](WP-01-provenance.md). Instrumentation hashes:

| Patch | SHA-256 |
| --- | --- |
| `0001-opt-in-md-bus-trace.patch` | `d24558fd0556e21c37eff3a7670d1a076f756224a30bd30fa5ac14f923f50d09` |
| `0002-md-baseline-checkpoints.patch` | `0c6521bf6c6adc78a6c1c0a696b8e9848829890d99a4bf65995bb0f35b93780e` |

The local image matched the public OS 1.63 profile: 8 MiB, CRC-32 `3d552c99`, SHA-1 `a872a2f3527063673d6ea6d3080c4c62ef0cadc1`, and Gearmulator FNV-64 `33b7c1a9e29f43fd`. Firmware bytes and the local SHA-256 are not published.

On macOS 26.6.2 arm64, CMake 4.0.1, Ninja 1.13.2, and Apple Clang 21.0.0, a clean pinned source export was configured and built as follows (optional plugins and unrelated synth targets disabled):

```sh
cmake -S /path/to/clean/gearmulator-md-mm -B /path/to/build-md-baseline -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_OSX_ARCHITECTURES=arm64 \
  -DBUILD_TESTING=ON \
  -Dgearmulator_BUILD_JUCEPLUGIN=OFF \
  -Dgearmulator_BUILD_JUCEPLUGIN_CLAP=OFF \
  -Dgearmulator_SYNTH_OSIRUS=OFF \
  -Dgearmulator_SYNTH_OSTIRUS=OFF \
  -Dgearmulator_SYNTH_VAVRA=OFF \
  -Dgearmulator_SYNTH_XENIA=OFF \
  -Dgearmulator_SYNTH_NODALRED2X=OFF \
  -Dgearmulator_SYNTH_JE8086=OFF \
  -Dgearmulator_SYNTH_ELEKTRON=ON
cmake --build /path/to/build-md-baseline \
  --target mdPanelReadinessFirmwareTest mdIdleSchedulerFirmwareTest mdUwFirmwareTest \
  --parallel 4
```

The capture wrapper requires a new output directory. Use a local image that passes `scripts/audit_md_image.py`; the wrapper checks the supported profile before starting either run. The full mode retains raw MMIO values in local files, so direct its output to a private path:

```sh
python3 scripts/capture_md_baseline.py \
  --driver /path/to/build-md-baseline/source/elektron/md/mdLibTest/mdPanelReadinessFirmwareTest \
  --firmware /path/to/your-machinedrum-flash.bin \
  --output-dir /private/tmp/md-baseline-run-1 \
  --timeout-seconds 300 \
  --full-private-trace \
  --trace-limit 12000000
```

The wrapper starts the same driver twice. Each driver process constructs a blank-flash machine and a separately labeled cached-start machine; it applies finite frame limits to readiness and a finite wall-clock timeout to the child process. `summary.json` contains only reviewed fingerprints, checkpoint fields, event counts, redacted event-order hashes, and outcome metadata. Do not publish the `.trace.txt` files: raw MMIO values include firmware-dependent DSP upload data.

For WP-03 runtime evidence, provide build metadata and leave `--full-private-trace` off. The metadata records the exact build argv and configured toolchain without exposing the private build path:

```json
{
  "command": [
    "cmake", "--build", "<build-dir>", "--target",
    "mdPanelReadinessFirmwareTest", "mdIdleSchedulerFirmwareTest",
    "mdUwFirmwareTest", "--parallel", "4"
  ],
  "toolchain": {
    "host": "macOS 26.6.2 arm64",
    "cmake": "4.0.1",
    "generator": "Ninja 1.13.2",
    "compiler": "Apple Clang 21.0.0",
    "build_type": "Release",
    "CMAKE_OSX_ARCHITECTURES": "arm64",
    "BUILD_TESTING": "ON",
    "gearmulator_BUILD_JUCEPLUGIN": "OFF",
    "gearmulator_BUILD_JUCEPLUGIN_CLAP": "OFF",
    "gearmulator_SYNTH_OSIRUS": "OFF",
    "gearmulator_SYNTH_OSTIRUS": "OFF",
    "gearmulator_SYNTH_VAVRA": "OFF",
    "gearmulator_SYNTH_XENIA": "OFF",
    "gearmulator_SYNTH_NODALRED2X": "OFF",
    "gearmulator_SYNTH_JE8086": "OFF",
    "gearmulator_SYNTH_ELEKTRON": "ON"
  }
}
```

Run the summarized capture and compare the two cold manifests and the two cached manifests:

```sh
python3 scripts/capture_md_baseline.py \
  --driver /path/to/build-md-baseline/source/elektron/md/mdLibTest/mdPanelReadinessFirmwareTest \
  --firmware /path/to/your-machinedrum-flash.bin \
  --build-metadata /path/to/build-metadata.json \
  --output-dir /private/tmp/md-baseline-contract-run \
  --timeout-seconds 180

python3 scripts/compare_captures.py \
  /private/tmp/md-baseline-contract-run/cold-a-cold.manifest.json \
  /private/tmp/md-baseline-contract-run/cold-b-cold.manifest.json
python3 scripts/compare_captures.py \
  /private/tmp/md-baseline-contract-run/cold-a-cached.manifest.json \
  /private/tmp/md-baseline-contract-run/cold-b-cached.manifest.json
```

Both comparisons returned `equivalent`, with no first divergence. The generated WP-03 manifests and JSONL projections contain event addresses, widths, regions, MCU-cycle timestamps, and checkpoint fields, but no MMIO values or callback PC samples. Keep the wrapper's `.trace.txt` files and process logs local; even summarized raw records may contain firmware-dependent MMIO values. The separate `--full-private-trace --trace-limit 12000000` mode is for local per-access analysis and does not emit the WP-03 projection files.

## Measured checkpoints

The driver advances in blocks of at most 128 frames at 44.1 kHz. Frame positions and emulated cycle counters below are model measurements, not wall-clock timings.

| State | Frames | Measured result |
| --- | ---: | --- |
| Cold reset | 0 | PC register `0x0000000c`, SP register `0`, MCU cycle 4; blank flash and factory initialization expected. |
| Cold DSP boot observed | 128 | Both DSPs reported booted by the first sample block; MCU cycle 116,106. The block sampling does not reveal which DSP completed first within those 128 frames. |
| Cold firmware ready | 102,400 | Panel handshake and firmware MIDI readiness true; both DSPs booted; 3,148 panel bytes, 314 tiles, 748 lit pixels. MCU cycle 92,879,824. |
| Cold initialization complete | 793,800 (18 s) | Firmware remained ready; factory cache published and flash dirty; 26,894 panel bytes, 2,682 tiles, 2,379 lit pixels. |
| Cold no-stimulus idle | 837,900 (19 s) | Firmware remained ready; host, MCU, DSP1, and DSP2 clocks all advanced from the initialization checkpoint. |
| Cached reset | 0 | PC register `0x0000000c`, SP register `0`; initialized flash and factory cache supplied; factory initialization not expected. |
| Cached firmware ready | 102,400 | Panel handshake and firmware MIDI readiness true; both DSPs booted; same panel startup counters as the cold ready point. MCU cycle 92,879,824. |
| Cached ready | 529,200 (12 s) | Firmware remained ready; factory cache present; 22,090 panel bytes, 2,207 tiles, 1,680 lit pixels. |
| Cached no-stimulus idle | 573,300 (13 s) | Firmware remained ready; host, MCU, DSP1, and DSP2 clocks all advanced from the cached ready checkpoint. |

Cold readiness arrived at frame 102,400 (about 2.32 seconds of emulated audio frames); factory flash initialization continued until the 18-second checkpoint. Cached-start readiness used the same observed frame count, while the factory cache was already present at reset. The repeated runs produced identical values for all published checkpoint fields.

## Bus trace coverage and repeatability

Each child run wrote 10,340,278 unfiltered MMIO records across the cold and cached instances, below the configured 12,000,000-record limit. No records were capped, filtered, deduplicated, or aggregated in full-private mode. The event-order comparison uses instance label, MCU cycle, direction, access width, and address; it deliberately excludes MMIO payload values and callback PC samples.

| Region and direction | Events per labeled instance, in each run |
| --- | ---: |
| SIM reads | 2,591,231 |
| SIM writes | 2,005,115 |
| DSP1 HI08 reads / writes | 6,336 / 38,772 |
| DSP2 HI08 reads / writes | 28,058 / 500,627 |

Both labeled instances had the same counts, and both independent driver runs had matching event counts and event-order hashes for the cold and cached phases. These traces cover construction through firmware-ready; the later factory-initialization and no-stimulus idle checkpoints are represented by state/cycle snapshots, not by continuing the raw trace.

The lower-volume reviewed mode also completed twice with identical retained-event order. It recorded 11,248 ordinary events per run while reporting counts and cycle intervals for aggregated DSP and panel-port writes. Its DSP write counts match the full trace; SIM write counts match when the ordinary SIM events and aggregated PPDAT/PPDDR writes are combined. Read totals differ by design because summary mode suppresses repeat reads and filters SIM reads. The WP-03 comparator independently compared the cold projections and cached projections; both reported 5,630 records compared and `equivalent`.

## Failure handling and limits

- A one-event trace limit returned exit code 4 with `incomplete: cold-a:trace_cap`.
- A missing firmware path returned exit code 2 with `failed: firmware_missing_or_unreadable` before launching the emulator.
- A temporary stalling driver with a 0.05-second timeout returned exit code 4 with `incomplete: cold-a:timeout`.
- The headless capture reached Gearmulator's firmware-ready and idle checkpoints only. It does not establish Octatrack execution, physical hardware behavior, audio parity, or a port architecture.
- Both DSP boot flags were first observed in the same 128-frame sampling block, so their sub-block completion order remains unresolved.
- Runtime checkpoints confirm the reset PC and SP register values and subsequent progress in this model. They do not resolve the source-map disagreements about clocks, SRAM size, or hardware revision.

`make check` passed: nine reference repositories validated, scripts compiled, and 16 tests passed. The pinned source targets built; the summarized capture completed twice and generated the WP-03 manifest/JSONL pairs, and the separate full-private capture completed twice without hitting its event caps. The cold and cached WP-03 comparisons each matched all 5,630 records. The negative cap/missing-input/stall cases produced incomplete or failed outcomes as intended. No Octatrack or hardware test was run in this packet.
