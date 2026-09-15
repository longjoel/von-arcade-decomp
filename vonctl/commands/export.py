"""Asset export commands."""

from __future__ import annotations

from pathlib import Path

from .. import config, process


def _disasm() -> Path:
    return config.build_dir() / "disasm"


def select_models(argv: list[str]) -> int:
    """Export polygon-ROM objects from a geometry trace (port of export-player-select-models.sh)."""
    trace = Path(argv[0]) if argv else _disasm() / "vonj-geometry-select-40s.trace"
    if not trace.is_absolute():
        trace = config.ROOT / trace
    if not trace.is_file():
        raise config.CommandError(f"geometry trace is missing: {trace}")
    rom = config.env_path("VON_GEOMETRY_ROM", _disasm() / "geometry-rom.bin")
    output_dir = config.env_path("VON_GEOMETRY_OUTPUT", _disasm() / "geometry-objects")
    window = config.env("VON_GEOMETRY_WINDOW", "16384") or "16384"
    if not rom.is_file():
        print("Geometry ROM is missing; assembling it from private artifacts...")
        process.run(process.python_tool("extract_geometry_rom.py") + ["--output", str(rom)],
                    cwd=config.ROOT)

    process.run(process.python_tool("dump_geometry_objects.py") + [
        "--trace", str(trace), "--rom", str(rom), "--output-dir", str(output_dir),
        "--window", window], cwd=config.ROOT)

    index = output_dir / "index.tsv"
    count = 0
    if index.is_file():
        for line in index.read_text(encoding="utf-8").splitlines()[1:]:
            fields = line.split("\t")
            if len(fields) < 2 or not fields[1]:
                continue
            oba = fields[1]
            stem = f"oba-{oba.removeprefix('0x')}"
            obj = output_dir / f"{stem}.obj"
            gltf = output_dir / f"{stem}.gltf"
            process.run(process.python_tool("export_geometry_obj.py") + [
                "--rom", str(rom), "--oba", oba, "--words", window, "--output", str(obj)],
                cwd=config.ROOT)
            process.run(process.python_tool("export_geometry_gltf.py") + [str(obj), str(gltf)],
                        cwd=config.ROOT)
            count += 1

    print(f"Exported {count} polygon-ROM objects to {output_dir}")
    return 0


def stage_arenas(argv: list[str]) -> int:
    """Regenerate textured stage arenas (port of export-stage-arenas-textured.sh)."""
    godot = config.env_path("VON_GODOT", config.ROOT.parent / "von-godot")
    cap_dir = config.env_path("VON_CAPTURE_DIR", _disasm() / "stage-captures")
    out_dir = godot / "assets" / "generated" / "arena"
    if not godot.is_dir():
        raise config.CommandError(f"no Godot project: {godot}")
    out_dir.mkdir(parents=True, exist_ok=True)

    ordinals = (config.env("VON_ORDINALS", "0 1 2 3 4 5 6 7 8 9") or "").split()
    for ordinal in ordinals:
        trace = cap_dir / f"ord{ordinal}.trace"
        if not (trace.is_file() and trace.stat().st_size > 0):
            print(f"ord {ordinal}: no capture trace, skipped")
            continue
        bank_dir = cap_dir / f"ord{ordinal}-banks"
        bank_args: list[str] = []
        if (bank_dir / "texture-11000000.hex").is_file() and \
           (bank_dir / "texture-11200000.hex").is_file():
            bank_args = ["--bank0", str(bank_dir / "texture-11000000.hex"),
                         "--bank1", str(bank_dir / "texture-11200000.hex")]
        else:
            print(f"ord {ordinal}: no captured texture banks; using boot sheets",
                  file=__import__("sys").stderr)
        palette = bank_dir / "palette.trace" if (bank_dir / "palette.trace").is_file() else trace
        process.run(process.python_tool("extract_stage_textured_gltf.py") + [
            "--stage", ordinal, "--trace", str(trace), "--palette-trace", str(palette),
            *bank_args, "--output", str(out_dir / f"stage_{int(ordinal):02d}_arena.gltf")],
            cwd=config.ROOT)
    return 0


EXPORTS = {
    "select-models": select_models,
    "stage-arenas": stage_arenas,
}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: vonctl export <name> [args...]\n")
        print("names:")
        for name in sorted(EXPORTS):
            print(f"  {name}")
        return 0
    name, rest = argv[0], argv[1:]
    handler = EXPORTS.get(name)
    if handler is None:
        raise config.CommandError(
            f"unknown export {name!r}; expected one of: {', '.join(sorted(EXPORTS))}"
        )
    return handler(rest)
