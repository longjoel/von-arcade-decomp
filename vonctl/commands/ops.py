"""Experiment commands: sandbox, fuzzing, hacking, twin-stick sweep, audit."""

from __future__ import annotations

import csv
import math
import subprocess
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

from .. import config, process


def _disasm() -> Path:
    return config.build_dir() / "disasm"


def _stage_rom_path() -> Path:
    rom_path = _disasm() / "rompath"
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError(f"staged ROM path is missing: {rom_path / 'vonj'}")
    return rom_path


def sandbox(argv: list[str], env: dict[str, str] | None = None) -> int:
    """Movement sandbox, single-cabinet 2P (port of scripts/sandbox-versus.sh)."""
    override = env or {}

    def setting(name: str, default: str | None = None) -> str | None:
        return override.get(name) if name in override else config.env(name, default)

    mame = config.mame_bin()
    config.require_file(mame, "MAME binary")
    set_name = setting("VON_SANDBOX_SET", "vonj") or "vonj"
    rompath_override = setting("VON_SANDBOX_ROMPATH", "")
    rom_path = Path(rompath_override) if rompath_override else _stage_rom_path()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_override = setting("VON_SANDBOX_OUT", "")
    out_dir = Path(out_override) if out_override else config.ROOT / "von" / "sandbox" / f"sandbox-{stamp}"
    seconds = int(setting("VON_SANDBOX_SECONDS", "1200") or "1200")
    for sub in ("cfg", "nvram", "inp"):
        (out_dir / sub).mkdir(parents=True, exist_ok=True)
    print(f"out: {out_dir}  budget: {seconds}s  set: {set_name}")

    run_env = {
        "VON_SANDBOX_LOG": str(out_dir / "sandbox.log"),
        "VON_SANDBOX_FREEZE": config.env("VON_SANDBOX_FREEZE", "1") or "1",
        "VON_SANDBOX_RECON": config.env("VON_SANDBOX_RECON", "8") or "8",
        "VON_SANDBOX_WEAPON_CASE": config.env("VON_SANDBOX_WEAPON_CASE", "left") or "left",
        "VON_SANDBOX_SHOT_INTERVAL": config.env("VON_SANDBOX_SHOT_INTERVAL", "6") or "6",
        "VON_SANDBOX_WEAPON_LOG": config.env("VON_SANDBOX_WEAPON_LOG", "0") or "0",
        "VON_SANDBOX_WEAPON_WRITES": config.env("VON_SANDBOX_WEAPON_WRITES", "0") or "0",
        "VON_SANDBOX_SINGLE_PLAYER": config.env("VON_SANDBOX_SINGLE_PLAYER", "0") or "0",
        "VON_SANDBOX_ACTIVE_LEVELS": config.env("VON_SANDBOX_ACTIVE_LEVELS", "0") or "0",
        **override,
    }
    process.run_to_log([
        str(mame), set_name, "-rompath", str(rom_path),
        "-video", "none", "-sound", "none", "-nothrottle", "-skip_gameinfo",
        "-cfg_directory", str(out_dir / "cfg"),
        "-nvram_directory", str(out_dir / "nvram"),
        "-input_directory", str(out_dir / "inp"),
        "-autoboot_script", str(config.TOOLS / "sandbox_versus.lua"),
        "-seconds_to_run", str(seconds),
    ], out_dir / "mame.log", env=run_env, cwd=out_dir)
    print(f"done: {out_dir}")
    return 0


def fuzz(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: vonctl fuzz versus|twin")
        return 0
    name = argv[0]
    if name == "versus":
        return _fuzz_versus(argv[1:])
    if name == "twin":
        return _fuzz_twin(argv[1:])
    raise config.CommandError("usage: vonctl fuzz versus|twin")


def _fuzz_versus(argv: list[str]) -> int:
    mame = config.env_path("VON_MAME_BIN", config.ROOT / "bin" / "von")
    config.require_file(mame, "MAME binary")
    rom_path = _stage_rom_path()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = config.env_path("VON_FUZZVERSUS_OUT", config.ROOT / "von" / "fuzz-versus" / f"fuzz-{stamp}")
    seconds = config.env_int("VON_FUZZVERSUS_SECONDS", 240)
    t0 = config.env_int("VON_FUZZ_T0", 7200)
    oslog = ["-oslog"] if config.env("VON_FUZZVERSUS_OSLOG") else []
    for sub in ("cfg", "nvram", "inp", "snaps"):
        (out_dir / sub).mkdir(parents=True, exist_ok=True)
    print(f"out: {out_dir}  budget: {seconds}s  steps: {config.env('VON_FUZZ_SELECT_STEPS', '0')}  "
          f"only: {config.env('VON_FUZZ_ONLY', 'all') or 'all'}")

    run_env = {
        "VON_FUZZ_LOG": str(out_dir / "fuzz.log"),
        "VON_FUZZ_SNAP_DIR": str(out_dir / "snaps"),
        "VON_FUZZ_COIN": str(t0),
        "VON_FUZZ_COIN2": str(t0 + 60),
        "VON_FUZZ_NO_START": "1",
        "VON_FUZZ_START2": str(t0 + 200),
        "VON_FUZZ_SELECT_FRAME": str(t0 + 950),
        "VON_FUZZ_SELECT_STEPS": config.env("VON_FUZZ_SELECT_STEPS", "0") or "0",
        "VON_FUZZ_SELECT_DOWN": config.env("VON_FUZZ_SELECT_DOWN", "0") or "0",
        "VON_FUZZ_SELECT_SEQ": config.env("VON_FUZZ_SELECT_SEQ", "") or "",
        "VON_FUZZ_BATTLE": str(config.env_int("VON_FUZZVERSUS_BATTLE", t0 + 2200)),
        "VON_FUZZ_HOLD": config.env("VON_FUZZ_HOLD", "45") or "45",
        "VON_FUZZ_SETTLE": config.env("VON_FUZZ_SETTLE", "45") or "45",
        "VON_FUZZ_ONLY": config.env("VON_FUZZ_ONLY", "") or "",
        "VON_FUZZ_TELEMETRY": config.env("VON_FUZZ_TELEMETRY", "") or "",
        "VON_FUZZ_STATELOG": config.env("VON_FUZZ_STATELOG", "") or "",
        "VON_FUZZ_TAPS": config.env("VON_FUZZ_TAPS", "") or "",
        "VON_GEOMETRY_OBJECT_MAX": config.env("VON_GEOMETRY_OBJECT_MAX", "8000000") or "8000000",
        "VON_FUZZ_SECONDS": str(seconds),
    }
    process.run_to_log([
        str(mame), "vonj", "-rompath", str(rom_path),
        "-video", "none", "-sound", "none", "-nothrottle", "-skip_gameinfo", *oslog,
        "-cfg_directory", str(out_dir / "cfg"),
        "-nvram_directory", str(out_dir / "nvram"),
        "-input_directory", str(out_dir / "inp"),
        "-autoboot_script", str(config.TOOLS / "fuzz_battle_ram.lua"),
        "-seconds_to_run", str(seconds),
    ], out_dir / "mame.log", env=run_env, cwd=out_dir)
    print(f"done: {out_dir}")
    return 0


def _fuzz_twin(argv: list[str]) -> int:
    mame = config.env_path("VON_MAME_BIN", config.mame_bin())
    config.require_file(mame, "MAME binary")
    rom_path = _stage_rom_path()
    out = config.env_path("VON_FUZZ_TWIN_OUT", Path("/tmp/fuzztwin"))
    for sub in ("p1snaps", "p2snaps"):
        (out / sub).mkdir(parents=True, exist_ok=True)
    p1_port = config.env_int("VON_P1_PORT", 12340)
    p2_port = config.env_int("VON_P2_PORT", 12341)
    seconds = config.env_int("VON_FUZZ_SECONDS", 110)
    script = config.TOOLS / "fuzz_battle_ram.lua"

    def launch(role: str, port: int, rport: int, idle: int, log: Path, snaps: Path,
               master: str, coin: str, start: str, extra: dict[str, str]) -> subprocess.Popen:
        env = {
            "SDL_VIDEODRIVER": "dummy",
            "VON_FUZZ_LOG": str(log), "VON_FUZZ_SNAP_DIR": str(snaps),
            "VON_FUZZ_IDLE": str(idle), "VON_FUZZ_SECONDS": str(seconds),
            "VON_FUZZ_COIN": coin, "VON_FUZZ_START": start,
            "VON_FUZZ_BATTLE": config.env("VON_FUZZ_BATTLE", "2400") or "2400",
            "VON_FUZZ_ONLY": config.env("VON_FUZZ_ONLY", "") or "",
            "VON_FUZZ_HOLD": config.env("VON_FUZZ_HOLD", "45") or "45",
            "VON_FUZZ_SETTLE": config.env("VON_FUZZ_SETTLE", "45") or "45",
            "VON_FUZZ_TAPS": config.env("VON_FUZZ_TAPS", "") or "",
            "VON_FUZZ_TELEMETRY": config.env("VON_FUZZ_TELEMETRY", "") or "",
            **extra,
        }
        command = [
            str(mame), "vonj", "-rompath", str(rom_path), "-verbose",
            "-video", "soft", "-sound", "none", "-skip_gameinfo",
            "-cfg_directory", str(out / f"{role}-cfg"),
            "-nvram_directory", str(out / f"{role}-nvram"),
            "-input_directory", str(out / f"{role}-inp"),
            "-snapshot_directory", str(out / f"{role}-snap"),
            "-comm_localhost", "127.0.0.1", "-comm_localport", str(port),
            "-comm_remotehost", "127.0.0.1", "-comm_remoteport", str(rport),
            "-comm_framesync",
        ]
        if master:
            command.append(master)
        command += ["-autoboot_script", str(script), "-seconds_to_run", str(seconds),
                    "-nothrottle", "-oslog"]
        return process.spawn_logged(command, out / f"{role}-mame.log", env=env)

    p1 = launch("p1", p1_port, p2_port, 0, out / "p1-fuzz.log", out / "p1snaps",
                "-comm_master", config.env("VON_P1_COIN", "900") or "900",
                config.env("VON_P1_START", "1500") or "1500",
                {"VON_FUZZ_COMM_ROLE": "1"})
    p2 = launch("p2", p2_port, p1_port, 1, out / "p2-fuzz.log", out / "p2snaps",
                "", config.env("VON_P2_COIN", "900") or "900",
                config.env("VON_P2_START", "1500") or "1500",
                {"VON_FUZZ_COMM_ROLE": "2"})
    process.wait_all([p1, p2])
    print(f"exit p1={p1.returncode} p2={p2.returncode}")
    return 0


def hack(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: vonctl hack bout")
        return 0
    if argv[0] != "bout":
        raise config.CommandError("usage: vonctl hack bout")
    mame = config.env_path("VON_MAME_BIN", config.ROOT / "bin" / "von-hack")
    config.require_file(mame, "hacking MAME binary")
    rom_path = config.env_path("VON_HACK_ROMPATH", _disasm() / "rompath")
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError(f"ROM path missing: {rom_path / 'vonj'}")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = config.env_path("VON_HACK_OUT", config.capture_dir() / f"hack-{stamp}")
    seconds = config.env_int("VON_HACK_SECONDS", 60)
    for sub in ("snap", "cfg", "nvram"):
        (out_dir / sub).mkdir(parents=True, exist_ok=True)
    process.run_to_log([
        str(mame), "vonj", "-rompath", str(rom_path),
        "-video", "soft", "-sound", "none", "-skip_gameinfo",
        "-debug", "-debugger", "none",
        "-cfg_directory", str(out_dir / "cfg"),
        "-nvram_directory", str(out_dir / "nvram"),
        "-snapshot_directory", str(out_dir / "snap"),
        "-autoboot_script", str(config.TOOLS / "hack_bout.lua"),
        "-seconds_to_run", str(seconds), "-nothrottle", "-oslog", "-verbose",
    ], out_dir / "mame.log", env={
        "SDL_VIDEODRIVER": config.env("SDL_VIDEODRIVER", "dummy") or "dummy",
        "VON_HACK_LOG": str(out_dir / "hack.log"),
        "VON_HACK_SNAP_DIR": str(out_dir / "snap"),
        "VON_HACK_SECONDS": str(seconds),
    })
    print(f"hack capture: {out_dir}")
    return 0


PROBES = [
    "up", "down", "left", "right", "up2", "down2", "left2", "right2",
    "up,up2", "down,down2", "left,left2", "right,right2",
    "up,down2", "down,up2", "right,left2", "left,right2",
    "dash", "shot", "right_shot",
    "up,up2,dash", "up,up2,shot", "right,right2,dash",
]


def sweep(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: vonctl sweep sticks")
        return 0
    if argv[0] != "sticks":
        raise config.CommandError("usage: vonctl sweep sticks")
    from . import capture as capture_cmd

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_root = config.env_path("VON_SWEEP_OUT", config.ROOT / "von" / "sandbox" / f"sweep-{stamp}")
    jobs = config.env_int("VON_SWEEP_JOBS", 6)
    frames = config.env_int("VON_SWEEP_FRAMES", 180)
    out_root.mkdir(parents=True, exist_ok=True)
    print(f"sweep: {len(PROBES)} probes -> {out_root} (jobs={jobs})")

    def run_one(probe: str) -> None:
        tag = probe.replace(",", "+")
        out_dir = out_root / tag
        capture_cmd.bout([], env={
            "VON_BOUT_OUT": str(out_dir),
            "VON_BOUT_PROGRAM": "probe",
            "VON_BOUT_PROBE": probe,
            "VON_BOUT_PROBE_FRAMES": str(frames),
            "VON_BOUT_SECONDS": "200",
        })

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        futures = [pool.submit(run_one, probe) for probe in PROBES]
        for future, probe in zip(futures, PROBES, strict=True):
            try:
                future.result()
            except config.CommandError as exc:
                print(f"probe {probe} failed: {exc}", file=__import__("sys").stderr)

    _sweep_summary(out_root, frames)
    return 0


def _sweep_summary(root: Path, frames: int) -> None:
    base = 9600
    print(f"{'probe':22s} {'travel':>8s} {'dx':>8s} {'dz':>8s} {'dyaw':>8s} {'n':>5s}")
    for tag in sorted(path.name for path in root.iterdir() if path.is_dir()):
        path = root / tag / "bout.csv"
        if not path.is_file():
            continue
        rows = {int(row["frame"]): row for row in csv.DictReader(path.open())}
        ordered = sorted(rows)
        if not ordered:
            continue
        a, b = base - 1, min(base + frames - 1, ordered[-1])
        if a not in rows or b not in rows:
            continue
        x0, z0 = float(rows[a]["p1x"]), float(rows[a]["p1z"])
        x1, z1 = float(rows[b]["p1x"]), float(rows[b]["p1z"])
        dyaw = float(rows[b]["p1yaw"]) - float(rows[a]["p1yaw"])
        print(f"{tag:22s} {math.dist((x0, z0), (x1, z1)):8.2f} {x1 - x0:8.2f} "
              f"{z1 - z0:8.2f} {dyaw:8.2f} {len(ordered):5d}")


def audit(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: vonctl audit clean-runtime")
        return 0
    if argv[0] in ("clean-runtime", "clean"):
        from . import checks

        return checks.clean_runtime(argv[1:])
    raise config.CommandError("usage: vonctl audit clean-runtime")
