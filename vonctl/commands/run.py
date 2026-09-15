"""Run commands: single, twin, i960 images, human recording, geometry viewer."""

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .. import config, process


def _mame_args(argv: list[str]) -> list[str]:
    return argv or ["-window", "-skip_gameinfo"]


def _ctrlr_args() -> list[str]:
    name, path = config.ctrlr_name(), config.ctrlr_path()
    if name and path.is_dir():
        return ["-ctrlr", name, "-ctrlrpath", str(path)]
    return []


def run(argv: list[str], env: dict[str, str] | None = None) -> int:
    """Run the original ROM set (port of scripts/run.sh)."""
    config.require_command("python3")
    mame = config.require_mame()
    set_name = config.env("VON_SET", "vonj") or "vonj"
    staging = config.prepare_rom_path()
    try:
        command = process.python_tool("mame_runner.py") + [
            "--mame", str(mame),
            "--set", set_name,
            "--rom-dir", str(staging),
            "--capture-dir", str(config.capture_dir()),
            "--root", str(config.ROOT),
        ]
        command += _ctrlr_args()
        command += ["--", *_mame_args(argv)]
        return process.run(command, env=env, cwd=config.ROOT, check=False)
    finally:
        config.cleanup_rom_path(staging)


def _port_busy(port: int) -> bool:
    if shutil.which("ss") is None:
        return False
    listing = subprocess.run(["ss", "-ltn"], capture_output=True, text=True).stdout
    return any(f":{port} " in line for line in listing.splitlines())


def _m2comm(line: str) -> bool:
    return line.startswith("M2COMM:")


def twin(argv: list[str], env: dict[str, str] | None = None) -> int:
    """Run two cabinets with isolated state and a synchronized link."""
    mame = config.require_mame()
    set_name = config.env("VON_SET", "vonj") or "vonj"
    p1_port = config.env_int("VON_P1_PORT", 12340)
    p2_port = config.env_int("VON_P2_PORT", 12341)
    for port in (p1_port, p2_port):
        if _port_busy(port):
            raise config.CommandError(f"communication port already in use: {port}")

    staging = config.prepare_rom_path()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    twin_dir = config.capture_dir() / f"twin-{set_name}-{stamp}"
    for cabinet in ("p1", "p2"):
        for sub in ("cfg", "nvram", "inp", "snap"):
            (twin_dir / cabinet / sub).mkdir(parents=True, exist_ok=True)

    geometry_root = config.env("VON_PROGRESS_GEOMETRY_STATE_LOG_ROOT", "")
    args = ["-window", "-skip_gameinfo", "-verbose", *argv, *_ctrlr_args()]
    seconds = config.env("VON_TWIN_SECONDS", "0")
    if seconds not in (None, "", "0"):
        args += ["-seconds_to_run", str(seconds)]
    diagnostics = ["-comm_diagnostics"] if config.env_flag("VON_COMM_DIAGNOSTICS") else []

    print(f"Starting cabinet P1 on comm port {p1_port}")
    print(f"Starting cabinet P2 on comm port {p2_port}")
    print(f"Twin capture directory: {twin_dir}")

    processes: list[subprocess.Popen] = []
    try:
        p1_env = {
            "VON_PROGRESS_LOG": str(twin_dir / "p1" / "progress.lua.log"),
            **(env or {}),
        }
        p2_env = {
            "VON_PROGRESS_LOG": str(twin_dir / "p2" / "progress.lua.log"),
            **(env or {}),
        }
        if geometry_root:
            Path(geometry_root).mkdir(parents=True, exist_ok=True)
            p1_env["VON_PROGRESS_GEOMETRY_STATE_LOG"] = str(Path(geometry_root) / "p1.log")
            p2_env["VON_PROGRESS_GEOMETRY_STATE_LOG"] = str(Path(geometry_root) / "p2.log")

        p1_cmd = [
            str(mame), set_name, "-rompath", str(staging),
        ] + _state_dirs(twin_dir / "p1") + [
            "-comm_localhost", "127.0.0.1", "-comm_localport", str(p1_port),
            "-comm_remotehost", "127.0.0.1", "-comm_remoteport", str(p2_port),
            "-comm_framesync", "-comm_master", *diagnostics, *args,
        ]
        p2_cmd = [
            str(mame), set_name, "-rompath", str(staging),
        ] + _state_dirs(twin_dir / "p2") + [
            "-comm_localhost", "127.0.0.1", "-comm_localport", str(p2_port),
            "-comm_remotehost", "127.0.0.1", "-comm_remoteport", str(p1_port),
            "-comm_framesync", *diagnostics, *args, "-sound", "none",
        ]
        processes.append(
            process.spawn_logged(p1_cmd, twin_dir / "p1" / "mame.log", env=p1_env,
                                 prefix="P1", match=_m2comm)
        )
        processes.append(
            process.spawn_logged(p2_cmd, twin_dir / "p2" / "mame.log", env=p2_env,
                                 prefix="P2", match=_m2comm)
        )
        return process.wait_any(processes)
    finally:
        for proc in processes:
            if proc.poll() is None:
                proc.terminate()
        for proc in processes:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        for port in (p1_port, p2_port):
            Path(f"socket.127.0.0.1:{port}").unlink(missing_ok=True)
        config.cleanup_rom_path(staging)


def _state_dirs(cabinet: Path) -> list[str]:
    return [
        "-cfg_directory", str(cabinet / "cfg"),
        "-nvram_directory", str(cabinet / "nvram"),
        "-input_directory", str(cabinet / "inp"),
        "-snapshot_directory", str(cabinet / "snap"),
    ]


def _i960_rompath(kind: str) -> Path:
    build = config.build_dir()
    if kind == "prototype":
        return build / "rompath"
    if kind == "reconstructed":
        return build / "rompath" / "reconstructed"
    if kind == "clean":
        return build / "rompath" / "reconstructed-clean"
    raise config.CommandError(f"unknown i960 image: {kind!r} (prototype, reconstructed, clean)")


def _ensure_i960(kind: str) -> None:
    rom_path = _i960_rompath(kind)
    marker = rom_path / "vonjdev" / "prototype-maincpu.bin"
    if not marker.exists():
        from . import build as build_cmd

        build_cmd.i960([])
    if not marker.exists():
        raise config.CommandError(f"i960 ROM staging is missing: {marker}")
    if kind in ("reconstructed", "clean"):
        image = Path(os_realdir(marker))
        print(f"Using {kind} i960 ROM: {image} ({image.stat().st_size} bytes)")
        print(hashlib.sha256(image.read_bytes()).hexdigest())


def os_realdir(path: Path) -> str:
    import os

    return os.path.realpath(path)


def i960(argv: list[str], kind: str = "prototype") -> int:
    """Run a generated i960 image (port of scripts/run-i960*.sh)."""
    mame = config.require_mame()
    _ensure_i960(kind)
    rom_path = _i960_rompath(kind)
    return process.run(
        [str(mame), "vonjdev", "-rompath", str(rom_path), *_mame_args(argv)],
        cwd=config.ROOT,
        check=False,
    )


def record(argv: list[str], env: dict[str, str] | None = None) -> int:
    """Human-instrumented capture (port of scripts/record-human.sh)."""
    mame = config.require_mame()
    rom_path = config.build_dir() / "disasm" / "rompath"
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError(f"staged ROM path is missing: {rom_path / 'vonj'}")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = config.env_path("VON_HUMAN_OUT", config.capture_dir() / f"human-{stamp}")
    seconds = config.env_int("VON_HUMAN_SECONDS", 600)
    t0 = config.env("VON_TRACE_T0", "0")
    t1 = config.env("VON_TRACE_T1", "600")
    every = config.env("VON_HUMAN_SNAP_EVERY_S", "10")
    cfg_src_raw = config.env("VON_HUMAN_CFG", str(config.ROOT / "von" / "input-preload" / "cfg"))
    cfg_src = Path(cfg_src_raw) if cfg_src_raw else None

    for sub in ("snaps", "cfg", "nvram", "inp"):
        (out_dir / sub).mkdir(parents=True, exist_ok=True)
    if cfg_src and cfg_src.is_dir():
        for cfg in cfg_src.glob("*.cfg"):
            shutil.copy2(cfg, out_dir / "cfg" / cfg.name)
        print(f"cfg: preloaded from {cfg_src}")
    elif cfg_src:
        print(f"cfg: WARNING source missing ({cfg_src}), starting unmapped", file=sys.stderr)
    else:
        print("cfg: starting unmapped (VON_HUMAN_CFG empty)")
    print(f"out: {out_dir}  budget: {seconds}s  trace window: [{t0}, {t1}]")

    command = [
        str(mame), "vonj", "-rompath", str(rom_path),
        "-sound", "auto", "-skip_gameinfo", "-log", "-oslog",
        "-cfg_directory", str(out_dir / "cfg"),
        "-nvram_directory", str(out_dir / "nvram"),
        "-input_directory", str(out_dir / "inp"),
        "-snapshot_directory", str(out_dir / "snaps"),
        "-autoboot_script", str(config.TOOLS / "record_human_session.lua"),
        "-seconds_to_run", str(seconds),
    ]
    run_env = {
        "VON_TRACE_T0": str(t0),
        "VON_TRACE_T1": str(t1),
        "VON_RECORD_LOG": str(out_dir / "record.log"),
        "VON_WATCH_WRITES": config.env("VON_WATCH_WRITES", "") or "",
        "VON_RECORD_SNAP_DIR": str(out_dir / "snaps"),
        "VON_RECORD_SNAP_EVERY_S": str(every),
        **(env or {}),
    }
    process.run_to_log(command, out_dir / "mame.log", env=run_env, cwd=out_dir)
    print(f"done: {out_dir}")
    return 0


def view(argv: list[str]) -> int:
    """Serve the geometry viewer locally and open it (port of view-geometry.sh)."""
    model = Path(argv[0]) if argv else Path("von/build/disasm/first-match-scenes/p1-first-match.gltf")
    model_path = model if model.is_absolute() else config.ROOT / model
    if not model_path.is_file():
        raise config.CommandError(f"model not found: {model_path}")
    config.require_command("chromium")
    port = config.env_int("VON_GEOMETRY_VIEWER_PORT", 8765)
    relative = model_path.relative_to(config.ROOT).as_posix()
    import urllib.parse

    encoded = urllib.parse.quote(relative)
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1",
         "--directory", str(config.ROOT)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    url = f"http://127.0.0.1:{port}/von/tools/geometry_viewer.html?file={encoded}"
    print(f"Opening {url}\nClose this terminal or press Ctrl-C to stop the local server.")
    subprocess.Popen(["chromium", "--new-window", url], stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL)
    try:
        return server.wait()
    except KeyboardInterrupt:
        server.terminate()
        return 0
