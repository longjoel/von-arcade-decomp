# Object state semantics (0x32560 table)

Derived from the i960 `vonj` listing and the recovered docs. The per-object
update `0x32810` dispatches on `object+0x172` (masked, 0..42) through the
43-entry table at `0x32560` (16-byte stride) when the action arms and geometry
prefix have run. `object+0x1b2` is the independent action selector (14-entry
table at `0x32968`); `object+0x1c4` is the speed scalar, `+0x184` the facing,
`+0x0c` the vertical position, `+0x150` the vertical velocity.

Confidence per row: K = KNOWN/LIKELY, S = SPECULATIVE. This is a working map,
not canonical evidence.

## Families

| family | states | meaning |
| --- | --- | --- |
| idle / clip player | 0, 1, 11, 15, 16, 17, 32, 36 | stand, action-class recovery, turn/pursuit, locomotion clip play |
| attack / weapon launch | 2–10, 12, 13, 38–40 | emit packet 31, set `+0x1b2=11`, speed from `cfg+0x59c/0x5a0/0x5a4` |
| jump / air | 22, 23, 24, 28, 29, 35, 37 | seed `+0x150`, integrate `+0x0c`, descent/land |
| landing / getup | 14, 25, 27, 30 | clip-end transitions back to 0/11/16 |
| dash | 19, 20, 21 | `+0x1b2=5`/`7`, `+0x190` timers, chain into 11/36–40 |
| turn / aim | 18, 26 | turn-in-place, aim-and-fire → 21 |
| locomotion | 31, 33, 34 | primary ground movement; speed from `cfg+0x56c/0x570/0x574` and `cfg+0x578..0x598` |
| ambient / helpers | 41, 42 | idle randomizer, init/terminal |

## Per-state summary

| # | handler | `+0x172`→ | `+0x1b2`= | key writes | meaning (conf) |
| --: | --- | --- | --- | --- | --- |
| 0 | 0x2f580 | — | 0 | `+0x186/188=0`, cfg clip publish | idle stand clip (K) |
| 1 | 0x2f930 | 0,15 | — | classifies `+0x102` | action-class recovery (K) |
| 2–8 | 0x2e450…0x2ebb0 | — | 11 | packet 31, cfg cb, `+0x1c4=cfg+0x59c/5a0` | weapon-launch attack variants (K) |
| 9 | 0x2ece0 | 2,3 | 11 | record pair, `+0x17a=21` | attack entry / clip selector (K) |
| 10 | 0x2ef90 | — | — | cb by `+0x174` | per-weapon tail dispatcher (K) |
| 11 | 0x2f010 | 0,12,13 | — | 3-phase cfg publish | turn/pursuit movement (K) |
| 12,13 | 0x2f360,0x2f260 | — | 11 | cfg cb, `+0x1c4=cfg+0x5a4` | weapon/action variants (K) |
| 14 | 0x2f460 | 0,16 | — | `+0x2e` slew | landing/phase transition (K) |
| 15 | 0x2fa20 | 16 | 0 | publish `cfg+0x78/7c` | locomotion clip player (K) |
| 16 | 0x2fb20 | — | 0 | dispatch `+0x170`→cfg | locomotion/movement clip (K) |
| 17 | 0x2fd50 | 0 | 0 | clip-end reset | locomotion clip-end (K) |
| 18 | 0x31910 | 0 | 10 | turn clip, random `+0x19a` | turn-in-place (K) |
| 19 | 0x31ab0 | 20 | 10,5 | dash entry | dash entry (K) |
| 20 | 0x31d20 | 11,21,36–40 | 5,7 | dash chain | dash chain (K) |
| 21 | 0x32120 | 0,1,11 | — | dash recovery | dash recovery (K) |
| 22 | 0x2fe30 | 23 | — | `+0x150=cfg+0x614` | jump takeoff (K) |
| 23 | 0x2ff80 | — | — | `+0x0c += +0x150` | airborne (K) |
| 24 | 0x300c0 | — | 0 | gravity `+0x150 -= cfg+0x62c` | descent/gravity (K) |
| 25 | 0x30230 | 0,11 | 0 | landing commit | landing commit (K) |
| 26 | 0x32330 | 21 | — | aim-and-fire, `+0x174` | turn/aim-and-fire (K) |
| 27,30 | 0x303e0,0x30420 | 0 | — | cb `cfg+0x430` | hit/knockdown recovery reset (S) |
| 28 | 0x30460 | 0 | — | getup clip | getup/land clip (S) |
| 29 | 0x30590 | — | 0 | air drift, `+0x150` clamp | air-drift/descent (K) |
| 31 | 0x30660 | 0,33,35 | — | weapon gate, `+0x1c4` speed | primary locomotion/action (K) |
| 32 | 0x30c20 | 0 | — | clip → idle | locomotion clip → idle (K) |
| 33 | 0x30d40 | — | — | sub-clip / weapon select | locomotion sub-clip (K) |
| 34 | 0x30e40 | 31 | — | speed entry | locomotion clip → 31 (K) |
| 35 | 0x30ff0 | — | — | air/hover loop | air/hover loop (K) |
| 36 | 0x31210 | 31 | — | sibling of 34 | locomotion → 31 (K) |
| 37 | 0x313e0 | — | — | air loop, vy reset | air loop (K) |
| 38,39,40 | 0x315a0,0x316d0,0x317f0 | 11 | 11 | packet 31, cfg cb | attack variants (K) |
| 41 | 0x324e0 | — | — | random `+0x19a` | ambient/idle randomizer (S) |
| 42 | 0x32540 | — | — | cb `cfg+0x43c` | init/terminal helper (S) |

## Transitions

```
1→0,15     9→2,3      11→0,12,13  14→0,16    15→16
17→0       18→0       19→20       20→11,21,36,37,38,39,40
21→0,1,11  22→23      25→0,11     26→21      27→0   28→0   30→0
31→0,33,35 32→0       34→31       36→31      38→11  39→11  40→11
```

No direct `+0x172` write (hand off via callback/action arm): 0, 2–8, 10, 12,
13, 16, 23, 24, 29, 33, 35, 37, 41, 42.

## See also

The opponent (CPU) behaviour that selects these states is annotated in
[opponent-ai.md](opponent-ai.md): a SHARC bearing query, a 10-sector
classifier (`0x73508`), a sector -> class table, and a 34-way class dispatcher
(`0x735f0`, table `0x73618`) that writes the command word at `object+0x108`.

## Input path

The `0x72ea0` commit gate accepts a command only in `+0x172 ∈ {15,16,31}`
(repeat byte `>0xf5`); the locomotion family is therefore the input-facing set.
Jump (22→23→24/28/29/35), dash (19/20/21), and attacks (2–10,12,13,18–21,26,
33,38–40) are entered from `+0x170`/`+0x1b2` inside that family. Handlers only
read the `+0x138..` weapon-availability bytes; the cooldown service
(`0x4a4xx`/`0x64xxx`) writes them. No handler writes working/display health
(`+0x1d0/+0x1d2`); that is the round/damage path (`0x87ce8`).
