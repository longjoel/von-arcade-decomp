# Agent instructions

## MAME MCP probing

This project includes a dependency-free MCP server at
`tools/mame-mcp/mame_mcp.py`. It speaks MCP over stdio and controls MAME's
GDB remote stub over TCP.

Use it when an investigation needs an interactive, instruction-level probe:

1. Select the target project's MAME executable; for this repository prefer the
   instrumented binary at `bin/von`.
2. Call `mame_start` with the target machine, ROM path, and runtime arguments.
   The server appends
   `-debugger gdbstub -debugger_host 127.0.0.1 -debugger_port 23946`.
3. Save a paused baseline with `mame_save_state` before a slow walk.
4. Use `gdb_run_to_breakpoint` to reach the target function, then
   `gdb_capture_probe` for registers, memory ranges, monitor commands, and
   recent MAME output.
5. Use `mame_load_state` to restore the baseline and repeat one changed probe
   at a time. Use the lower-level `gdb_breakpoint`, `gdb_continue`,
   `gdb_step`, `gdb_read_registers`, `gdb_read_memory`, and `gdb_monitor`
   tools when a composite capture is not sufficient.
6. Preserve useful observations as reproducible metadata, fixtures, or
   deterministic trace checks in the repository.
7. Call `mame_stop` when the probe is complete.

For an already-running custom MAME, use `mame_connect` with its GDB stub
host/port. MAME's GDB stub selects the first CPU and its program address
space; it does not provide arbitrary CPU selection through this server.

Example start arguments for the reconstructed i960 target:

```json
{
  "executable": "/home/longjoel/Work/von-arcade-decomp/bin/von",
  "args": [
    "vonjdev",
    "-rompath",
    "/home/longjoel/Work/von-arcade-decomp/von/build/rompath/reconstructed",
    "-video", "none", "-sound", "none", "-skip_gameinfo"
  ],
  "cwd": "/home/longjoel/Work/von-arcade-decomp"
}
```

Use existing instrumented traces and Lua/C diagnostics for long-running,
coverage-oriented, or regression work. Use MCP for short, targeted probes and
then convert confirmed behavior into the project's normal deterministic
evidence format. `mame_output` captures only the bounded stdout/stderr tail;
project-specific trace files still need their normal logging setup. Do not
assume that a live GDB observation alone is a reproducible result.

The MCP server is configured for an MCP client with:

```json
{
  "mame-gdb": {
    "command": "python3",
    "args": [
      "/home/longjoel/Work/von-arcade-decomp/tools/mame-mcp/mame_mcp.py"
    ]
  }
}
```

Keep unrelated existing worktree changes intact when adding probe artifacts or
updating reconstruction code.
