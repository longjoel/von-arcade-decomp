"""Command-line entry point for the Virtual-On harness."""

from __future__ import annotations

import sys

from . import __version__, config
from .commands import REGISTRY

HELP = """\
vonctl - Virtual-On reconstruction harness

usage: vonctl <command> [args...]

Core
  status                     machine-generated project status
  test [suite...]            run manifest-defined test suites
  test-remote [suite...]     run the test suites on the remote host (zathras)
  remote-sync                rsync sources to the remote host (no ROMs)
  check <name>               integration checks: smoke|twin|sharc|clean-runtime
  preflight                  read-only environment readiness report
  e2e                        tests then a headless one-second twin boot
  install                    install build/runtime dependencies
  deploy                     package a ROM-free deployment tarball

Run
  run [mame args...]         run the original ROM set
  twin [mame args...]        run two linked cabinets
  i960 [kind] [args...]      run a generated i960 image (prototype|reconstructed|clean)
  record [human]             human-instrumented capture
  view geometry [model]      serve and open the geometry viewer

Capture and trace
  trace <name> [args...]     trace/capture recipes (vonctl trace --help)
  capture <name> [args...]   audio|bout|single-player|stage-arenas|stage-banks|action-clips
  export <name> [args...]    select-models|stage-arenas
  sandbox                    movement sandbox run
  fuzz versus|twin           input fuzzing
  hack bout                  instrumented hacking run
  sweep sticks               twin-stick mapping sweep
  audit clean-runtime        clean i960 runtime audit

Build
  build <name> [args...]     mame|docker|remote|i960|i960-remote
  disasm <name> [args...]    i960|cpu3|sharc|remote-i960
  ghidra run|install         Ghidra i960 analysis

Run `vonctl <command> --help` for command-specific usage.
"""


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0] in ("-h", "--help"):
        print(HELP)
        return 0
    if argv[0] in ("-V", "--version"):
        print(f"vonctl {__version__}")
        return 0

    name, rest = argv[0], argv[1:]
    handler = REGISTRY.get(name)
    if handler is None:
        print(f"vonctl: unknown command {name!r}\n", file=sys.stderr)
        print(HELP, file=sys.stderr)
        return 2
    try:
        return handler(rest) or 0
    except config.CommandError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return exc.code
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
