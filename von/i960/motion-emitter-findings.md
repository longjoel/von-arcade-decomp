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

## 1b. Emitter -> part-OBA mapping (`KNOWN`)

Extended trace `0049` logs every copro-FIFO write. Correlating those packets
with the geometry object submission order shows that **the emitters emit parts
in the model's submission order**, and that the emitter at i960 `0x8d488`
carries the part's **OBA in `r6`** (a value in `0x0080_0000..0x00b0_0000`, not
a pointer). Its 12 tagged OBAs are the 6 animated Temjin limbs
(`009e55bf/5590/563e/54ec/54bd/556b`) plus 6 from the other mech. The body
emitters (`0x8d714`/`0x8e164`) do not tag OBA; their `r6` is a source-record
pointer and the part order matches the geometry order by elimination.

`von/tools/map_emitter_obas.py` extracts the tagged mapping from a trace.

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

## 6. What this unlocks

- **Per-part animation from ROM data**, provenance-gated: the motion tables are
  a first-class decodable asset, sibling to the model part tables.
- **Clip inventory and annotation**: every clip is `(fighter, offset, frames,
  parts, raw records)`, stable IDs, so clips can be labelled and later bound to
  kernel state.
- **A ground-truth tap**: the emitter `r6`/`g2` labels make it a reference for
  validating any later decode, and the SHARC probe turns the DSP into a callable
  transform function.
