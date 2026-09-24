#!/usr/bin/env python3
"""Build and run the WP-06 ColdFire ISA/exception probe on two QEMU CPUs."""

from __future__ import annotations

import argparse
import os
import re
import select
import subprocess
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PROBE = Path(__file__).with_name("cpu_compat.S")
LINKER_SCRIPT = Path(__file__).with_name("an5206.ld")
OUTPUT_ADDRESS = 0x00020000
SUCCESS = 0xC0DEF00D
FAILURE_PREFIX = 0xBAD00000

FIELDS = (
    "result",
    "initial_sp",
    "trap_sp",
    "sp_after_trap",
    "trap_count",
    "arithmetic_pass",
    "trap_frame_fv_sr",
    "trap_stacked_pc",
    "privilege_handler_sp",
    "privilege_frame_fv_sr",
    "privilege_stacked_pc",
    "privilege_count",
    "user_sp_before_privilege",
    "user_sp_after_privilege_return",
    "vbr_alignment_handler",
)
STACK_FIELDS = (
    "result",
    "user_sp_before_trap",
    "supervisor_handler_sp",
    "user_sp_after_rte",
)
IRQ_FIELDS = (
    "result",
    "handlers_before_unmask",
    "timer_status_before_unmask",
    "handler_count_after_unmask",
)
ALIGNMENT_FIELDS = (
    "result",
    "byte_at_base",
    "word_at_even_address",
    "word_at_odd_address",
    "long_at_even_address",
    "long_at_odd_address",
    "long_store_readback_at_odd_address",
)
CAS_FIELDS = (
    "result",
    "cas_memory_after",
)
SELF_MODIFY_FIELDS = (
    "result",
    "first_execution",
    "execution_after_write",
)
CACHE_CONTROL_FIELDS = (
    "result",
    "cpushl_returned",
    "cacr_write_returned",
    "cacr_read_completed",
    "cacr_read_value",
    "memory_after_trap",
)
USER_PRIVILEGE_FIELDS = (
    "result",
    "exception_count",
    "exception_frame",
    "stacked_pc",
    "expected_pc",
    "exception_frame_sp",
    "memory_after_trap",
)


class Monitor:
    def __init__(self, process: subprocess.Popen[bytes]):
        self.process = process
        self.buffer = bytearray()
        self.read_reply()

    def read_reply(self, timeout: float = 3.0) -> str:
        prompt = b"(qemu) "
        deadline = time.monotonic() + timeout
        while prompt not in self.buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise TimeoutError("timed out waiting for the QEMU monitor prompt")
            stdout = self.process.stdout
            if stdout is None:
                raise RuntimeError("QEMU monitor output is unavailable")
            ready, _, _ = select.select([stdout], [], [], remaining)
            if not ready:
                raise TimeoutError("timed out waiting for the QEMU monitor prompt")
            chunk = os.read(stdout.fileno(), 4096)
            if not chunk:
                raise RuntimeError("QEMU monitor closed")
            self.buffer.extend(chunk)
        end = self.buffer.index(prompt) + len(prompt)
        reply = bytes(self.buffer[:end]).decode("utf-8", errors="replace")
        del self.buffer[:end]
        return reply

    def command(self, command: str) -> str:
        stdin = self.process.stdin
        if stdin is None:
            raise RuntimeError("QEMU monitor input is unavailable")
        stdin.write(command.encode("ascii") + b"\n")
        stdin.flush()
        return self.read_reply()


def read_words(reply: str, expected: int) -> list[int]:
    data_lines = [line for line in reply.splitlines() if re.match(r"\s*[0-9a-fA-F]{8}:", line)]
    values = re.findall(r"0x([0-9a-fA-F]{8})", "\n".join(data_lines))
    words = [int(value, 16) for value in values]
    if len(words) != expected:
        raise RuntimeError(f"expected {expected} output words, found {len(words)}: {reply!r}")
    return words


def run_cpu(
    qemu: str,
    elf: Path,
    cpu: str,
    fields: tuple[str, ...] = FIELDS,
    expected_marker: int = SUCCESS,
) -> dict[str, int]:
    command = [
        qemu,
        "-M",
        "an5206",
        "-cpu",
        cpu,
        "-m",
        "4M",
        "-kernel",
        str(elf),
        "-display",
        "none",
        "-serial",
        "null",
        "-monitor",
        "stdio",
    ]
    process = subprocess.Popen(
        command,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    monitor = None
    try:
        monitor = Monitor(process)
        deadline = time.monotonic() + 5.0
        marker = 0
        while time.monotonic() < deadline:
            reply = monitor.command(f"xp /1wx 0x{OUTPUT_ADDRESS:08x}")
            found = read_words(reply, 1)
            marker = found[0] if found else 0
            if marker in (
                SUCCESS,
                FAILURE_PREFIX | 1,
                FAILURE_PREFIX | 2,
                FAILURE_PREFIX | 3,
                FAILURE_PREFIX | 4,
                FAILURE_PREFIX | 8,
            ):
                break
            time.sleep(0.02)
        if marker != expected_marker:
            raise RuntimeError(
                f"{cpu}: expected marker 0x{expected_marker:08x}, got 0x{marker:08x}"
            )
        monitor.command("stop")
        words = read_words(
            monitor.command(f"xp /{len(fields)}wx 0x{OUTPUT_ADDRESS:08x}"),
            len(fields),
        )
        result = dict(zip(fields, words, strict=True))
        if result["result"] != expected_marker:
            raise RuntimeError(f"{cpu}: unexpected result marker 0x{result['result']:08x}")
        return result
    finally:
        if monitor is not None:
            try:
                monitor.command("quit")
            except (BrokenPipeError, OSError, RuntimeError, TimeoutError):
                pass
        if process.poll() is None:
            process.terminate()
        try:
            process.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            process.kill()
        process.wait()


def expect_unimplemented_control_register(qemu: str, elf: Path, name: str) -> None:
    command = [
        qemu,
        "-M",
        "an5206",
        "-cpu",
        "cfv4e",
        "-m",
        "4M",
        "-kernel",
        str(elf),
        "-display",
        "none",
        "-serial",
        "null",
    ]
    try:
        result = subprocess.run(command, capture_output=True, timeout=5, check=False)
    except subprocess.TimeoutExpired as error:
        raise RuntimeError(f"cfv4e unexpectedly continued through the {name} MOVEC") from error
    diagnostic = (result.stdout + result.stderr).decode("utf-8", errors="replace")
    if result.returncode == 0 or "Unimplemented control register write" not in diagnostic:
        raise RuntimeError(
            f"cfv4e did not reject the {name} MOVEC as expected; "
            f"exit={result.returncode}, diagnostic={diagnostic[-500:]!r}"
        )
    print(f"cfv4e rejects MOVEC to {name}; ACR0/ACR1 writes preceded it")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cc", default=os.environ.get("M68K_CC", "m68k-elf-gcc"))
    parser.add_argument(
        "--qemu",
        default=os.environ.get("QEMU_M68K", "qemu-system-m68k"),
    )
    args = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="wp06-") as temp_name:
        temp_dir = Path(temp_name)
        elf = temp_dir / "cpu_compat.elf"
        alignment_elf = temp_dir / "alignment_endian.elf"
        stack_device_elf = temp_dir / "stack_eusp_device_bit.elf"
        stack_emulator_elf = temp_dir / "stack_eusp_emulator_bit.elf"
        irq_elf = temp_dir / "interrupt_mask.elf"
        cas_elf = temp_dir / "cas_model.elf"
        self_modify_elf = temp_dir / "self_modifying_code.elf"
        cache_control_elf = temp_dir / "cache_control.elf"
        user_privilege_elfs = {}
        rambar_elf = temp_dir / "unimplemented_rambar.elf"
        mbar_elf = temp_dir / "unimplemented_mbar.elf"
        build = [
            args.cc,
            "-mcpu=5206e",
            "-nostdlib",
            f"-Wl,-T,{LINKER_SCRIPT}",
            "-o",
            str(elf),
            str(PROBE),
        ]
        subprocess.run(build, check=True, cwd=ROOT)
        alignment_build = [
            args.cc,
            "-mcpu=5206e",
            "-nostdlib",
            f"-Wl,-T,{LINKER_SCRIPT}",
            "-o",
            str(alignment_elf),
            str(Path(__file__).with_name("alignment_endian.S")),
        ]
        subprocess.run(alignment_build, check=True, cwd=ROOT)
        irq_build = [
            args.cc,
            "-mcpu=5206e",
            "-nostdlib",
            f"-Wl,-T,{LINKER_SCRIPT}",
            "-o",
            str(irq_elf),
            str(Path(__file__).with_name("interrupt_mask.S")),
        ]
        subprocess.run(irq_build, check=True, cwd=ROOT)
        cas_build = [
            args.cc,
            "-mcpu=68020",
            "-nostdlib",
            f"-Wl,-T,{LINKER_SCRIPT}",
            "-o",
            str(cas_elf),
            str(Path(__file__).with_name("cas_model.S")),
        ]
        subprocess.run(cas_build, check=True, cwd=ROOT)
        self_modify_build = [
            args.cc,
            "-mcpu=5206e",
            "-nostdlib",
            f"-Wl,-T,{LINKER_SCRIPT}",
            "-o",
            str(self_modify_elf),
            str(Path(__file__).with_name("self_modifying_code.S")),
        ]
        subprocess.run(self_modify_build, check=True, cwd=ROOT)
        cache_control_build = [
            args.cc,
            "-mcpu=5206e",
            "-nostdlib",
            f"-Wl,-T,{LINKER_SCRIPT}",
            "-o",
            str(cache_control_elf),
            str(Path(__file__).with_name("cache_control.S")),
        ]
        subprocess.run(cache_control_build, check=True, cwd=ROOT)
        for probe_kind, name in (
            (0, "user_cpushl"),
            (1, "user_cacr_write"),
            (2, "user_cacr_read"),
        ):
            user_privilege_elf = temp_dir / f"{name}.elf"
            user_privilege_build = [
                args.cc,
                "-mcpu=5206e",
                f"-DPROBE_KIND={probe_kind}",
                "-nostdlib",
                f"-Wl,-T,{LINKER_SCRIPT}",
                "-o",
                str(user_privilege_elf),
                str(Path(__file__).with_name("user_privilege_cache.S")),
            ]
            subprocess.run(user_privilege_build, check=True, cwd=ROOT)
            user_privilege_elfs[name] = user_privilege_elf
        for mask, stack_elf in ((0x20, stack_device_elf), (0x10, stack_emulator_elf)):
            stack_build = [
                args.cc,
                "-mcpu=5475",
                f"-DEUSP_MASK=0x{mask:x}",
                "-nostdlib",
                f"-Wl,-T,{LINKER_SCRIPT}",
                "-o",
                str(stack_elf),
                str(Path(__file__).with_name("stack_eusp.S")),
            ]
            subprocess.run(stack_build, check=True, cwd=ROOT)
        movec_source = Path(__file__).with_name("unimplemented_movec.S")
        for register, control_register in (("RAMBAR0", 0x0C04), ("MBAR", 0x0C0F)):
            movec_build = [
                args.cc,
                "-mcpu=5475",
                f"-DCONTROL_REGISTER=0x{control_register:04x}",
                "-nostdlib",
                f"-Wl,-T,{LINKER_SCRIPT}",
                "-o",
                str(rambar_elf if register == "RAMBAR0" else mbar_elf),
                str(movec_source),
            ]
            subprocess.run(movec_build, check=True, cwd=ROOT)
        results = {
            cpu: run_cpu(args.qemu, elf, cpu)
            for cpu in ("m5206", "cfv4e")
        }
        alignment_results = {
            cpu: run_cpu(args.qemu, alignment_elf, cpu, ALIGNMENT_FIELDS)
            for cpu in ("m5206", "cfv4e")
        }
        irq_results = {
            cpu: run_cpu(args.qemu, irq_elf, cpu, IRQ_FIELDS)
            for cpu in ("m5206", "cfv4e")
        }
        cas_control_result = run_cpu(args.qemu, cas_elf, "m68020", CAS_FIELDS)
        cas_coldfire_results = {
            cpu: run_cpu(
                args.qemu,
                cas_elf,
                cpu,
                CAS_FIELDS,
                expected_marker=FAILURE_PREFIX | 4,
            )
            for cpu in ("m5206", "cfv4e")
        }
        self_modify_results = {
            cpu: run_cpu(args.qemu, self_modify_elf, cpu, SELF_MODIFY_FIELDS)
            for cpu in ("m5206", "cfv4e")
        }
        cache_control_results = {
            cpu: run_cpu(
                args.qemu,
                cache_control_elf,
                cpu,
                CACHE_CONTROL_FIELDS,
                expected_marker=FAILURE_PREFIX | 4,
            )
            for cpu in ("m5206", "cfv4e")
        }
        user_privilege_expected_markers = {
            "user_cpushl": FAILURE_PREFIX | 8,
            "user_cacr_write": FAILURE_PREFIX | 8,
            "user_cacr_read": FAILURE_PREFIX | 4,
        }
        user_privilege_results = {
            (cpu, name): run_cpu(
                args.qemu,
                user_privilege_elf,
                cpu,
                USER_PRIVILEGE_FIELDS,
                expected_marker=user_privilege_expected_markers[name],
            )
            for cpu in ("m5206", "cfv4e")
            for name, user_privilege_elf in user_privilege_elfs.items()
        }
        stack_device_result = run_cpu(args.qemu, stack_device_elf, "cfv4e", STACK_FIELDS)
        stack_emulator_result = run_cpu(args.qemu, stack_emulator_elf, "cfv4e", STACK_FIELDS)
        expect_unimplemented_control_register(args.qemu, rambar_elf, "RAMBAR0")
        expect_unimplemented_control_register(args.qemu, mbar_elf, "MBAR")

    for cpu, values in results.items():
        print(f"{cpu}:")
        for field, value in values.items():
            print(f"  {field}: 0x{value:08x}")
    if results["m5206"] != results["cfv4e"]:
        print("CPU outputs differ")
        return 1
    print("CPU outputs match")
    print("data alignment and big-endian memory access:")
    for cpu, values in alignment_results.items():
        print(f"{cpu}: {values}")
    expected_alignment = {
        "result": SUCCESS,
        "byte_at_base": 0x12,
        "word_at_even_address": 0x1234,
        "word_at_odd_address": 0x3456,
        "long_at_even_address": 0x12345678,
        "long_at_odd_address": 0x34567800,
        "long_store_readback_at_odd_address": 0xA1B2C3D4,
    }
    if (
        alignment_results["m5206"] != expected_alignment
        or alignment_results["cfv4e"] != expected_alignment
    ):
        print("data alignment/byte-order result differed from the expected big-endian values")
        return 1
    print("aligned and odd-address byte/word/long operations match on both CPU models")
    print("level-4 timer interrupt with SR.I mask:")
    for cpu, values in irq_results.items():
        print(f"{cpu}: {values}")
    expected_irq = {
        "result": SUCCESS,
        "handlers_before_unmask": 0,
        "timer_status_before_unmask": 2,
        "handler_count_after_unmask": 1,
    }
    if irq_results["m5206"] != expected_irq or irq_results["cfv4e"] != expected_irq:
        print("interrupt masking or delivery differed from the expected CPU-model result")
        return 1
    if irq_results["m5206"] != irq_results["cfv4e"]:
        print("interrupt outputs differ")
        return 1
    print("CAS instruction decoding:")
    print(f"m68020 control: {cas_control_result}")
    for cpu, values in cas_coldfire_results.items():
        print(f"{cpu}: {values}")
    if cas_control_result != {"result": SUCCESS, "cas_memory_after": 0x87654321}:
        print("CAS control result changed; check the known 68020 instruction encoding")
        return 1
    expected_cas_trap = {"result": FAILURE_PREFIX | 4, "cas_memory_after": 0x12345678}
    if any(values != expected_cas_trap for values in cas_coldfire_results.values()):
        print("a ColdFire QEMU model did not take the expected illegal-instruction vector for CAS")
        return 1
    print("CAS executes on the 68020 control model and takes vector 4 on both ColdFire models")
    print("self-modifying code in RAM:")
    for cpu, values in self_modify_results.items():
        print(f"{cpu}: {values}")
    expected_self_modify = {
        "result": SUCCESS,
        "first_execution": 1,
        "execution_after_write": 2,
    }
    if any(values != expected_self_modify for values in self_modify_results.values()):
        print("the code-write probe did not execute the updated instruction on both CPU models")
        return 1
    print("both CPU models execute the replacement instruction after a RAM code write")
    print("cache-control instructions and CACR model behavior:")
    for cpu, values in cache_control_results.items():
        print(f"{cpu}: {values}")
    expected_cache_control = {
        "result": FAILURE_PREFIX | 4,
        "cpushl_returned": 1,
        "cacr_write_returned": 1,
        "cacr_read_completed": 0,
        "cacr_read_value": 0,
        "memory_after_trap": 0x13579BDF,
    }
    if any(values != expected_cache_control for values in cache_control_results.values()):
        print("the pinned cache-control/CACR behavior changed")
        return 1
    print("both models execute supervisor CPUSHL and CACR write, then take vector 4 on CACR read")
    print("user-mode cache-control privilege exceptions:")
    for (cpu, name), values in user_privilege_results.items():
        print(f"{cpu} {name}: {values}")
    for (cpu, name), values in user_privilege_results.items():
        if (
            values["result"] != user_privilege_expected_markers[name]
            or values["exception_count"] != 1
            or values["stacked_pc"] != values["expected_pc"]
            or values["exception_frame_sp"] != 0x00007EF8
            or values["memory_after_trap"] != 0x13579BDF
        ):
            print(f"{cpu} {name} did not produce the expected bounded exception")
            return 1
    print("both models take vector 8 for user-mode CPUSHL/CACR writes and vector 4 for CACR reads")
    print("cfv4e EUSP with MCF54455 manual bit 0x20:")
    for field, value in stack_device_result.items():
        print(f"  {field}: 0x{value:08x}")
    if stack_device_result != {
        "result": SUCCESS,
        "user_sp_before_trap": 0x00007F00,
        "supervisor_handler_sp": 0x00007EF8,
        "user_sp_after_rte": 0x00007F00,
    }:
        print("QEMU's bit-0x20 result changed; compare it with the MCF54455 manual")
        return 1
    print("QEMU did not activate EUSP at the MCF54455-defined bit 0x20")
    print("cfv4e EUSP with QEMU's source-defined bit 0x10:")
    for field, value in stack_emulator_result.items():
        print(f"  {field}: 0x{value:08x}")
    if stack_emulator_result != {
        "result": SUCCESS,
        "user_sp_before_trap": 0x00006000,
        "supervisor_handler_sp": 0x00007EF8,
        "user_sp_after_rte": 0x00006000,
    }:
        print("QEMU's bit-0x10 result changed; update the recorded emulator finding")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
