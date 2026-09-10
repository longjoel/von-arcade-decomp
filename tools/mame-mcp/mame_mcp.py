#!/usr/bin/env python3
"""MCP server for probing a MAME GDB stub.

The server speaks MCP over stdin/stdout and the GDB remote protocol over a
local TCP connection.  It intentionally has no third-party dependencies.
"""

from __future__ import annotations

import json
import os
import re
import select
import socket
import subprocess
import sys
import threading
import time
import xml.etree.ElementTree as ET
from collections import deque
from pathlib import Path
from typing import Any


MAX_MEMORY_TRANSFER = 1024 * 1024


class GdbError(RuntimeError):
    pass


class GdbRemote:
    def __init__(self, host: str, port: int, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.sock: socket.socket | None = None
        self._rx = bytearray()

    @property
    def connected(self) -> bool:
        return self.sock is not None

    def connect(self, wait: float = 0.0) -> None:
        deadline = time.monotonic() + wait
        last_error: Exception | None = None
        while True:
            try:
                self.sock = socket.create_connection((self.host, self.port), self.timeout)
                self.sock.settimeout(self.timeout)
                # MAME stops at startup and sends a stop reply immediately.
                self._drain_initial_packets()
                return
            except OSError as exc:
                last_error = exc
                self.close()
                if time.monotonic() >= deadline:
                    raise GdbError(f"could not connect to MAME GDB stub at {self.host}:{self.port}: {exc}") from exc
                time.sleep(0.05)
        raise GdbError(str(last_error))

    def close(self) -> None:
        if self.sock is not None:
            try:
                self.sock.close()
            finally:
                self.sock = None
        self._rx.clear()

    def _recv(self, count: int = 4096) -> bytes:
        if self.sock is None:
            raise GdbError("not connected")
        try:
            data = self.sock.recv(count)
        except socket.timeout as exc:
            raise GdbError("timed out waiting for MAME GDB stub") from exc
        if not data:
            self.close()
            raise GdbError("MAME GDB stub closed the connection")
        return data

    def _read_byte(self) -> int:
        while not self._rx:
            self._rx.extend(self._recv())
        value = self._rx[0]
        del self._rx[0]
        return value

    def _read_packet(self) -> str | None:
        """Read one remote packet, acknowledging it; ignore standalone ACKs."""
        while True:
            ch = self._read_byte()
            if ch in (ord("+"), ord("-")):
                continue
            if ch == 3:
                continue
            if ch != ord("$"):
                continue
            body = bytearray()
            while True:
                ch = self._read_byte()
                if ch == ord("#"):
                    break
                body.append(ch)
            checksum = bytes([self._read_byte(), self._read_byte()])
            try:
                expected = int(checksum.decode("ascii"), 16)
            except ValueError:
                expected = -1
            if sum(body) & 0xFF != expected:
                self._send_raw(b"-")
                continue
            self._send_raw(b"+")
            return body.decode("ascii", errors="replace")

    def _send_raw(self, data: bytes) -> None:
        if self.sock is None:
            raise GdbError("not connected")
        try:
            self.sock.sendall(data)
        except OSError as exc:
            self.close()
            raise GdbError(f"GDB send failed: {exc}") from exc

    def _drain_initial_packets(self) -> None:
        if self.sock is None:
            return
        ready, _, _ = select.select([self.sock], [], [], min(self.timeout, 0.25))
        if ready:
            self._read_packet()

    def request(self, payload: str, *, wait_reply: bool = True) -> str:
        if not self.connected:
            raise GdbError("not connected")
        encoded = payload.encode("ascii")
        packet = b"$" + encoded + b"#%02x" % (sum(encoded) & 0xFF)
        self._send_raw(packet)
        if not wait_reply:
            return ""
        return self._read_packet() or ""

    def interrupt(self) -> str:
        self._send_raw(b"\x03")
        return self._read_packet() or ""


class MameMcp:
    def __init__(self) -> None:
        self.gdb: GdbRemote | None = None
        self.process: subprocess.Popen[bytes] | None = None
        self.target_xml: str | None = None
        self.output_lines: deque[dict[str, Any]] = deque(maxlen=10_000)
        self.output_seq = 0
        self.output_thread: threading.Thread | None = None
        self.output_file: Any = None

    def _require_gdb(self) -> GdbRemote:
        if self.gdb is None or not self.gdb.connected:
            raise GdbError("MAME GDB stub is not connected; call mame_start or mame_connect first")
        return self.gdb

    def _start(self, args: dict[str, Any]) -> dict[str, Any]:
        if self.process and self.process.poll() is None:
            raise GdbError("MAME is already running")
        executable = str(args.get("executable") or os.environ.get("MAME_BIN") or self._default_mame())
        mame_args = args.get("args", [])
        if not isinstance(mame_args, list) or not all(isinstance(x, str) for x in mame_args):
            raise GdbError("args must be a list of strings")
        host = str(args.get("host", "127.0.0.1"))
        port = int(args.get("port", 23946))
        if not (1 <= port <= 65535):
            raise GdbError("port must be between 1 and 65535")
        # Selecting the provider is not enough: MAME keeps the debugger
        # disabled unless -debug is present.  Add it here so every MCP-launched
        # session reliably reaches the GDB stub's initial stop.
        if "-debug" not in mame_args and "-nodebug" not in mame_args:
            mame_args = [*mame_args, "-debug"]
        command = [executable, *mame_args, "-debugger", "gdbstub", "-debugger_host", host, "-debugger_port", str(port)]
        cwd = args.get("cwd")
        env = os.environ.copy()
        extra_env = args.get("env", {})
        if extra_env:
            if not isinstance(extra_env, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in extra_env.items()):
                raise GdbError("env must be an object of string values")
            env.update(extra_env)
        try:
            self.process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except OSError as exc:
            raise GdbError(f"could not start MAME: {exc}") from exc
        output_file = args.get("output_file")
        if output_file:
            try:
                self.output_file = Path(str(output_file)).open("w", encoding="utf-8")
            except OSError as exc:
                self.process.terminate()
                raise GdbError(f"could not open output_file: {exc}") from exc
        self.output_lines.clear()
        self.output_seq = 0
        self.output_thread = threading.Thread(target=self._capture_output, args=(self.process,), daemon=True)
        self.output_thread.start()
        self.gdb = GdbRemote(host, port, float(args.get("timeout", 5.0)))
        try:
            self.gdb.connect(float(args.get("connect_timeout", 10.0)))
            self._initialize_target()
        except Exception:
            self._stop()
            raise
        return self._status()

    @staticmethod
    def _default_mame() -> str:
        project_binary = Path(__file__).resolve().parents[2] / "bin" / "von"
        if project_binary.is_file():
            return str(project_binary)
        return os.environ.get("MAME_EXECUTABLE", "mame")

    def _connect(self, args: dict[str, Any]) -> dict[str, Any]:
        if self.gdb and self.gdb.connected:
            return self._status()
        self.gdb = GdbRemote(str(args.get("host", "127.0.0.1")), int(args.get("port", 23946)), float(args.get("timeout", 5.0)))
        self.gdb.connect(float(args.get("connect_timeout", 0.0)))
        self._initialize_target()
        return self._status()

    def _initialize_target(self) -> None:
        gdb = self._require_gdb()
        gdb.request("qSupported")
        chunks: list[str] = []
        offset = 0
        while True:
            reply = gdb.request(f"qXfer:features:read:target.xml:{offset:x},fff")
            if not reply or reply[0] not in "ml":
                break
            chunks.append(reply[1:])
            offset += len(reply) - 1
            if reply[0] == "l":
                break
        self.target_xml = "".join(chunks) or None
        # MAME requires the target description to have been requested before g/p.
        gdb.request("Hc0")

    def _stop(self) -> dict[str, Any]:
        if self.gdb:
            self.gdb.close()
        self.gdb = None
        if self.process and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=2)
        code = self.process.poll() if self.process else None
        self.process = None
        if self.output_file:
            self.output_file.close()
            self.output_file = None
        return {"stopped": True, "exit_code": code}

    def _capture_output(self, process: subprocess.Popen[bytes]) -> None:
        if process.stdout is None:
            return
        for raw_line in iter(process.stdout.readline, b""):
            line = raw_line.decode("utf-8", errors="replace").rstrip("\r\n")
            if self.output_file:
                self.output_file.write(line + "\n")
                self.output_file.flush()
            self.output_seq += 1
            self.output_lines.append({"seq": self.output_seq, "time": time.time(), "line": line})

    def _output(self, args: dict[str, Any]) -> dict[str, Any]:
        since = args.get("since", 0)
        if not isinstance(since, int) or since < 0:
            raise GdbError("since must be a non-negative output sequence number")
        limit = args.get("limit", 200)
        if not isinstance(limit, int) or not 1 <= limit <= 10_000:
            raise GdbError("limit must be between 1 and 10000")
        lines = [item for item in self.output_lines if item["seq"] > since]
        return {"lines": lines[-limit:], "next_since": self.output_seq, "dropped_before": self.output_lines[0]["seq"] if self.output_lines else self.output_seq + 1}

    def _status(self) -> dict[str, Any]:
        return {
            "connected": bool(self.gdb and self.gdb.connected),
            "mame_running": bool(self.process and self.process.poll() is None),
            "pid": self.process.pid if self.process else None,
            "host": self.gdb.host if self.gdb else None,
            "port": self.gdb.port if self.gdb else None,
            "exit_code": self.process.poll() if self.process else None,
        }

    def call(self, name: str, args: dict[str, Any]) -> Any:
        if name == "mame_start": return self._start(args)
        if name == "mame_connect": return self._connect(args)
        if name == "mame_stop": return self._stop()
        if name == "mame_status": return self._status()
        if name == "mame_output": return self._output(args)
        gdb = self._require_gdb()
        if name == "gdb_raw":
            payload = args.get("packet")
            if not isinstance(payload, str) or not payload or any(ord(c) < 0x20 for c in payload):
                raise GdbError("packet must be a non-empty printable ASCII string")
            return {"packet": payload, "reply": gdb.request(payload)}
        if name == "gdb_read_memory":
            address, length = self._address_length(args)
            reply = gdb.request(f"m{address:x},{length:x}")
            return {"address": address, "length": length, "hex": reply, "bytes": list(bytes.fromhex(reply)) if reply != "E01" else []}
        if name == "gdb_write_memory":
            address = self._number(args, "address")
            data = args.get("hex")
            if not isinstance(data, str) or len(data) % 2 or not re.fullmatch(r"[0-9a-fA-F]*", data):
                raise GdbError("hex must contain an even number of hexadecimal digits")
            if len(data) // 2 > MAX_MEMORY_TRANSFER:
                raise GdbError(f"write exceeds {MAX_MEMORY_TRANSFER} bytes")
            return {"address": address, "length": len(data) // 2, "reply": gdb.request(f"M{address:x},{len(data)//2:x}:{data}")}
        if name == "gdb_read_registers":
            reply = gdb.request("g")
            return {"hex": reply, "registers": self._decode_registers(reply)}
        if name == "gdb_read_register":
            number = self._number(args, "number")
            return {"number": number, "hex": gdb.request(f"p{number:x}")}
        if name == "gdb_write_register":
            number = self._number(args, "number")
            value = args.get("hex")
            if not isinstance(value, str) or not value or len(value) % 2 or not re.fullmatch(r"[0-9a-fA-F]+", value):
                raise GdbError("hex must contain an even number of hexadecimal digits")
            return {"number": number, "reply": gdb.request(f"P{number:x}={value}")}
        if name == "gdb_continue":
            return {"stop": gdb.request("c")}
        if name == "gdb_step":
            return {"stop": gdb.request("s")}
        if name == "gdb_interrupt":
            return {"stop": gdb.interrupt()}
        if name == "gdb_breakpoint":
            address = self._number(args, "address")
            kind = self._number(args, "kind", default=1)
            remove = bool(args.get("remove", False))
            packet = f"z0,{address:x},{kind:x}" if remove else f"Z0,{address:x},{kind:x}"
            return {"address": address, "remove": remove, "reply": gdb.request(packet)}
        if name == "gdb_monitor":
            command = args.get("command")
            if not isinstance(command, str) or not command:
                raise GdbError("command must be a non-empty string")
            encoded = command.encode("utf-8").hex()
            reply = gdb.request(f"qRcmd,{encoded}")
            try:
                output = bytes.fromhex(reply).decode("utf-8", errors="replace")
            except ValueError:
                output = reply
            return {"command": command, "output": output, "raw": reply}
        if name == "mame_save_state":
            state = self._state_name(args)
            return {"state": state, **self._monitor_text(f"statesave {state}")}
        if name == "mame_load_state":
            state = self._state_name(args)
            return {"state": state, **self._monitor_text(f"stateload {state}")}
        if name == "gdb_run_to_breakpoint":
            address = self._number(args, "address")
            kind = self._number(args, "kind", default=1)
            temporary = bool(args.get("temporary", True))
            set_reply = gdb.request(f"Z0,{address:x},{kind:x}")
            stop = gdb.request("c")
            remove_reply = None
            if temporary:
                remove_reply = gdb.request(f"z0,{address:x},{kind:x}")
            return {"address": address, "stop": stop, "set_reply": set_reply, "remove_reply": remove_reply}
        if name == "gdb_capture_probe":
            return self._capture_probe(args)
        raise GdbError(f"unknown tool: {name}")

    def _monitor_text(self, command: str) -> dict[str, str]:
        reply = self._require_gdb().request(f"qRcmd,{command.encode('utf-8').hex()}")
        try:
            output = bytes.fromhex(reply).decode("utf-8", errors="replace")
        except ValueError:
            output = reply
        return {"output": output, "raw": reply}

    @staticmethod
    def _state_name(args: dict[str, Any]) -> str:
        state = args.get("name")
        if not isinstance(state, str) or not re.fullmatch(r"[A-Za-z0-9_.-]+", state):
            raise GdbError("state name must contain only letters, numbers, '.', '_' or '-'")
        return state

    def _capture_probe(self, args: dict[str, Any]) -> dict[str, Any]:
        gdb = self._require_gdb()
        result: dict[str, Any] = {"output": self._output({"since": args.get("output_since", 0), "limit": args.get("output_limit", 200)})}
        if args.get("registers", True):
            raw = gdb.request("g")
            result["registers"] = {"hex": raw, "decoded": self._decode_registers(raw)}
        memories = args.get("memory", [])
        if not isinstance(memories, list):
            raise GdbError("memory must be a list of {address, length} objects")
        result["memory"] = []
        for item in memories:
            if not isinstance(item, dict):
                raise GdbError("each memory probe must be an object")
            address, length = self._address_length(item)
            raw = gdb.request(f"m{address:x},{length:x}")
            result["memory"].append({"address": address, "length": length, "hex": raw})
        monitors = args.get("monitor", [])
        if not isinstance(monitors, list) or not all(isinstance(command, str) and command for command in monitors):
            raise GdbError("monitor must be a list of non-empty strings")
        result["monitor"] = [self._monitor_text(command) for command in monitors]
        result["captured_at"] = time.time()
        return result

    @staticmethod
    def _number(args: dict[str, Any], key: str, default: int | None = None) -> int:
        value = args.get(key, default)
        if isinstance(value, str):
            try: value = int(value, 0)
            except ValueError: value = None
        if not isinstance(value, int) or value < 0:
            raise GdbError(f"{key} must be a non-negative integer or 0x-prefixed string")
        return value

    def _address_length(self, args: dict[str, Any]) -> tuple[int, int]:
        address = self._number(args, "address")
        length = self._number(args, "length")
        if length > MAX_MEMORY_TRANSFER:
            raise GdbError(f"read exceeds {MAX_MEMORY_TRANSFER} bytes")
        return address, length

    def _decode_registers(self, raw: str) -> list[dict[str, Any]]:
        if not self.target_xml:
            return []
        try:
            root = ET.fromstring(self.target_xml)
        except ET.ParseError:
            return []
        result: list[dict[str, Any]] = []
        offset = 0
        for reg in root.findall(".//reg"):
            bits = int(reg.attrib.get("bitsize", "0"))
            width = bits // 8 * 2
            value = raw[offset:offset + width]
            result.append({"number": len(result), "name": reg.attrib.get("name"), "bits": bits, "hex": value})
            offset += width
        return result


TOOLS = [
    {"name": "mame_start", "description": "Start MAME with its GDB stub enabled and connect to it. Optional output_file preserves the complete MAME stdout/stderr stream for trace evidence.", "inputSchema": {"type": "object", "properties": {"executable": {"type": "string"}, "args": {"type": "array", "items": {"type": "string"}}, "cwd": {"type": "string"}, "env": {"type": "object", "additionalProperties": {"type": "string"}}, "output_file": {"type": "string"}, "host": {"type": "string", "default": "127.0.0.1"}, "port": {"type": "integer", "default": 23946}, "timeout": {"type": "number", "default": 5}, "connect_timeout": {"type": "number", "default": 10}}}},
    {"name": "mame_connect", "description": "Connect to an already-running MAME GDB stub.", "inputSchema": {"type": "object", "properties": {"host": {"type": "string", "default": "127.0.0.1"}, "port": {"type": "integer", "default": 23946}, "connect_timeout": {"type": "number"}}}},
    {"name": "mame_stop", "description": "Disconnect and stop a MAME process started by this server.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "mame_status", "description": "Report MAME process and GDB connection state.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "mame_output", "description": "Read recent stdout/stderr captured from a MAME process started by this server.", "inputSchema": {"type": "object", "properties": {"since": {"type": "integer", "default": 0}, "limit": {"type": "integer", "default": 200}}}},
    {"name": "mame_save_state", "description": "Save the complete paused MAME machine state using the debugger state directory.", "inputSchema": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}},
    {"name": "mame_load_state", "description": "Load a previously saved paused MAME machine state.", "inputSchema": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}},
    {"name": "gdb_read_memory", "description": "Read bytes from the currently selected MAME address space.", "inputSchema": {"type": "object", "required": ["address", "length"], "properties": {"address": {"type": ["integer", "string"]}, "length": {"type": ["integer", "string"]}}}},
    {"name": "gdb_write_memory", "description": "Write hexadecimal bytes to the currently selected MAME address space.", "inputSchema": {"type": "object", "required": ["address", "hex"], "properties": {"address": {"type": ["integer", "string"]}, "hex": {"type": "string"}}}},
    {"name": "gdb_read_registers", "description": "Read all registers and decode names from MAME's target XML.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "gdb_read_register", "description": "Read one GDB register by numeric index.", "inputSchema": {"type": "object", "required": ["number"], "properties": {"number": {"type": ["integer", "string"]}}}},
    {"name": "gdb_write_register", "description": "Write one GDB register by numeric index using target-endian hexadecimal bytes.", "inputSchema": {"type": "object", "required": ["number", "hex"], "properties": {"number": {"type": ["integer", "string"]}, "hex": {"type": "string"}}}},
    {"name": "gdb_continue", "description": "Continue MAME until the next breakpoint, watchpoint, or stop.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "gdb_run_to_breakpoint", "description": "Set a breakpoint, run until it fires, and optionally remove it.", "inputSchema": {"type": "object", "required": ["address"], "properties": {"address": {"type": ["integer", "string"]}, "kind": {"type": ["integer", "string"], "default": 1}, "temporary": {"type": "boolean", "default": True}}}},
    {"name": "gdb_step", "description": "Single-step the selected MAME CPU.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "gdb_interrupt", "description": "Interrupt a running MAME target.", "inputSchema": {"type": "object", "properties": {}}},
    {"name": "gdb_breakpoint", "description": "Set or remove a software breakpoint.", "inputSchema": {"type": "object", "required": ["address"], "properties": {"address": {"type": ["integer", "string"]}, "kind": {"type": ["integer", "string"], "default": 1}, "remove": {"type": "boolean"}}}},
    {"name": "gdb_monitor", "description": "Run a MAME debugger console command through GDB qRcmd.", "inputSchema": {"type": "object", "required": ["command"], "properties": {"command": {"type": "string"}}}},
    {"name": "gdb_capture_probe", "description": "Capture registers, selected memory ranges, MAME output, and debugger commands at the current stop.", "inputSchema": {"type": "object", "properties": {"registers": {"type": "boolean", "default": True}, "memory": {"type": "array", "items": {"type": "object"}}, "monitor": {"type": "array", "items": {"type": "string"}}, "output_since": {"type": "integer", "default": 0}, "output_limit": {"type": "integer", "default": 200}}}},
    {"name": "gdb_raw", "description": "Send one printable ASCII GDB remote packet for an unsupported probe.", "inputSchema": {"type": "object", "required": ["packet"], "properties": {"packet": {"type": "string"}}}},
]


def response(request_id: Any, result: Any = None, error: dict[str, Any] | None = None) -> None:
    message: dict[str, Any] = {"jsonrpc": "2.0", "id": request_id}
    if error is not None: message["error"] = error
    else: message["result"] = result
    sys.stdout.write(json.dumps(message, separators=(",", ":")) + "\n")
    sys.stdout.flush()


def main() -> int:
    server = MameMcp()
    for line in sys.stdin:
        request_id = None
        try:
            request = json.loads(line)
            method = request.get("method")
            request_id = request.get("id")
            if method == "initialize":
                result = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}, "serverInfo": {"name": "mame-gdb", "version": "0.1.0"}}
                response(request_id, result)
            elif method == "notifications/initialized":
                continue
            elif method == "tools/list":
                response(request_id, {"tools": TOOLS})
            elif method == "tools/call":
                params = request.get("params", {})
                result = server.call(str(params.get("name")), params.get("arguments") or {})
                response(request_id, {"content": [{"type": "text", "text": json.dumps(result, indent=2)}], "structuredContent": result})
            elif request_id is not None:
                response(request_id, error={"code": -32601, "message": f"method not found: {method}"})
        except Exception as exc:
            if "request_id" in locals() and request_id is not None:
                response(request_id, error={"code": -32000, "message": str(exc)})
    server._stop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
