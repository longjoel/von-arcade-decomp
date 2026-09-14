# Per-part motion records and the transform emitter

> **Working notebook.** Bounded interpretations, not promoted reconstruction.
> Confidence tags: `KNOWN` (verified against listing/trace), `LIKELY`,
> `SPECULATIVE`. Provenance is `observed:<trace>` for original execution and
> `synthetic:<listing>` for readings of `von/build/disasm/vonj-maincpu.lst`.

This note records how the game stores and emits per-part animation for the
fighters, the tools built to extract it, and the one convention that is still
open. It is the entry point for the motion/rig work used by `von-godot`.

## 1. Motion tables in main_data (`KNOWN` contents)

Each fighter's profile is a blob in the i960 program image reached from the
table at `0x19360` (10 pointers, roster order), name strings at `0x19390`.

- Profile regions hold runs of paired motion-table pointers from `+0x70`.
- A header is two words: `[data_ptr, (frames << 16) | parts]`.
- The record stride is `12 * frame * parts` bytes; each part/frame record is
  six signed 16-bit words. `0x8dd40` reads the frame count from `+0x4`, the
  part count from `+0x6`, strides into `data_ptr`, and emits six `ldos` values
  at record offsets `+0,+2,+4,+6,+8,+10`.

Roughly 200 clips per fighter; an 8-part "skeleton" family is shared by all
fighters, plus a fighter-specific body family (Apharmd 15, Temjin 15, …).

Tool: `von/tools/dump_motion_tables.py` (+ `test_dump_motion_tables.py`). It
reconstructs `maincpu` and `main_data`, scans each profile for valid headers,
and emits per-fighter JSON (base64 raw records). Written to the git-ignored
`von/build/motion-tables/`.

## 1b. Emitter -> part-OBA mapping (`KNOWN`, debugger-confirmed)

Extended trace `0049` logs every copro-FIFO write. At the transform emitters
the i960 holds the part's **OBA**: the body emitter (`0x8e164`) in `g4` (and
`r10`), the option/limb emitter (`0x8d488`) in `r6` (a value in
`0x0080_0000..0x00b0_0000`, not a pointer). The body emitters
(`0x8d714`/`0x8e164`) otherwise carry a source-record pointer in `r6`.

`von/tools/probe_emitter_obas.py` breaks repeatedly at the emitters over MAME's
GDB stub and records `(pc, r6, g2, g4)`, emitting the exact `g2 -> OBA` and
`r6 -> OBA` tables (retained at `von/i960/emitter-g2-oba.json` /
`emitter-r6-oba.json`). The mapping is consistent (no conflicting `g2`).

Exact Temjin body map (dest record -> OBA): `5046d0->009e410d`,
`5046dc->009e35b7`, `5046e8->009e2ea2`, `5046f4->009e30ab`, `504700->009e343a`,
`50470c->009e3588`, `504718->009e3531`, `504724->009e2f5d`, `504730->009e3300`,
`50473c->009e3054`, `504748->009e332f`, `504754->009e2cb1`; the second mech
(base `504930`) is the `00a8xxxx` set. Because a FIFO trace records `g2` for
every packet, each emitted part can now be labelled with its OBA.

The earlier `map_emitter_obas.py` (trace-only) recovers the `r6`-tagged subset
without the debugger.

## 2. Record semantics — six 16-bit words (`KNOWN`)

The emitter packet is a fixed sequence written to the copro FIFO at
`0x884000`:

```
5, 47, a, b, c, 22, d, 21, e, 20, f, 58
```

Decoding the i960 emitter and the SHARC handlers:

- The last three (`f,e,d`) are sent under opcodes **20/21/22** and **rotate the
  12-word matrix** at DM `0x30101` (columns 0–2). By which matrix rows each
  handler mixes: op20 = **X**, op21 = **Y**, op22 = **Z**, pre-multipled in
  send order, so `R = Rx(a0) * Ry(a1) * Rz(a2)`.
- The angle unit is `int16 * 2*pi/65536` (SHARC constant `0x38C9116D` =
  `pi/32768`; `0x3FC90FDB` = `pi/2`). Sin/cos are at `0x20DBE`/`0x20DC4`.
- The first three (`c,b,a`) are sent under opcode **47** and are multiplied by
  the 3x3 part (words 0–8) into the translation words 9–11, i.e.
  `t = R * v`.

So a record is a **local TRS**: `M = [ R(a0,a1,a2) | R·(c,b,a) ]`. This
explains the earlier puzzle that `|v|` was invariant across frames — `R·v`
preserves the bone length.

## 3. Bone markers (`KNOWN` shape, `LIKELY` role)

Model part tables are `[tpa, tha, oba]` triples interrupted by `[0,0,k]`
markers with `k <= 5`. The walker files one pose entry per marker into six RAM
slots at `0x562430 + 3*k`, which the motion code reads. This is a **six-bone
pose system**, not an explicit per-part parent list; the ROM does not store a
flat parent array.

## 4. Emitter tracing (`KNOWN`)

Two i960 emitters write the packet:

| emitter | caller(s) | object class | observed parts |
| --- | --- | --- | --- |
| `0x8dd40` | `0x33e80`, `0x33eb8`, `0x3a9fc` | option / sub-object | 7 |
| `0x8e120` | `0x345ec`, `0x346d4` | mech body | 15 |

Patch `0049-von-emitter-transform-tracing.patch` logs every `0x884000` write
in `[0x8d000,0x8e400)` with `time`, `pc`, `data`, `r6`, `g0`, `g2`. It is in
the `select-sweep` profile and gated by `VON_EMITTER_T0/T1`. The packet is
self-labelling: `r6` is the per-part record pointer (steps 12), `g2` the
object, and a packet starts at `data=5`.

Capture it alongside the geometry trace:

```sh
VON_TRACE_T0=0 VON_TRACE_T1=180 VON_EMITTER_T0=0 VON_EMITTER_T1=180 \
  bash scripts/record-human.sh
```

## 5. Open convention (`SPECULATIVE`)

Records are **absolute local rotations** — an integration test (treating the
angles as deltas and accumulating) scored worse than the absolute hypothesis
(60° vs 33° mean edge residual), so they are not integrator inputs.

Composing the exact emitted `M` against the geometry-board world matrices does
not close: for no `(parent, child)` pair is `inv(W_parent)*W_child ≈ M` below a
~27° floor, with the best axis/transpose conventions. This means the matrix the
geometry parser logs is not related to the SHARC local matrix the way we
assumed (it may carry its own object-level transform or use a different basis).

**Next step (decisive):** calibrate against the SHARC directly. `probe_sharc_transform.lua`
finds the SHARC (`adsp21062(:copro_adsp)`), injects the packet, and reads the
12-word result at `DM(0x30101)`. Feeding one captured packet and reading the
hardware matrix pins the true relationship without any inference. Then the
parent tree follows from `inv(W_parent)*W_child = M_child`.

## 5b. SHARC probe attempt (`probe_sharc_transform.lua`, 2026-09-14)

The decisive hardware calibration was attempted and **does not yet land**:

- With `VON_SHARC_XF_RESET=1` the probe writes an identity 3x4 to `0x30200`
  and points `DM(0x30101)` there in the inject frame; a readback confirms the
  identity is present for that frame.
- A write tap over `0x30200..0x3022c` (`VON_SHARC_XF_TAP=1`) records **only**
  the reset writes (PC `0x20126`); the injected packet produces **no** handler
  writes, even with the recovered batch handshake
  (`0x800010=0x101`, `0x804000..c`) prepended. The live-injection handshake is
  the same unresolved blocker noted elsewhere.

**Cross-checks (2026-09-14).**

1. **The uploaded program is constant.** Hashing the live SHARC program space
   at frames 300/600/900/1800/3600/7200 (boot -> select -> match) gives the
   **same** hash `76efddc5` every time. So opcode semantics are **not**
   context-dependent: there is one program and one dispatch.
2. **The packet structure is confirmed.** A live emitter capture
   (`bin/von -log -oslog`, `VON_EMITTER`) shows a real record at PC `0x8de14`,
   `g2=0x5046d0` (a Temjin body slot):
   `5, 47, 49020, 15664, 18331, 22, 80, 21, 574, 20, 12, 58` — i.e. the
   `47/22/21/20` packet this note describes, not the `2f/16/15/14` geometry
   packet that `sharc_transform.py` models.
3. **Injection still does not land.** Re-injecting that exact packet with the
   identity reset + tap + batch handshake still produces **no** handler writes;
   only the reset writes (PC `0x20dd8`) appear. The FIFO arm/handshake remains
   the blocker.

**Opcode conflict to resolve.** Since the program is fixed, service `22` cannot
be both this note's Z-rotation and the `recovered_sharc_opcode_22.c`
projection/affine service. Either the recovered opcode models are ADSP
*instruction* semantics (from the SHARC CPU core) rather than FIFO *service*
handlers, or the service dispatch table is not indexed the way the note
assumes. Resolving it needs the SHARC program disassembled (its dispatch and
the `20/21/22/47/58` handlers), which is blocked on building MAME `unidasm`
(the local tree has no generated tools project).

Next: build `unidasm` (or otherwise obtain the listing) and decode the upload's
dispatch, and/or land the injection to read the hardware matrix directly.

## 5c. SHARC program disassembled; service dispatch table (`KNOWN`, 2026-09-14)

`unidasm` was built locally (`make -f unidasm.make config=debug64`, after
building `libdasm.a` and the tool deps; the host SDL2 dev symlink is broken, so
the generated link line needed `-l:libSDL2-2.0.so.0`). The uploaded program
(`extract_sharc_bootstrap.py` -> `pack_sharc_program.py`, 3680 48-bit slots)
now disassembles as `von/build/disasm/vonj-sharc-program.lst`
(`unidasm ... -arch sharc -basepc 0x20000`; runtime PM = file index + `0x20000`).

The main FIFO loop at PM `0x2011E`:

```
2011e: IF FLAG0_IN, JUMP 2011e     ; poll
2011f: R0 = DM(I0,M0)              ; read a word
20120: R0 = R0 AND 0xff
20121: R2 = 8
20122: COMP(R0,R2)
20123: IF NE, JUMP 2011e           ; loop until low byte == 8
20124: CALL 201BF                  ; setup
2012b: R0 = DM(I0,M0)
2012c: M7 = R0
2012d: I15 = DM(M7, I2)            ; I2 = 0x00030000  -> service table
2012e: CALL (M8, I15)              ; dispatch
```

So a leading word whose **low byte is `8`** starts a command, the next word is
the **service index**, and `DM(0x30000 + index)` holds the handler PM address.
The table has **20 entries** (`0x00`..`0x13` -> `0x20133`..`0x20cca`); handler 0
(`0x20133`) is `F0 = F0 + F1` (add), i.e. these are arithmetic/math services.
Retained as `von/i960/sharc-service-dispatch.json`.

**Consequence for the animation decode.** The motion packet's numbers
`20/21/22/47/58` are **outside** the 20-entry service table, so they are not
dispatch indices for this table. Combined with the constant program hash
(§5b) and the recovered models, the likely reading is that
`recovered_sharc_opcode_*.c` are MAME **ADSP instruction** semantics (the SHARC
CPU core opcode switch), not FIFO service handlers, and the transform is
composed *inside* one of the 20 service handlers (rotation/subroutine code the
handlers call). §2's "opcode 20/21/22 rotate the matrix" therefore needs
re-checking against the handler bodies, not the instruction models.

## 6. What this unlocks

- **Per-part animation from ROM data**, provenance-gated: the motion tables are
  a first-class decodable asset, sibling to the model part tables.
- **Clip inventory and annotation**: every clip is `(fighter, offset, frames,
  parts, raw records)`, stable IDs, so clips can be labelled and later bound to
  kernel state.
- **A ground-truth tap**: the emitter `r6`/`g2` labels make it a reference for
  validating any later decode, and the SHARC probe turns the DSP into a callable
  transform function.
