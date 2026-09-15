"""Run the test harness on the remote host.

The source tree is rsynced and the `mame-von` fork is cloned lazily when a
suite needs its sources. Private ROMs and the multi-hundred-MB trace captures
stay local by default; pass `--with-roms` / `--with-traces` (or set
`VON_REMOTE_WITH_ROMS=1` / `VON_REMOTE_WITH_TRACES=1`) to include them.
"""

from __future__ import annotations

import shlex
import subprocess
from pathlib import Path

from .. import config, process

_BASE_EXCLUDES = [
    "mame/",
    "von/captures/",
    "von/sandbox/",
    "von/fuzz-versus/",
    "dist/",
    "node_modules/",
    "__pycache__/",
    "*.pyc",
    # The parent .git is synced so git-based tools work remotely, but the
    # absorbed MAME submodule objects stay local.
    ".git/modules/",
    ".git/index.lock",
    ".git/*.lock",
]

_BINARY_EXCLUDES = ["bin/von", "bin/von-hack", "bin/von-geometry"]

# Specific trace/capture fixtures that tests read. `--with-traces` syncs just
# these (a few hundred MB) instead of the whole multi-GB trace tree.
_TEST_ARTIFACTS = [
    "von/build/disasm/vonj-geometry-select-45s-drone0.trace",
    "von/build/disasm/vonj-geometry-select-50s.trace",
    "von/build/disasm/vonj-post-start-45s-drone0.trace",
    "von/build/disasm/von-sharc-opcode-17-helper-sweep-reset45-delayed.trace",
    "von/build/audio-queue/manual-02/input-audio.log",
    "von/build/evidence/quarantine/collision.ndjson",
    "von/captures/fifo-program-20260912T/mame.log",
    "von/captures/vonj-20260907T211227Z/inp/stage3-fleet",
]

# Test suites whose files read MAME sources, so the fork must be present.
_MAME_SUITES = {"contract", "trace", "smoke", "capture", "attract"}


def _settings() -> tuple[str, str, list[str]]:
    from .build import _remote_config

    values = _remote_config()
    host = config.env("VON_REMOTE_HOST") or values.get("VON_REMOTE_HOST", "zathras")
    test_dir = config.env("VON_REMOTE_TEST_DIR") or "von-arcade-decomp"
    ssh_config = config.env("VON_SSH_CONFIG", str(Path.home() / ".ssh" / "config"))
    ssh_args = ["-F", ssh_config] if Path(ssh_config).is_file() else []
    return host, test_dir, ssh_args


def _parse(argv: list[str]) -> tuple[list[str], dict[str, bool]]:
    flags = {
        "roms": config.env_flag("VON_REMOTE_WITH_ROMS"),
        "traces": config.env_flag("VON_REMOTE_WITH_TRACES"),
        "binary": config.env_flag("VON_REMOTE_WITH_BINARY"),
    }
    rest: list[str] = []
    for arg in argv:
        if arg == "--with-roms":
            flags["roms"] = True
        elif arg == "--with-traces":
            flags["traces"] = True
        elif arg == "--with-binary":
            flags["binary"] = True
        else:
            rest.append(arg)
    return rest, flags


def _excludes(flags: dict[str, bool]) -> list[str]:
    excludes = list(_BASE_EXCLUDES)
    excludes += [
        "von/build/action-clips/",
        "von/build/disasm/stage-captures/",
        "*.trace",
        "*.hex",
    ]
    if not flags["roms"]:
        excludes.append("von/artifacts/")
    if not flags.get("binary"):
        excludes += _BINARY_EXCLUDES
    return excludes


def _remote_env() -> str:
    from .build import _remote_config

    values = _remote_config()
    return config.env("VON_REMOTE_ENV") or values.get("VON_REMOTE_ENV", "")


def _remote_abs(host: str, path: str, ssh_args: list[str]) -> str:
    if path.startswith("/"):
        return path
    home = subprocess.run(
        ["ssh", *ssh_args, host, 'printf %s "$HOME"'], capture_output=True, text=True
    ).stdout.strip()
    return f"{home}/{path}" if home else path


def _rsync_ssh(ssh_args: list[str]) -> str:
    if not ssh_args:
        return "ssh"
    return "ssh " + " ".join(shlex.quote(arg) for arg in ssh_args)


def sync(argv: list[str]) -> int:
    """Rsync the source tree to the host, keeping private data local by default."""
    _, flags = _parse(argv)
    host, test_dir, ssh_args = _settings()
    for command in ("ssh", "rsync"):
        config.require_command(command)
    remote = _remote_abs(host, test_dir, ssh_args)
    if subprocess.run(["ssh", *ssh_args, host, "true"], capture_output=True).returncode != 0:
        raise config.CommandError(f"SSH connection failed for {host}")
    print(f"Synchronizing sources to {host}:{remote} ...")
    excludes: list[str] = []
    for pattern in _excludes(flags):
        excludes += ["--exclude", pattern]
    process.run([
        "rsync", "-a", "--delete", "-e", _rsync_ssh(ssh_args), *excludes,
        f"{config.ROOT}/", f"{host}:{remote}/",
    ])
    if flags["traces"]:
        fixtures = [path for path in _TEST_ARTIFACTS if (config.ROOT / path).exists()]
        if fixtures:
            print(f"Syncing {len(fixtures)} trace/capture fixture(s) ...")
            process.run(
                ["rsync", "-aR", *fixtures, f"{host}:{remote}/"],
                cwd=config.ROOT,
            )
    return 0


def ensure_mame(argv: list[str]) -> int:
    """Clone or refresh the mame-von fork on the host."""
    host, test_dir, ssh_args = _settings()
    config.require_command("ssh")
    remote = _remote_abs(host, test_dir, ssh_args)
    fork_url = config.env("VON_MAME_FORK_URL", "https://github.com/longjoel/mame-von.git")
    fork_branch = config.env("VON_MAME_FORK_BRANCH", "von-0.289")
    target = f"{remote}/mame"
    command = (
        f"if [ -d {shlex.quote(target)}/.git ]; then "
        f"git -C {shlex.quote(target)} fetch --depth 1 origin {fork_branch} && "
        f"git -C {shlex.quote(target)} checkout -q --detach FETCH_HEAD; "
        f"else git clone --depth 1 --branch {fork_branch} {fork_url} {shlex.quote(target)}; fi"
    )
    print(f"Ensuring mame-von fork on {host} ...")
    if process.run(["ssh", *ssh_args, host, command], check=False) != 0:
        raise config.CommandError(f"failed to fetch the fork on {host}")
    return 0


def test(argv: list[str]) -> int:
    """Run `vonctl test` on the remote host."""
    suites, flags = _parse(argv)
    suites = suites or ["unit"]
    host, test_dir, ssh_args = _settings()
    sync_args = []
    if flags["roms"]:
        sync_args.append("--with-roms")
    if flags["traces"]:
        sync_args.append("--with-traces")
    if flags["binary"]:
        sync_args.append("--with-binary")
    sync(sync_args)
    if any(suite in _MAME_SUITES for suite in suites):
        ensure_mame([])
    remote = _remote_abs(host, test_dir, ssh_args)
    env_prefix = _remote_env()
    prefix = f"{env_prefix} " if env_prefix else ""
    command = "cd " + shlex.quote(remote) + " && " + prefix + "./bin/vonctl test " + " ".join(
        shlex.quote(suite) for suite in suites
    )
    print(f"Running `vonctl test {' '.join(suites)}` on {host} ...")
    return process.run(["ssh", *ssh_args, host, command], check=False)
