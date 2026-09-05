# Reconstruction handbook

## Objective and scope

The active objective is an input-free, 60-emulated-second `vonjdev` attract
run whose i960 execution comes entirely from generated source. MAME continues
to provide the Model 2 devices, audio CPU, SHARC, and communication model.
Original, privately held asset ROMs remain available to the local runtime.

The milestone is complete only when the replacement image:

1. resets and initializes the board;
2. uploads and starts geometry/SHARC support;
3. initializes texture, palette, tile, text, and audio command paths;
4. enters the attract scheduler;
5. renders legal/title and continuing attract activity;
6. produces audio command activity;
7. remains alive for 60 emulated seconds; and
8. executes no original i960 instructions.

Credit handling, character selection, a complete match, results, versus play,
service menus, replacement audio firmware, and replacement communication
firmware are later objectives.

## Current reconstruction boundary

The current generated image has crossed the reset, hardware-startup, attract-
scheduler, and short-runtime boundaries. `reconstructed_main.c` records the
startup phases through `INIT`; the state trace also records a nonzero heartbeat,
an attract transition, text-tile effects, and the generated audio bridge's
startup command. The latest rebuilt development run completed 60 emulated
seconds and recorded seven recurring geometry submissions. These observations
are development evidence until they are registered with the canonical evidence
manifest.

Two boundaries remain deliberately explicit. Geometry startup now performs the
validated SHARC and geometry-program uploads, profile/register initialization,
texture setup, command-window preparation, and initial handshake, but it does
not submit the unvalidated bulk display-list stream. The audio initializer emits the observed
framed startup bytes through the host-visible UART without raising the
unrecovered interrupt vector. Neither bridge should be promoted to a complete
original-path equivalence claim without a bounded original/reconstructed event
comparison.

### Original boot/title capture (drone0, 2026-09-04)

A fresh 30-second original `vonj` run was captured on `drone0` at roughly
120% emulation speed. The half-second screenshots and trace show this ordered
presentation: Model 2 BCRX startup/status text and coprocessor/geometry/texture
loading; the Japanese-set legal warning at approximately frame 780; the
animated SEGA logo at approximately 15–16 seconds (capture frames 0030–0032);
and the graphics-only
`VIRTUAL-ON` title/`INSERT COIN(S)` attract screen. A separate scripted-input
run then confirmed the later `VR.TEMJIN` machine-select path.

The matching no-input sound-enabled capture is a 30-second stereo 44.1 kHz PCM
WAV and is non-silent (mean -34.6 dB, peak -15.5 dB). This establishes the
reproducible audiovisual fixture needed to isolate the logo animation and its
sound commands.

The repro now enters a generated `SEGA` phase at the captured boot-relative
time. `reconstructed_main.c` owns the phase transition and submits captured
tile IDs through the normal Model 2 tile device; `recovered_sega_char.c` restores
the matching original character-RAM window. The temporary renderer-side logo
overlay has been removed. The remaining mismatch is tile presentation state
(layer timing/control and the logo's exact animation), not a 3D display-list or
texture-parser issue.

The boot/title timing is now also a first dual-target slice: the pure
`recovered_attract_schedule.c` implementation is compiled into the i960 image
and natively exercised by `test_recovered_attract_schedule.py` on Linux. The
hardware-facing render and MMIO calls remain behind the next platform-boundary
step.

The SEGA phase now crosses that boundary through
`recovered_attract_platform.c`: Linux records the typed presentation event,
while the i960 adapter owns the same event's work-RAM and video side effects.
The focused recorder tests and the full 60-second clean attract audit both
pass.

The next integration unit is therefore the earliest missing sustained-attract
discriminator: validate one legal/title-to-attract geometry submission against
the original parser boundary. Its fixture should contain the smallest accepted
command window and the corresponding video/geometry state changes. If that
fixture cannot be made safe, record the first parser divergence and keep the
bulk stream out of the generated image. After that comparison, rerun the
ordered gates and register the 60-second run plus the generated-PC exclusion
audit as canonical evidence.

### Geometry packet integration (2026-09-05)

The existing `recovered_geometry_object_packet.c` model is now linked into the
generated i960 image. At recurring match-entry geometry ticks,
`recovered_geometry_object_packet_probe()` emits the proven first-emitter
submission into the command-window scratch boundary: the ten-word
`0x2f/0x16/0x15/0x14` prefix, tagged transform continuation, `0x06/0x05/0x06`,
the six-word `0x1f` XZ request, and the response-forwarded `0x0a` request.
This integrates the packet producer while keeping its unvalidated payload out
of the display-list parser. The packet vector test, ledger validation, remote
i960 build, and a 30-second reconstructed run all pass. A bounded 35-second
original capture records 4096 FIFO events; `analyze_geometry_object_packet_trace.py`
finds the exact ten-word prefix at PCs `0x34048..0x340e4`, including the
concrete `b6d0/4c4c/bb8b` base and `0x6c/0x17/0xffffff80` parameters. The
unit is now `trace-validated` for prefix framing and the first sample. The
reconstructed probe still writes command-window scratch rather than the
unvalidated display-list FIFO, so full payload timing and downstream geometry
consumption remain provisional.

The match-entry seed now also uses the first captured matrix/object batch from
`twin-vonj-20260901T165911Z/p1`: one exact 3x4 matrix, the legal
`0x00800101` polygon-ROM opcode, and eight ordered object records (`oba`
`0x0084553f` through `0x009e3f80`). This replaces the former single-object
placeholder while retaining the parser-safe seed boundary; later frame and
transform records are not yet reconstructed.
Each four-word record is built through
`recovered_geometry_polygon_object_submission()`, which preserves the traced
`tpa/tha/oba/count` field order and the legal `0x00800101` opcode boundary.
Matrix records are emitted through `recovered_geometry_matrix_submission()`,
which preserves the `0x05800000` opcode and all twelve IEEE-754 words.
The MMIO seed now preserves the observed interleaving: matrix 1 with object 1,
matrix 2 with objects 2–4, matrix 3 with objects 5–6, and matrices 4–5 with
objects 7–8.

The refreshed remote i960 build produced a 34,256-byte generated image and
the reconstructed `vonjdev` target completed a 35-emulated-second headless
run at 100% average speed. This verifies that the expanded seed is accepted by
the current development runtime; it is not yet evidence of full original
frame equivalence.

The reconstructed-side geometry callbacks are now enabled under `vonjdev`.
Comparing the rebuilt run against the preserved original capture with
`compare_geometry_event_prefix.py` gives an exact match for the first 13
ordered matrix/object events, including all matrix values and object
`tpa/tha/oba/count` fields. This is the first direct original-versus-C
geometry equivalence slice; later events remain outside the seeded fixture.

The geometry-profile rebuild initially exposed a startup boundary: the SHARC
upload was incorrectly implemented as an incrementing pointer, truncating the
fixed FIFO window at 8,192 words and causing `copro_adsp` PC-stack underflow.
The transport now writes all 11,038 words to the fixed FIFO address, and the
geometry program port is likewise exercised from its validated ROM-backed
window. A fresh 60-emulated-second run completes at 96.4% average speed,
emits 18,811 geometry callbacks, and retains the 13-event original-vs-C prefix
match. The remaining provisional boundary is downstream display-list
consumption, not startup upload transport.

The display-list seed now includes the parser-observed setup grammar
(`0x0b001616` through `0x08001010`) before the validated matrix/object records,
followed by the bounded end opcode `0x07800f0f`. This prevents the parser from
falling through into the recurring startup sentinel. The setup opcode and
payload prefix now agree with the original late-run trace; texture parameter
and texture-data counts are deliberately zero until their bulk payloads are
validated. The rebuilt 60-second run remains stable (95.1% average speed,
18,811 geometry callbacks, 13-event exact prefix match), so the unresolved
fidelity boundary is explicitly the texture/display-list payload rather than
transport or parser alignment.

The player-model evidence is now also consumed by the generated C display list:
the seed emits all 40 polygon-ROM object slots observed at the exact
`16.288808`-second select-screen frame (including the four model assemblies and
their component meshes), rather than only the original eight-object probe.
The reconstructed 35-second run remains stable at 100.00% average speed and
logs 2,440 object callbacks with the complete 37-matrix/40-object event
sequence repeated across the run.

The source-window boundary is reproducible without embedding guessed C arrays.
`von/tools/extract_coprocessor_sources.py` assembles the four maincpu ROMs and
the main_data ROM pairs, then extracts the exact upload slices into build
fixtures. The recorded lengths and SHA-256 values are checked in at
`von/i960/coprocessor-source-windows.json` and covered by
`von/tools/test_extract_coprocessor_sources.py`.

A follow-up 60-emulated-second run of the same rebuilt image also completed at
99.99% average speed. The generated-state trace records a continuously
advancing heartbeat and attract phase, with `geometry_submissions=7` by the
end of the window. This closes the current runtime-stability gate while later
frame geometry remains a fidelity work item.

## Source of truth

### Baseline recheck (2026-09-04)

The refreshed unit, contract, and trace suites pass. Smoke fails because its
geometry projection and two SHARC helper tests depend on missing development
captures, including `vonj-geometry-select-50s.trace`,
`von-sharc-opcode-17-helper-sweep-reset45-delayed.trace`, and
`von-sharc-opcode-17-nonzero.runtime.log`. These files were not found in the
local workspace or the corresponding `drone0` build directory. Restore or
reproduce the fixtures before promoting another integration unit; missing
captures are not evidence of a behavioral mismatch.

The clean runtime audit now rejects empty PC coverage and requires a recorded
emulated completion time reaching the requested duration. Each invocation has
its own capture and cabinet-state directories under
`von/build/i960/clean-audit/run-*`, preventing reuse of old coverage and mixed
progress logs. Regression cases cover empty, escaped, unaligned, incomplete,
and duplicate-completion captures, plus a valid completed capture.
An isolated diagnostic rerun completed 60 emulated seconds with exit status
zero and 1,340 observed ROM PCs inside the generated extent (`0x7db0` bytes).
Its local capture is `von/build/i960/clean-audit/run-tv3ifiMM/`; this does not
override the failed smoke gate or constitute canonical evidence.

This remains a bounded runtime check: the Lua collector enumerates only the
first 2 MiB of ROM addresses and starts tracking from its periodic callback.
It does not yet prove coverage from reset or absence of execution elsewhere
in the address space, and it does not compare audiovisual behavior. The
historical attract pass must not be promoted to complete reconstruction
equivalence on that basis.

Run:

```sh
./scripts/status.sh
```

The ledger owns lifecycle state, the worklist owns the current closure queue,
the test manifest owns suite membership, and the evidence manifest owns
canonical evidence. Narrative documents intentionally do not repeat their
totals.

Before selecting more work, run the live status and regenerate stale reports:

```sh
./scripts/status.sh --write-markdown
```

Treat the generated reports as a snapshot of the machine-readable state, not
as a second plan. A large modeled queue is not parallel work in progress: the
active limit remains one integration unit and one supporting experiment.

## Checkpoint contract

The milestone is a sequence of observable gates. A later gate must not be used
to justify work while an earlier gate is failing.

| Order | Checkpoint | Minimum observation |
| --- | --- | --- |
| 1 | generated reset | reset and initial register/stack setup execute from generated code |
| 2 | hardware initialization | board, texture, palette, tile/text, geometry, SHARC, and audio setup complete |
| 3 | attract scheduler | the input-free scheduler reaches its attract state transition |
| 4 | legal/title output | title or legal presentation produces the expected watched video/text effects |
| 5 | audio activity | the original and generated paths emit comparable audio commands |
| 6 | sustained attract | geometry/video state continues changing through the 60-second run |
| 7 | clean execution | no exception, stall, or executed i960 PC outside generated code |

For every failed gate, record the last matching ordered event and the first
divergent event. The first divergence, rather than the largest coverage gap,
selects the next work unit. Coverage-only edges remain possible static edges
until a causal trace observes the call.

## Lifecycle

| Stage | Meaning |
| --- | --- |
| `planned` | Stable identity and a reason the unit may matter. |
| `modeled` | Bounded readable implementation and focused test exist. |
| `integrated` | The generated image invokes it on the target path and prior checkpoints still pass. |
| `trace-validated` | Ordered effects match original execution for canonical evidence. |
| `byte-validated` | Generated bytes match the declared original range. |
| `blocked` | A named missing fact prevents safe progress and defines the next experiment. |

Physical ROM classification and semantic lifecycle are separate. Only the
union of physical `code` ranges contributes byte coverage. Behavioral C can be
valuable without matching the original compiler's instruction selection.

## Work-unit loop

Keep one active integration unit and at most one supporting experiment:

1. Select the unit closest to the earliest failing runtime checkpoint.
2. State one falsifiable hypothesis and expected discriminator.
3. Prove the function boundary, dynamic caller, exits, and relevant data or
   hardware references.
4. Capture the smallest original fixture that distinguishes the behavior.
5. Implement production C through an explicit hardware interface.
6. Add a focused unit or contract test.
7. Link and invoke the implementation in the replacement image.
8. Compare ordered original and reconstructed effects.
9. Rerun every earlier checkpoint.
10. Register canonical evidence and update the ledger in the same change.

Use the queue-item, capture, evidence, and promotion templates in
[Evidence and assets plan](evidence-and-assets-plan.md).

The active unit must name the checkpoint it is expected to advance. Its
working record includes one falsifiable hypothesis, one discriminator, the
dynamic caller or entry evidence, the relevant inputs and outputs, and the
smallest fixture that can reproduce the decision. If the discriminator does
not change the queue, implementation, confidence, or verifier, stop the
experiment and quarantine its output instead of expanding the capture.

Do not open a second modeled implementation unit while the active unit is
awaiting integration or comparison. A supporting experiment is allowed only
when it resolves a named uncertainty in that unit.

## Validation commands

```sh
./scripts/test.sh
python3 von/tools/run_tests.py trace
python3 von/tools/run_tests.py smoke --jobs 1
python3 von/tools/run_tests.py attract --jobs 1
```

From `von/`, the recovered C collection also supports:

```sh
make check-recovered-c
make check
```

`unit`, `contract`, and `trace` are designed not to require private ROMs.
`smoke` checks a short clean-image boot. `attract` owns the complete milestone
and must reject execution outside generated code.

The required validation order is `unit`, `contract`, `trace`, `smoke`, then
`attract`. A changed producer, test manifest, capture recipe, or ledger makes
the corresponding generated result stale; report the stale state rather than
copying an old result into this document.

## Engineering order

1. Establish a clean baseline by running the currently stale trace, smoke, and
   attract suites.
2. Identify the earliest failing checkpoint and first divergent event.
3. Integrate and validate an existing modeled dependency on that path.
4. Open new discovery only when the active failure lacks a modeled dependency.
5. Advance through scheduler, title/UI, audio commands, and sustained geometry
   activity in checkpoint order.
6. Calibrate byte reproduction separately with the pinned Intel CTOOLS track.

At each step, preserve the earlier checkpoint fixtures and rerun them after an
integration change. Promote a unit only when its lifecycle evidence is
complete: readable bounded behavior and a focused test for `modeled`, generated
image invocation and earlier-gate stability for `integrated`, and a registered
canonical original/reconstructed event comparison with a passing verifier for
`trace-validated`. Byte similarity is an independent claim and never replaces
behavioral evidence.

The broad SHARC probe campaign is frozen. New SHARC work requires a named host
integration failure that existing evidence cannot discriminate.

## Longer-term sequence

- Complete the C-only attract path.
- Recover credit, selection, and single-player match flow.
- Validate linked two-cabinet game state and inputs.
- Decide whether communication Z80 and audio 68000 replacement are required.
- Resolve remaining code/data classification and optional byte matching.
- Publish reproducible validation reports and explicitly unsupported hardware.

## Work-unit template

```yaml
id: maincpu.example-service
image: maincpu
subsystem: example
range: {start: 0x00000000, end: 0x00000000}
checkpoint: scheduler-enters-attract
stage: planned
hypothesis: <one falsifiable statement>
expected_discriminator: <specific event or state difference>
entry_and_callers: <static and dynamic evidence>
inputs: <registers, memory, and hardware state>
outputs: <return values and ordered side effects>
source: von/i960/recovered_example.c
tests: []
evidence_ids: []
unresolved: []
```

Do not create comparison-only wrappers or no-op dependencies to increase a
metric. A failed unit records its earliest failure and does not advance stage.
