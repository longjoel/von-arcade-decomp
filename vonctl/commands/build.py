"""Build commands: local MAME, Docker MAME, remote MAME, i960 images.

The MAME source is now the `mame/` submodule (the `mame-von` fork). There is no
patch stack to apply: the fork commit is the build input.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from .. import config, process

_MAKE_ARGS = [
    "REGENIE=1", "TARGET=mame", "SUBTARGET=von",
    "SOURCES=src/mame/sega/model2.cpp",
    "USE_QTDEBUG=0", "NO_USE_MIDI=1", "NO_USE_PORTAUDIO=1",
    "NO_USE_PIPEWIRE=1", "NO_USE_PULSEAUDIO=1", "NOWERROR=1",
]


def _make_command(prefix: str = "") -> str:
    cd = f"cd {prefix} && " if prefix else ""
    return cd + "make " + " ".join(_MAKE_ARGS) + ' -j"${JOBS:-$(nproc)}"'


def _jobs() -> str:
    return config.env("JOBS", "") or str(os.cpu_count() or 1)


def _require_submodule() -> None:
    if not (config.MAME_DIR / "makefile").is_file():
        raise config.CommandError(
            f"MAME submodule is not checked out: {config.MAME_DIR}\n"
            "Run `git submodule update --init mame`."
        )


def _brew_build_env() -> dict[str, str]:
    if shutil.which("brew") is None:
        return {}
    listed = subprocess.run(
        ["brew", "list", "--formula", "mesa"], capture_output=True, text=True
    )
    alsa = subprocess.run(
        ["brew", "list", "--formula", "alsa-lib"], capture_output=True, text=True
    )
    if listed.returncode != 0 or alsa.returncode != 0:
        return {}
    mesa = subprocess.run(["brew", "--prefix", "mesa"], capture_output=True, text=True).stdout.strip()
    alsa_prefix = subprocess.run(["brew", "--prefix", "alsa-lib"], capture_output=True, text=True).stdout.strip()
    brew = subprocess.run(["brew", "--prefix"], capture_output=True, text=True).stdout.strip()
    cflags = (f"-I{mesa}/include -I{alsa_prefix}/include -I{brew}/include "
              f"-I{brew}/include/SDL2 " + os.environ.get("CFLAGS", ""))
    environ = process.merged_env()
    return {
        "CFLAGS": cflags,
        "CXXFLAGS": f"-iquote {config.MAME_DIR}/src/frontend/mame "
                    f"-iquote {config.MAME_DIR}/src/lib/util {cflags} "
                    + environ.get("CXXFLAGS", ""),
        "LDFLAGS": f"-L{mesa}/lib -L{brew}/lib " + environ.get("LDFLAGS", ""),
    }


def mame(argv: list[str]) -> int:
    """Build the reduced Virtual-On MAME target locally from the fork."""
    config.require_command("make")
    _require_submodule()
    (config.MAME_DIR / "makefile").touch()
    (config.MAME_DIR / "build" / "generated" / "mame" / "von" / "drivlist.cpp").unlink(missing_ok=True)

    print("Building reduced Virtual-On MAME target...")
    process.run(["make", *_MAKE_ARGS, f"-j{_jobs()}"], cwd=config.MAME_DIR, env=_brew_build_env())
    output = config.MAME_DIR / "von"
    if not output.is_file():
        raise config.CommandError(f"local MAME build did not produce {output}")
    destination = config.mame_bin()
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output, destination)
    destination.chmod(0o755)
    print(f"Built {destination}")
    return 0


def docker_mame(argv: list[str]) -> int:
    """Build MAME in the pinned Docker image."""
    config.require_command("docker")
    _require_submodule()
    image = config.env("VON_MAME_BUILD_IMAGE", config.DEFAULT_MAME_BUILD_IMAGE) or config.DEFAULT_MAME_BUILD_IMAGE
    if subprocess.run(["docker", "image", "inspect", image], capture_output=True).returncode != 0:
        raise config.CommandError(f"Docker image not found: {image}")
    process.run([
        "docker", "run", "--rm",
        "--user", f"{os.getuid()}:{os.getgid()}",
        "-e", f"JOBS={config.env('JOBS', '') or ''}",
        "-v", f"{config.ROOT}:/src",
        "-w", "/src",
        image,
        "bash", "-lc", _make_command("mame"),
    ])
    return 0


def _remote_config() -> dict[str, str]:
    example = config.ROOT / "config" / "remote-build.env.example"
    if not example.is_file():
        raise config.CommandError(f"missing remote build example config: {example}")
    values: dict[str, str] = {}
    for path in (example, config.ROOT / "config" / "remote-build.local.env"):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                values[key.strip()] = value.strip()
    return values


def remote_mame(argv: list[str]) -> int:
    """Build the mame-von fork on the remote host in Docker.

    The remote only needs the fork; it is cloned/fetched from GitHub into
    `VON_REMOTE_MAME_DIR`, so no parent-repo checkout is required there.
    """
    import shlex

    values = _remote_config()
    host = config.env("VON_REMOTE_HOST") or values.get("VON_REMOTE_HOST", "zathras")
    mame_dir = config.env("VON_REMOTE_MAME_DIR") or values.get("VON_REMOTE_MAME_DIR", "mame-von")
    image = config.env("VON_MAME_BUILD_IMAGE") or values.get("VON_MAME_BUILD_IMAGE", config.DEFAULT_MAME_BUILD_IMAGE)
    jobs = config.env("VON_REMOTE_JOBS", "") or ""
    fork_url = config.env("VON_MAME_FORK_URL", "https://github.com/longjoel/mame-von.git")
    fork_branch = config.env("VON_MAME_FORK_BRANCH", "von-0.289")
    ssh_config = config.env("VON_SSH_CONFIG", str(Path.home() / ".ssh" / "config"))
    ssh_args = ["-F", ssh_config] if Path(ssh_config).is_file() else []
    for command in ("ssh", "scp"):
        config.require_command(command)

    print(f"Checking remote build host {host}...")
    if subprocess.run(["ssh", *ssh_args, host, "true"], capture_output=True).returncode != 0:
        raise config.CommandError(f"SSH connection failed for {host}")
    if subprocess.run(["ssh", *ssh_args, host, "command -v git"], capture_output=True).returncode != 0:
        raise config.CommandError(f"git is not available on {host}")
    if subprocess.run(["ssh", *ssh_args, host, "docker info"], capture_output=True).returncode != 0:
        raise config.CommandError(
            f"docker is not usable on {host} (is the user in the docker group?)"
        )
    if subprocess.run(["ssh", *ssh_args, host, "docker image inspect", image],
                      capture_output=True).returncode != 0:
        raise config.CommandError(
            f"Docker image not found on {host}: {image}\n"
            f"Build it there from docker/mame-build.Dockerfile."
        )

    home = subprocess.run(["ssh", *ssh_args, host, 'printf %s "$HOME"'],
                          capture_output=True, text=True).stdout.strip()
    if not mame_dir.startswith("/"):
        mame_dir = f"{home}/{mame_dir}" if home else mame_dir
    ids = subprocess.run(["ssh", *ssh_args, host, "id -u; id -g"],
                         capture_output=True, text=True).stdout.split()
    uid = ids[0] if ids else "0"
    gid = ids[1] if len(ids) > 1 else uid

    print(f"Synchronizing mame-von fork ({fork_branch}) on {host}...")
    quoted_dir = shlex.quote(mame_dir)
    prepare = (
        f"if [ -d {quoted_dir}/.git ]; then "
        f"git -C {quoted_dir} fetch --depth 1 origin {fork_branch} && "
        f"git -C {quoted_dir} checkout -q --detach FETCH_HEAD; "
        f"else git clone --depth 1 --branch {fork_branch} {fork_url} {quoted_dir}; fi"
    )
    if process.run(["ssh", *ssh_args, host, prepare], check=False) != 0:
        raise config.CommandError(f"failed to fetch the fork on {host}")

    print("Building MAME remotely in Docker...")
    remote_command = (
        f"docker run --rm --user {uid}:{gid} -e HOME=/tmp "
        f"-v {shlex.quote(mame_dir + ':/src')} -w /src "
        f"-e JOBS={shlex.quote(jobs)} {shlex.quote(image)} "
        f"bash -lc {shlex.quote(_make_command())}"
    )
    if process.run(["ssh", *ssh_args, host, remote_command], check=False) != 0:
        raise config.CommandError("remote MAME build failed")

    destination = config.mame_bin()
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.parent / ".von.remote.tmp"
    temporary.unlink(missing_ok=True)
    if process.run(["scp", *ssh_args, f"{host}:{mame_dir}/von", str(temporary)], check=False) != 0:
        temporary.unlink(missing_ok=True)
        raise config.CommandError("failed to copy the remote MAME binary")
    temporary.chmod(0o755)
    temporary.replace(destination)
    print(f"Synchronized {destination} (remote host: {host})")
    return 0


def docker_image(argv: list[str]) -> int:
    """Build the MAME build image locally from docker/mame-build.Dockerfile."""
    config.require_command("docker")
    dockerfile = config.ROOT / "docker" / "mame-build.Dockerfile"
    config.require_file(dockerfile, "MAME build Dockerfile")
    image = config.env("VON_MAME_BUILD_IMAGE", config.DEFAULT_MAME_BUILD_IMAGE) or config.DEFAULT_MAME_BUILD_IMAGE
    process.run(["docker", "build", "-t", image, "-f", str(dockerfile), str(config.ROOT)])
    print(f"Built image {image}")
    return 0


def remote_docker_image(argv: list[str]) -> int:
    """Build the MAME build image on the remote host."""
    import shlex

    values = _remote_config()
    host = config.env("VON_REMOTE_HOST") or values.get("VON_REMOTE_HOST", "zathras")
    image = config.env("VON_MAME_BUILD_IMAGE") or values.get("VON_MAME_BUILD_IMAGE", config.DEFAULT_MAME_BUILD_IMAGE)
    dockerfile = config.ROOT / "docker" / "mame-build.Dockerfile"
    config.require_file(dockerfile, "MAME build Dockerfile")
    ssh_config = config.env("VON_SSH_CONFIG", str(Path.home() / ".ssh" / "config"))
    ssh_args = ["-F", ssh_config] if Path(ssh_config).is_file() else []
    config.require_command("ssh")
    print(f"Building image {image} on {host} (this may take a few minutes)...")
    command = (
        'd=$(mktemp -d) && cd "$d" && '
        f"docker build -t {shlex.quote(image)} -f - . ; "
        'status=$?; cd / && rm -rf "$d"; exit $status'
    )
    completed = subprocess.run(
        ["ssh", *ssh_args, host, command],
        input=dockerfile.read_text(encoding="utf-8"), text=True,
    )
    if completed.returncode != 0:
        raise config.CommandError(f"remote image build failed on {host}")
    print(f"Built image {image} on {host}")
    return 0


def i960(argv: list[str]) -> int:
    """Build the prototype/clean i960 images (port of scripts/i960-build.sh)."""
    config.require_command("docker")
    if subprocess.run(["docker", "info"], capture_output=True).returncode != 0:
        raise config.CommandError(
            "Docker daemon is unavailable; the i960 build requires the pinned compiler image"
        )
    image = config.env("VON_I960_IMAGE", config.I960_IMAGE) or config.I960_IMAGE
    build = config.build_dir() / "i960"
    build.mkdir(parents=True, exist_ok=True)
    process.run(process.python_tool("extract_maincpu.py") + [
        "--output", str(build / "vonj-original-maincpu.bin")], cwd=config.ROOT)
    process.run([
        "docker", "run", "--rm",
        "--user", f"{os.getuid()}:{os.getgid()}", "-e", "HOME=/tmp",
        "-v", f"{config.ROOT}:/src",
        "-w", "/src/von/i960",
        "--entrypoint", "/bin/bash",
        image,
        "/src/scripts/i960-build-inner.sh",
    ])
    _package_clean()
    return 0


def _package_clean() -> None:
    build = config.build_dir()
    process.run(process.python_tool("build_clean_i960_image.py") + [
        "--generated", str(build / "i960" / "reconstructed.bin"),
        "--original", str(build / "i960" / "vonj-original-maincpu.bin"),
        "--ranges", str(config.ROOT / "von" / "i960" / "approved_data_ranges.json"),
        "--output", str(build / "i960" / "reconstructed-clean-maincpu.bin"),
        "--build-manifest", str(build / "i960" / "reconstructed-clean-maincpu.manifest.json"),
    ], cwd=config.ROOT)
    target = build / "rompath" / "reconstructed-clean"
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(build / "rompath" / "reconstructed", target)
    link = target / "vonjdev" / "prototype-maincpu.bin"
    link.unlink(missing_ok=True)
    link.symlink_to("../../../i960/reconstructed-clean-maincpu.bin")


def remote_i960(argv: list[str]) -> int:
    """Build the i960 images on the remote host (port of scripts/remote-i960-build.sh)."""
    values = _remote_config()
    host = config.env("VON_REMOTE_HOST") or values.get("VON_REMOTE_HOST", "drone0")
    checkout = config.env("VON_REMOTE_CHECKOUT") or values.get("VON_REMOTE_CHECKOUT", "/home/drone/von-arcade-decomp")
    image = config.env("VON_I960_IMAGE", config.I960_IMAGE) or config.I960_IMAGE
    for command in ("ssh", "rsync"):
        config.require_command(command)

    print(f"Synchronizing i960 C sources to {host}...")
    build = config.build_dir() / "i960"
    build.mkdir(parents=True, exist_ok=True)
    process.run(process.python_tool("extract_maincpu.py") + [
        "--output", str(build / "vonj-original-maincpu.bin")], cwd=config.ROOT)
    process.run(["rsync", "-a", "--delete", f"{config.ROOT}/von/i960/", f"{host}:{checkout}/von/i960/"])
    process.run(["rsync", "-a", f"{config.ROOT}/scripts/i960-build-inner.sh",
                 f"{host}:{checkout}/scripts/i960-build-inner.sh"])
    process.run(["rsync", "-a", str(config.TOOLS / "build_clean_i960_image.py"),
                 f"{host}:{checkout}/von/tools/build_clean_i960_image.py"])
    process.run(["rsync", "-a", str(build / "vonj-original-maincpu.bin"),
                 f"{host}:{checkout}/von/build/i960/vonj-original-maincpu.bin"])

    print("Building i960 C images remotely in Docker...")
    process.run(["ssh", host,
                 f"docker run --rm -v '{checkout}:/src' -w /src/von/i960 --entrypoint /bin/bash "
                 f"'{image}' /src/scripts/i960-build-inner.sh"])
    for artifact in (
        "prototype.elf", "prototype.bin", "prototype-maincpu.bin", "prototype.lst",
        "reconstructed.elf", "reconstructed.bin", "reconstructed.lst",
        "reconstructed-maincpu.bin", "reconstructed_reset.elf",
        "reconstructed_reset.bin", "reconstructed_reset.lst",
    ):
        process.run(["scp", f"{host}:{checkout}/von/build/i960/{artifact}", str(build / artifact)])
    process.run(["rsync", "-a", "--delete",
                 f"{host}:{checkout}/von/build/rompath/reconstructed/",
                 str(config.build_dir() / "rompath" / "reconstructed" / "")])
    _package_clean()
    print("Synchronized reconstructed i960 image")
    return 0


BUILDS = {
    "mame": mame,
    "docker": docker_mame,
    "remote": remote_mame,
    "image": docker_image,
    "image-remote": remote_docker_image,
    "i960": i960,
    "i960-package": lambda argv: _package_clean(),
    "i960-remote": remote_i960,
}


def main(argv: list[str]) -> int:
    if not argv or argv[0] in ("-h", "--help"):
        print("usage: vonctl build <name> [args...]\n")
        print("names:")
        for name in sorted(BUILDS):
            print(f"  {name}")
        return 0
    name, rest = argv[0], argv[1:]
    handler = BUILDS.get(name)
    if handler is None:
        raise config.CommandError(
            f"unknown build {name!r}; expected one of: {', '.join(sorted(BUILDS))}"
        )
    return handler(rest)
