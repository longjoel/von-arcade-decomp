# Build, run, and capture operations

Run commands from the repository root. The `vonctl` harness (`./bin/vonctl`)
owns every operation; the legacy `scripts/*.sh` entrypoints are one-line shims
onto it. Run `./bin/vonctl --help` for the command map.

## Daily path

```sh
./bin/vonctl build remote     # build the mame-von fork on drone0 and copy bin/von
./bin/vonctl run              # local original-ROM cabinet
./bin/vonctl twin             # linked local cabinet pair
./bin/vonctl e2e              # audit, validate, and boot headlessly
./bin/vonctl status           # live reconstruction/test/evidence status
```

## Prepare and build

```sh
./bin/vonctl install
./bin/vonctl build image         # build the pinned MAME build image locally
./bin/vonctl build image-remote  # ...or on the remote host
./bin/vonctl build mame          # local reduced target
./bin/vonctl build docker        # pinned MAME build image
./bin/vonctl build remote        # remote host (zathras)
./bin/vonctl build i960
./bin/vonctl build i960-remote
```

`scripts/i960-build-inner.sh` remains shell because it executes inside the
pinned i960 compiler container. Everything else routes through `vonctl`.

The MAME source is the `mame/` submodule (the `longjoel/mame-von` fork); there
is no patch stack to apply. Run `git submodule update --init mame` after
cloning. Instrumentation is moving to the engine's Lua API rather than C++
tracing patches.

Local overrides belong in `config/remote-build.local.env`, copied from the
tracked example. The pinned i960 Docker image supplies GCC/binutils.

## i960 analysis and runtime

```sh
./bin/vonctl disasm i960
./bin/vonctl disasm remote-i960
./bin/vonctl trace i960-boot
./bin/vonctl trace i960-reconstructed
./bin/vonctl i960 prototype
./bin/vonctl i960 reconstructed
./bin/vonctl i960 clean
./bin/vonctl audit clean-runtime
```

The clean image contains generated code, approved hash-verified data ranges,
and `0xff` elsewhere. Its audit must reject any visited PC beyond the declared
generated extent.

## Tests

```sh
./bin/vonctl test                 # unit + contract
./bin/vonctl test unit
./bin/vonctl test contract
./bin/vonctl test trace
./bin/vonctl test smoke --jobs 1
./bin/vonctl test attract --jobs 1
./bin/vonctl check smoke          # MAME validation and short reconstructed boot
./bin/vonctl check twin           # twin diagnostic matrix
./bin/vonctl check sharc          # recovered SHARC model checkpoint
```

Run suites on the remote host (`zathras`) to offload CPU-heavy runs. Sources
and derived listings are synced; private ROMs and trace captures stay local
unless `--with-roms` / `--with-traces` is passed:

```sh
./bin/vonctl test-remote unit
./bin/vonctl test-remote contract
./bin/vonctl test-remote unit --with-roms
./bin/vonctl remote-sync          # sync only, no run
```

## Geometry capture

```sh
./bin/vonctl trace geometry-select
./bin/vonctl trace geometry-twin
./bin/vonctl trace geometry-first-match
./bin/vonctl trace geometry-material-twin
python3 von/tools/extract_geometry_rom.py
./bin/vonctl export select-models <trace>
```

Every promoted export must follow the evidence-pack rules in
[Evidence and assets plan](evidence-and-assets-plan.md). A plausible glTF is
not automatically a validated asset.

## Audio capture

```sh
VON_AUDIO_SECONDS=30 ./bin/vonctl capture audio /tmp/vonj.wav
python3 von/tools/extract_scsp_audio.py \
  von/artifacts/mpr-18652.32 von/artifacts/mpr-18653.34 \
  --output /tmp/vonj-scsp-region.wav
```

Descriptor and runtime extraction procedures are in [Audio](audio.md).

## Twin cabinets

```sh
./bin/vonctl twin
VON_TWIN_MATRIX=targeted ./bin/vonctl check twin
```

Each cabinet needs isolated state and opposite communication roles. Socket
tests require permission to bind loopback ports. See
[versus-link-findings.md](versus-link-findings.md) for the retained result.

## Deployment

```sh
./bin/vonctl deploy
```

Deployment output belongs under `dist/` and must never contain private ROMs,
raw ROM regions, or locally generated derived media unless redistribution has
been reviewed separately.
