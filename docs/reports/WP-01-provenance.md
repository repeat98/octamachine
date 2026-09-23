# WP-01 — Source provenance and clean build record

- Date: 2026-09-23
- Owner: Codex
- Branch: `work/wp-01-source-provenance`
- Status: `done` ([PR #4](https://github.com/repeat98/octamachine/pull/4), merged as `29471d01c61bbd8e83aa925157ae8fc4e25ddfa8`)

## Result

The trace patch applies to a clean checkout of the pinned Gearmulator MD/MM source, and the trace-enabled `mdLib` builds with its required source dependencies at their recorded Git-link commits. This is a source/build result only; it does not establish a Machinedrum firmware boot.

## Repository and reference revisions

The octamachine work branch is based on `6cdc2585ae8d62deb6c264538a35417c279b9b89` (merge of WP-34 PR #3). `references.json` pins `gearmulator-md-mm` and the `octemu` submodule. Other listed refs name moving branches; the following are the local checkout snapshots observed for this prompt, not new manifest pins:

| Reference | Observed commit | Local source state |
| --- | --- | --- |
| `gearmulator-md-mm` | `8cea0524a75435122c20b669ca114c9ac6509ba2` | Root checkout has a local `mdmc.cpp` change and build directories; nested DSP changes are listed below. |
| `octemu` | `87000189418c8ca2026dc047bda220b66802809d` | Tracked submodule is clean. |
| `gearmulator` | `8aad2439f1999388a9edea2ab31835fc65f55ef6` | Root checkout is clean; recursive submodules are uninitialized. |
| `octabam` | `f77d5d728732d05b3d1a8934872b99a50bd2e935` | Root checkout is clean; its two listed nested modules are uninitialized. |
| `octamax` | `7d9debcfdf7dbb1351066f6010d7f250d2b2ab28` | Root checkout is clean. |
| `dsp56300` | `c051afad31612c2d2c7a81a7ab23e1c5ac9e61af` | Separate local research checkout is modified; it is not the Gearmulator MD/MM submodule checkout. |
| `mc68k` | `4a6d0d17a1f2b30077ab726c27fe9bb770fa0456` | Local research checkout has an untracked `.DS_Store`; Gearmulator's pinned submodule is a different commit. |
| `elektron-firmware-tool` | `065d18f4195793e61891e387813488ee59f6d1ca` | Separate local research checkout has a modified `main.c`; octemu's pinned tool checkout is listed below. |
| `mame` | `d7ffd71ed97831b7f995337d6c5bd1bbb03898af` | Root checkout is clean. |

### Gearmulator MD/MM recursive revisions

The parent commit is the exact `references.json` pin. The recursive Git-link snapshot reported by `git submodule status --recursive` is:

| Path | Commit | State in the original local checkout |
| --- | --- | --- |
| `source/3rdparty/RmlUi` | `97bb5921595a0528bd67d61f328885ac19643623` | initialized |
| `source/3rdparty/freetype` | `828916527ce4f69af722bce46ce54d289001a0bd` | initialized |
| `source/3rdparty/freetype/subprojects/dlg` | `72dfcc858c040c54a6a0b88fcb7e70ee186d3167` | initialized |
| `source/3rdparty/lunasvg` | `f8aabfb444bb37f69df7290790f57e4a27730a93` | initialized |
| `source/3rdparty/lunasvg/plutovg` | `5e4712cf873b0c7829a4a6157763e2ad3ac49164` | initialized |
| `source/JUCE` | `f96dadf41974b512ab0e2d13767c9b1902470dc7` | uninitialized |
| `source/clap-juce-extensions` | `2aaad9e637c62a4eed4664a7e8ef52dca9dc3ba6` | uninitialized |
| `source/cpp-terminal` | `a79a1a1766e0e8f768955d782e1b84ad5a82b843` | initialized |
| `source/dsp56300` | `1378c43074e6ec22f69f14ed55c21e44c5ccadc1` | initialized, locally modified |
| `source/dsp56300/source/asmjit` | `3577608cab0bc509f856ebf6e41b2f9d9f71acc4` | initialized |
| `source/mc68k` | `ace95b3d0a5a332db147244762dda65f9a010b9f` | initialized |

The selected `mdLib` build used clean archive contents at the pinned `dsp56300`, `asmjit`, `mc68k`, `RmlUi`, `freetype`, and `dlg` commits. JUCE and CLAP were not required because plugin builds were disabled. Other optional components were not built.

### Modifications in existing ignored trees

The clean build did not alter these trees. Their local state at the start of WP-01 was:

- `vendor/gearmulator-md-mm`: tracked `source/elektron/md/mdLib/mdmc.cpp` was modified; `build-headless/` and `build-octamachine/` were untracked. Its nested DSP56300 checkout at `1378c43074e6ec22f69f14ed55c21e44c5ccadc1` had tracked changes to `source/dsp56kEmu/dsp.cpp` and `dsp.h`, plus local `.DS_Store` files.
- Separate `vendor/dsp56300` checkout at `c051afad31612c2d2c7a81a7ab23e1c5ac9e61af`: tracked changes to `source/CMakeLists.txt`; `source/dsp56kEmu/{agu.h,assembler.cpp,dma.cpp,dsp.cpp,dsp.h,dsp_ops_alu.inl,esai.cpp,jitops.h,jitops_alu.cpp,memory.cpp,memory.h,peripherals.cpp,peripherals.h}`; untracked `build/`, `source/dsp_host/`, and `.DS_Store` files.
- `vendor/octemu/vendor/dsp56300` at the same base commit: tracked changes to `source/dsp56kEmu/{dma.cpp,dma.h,dsp.cpp,dsp_ops_alu.inl,esai.cpp,hdi08.cpp,interrupts.h,jitblock.cpp,jitdspregs.cpp,jitops.h,jitops_alu.cpp,jitops_alu.inl,peripherals.cpp}`; untracked `build/` and `.DS_Store` files.
- `vendor/octemu/vendor/qemu` at `e8d693e12af9cbb89d724baadfcc08559669e279`: tracked changes to `accel/tcg/{cpu-exec.c,tb-maint.c,translator.c}`, `hw/m68k/{mcf_intc.c,meson.build}`, `include/hw/m68k/mcf.h`, `target/m68k/{cpu.c,helper.c,helper.h,translate.c}`, and `util/qemu-timer.c`; untracked `hw/m68k/{ot-ata.c,ot-audio-shm.h,ot-board.c,ot-dsp-port.c,ot-dsp-shim.cc,ot-dsp56k.cc,ot-dsp56k.h,ot-panel-uart.c,ot-panel-wire.h,ot-qemu.h}`, `include/exec/ot-insn-budget.h`, `.DS_Store`, and a build directory.
- `vendor/octemu/vendor/elektron-firmware-tool` is clean at `a5bce9a6af644386d900924082993a805e812874`. The separate `vendor/elektron-firmware-tool` checkout at `065d18f4195793e61891e387813488ee59f6d1ca` has modified `main.c`; `vendor/mc68k` at `4a6d0d17a1f2b30077ab726c27fe9bb770fa0456` has an untracked `.DS_Store`.

### Octemu build inputs

The tracked octemu source pin is `87000189418c8ca2026dc047bda220b66802809d`. Its local build scripts record these dependency bases:

| Dependency | Base commit | Source of pin |
| --- | --- | --- |
| `dsp56300` | `c051afad31612c2d2c7a81a7ab23e1c5ac9e61af` | `vendor/octemu/patches/dsp56300/BASE_COMMIT.txt` |
| QEMU | `e8d693e12af9cbb89d724baadfcc08559669e279` | `vendor/octemu/patches/qemu/BASE_COMMIT.txt` |
| `elektron-firmware-tool` | `a5bce9a6af644386d900924082993a805e812874` | default `EFT_PIN` in `vendor/octemu/scripts/setup.sh` |
| `asmjit` | `3577608cab0bc509f856ebf6e41b2f9d9f71acc4` | recursive DSP submodule in the DSP base checkout |

The local octemu QEMU and DSP worktrees have tracked source modifications and generated build directories. QEMU is modified at tracked files under `accel/tcg/`, `hw/m68k/`, `include/hw/m68k/`, `target/m68k/`, and `util/`, and has untracked Octatrack board sources. The DSP tree has 13 modified tracked source files and a local build directory. The firmware-tool checkout is clean at its expected pin. These are local prepared dependencies, not clean-build evidence for octemu in this prompt.

## Patch identity and clean Gearmulator build

| Patch | SHA-256 | Result |
| --- | --- | --- |
| `patches/gearmulator-md-mm/0001-opt-in-md-bus-trace.patch` | `d24558fd0556e21c37eff3a7670d1a076f756224a30bd30fa5ac14f923f50d09` | Applies to the clean parent checkout; `git diff --check` passes. |
| `patches/octemu/0001-sdram-alias-and-interactive-pace.patch` | `fbc3bd6e4cc0f270fb4196814940345dddf88a7c8b432ad5e30275ca160552d9` | Recorded separately; not applied or built during WP-01. |

For a fresh contributor checkout, the project setup path is documented in [Getting Started](../GETTING_STARTED.md#machinedrum-reference-emulator): fetch the pinned reference, recursively initialize its submodules, and run `make gearmulator-prepare`. For the clean verification here, a detached worktree was created at the pinned parent commit before patch application. Required submodule contents were exported from their exact Git-link commits into that isolated tree, avoiding the modified research copies. The patch was checked/applied with:

```sh
git -C "$CHECKOUT" apply --check "$REPO_ROOT/patches/gearmulator-md-mm/0001-opt-in-md-bus-trace.patch"
git -C "$CHECKOUT" apply "$REPO_ROOT/patches/gearmulator-md-mm/0001-opt-in-md-bus-trace.patch"
```

The root was configured with this command (paths shortened here to `$CHECKOUT`):

```sh
cmake -S "$CHECKOUT" -B "$CHECKOUT/build-mdlib" -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TESTING=OFF \
  -Dgearmulator_BUILD_JUCEPLUGIN=OFF \
  -Dgearmulator_SYNTH_OSIRUS=OFF \
  -Dgearmulator_SYNTH_OSTIRUS=OFF \
  -Dgearmulator_SYNTH_VAVRA=OFF \
  -Dgearmulator_SYNTH_XENIA=OFF \
  -Dgearmulator_SYNTH_NODALRED2X=OFF \
  -Dgearmulator_SYNTH_JE8086=OFF \
  -Dgearmulator_SYNTH_ELEKTRON=ON
cmake --build "$CHECKOUT/build-mdlib" --target mdLib --parallel 4
```

Observed result: CMake configuration succeeded and Ninja built all 222 steps, ending with `source/elektron/md/mdLib/libmdLib.a`. The build emitted upstream `-Ofast` deprecation and AsmJit `memset`/`memcpy` warnings. CMake also warned that it could not detect an Xcode version and that `rclone.conf` was absent; neither prevented the Ninja `mdLib` build. No firmware was loaded and no emulator runtime was launched.

## Host prerequisites and supported host

The pinned octemu README describes a macOS build. On this machine the observed host was macOS 26.6.2, Darwin 25.6.0, arm64; Git 2.49.0, CMake 4.0.1, Ninja 1.13.2, Apple Clang 21.0.0, Python 3.14.6, GNU Make 3.81, and SDL2 2.32.4.

`make -C vendor/octemu doctor` reported every required tool present: CMake, Ninja, pkg-config, SDL2, Python, `mformat`, `rsvg-convert`, and ImageMagick. It also reported optional `ffmpeg`, `m68k-elf-as`, and `m68k-elf-ld` present. The upstream guide calls for Python 3.11 or newer; this host exceeds that requirement. CMake did not detect an Xcode version, but the Gearmulator Ninja build completed. The octemu dependency setup, QEMU build, main octemu build, and firmware acquisition were not run for this packet.

## License and provenance inventory

This records notices present in the checked-out source; it does not grant rights beyond those notices. The octamachine README currently declares no project-wide code license. Relevant source notices observed:

| Source | Notice in checkout | Provenance note |
| --- | --- | --- |
| Gearmulator MD/MM | GNU GPL version 3 text in `LICENSE.md`; upstream README identifies GPLv3 | The trace patch modifies this source tree. |
| Gearmulator DSP56300 and mc68k | GNU GPL version 3 text in their `LICENSE.md` files | Separate nested projects with their own notices. |
| AsmJit | Zlib-style license in `source/asmjit/LICENSE.md` | Nested DSP dependency. |
| RmlUi | MIT in `source/3rdparty/RmlUi/LICENSE.txt` | Nested Gearmulator dependency. |
| FreeType | `LICENSE.TXT` describes the FreeType License and GPL alternatives | Keep the selected notice and obligations with any use. |
| Octemu source | MIT for the project's own source in `LICENSE.md` | The README distinguishes source components and built artifacts. |
| Octemu QEMU / DSP outputs | README says the combined QEMU binary combines QEMU GPL-2.0-only with DSP GPL-3.0-only and must not be distributed; `octdsp` is GPL-3.0-only; standalone `octemu` is listed as MIT | This is the upstream project's stated distribution restriction. |
| Elektron firmware tool | MIT in its `LICENSE` | Octemu fetches the pinned upstream source locally. |
| Machinedrum and Octatrack firmware | Not included in these repositories | Users provide their own firmware; no permission to redistribute it is inferred. |

The octemu README and LICENSE and each nested project's notices remain the primary references. This inventory is scoped to the source and build boundary above, not a complete license review of every optional dependency.

## Remaining limits and next action

- The trace patch and `mdLib` build are reproduced from clean, pinned source content.
- No complete Gearmulator application build, Machinedrum firmware boot, octemu build, Octatrack firmware boot, audio comparison, or hardware test was performed.
- The local ignored research trees remain modified; the isolated build left them untouched.
- `references.json` still uses moving branch refs for auxiliary research repositories. Their observed commits are recorded above; a deliberate manifest pinning policy remains a separate maintenance choice.

WP-01 is accepted in PR #4, merged as `29471d01c61bbd8e83aa925157ae8fc4e25ddfa8`. Next: dispatch WP-02 and WP-03. WP-04 and WP-05 still require their source/profile and capture-contract prerequisites.
