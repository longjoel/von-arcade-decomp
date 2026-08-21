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

If MAME is installed, launch a set explicitly:

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

### Billboard workaround

The shared Model 2B configuration normally includes the Sega Versus City
billboard controller, whose separate `epr-18022.ic2` ROM is not part of the
Virtual-On dump. The Virtual-On sets use a dedicated configuration that removes
that unused controller rather than substituting fabricated ROM data. Other Model
2 drivers retain the billboard device unchanged.

## Project scripts

Run the project workflow from the repository root:

```sh
./scripts/install.sh   # install Linuxbrew build dependencies
./scripts/prepare-mame.sh # clone/pin MAME and apply project patches
./scripts/build.sh     # build the reduced x64 MAME target
./scripts/i960-build.sh # build the Docker-backed i960 C prototype
./scripts/disasm-i960.sh # reconstruct and disassemble the original vonj i960 ROM
./scripts/trace-i960-boot.sh # trace reset and early host initialization in MAME
python3 von/tools/analyze_geo_upload.py # locate the captured geometry stream in main_data
python3 von/tools/analyze_i960_refs.py # list host-code references to Model 2 regions
./scripts/run-i960.sh  # run the generated i960 host ROM with original support ROMs
./scripts/test.sh      # audit ROMs and validate the vonj driver
./scripts/run.sh       # launch vonj; pass extra MAME arguments
./scripts/run-twin.sh  # launch two linked cabinet instances
./scripts/e2e.sh       # build, test, and run one headless second
./scripts/deploy.sh    # build, test, and create a ROM-free tarball
```

The default set is `vonj`. Override it with `VON_SET=vonu` when needed. Set
`JOBS` to control build parallelism. Deployment artifacts are written to
`dist/` and never contain files from `artifacts/`.

The generated i960 host ROM can be run directly with:

```sh
./scripts/run-i960.sh
```

`run-twin.sh` starts two Model 2 cabinet processes with reversed communication
ports and isolated state directories. P2 is silent by default; P1 retains normal
audio. Each emulator process exposes its own P1 cabinet controls; host-level
keyboard/controller separation is a follow-up input-mapping task.

For a manual versus boot, focus each cabinet window in turn and press `5` to
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

Saturn and PC versions are deferred until the arcade path is understood.
