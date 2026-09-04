# Cyber Troopers: Virtual-On research workspace

This repository reverse-engineers the arcade version of *Cyber Troopers:
Virtual-On*. MAME is the execution environment and behavioral oracle while the
original Intel i960 host program, Model 2 geometry path, audio interactions,
and twin-cabinet behavior are recovered into readable source and reproducible
evidence.

The active delivery objective is a 60-emulated-second attract run using only
generated i960 code. It is not yet a standalone reconstructed game. Run
`./scripts/status.sh` for the current, machine-generated state.

## Documentation

Start with the [documentation map](docs/README.md):

- [Reconstruction handbook](docs/reconstruction.md)
- [Evidence, cleanup, and validated-assets plan](docs/evidence-and-assets-plan.md)
- [Build and capture operations](docs/operations.md)
- [Geometry recovery](docs/geometry.md)
- [Audio recovery](docs/audio.md)
- [SHARC boundary](docs/sharc.md)

Generated reports:

- [Current status](generated-status.md)
- [Attract worklist](attract_worklist.md)

Address-level notebooks and hardware references are indexed separately in the
documentation map. They are research inputs, not competing sources of current
project status.

## ROM policy

`von/artifacts/` is for privately obtained ROMs only. ROM files and locally
derived media are ignored by Git and must not be redistributed. The tracked
`rom_manifest.json` contains labels, sizes, and hashes so contributors can
verify equivalent private dumps without storing ROM content.

Audit the local set with:

```sh
python3 von/tools/rom_audit.py
```

The files may pass integrity checks while the set identity remains
`unverified`; those are separate claims.

## Quick start

Prepare or build the reduced MAME target, then run the original `vonj` set:

```sh
./scripts/prepare-mame.sh
./scripts/remote-build.sh
./scripts/run.sh
```

Run the core verification path with:

```sh
./scripts/test.sh
./scripts/e2e.sh
./scripts/status.sh
```

Run the generated i960 image with:

```sh
./scripts/remote-i960-build.sh
./scripts/run-i960-reconstructed.sh \
  -video none -sound none -oslog -seconds_to_run 1 -skip_gameinfo
```

Complete command groups and patch-profile guidance are in
[operations.md](docs/operations.md).

## Repository boundaries

The workspace has three cooperating repositories:

```text
von-arcade-decomp
  capture, disassembly, recovered code, validation, asset generation
          |
          +--> von-runner
          |      native kernel boundary and provenance-gated extraction
          |
          +--> von-viewer
                 folder inspection and future validated evidence-pack showcase
```

`von-runner` and `von-viewer` are separate repositories and may be modified
concurrently. This repository must not write into them implicitly. Transfers
between projects should be explicit, reproducible commands that carry hashes
and evidence metadata.

## Hardware and reconstruction boundaries

- The i960 is the active replacement target.
- MAME currently supplies SHARC execution, SCSP/audio CPU behavior, and the
  communication model.
- Generic MAME Model 2 helpers may be adapted when behavior matches captured
  evidence and licensing is preserved.
- Virtual-On's uploaded SHARC semantics must be derived from ROM behavior, not
  inferred from plausible rendering.
- Temporary MAME tracing patches are evidence tools, not automatically
  upstream-ready changes.
- Geometry data, runtime transforms, textures, animation, identity, and audio
  semantics are separate validation claims.

The dedicated Virtual-On configuration omits the unrelated Sega Versus City
billboard controller instead of fabricating its separate ROM. Other Model 2
drivers retain their normal billboard configuration.

## Twin-cabinet target

The first multiplayer target is two local cabinet instances with independent
inputs and synchronized state. Launch them with:

```sh
./scripts/run-twin.sh
VON_TWIN_MATRIX=targeted ./scripts/test-twin.sh
```

One cabinet must be configured as Master and the other as Slave. Each run must
use isolated state directories. The retained findings and limitations are in
[versus-link-findings.md](versus-link-findings.md).

## Evidence rule

Every promoted reconstruction or asset follows the same progression:

```text
bounded hypothesis
  -> reproducible original capture
  -> readable model and focused test
  -> generated-image integration
  -> ordered original/reconstructed comparison
  -> canonical evidence registration
```

A file, model, trace, test count, or visual resemblance does not establish
validation by itself. Existing generated media is considered
`legacy-unreviewed` until reproduced by the current evidence pipeline.
