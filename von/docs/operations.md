# Build, run, and capture operations

Run commands from the repository root.

## Daily path

```sh
./scripts/remote-build.sh       # build patched MAME on drone0 and copy bin/von
./scripts/run.sh                # local original-ROM cabinet
./scripts/run-twin.sh           # linked local cabinet pair
./scripts/e2e.sh                # audit, validate, and boot headlessly
./scripts/status.sh             # live reconstruction/test/evidence status
```

Set `VON_MAME_PATCH_SET` to `core`, `geometry-trace`, `geometry-material`, or
`debug` only when the requested capture requires that instrumentation. Normal
runs should use the smallest patch profile.

## Prepare and build

```sh
./scripts/install.sh
./scripts/prepare-mame.sh
./scripts/build.sh
./scripts/build-mame-docker.sh
./scripts/i960-build.sh
./scripts/remote-i960-build.sh
```

Local overrides belong in `config/remote-build.local.env`, copied from the
tracked example. The pinned i960 Docker image supplies GCC/binutils.

## i960 analysis and runtime

```sh
./scripts/disasm-i960.sh
./scripts/remote-disasm-i960.sh
./scripts/trace-i960-boot.sh
./scripts/trace-i960-reconstructed.sh
./scripts/run-i960.sh
./scripts/run-i960-reconstructed.sh
./scripts/run-i960-clean.sh
./scripts/audit-i960-clean-runtime.sh
```

The clean image contains generated code, approved hash-verified data ranges,
and `0xff` elsewhere. Its audit must reject any visited PC beyond the declared
generated extent.

## Tests

```sh
./scripts/test.sh
python3 von/tools/run_tests.py unit
python3 von/tools/run_tests.py contract
python3 von/tools/run_tests.py trace
python3 von/tools/run_tests.py smoke --jobs 1
python3 von/tools/run_tests.py attract --jobs 1
```

## Geometry capture

```sh
./scripts/trace-geometry-select.sh
./scripts/trace-geometry-twin.sh
./scripts/trace-geometry-first-match.sh
./scripts/trace-geometry-material-twin.sh
python3 von/tools/extract_geometry_rom.py
./scripts/export-player-select-models.sh <trace>
```

Every promoted export must follow the evidence-pack rules in
[Evidence and assets plan](evidence-and-assets-plan.md). A plausible glTF is
not automatically a validated asset.

## Audio capture

```sh
VON_AUDIO_SECONDS=30 ./scripts/capture-audio.sh /tmp/vonj.wav
python3 von/tools/extract_scsp_audio.py \
  von/artifacts/mpr-18652.32 von/artifacts/mpr-18653.34 \
  --output /tmp/vonj-scsp-region.wav
```

Descriptor and runtime extraction procedures are in [Audio](audio.md).

## Twin cabinets

```sh
./scripts/run-twin.sh
VON_TWIN_MATRIX=targeted ./scripts/test-twin.sh
```

Each cabinet needs isolated state and opposite communication roles. Socket
tests require permission to bind loopback ports. See
[versus-link-findings.md](../versus-link-findings.md) for the retained result.

## Deployment

```sh
./scripts/deploy.sh
```

Deployment output belongs under `dist/` and must never contain private ROMs,
raw ROM regions, or locally generated derived media unless redistribution has
been reviewed separately.
