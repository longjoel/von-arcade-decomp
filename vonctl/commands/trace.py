"""Trace commands: geometry, SHARC, i960 coverage, camera, and progress taps."""

from __future__ import annotations

import contextlib
import re
import shutil
from pathlib import Path

from .. import config, process


def _disasm() -> Path:
    return config.build_dir() / "disasm"


def _count(path: Path, marker: str) -> int:
    if not path.is_file():
        return 0
    return len(re.findall(re.escape(marker), path.read_text(encoding="utf-8", errors="replace")))


def _run_mame_to_log(mame: Path, mame_args: list[str], log_path: Path,
                     env: dict[str, str] | None = None, cwd: Path | None = None) -> int:
    return process.run_to_log([str(mame), *mame_args], log_path, env=env, cwd=cwd)


def _summarize(trace: Path) -> None:
    summary = config.TOOLS / "summarize_mame_trace.py"
    if summary.is_file():
        process.run(process.python_tool("summarize_mame_trace.py") + [str(trace)],
                    cwd=config.ROOT, check=False)


def camera(argv: list[str]) -> int:
    mame = config.env_path("VON_MAME_BIN", config.ROOT / "bin" / "von")
    config.require_file(mame, "MAME binary")
    rom_path = _disasm() / "rompath"
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError(f"no rompath: {rom_path}")
    out_dir = config.env_path("VON_CAMERA_DIR", _disasm())
    out_dir.mkdir(parents=True, exist_ok=True)
    seconds = config.env_int("VON_CAMERA_SECONDS", 70)
    ordinal = config.env("VON_CAMERA_ORDINAL", "1")
    trace = out_dir / f"vonj-camera-{ordinal}-{seconds}s.trace"
    lua_log = out_dir / f"vonj-camera-{ordinal}-{seconds}s.lua.log"
    _run_mame_to_log(
        mame,
        ["vonj", "-rompath", str(rom_path), "-video", "none", "-sound", "none", "-oslog",
         "-autoboot_script", str(config.TOOLS / "probe_camera.lua"),
         "-seconds_to_run", str(seconds + 10), "-skip_gameinfo", "-nothrottle"],
        trace,
        env={"SDL_VIDEODRIVER": config.env("SDL_VIDEODRIVER", "dummy") or "dummy",
             "VON_CAMERA_LOG": str(lua_log), "VON_CAMERA_ORDINAL": str(ordinal),
             "VON_CAMERA_SECONDS": str(seconds)},
    )
    objects = _count(trace, "vonj_geometry_object:")
    matrices = _count(trace, "vonj_geometry_matrix:")
    print(f"wrote {trace} (objects={objects} matrices={matrices})")
    return 0


def geometry_buffer(argv: list[str]) -> int:
    mame = config.MAME_DIR / "von"
    config.require_file(mame, "MAME binary")
    toolbox = config.env("VON_TOOLBOX", "von-mame")
    rom_path = _disasm() / "rompath"
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError("staged ROM path is missing")
    out_dir = _disasm()
    seconds = config.env_int("VON_GEOMETRY_SECONDS", 10)
    log_path = out_dir / "vonj-geometry-buffer.log"
    dump = out_dir / "vonj-geometry-buffer.hex"
    trace = out_dir / "vonj-geometry-buffer.trace"
    for stale in [log_path, *out_dir.glob("vonj-geometry-buffer.hex.*")]:
        stale.unlink(missing_ok=True)
    command = process.toolbox_prefix(toolbox) + [
        "env", f"VON_GEOMETRY_BUFFER_LOG={log_path}", f"VON_GEOMETRY_BUFFER_DUMP={dump}",
        str(mame), "vonj", "-rompath", str(rom_path), "-video", "none", "-sound", "none",
        "-oslog", "-autoboot_script", str(config.TOOLS / "trace_geometry_buffer.lua"),
        "-seconds_to_run", str(seconds), "-skip_gameinfo", "-nothrottle",
    ]
    process.run_to_log(command, trace)
    print(f"Wrote {log_path}")
    print(f"Wrote {dump}.N dumps")
    return 0


def _run_twin_capture(seconds: int, script: Path, args: list[str], run_log: Path,
                      env: dict[str, str] | None = None) -> Path:
    from . import run as run_cmd

    from .. import process as proc

    run_log.parent.mkdir(parents=True, exist_ok=True)
    with run_log.open("w", encoding="utf-8") as stream, \
            contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
        run_cmd.twin(args, {"VON_TWIN_SECONDS": str(seconds), "VON_PROGRESS_SECONDS": str(seconds),
                            **(env or {})})
    text = run_log.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"(?m)^Twin capture directory: (.+)$", text)
    if not match:
        raise config.CommandError(f"twin runner did not report a capture directory; see {run_log}")
    twin_dir = Path(match.group(1).strip())
    for cabinet in ("p1", "p2"):
        if not (twin_dir / cabinet / "mame.log").is_file():
            raise config.CommandError(f"twin runner produced no {cabinet} log; see {run_log}")
    return twin_dir


def _extract_geometry_rom() -> Path:
    rom = config.env_path("VON_GEOMETRY_ROM", _disasm() / "geometry-rom.bin")
    if not rom.is_file():
        rom.parent.mkdir(parents=True, exist_ok=True)
        process.run(process.python_tool("extract_geometry_rom.py") + ["--output", str(rom)],
                    cwd=config.ROOT)
    return rom


def _positive_seconds(name: str, default: int) -> int:
    value = config.env_int(name, default)
    if value < 1:
        raise config.CommandError(f"{name} must be a positive integer")
    return value


def geometry_first_match(argv: list[str]) -> int:
    seconds = _positive_seconds("VON_GEOMETRY_FIRST_MATCH_SECONDS", 35)
    rom = _extract_geometry_rom()
    output_root = config.env_path(
        "VON_GEOMETRY_FIRST_MATCH_OUTPUT", _disasm() / "first-match-twin"
    )
    script = config.TOOLS / "gameplay_progress.lua"
    run_log = _disasm() / "geometry-first-match-run.log"
    twin_dir = _run_twin_capture(
        seconds, script,
        ["-video", "none", "-sound", "none", "-oslog", "-nothrottle",
         "-autoboot_script", str(script)],
        run_log, {"VON_PROGRESS_COMBAT": "0"},
    )
    output_dir = output_root / twin_dir.name
    for cabinet in ("p1", "p2"):
        (output_dir / cabinet).mkdir(parents=True, exist_ok=True)
        trace = twin_dir / cabinet / "mame.log"
        process.run(process.python_tool("dump_geometry_objects.py") + [
            "--trace", str(trace), "--rom", str(rom),
            "--output-dir", str(output_dir / cabinet / "objects")], cwd=config.ROOT)
        process.run(process.python_tool("export_geometry_frame_gltf.py") + [
            "--trace", str(trace), "--rom", str(rom),
            "--output", str(output_dir / cabinet / "first-match-frame.gltf"),
            "--max-time", "32.8", "--min-objects", "100"], cwd=config.ROOT)
    print(f"First-match geometry capture: {twin_dir}")
    print(f"Extracted scene and models: {output_dir}")
    return 0


def geometry_material_twin(argv: list[str]) -> int:
    seconds = _positive_seconds("VON_GEOMETRY_MATERIAL_SECONDS", 35)
    rom = _extract_geometry_rom()
    texture_rom = config.env_path(
        "VON_GEOMETRY_TEXTURE_ROM", _disasm() / "texture-pipeline" / "texture-rom.bin"
    )
    bank0 = config.env_path(
        "VON_GEOMETRY_TEXTURE_BANK", _disasm() / "texture-pipeline" / "bank0-primary.bin"
    )
    bank1 = config.env_path(
        "VON_GEOMETRY_TEXTURE_BANK1", _disasm() / "texture-pipeline" / "bank1-primary.bin"
    )
    output_root = config.env_path(
        "VON_GEOMETRY_MATERIAL_OUTPUT", _disasm() / "first-match-material-twin"
    )
    if not (texture_rom.is_file() and bank0.is_file() and bank1.is_file()):
        process.run(process.python_tool("extract_texture_pipeline.py") + [
            "--output-dir", str(bank0.parent)], cwd=config.ROOT)
    script = config.TOOLS / "gameplay_progress.lua"
    run_log = _disasm() / "geometry-material-run.log"
    twin_dir = _run_twin_capture(
        seconds, script,
        ["-video", "none", "-sound", "none", "-oslog", "-nothrottle",
         "-autoboot_script", str(script)],
        run_log, {"VON_PROGRESS_COMBAT": "0"},
    )
    output_dir = output_root / twin_dir.name
    for cabinet in ("p1", "p2"):
        cabinet_dir = output_dir / cabinet
        cabinet_dir.mkdir(parents=True, exist_ok=True)
        trace = twin_dir / cabinet / "mame.log"
        frame = cabinet_dir / "first-match-frame-textured.gltf"
        process.run(process.python_tool("export_geometry_frame_textured_gltf.py") + [
            "--trace", str(trace), "--rom", str(rom), "--texture-rom", str(texture_rom),
            "--bank0", str(bank0), "--bank1", str(bank1), "--palette-trace", str(trace),
            "--output", str(frame), "--max-time", "32.8", "--min-objects", "100"],
            cwd=config.ROOT)
        frame_time = _gltf_trace_time(frame)
        objects = cabinet_dir / "objects"
        process.run(process.python_tool("dump_geometry_objects.py") + [
            "--trace", str(trace), "--rom", str(rom), "--output-dir", str(objects)],
            cwd=config.ROOT)
        textured = cabinet_dir / "textured-objects"
        textured.mkdir(parents=True, exist_ok=True)
        index = objects / "index.tsv"
        if index.is_file():
            for line in index.read_text(encoding="utf-8").splitlines()[1:]:
                fields = line.split("\t")
                if len(fields) < 4 or not fields[1]:
                    continue
                oba, tpa, tha = fields[1], fields[2], fields[3]
                process.run(process.python_tool("export_geometry_textured_gltf.py") + [
                    "--rom", str(rom), "--texture-rom", str(texture_rom),
                    "--bank0", str(bank0), "--bank1", str(bank1),
                    "--palette-trace", str(trace), "--palette-time", frame_time,
                    "--oba", oba, "--tpa", tpa, "--tha", tha,
                    "--output", str(textured / f"oba-{oba.removeprefix('0x')}.gltf")],
                    cwd=config.ROOT)
        process.run(process.python_tool("export_geometry_frame_gltf.py") + [
            "--trace", str(trace), "--rom", str(rom),
            "--output", str(cabinet_dir / "first-match-frame.gltf"),
            "--max-time", "32.8", "--min-objects", "100"], cwd=config.ROOT)
        process.run(process.python_tool("extract_texture_tiles.py") + [
            "--trace", str(trace), "--bank0", str(bank0), "--bank1", str(bank1),
            "--output-dir", str(cabinet_dir / "texture-tiles"), "--limit", "2048"],
            cwd=config.ROOT)
    print(f"First-match material capture: {twin_dir}")
    print(f"Extracted geometry and texture materials: {output_dir}")
    return 0


def _gltf_trace_time(path: Path) -> str:
    import json

    return str(json.loads(path.read_text(encoding="utf-8"))["extras"]["trace_time"])


def geometry_twin(argv: list[str]) -> int:
    seconds = _positive_seconds("VON_GEOMETRY_TWIN_SECONDS", 20)
    rom = _extract_geometry_rom()
    output_root = config.env_path("VON_GEOMETRY_TWIN_OUTPUT", _disasm() / "player-select-twin")
    script = config.TOOLS / "gameplay_progress.lua"
    run_log = _disasm() / "geometry-twin-run.log"
    twin_dir = _run_twin_capture(
        seconds, script,
        ["-video", "none", "-sound", "none", "-oslog", "-nothrottle",
         "-autoboot_script", str(script)],
        run_log,
    )
    output_dir = output_root / twin_dir.name
    for cabinet in ("p1", "p2"):
        cabinet_dir = output_dir / cabinet
        cabinet_dir.mkdir(parents=True, exist_ok=True)
        trace = twin_dir / cabinet / "mame.log"
        process.run(process.python_tool("dump_geometry_objects.py") + [
            "--trace", str(trace), "--rom", str(rom),
            "--output-dir", str(cabinet_dir / "objects")], cwd=config.ROOT)
        process.run(process.python_tool("export_geometry_animation_gltf.py") + [
            "--trace", str(trace), "--rom", str(rom),
            "--output", str(cabinet_dir / "player-select-animation.gltf")], cwd=config.ROOT)
    print(f"Twin geometry capture: {twin_dir}")
    print(f"Extracted models: {output_dir}")
    return 0


def geometry_select(argv: list[str]) -> int:
    mame = config.env_path("VON_MAME_BIN", config.ROOT / "bin" / "von")
    config.require_file(mame, "MAME binary")
    seconds = config.env_int("VON_GEOMETRY_SELECT_SECONDS", 40)
    out_dir = _disasm()
    rom_path = out_dir / "rompath"
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError(f"staged ROM path is missing: {rom_path / 'vonj'}")
    trace = out_dir / f"vonj-geometry-select-{seconds}s.trace"
    lua_log = out_dir / f"vonj-geometry-select-{seconds}s.lua.log"
    status = _run_mame_to_log(
        mame,
        ["vonj", "-rompath", str(rom_path), "-video", "none", "-sound", "none", "-oslog",
         "-autoboot_script", str(config.TOOLS / "gameplay_progress.lua"),
         "-seconds_to_run", str(seconds), "-skip_gameinfo", "-nothrottle"],
        trace,
        env={
            "SDL_VIDEODRIVER": config.env("SDL_VIDEODRIVER", "dummy") or "dummy",
            "VON_PROGRESS_SECONDS": str(seconds),
            "VON_PROGRESS_LOG": str(lua_log),
            "VON_PROGRESS_CAPTURE_START_FRAME": str(config.env_int("VON_PROGRESS_CAPTURE_START_FRAME", 0)),
            "VON_PROGRESS_COIN_FRAME": str(config.env_int("VON_PROGRESS_COIN_FRAME", 900)),
            "VON_PROGRESS_START_FRAME": str(config.env_int("VON_PROGRESS_START_FRAME", 1500)),
        },
    )
    _summarize(trace)
    objects = _count(trace, "vonj_geometry_object:")
    matrices = _count(trace, "vonj_geometry_matrix:")
    polygons = _count(trace, "vonj_geometry_polygon:")
    print(f"Wrote {trace}")
    print(f"Wrote {lua_log}")
    print(f"Geometry events: objects={objects} matrices={matrices} polygons={polygons}")
    if status != 0 or objects + matrices + polygons == 0:
        _geometry_failure_bundle(trace, lua_log, seconds, status, objects, matrices, polygons)
        return status
    return 0


def _geometry_failure_bundle(trace, lua_log, seconds, status, objects, matrices, polygons) -> None:
    from datetime import datetime

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    bundle = _disasm() / f"bundle-geometry-select-{seconds}s-{stamp}"
    bundle.mkdir(parents=True, exist_ok=True)
    (bundle / "manifest.txt").write_text(
        "script: trace-geometry-select\n"
        f"mame_exit: {status}\nseconds_to_run: {seconds}\n"
        f"objects: {objects}\nmatrices: {matrices}\npolygons: {polygons}\n"
        f"trace_log: {trace}\nlua_log: {lua_log}\n",
        encoding="utf-8",
    )
    for source, name, lines in ((trace, "trace-tail.log", 200), (lua_log, "lua-tail.log", 100)):
        if source.is_file():
            text = source.read_text(encoding="utf-8", errors="replace").splitlines()
            (bundle / name).write_text("\n".join(text[-lines:]) + "\n", encoding="utf-8")
    print(f"Failure bundle: {bundle}")


def i960_boot(argv: list[str]) -> int:
    mame = config.require_mame()
    out_dir = _disasm()
    trace = out_dir / "vonj-boot.trace"
    error_log = out_dir / "error.log"
    rom_path = out_dir / "rompath"
    (rom_path / "vonj").mkdir(parents=True, exist_ok=True)
    for rom in config.rom_dir().iterdir():
        if rom.is_file():
            link = rom_path / "vonj" / rom.name
            link.unlink(missing_ok=True)
            link.symlink_to(rom)
    _run_mame_to_log(
        mame,
        ["vonj", "-rompath", str(rom_path), "-video", "none", "-sound", "none", "-oslog",
         "-seconds_to_run", config.env("VON_TRACE_SECONDS", "1") or "1",
         "-skip_gameinfo"],
        trace,
        cwd=out_dir,
    )
    if error_log.is_file():
        shutil.copy2(error_log, trace)
    _summarize(trace)
    print(f"Wrote {trace}")
    return 0


def i960_reconstructed(argv: list[str]) -> int:
    from . import run as run_cmd

    out = _disasm() / "vonj-reconstructed-boot.trace"
    from .checks import subprocess_output  # noqa: F401  (kept for parity imports)

    with out.open("w", encoding="utf-8") as stream, contextlib.redirect_stdout(stream), \
            contextlib.redirect_stderr(stream):
        run_cmd.i960(
            ["-video", "none", "-sound", "none", "-oslog",
             "-seconds_to_run", config.env("VON_TRACE_SECONDS", "1") or "1", "-skip_gameinfo"],
            kind="reconstructed",
        )
    print(f"Wrote {out}")
    return 0


def i960_attract_coverage(argv: list[str]) -> int:
    mame = config.require_mame()
    seconds = config.env_int("VON_ATTRACT_SECONDS", 60)
    capture_id = f"vonj-attract-{seconds}s"
    out_dir = config.build_dir() / "attract-coverage"
    run_dir = out_dir / capture_id
    pc_log = out_dir / f"vonj-attract-{seconds}s.pcs"
    json_report = out_dir / f"vonj-attract-{seconds}s.json"
    markdown_report = out_dir / f"vonj-attract-{seconds}s.md"
    worklist_json = out_dir / f"vonj-attract-{seconds}s.worklist.json"
    worklist_markdown = out_dir / f"vonj-attract-{seconds}s.worklist.md"
    capture_manifest = out_dir / f"vonj-attract-{seconds}s.capture.json"
    listing = _disasm() / "vonj-maincpu.lst"
    rom_path = _disasm() / "rompath"
    if not listing.is_file():
        raise config.CommandError("i960 listing is missing; run `vonctl disasm remote-i960`")
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError(f"staged vonj ROM path is missing: {rom_path / 'vonj'}")
    for sub in ("cfg", "nvram", "state"):
        (run_dir / sub).mkdir(parents=True, exist_ok=True)

    command = [
        str(mame), "vonj", "-rompath", str(rom_path),
        "-debug", "-debugger", "none", "-video", "none", "-sound", "none",
        "-skip_gameinfo", "-nothrottle",
        "-cfg_directory", str(run_dir / "cfg"),
        "-nvram_directory", str(run_dir / "nvram"),
        "-state_directory", str(run_dir / "state"),
        "-autoboot_script", str(config.TOOLS / "trace_i960_attract_coverage.lua"),
        "-seconds_to_run", str(seconds),
    ]
    process.run(command, env={
        "VON_ATTRACT_SECONDS": str(seconds),
        "VON_ATTRACT_PC_LOG": str(pc_log),
        "SDL_VIDEODRIVER": config.env("SDL_VIDEODRIVER", "dummy") or "dummy",
    }, cwd=config.ROOT)

    process.run(process.python_tool("analyze_attract_coverage.py") + [
        "--pcs", str(pc_log), "--listing", str(listing),
        "--json", str(json_report), "--markdown", str(markdown_report),
        "--capture-id", capture_id,
        "--annotations", str(config.ROOT / "von" / "ghidra" / "AnnotateVonI960.py")],
        cwd=config.ROOT)
    manifest_command = process.python_tool("capture_manifest.py") + [
        "--output", str(capture_manifest), "--root", str(config.ROOT),
        "--id", capture_id, "--objective", "c-only-i960-attract-60s",
        "--hypothesis", "Tier A coverage inventories territory reached by the input-free attract stimulus",
        "--expected-discriminator", "The coverage report records possible_static_edges without claiming executed edges",
        "--seconds", str(seconds), "--phase", "stable-attract", "--set", "vonj",
        "--checkpoint", "reset", "--checkpoint", "hardware-init", "--checkpoint", "scheduler",
        "--checkpoint", "attract-entry", "--checkpoint", "duration-complete",
        "--mame-revision", _git_rev(config.MAME_DIR),
        "--patch-profile", "none",
        "--execution-engine", "interpreter",
        "--command", str(mame), "--command", "vonj", "--command", "-rompath",
        "--command", str(rom_path), "--command", "-debug", "--command", "-debugger",
        "--command", "none", "--command", "-video", "--command", "none",
        "--command", "-sound", "--command", "none", "--command", "-skip_gameinfo",
        "--command", "-nothrottle", "--command", "-cfg_directory", "--command", str(run_dir / "cfg"),
        "--command", "-nvram_directory", "--command", str(run_dir / "nvram"),
        "--command", "-state_directory", "--command", str(run_dir / "state"),
        "--command", "-autoboot_script",
        "--command", str(config.TOOLS / "trace_i960_attract_coverage.lua"),
        "--command", "-seconds_to_run", "--command", str(seconds),
        "--coverage-report", str(json_report),
        "--cfg-directory", str(run_dir / "cfg"),
        "--nvram-directory", str(run_dir / "nvram"),
        "--state-directory", str(run_dir / "state"),
        "--input", str(config.ROOT / "von" / "rom_manifest.json"),
        "--artifact", str(pc_log), "--artifact", str(json_report),
    ]
    process.run(manifest_command, cwd=config.ROOT)
    process.run(process.python_tool("build_attract_worklist.py") + [
        "--coverage", str(json_report),
        "--ledger", str(config.ROOT / "von" / "reconstruction_ledger.json"),
        "--json", str(worklist_json), "--markdown", str(worklist_markdown),
        "--root", str(config.ROOT)], cwd=config.ROOT)
    print(f"PC coverage: {pc_log}")
    print(f"Coverage report: {markdown_report}")
    print(f"Worklist: {worklist_markdown}")
    print(f"Capture manifest: {capture_manifest}")
    return 0


def _git_rev(path: Path) -> str:
    import subprocess

    return subprocess.run(
        ["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True
    ).stdout.strip()


def i960_audio_queue(argv: list[str]) -> int:
    mame = config.require_mame()
    seconds = config.env_int("VON_AUDIO_QUEUE_SECONDS", 5)
    max_samples = config.env_int("VON_AUDIO_QUEUE_MAX_SAMPLES", 4096)
    out = config.env_path(
        "VON_AUDIO_QUEUE_LOG", config.build_dir() / "attract-coverage" / "vonj-audio-queue.log"
    )
    rom_path = _disasm() / "rompath"
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError(f"original vonj ROM staging is missing: {rom_path / 'vonj'}")
    out.parent.mkdir(parents=True, exist_ok=True)
    process.run([
        str(mame), "vonj", "-rompath", str(rom_path), "-bench", str(seconds),
        "-skip_gameinfo", "-autoboot_script",
        str(config.TOOLS / "trace_i960_audio_queue_original.lua"),
    ], env={
        "VON_AUDIO_QUEUE_SECONDS": str(seconds),
        "VON_AUDIO_QUEUE_MAX_SAMPLES": str(max_samples),
        "VON_AUDIO_QUEUE_LOG": str(out),
        "SDL_VIDEODRIVER": config.env("SDL_VIDEODRIVER", "dummy") or "dummy",
    }, cwd=config.ROOT)
    print(f"Original-vonj audio queue trace: {out}")
    return 0


def i960_audio_queue_single_player(argv: list[str]) -> int:
    from . import capture as capture_cmd

    out_root = config.env_path(
        "VON_CAPTURE_OUTPUT_ROOT", config.capture_dir() / "audio-queue-single-player"
    )
    steps = config.env("VON_CAPTURE_SELECTOR_STEPS", "0") or "0"
    if not steps.isdigit():
        raise config.CommandError("VON_CAPTURE_SELECTOR_STEPS must be nonnegative")
    out_root.mkdir(parents=True, exist_ok=True)
    capture_cmd.single_player([], env={
        "VON_CAPTURE_SELECTOR_COUNT": "1",
        "VON_CAPTURE_SELECTOR_START": steps,
        "VON_CAPTURE_ENABLE_PC_TRACE": "0",
        "VON_CAPTURE_QUEUE_TRACE": "1",
        "VON_CAPTURE_QUEUE_MAX_SAMPLES": str(config.env_int("VON_CAPTURE_QUEUE_MAX_SAMPLES", 4096)),
        "VON_CAPTURE_QUEUE_SAMPLE_INTERVAL": config.env("VON_CAPTURE_QUEUE_SAMPLE_INTERVAL", "4") or "4",
        "VON_CAPTURE_OUTPUT_ROOT": str(out_root),
    })
    print(f"Original-vonj selector-{steps} audio queue capture: {out_root}")
    return 0


def i960_exploratory(argv: list[str]) -> int:
    mame = config.require_mame()
    seconds = config.env_int("VON_EXPLORATORY_SECONDS", 60)
    out_dir = config.build_dir() / "attract-coverage"
    pc_log = out_dir / f"exploratory-accelerated-vonj-{seconds}s.pcs"
    events = out_dir / f"exploratory-accelerated-vonj-{seconds}s.events"
    rom_path = _disasm() / "rompath"
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError(f"original vonj ROM staging is missing: {rom_path / 'vonj'}")
    out_dir.mkdir(parents=True, exist_ok=True)
    process.run([
        str(mame), "vonj", "-rompath", str(rom_path), "-bench", str(seconds),
        "-skip_gameinfo", "-autoboot_script",
        str(config.TOOLS / "trace_i960_exploratory_accelerated.lua"),
    ], env={
        "VON_EXPLORATORY_SECONDS": str(seconds),
        "VON_EXPLORATORY_PC_LOG": str(pc_log),
        "VON_EXPLORATORY_EVENTS_LOG": str(events),
        "SDL_VIDEODRIVER": config.env("SDL_VIDEODRIVER", "dummy") or "dummy",
    }, cwd=config.ROOT)
    print(f"Exploratory PCS (not strict evidence): {pc_log}")
    print(f"Exploratory events (not strict evidence): {events}")
    return 0


def texture_buffers(argv: list[str]) -> int:
    mame = config.require_mame()
    rom_path = _disasm() / "rompath"
    out_dir = _disasm()
    frames = config.env_int("VON_TEXTURE_FRAMES", 600)
    seconds = config.env_int("VON_TEXTURE_SECONDS", 10)
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError("staged ROM path is missing")
    for pattern in ("texture-11000000.*.hex", "texture-11200000.*.hex"):
        for stale in out_dir.glob(pattern):
            stale.unlink()
    trace = out_dir / "vonj-texture-buffers.trace"
    _run_mame_to_log(
        mame,
        ["vonj", "-rompath", str(rom_path), "-video", "none", "-sound", "none", "-oslog",
         "-autoboot_script", str(config.TOOLS / "trace_texture_buffers.lua"),
         "-seconds_to_run", str(seconds), "-skip_gameinfo", "-nothrottle"],
        trace,
        env={
            "SDL_VIDEODRIVER": config.env("SDL_VIDEODRIVER", "dummy") or "dummy",
            "VON_TEXTURE_LOG": str(out_dir / "vonj-texture-buffers.log"),
            "VON_TEXTURE_DUMP_DIR": str(out_dir),
            "VON_TEXTURE_FRAMES": str(frames),
        },
    )
    _summarize(trace)
    for bank in ("11000000", "11200000"):
        latest = _newest(out_dir, f"texture-{bank}.*.hex")
        if latest is None:
            raise config.CommandError(f"no texture dump was captured for {bank}")
        link = out_dir / f"texture-{bank}.hex"
        link.unlink(missing_ok=True)
        link.symlink_to(latest.name)
    print(f"Wrote {out_dir / 'vonj-texture-buffers.log'}")
    print(f"Published {out_dir / 'texture-11000000.hex'} and {out_dir / 'texture-11200000.hex'}")
    return 0


def _newest(directory: Path, pattern: str) -> Path | None:
    candidates = [path for path in directory.glob(pattern) if path.is_file()]
    return max(candidates, key=lambda path: path.stat().st_mtime) if candidates else None


def von_progress(argv: list[str]) -> int:
    mame = config.MAME_DIR / "von"
    config.require_file(mame, "MAME binary")
    toolbox = config.env("VON_TOOLBOX", "von-mame")
    seconds = config.env_int("VON_PROGRESS_SECONDS", 150)
    rom_path = _disasm() / "rompath"
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError(f"staged ROM path is missing: {rom_path / 'vonj'}")
    out_dir = _disasm()
    trace = out_dir / f"vonj-progress-{seconds}s.trace"
    lua_log = out_dir / f"vonj-progress-{seconds}s.lua.log"
    snap_dir = out_dir / "vonj-progress-snaps"
    snap_dir.mkdir(parents=True, exist_ok=True)
    command = process.toolbox_prefix(toolbox) + [
        "env", f"VON_PROGRESS_SECONDS={seconds}", f"VON_PROGRESS_LOG={lua_log}",
        str(mame), "vonj", "-rompath", str(rom_path),
        "-video", "none", "-sound", "none", "-oslog",
        "-snapshot_directory", str(snap_dir),
        "-autoboot_script", str(config.TOOLS / "gameplay_progress.lua"),
        "-seconds_to_run", str(seconds), "-skip_gameinfo", "-nothrottle",
    ]
    process.run_to_log(command, trace)
    _summarize(trace)
    print(f"Wrote {trace}")
    print(f"Wrote {lua_log}")
    return 0


def von_toolbox(argv: list[str]) -> int:
    mame = config.MAME_DIR / "von"
    config.require_file(mame, "MAME binary")
    toolbox = config.env("VON_TOOLBOX", "von-mame")
    seconds = config.env_int("VON_TRACE_SECONDS", 5)
    rom_path = _disasm() / "rompath"
    if not (rom_path / "vonj").is_dir():
        raise config.CommandError(f"staged ROM path is missing: {rom_path / 'vonj'}")
    trace = _disasm() / f"vonj-toolbox-{seconds}s.trace"
    command = process.toolbox_prefix(toolbox) + [
        str(mame), "vonj", "-rompath", str(rom_path),
        "-video", "none", "-sound", "none", "-oslog",
        "-seconds_to_run", str(seconds), "-skip_gameinfo", "-nothrottle",
    ]
    process.run_to_log(command, trace)
    print(f"Wrote {trace}")
    return 0


TRACES = {
    "camera": camera,
    "geometry-buffer": geometry_buffer,
    "geometry-first-match": geometry_first_match,
    "geometry-material-twin": geometry_material_twin,
    "geometry-twin": geometry_twin,
    "geometry-select": geometry_select,
    "i960-attract-coverage": i960_attract_coverage,
    "i960-audio-queue": i960_audio_queue,
    "i960-audio-queue-single-player": i960_audio_queue_single_player,
    "i960-boot": i960_boot,
    "i960-exploratory": i960_exploratory,
    "i960-reconstructed": i960_reconstructed,
    "texture-buffers": texture_buffers,
    "von-progress": von_progress,
    "von-toolbox": von_toolbox,
}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: vonctl trace <name> [args...]\n")
        print("names:")
        for name in sorted(TRACES):
            print(f"  {name}")
        return 0
    name, rest = argv[0], argv[1:]
    handler = TRACES.get(name)
    if handler is None:
        raise config.CommandError(
            f"unknown trace {name!r}; expected one of: {', '.join(sorted(TRACES))}"
        )
    return handler(rest)
