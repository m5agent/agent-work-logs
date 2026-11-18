"""Observe loads by the unchanged UIFlow2 guest, never read MMIO via GDB."""
import json
import re
import time

import gdb


API_ENTRY = 0x4825BBC4
ID_COMPARISON = 0x481A1DA8
DSI_HEADER = 0x500A006C
DSI_PAYLOAD = 0x500A0070
DSI_STATUS = 0x500A0074
MEMORY_OP = re.compile(
    r"\s*(?:c\.)?(lw|sw|lwu|lbu|sh|sb)\s+(\w+),\s*"
    r"(-?(?:0x[0-9a-f]+|\d+))\((\w+)\)(?:\s.*)?",
    re.I,
)


def reg(name):
    return int(gdb.selected_frame().read_register(name)) & 0xFFFFFFFF


def breakpoint_at(address):
    return gdb.Breakpoint(f"*{address:#x}", type=gdb.BP_HARDWARE_BREAKPOINT,
                          temporary=True, internal=True)


def read():
    breakpoint_at(API_ENTRY)
    gdb.execute("continue", to_string=True)
    assert reg("pc") == API_ENTRY
    command, size, dest, return_pc = (reg(x) for x in ("a1", "a3", "a2", "ra"))
    impl = int(gdb.parse_and_eval("*(unsigned int*)$a0"))
    assert command == 0 and size == 1
    assert 0x48000000 <= impl < 0x4F000000
    breakpoint_at(impl)
    gdb.execute("continue", to_string=True)
    assert reg("pc") == impl
    deadline = time.monotonic() + 9
    trace = {"command": command, "requested_bytes": size, "driver_entry": impl}
    for _ in range(1000):
        assert time.monotonic() < deadline, "bounded FIFO observation timed out"
        pc = reg("pc")
        assert pc != return_pc, "driver returned before the FIFO load"
        instruction = gdb.selected_frame().architecture().disassemble(pc, count=1)[0]
        match = MEMORY_OP.fullmatch(instruction["asm"].strip())
        if match is not None:
            opcode, value_reg, displacement, base = match.groups()
            address = (reg(base) + int(displacement, 0)) & 0xFFFFFFFF
            if opcode == "sw" and address == DSI_HEADER:
                trace.setdefault("header_words_written", []).append(reg(value_reg))
            if opcode in {"lw", "lwu"} and address in {DSI_STATUS, DSI_PAYLOAD}:
                gdb.execute("stepi", to_string=True)
                assert reg("pc") == pc + instruction["length"]
                word = reg(value_reg)
                if address == DSI_PAYLOAD:
                    trace["rx_payload"] = {"address": address, "pc": pc, "word": word}
                    break
                trace["last_status"] = {"address": address, "pc": pc, "word": word}
                continue
        gdb.execute("stepi", to_string=True)
    else:
        raise RuntimeError("guest did not read the RX FIFO within the instruction bound")
    assert any(value & 0x3f == 0x06 for value in trace.get("header_words_written", []))
    breakpoint_at(return_pc)
    gdb.execute("continue", to_string=True)
    assert reg("pc") == return_pc
    byte = int(gdb.parse_and_eval(f"*(unsigned char*){dest:#x}"))
    trace["api_return"] = {"pc": return_pc, "status": reg("a0"), "byte": byte}
    breakpoint_at(ID_COMPARISON)
    gdb.execute("continue", to_string=True)
    assert reg("pc") == ID_COMPARISON
    actual = [reg("a5")] + [int(gdb.parse_and_eval(f"*(unsigned char*)($sp+{off})"))
                           for off in (25, 26)]
    trace["comparison"] = {"pc": ID_COMPARISON, "actual": actual, "expected_first": reg("s6")}
    print("FIFO_OBSERVATION " + json.dumps(trace, sort_keys=True))


try:
    read()
finally:
    gdb.execute("detach")
