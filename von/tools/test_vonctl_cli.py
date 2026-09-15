#!/usr/bin/env python3
"""Contract tests for the vonctl harness and its script shims."""

from __future__ import annotations

import io
import re
import sys
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from vonctl import cli  # noqa: E402
from vonctl.commands import REGISTRY  # noqa: E402
from vonctl.commands.build import BUILDS  # noqa: E402
from vonctl.commands.capture import CAPTURES  # noqa: E402
from vonctl.commands.disasm import DISASM  # noqa: E402
from vonctl.commands.export import EXPORTS  # noqa: E402
from vonctl.commands.trace import TRACES  # noqa: E402

SCRIPTS = ROOT / "scripts"
SHIM = re.compile(r'bin/vonctl" ([^\n"]*)"?\$@"')

RETAINED_SHELL = {"i960-build-inner.sh"}

GROUPS = {
    "trace": set(TRACES),
    "capture": set(CAPTURES),
    "build": set(BUILDS),
    "disasm": set(DISASM),
    "export": set(EXPORTS),
    "ghidra": {"run", "install"},
    "check": {"smoke", "twin", "sharc", "clean-runtime"},
    "fuzz": {"versus", "twin"},
    "hack": {"bout"},
    "sweep": {"sticks"},
    "audit": {"clean-runtime"},
    "i960": {"prototype", "reconstructed", "clean"},
}


def shim_tokens(path: Path) -> list[str] | None:
    match = SHIM.search(path.read_text(encoding="utf-8"))
    return match.group(1).split() if match else None


def test_registry_has_expected_commands() -> None:
    for name in ("status", "test", "preflight", "e2e", "run", "twin", "i960",
                 "trace", "capture", "build", "disasm", "deploy", "check"):
        assert name in REGISTRY, name


def test_scripts_are_shims() -> None:
    for path in sorted(SCRIPTS.glob("*.sh")):
        if path.name in RETAINED_SHELL:
            continue
        tokens = shim_tokens(path)
        assert tokens, f"{path.name} is not a vonctl shim"
        command = tokens[0]
        assert command in REGISTRY, f"{path.name}: unknown command {command!r}"
        if command in GROUPS and len(tokens) > 1:
            assert tokens[1] in GROUPS[command], (
                f"{path.name}: unknown {command} subcommand {tokens[1]!r}"
            )


def test_group_mains_print_names() -> None:
    for name in GROUPS:
        handler = REGISTRY[name]
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            code = handler([])
        assert code == 0, name
        assert "usage:" in buffer.getvalue(), name


def test_unknown_command_exits_2() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        assert cli.main(["definitely-not-a-command"]) == 2


def test_help_exits_0() -> None:
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        assert cli.main(["--help"]) == 0
    assert "vonctl" in buffer.getvalue()


TEST_NAMES = [
    test_registry_has_expected_commands,
    test_scripts_are_shims,
    test_group_mains_print_names,
    test_unknown_command_exits_2,
    test_help_exits_0,
]


def main() -> int:
    for test in TEST_NAMES:
        test()
        print(f"ok {test.__name__}")
    print(f"{len(TEST_NAMES)} vonctl contract tests passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
