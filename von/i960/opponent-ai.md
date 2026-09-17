# Opponent (CPU) AI annotations

> Address-level notes for the Virtual-On opponent logic, recovered from
> `von/build/disasm/vonj-maincpu.lst`. Confidence tags: `KNOWN` when an
> instruction mapping is direct, `LIKELY` when the role is inferred from the
> surrounding state machine.

The opponent is not a separate program: it is the fighter object at
`0x005040d0` (player `0x00503ad0`), each pointing at the other through
`+0x74`. The AI reuses the same per-fighter state machine as the player and
adds a small perception→class→command pipeline. It never reads raw controller
input; it reads the opponent's *mech index* (`+0x64`) and *action state*
(`+0x172`).

## Evidence status

Structural facts (table indices, control flow, store sites) are
instruction-derived and are not guesses. Semantic names are hypotheses, and
they are not equal:

- **Runtime-validated**: the bearing-sector classifier (§1: recomputed from
  object positions/facing, matches the logged sector in 93.9% of 2300 frames);
  the packed command word and commit gate (§7, matches the consumer decode);
  the transition table `3*group+pattern` (§8, read directly from every
  handler); the hand-move dispatch (§10, corroborated by the
  `"HAND_MOVE ID ERROR"` string at `0xbd710`).
- **Instruction-grounded, not runtime-validated**: the 8-direction code table
  (§7), `+0x64` as the roster index (§4), the event triggers (§9).
- **Inferred labels (not proven)**: "side-step" for `0xa98f0`; "mech matchup"
  for `0x7a3e0`; the per-mech reading of the `0x79050` arms. These are the
  weakest claims in this note and should be tested before being relied on.

A label that has not survived a falsification attempt is marked `LIKELY` or
`SPECULATIVE` in place; the `KNOWN` tags on sections above refer to the
structural chain, not to the semantic name.

## 1. Perception — bearing to the opponent (`0x76590`, `KNOWN` shape)

`0x76590` (geometry object band pair) is the "where is he" step:

1. `0x765a0`-`0x765d8`: SHARC `0x884000` service `0xFFFF` with own/other
   `+0x08`/`+0x10` (x/z); the response is stored to `0x504d60`.
2. `0x76600`-`0x7661c`: SHARC service `10` with `(other - self)`; response `g0`.
3. `0x76624`-`0x7662c`: `g0 -= self+0x184` (own facing) -> relative bearing,
   stored at `0x504d64`.
4. `0x76634` `bal 0x73508`: classify the bearing into a sector.

`0x73508` is a signed sector map (i960 angle units: `0x10000` = 360°). Index
in `g0 = (s16)bearing`:

| sector | range | bound used |
| ---: | --- | --- |
| 0 | 0°..5° | `< 0x38D` |
| 1 | 5°..30° | `< 0x1554` |
| 2 | 30°..90° | `< 0x3FFF` |
| 3 | 90°..135° | `< 0x5FFF` |
| 4 | 135°..180° | else |
| 5 | -180°..-135° | `>= -0x6000` |
| 6 | -135°..-90° | `>= -0x4000` |
| 7 | -90°..-30° | `>= -0x1555` |
| 8 | -30°..-5° | `>= -0x38E` |
| 9 | -5°..0° | else |

The sector is stored at `0x504d68` (`0x76638`). Note `0x504d60` is a SHARC
geometry response, not a wall-clock timer, even though the state machine uses
it as a threshold.

**Validated (observed):** recomputing the sector from the two objects'
positions and facing over the 2300-frame attract capture matches the logged
`0x504d68` in **93.9%** of frames using object A and the convention
`bearing = atan2(-(x_other - x_self), z_other - z_self) - facing`. The
remaining frames are consistent with the global being last-writer for whichever
object ran the classifier most recently. This confirms the "relative bearing ->
sector" semantics rather than only the address chain.

## 2. Class dispatch (`0x735f0`, `KNOWN`)

`0x735f0` loads the current behavior class from `0x504d94`, rejects `> 33`
(takes `0x74848`), and jumps through the `0x73618` table:

| class | handler | class | handler |
| ---: | ---: | ---: | ---: |
| 0 | `0x74848` | 17 | `0x74110` |
| 1 | `0x736a0` | 18 | `0x7411c` |
| 2 | `0x737c8` | 19 | `0x74138` |
| 3 | `0x73900` | 20 | `0x7415c` |
| 4 | `0x73a34` | 21 | `0x74178` |
| 5 | `0x73b68` | 22 | `0x74194` |
| 6 | `0x73c98` | 23 | `0x745bc` |
| 7 | `0x73dcc` | 24/25 | `0x74848` |
| 8 | `0x74148` | 26 | `0x745e4` |
| 9 | `0x744ec` | 27 | `0x7460c` |
| 10 | `0x73fdc` | 28 | `0x74634` |
| 11 | `0x73ffc` | 29 | `0x74674` |
| 12 | `0x7402c` | 30 | `0x746f4` |
| 13 | `0x7408c` | 31 | `0x74754` |
| 14 | `0x740ec` | 32 | `0x7479c` |
| 15 | `0x740f8` | 33 | `0x747e4` |
| 16 | `0x74104` | | |

Every handler writes the fighter command word at **`object+0x108`** through
`r6 = object+0xec` (`stos rX,0x1c(r6)`, set once at `0x73604`). This is the
same command the input consumer produces for a human, so the AI injects a
synthesised input rather than bypassing the state machine.

### Class semantics (`LIKELY`)

| class | output | role |
| ---: | --- | --- |
| 1 | service 29 with facing + 0 | move forward |
| 2 | service 29 with facing + `0x2000` (+45°) | veer right |
| 3 | service 29 with facing - `0x2000` (-45°) | veer left |
| 4 | service 29 with facing - `0x8000` (180°) | move backward |
| 5 | service 29 with facing + 0 | forward (alt speed) |
| 6 | service 29 with facing - `0x4000` (-90°) | side-step |
| 7 | distance/state gate, then command | approach/retreat |
| 8 | `0` / `0x707` / `0x303` / `0x505` by class | neutral or move |
| 9 | `0x404`, own/other class + `+0x184` compare | turn/aim |
| 10 | `0x72b40[sector]` = `0x0202` | hold direction 2 |
| 11 | `0x72b60[sector]` = `0x0606` | hold direction 6 |
| 12 | `0x400`; if sector < 3 -> class 26 | attack/steer |
| 13 | `4`; if sector < 3 -> class 27 | attack/steer |
| 14 | `0x400` (setbit 8) | guard/block |
| 15 | `7` | move |
| 16 | `0x405` | move |
| 17 | `0x304` | move |
| 18 | `0x101`, or `0` when own class is 3/8 | move |
| 19 | `0x707` | move |
| 20 | `0x303`, or `0` when own class is 3/8 | move |
| 21 | `0x505`, or `0` when own class is 3/8 | move |
| 22 | `0x602` when own state `+0x172` is 11, else table `0x741d8` | state branch |
| 23 | `0x400` (setbit 10) + class 12 when sector >= 3 | attack/steer |
| 26 | `0x400` + class 12 when sector >= 3 | attack/steer |
| 27 | `4` + class 13 when sector >= 3 | attack/steer |
| 28 | `0x206` | attack variant |
| 29 | command per `+0x170`; `0xffff` + reset `0x504db4 = 1` on 0/4/5/6 | attack/timeout |
| 30 | `0xffff` + reset `0x504db4 = 1` when state `+0x172` not in 0/4/5 | timeout |
| 31 | `0x404` | attack variant |
| 32 | `0x202` | attack variant |
| 33 | `0x606` | attack variant |
| 0/24/25 | `0xffff` (invalid/no-op) | idle |

The command word is two nibble lanes; `0x0202`/`0x0606` set both lanes to
direction 2/6, and `0x101`..`0x707` are the paired movement levels. Classes 10
and 11 are the only sector-table lookups (`0x72b40`/`0x72b60`, both uniform
across sectors), so the class table above is the real decision content.

The service-29 calls are the SHARC trig/velocity service (see
`von_movement.h`), so classes 1-6 are facing-relative movement primitives.

## 3. Sector -> class tables (`KNOWN` contents)

The action-5/action-10 wrappers select a table and index it by the sector
(`0x504d68`); the value is written to `0x504d94` (the next class):

| wrapper | table | values by sector 0..9 |
| --- | ---: | --- |
| `0x783c8` (action 5) | `0x72690` | `8, 0x12, C, C, C, D, D, D, 0x13, 8` |
| `0x78408` (action 10) | `0x72750` | `9, 0x10, C, C, C, D, D, D, 0x11, 9` |
| `0x78448` (action 10) | `0x72990` | `A, A, C, C, C, D, D, D, A, A` |
| `0x78488` (action 10) | `0x729f0` | `B, B, C, C, C, D, D, D, B, B` |
| `0x78a58` (0x78a30) | `0x72a20` | `0x12, C, C, C, C, D, 0x13, 0x13, 8, 0x12` |
| `0x78830` (0x78818) | `0x72690` | action-5 table (mode-gated) |
| `0x78be8` (0x78bd8) | `0x72690` | action-5 table (mode-gated) |

`A/B/C/D` = classes 10/11/12/13. Classes `C`/`D` (12/13, the weapon/action
variants of `state-semantics.md`) cover the front and side sectors; only the
near-ahead (0/1) and near-behind (8/9) sectors get the specialised entries.

## 4. Feedback and randomness

- `0x504d94` is written by the action wrappers above, by the match-phase
  selectors (`0x752xx`, `0x753xx`), and by the class handlers (`0x736xx`), then
  read back by the state machine (`recovered_object_state_runtime`) and by
  `0x735f0` itself.
- The state machine also consumes a random role from `0x79664`
  (`recovered_object_state_random_selector`): `[1,1,2,2,3,3,5,6]` indexed by
  `random & 7`, so identical situations can select different transitions.
- `0x7a3e0` (route head) compares own `+0x64` against the opponent's `+0x64`
  and routes to mode 11 / ratio paths before the class selection.

### `object+0x64` is the mech/roster index (`KNOWN`)

`+0x64` is not a behaviour state; it is the fighter's roster index. The
object initializer `0x27550` stores its `g3` argument there
(`0x2756c st g3,0x64(g0)`), and the startup arm at `0x19d44`-`0x19dcc` passes
`0x503a98` (player) and `0x503a9c` (CPU) and derives the config from
`0x19360[index]`, the 10-entry roster profile table. The match reset clears it
to 0 (`0xce75c`/`0xce764`). In the attract capture the player field stayed `0`
and the CPU field was `5` for one match segment -- a constant per object
lifetime, i.e. the mech identity.

Consequences: `recovered_object_state_runtime`'s `state`/`related_state`
context fields are this mech index, so the `0x79050` arms are **per-mech
behaviour**, and the `0x7a3e0` comparison is a mech-matchup dispatch (own
roster index vs the opponent's). The recovered "state 0..9" naming should be
read as "kind/mech 0..9".

## 5. Summary

The opponent is a **10-sector reactive classifier**:

```
opponent position -> SHARC -> bearing -> 10 sectors (0x73508)
sector + situation -> table (0x72690/... ) -> class (0x504d94)
class -> handler (0x73618) -> command word at object+0x108
                       (movement via SHARC service 29, or canned attack)
```

No pathing, prediction, or input reading; 10-way spatial resolution with two
dominant attack classes and a random role. This is consistent with the
observed weak but "reactive" behaviour.

## 6. Runtime validation (`observed:von-ai-state.log`)

`von/tools/probe_ai_state.lua` samples the AI globals and both objects each
frame during the input-free attract (`VON_AI_LOG`, `VON_AI_SECONDS`). In a
40-second run (2300 frames):

- sectors seen: `0` (1360), `1`, `2`, `7`, `8`, `9` — the fighters face each
  other, so the classifier lives near the 0/9 boundary and steps through
  adjacent sectors; adjacent-sector transitions dominate.
- classes seen: `0` (idle, 1221), then `18`, `8`, `6`, `10`, `2`, `11`, `13`,
  `5`, `1`, `12`, `19` — all within the decoded 0-33 range.
- commands written to `object+0x108`: `0000` (idle), `0101`, `0202`, `0404`,
  `0606`, `0707` (paired nibble lanes), `0004`/`0400` (single lane), `0206`,
  and `ffff` — matching the packed command format the handlers emit.

Caveat: `0x504d94`/`0x504d68` are shared and last-writer, so the per-frame
pairing in the log is approximate; a per-object tap would tighten the
class -> command mapping.

## 7. Command-word encoding (`KNOWN` shape)

The consumer head (`0x25040`-`0x2515c`) decodes `object+0x108` as two packed
direction lanes:

```
command = (nibble[(ma >> 12) & 0xf] << 8) | nibble[(ma >> 20) & 0xf]
```

where `nibble[]` is the 16-entry table at `0x3d70`/`0x3da0`
(`[0xff,4,0,0xff,6,5,7,0xff,2,3,1,0xff,...]`). The high byte is the
translation lane and the low byte the twist lane, each a 0-7 direction code.
That is why the AI's handlers write paired values (`0x0101`..`0x0707`) or
single-lane values (`0x0004`, `0x0400`).

The commit gate (`0x268c4`-`0x26968`) latches the decode into `object+0x137`
only when the held/repeat counters pass a threshold (`in[0x56]`/`in[0x57] >
0xEE`, gate A, or `> 0xF5`, gate B) and only in states 15/16/31 (gate B) -- so
an AI command must persist long enough to be accepted.

The `0x3d70`/`0x3da0` table is an **8-direction compass map**. The nibble is
the stick direction bits `(ma >> 4) & 0xf` (`0x10` down, `0x20` up, `0x40`
right, `0x80` left, per the twin-stick map), and the table output is:

| stick | nibble | code | direction |
| --- | ---: | ---: | --- |
| up | 2 | 0 | up |
| up+left | 10 | 1 | up-left |
| left | 8 | 2 | left |
| down+left | 9 | 3 | down-left |
| down | 1 | 4 | down |
| down+right | 5 | 5 | down-right |
| right | 4 | 6 | right |
| up+right | 6 | 7 | up-right |

So an AI command word `0xNNNN` sets the translation lane and the twist lane to
the same compass bearing `NN`; single-lane values (`0x0004`, `0x0400`) set one
lane to `0` and the other to a bearing. The service-29 handlers still compute
the actual velocity via the SHARC, so the command word selects the animation
bearing.

## 8. Transition -> movement command (`KNOWN` shape)

The state machine's transition (`0x504d98`) is consumed at `0x74964`-`0x74978`,
which indexes a 24-entry table at `0x7497c` (transition -> handler). The
handlers are small and set `g5`/`g6` before the common tail:

- default (`0`, `22`, `23`) -> `g5 = g6 = 1` (`0x74D20`).
- `7`/`8`/`9` (`0x74B20`/`0x74B30`/`0x74B44`): taken only while the action
  counter `0x504db4 < 4`; otherwise default. `7` -> `g5=2,g6=1`;
  `8` -> `g5=1,g6=2`; `9` -> `g5=2,g6=2`.
- `10`/`11`/`12` (`0x74C24`/`0x74C38`/`0x74C50`): taken only while the clip
  cursor `+0x17a > 7`; otherwise default. `10` -> `g5=2,g6=1`;
  `11` -> `g5=1,g6=2`; `12` -> `g5=2,g6=2`.
- `1`-`6` and `13`-`21` have their own `+0x172`/`+0x170`/counter gates.

The common tail `0x74D28`-`0x74E50` computes the **movement bytes**:

```
74da4: cmpi g6,2 ; g6 = current MA (0x504dac)
74db0: g4 = 0
74db4..74dd0: g4 = 4/2/1 from g6/MA bit0
74dd4..74dec: g0 = 1, or 2/4 from g5 and bit0 of current MA
74df0..74e34: setbit 3/4/5 of g4/g0 per r8/r9 (16 or 8)
74e10: st g4,0x504dac     ; MA
74e48: st g0,0x504db0     ; MB
```

So the transition id selects the CPU's stick command: `g5`/`g6` pick the
forward/back/strafe pattern and `r8`/`r9` (16 or 8) pick the direction bits,
which are written to the same `0x504dac`/`0x504db0` cells the local controller
feeds. This closes the AI loop: perception -> class -> transition -> movement
input.

Runtime sample (extended `probe_ai_state.lua`): transitions `0/1/2/7/13`, with
mostly `7`, and MA/MB pairs like `(7, 0x09, 0x0c)`, `(7, 0x11, 0x14)`,
`(7, 0x21, 0x24)`. The `0x08`/`0x10`/`0x20` bits vary because the tail also
reads the class (`0x504d94`) and counter (`0x504db4`), so the transition alone
does not fix the movement bytes.

### The transition table (`KNOWN`)

Every handler ends in one of four `(g5,g6)` selections, and they follow
`transition mod 3`:

| transition mod 3 | `(g5,g6)` | tail pattern |
| ---: | --- | --- |
| 1 | `(2,1)` | `g4 = 1`, `g0` from MA bit0 |
| 2 | `(1,2)` | `g4` from MA bit0, `g0 = 1` |
| 0 | `(2,2)` | both from MA bit0 |
| (special) | `(1,1)` | default, transitions `0`/`20`/`21`/`22`/`23` |

The quotient (`transition / 3`) selects the gate:

| group | transitions | gate |
| --- | --- | --- |
| 1-3 | 1,2,3 | own kind `+0x64`, own `+0x170`/`+0x172`, opponent kind |
| 4-6 | 4,5,6 | `counter >= 0` (always true -> default) |
| 7-9 | 7,8,9 | `counter < 4` |
| 10-12 | 10,11,12 | clip cursor `+0x17a > 7` |
| 13-15 | 13,14,15 | own `+0x172` state bands |
| 16-18 | 16,17,18 | `counter < 1` |
| 19 | 19 | `counter % 10 < 4` |
| 20-21 | 20,21 | own `+0x170` in {0,2}/{0,3}, then counter |

So the state machine's transition id is a compact `(gate, movement pattern)`
pair: `id = 3*group + pattern`. That is the whole opponent decision surface.

## 9. Animation-cursor events (`KNOWN` shape)

Three per-object handlers fire at specific animation-cursor values (`+0x17a`)
and are selected by the `0xbf180`/`0xbf1c0`/`0xbf200` dispatchers. Those pass
`g0 = object`, `g1 = object+0x200`, `g2 = context` (`0x565320` player /
`0x5658a0` CPU); the handlers claim a slot in an **object hand-move range** and
read a context field:

| trigger (caller) | handler | object range | scan | context field |
| --- | ---: | --- | ---: | ---: |
| `+0x17a == 0x46` (`0x42538`) | `0xa1050` | `object+0x240` (rec 2) | 4 | `+0x58` |
| `+0x17a == 0x5f` (`0x42864`) | `0xa98f0` | `object+0x380` (rec 12) | 8 | `+0x210` |
| `(+0x17a & 7) == 0` and `<= 0x26` (`0x4328c`) | `0xa55e0` | `object+0x2C0` (rec 6) | 8 | `+0x108` |

`0xbf0c0`/`0xbf120` scan the range for a free record (flags byte); the handler
then writes the flags/id (e.g. `0xa1050` writes flags `7`, id `8`).

`0xa98f0` is the aim/step event: it emits SHARC service 29 with
`facing + 0x4000` (or `+0x1000`) and a float (`8.0`/`16.0`), service 30 with
the same inputs, then service 31 with the opponent's position
(`related+0x14/0x18/0x1c`) -- a side-step vector derived from the opponent
bearing and distance.

## 10. Hand-move records (`object+0x200`)

The `+0x200` region the event handlers and `0x77c40` touch is a 32-record
hand-move (attack) table, 0x20 bytes each:

- `0xbd6b8` resets all 32 records and, on an invalid id, prints
  `"HAND_MOVE ID ERROR [1P:%2d]"` (string at `0xbd710`).
- `0x77c40` scans both objects' records and aggregates flags into `0x504e50`
  (bits 0/2/3/4/5/6/7), counting records whose id halfword has bit 13.
- `0xbd730` is the per-record dispatcher: `record[0]` is a flags byte
  (0..0xcc valid; `> 0xcc` takes the error path), `record[2]` is the id
  (low 5 bits masked), and `0xbcf40[flags*8]` selects the handler:

| flags | handler | flags | handler |
| ---: | ---: | ---: | ---: |
| `0x00` | `0xbcb90` | `0x49`-`0x4e` | `0xa5b90` |
| `0x01`-`0x05` | `0x9f070` | `0x4f`-`0x54` | `0xaa000` |
| `0x06`, `0x90` | `0x9f1f0` | `0x5b`-`0x5f` | `0xaa4c0` |
| `0x07`-`0x12`, default | `0x9ece0` | `0x61`-`0x66` | `0xaa740` |
| `0x13`-`0x18` | `0xa12e0` | `0xa9`-`0xab`, `0xae` | `0xb2f80` |
| `0x25`-`0x2a` | `0xa38f0` | `0xac`/`0xad` | `0xb3480`/`0xb3990` |
| `0x43`-`0x48` | `0xa3b80` | `0xb5`-`0xba` | `0xb71a0` |
| `0x40` | `0xa5930` | `0xc8`-`0xcb` | `0xbad00`/`0xbbec0`/`0xbb820`/`0xbc570` |

The per-record context lives in the 0x580-byte blocks `0x565320` (player) /
`0x5658a0` (CPU) at `index * 0x2c` (32 records x 0x2c = 0x580, which is the
gap between the two bases). `0xbd730` is called from 15 sites (startup arms,
match phases, and the AI region). The event handlers use the object hand-move
ranges in section 9 and read individual context fields; whether `0xbd730`'s
`index*0x2c` records align with the object's `index*0x20` records is not yet
confirmed.

## Open items

- The `0x504d60` SHARC response's physical meaning (distance, height, or
  projection) is unconfirmed.
- Whether the `0x79050` arms are truly one-per-mech (10 arms, 10 roster
  entries) or a shared generic table indexed by `+0x64` needs a per-mech
  capture.
