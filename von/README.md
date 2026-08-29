# Cyber Troopers: Virtual-On research workspace

This workspace is an arcade-first reverse-engineering project for Cyber Troopers:
Virtual-On. The initial runtime is MAME, used both as an execution environment
and as a behavioral oracle while the game and Model 2 hardware are documented.

The first playable target is two local players on one computer. The presentation
may be two windows or one combined two-screen layout; the important invariant is
that both cabinet units receive independent input and remain synchronized.

## ROM policy

`artifacts/` is for locally obtained ROMs only. ROM files are ignored by Git and
must not be added to commits or redistributed. `rom_manifest.json` contains only
labels, sizes, and cryptographic hashes so a contributor can verify an equivalent
private dump.

Run the audit from the repository root:

```sh
python3 von/tools/rom_audit.py
```

The current files are catalogued, but the manifest deliberately marks the set as
`unverified` until it is matched to an exact MAME software-list/driver revision.
The names suggest a Model 2 twin configuration; this is a hypothesis to verify,
not an assumption the tooling silently enforces.

## MAME harness

If MAME is installed, launch the default `vonj` set explicitly:

```sh
python3 von/tools/mame_runner.py --mame /path/to/mame --set vonu
```

The wrapper keeps ROMs in `von/artifacts`, writes emulator state/output below
`von/captures/`, and accepts additional MAME arguments after `--`:

```sh
python3 von/tools/mame_runner.py \
  --mame /path/to/mame --set vonu -- \
  -window -skip_gameinfo
```

The wrapper does not claim that the current MAME driver is complete. Missing
hardware behavior should be recorded as a reproducible scenario before it is
changed.

The initial hardware inventory is documented in [`chip-map.md`](chip-map.md).
It distinguishes confirmed board/ROM mappings from inferred and unresolved
physical chip identities.

The first host-ROM analysis is documented in
[`i960/boot-path.md`](i960/boot-path.md). Run `./scripts/disasm-i960.sh` to
recreate its local disassembly output.
Address-level interpretations are maintained in
[`i960/disassembly-annotations.md`](i960/disassembly-annotations.md).

### Billboard workaround

The shared Model 2B configuration normally includes the Sega Versus City
billboard controller, whose separate `epr-18022.ic2` ROM is not part of the
Virtual-On dump. The Virtual-On sets use a dedicated configuration that removes
that unused controller rather than substituting fabricated ROM data. Other Model
2 drivers retain the billboard device unchanged.

## Project scripts

Run the project workflow from the repository root:

```sh
./scripts/install.sh   # optionally install Homebrew dependencies
./scripts/prepare-mame.sh # clone/pin MAME and apply the selected patch set
./scripts/build.sh     # optional local reduced x64 MAME build
./scripts/build-mame-docker.sh # build the reduced target in Docker
./scripts/i960-build.sh # build the Docker-backed i960 C prototype
./scripts/remote-i960-build.sh # build the C images on drone0
./scripts/disasm-i960.sh # reconstruct and disassemble the original vonj i960 ROM
./scripts/trace-i960-boot.sh # trace reset and early host initialization in MAME
./scripts/trace-i960-reconstructed.sh # trace the C reconstruction under MAME
./scripts/remote-disasm-i960.sh # generate the original i960 listing on drone0
./scripts/disasm-cpu3.sh # normalize and disassemble the communication Z80
python3 von/tools/analyze_geo_upload.py # locate the captured geometry stream in main_data
python3 von/tools/analyze_i960_refs.py # list host-code references to Model 2 regions
python3 von/tools/compare_tile_trace.py --original <trace> --prototype <trace> # compare warning tile writes
./scripts/run-i960.sh  # run the generated i960 host ROM with original support ROMs
./scripts/run-i960-clean.sh # run generated code with only approved original data ranges
./scripts/audit-i960-clean-runtime.sh # prove a clean run executes generated code only
./scripts/test.sh      # audit ROMs and validate the local bin/von
./scripts/run.sh       # launch vonj locally; pass extra MAME arguments
./scripts/run-twin.sh  # launch two linked local cabinet instances
./scripts/test-twin.sh # configure roles, then run deterministic link/start diagnostic
./scripts/e2e.sh       # test and run one headless second
./scripts/deploy.sh    # test and create a ROM-free tarball
```

The default set is `vonj`. Override it with `VON_SET=vonu` when needed. Set
`JOBS` to control build parallelism. Deployment artifacts are written to
`dist/` and never contain files from `artifacts/`.

### Daily build and run workflow

Copy `config/remote-build.env.example` to
`config/remote-build.local.env` when the defaults need changing. The normal
build command synchronizes scripts, patches, and the modified communication
source to `drone0`, builds MAME in the remote Docker image, and copies the
result to `bin/von`:

```sh
./scripts/remote-build.sh
./scripts/run.sh                         # local single-player window
./scripts/run-twin.sh                    # local linked twin cabinets
./scripts/e2e.sh                         # ROM audit, validation, 1-second headless boot
./scripts/deploy.sh                      # package bin/von without ROMs
```

ROMs remain private in `von/artifacts/`. Each run creates a temporary staged
`vonj/` ROM directory and isolated capture/state directories. To build with
the optional tracing patches, use `VON_MAME_PATCH_SET=debug
./scripts/remote-build.sh`; the debug patch set is otherwise unchanged.

MAME preparation defaults to the `core` patch set, applying Virtual-On support
and communication diagnostics. Set `VON_MAME_PATCH_SET=debug` to include the
existing graphics tracing patches as well.

The generated i960 host ROM can be run directly with:

```sh
./scripts/run-i960.sh
./scripts/run-i960-reconstructed.sh
./scripts/run-i960-clean.sh
```

`run-twin.sh` starts two Model 2 cabinet processes with reversed communication
ports and isolated state directories. P2 is silent by default; P1 retains normal
audio. Each emulator process exposes its own P1 cabinet controls; host-level
keyboard/controller separation is a follow-up input-mapping task.

Use `VON_COMM_DIAGNOSTICS=1 ./scripts/run-twin.sh` to enable the isolated
communication trace. The diagnostic option reports link transitions, shared RAM
bytes `00..03`, the role byte, handshake/frame packet IDs, and transmit/receive
failures without enabling the graphics tracing patches. For a reproducible
matrix, run `VON_TWIN_MATRIX=targeted ./scripts/test-twin.sh`; use `full` only
after targeted candidates have been exhausted. Results and per-cabinet logs are
written below `von/captures/twin-diagnostic-*`.

The service manual calls the relevant game setting `Network Link Attribute` and
requires one seat to be Master and the other Slave. It also says versus settings
are effective from the Master side, so the harness keeps the eight SW3 bits
labelled unknown and varies them independently of the explicit communication
role override.

The confirmed versus/link findings and the passing capture are recorded in
[`versus-link-findings.md`](versus-link-findings.md).

`test-twin.sh` first drives the documented Test Menu directly through the MAME
input fields, sets P1 to Master and P2 to Slave, exits to commit the settings,
then injects credits, starts, and scripted movement/fire inputs. It uses fresh
per-cabinet state directories, so each matrix case starts from a clean saved
configuration. For a manual versus boot, focus each cabinet window in turn and press `5` to
insert a credit, then `1` to start. The default Virtual-On controls are the
P1 dual-stick bindings: `E/D/S/F` for the left stick, `I/K/J/L` for the right
stick, and `Left Ctrl`, `Left Alt`, `Space`, and `Left Shift` for buttons 1-4.
Both cabinets must be credited and started before diagnosing a match-start
stall. `Tab` opens MAME's input menu if these bindings have been changed.

## Project stages

1. Verify the dump and identify the exact arcade/twin set.
2. Establish deterministic boot, attract-mode, and versus-mode captures.
3. Repair Model 2 twin-unit communication, input routing, timing, and video
   presentation in the MAME driver.
4. Annotate disassembly and recover game subsystems behind explicit hardware
   interfaces.
5. Translate validated regions into readable, buildable source with regression
   traces against the original execution.

The full ROM-to-C work list is tracked in
[`reconstruction-roadmap.md`](reconstruction-roadmap.md), and measured
progress is tracked in [`reconstruction_ledger.json`](reconstruction_ledger.json).
Phase 0 inventory evidence is recorded in
[`phase0-inventory.md`](phase0-inventory.md).
The headline percentage counts only confirmed executable firmware bytes whose
generated C image matches the original bytes exactly. Validate and print the
current report with:

```sh
python3 von/tools/reconstruction_progress.py --report
```

Compare a candidate image against one ledger slice with:

```sh
python3 von/tools/reconstruction_progress.py \
  --compare maincpu/reset_startup \
  --original von/build/disasm/vonj-maincpu.bin \
  --generated von/build/i960/reconstructed-maincpu.bin
```

The comparison prints the equal-byte count and SHA-256 values; it does not
change the ledger status automatically.

Each unit follows [`reconstruction_work_unit.md`](reconstruction_work_unit.md):
classify a bounded slice, recover it into C, build it with the pinned target
toolchain, byte-compare it, run the relevant regression, and then update the
ledger. Behavioral reconstructions that do not yet byte-match remain
provisional and do not increase the headline percentage.

Saturn and PC versions are deferred until the arcade path is understood.
