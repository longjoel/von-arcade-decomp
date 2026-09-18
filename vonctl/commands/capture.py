"""Capture commands: audio, bout telemetry, per-mech captures, stage banks."""

from __future__ import annotations

import shutil
from datetime import datetime, timezone
from pathlib import Path

from .. import config, process


def _disasm() -> Path:
    return config.build_dir() / "disasm"


def audio(argv: list[str]) -> int:
    """Capture emulated audio to WAV (port of scripts/capture-audio.sh)."""
    mame = config.require_mame()
    seconds = config.env_int("VON_AUDIO_SECONDS", 30)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output = Path(argv[0]) if argv else config.capture_dir() / f"vonj-audio-{stamp}.wav"
    output.parent.mkdir(parents=True, exist_ok=True)
    staging = config.prepare_rom_path()

    audio_args = []
    if config.env("VON_AUDIO_SCRIPT"):
        audio_args = ["-autoboot_script", config.env("VON_AUDIO_SCRIPT", "") or ""]
    log_args = ["-log", "-oslog"] if config.env_flag("VON_MAME_LOG") else []

    print(f"Capturing {seconds} emulated seconds to {output}")
    try:
        process.run([
            str(mame), "vonj", "-rompath", str(staging),
            "-video", "none", "-sound", "sdl",
            "-samplerate", config.env("VON_AUDIO_RATE", "44100") or "44100",
            "-wavwrite", str(output), "-skip_gameinfo", "-nothrottle",
            "-seconds_to_run", str(seconds), *log_args, *audio_args,
        ], env={
            "SDL_VIDEODRIVER": config.env("SDL_VIDEODRIVER", "dummy") or "dummy",
            "SDL_AUDIODRIVER": config.env("SDL_AUDIODRIVER", "dummy") or "dummy",
        }, cwd=config.ROOT)
    finally:
        config.cleanup_rom_path(staging)
    print(f"Wrote {output}")
    return 0


def bout(argv: list[str], env: dict[str, str] | None = None) -> int:
    """Deterministic versus-bout telemetry (port of scripts/capture-bout.sh)."""
    from . import ops

    override = env or {}

    def setting(name: str, default: str) -> str:
        return override[name] if name in override else (config.env(name, default) or default)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_dir = Path(setting("VON_BOUT_OUT", str(config.capture_dir() / f"bout-{stamp}")))
    out_dir.mkdir(parents=True, exist_ok=True)
    telemetry_path = out_dir / "bout.csv"
    ops.sandbox([], env={
        "VON_SANDBOX_OUT": str(out_dir),
        "VON_SANDBOX_SECONDS": setting("VON_BOUT_SECONDS", "220"),
        "VON_SANDBOX_ACTIVE_LEVELS": setting("VON_BOUT_ACTIVE_LEVELS", "0"),
        "VON_SANDBOX_FREEZE": setting("VON_BOUT_FREEZE", "1"),
        "VON_SANDBOX_PROGRAM": setting("VON_BOUT_PROGRAM", "default"),
        "VON_SANDBOX_PROBE": setting("VON_BOUT_PROBE", ""),
        "VON_SANDBOX_PROBE_FRAMES": setting("VON_BOUT_PROBE_FRAMES", "180"),
        "VON_SANDBOX_WEAPON_CASE": setting("VON_BOUT_WEAPON_CASE", "both"),
        "VON_SANDBOX_TELEMETRY": str(telemetry_path),
        "VON_SANDBOX_SET": setting("VON_BOUT_SET", "vonj"),
        "VON_SANDBOX_ROMPATH": setting("VON_BOUT_ROMPATH", ""),
    })
    row_count = 0
    if telemetry_path.is_file():
        with telemetry_path.open(encoding="utf-8", errors="replace") as telemetry:
            row_count = sum(1 for _ in telemetry)
    # The Lua script opens the CSV at boot, so a header-only file still means
    # MAME never reached the sandbox battle/telemetry phase.
    if row_count < 2:
        raise config.CommandError(
            f"bout capture produced no telemetry: {telemetry_path} "
            f"(inspect {out_dir / 'mame.log'})"
        )
    print(f"bout telemetry: {telemetry_path}")
    return 0


def single_player(argv: list[str], env: dict[str, str] | None = None) -> int:
    """Per-mech original-ROM capture matrix (port of capture-single-player-original.sh)."""
    mame = config.require_mame()
    rom_path = _disasm() / "rompath"
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError(f"original-ROM staging is missing: {rom_path / 'vonj'}")

    count = config.env_int("VON_CAPTURE_SELECTOR_COUNT", 8)
    start = config.env_int("VON_CAPTURE_SELECTOR_START", 0)
    pc_trace = config.env("VON_CAPTURE_ENABLE_PC_TRACE", "0")
    queue_trace = config.env("VON_CAPTURE_QUEUE_TRACE", "0")
    if count < 1:
        raise config.CommandError("VON_CAPTURE_SELECTOR_COUNT must be positive")
    if start < 0:
        raise config.CommandError("VON_CAPTURE_SELECTOR_START must be nonnegative")
    if pc_trace not in ("0", "1"):
        raise config.CommandError("VON_CAPTURE_ENABLE_PC_TRACE must be 0 or 1")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_root = config.env_path("VON_CAPTURE_OUTPUT_ROOT", config.capture_dir())
    run_root = out_root / f"single-player-{stamp}"
    run_root.mkdir(parents=True, exist_ok=True)

    for selector in range(start, start + count):
        run_dir = run_root / f"mech-{selector:02d}"
        (run_dir / "snap").mkdir(parents=True, exist_ok=True)
        print(f"Capturing selector {selector} into {run_dir}")
        debug_args = ["-debug", "-debugger", "none"] if pc_trace == "1" else []
        command = [
            str(mame), "vonj", "-rompath", str(rom_path),
            "-cfg_directory", str(run_dir / "cfg"),
            "-nvram_directory", str(run_dir / "nvram"),
            "-input_directory", str(run_dir / "inp"),
            "-snapshot_directory", str(run_dir / "snap"),
            "-video", "none", "-sound", "none", "-oslog", "-nothrottle", "-skip_gameinfo",
            *debug_args,
            "-autoboot_script", str(config.TOOLS / "capture_single_player.lua"),
        ]
        run_env = {
            "VON_CAPTURE_DIR": str(run_dir),
            "VON_CAPTURE_SELECT_STEPS": str(selector),
            "SDL_VIDEODRIVER": config.env("SDL_VIDEODRIVER", "dummy") or "dummy",
            **(env or {}),
        }
        process.run_to_log(command, run_dir / "mame.log", env=run_env, cwd=config.ROOT)
        if queue_trace != "1":
            process.run(process.python_tool("finalize_single_player_capture.py") + [
                "--capture-dir", str(run_dir), "--selector-steps", str(selector),
                "--mame", str(mame), "--rom", str(rom_path / "vonj" / "epr-18664b.15"),
            ], cwd=config.ROOT)
    print(f"Single-player original-ROM capture matrix: {run_root}")
    return 0


def _mame_default() -> Path:
    return config.env_path("VON_MAME_BIN", config.ROOT / "bin" / "von")


def _stage_rom_path() -> Path:
    rom_path = _disasm() / "rompath"
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError(f"no rompath: {rom_path}")
    return rom_path


def stage_arenas(argv: list[str]) -> int:
    """One geometry trace per stage ordinal (port of capture-stage-arenas.sh)."""
    mame = _mame_default()
    config.require_file(mame, "MAME binary")
    rom_path = _stage_rom_path()
    out_dir = config.env_path("VON_CAPTURE_DIR", _disasm() / "stage-captures")
    out_dir.mkdir(parents=True, exist_ok=True)
    ordinals = (config.env("VON_ORDINALS", "0 1 2 3 4 5 6 7 8 9") or "").split()
    seconds = config.env_int("VON_STAGE_SECONDS", 50)
    for ordinal in ordinals:
        trace = out_dir / f"ord{ordinal}.trace"
        if trace.is_file() and trace.stat().st_size > 0:
            print(f"ord {ordinal}: already captured ({trace})")
            continue
        process.run_to_log([
            str(mame), "vonj", "-rompath", str(rom_path),
            "-video", "none", "-sound", "none", "-oslog",
            "-autoboot_script", str(config.TOOLS / "probe_stage_binding.lua"),
            "-seconds_to_run", str(seconds + 10), "-skip_gameinfo", "-nothrottle",
        ], trace, env={
            "VON_STAGE_LOG": str(out_dir / f"ord{ordinal}.lua.log"),
            "VON_STAGE_ORDINAL": ordinal,
            "VON_STAGE_SECONDS": str(seconds),
            "VON_STAGE_TEXTURE_DUMP": str(out_dir / f"ord{ordinal}-banks"),
            "VON_STAGE_TEXTURE_FRAME": str(seconds * 60 - 120),
        })
        objects = _count(trace, "vonj_geometry_object:")
        print(f"ord {ordinal}: {objects} geometry objects -> {trace}")
    return 0


def stage_banks(argv: list[str]) -> int:
    """Texture RAM + palette per stage ordinal (port of capture-stage-banks.sh)."""
    mame = _mame_default()
    config.require_file(mame, "MAME binary")
    rom_path = _stage_rom_path()
    out_dir = config.env_path("VON_CAPTURE_DIR", _disasm() / "stage-captures")
    out_dir.mkdir(parents=True, exist_ok=True)
    ordinals = (config.env("VON_ORDINALS", "0 1 2 3 4 5 6 7 8 9") or "").split()
    seconds = config.env_int("VON_STAGE_SECONDS", 50)
    for ordinal in ordinals:
        bank_dir = out_dir / f"ord{ordinal}-banks"
        if (bank_dir / "texture-11000000.hex").is_file() and \
           (bank_dir / "texture-11200000.hex").is_file() and \
           (bank_dir / "palette.trace").is_file():
            print(f"ord {ordinal}: banks already captured ({bank_dir})")
            continue
        process.run_to_log([
            str(mame), "vonj", "-rompath", str(rom_path),
            "-video", "none", "-sound", "none",
            "-autoboot_script", str(config.TOOLS / "probe_stage_binding.lua"),
            "-seconds_to_run", str(seconds + 10), "-skip_gameinfo", "-nothrottle",
        ], out_dir / f"ord{ordinal}.banks.mame.log", env={
            "SDL_VIDEODRIVER": "dummy",
            "SDL_AUDIODRIVER": "dummy",
            "VON_STAGE_LOG": str(out_dir / f"ord{ordinal}.banks.log"),
            "VON_STAGE_ORDINAL": ordinal,
            "VON_STAGE_SECONDS": str(seconds),
            "VON_STAGE_TEXTURE_DUMP": str(bank_dir),
            "VON_STAGE_TEXTURE_FRAME": str(seconds * 60 - 120),
            "VON_STAGE_PALETTE_DUMP": str(bank_dir / "palette.trace"),
            "VON_STAGE_SNAPSHOT": str(out_dir / f"ord{ordinal}-reference.png"),
        })
        print(f"ord {ordinal}: banks -> {bank_dir}")
    return 0


def action_clips(argv: list[str]) -> int:
    """Deterministic action schedule + geometry trace (port of capture-action-clips.sh)."""
    mame = _mame_default()
    config.require_file(mame, "MAME binary")
    rom_path = _stage_rom_path()
    seconds = config.env_int("VON_ACTION_SECONDS", 88)
    out_dir = config.env_path("VON_ACTION_OUT", config.build_dir() / "action-clips")
    out_dir.mkdir(parents=True, exist_ok=True)
    trace = out_dir / f"action-twin-{seconds}s.trace"
    action_log = out_dir / f"action-twin-{seconds}s.actions.log"
    process.run_to_log([
        str(mame), "vonj", "-rompath", str(rom_path),
        "-video", "none", "-sound", "none", "-oslog",
        "-autoboot_script", str(config.TOOLS / "action_schedule.lua"),
        "-seconds_to_run", str(seconds), "-skip_gameinfo", "-nothrottle",
    ], trace, env={
        "SDL_VIDEODRIVER": config.env("SDL_VIDEODRIVER", "dummy") or "dummy",
        "VON_ACTION_LOG": str(action_log),
        "VON_ACTION_SECONDS": str(seconds),
        "VON_ACTION_START_FRAME": str(config.env_int("VON_ACTION_START_FRAME", 2120)),
        "VON_ACTION_CYCLES": str(config.env_int("VON_ACTION_CYCLES", 2)),
        "VON_FIFO_MAX": config.env("VON_FIFO_MAX", "1") or "1",
        "VON_GEOMETRY_OBJECT_MAX": config.env("VON_GEOMETRY_OBJECT_MAX", "2000000") or "2000000",
    })
    objects = _count(trace, "vonj_geometry_object:")
    matrices = _count(trace, "vonj_geometry_matrix:")
    print(f"wrote {trace}")
    print(f"wrote {action_log}")
    print(f"geometry: objects={objects} matrices={matrices}")
    return 0


def _count(path: Path, marker: str) -> int:
    import re

    if not path.is_file():
        return 0
    return len(re.findall(re.escape(marker), path.read_text(encoding="utf-8", errors="replace")))


CAPTURES = {
    "audio": audio,
    "bout": bout,
    "single-player": single_player,
    "stage-arenas": stage_arenas,
    "stage-banks": stage_banks,
    "action-clips": action_clips,
}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: vonctl capture <name> [args...]\n")
        print("names:")
        for name in sorted(CAPTURES):
            print(f"  {name}")
        return 0
    name, rest = argv[0], argv[1:]
    handler = CAPTURES.get(name)
    if handler is None:
        raise config.CommandError(
            f"unknown capture {name!r}; expected one of: {', '.join(sorted(CAPTURES))}"
        )
    return handler(rest)
