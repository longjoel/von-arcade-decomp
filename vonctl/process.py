"""Subprocess helpers used by the harness command modules."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
import time
from collections.abc import Callable, Iterable, Sequence
from pathlib import Path

from . import config


def merged_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    environment = os.environ.copy()
    environment.update(config.runtime_env())
    if extra:
        environment.update({key: str(value) for key, value in extra.items()})
    return environment


def display(argv: Sequence[object]) -> str:
    return subprocess.list2cmdline([str(arg) for arg in argv])


def run(
    argv: Sequence[object],
    *,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    check: bool = True,
) -> int:
    """Run a command inheriting the console streams."""
    printable = [str(arg) for arg in argv]
    completed = subprocess.run(printable, cwd=cwd, env=merged_env(env))
    if check and completed.returncode != 0:
        raise config.CommandError(
            f"command failed ({completed.returncode}): {display(printable)}",
            completed.returncode,
        )
    return completed.returncode


def run_to_log(
    argv: Sequence[object],
    log_path: Path,
    *,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    check: bool = False,
) -> int:
    """Run a command with stdout+stderr captured to a file."""
    log_path.parent.mkdir(parents=True, exist_ok=True)
    printable = [str(arg) for arg in argv]
    with log_path.open("wb") as stream:
        completed = subprocess.run(
            printable, cwd=cwd, env=merged_env(env), stdout=stream, stderr=subprocess.STDOUT
        )
    if check and completed.returncode != 0:
        raise config.CommandError(
            f"command failed ({completed.returncode}): {display(printable)}",
            completed.returncode,
        )
    return completed.returncode


def _relay(
    stream,
    log_path: Path,
    prefix: str | None,
    match: Callable[[str], bool] | None,
) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8", errors="replace") as log, stream:
        for line in stream:
            log.write(line)
            log.flush()
            if match is not None and match(line):
                label = f"{prefix} " if prefix else ""
                sys.stdout.write(f"{label}{line}")
                sys.stdout.flush()


def spawn_logged(
    argv: Sequence[object],
    log_path: Path,
    *,
    env: dict[str, str] | None = None,
    cwd: Path | None = None,
    prefix: str | None = None,
    match: Callable[[str], bool] | None = None,
) -> subprocess.Popen:
    """Start a command, streaming a copy of its output to the console.

    The full output is always written to `log_path`; `match` decides which
    lines are echoed live (used to surface M2COMM diagnostics from twin runs).
    """
    printable = [str(arg) for arg in argv]
    process = subprocess.Popen(
        printable,
        cwd=cwd,
        env=merged_env(env),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    assert process.stdout is not None
    thread = threading.Thread(
        target=_relay,
        args=(process.stdout, log_path, prefix, match),
        daemon=True,
    )
    thread.start()
    process._von_relay_thread = thread  # type: ignore[attr-defined]
    return process


def wait_any(processes: Iterable[subprocess.Popen]) -> int:
    """Return the exit code of the first process to finish, like `wait -n`."""
    pending = [process for process in processes if process.poll() is None]
    while pending:
        for process in pending:
            code = process.poll()
            if code is not None:
                return code
        time.sleep(0.05)
    return processes[0].returncode if processes else 0


def wait_all(processes: Iterable[subprocess.Popen]) -> int:
    """Wait for every process and return the first nonzero exit code."""
    codes = [process.wait() for process in processes]
    return next((code for code in codes if code), 0)


def toolbox_prefix(name: str | None) -> list[str]:
    """Wrap a command to run inside a toolbox container when requested."""
    if not name:
        return []
    return ["toolbox", "run", "--container", name]


def python_tool(name: str) -> list[str]:
    """Command prefix for a script under von/tools."""
    return [sys.executable, str(config.TOOLS / name)]
