# Twin link: the per-frame state sync loop

> Address-level annotations for how two linked cabinets stay in sync.
> Recovered from `von/build/disasm/vonj-maincpu.lst`; the Z80 side is in
> [../docs/cpu3-disassembly.md](../docs/cpu3-disassembly.md). Confidence:
> `KNOWN` where the instruction mapping is direct.

## Model

Each cabinet runs the whole match locally: it owns both fighter objects
(`0x00503ad0`, `0x005040d0`, cross-linked via `+0x74`) and runs the shared
state machine and AI. There is no server and no cache-coherent shared system
memory. Each cabinet is authoritative for **its own** fighter and publishes a
per-frame record of that fighter (input, command, health, position, heading)
into a dual-port mailbox; the peer copies the record out and uses the remote
fighter's input and state. Sync is therefore a **per-frame block exchange**,
not lockstep input-only and not copy-on-write.

## 1. Local publish (`0x273f0` / `0x274a0`, `KNOWN`)

Two per-object update variants, both after the frame step, write the local
fighter into the transmit record at `0x5032f0`:

```
273f0: mov  g0,r4
273f4: bal  0x23ce8
273fc: call 0x371e0              ; VON_FN_FRAME_STEP (input consumer + heading)
27400: ldob 0x504db0,g5          ; local MB
27408: ldob 0x504dac,g4          ; local MA
27410: stob g5,0x503805          ; record+0x515 = MB
27418: stob g4,0x503804          ; record+0x514 = MA
27420: ldos 0x108(r4),g4
27424: stos g4,0x503806          ; record+0x516 = command
2742c: ldos 0x1d0(r4),g4
27430: stos g4,0x503808          ; record+0x518 = +0x1d0 (health/status)
27438: ldos 0x1d2(r4),g4
2743c: stos g4,0x50380a          ; record+0x51a = +0x1d2
27444: ldos 0x1d8(r4),g4
27448: stos g4,0x50380c          ; record+0x51c = +0x1d8
27450: ld   0x8(r4),g1
27454: st   g1,0x503810          ; record+0x520 = x
2745c: ld   0xc(r4),g1
27460: st   g1,0x503814          ; record+0x524 = y
27468: ld   0x10(r4),g1
2746c: st   g1,0x503818          ; record+0x528 = z
27474: ldos 0x2e(r4),g4
27488: st   g4,0x50381c          ; record+0x52c = heading (+0x2e)
27490: call 0x32810              ; backbone
```

`0x274a0` is the sibling arm (`call 0x3e5e0` first) with the same stores.

## 2. Mailbox exchange (`0x14b4`-`0x1564`, `KNOWN`)

Reached from the interrupt dispatcher `0x1380` (saves context, reads the
pending mask `0x501cd0`, dispatches by level; the level-1 arm at `0x1424` runs
the frame services and then the exchange). The exchange:

```
14cc: lda 0x5032f0,g1            ; local transmit record
14c4: lda 0x1a12000,g0           ; shared own half (frameStart 0x2000)
14d4: shlo 8,7,g2                ; 0x700 bytes
1508: call 0xf5d40               ; publish local -> shared

150c: lda 0x501ce0,g0            ; local receive buffer
1514: lda 0x1a12700,g1           ; shared peer half (frameOffset 0x700)
151c: shlo 8,7,g2                ; 0x700 bytes
1520: call 0xf5d40               ; fetch peer -> local
```

Then a checksum gate and a second copy into the record table:

```
1524: ldos 0x501ce2,g4           ; received checksum field
152c: ldos 0x502236,g5           ; local expected
153c: xor/and/sub ...            ; mismatch -> 0x1594 (0x5024f4 = r6)
1550: lda 0x5024f0,g0            ; record table base
1558: lda 0x501ce0,g1            ; received buffer
1560: shlo 8,7,g2                ; 0x700
1564: call 0xf5d40               ; accept peer record
1584: st g3,0x515080             ; link progress flag = 2
```

`0x501ce0` is the raw received block; `0x5024f0` is the accepted peer record
table (`0x700` stride: `0x5024f0`, `0x502bf0`, `0x5032f0` = records 0/1/2).

## 3. Remote consume (`0x72ea0`, `KNOWN`)

The input-commit gate reads the remote fighter's input from the accepted
record when linked (`0x503a08 == 2`) and in gameplay (`0x5039f4 == 4`):

```
72ec0: ldob 0x1a14002,g4         ; FG flip-gate
72ec8: and  1,g4,g4              ; active buffer half
72ed8: lda  0x5024f0(g5),g5      ; g5 = 0x700*(FG&1)
72ee0: ldob 0x514(g5),g4         ; remote MA
72eec: st   g4,0x504dac
72ef4: ldob 0x515(g5),g4         ; remote MB
72f00: st   g4,0x504db0
```

So the local fighter's own `0x504dac`/`0x504db0` feed the transmit record, and
the remote fighter's are overwritten from the received record before the
commit gate runs.

## 4. Record layout (`0x5032f0` transmit, peer accepts at `0x5024f0`)

| Offset | Field |
| ---: | --- |
| `+0x04` | link status / checksum (`0xfe` idle, `0x5024f4`) |
| `+0x514` | MA (packed translation input) |
| `+0x515` | MB (packed twist input) |
| `+0x516` | command halfword (`object+0x108`) |
| `+0x518` | `object+0x1d0` (health/status) |
| `+0x51a` | `object+0x1d2` |
| `+0x51c` | `object+0x1d8` |
| `+0x520` | x (`object+0x08`) |
| `+0x524` | y (`object+0x0c`) |
| `+0x528` | z (`object+0x10`) |
| `+0x52c` | heading (`object+0x2e`) |

## 5. Frame timing

- The exchange runs in the interrupt path (VINT-class), once per frame.
- The board's Z80 HDLC moves the record (`0x02` type + bank flip), and the
  master's vsync clocks the pair; see
  [../docs/cpu3-disassembly.md](../docs/cpu3-disassembly.md).
- The `FG` flip-gate (`0x1a14002` bit0) selects the active record half, so the
  game consumes the half the board is not currently filling.

## Open items

- Whether the remote fighter's simulation is corrected by the received
  position/heading (and where the accept consumer is) is not yet traced; only
  the input consume at `0x72ea0` is located.
- The `0x502236` expected-checksum source and the `0x515080` progress flag
  semantics are unnamed.
