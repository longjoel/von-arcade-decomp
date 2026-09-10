# MAME GDB MCP server

This is a dependency-free, project-neutral MCP server that exposes any
compatible MAME executable's `gdbstub` through probe-oriented tools. It uses
stdio for MCP and TCP for MAME's GDB remote protocol.

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

1. Call `mame_start` with the desired executable and machine-specific `args`.
   Set `output_file` when the complete MAME stream must be retained for later
   trace correlation; `mame_output` remains useful for bounded live output.
2. Save a paused baseline with `mame_save_state`.
3. Use `gdb_run_to_breakpoint` to reach a function without single-stepping the
   entire run.
4. Use `gdb_capture_probe` to collect registers, selected memory ranges,
   debugger output, and recent MAME stdout/stderr as one evidence record.
5. Use `mame_load_state` to restore the baseline and repeat with one changed
   probe.
6. Call `mame_stop` when finished.

For an externally launched MAME, launch it with:

```text
-debug -debugger gdbstub -debugger_host 127.0.0.1 -debugger_port 23946
```

Then call `mame_connect`. The server selects MAME's first CPU/address space,
which is also the limitation of MAME's current GDB stub implementation.

`mame_output` exposes a bounded, sequence-numbered tail of stdout/stderr from
MAME processes launched by the server. It does not replace project-specific
trace files or Lua/C instrumentation, but it makes short probe evidence easy
to capture without a pipe deadlock.

`gdb_raw` is available for packets not yet wrapped by a named tool. Memory
transfers are capped at 1 MiB per call to keep MCP responses manageable.
