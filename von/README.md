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
./scripts/trace-geometry-twin.sh # capture and export linked player-select geometry
./scripts/trace-geometry-first-match.sh # capture and export the deterministic first match scene
./scripts/trace-geometry-material-twin.sh # capture first-match geometry and indexed materials
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
and communication diagnostics. Set `VON_MAME_PATCH_SET=geometry-trace` for the
focused geometry extraction instrumentation, `geometry-material` to add
first-match texture-command tracing, or `VON_MAME_PATCH_SET=debug` to include
all existing graphics tracing patches.

### Geometry capture and model extraction

The debug patch set instruments the Model 2 polygon renderer at three useful
boundaries: object submissions, transformation-matrix writes, and accepted
polygons after vertex transformation. The polygon ROMs can be assembled into
the CPU-visible geometry address space, so a capture can be turned into raw
meshes without redistributing ROM data:

```sh
VON_MAME_PATCH_SET=debug ./scripts/remote-build.sh
./scripts/trace-geometry-select.sh
python3 von/tools/extract_geometry_rom.py
python3 von/tools/dump_geometry_objects.py \
  --trace von/build/disasm/vonj-geometry-select-40s.trace
./scripts/export-player-select-models.sh \
  von/build/disasm/vonj-geometry-select-40s.trace
```

That batch command emits one OBJ and one self-contained glTF asset per unique
polygon-ROM object. Individual objects can also be exported directly:

```sh
python3 von/tools/export_geometry_obj.py \
  --oba 0x0084553f \
  --output von/build/disasm/geometry-objects/oba-0084553f.obj
python3 von/tools/export_geometry_gltf.py \
  von/build/disasm/geometry-objects/oba-0084553f.obj \
  von/build/disasm/geometry-objects/oba-0084553f.gltf
```

When a capture contains complete 40-object select-screen frames, the matrix
trace can be exported as one animated glTF model:

```sh
python3 von/tools/export_geometry_animation_gltf.py \
  --trace von/build/disasm/vonj-geometry-select-40s.trace
```

For a diagnostic view of polygon submission order, export a single geometry
frame as a cumulative triangle animation. It filters to mode-3 polygon-ROM
submissions (excluding the video/HUD path) and caps the output by default:

```sh
python3 von/tools/export_geometry_triangle_build_gltf.py \
  --trace von/captures/twin-vonj-20260830T144329Z/p2/mame.log \
  --rom von/build/disasm/geometry-rom.bin \
  --time 16.288808 --min-objects 40 --max-triangles 3000 \
  --output von/build/disasm/triangle-build.gltf
```

Open the result in F3D and play `triangle_submission_order`; triangles appear
in traced submission order. Early entries are commonly arena geometry, which
is useful for identifying the point where fighter submissions begin.
Use `--start-object N --max-objects M` to isolate a contiguous submission
assembly while retaining its original slot number in every triangle node.
For the recorded deterministic first match, slots 6–24 form a complete
1,706-triangle Virtualoid assembly (rather than arena geometry):

```sh
python3 von/tools/export_geometry_triangle_build_gltf.py \
  --trace von/captures/twin-vonj-20260830T144329Z/p2/mame.log \
  --rom von/build/disasm/geometry-rom.bin \
  --time 16.288808 --min-objects 40 --start-object 6 --max-objects 19 \
  --max-triangles 0 --seconds 12 \
  --output von/build/disasm/fighter-assembly-slot-06.gltf
```

For extraction rather than diagnosis, use the static frame exporter with the
same ROM-backed submission slice. This emits one mesh per unique ROM OBA and
one transformed node per submitted part: it is the lightweight model file to
open or archive.

```sh
python3 von/tools/export_geometry_frame_gltf.py \
  --trace von/captures/twin-vonj-20260830T144329Z/p2/mame.log \
  --rom von/build/disasm/geometry-rom.bin \
  --time 16.288808 --min-objects 40 --start-object 6 --max-objects 19 \
  --output von/build/disasm/fighter-assembly-slot-06-static.gltf
```

The polygon-ROM decoder has a small independently verified format boundary.
An OBA is a word address (`(oba & 0x3fffff) * 4`) into the assembled polygon
ROM. It begins with two float3 seed points, followed by fixed-size polygon
records. Each record contains an attribute word, three non-position words,
and two float3 positions. Attribute bit 0 selects a quad; otherwise the final
float3 remains present in the record but is not a polygon corner. Quads use
the stored corner grid order `p0, p1, p2, p3` and are triangulated as
`(p0,p1,p2)` plus `(p1,p3,p2)`. The arena floor object `0x0091af12` is the
minimal validation case: it is exactly one 10,000-by-10,000 quad at local
`y = -40`, and both exported halves have the same facing. Attribute bits
8–9 update the two seed points for the following record; their final hardware
names remain intentionally undecided.

The geometry trace also records the parser opcode that invokes each object
submission. In the deterministic first-match capture at `16.288808`, all 40
polygon-ROM submissions—including the complete slots 6–24 Virtualoid
assembly—use `0x00800101`. This establishes one concrete model-object command
class for the next SHARC/geometry-buffer recovery pass; it does not yet expose
the upstream entity or transform packet format.

The single-cabinet capture script uses `bin/von` directly and defaults to SDL's
dummy video backend, so it also works on headless build hosts. A single cabinet
can remain at the Model 2 boot screen while waiting for the twin communication
link; that is expected for this game and is why player-select extraction uses
the linked harness below.

For a reproducible linked capture that drives both cabinets through coin/start
and exports the first 40-object player-select frames, run:

```sh
VON_MAME_PATCH_SET=geometry-trace ./scripts/remote-build.sh
VON_GEOMETRY_TWIN_SECONDS=20 ./scripts/trace-geometry-twin.sh
```

The command writes the raw per-cabinet traces below `von/captures/`, then emits
40 individual OBJ/glTF object assets and a self-contained animated glTF for
each cabinet below `von/build/disasm/player-select-twin-*/`. The linked run must
be allowed to bind localhost sockets; sandboxed environments may need their
network namespace disabled for this diagnostic.

After machine selection, the game plays a short in-game scene before entering
the first match. The first opponent and arena are deterministic, making this a
useful geometry extraction checkpoint. The first-match capture disables combat
inputs so movement and firing do not alter the scene:

```sh
VON_MAME_PATCH_SET=geometry-trace ./scripts/remote-build.sh
./scripts/trace-geometry-first-match.sh
```

The command records the linked raw traces below `von/captures/`, exports each
unique polygon-ROM object as OBJ/glTF, and writes a timestamped scene glTF with
all object slots and their traced transforms below
`von/build/disasm/first-match-twin-*/`. The standalone frame exporter can target
a known timestamp or automatically select the latest frame before a cutoff:

```sh
python3 von/tools/export_geometry_frame_gltf.py \
  --trace von/captures/<capture>/p1/mame.log \
  --output von/build/disasm/first-match-frame.gltf \
  --max-time 32.8 --min-objects 100
```

For material evidence, build the `geometry-material` profile and run its
passive capture wrapper:

```sh
VON_MAME_PATCH_SET=geometry-material ./scripts/remote-build.sh
./scripts/trace-geometry-material-twin.sh
```

This records bounded texture commands beginning at the known post-selection
transition and extracts referenced indexed texture tiles as PGM previews with
an `index.tsv` manifest beside the scene exports. Each object also receives a
`textured-objects/oba-*.gltf` export with UV accessors, glTF material groups,
and embedded PNG tiles rendered through the captured palette, color-translation,
and luma state. The same capture also emits a complete
`first-match-frame-textured.gltf` scene with the traced object slots and
transforms; its palette state is selected at the frame's geometry timestamp.
The isolated object files record that same timestamp as `extras.palette_time`
so their rendering provenance is visible without consulting the trace.
For example:

```sh
./scripts/view-geometry.sh \
  von/build/disasm/first-match-material-twin/<capture>/p1/textured-objects/oba-00a670ca.gltf
./scripts/view-geometry.sh \
  von/build/disasm/first-match-material-twin/<capture>/p1/first-match-frame-textured.gltf
```

The standalone exporter remains able to emit grayscale tiles when
`--palette-trace` is omitted; this preserves the recovered 4bpp texel values
when no palette capture is available. The material wrapper enables palette
tracing so its model artifacts use the recovered RGB path and freezes isolated
object previews at the same selected frame timestamp as the combined scene.

For a lightweight isolated preview, Chromium is enough; no Blender or external
JavaScript packages are required. The viewer supports drag orbit and wheel zoom:

```sh
./scripts/view-geometry.sh \
  von/build/disasm/first-match-scenes/p1-first-match.gltf
./scripts/view-geometry.sh \
  von/build/disasm/first-match-geometry-objects/oba-0091e76c.gltf
```

The first command shows the extracted scene. The second shows one object in
isolation; replace the filename with any exported `.gltf`. The script serves
the files only on localhost and opens the bundled dependency-free WebGL viewer
in Chromium.

`geometry-trace` is a smaller build profile containing only the object/matrix
geometry instrumentation and renderer-boundary diagnostics. It avoids the
high-volume polygon and texture logs in the full `debug` profile, which makes
linked extraction practical on slower build hosts.

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

### Current reconstruction milestone

The latest pass recovered the profile-dependent transfer schedule of the
startup asset loader at `0x1bda0-0x1c21c`. Its new descriptor API identifies
20 profile-zero and 17 alternate-profile operations: packed color-table
expansion, ROM halfword byte swaps into mapped RAM, a small `0x9999` fill, and
four final table expansions. This makes the early graphics/asset layout
inspectable without executing mapped hardware writes; resource names and active
integration remain the next boundary.

It also now records the adjacent `0x1c220` video-control bootstrap: two
control-window writes, the fixed `0x1c730` helper request, six caller-value
state writes around video clearing, and the terminal `0xffffffff` state
sentinel. These plans are inspectable and regression-tested before mapped
hardware-write integration.

The `0x1c730` helper behind that bootstrap is now recovered as an exhaustive
byte-to-four-bit-lane expansion. Trace captures now automatically emit compact
JSON and Markdown summaries with checksums, event counts, and collapsed repeated
diagnostics. Run `python3 von/tools/summarize_mame_trace.py <trace> --archive`
to retain a raw trace losslessly as gzip while replacing its plaintext copy.

The preceding unattended pass recovered five additional host-side audio units
from the i960 attract trace and integrated the SCSP startup sequence into the
reconstructed main path:

- `0x2a430`: four-iteration SCSP register-settle delay
- `0x2a5f0`: alternate status-gated 16-bit audio command sender
- `0x2a690`: signed level clamp to `1..127` and `0xa0, 1, level` framing
- `0x2a870`: raw `0xa0, 0, low_byte(value)` command sender
- `0x2a8a0`: 64-byte FIFO initialization, SCSP control sequence, and startup
  `0xff` command

The producer and consumer paths are covered by exhaustive host-side tests,
including 983,040 parameterized framing vectors, 262,144 frame vectors,
266,240 FIFO-capacity vectors, 20,480 consumer vectors, and 65,536 interrupt
mask vectors and 65,536 text font-mode prefixes. The full test script, ROM
audit, and MAME validation pass. The
drone0 i960 build produces the reconstructed image, and the clean runtime
audit confirms that all 320 visited instructions execute from generated code.

The ledger currently records `6,116/6,116` classified executable bytes as
C-represented behavioral reconstructions. The strict byte-match headline is
still `0/6,116`, because these slices remain provisional pending compiler/ABI
calibration and byte-for-byte comparison. The refreshed 60-second attract
worklist contains 41 represented units and 221 remaining untriaged units.

Saturn and PC versions are deferred until the arcade path is understood.
