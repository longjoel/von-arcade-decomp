# MAME GDB MCP server

This is a dependency-free MCP server that exposes MAME's `gdbstub` through
probe-oriented tools. It uses stdio for MCP and TCP for MAME's GDB remote
protocol.

Start it from an MCP client with:

```json
{
  "mame-gdb": {
    "command": "python3",
    "args": ["/absolute/path/to/von-arcade-decomp/tools/mame-mcp/mame_mcp.py"]
  }
}
```

Typical flow:

1. Call `mame_start` with `args` such as `["vonj", "-video", "none", "-sound", "none", "-skip_gameinfo"]`.
2. Use `gdb_read_registers`, `gdb_read_memory`, `gdb_breakpoint`, `gdb_step`, or `gdb_continue`.
3. Use `gdb_monitor` for MAME debugger commands, for example `help` or `info schedules`.
4. Call `mame_stop` when finished.

For an externally launched MAME, launch it with:

```text
-debugger gdbstub -debugger_host 127.0.0.1 -debugger_port 23946
```

Then call `mame_connect`. The server selects MAME's first CPU/address space,
which is also the limitation of MAME's current GDB stub implementation.

`gdb_raw` is available for packets not yet wrapped by a named tool. Memory
transfers are capped at 1 MiB per call to keep MCP responses manageable.
