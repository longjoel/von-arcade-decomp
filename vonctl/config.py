"""Shared configuration and path helpers.

Mirrors `scripts/common.sh` so the harness can replace the bash entrypoints
without changing where artifacts land or which environment variables override
paths.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MAME_URL = "https://github.com/mamedev/mame.git"
MAME_REF = "569c5e9d4534cb244ff67ebbdb5f9fe69a465318"
MAME_DIR = ROOT / "mame"
TOOLS = ROOT / "von" / "tools"

I960_IMAGE = (
    "ghcr.io/nkito/i960_sbc@sha256:"
    "c4baf40df8c6db1774e2bb87020824ca0d99201b11fb1944ef3a6d2922bd4b6c"
)
DEFAULT_MAME_BUILD_IMAGE = "von-mame-build:ubuntu26.04"
DEFAULT_CTRLR = "x360twin"


class CommandError(Exception):
    """A user-facing failure. Reported without a traceback."""

    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.code = code


def env(name: str, default: str | None = None) -> str | None:
    value = os.environ.get(name)
    return default if value is None else value


def env_flag(name: str, default: str = "0") -> bool:
    return env(name, default) == "1"


def env_int(name: str, default: int) -> int:
    raw = env(name)
    if raw is None or raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise CommandError(f"{name} must be an integer, got {raw!r}") from exc


def env_path(name: str, default: Path) -> Path:
    value = env(name)
    return Path(value).resolve() if value else default


def mame_bin() -> Path:
    return env_path("VON_MAME_BIN", ROOT / "bin" / "von")


def unidasm() -> Path:
    return env_path("VON_UNIDASM", MAME_DIR / "unidasm")


def rom_dir() -> Path:
    return env_path("VON_ROM_DIR", ROOT / "von" / "artifacts")


def capture_dir() -> Path:
    return env_path("VON_CAPTURE_DIR", ROOT / "von" / "captures")


def build_dir() -> Path:
    return ROOT / "von" / "build"


def ctrlr_name() -> str:
    return env("VON_CTRLR", DEFAULT_CTRLR) or ""


def ctrlr_path() -> Path:
    return env_path("VON_CTRLRPATH", ROOT / "ctrlr")


def require_command(name: str) -> None:
    if shutil.which(name) is None:
        raise CommandError(f"required command not found: {name}")


def require_mame() -> Path:
    binary = mame_bin()
    if not binary.is_file() or not os.access(binary, os.X_OK):
        raise CommandError(
            f"MAME is not built: {binary}\nRun `vonctl build mame` first."
        )
    return binary


def require_file(path: Path, label: str | None = None) -> Path:
    if not path.is_file():
        raise CommandError(f"{label or 'file'} not found: {path}")
    return path


def runtime_env() -> dict[str, str]:
    """macOS Homebrew runtime library path, mirroring `brew_runtime_path`."""
    if shutil.which("brew") is None:
        return {}
    prefix = subprocess.run(
        ["brew", "--prefix"], capture_output=True, text=True, check=True
    ).stdout.strip()
    paths = [f"{prefix}/lib"]
    for formula in ("sdl2_ttf", "sdl2-compat", "mesa", "alsa-lib", "pipewire"):
        listed = subprocess.run(
            ["brew", "list", "--formula", formula], capture_output=True, text=True
        )
        if listed.returncode == 0:
            formula_prefix = subprocess.run(
                ["brew", "--prefix", formula], capture_output=True, text=True, check=True
            ).stdout.strip()
            paths.insert(0, f"{formula_prefix}/lib")
    if not paths:
        return {}
    joined = ":".join(paths)
    existing = os.environ.get("LD_LIBRARY_PATH")
    return {"LD_LIBRARY_PATH": f"{joined}:{existing}" if existing else joined}


def prepare_rom_path(set_name: str = "vonj") -> Path:
    """Symlink the private ROM set into a disposable staging directory."""
    source = rom_dir()
    if not source.is_dir():
        raise CommandError(f"ROM directory does not exist: {source}")
    root = build_dir()
    root.mkdir(parents=True, exist_ok=True)
    staging = Path(tempfile.mkdtemp(prefix="rompath.", dir=root))
    target = staging / set_name
    target.mkdir(parents=True, exist_ok=True)
    for rom in sorted(source.iterdir()):
        if rom.is_file():
            (target / rom.name).symlink_to(rom)
    return staging


def cleanup_rom_path(staging: Path | None) -> None:
    if staging is not None and staging.is_dir():
        shutil.rmtree(staging, ignore_errors=True)
