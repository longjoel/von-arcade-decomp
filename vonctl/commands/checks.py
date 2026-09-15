"""Integration checks: MAME smoke, twin diagnostic matrix, SHARC, clean runtime."""

from __future__ import annotations

import glob
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from .. import config, process


def _run(argv: list[str], *, env: dict[str, str] | None = None, cwd=None, check: bool = True) -> int:
    return process.run(argv, env=env, cwd=cwd, check=check)


def _configured_set() -> str:
    return config.env("VON_SET", "vonj") or "vonj"


def smoke(argv: list[str]) -> int:
    """Port of scripts/test-mame-smoke.sh."""
    config.require_command("python3")
    mame = config.require_mame()

    _run(process.python_tool("rom_audit.py"), cwd=config.ROOT)
    staging = config.prepare_rom_path()
    try:
        listing = subprocess_output([str(mame), "-listfull"])
        for name in ("vonj", "vonu", "vonjdev"):
            if not re.search(rf"(?m)^{re.escape(name)}\s", listing):
                raise config.CommandError(f"{name} driver is not present in the built target")
        _run([str(mame), "vonj", "-rompath", str(staging), "-validate"])
        prototype = config.build_dir() / "i960" / "prototype-maincpu.bin"
        if prototype.is_file():
            _run([str(mame), "vonjdev", "-rompath", str(staging), "-validate"])
        clean_runtime([], seconds=config.env_int("VON_CLEAN_AUDIT_SECONDS", 1))
    finally:
        config.cleanup_rom_path(staging)
    print("MAME smoke suite passed.")
    return 0


def subprocess_output(argv: list[str]) -> str:
    import subprocess

    completed = subprocess.run(argv, capture_output=True, text=True, env=process.merged_env())
    if completed.returncode != 0:
        raise config.CommandError(
            f"command failed ({completed.returncode}): {process.display(argv)}"
        )
    return completed.stdout


def _matches(pattern: str, *paths: Path) -> bool:
    regex = re.compile(pattern)
    for path in paths:
        if path.is_file() and regex.search(path.read_text(encoding="utf-8", errors="replace")):
            return True
    return False


def _twin_cases(matrix: str) -> list[tuple[str, str]]:
    if matrix == "default":
        return [("ff", "ff")]
    if matrix == "targeted":
        cases = [("ff", "ff")]
        for bit in range(8):
            value = f"{0xFF ^ (1 << bit):02x}"
            cases.append((value, "ff"))
            cases.append((value, value))
        return cases
    if matrix == "full":
        return [(f"{value:02x}", "ff") for value in range(256)]
    raise config.CommandError("VON_TWIN_MATRIX must be default, targeted, or full")


def _twin_cfg(set_name: str, value: str) -> str:
    return (
        '<mameconfig version="10">\n'
        ' <system name="default">\n'
        "  <input>\n"
        f'   <port tag=":SW" type="DIPSWITCH" mask="ff" value="{value}" />\n'
        "  </input>\n"
        " </system>\n"
        "</mameconfig>\n"
    )


def twin(argv: list[str]) -> int:
    """Port of scripts/test-twin.sh (DIP-switch diagnostic matrix)."""
    mame = config.require_mame()
    strings = subprocess_output(["strings", str(mame)]) if _which("strings") else ""
    if "comm_diagnostics" not in strings:
        raise config.CommandError(
            "MAME binary lacks -comm_diagnostics; rebuild the diagnostic MAME binary first"
        )

    set_name = _configured_set()
    seconds = config.env_int("VON_TWIN_SECONDS", 60)
    matrix = config.env("VON_TWIN_MATRIX", "default") or "default"
    preflight = config.env("VON_TWIN_PREFLIGHT", "1") or "1"
    staging = config.prepare_rom_path()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = config.capture_dir() / f"twin-diagnostic-{set_name}-{stamp}"
    lua = config.TOOLS / "twin_diagnostic.lua"
    out_dir.mkdir(parents=True, exist_ok=True)
    results = out_dir / "results.csv"

    header = (
        "case,p1_sw3,p2_sw3,p1_link,p2_link,p1_stable,p2_stable,"
        "p1_battle_candidate,p2_battle_candidate,result,earliest_failure\n"
    )
    results.write_text(header, encoding="utf-8")

    try:
        for number, (p1_sw3, p2_sw3) in enumerate(_twin_cases(matrix), start=1):
            _twin_case(
                mame, staging, out_dir, results, set_name, seconds, preflight,
                lua, number, p1_sw3, p2_sw3,
            )
    finally:
        config.cleanup_rom_path(staging)
    print(f"Twin diagnostic results: {results}")
    return 0


def _twin_case(mame, staging, out_dir, results, set_name, seconds, preflight, lua,
               number, p1_sw3, p2_sw3) -> None:
    name = f"case-{number}"
    case_dir = out_dir / name
    p1 = case_dir / "p1"
    p2 = case_dir / "p2"
    for cabinet, value in ((p1, p1_sw3), (p2, p2_sw3)):
        for sub in ("cfg", "nvram", "inp", "snap"):
            (cabinet / sub).mkdir(parents=True, exist_ok=True)
        (cabinet / "cfg" / f"{set_name}.cfg").write_text(
            _twin_cfg(set_name, value), encoding="utf-8"
        )

    base = [
        str(mame), set_name, "-rompath", str(staging),
        "-comm_localhost", "127.0.0.1", "-comm_framesync", "-comm_diagnostics",
        "-autoboot_script", str(lua),
        "-video", "none", "-sound", "none", "-skip_gameinfo", "-nothrottle",
        "-verbose", "-oslog",
    ]
    p1_cmd = base + [
        "-cfg_directory", str(p1 / "cfg"), "-nvram_directory", str(p1 / "nvram"),
        "-input_directory", str(p1 / "inp"), "-snapshot_directory", str(p1 / "snap"),
        "-comm_localport", "12340", "-comm_remotehost", "127.0.0.1",
        "-comm_remoteport", "12341", "-comm_master",
    ]
    p2_cmd = base + [
        "-cfg_directory", str(p2 / "cfg"), "-nvram_directory", str(p2 / "nvram"),
        "-input_directory", str(p2 / "inp"), "-snapshot_directory", str(p2 / "snap"),
        "-comm_localport", "12341", "-comm_remotehost", "127.0.0.1",
        "-comm_remoteport", "12340",
    ]
    env_common = {"SDL_VIDEODRIVER": config.env("SDL_VIDEODRIVER", "dummy") or "dummy",
                  "VON_TWIN_PREFLIGHT": preflight}
    p1_proc = process.spawn_logged(
        p1_cmd, p1 / "mame.log", env={**env_common, "VON_TWIN_LOG": str(p1 / "twin_diagnostic.lua.log"),
                                      "VON_TWIN_ROLE": "master"}
    )
    p2_proc = process.spawn_logged(
        p2_cmd, p2 / "mame.log", env={**env_common, "VON_TWIN_LOG": str(p2 / "twin_diagnostic.lua.log"),
                                      "VON_TWIN_ROLE": "slave"}
    )
    process.wait_all([p1_proc, p2_proc])

    p1_log, p2_log = p1 / "mame.log", p2 / "mame.log"
    p1_lua, p2_lua = p1 / "twin_diagnostic.lua.log", p2 / "twin_diagnostic.lua.log"
    p1_link = _matches("diag link-state=established", p1_log)
    p2_link = _matches("diag link-state=established", p2_log)
    p1_stable = p1_link and not _matches("diag link-state=failed", p1_log)
    p2_stable = p2_link and not _matches("diag link-state=failed", p2_log)
    p1_battle = _matches("battle-screen-change", p1_lua)
    p2_battle = _matches("battle-screen-change", p2_lua)

    result, stage = "fail", "socket-setup"
    if (p1_link or p2_link) and not (p1_stable and p2_stable):
        stage = "link-stability"
    elif p1_stable and p2_stable:
        stage = "menu-synchronization"
        if p1_battle and p2_battle:
            result, stage = "pass", "none"
    elif _matches(
        "listen on socket|connect to socket|diag packet id=ff|diag packet id=fe", p1_log, p2_log
    ):
        stage = "handshake"

    with results.open("a", encoding="utf-8") as handle:
        handle.write(
            f"{name},{p1_sw3},{p2_sw3},{int(p1_link)},{int(p2_link)},"
            f"{int(p1_stable)},{int(p2_stable)},{int(p1_battle)},{int(p2_battle)},"
            f"{result},{stage}\n"
        )


def sharc(argv: list[str]) -> int:
    """Port of scripts/test-sharc-recovered.sh."""
    tests = sorted(glob.glob(str(config.TOOLS / "test_recovered_sharc_*.py")))
    tests += [
        str(config.TOOLS / "test_sharc_service_contract.py"),
        str(config.TOOLS / "test_sharc_precision_fixtures.py"),
        str(config.TOOLS / "test_sharc_40bit_reference.py"),
    ]
    for path in tests:
        process.run([sys.executable, path], cwd=config.ROOT)
    print(f"SHARC recovered-model checkpoint passed: {len(tests)} tests.")
    return 0


def _which(name: str) -> str | None:
    import shutil

    return shutil.which(name)


def clean_runtime(argv: list[str], *, seconds: int | None = None) -> int:
    """Port of scripts/audit-i960-clean-runtime.sh."""
    mame = config.require_mame()
    seconds = config.env_int("VON_CLEAN_AUDIT_SECONDS", 8) if seconds is None else seconds
    base = config.build_dir() / "i960" / "clean-audit"
    output = config.env_path("VON_CLEAN_AUDIT_OUTPUT_DIR", base)
    output.mkdir(parents=True, exist_ok=True)
    run_dir = Path(
        __import__("tempfile").mkdtemp(prefix="run-", dir=output)
    )
    print(f"Clean audit capture: {run_dir}")
    pc_log = run_dir / f"clean-{seconds}s.pcs"
    progress_log = run_dir / f"clean-{seconds}s.progress"
    run_log = run_dir / f"clean-{seconds}s.log"
    rom_path = config.build_dir() / "rompath" / "reconstructed-clean"
    manifest = config.build_dir() / "i960" / "reconstructed-clean-maincpu.manifest.json"

    if not (rom_path / "vonjdev" / "prototype-maincpu.bin").exists():
        _build_i960()
    if not manifest.is_file():
        raise config.CommandError(f"clean image manifest is missing: {manifest}")

    mame_status = process.run_to_log(
        [
            str(mame), "vonjdev", "-rompath", str(rom_path),
            "-debug", "-debugger", "none", "-video", "none", "-sound", "none",
            "-skip_gameinfo", "-nothrottle",
            "-cfg_directory", str(run_dir / "cfg"),
            "-nvram_directory", str(run_dir / "nvram"),
            "-state_directory", str(run_dir / "state"),
            "-autoboot_script", str(config.TOOLS / "trace_i960_attract_coverage.lua"),
            "-seconds_to_run", str(seconds),
        ],
        run_log,
        env={
            "VON_ATTRACT_SECONDS": str(seconds),
            "VON_ATTRACT_PC_LOG": str(pc_log),
            "VON_ATTRACT_PROGRESS_LOG": str(progress_log),
            "SDL_VIDEODRIVER": config.env("SDL_VIDEODRIVER", "dummy") or "dummy",
        },
    )

    audit_status = 0
    if pc_log.is_file() and pc_log.stat().st_size > 0:
        audit_status = process.run(
            process.python_tool("audit_clean_i960_coverage.py")
            + ["--pcs", str(pc_log), "--manifest", str(manifest),
               "--expected-seconds", str(seconds)],
            cwd=config.ROOT,
            check=False,
        )
    else:
        print(f"error: MAME produced no i960 PC coverage: {pc_log}", file=sys.stderr)
        audit_status = 1

    if mame_status != 0:
        raise config.CommandError(f"MAME clean runtime exited with status {mame_status}")
    if _matches(r"Unhandled 00|Unhandled exception|\[LUA ERROR\]", run_log):
        raise config.CommandError(
            f"MAME reported an i960 or instrumentation failure; see {run_log}"
        )
    return audit_status


def _build_i960() -> None:
    from . import build as build_cmd

    build_cmd.i960([])
