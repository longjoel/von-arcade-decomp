"""Disassembly and Ghidra commands."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .. import config, process


def _disasm() -> Path:
    return config.build_dir() / "disasm"


def _run_docker_objdump(image: str, workdir: str, shell_command: str) -> int:
    return process.run([
        "docker", "run", "--rm",
        "--user", f"{os.getuid()}:{os.getgid()}", "-e", "HOME=/tmp",
        "-v", f"{config.ROOT}:/src",
        "-w", f"/src/{workdir}",
        "--entrypoint", "/bin/bash",
        image,
        "-lc", shell_command,
    ])


def i960(argv: list[str]) -> int:
    """Disassemble the original i960 main CPU (port of scripts/disasm-i960.sh)."""
    config.require_command("docker")
    out_dir = _disasm()
    out_dir.mkdir(parents=True, exist_ok=True)
    image = config.env("VON_I960_IMAGE", config.I960_IMAGE) or config.I960_IMAGE
    process.run(process.python_tool("extract_maincpu.py") + [
        "--output", str(out_dir / "vonj-maincpu.bin")], cwd=config.ROOT)
    _run_docker_objdump(
        image, "von/build/disasm",
        "i960-elf-objdump -m i960 -b binary --adjust-vma=0 -D vonj-maincpu.bin > vonj-maincpu.lst",
    )
    print(f"Wrote {out_dir / 'vonj-maincpu.lst'}")
    return 0


def cpu3(argv: list[str]) -> int:
    """Disassemble the Z80 communication CPU (port of scripts/disasm-cpu3.sh)."""
    out_dir = _disasm()
    out_dir.mkdir(parents=True, exist_ok=True)
    unidasm = config.unidasm()
    config.require_file(unidasm, "unidasm")
    image = out_dir / "vonj-cpu3.bin"
    listing = out_dir / "vonj-cpu3.lst"
    process.run(process.python_tool("extract_cpu3.py") + ["--output", str(image)], cwd=config.ROOT)
    with listing.open("w", encoding="utf-8") as stream:
        subprocess.run([str(unidasm), str(image), "-arch", "z80", "-basepc", "0"],
                       stdout=stream, check=True, env=process.merged_env())
    print(f"Wrote {listing}")
    return 0


def audio(argv: list[str]) -> int:
    """Disassemble the 68000 sound CPU (epr-18670.31)."""
    out_dir = _disasm()
    out_dir.mkdir(parents=True, exist_ok=True)
    unidasm = config.unidasm()
    config.require_file(unidasm, "unidasm")
    image = out_dir / "vonj-audio.bin"
    listing = out_dir / "vonj-audio.lst"
    process.run(process.python_tool("extract_audio.py") + ["--output", str(image)],
                cwd=config.ROOT)
    with listing.open("w", encoding="utf-8") as stream:
        subprocess.run([str(unidasm), str(image), "-arch", "m68000",
                        "-basepc", "0x600000"],
                       stdout=stream, check=True, env=process.merged_env())
    print(f"Wrote {listing}")
    return 0


def sharc(argv: list[str]) -> int:
    """Disassemble the SHARC bootstrap (port of scripts/disasm-sharc.sh)."""
    out_dir = _disasm()
    out_dir.mkdir(parents=True, exist_ok=True)
    unidasm = config.unidasm()
    config.require_file(unidasm, "unidasm")
    maincpu = out_dir / "vonj-maincpu.bin"
    bootstrap = out_dir / "vonj-sharc-bootstrap.bin"
    program = out_dir / "vonj-sharc-program.bin"
    listing = out_dir / "vonj-sharc-bootstrap.lst"
    process.run(process.python_tool("extract_maincpu.py") + ["--output", str(maincpu)], cwd=config.ROOT)
    process.run(process.python_tool("extract_sharc_bootstrap.py") + [
        "--input", str(maincpu), "--output", str(bootstrap)], cwd=config.ROOT)
    process.run(process.python_tool("pack_sharc_program.py") + [str(bootstrap), str(program)],
                cwd=config.ROOT)
    with listing.open("w", encoding="utf-8") as stream:
        subprocess.run([str(unidasm), str(program), "-arch", "sharc", "-basepc", "0", "-count", "3680"],
                       stdout=stream, check=True, env=process.merged_env())
    print(f"Wrote {listing}")
    return 0


def remote_i960(argv: list[str]) -> int:
    """Disassemble the i960 on the remote host (port of scripts/remote-disasm-i960.sh)."""
    values = _remote_config()
    host = config.env("VON_REMOTE_HOST") or values.get("VON_REMOTE_HOST", "drone0")
    checkout = config.env("VON_REMOTE_CHECKOUT") or values.get("VON_REMOTE_CHECKOUT", "/home/drone/von-arcade-decomp")
    image = config.env("VON_I960_IMAGE", config.I960_IMAGE) or config.I960_IMAGE
    for command in ("ssh", "rsync"):
        config.require_command(command)
    out_dir = _disasm()
    out_dir.mkdir(parents=True, exist_ok=True)
    process.run(process.python_tool("extract_maincpu.py") + [
        "--output", str(out_dir / "vonj-maincpu.bin")], cwd=config.ROOT)
    process.run(["ssh", host, f"mkdir -p '{checkout}/von/build/disasm'"])
    process.run(["rsync", "-a", str(out_dir / "vonj-maincpu.bin"),
                 f"{host}:{checkout}/von/build/disasm/vonj-maincpu.bin"])
    process.run(["ssh", host,
                 f"docker run --rm -v '{checkout}:/src' -w /src/von/build/disasm "
                 f"--entrypoint /bin/bash '{image}' -lc "
                 "'i960-elf-objdump -m i960 -b binary --adjust-vma=0 -D vonj-maincpu.bin > vonj-maincpu.lst'"])
    process.run(["rsync", "-a", f"{host}:{checkout}/von/build/disasm/vonj-maincpu.lst",
                 str(out_dir / "vonj-maincpu.lst")])
    print(f"Wrote {out_dir / 'vonj-maincpu.lst'}")
    return 0


def _remote_config() -> dict[str, str]:
    from .build import _remote_config as reader

    return reader()


def _ghidra_home() -> Path:
    default = config.ROOT.parent / "voff" / "ghidra" / "ghidra_11.3.1_PUBLIC"
    return config.env_path("GHIDRA_HOME", default)


def ghidra(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: vonctl ghidra run|install")
        return 0
    if argv[0] == "install":
        return _ghidra_install(argv[1:])
    if argv[0] == "run":
        return _ghidra_run(argv[1:])
    raise config.CommandError("usage: vonctl ghidra run|install")


def _ghidra_run(argv: list[str]) -> int:
    home = _ghidra_home()
    headless = home / "support" / "analyzeHeadless"
    processor = home / "Ghidra" / "Processors" / "i960"
    if not (headless.is_file() and os.access(headless, os.X_OK)):
        raise config.CommandError(f"Ghidra headless analyzer not found: {headless}")
    if not (processor / "data" / "languages" / "i960.ldefs").is_file():
        raise config.CommandError(
            f"i960 Ghidra processor module is not installed: {processor}\n"
            "Install mumbel/ghidra_i960 into Ghidra/Processors/i960 first."
        )
    rom_image = _disasm() / "vonj-maincpu.bin"
    project_dir = config.build_dir() / "ghidra"
    project_name = "vonj-i960"
    scripts = config.ROOT / "von" / "ghidra"
    process.run(process.python_tool("extract_maincpu.py") + ["--output", str(rom_image)], cwd=config.ROOT)
    project_dir.mkdir(parents=True, exist_ok=True)

    process.run([
        str(headless), str(project_dir), project_name,
        "-import", str(rom_image), "-processor", "i960:LE:32:default", "-cspec", "default",
        "-scriptPath", str(scripts), "-postscript", "AnnotateVonI960.py",
        "-overwrite", "-log", str(project_dir / "analyze.log"),
    ])
    report = project_dir / "report.txt"
    process.run_to_log([
        str(headless), str(project_dir), project_name,
        "-process", rom_image.name, "-scriptPath", str(scripts),
        "-postscript", "ReportVonI960.py", "-log", str(project_dir / "report.log"),
    ], report)
    print(f"Ghidra project: {project_dir}/{project_name}")
    print(f"Ghidra report: {report}")
    return 0


def _ghidra_install(argv: list[str]) -> int:
    home = _ghidra_home()
    target = home / "Ghidra" / "Processors" / "i960"
    ref = "727ef7872c5b1cd6ceb5a81f5e474d1ced92945c"
    if not (home / "Ghidra" / "Processors").is_dir():
        raise config.CommandError(f"invalid Ghidra installation: {home}")
    work = Path(tempfile.mkdtemp())
    try:
        process.run(["git", "clone", "--quiet", "https://github.com/mumbel/ghidra_i960.git",
                     str(work / "i960")])
        process.run(["git", "-C", str(work / "i960"), "checkout", "--quiet", ref])
        target.mkdir(parents=True, exist_ok=True)
        shutil.copytree(work / "i960" / "data", target / "data", dirs_exist_ok=True)
        patch_file = config.ROOT / "von" / "ghidra" / "i960-bal-call.patch"
        with patch_file.open("rb") as stream:
            subprocess.run(["patch", "-d", str(target), "-p1"], stdin=stream, check=True,
                           env=process.merged_env())
    finally:
        shutil.rmtree(work, ignore_errors=True)
    print(f"Installed i960 Ghidra module at {target}")
    print(f"Source revision: {ref}")
    return 0


DISASM = {
    "i960": i960,
    "audio": audio,
    "cpu3": cpu3,
    "sharc": sharc,
    "remote-i960": remote_i960,
}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: vonctl disasm <name> [args...]\n")
        print("names:")
        for name in sorted(DISASM):
            print(f"  {name}")
        return 0
    name, rest = argv[0], argv[1:]
    handler = DISASM.get(name)
    if handler is None:
        raise config.CommandError(
            f"unknown disasm {name!r}; expected one of: {', '.join(sorted(DISASM))}"
        )
    return handler(rest)
