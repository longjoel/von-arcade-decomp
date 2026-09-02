# MAME SHARC precision follow-up

This is the proposed follow-up from the Virtual-On reduction work. It is kept
separate from the game-specific recovered C model because the current
Virtual-On trig path already agrees between MAME's DRC and interpreter.

## Confirmed architectural requirement

The ADSP-2106x manual describes a 40-bit extended format with an eight-bit
exponent and a 32-bit mantissa. With `MODE1.RND32` set, the computation unit
zeros the low eight bits of each 40-bit input before an ALU or multiplier
operation, performs the operation, rounds the result to the IEEE 32-bit
boundary, and writes the low eight result bits as zero. Fixed-point-to-float
conversion is the exception: `FLOAT` always rounds to the 40-bit boundary.

The primary reference is Analog Devices, *ADSP-2106x SHARC Processor User's
Manual*, revision 2.1, sections 2.2.1, 2.5.2.3, and 2.6.4. Its relevant
statements are summarized in the repository's SHARC notes and linked from
`disassembly-annotations.md`.

## MAME gap

The current MAME SHARC core represents each data register as the union
`{ int32_t r; float f; }` in `src/devices/cpu/sharc/sharc.h`. The interpreter's
`FADD` and `FMUL` helpers in `compute.hxx` therefore perform finite arithmetic
through host `float`; `MODE1.RND32` is declared in the core but is not used to
apply a 40-bit input/output boundary there. The DRC has its own 32-bit
floating operations, so it has the same architectural gap rather than merely
being out of sync with the interpreter.

The Virtual-On capture gives us a useful real-world reproducer without making
the game part of the fix: i960 PC `0x000c58d4` sends SHARC opcode `0x17`, and
the handler emits a variable-length result stream through SHARC output address
`0x00c00000`. The generic MAME layer should preserve that FIFO stream exactly;
the recovered project can then interpret its words as geometry data. This is
also why the first upstream patch should improve the SHARC numeric core and
its neutral test harness, rather than special-case opcode `0x17` or the
`0xbdcccccd` sentinel.

## What can be borrowed from MAME

Yes. The SHARC implementation files in this checkout carry MAME's BSD-3-Clause
license headers, so code adapted from them can remain compatible with this
project when the attribution and license notice are retained. This does not
apply automatically to every file in the MAME tree; each source file's header
is the authority for its contribution.

The useful reuse is concentrated in three places:

* `src/devices/cpu/sharc/sharcops.hxx` defines instruction dispatch, register
  selection, memory-operation ordering, delayed control transfers, and
  ASTAT/STKY flag conventions. These are good references for making a
  standalone interpreter agree with SHARC timing and side effects.
* `src/devices/cpu/sharc/compute.hxx` contains the operation-by-operation
  exception policy: denormal flushing, canonical NaNs, overflow saturation in
  truncate mode, and ASTAT/STKY updates. Its arithmetic implementation is
  currently 32-bit, so it is a policy reference rather than a drop-in
  implementation of the extended format.
* `src/devices/cpu/sharc/sharcdrc.cpp` and `sharcfe.cpp` show how MAME lowers
  the same instruction semantics into UML and handles delayed branches. They
  are useful for the eventual interpreter/DRC parity patch, but their generated
  code should not be copied into the recovered game routines.

The local `sharcfloat40.h` seam follows this plan: it is a small BSD-marked,
host-independent implementation developed for the missing 40-bit behavior,
while the recovered Virtual-On C files use only ROM-observed contracts. The
next MAME contribution should adapt the generic arithmetic and flags in the
core, then add neutral CPU fixtures; it should not add Virtual-On addresses or
geometry assumptions to MAME.

The seam's first large-exponent regression is now fixed. A `FADD` with an
exponent gap greater than the destination precision used to left-shift the
larger significand into a wrapping `uint64_t`, and the zero operand's sentinel
shift could also be mistaken for a real exponent. The helper now handles zero
identity cases explicitly, bypasses irrelevant far operands, and evaluates the
exact half-ULP case without an overflowing alignment shift. The new fixture is
`fadd_far_exponent_does_not_overflow_alignment`; both the MAME seam harness and
the independent arbitrary-width oracle pass it.

The seam now also classifies the four non-normal classes (denormal, infinity,
NaN, and signed zero). Since only normal values and signed zero are implemented
by this transitional register model, `decode()` rejects the other three
classes explicitly instead of treating their exponent fields as ordinary
normals. The MAME harness covers all three rejection cases; this is an
intentional guard until the generic SHARC exception policy is moved into the
40-bit representation.

The arithmetic seam now widens significand intermediates to 128 bits. Two
normal SHARC significands contain 33 bits including the hidden bit, so a
multiply can require 66 bits before normalization; the former 64-bit product
could wrap before the destination precision was applied. The shared fixtures
`fmul_wide_significand_does_not_wrap` and
`fmul_wide_significand_rnd32_does_not_wrap` exercise the maximum-normal product
with both 40-bit and `RND32` destinations. They pass in both the independent
arbitrary-width oracle and the MAME seam harness.

The reduced `von` MAME target also rebuilds successfully with the widened seam.
This is an integration/compile check only: the live SHARC register union still
uses the existing 32-bit execution path until the interpreter and DRC migration
described below is completed. The build-preparation script recognizes the
already-present, locally evolved 40-bit header and register patches so repeated
builds do not mistake those dirty-tree changes for unapplied patches.

The same exception policy was applied to the DRC compound `FMUL + ABS`
instruction at multi-operation selector `0x1d`. Its NaN operand now produces
the interpreter's canonical NaN, sets `AI` and sticky `AIS`, and leaves `AS`
clear; ordinary zero and denormal handling remains the existing signed-zero
path. The neutral source patch is
`third_party/patches/0033-von-sharc-drc-compound-abs-special-cases.patch` and
its contract is checked by `von/tools/test_sharc_drc_abs_special_cases.py`.
This patch and the scalar DRC special-case patch remain preserved candidates;
they are not part of the active `sharc-precision` profile because they do not
apply independently to the pinned core tree. The active profile contains only
the clean 40-bit header and register-seam patches.

## New runtime boundary from the twin capture

The rebuilt local MAME subtarget now has an explicit `VON_SHARC_DRC=1` switch,
and an escalated two-cabinet `vonj` run reached the live linked scene through
the DRC. Both cabinets established the M2COMM link and produced the same
geometry state snapshot at frame 2070:

* mode `0x00000007`, byte-map pointer `0x02fc0d50`, records pointer
  `0x02bef690`, and auxiliary pointer `0x02bf039c`;
* special mask `0x000000a0`; general mask initially `0x000002a8`, later
  changing through `0x000003a4`, `0x000001a4`, `0x000000a0`, and other values;
* the first 32 byte-map entries are all `0x80`, so the callback gate's map-bit-5
  path is bypassed in this scene;
* sampled runtime records for selectors 0, 6, and 13 are respectively
  `00000000 00000000 3f800000 00000000 c8435000`,
  `00000000 00000000 3f800000 00000000 c1900000`, and
  `00000000 00000000 3f800000 00000000 00000000`.

The same logged run produced 1,097 complete projection response triplets on
P1 and 1,096 on P2 before the capture tails (the remaining logged responses
were an incomplete final sequence). The triplet starts at i960 PC `0x6f7ac`,
reads the middle response at `0x6f7b4`, and finishes at `0x6f818`; every
complete triplet in this live scene was `[0, 13, 0]`. This confirms that the
recovered projection packet is active in a linked DRC run, while the pointer
values and raw record words remain state snapshots rather than stable semantic
names. It is a separate scene from the interpreter geometry-select trace,
where the middle response also exercises 0 and 6, so this is not yet a numeric
parity test of the two execution paths.

## Regression boundary

The Virtual-On fixture is the first regression layer:

```sh
python3 von/tools/verify_sharc_trig_quadrants.py /tmp/von-sharc-trig-quadrants.trace
python3 von/tools/verify_sharc_trig_quadrants.py /tmp/von-sharc-trig-quadrants-nodrc.trace
```

Both traces currently pass the same sixteen words. The recovered opcode-0x35
model also now matches its live `0x4306a2f7` vector after preserving the ROM's
per-instruction quotient/residual rounding schedule. A MAME change must retain
these results. The next layer should be a synthetic SHARC CPU test containing:

1. a 40-bit operand whose low eight mantissa bits are nonzero, with `RND32`
   clear, followed by `FADD` and `FMUL`;
2. the same operation with `RND32` set, proving input low-bit clearing and
   32-bit output rounding;
3. `FLOAT` under both modes, proving that its conversion boundary remains
   40-bit; and
4. truncation and round-to-nearest cases near a halfway boundary.

The newer `0x20d68` fixture adds ROM-derived branch boundaries: the exact
`2-sqrt(3)` threshold, finite ratios, and the 124-step `LOGB` guard. Its
verifiers live under `von/tools/verify_sharc_20d68_*.py`. These captures come
from MAME's interpreter because the local `vonj` diagnostic configuration
deliberately disables the SHARC DRC to expose instruction-level state; they
are therefore compatibility oracles, not interpreter/DRC parity tests.

The helper listing also supplies an emulator-facing algebraic fixture:
`0x20d9a` starts the `z = r²` path, `0x20d9b..0x20da0` stage the rational
correction numerator and denominator, and `0x20da1..0x20da8` perform the
reciprocal refinement. A future MAME test can assert those intermediate
register words as well as the final angle. This keeps the eventual upstream
change focused on generic SHARC arithmetic and pipeline timing rather than
embedding Virtual-On-specific code in the CPU core.

The current candidate model now matches the captured finite words through both
direct and `r > 1` reciprocal paths, including `1:1`, `2:1`, and `4:1`. It
also matches the normal finite `LOGB` guard at both sides of the captured
123/124-step boundary. The remaining precision work is confined to
exceptional values and proving that the C operation schedule agrees beyond the
captured finite fixtures. The eight-vector non-normal capture now establishes
that MAME's current interpreter caller path canonicalizes NaNs, saturates
infinities, and flushes subnormals before this helper. Those are compatibility fixtures, not
proof that generic MAME 40-bit arithmetic is complete; direct infinity input
and exact status-flag behavior still need separate evidence.

The direct opcode-`0x0f` probe was separately checked through the opt-in DRC
with `probe_sharc_opcode_0f_poll.lua`. The ordinary per-instruction output
diagnostic does not see DRC-generated memory writes, but polling the host FIFO
does: the seven-vector packet sequence returned
`0x00000000, 0x00003fff, 0x00001fff, 0xffffc000, 0x00007fff, 0xffffe000,
0x00000000` in both the DRC and interpreter runs. The checked-in verifier is
`von/tools/verify_sharc_opcode_0f_poll.py`. This closes that diagnostic blind
spot and confirms that the DRC can execute the shared reduction path and
publish its results; it is not evidence that the two engines are fully
bit-exact for all 40-bit or exceptional cases. The polling stimulus is
retained as a reusable engine-boundary probe.

The corresponding eight-vector nonfinite FIFO capture initially exposed a DRC
gap. The interpreter returned canonical NaN for all NaN cases, while the old DRC returned
`0x00003fff` for NaN in the first argument and zero for NaN in the second; the
infinity, subnormal-flush, and signed-infinity results agreed. Static source
inspection pointed at the generic boundary: `compute.hxx` explicitly
classifies/canonicalizes NaNs, whereas the old DRC's `UML_FSCOPYI`/`UML_FSADD`/
`UML_FSSUB` lowering had no corresponding explicit canonicalization.

A focused experiment then canonicalized NaN inputs and results around the DRC's
scalar `FADD`, `FSUB`, and `FAVG` lowering. The eight direct FIFO results did not
change, so those three scalar boundaries are not sufficient to explain this
caller-level divergence. The remaining candidates are the helper's generated
`RECIPS`/comparison path or a DRC/interpreter difference at the call boundary;
the experiment was removed rather than retained as an unvalidated fix.

The next bounded diagnostic, retained as
`third_party/patches/0027-von-sharc-drc-angle-tracing.patch`, runs after the
generated instructions at the two caller `FSUB` PCs and throughout `0x20d68`.
It shows the DRC entering `0x20d68` with raw `0x7fc00000` for the NaN operand,
while the interpreter enters with canonical `0xffffffff`; the finite operand
and all subsequent finite cases are unchanged. This moves the suspected fault
to the fused compute/memory lowering or its register-writeback policy, before
the helper's `RECIPS` path. The trace is bounded to 512 records and is debug
patch instrumentation only.

That isolation led to a neutral candidate fix in
`third_party/patches/0028-von-sharc-drc-float-special-cases.patch`: it
canonicalizes scalar `FSUB` NaN writeback, implements the interpreter's zero,
infinity, and NaN cases for `LOGB`, and raises sticky `STKY.AIS` alongside
`ASTAT.AI` for invalid results. With DRC enabled, the eight-vector direct-FIFO
sequence now matches the interpreter exactly; the finite seven-vector
sequence still matches as well. The returned-word parity is runtime-verified
by `von/tools/verify_sharc_opcode_0f_nonfinite_poll.py`; the sticky-flag writes
are currently source-verified and need a dedicated state-register probe before
this is treated as a complete upstream fix.
It remains evidence for a future rebased precision change, not an active build
patch.

The state-register probe is available through the same Lua FIFO harness.
Registering `SHARC_STKY` with MAME's state table made it readable from Lua.
A clean eight-vector rerun reports identical `ASTAT` and `STKY` words for the
interpreter and DRC on every vector, including the common `STKY.AIS` invariant.
`verify_sharc_opcode_0f_state.py` accepts a comparison log and checks the
complete ordered state samples, closing the previously observed flag-parity
gap for this caller path. This remains a targeted opcode-0x0f fixture, not
proof of all SHARC instructions' flag behavior.

Only after those synthetic cases are available should the core representation
be changed. The existing Virtual-On trace is a compatibility oracle, not by
itself proof of the complete SHARC numeric implementation.

## Upstream contribution boundary

The local MAME checkout currently has no SHARC-specific unit-test directory or
fixture harness. The practical first contribution should therefore include a
small, self-contained CPU-level test rather than attempting to encode the
Virtual-On trace in the driver. The test needs to exercise both execution
paths: interpreter arithmetic is implemented in `compute.hxx`, while the DRC
emits its own arithmetic in `sharcdrc.cpp`.

The proposed patch order is:

1. Introduce a 40-bit SHARC register representation and conversion helpers,
   with explicit round-to-nearest/truncate and `RND32` boundaries.
2. Convert the interpreter arithmetic helpers, preserving the existing
   exception and ASTAT behavior where the manual defines it.
3. Make the DRC use the same semantic helpers or an equivalent lowered model.
4. Add synthetic arithmetic fixtures before enabling the change for a game.
5. Re-run the Virtual-On compatibility fixtures, including the `0x20d68`
   intermediate trace and non-normal caller capture.

The current Virtual-On-specific edits under `third_party/mame-master` are
diagnostic instrumentation only and are deliberately not presented as an
upstream patch. This keeps the eventual MAME change reviewable: the game
provides difficult real-world oracles, while the generic tests demonstrate
that the proposed behavior is architectural rather than a ROM-specific hack.

The first architecture-level vector contract is now checked into
`von/i960/sharc_precision_fixtures.json` and validated by
`von/tools/test_sharc_precision_fixtures.py`. It uses the manual's raw layout
(sign bit 39, exponent bits 38..31, fraction bits 30..0) and covers the
minimal discriminating cases: an extended low bit surviving `FADD`/`FMUL`,
that bit being removed by `RND32`, and `FLOAT 3` retaining the 40-bit
conversion boundary. These vectors are a specification seed for a future
MAME CPU test; they are not yet interpreter/DRC pass results.

The fixture test now evaluates those cases through the independent exact
rational model in `von/i960/sharc_extended_reference.py`. That model applies
the input boundary, significand precision, and output boundary separately,
so it can serve as the expected-value generator when a MAME-level 40-bit
probe becomes available. It intentionally covers only normal and zero values
for now, including nearest-even halfway cases and truncation; exceptional
behavior remains represented by the live Virtual On compatibility probes.

The same fixture is now executed by the standalone C++ oracle in
`von/tools/sharc_40bit_reference.cpp`, via
`von/tools/test_sharc_40bit_reference.py`. It uses arbitrary-width integer
intermediates and the raw 40-bit encoding, so the halfway cases are checked by
two independent implementations before the MAME register representation is
changed. This is an execution oracle and test seam, not a claim that MAME's
interpreter or DRC already preserves the extended bits.

The seam is now exposed from the core's `sharc.h` as the named
`SHARC_REG_EXTENDED` type, without changing the size or layout of the live
`SHARC_REG` union. The x64 MAME subtarget rebuild and a direct syntax compile
of `src/devices/cpu/sharc/sharc.cpp` both accept that dependency. The static
MAME seam test checks this exposure in addition to the arithmetic vectors.

The first live ABI boundary is now explicit as well: DRC symbol registration,
the DRC register map, and both fast-register synchronization directions point
at `SHARC_REG.r` rather than the containing object. This is behaviorally
unchanged with the current union, but prevents a future extended field from
being accidentally exposed as a 32-bit UML register.
The alternate-register DRC swap blocks likewise use per-register `.r` moves;
the previous `SWAPDQ` object-range optimization was removed because it assumes
that adjacent register objects are adjacent 32-bit words.

Save-state registration also now saves each `.r` field individually instead of
treating `r[16]` as a contiguous `int32` array. This preserves the public
low-word state view when the containing register object grows.

The first MAME-side seam is now present in
`src/devices/cpu/sharc/sharcfloat40.h`. It implements the normal/zero subset
of `FADD`, `FMUL`, `FLOAT`, input rounding, and output rounding without changing
the existing `SHARC_REG` ABI. `von/tools/test_mame_sharc_float40.py` compiles
that header as a small MAME-style harness against the same ten vectors; this
keeps the exact behavior in the MAME tree while the register-file conversion
is developed separately. It is intentionally not wired into the interpreter
yet: the current register union and DRC register map still discard the upper
eight mantissa bits, so enabling only one execution path would create a false
partial fix.

The register audit makes that boundary concrete. `sharc_internal_state` stores
the register file as `SHARC_REG r[16]`; save-state registration and debugger
state exposure currently address `.r`, while `sharc.cpp` gives the DRC direct
pointers to each register object. A safe conversion therefore needs one
coordinated change to the register storage, save-state fields, debugger view,
interpreter accessors, and DRC register lowering. Adding an untracked shadow
field or changing just `FADD`/`FMUL` would leave loads, integer aliases, and
compiled blocks reading different values. The standalone seam is intentionally
the first tested component of that larger conversion.

The concrete migration invariant is: every register read must select either
the complete extended value for a floating operation, the storage low 32-bit
word for an integer operation, or the IEEE-32 projection for a 32-bit float
operation, and every write must update both views. The DRC symbol map and
integer-register synchronization loops now explicitly use `r[i].r`, so they
retain a narrow low-word ABI while the containing register representation is
being expanded. The first integration test should exercise one
extended-bit-producing sequence through interpreter and DRC, then read it via
both a floating operation and an integer move; matching only the final float
result is insufficient.

The MAME seam names these projections explicitly: `storage_low_word()` returns
bits 31..0 of the 40-bit encoding, while `ieee32_word()` returns the extended
value shifted through the 32-bit float boundary. For example, raw
`0x3f80000001` exposes storage word `0x80000001` but IEEE word `0x3f800000`.

## Current execution limitation

An attempted comparison build temporarily enabled the existing MAME `-drc`
path for `vonj`. The SHARC source compiled, but the local `mamevon` link
initially failed before producing a runnable binary, with unresolved symbols
spanning the Model 2 devices, FIFO support, and DRC UML backend. This was a
build-state limitation, not evidence of an interpreter/DRC numeric mismatch.

That link issue was resolved in the repository's focused `mame-von.lua`
definition by declaring the transitive Model 2 devices and buses used by the
included source files. With the temporary `vonj` DRC guard disabled, the
subtarget then built successfully. The same eight-vector non-normal probe was
run through that DRC binary: the runtime verifier passed, and the extracted
`20d68`, helper, result, and output trace sections matched the interpreter
trace exactly (312 helper-state lines, 8 result lines, and 8 output lines).
The normal `vonj` binary was rebuilt afterward with its interpreter guard
restored. This is the first direct interpreter/DRC parity result in the
project, though it covers the caller's 32-bit/non-normal boundary rather than
the unimplemented generic 40-bit arithmetic fixture above.

The DRC path is now opt-in through `VON_SHARC_DRC=1`; the default remains the
interpreter for diagnostic runs. Because MAME's CPU policy also requires the
global `-drc` option, a valid DRC comparison invocation must provide both
`VON_SHARC_DRC=1` and `-drc`; setting the environment variable alone silently
leaves the SHARC in interpreter mode. The same rebuilt binaries were then run with the existing signed-angle
quadrant probe. Both passed the sixteen-word regression verifier, and the
filtered rational/reduction/output logs matched exactly across 520 lines.
Together, these two probes show interpreter/DRC parity for the recovered
finite trig path and its exceptional caller boundary; they still do not test
an operand whose eight extended mantissa bits are nonzero.

The new post-dispatch boundary trace in
`third_party/patches/0030-von-sharc-interpreter-angle-boundary-tracing.patch`
clarifies the remaining flag discrepancy. The interpreter reports `ASTAT`
directly after each instruction, while the DRC trace reports the same logical
flags in its lazy `astat_drc` storage and leaves the ordinary `astat` field
stale until synchronization. This is useful evidence for an upstream MAME
fix: any generic SHARC state/debugger read must export the DRC flag shadow at
the same architectural boundaries, rather than treating the raw `astat`
member as authoritative during a generated block.
