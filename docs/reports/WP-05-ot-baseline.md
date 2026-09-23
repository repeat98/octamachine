# WP-05 — Octatrack OS 1.40C baseline

Date: 2026-09-23

Scope: the unmodified Octatrack OS 1.40C image in the pinned octemu Octatrack MKII model. This is emulator evidence only.

## Result

The official OS 1.40C distribution archive was verified against octemu's pinned SHA-256, and its extracted `main.bin` section is 1,112,560 bytes. The unmodified image reaches the `PTCH` project screen in both bounded headless and windowed runs using the same generated CompactFlash project and NVRAM state copied independently for each run. The loading overlay disappears and the screen remains available for a 16-second guest-time dwell before input.

Both runs accepted a scripted PLAY tap, lit the script-checked panel lamp condition, accepted STOP, and exited with status 0. The windowed screenshots show the green PLAY indicator and a yellow sequencer lamp after the tap. This establishes a runnable Octatrack emulator baseline and a known UI response; it does not establish Machinedrum firmware compatibility or behavior on physical hardware.

Reviewed, redacted v1 metadata and event projections:

- Headless: [manifest](WP-05-ot-headless-v1.manifest.json), [event projection](WP-05-ot-headless-v1.events.jsonl).
- Windowed UI: [manifest](WP-05-ot-ui-v1.manifest.json), [event projection](WP-05-ot-ui-v1.events.jsonl).
- Reusable walks: [`tests/walks/wp05-octatrack-panel.jsonl`](../../tests/walks/wp05-octatrack-panel.jsonl) and [`tests/walks/wp05-octatrack-panel-ui.jsonl`](../../tests/walks/wp05-octatrack-panel-ui.jsonl).

The JSONL projections retain screen observations, scripted inputs, lamp state, and named guest-audio-block marks. The `walk_step` time in each projection is an ordered script index, not elapsed time. Full emulator logs, firmware, card/NVRAM images, and screenshots remain local under ignored `vendor/octemu/out/`.

## Input, source, and build profile

- Target model: octemu's `Elektron Octatrack MKII (MCF54455), v2`, default `cfv4e` CPU and 256 MiB SDRAM. The physical board revision and carrier are still unidentified.
- Firmware: OS 1.40C `main.bin`, extracted unchanged from the official distribution archive. Archive SHA-256: `370c55a3dad3996b8e4b46400a205066fdaf185ad4d0255a3a3f835060573ff0`; extracted main image size: 1,112,560 bytes. The archive pin is from octemu's committed OS fetch rule. No firmware patch or image transform was used.
- Emulator: octemu `87000189418c8ca2026dc047bda220b66802809d`; QEMU base `e8d693e12af9cbb89d724baadfcc08559669e279` with the 13 committed QEMU patches under `vendor/octemu/patches/qemu/`; DSP56300 base `c051afad31612c2d2c7a81a7ab23e1c5ac9e61af` with the 11 committed patches under `vendor/octemu/patches/dsp56300/`. The run manifests record each patch digest.
- Host/build: macOS 26.6.2 arm64, CMake 4.0.1, Meson 1.10.2, Ninja 1.13.2, Apple Clang 21.0.0.

From the repository root, the source and local inputs were prepared with:

```sh
make -C vendor/octemu doctor
make -C vendor/octemu setup
make -C vendor/octemu os
JOBS=8 make -C vendor/octemu qemu
make -C vendor/octemu
make -C vendor/octemu fixtures
```

`doctor`, `setup`, the QEMU build, the default octemu build, and fixture creation completed. QEMU produced the patched Octatrack board; the default build produced `octemu`, `octdsp`, and the panel raster. The firmware archive matched the pinned digest before extraction. Firmware and fixture contents were not added to Git.

The fixture target creates the `fx2` test project and sample in a local card image. Before each run, fresh card and NVRAM copies were made from that same fixture output. `--read-only` discarded card writes at process exit. The two runs therefore start from the same saved content while keeping their mutable files separate.

## Reproduction

Run these from `vendor/octemu/` after the preparation commands above. The scripts live at the repository root under `tests/walks/`.

```sh
mkdir -p out/wp05/headless out/wp05/ui
cp out/fx2/card.img out/wp05/headless/card.img
cp out/fx2/nvram.bin out/wp05/headless/nvram.bin
./octemu --headless --read-only --os out/os/main.bin \
  --cf-card out/wp05/headless/card.img \
  --nvram out/wp05/headless/nvram.bin \
  --script ../../tests/walks/wp05-octatrack-panel.jsonl --timeout 240

cp out/fx2/card.img out/wp05/ui/card.img
cp out/fx2/nvram.bin out/wp05/ui/nvram.bin
OCTA_NO_FOCUS=1 ./octemu --read-only --os out/os/main.bin \
  --cf-card out/wp05/ui/card.img \
  --nvram out/wp05/ui/nvram.bin \
  --script ../../tests/walks/wp05-octatrack-panel-ui.jsonl --timeout 240
```

`OCTA_NO_FOCUS=1` leaves the host foreground application alone while still running the windowed SDL renderer and monitor. The windowed script saves before/after panel screenshots as local PPM files. They are 2,500 × 1,364 and remain ignored with the other local run artifacts.

Latest bounded runs, both started from the regenerated fixture copies:

| Mode | Start (UTC) | Observations | Final guest mark | Result |
| --- | --- | --- | ---: | --- |
| Headless | 2026-09-23 21:44:08 | `PTCH`; loading text gone; PLAY lamp condition lit; STOP accepted | 64,888 blocks | exit 0; 64,909 guest audio blocks consumed |
| Windowed | 2026-09-23 21:44:49 | `PTCH`; loading text gone; PLAY lamp condition lit; STOP accepted; before/after screenshots | 64,274 blocks | exit 0; 64,320 guest audio blocks consumed |

Both runs reported ROM boot completion for DSP core 0 at `0x31000` and core 1 at `0x32000`. Those messages show progress in the emulator's DSP model; they are not a DSP upload or audio-fidelity claim for the Machinedrum payload.

An earlier no-card check reached `C0MPACT` with a 90-second wall-clock timeout. That is a separate no-card boot observation, not the ready-screen result above. An optional GIF attempt failed because the installed ffmpeg could not load its local x265 dylib; the required UI walk and built-in PPM screenshots completed without ffmpeg.

## Source map for the run profile

These locations describe the emulator model used by both manifests; they are source-model observations, not physical-board validation.

| Boundary | Source locations | What the model connects |
| --- | --- | --- |
| CPU, reset, memory | `vendor/octemu/vendor/qemu/hw/m68k/ot-board.c:50-81, 2419-2479, 2564-2594, 2786-2803` | Declares the CFV4e/MCF54455 Octatrack MKII model; maps SDRAM, SRAM, CS1, and MBAR; loads the raw OS at `0x40000400`; initializes the stack; and installs the DSP interface. |
| DSP host port and cores | `vendor/octemu/src/board/ot-dsp-port.c:2-15, 101-179`; `ot-dsp-shim.cc:725-800`; `ot-audio-shm.h:1-76` | Models the two DSP56721 cores, HDI24 registers and host requests, DSP/ColdFire interleave, and 16-frame shared audio blocks. The run log reported both DSP ROM boots. |
| Panel and controls | `vendor/octemu/src/board/ot-panel-uart.c:1-28, 355-403`; `src/script.c:25-40, 332-369`; `src/main.c:576-604` | Connects the 312,500-baud UART1 panel stream to the virtual panel frontend; scripts drive the same key/lamp/display state path. The wait and tap conditions use guest audio time; the process timeout is wall time. |
| CompactFlash and NVRAM | `vendor/octemu/src/board/ot-ata.c:1-20, 663-714`; `vendor/octemu/vendor/qemu/hw/m68k/ot-board.c:2441-2447, 2544-2549`; `src/main.c:84-98` | Maps the ATA-backed CF card and CS1 NVRAM, restores the 1 MiB NVRAM image, and supports a read-only card overlay for isolated runs. |
| Audio and host pacing | `vendor/octemu/src/board/ot-dsp-shim.cc:270-283, 569-629`; `vendor/octemu/src/board/ot-audio-shm.h:35-76`; `vendor/octemu/src/audio.c:1-11, 655-698, 874-930` | Paces guest DSP work in 16-frame blocks, transfers samples over shared memory, and plays them through the host monitor. The source explicitly separates sample-exact recordings from live resampled playback. |

## Timing and fidelity limits

The walks wait on guest audio progress: one block is 16 frames at 44.1 kHz. Their 16-second boot dwell, PLAY settle/verification, and one-second playback dwell therefore describe guest progress. The 240-second process timeout and the UART's asynchronous host/frontend work use wall-clock scheduling. The emulator does not guarantee real-time host execution.

The successful windowed run logged a live-monitor ratio of `0.8420–1.0000`, a 298-cent reported spread, and 90,181 starved frames. These are artifacts of the host's live resampling/playback path in that one run. They are not guest-cycle measurements, do not change the observed scripted panel state, and do not establish sample parity. No audio recording or audio-quality comparison was made.

The panel screenshot and event projection establish one scripted PLAY/STOP response. They do not establish all controls, MIDI, sequencing, persistent-state semantics, audio routing, physical timing, hardware revision, recovery behavior, or a port. No Octatrack hardware was run, and no Machinedrum firmware ran in octemu.
