"""Command registry for the `vonctl` harness."""

from __future__ import annotations

from .. import config
from . import build, capture, checks, core, disasm, export, ops, remote, run, trace


def _i960(argv: list[str]) -> int:
    kinds = ("prototype", "reconstructed", "clean")
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: vonctl i960 [prototype|reconstructed|clean] [mame args...]")
        return 0
    kind = argv[0] if argv[0] in kinds else "prototype"
    rest = argv[1:] if argv[0] in kinds else argv
    return run.i960(rest, kind=kind)


def _check(argv: list[str]) -> int:
    table = {
        "smoke": checks.smoke,
        "twin": checks.twin,
        "sharc": checks.sharc,
        "clean-runtime": lambda rest: checks.clean_runtime(rest),
    }
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: vonctl check smoke|twin|sharc|clean-runtime")
        return 0
    handler = table.get(argv[0])
    if handler is None:
        raise config.CommandError("usage: vonctl check smoke|twin|sharc|clean-runtime")
    return handler(argv[1:])


REGISTRY = {
    "status": core.status,
    "test": core.test,
    "test-remote": remote.test,
    "remote-sync": remote.sync,
    "preflight": core.preflight,
    "e2e": core.e2e,
    "install": core.install,
    "deploy": core.deploy,
    "check": _check,
    "run": run.run,
    "twin": run.twin,
    "i960": _i960,
    "record": run.record,
    "view": run.view,
    "trace": trace.main,
    "capture": capture.main,
    "export": export.main,
    "build": build.main,
    "disasm": disasm.main,
    "ghidra": disasm.ghidra,
    "fuzz": ops.fuzz,
    "sandbox": ops.sandbox,
    "hack": ops.hack,
    "sweep": ops.sweep,
    "audit": ops.audit,
}
