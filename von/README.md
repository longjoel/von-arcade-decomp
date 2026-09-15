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

The `vonctl` harness (`./bin/vonctl`) is the single entry point; the
`scripts/*.sh` wrappers are one-line shims onto it.

Build the reduced MAME target, then run the original `vonj` set:

```sh
./bin/vonctl build mame      # or: ./bin/vonctl build remote
./bin/vonctl run
```

Run the core verification path with:

```sh
./bin/vonctl test
./bin/vonctl e2e
./bin/vonctl status
```

Run the generated i960 image with:

```sh
./bin/vonctl build i960-remote
./bin/vonctl i960 reconstructed \
  -video none -sound none -oslog -seconds_to_run 1 -skip_gameinfo
```

Complete command groups are in
[operations.md](docs/operations.md).

## Repository boundaries

The workspace has four cooperating repositories. `von-discovery` is an archive
of superseded scripts and is not part of the live pipeline.

```text
von-arcade-decomp
  capture, disassembly, recovered code, validation, asset generation
          |
          +--> von-runner
          |      native kernel boundary and provenance-gated extraction
          |
          +--> von-godot
          |      Godot presentation host
          |
          +--> von-data-tool
                 ROM forensics, model/audio/texture browser, clip labeler
```

Each repository may be modified concurrently with the others. This repository
must not write into them implicitly. Transfers between projects should be
explicit, reproducible commands that carry hashes and evidence metadata. The
retired `von-viewer` browser has been folded into `von-data-tool`.

## Hardware and reconstruction boundaries

- The i960 is the active replacement target.
- MAME currently supplies SHARC execution, SCSP/audio CPU behavior, and the
  communication model.
- Generic MAME Model 2 helpers may be adapted when behavior matches captured
  evidence and licensing is preserved.
- Virtual-On's uploaded SHARC semantics must be derived from ROM behavior, not
  inferred from plausible rendering.
- New instrumentation belongs in the engine's Lua API, not in additional C++
  tracing patches. The `mame/` submodule is the `longjoel/mame-von` fork; its
  driver and debugger fixes are committed there.
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
[versus-link-findings.md](docs/versus-link-findings.md).

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
