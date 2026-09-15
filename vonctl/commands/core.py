"""Core commands: status, test, preflight, e2e, install, deploy."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tarfile
from datetime import datetime, timezone

from .. import config, process


def _tool(name: str, argv: list[str], *, cwd=config.ROOT, check: bool = True) -> int:
    return process.run(process.python_tool(name) + argv, cwd=cwd, check=check)


def status(argv: list[str]) -> int:
    """Machine-generated project status (delegates to project_status.py)."""
    return _tool("project_status.py", argv)


def test(argv: list[str]) -> int:
    """Run manifest-defined test suites (default: unit contract)."""
    suites = argv or ["unit", "contract"]
    return _tool("run_tests.py", suites)


def install(argv: list[str]) -> int:
    """Install build/runtime dependencies (Homebrew on macOS)."""
    if shutil.which("brew") is None:
        print(
            "Homebrew not found; use your Linux distribution packages for "
            "MAME build/runtime dependencies."
        )
    else:
        process.run(["brew", "install", "mesa", "alsa-lib", "sdl2", "sdl2_ttf", "pipewire"])
        print("Homebrew dependencies installed.")
    print(f"Build remotely with `vonctl build remote`, or locally with `vonctl build mame`.")
    return 0


def preflight(argv: list[str]) -> int:
    """Read-only environment readiness report for agent sessions."""
    failures = 0
    advisories = 0

    def need(name: str) -> None:
        nonlocal failures
        if shutil.which(name):
            print(f"READY     {name}")
        else:
            print(f"MISSING   {name} (required)")
            failures += 1

    def want(label: str, argv: list[str], reason: str) -> None:
        nonlocal advisories
        try:
            code = subprocess.run(
                argv, capture_output=True, env=process.merged_env()
            ).returncode
        except OSError:
            code = 1
        if code == 0:
            print(f"READY     {label}")
        else:
            print(f"GAP       {label} -- {reason}")
            advisories += 1

    need("cc")
    need("python3")
    need("git")

    want("gh auth", ["gh", "auth", "status"], "push/fetch need a valid GitHub token")
    want("docker", ["docker", "info"], "i960 image build needs the daemon")
    want("sudo docker", ["sudo", "-n", "docker", "info"], "image build here needs sudo")
    want(
        "ssh drone0",
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", "drone0", "true"],
        "remote builds need drone0 reachability",
    )
    want("MAME binary", ["test", "-x", str(config.mame_bin())], "traces and smoke need bin/von")
    want(
        "staged ROMs",
        ["test", "-d", str(config.build_dir() / "disasm" / "rompath" / "vonj")],
        "traces need staged ROMs",
    )
    want(
        "attract coverage",
        ["test", "-f", str(config.build_dir() / "attract-coverage" / "vonj-attract-60s.json")],
        "worklist regen needs the coverage report",
    )
    want("i960 toolchain", ["sh", "-c", "command -v i960-elf-gcc"], "only via docker/drone0 here")

    print(f"required failures: {failures}, advisory gaps: {advisories}")
    return 0 if failures == 0 else 1


def e2e(argv: list[str]) -> int:
    """Run the test suites, then a headless one-second twin boot."""
    test(argv)
    set_name = config.env("VON_SET", "vonj")
    print(f"Booting {set_name} headlessly for one second...")
    from . import run as run_cmd

    return run_cmd.twin(
        ["-window", "-video", "none", "-sound", "none", "-skip_gameinfo", "-seconds_to_run", "1"],
        env={"SDL_VIDEODRIVER": config.env("SDL_VIDEODRIVER", "dummy") or "dummy"},
    )


def deploy(argv: list[str]) -> int:
    """Run tests and package a ROM-free deployment tarball."""
    process.require_command("tar")
    test([])

    version = config.env("VON_VERSION") or datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )
    package = f"von-arcade-decomp-{version}"
    stage = config.build_dir() / "deploy" / package
    dist = config.ROOT / "dist"

    if stage.exists():
        shutil.rmtree(stage)
    (stage / "bin").mkdir(parents=True)
    (stage / "scripts").mkdir()
    (stage / "von" / "tools").mkdir(parents=True)

    shutil.copy2(config.mame_bin(), stage / "bin" / "von")
    shutil.copy2(config.ROOT / "bin" / "vonctl", stage / "bin" / "vonctl")
    shutil.copytree(config.ROOT / "vonctl", stage / "vonctl")
    for name in ("README.md", "rom_manifest.json"):
        shutil.copy2(config.ROOT / "von" / name, stage / "von" / name)
    for name in ("mame_runner.py", "rom_audit.py"):
        shutil.copy2(config.TOOLS / name, stage / "von" / "tools" / name)
    for name in ("run.sh", "run-twin.sh"):
        shutil.copy2(config.ROOT / "scripts" / name, stage / "scripts" / name)
    for path in (stage / "bin" / "vonctl", stage / "bin" / "von", stage / "scripts" / "run.sh",
                 stage / "scripts" / "run-twin.sh"):
        path.chmod(0o755)

    dist.mkdir(parents=True, exist_ok=True)
    archive = dist / f"{package}.tar.gz"
    with tarfile.open(archive, "w:gz") as tar:
        tar.add(stage, arcname=package)
    print(f"Created {archive}")
    print("ROMs are intentionally excluded from the deployment package.")
    return 0
