# Weapon damage attribution (replayed human bouts)

Date: 2026-09-12
Analyzer: `von/tools/analyze-weapon-damage` (test:
`von/tools/test_analyze_weapon_damage.py`)

## Scope

Goal: attribute per-frame health drops in the instrumented replay logs to the
three player weapon slots and classify each drop as a discrete hit or a
sustained per-frame drain.

Data used:

| log | layout | notes |
| --- | --- | --- |
| `/home/longjoel/von-scratch/replay-weapons2/record.log` | new (6 hp cells) | primary; 5595 rows, frames 2000..7594 |
| `/home/longjoel/von-scratch/replay-weapons/record.log` | legacy (4 hp cells) | cross-check of the same macro; logger logged `0x503ca2,0x50380a,0x503ca4,0x5042a4` |
| `/tmp/opencode/vonrun/replay-022721/record.log` | new | independent replay of `human-20260909T022721Z` |

The primary log replays `human-20260909T021757Z`. The cell order is
`0x503ca8 (snapshot), 0x503ca0 (working player), 0x503ca2 (display player),
0x50380a (opponent side), 0x5042a8 (working mirror), 0x5042a2 (display
mirror)`.

## Method

`von/tools/analyze-weapon-damage` parses the `weapon:` rows and:

1. finds a **timer start** wherever a 16-bit cooldown timer transitions
   `0 -> positive`, separately recording mid-cooldown refires (a jump of
   `>50` while already positive, i.e. the documented `~+295` stacking);
2. groups **consecutive decreasing frames** of a health cell into one drop
   event (start = first dropped frame);
3. classifies the shape using the **working** cell (`0x503ca0`), not the
   display cell: it counts how many frames inside the event window actually
   lower the working value. One application = `discrete`; two or more =
   `sustained`. A drop `>= 250`, or an event whose window rewrites the round
   snapshot cell (`0x503ca8`), is a `transition`; a drop `< 20` is `tiny`;
4. associates each event with the **most recent player fire** within a
   window (default 180 frames) and records the latency, and reports
   lower-bound "implied opponent fires" from the un-attributable events;
5. aggregates per slot: attributed hit sizes, count, total, latency
   mean/deviation, fires that produced no event, and a confidence label.

The legacy layout does not log the working cell, so it falls back to the
display ramp and marks those shapes `sustained(ramp-only)`.

## Cell behaviour: the display cell is not the instantaneous value

The same macro was logged with both layouts; both give the same 15 drop
events and the same sizes.

- `0x503ca0` (working) drops the full hit in **one frame**, every time.
  Across the whole primary capture it has 15 decreasing frames and
  **zero consecutive-decrease pairs**.
- `0x503ca2` (display) eases toward the working value at ~5–9 units/frame,
  so an instantaneous hit appears as a 2–35 frame ramp. For example the
  `-150` hit lands in one frame at `f3212` on the working cell and ramps
  `480 -> 330` over `f3213..f3229` on the display.

Consequence: span alone cannot separate "discrete" from "sustained". On the
legacy log (no working cell) the same events classify as
`sustained(ramp-only)`; the new log, with the working cell, shows they are
all discrete. **In this capture there are no sustained per-frame drains.**
The apparent 8–9/frame "beam drains" are the health-bar easing animation.

The opponent-side cell `0x50380a` is a delayed self-mirror, not an
independent opponent HP: its non-baseline excursions reproduce the display
cell's values a few frames later and then reset to their 750/780 baseline
(`f2368-2371`: `0x50380a` = `739,730,721,714`, the same values
`0x503ca2` holds; `f2379`: `0x50380a` snaps back to `750`). The working
mirror `0x5042a8` is constant within each round (`830`, `1000`, `750`,
`1000`), and the display mirror `0x5042a2` only animates the round reset.
Neither carries per-hit opponent damage. This matches
`weapon-behavior-findings.md`, which calls `0x50380a` "derived/churn".

## Results

### Timer starts (player weapon fires)

| slot | weapon | timer | fresh starts | refires |
| --- | --- | --- | --- | --- |
| 1 | right | `0x503cbc` | `2215, 2336, 2381, 2426, 2608, 2934, 3144, 5538, 6365, 6545, 7350` (11) | — |
| 2 | left | `0x503cba` | `3041, 5658, 5840, 5933, 7494` (5) | `2061, 5937` |
| 3 | both | `0x503cbe` | none | — |

Right-slot cooldown runs are rapid (mostly `10–40` frames, or `160` when two
shots stack); the left-slot run starting at `3041` lasts until the `f3909`
round reset, consistent with the 300-frame base timer plus stacking.

### Live-cell drop events (display cell `0x503ca2`)

| # | frames | span | damage | shape | proximity slot | latency |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | f2326-2329 | 4 | 32 | discrete | 1 | 111 |
| 2 | f2368-2371 | 4 | 34 | discrete | 1 | 32 |
| 3 | f2376-2379 | 4 | 34 | discrete | 1 | 40 |
| 4 | f2560-2568 | 9 | 80 | discrete | 1 | 134 |
| 5 | f2921-2924 | 4 | 30 | discrete | — | 313 |
| 6 | f2927-2930 | 4 | 30 | discrete | — | 319 |
| 7 | f2934-2937 | 4 | 30 | discrete | 1 | 0 |
| 8 | f2941-2944 | 4 | 30 | discrete | 1 | 7 |
| 9 | f3213-3229 | 17 | 150 | discrete | 1 | 69 |
| 10 | f3909 | 1 | 330 | transition | — | 765 |
| 11 | f5243-5277 | 35 | 207 | discrete | — | 2099 |
| 12 | f6077-6087 | 11 | 63 | discrete | 2 | 144 |
| 13 | f6266-6285 | 20 | 115 | discrete | — | 333 |
| 14 | f6395-6429 | 35 | 207 | discrete | 1 | 30 |
| 15 | f6635-6636 | 2 | 8 | tiny | 1 | 90 |

Hit-size catalog over the capture (reliable part):

| size | count | frames |
| --- | --- | --- |
| 8 | 1 | f6635 |
| 30 | 4 | f2921, f2927, f2934, f2941 |
| 32 | 1 | f2326 |
| 34 | 2 | f2368, f2376 |
| 63 | 1 | f6077 |
| 80 | 1 | f2560 |
| 115 | 1 | f6266 |
| 150 | 1 | f3213 |
| 207 | 2 | f5243, f6395 |

`f3909` (`330`, snapshot cell rewritten) is the round-1 end copy, not a hit.

### Per-slot estimates

These are the requested slot-keyed numbers. The "hit sizes" are the live-cell
drops whose start falls within 180 frames after that slot's most recent fire.
They are **not causally attributable** (see Confounds).

| slot | weapon | fires | proximity drops | hit sizes | count | median | latency mean ± sd | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | right | 11 | 9 | 8, 30, 30, 32, 34, 34, 80, 150, 207 | 9 | 34 | 57 ± 44 | none (proximity only) |
| 2 | left | 5 | 1 | 63 | 1 | 63 | 144 | none |
| 3 | both | 0 | 0 | — | 0 | — | — | none |

## Confounds and why no causal attribution is possible

1. **The live cell is damage received, the timers are damage dealt by the
   same fighter.** `0x503ca2` is the local player's own health; its drops are
   hits the local player *takes*. The weapon timers are the local player's
   own cooldowns. There is no logged mapping from the local fighter's shots
   to the local health, so the drops cannot be the local weapons' damage.
2. **No consistent fire -> drop latency.** The right-slot latencies are
   `0, 7, 30, 32, 40, 69, 90, 111, 134` frames and the unexplained drops sit
   `312–2099` frames after the previous fire. No fixed travel/lock time
   fits. The attribution window covers ~38% of frames, so a proximity match
   is expected by chance for many drops.
3. **The opponent HP is not logged.** `0x50380a` self-mirrors the local
   display and resets to a baseline; the mirror pair is round-constant. Of
   its 119 detected drops, 68 are `>= 250` round copies and the rest are the
   mirror ramp, not independent hits.
4. **Round transitions copy large values.** `f3909` copies `330` and rewrites
   `0x503ca8`; drops of `270/357/420/535/738/750` appear on `0x50380a` at
   round boundaries in the same capture. These are excluded by the
   transition rule.
5. **The replay does not appear to drive the logged fighter.** Replaying two
   *different* human macros — `human-20260909T021757Z` (4687 rows) and
   `human-20260909T022721Z` (5140 rows, different md5) — produced a
   byte-identical weapon log for frames 2000..4999 and an identical
   live-event sequence through frame 6999. Human aim therefore cannot be
   read out of this capture; any "misses" here are not the human's misses.

## Update 2026-09-12: corrected opponent cell and the dealt-damage signal

The "working mirror" cell this report relied on (`0x5042a8`) is the opponent's
round **snapshot**, not its working HP. The bout struct is symmetric at
`+0x600`, so the opponent working cell is `0x5042a0` (pair of `0x503ca0`; set
from `0x51d1b0` with it at `0x87ce8`). `VON_RECORD_WEAPON_LOG` now logs seven
cells (`...0x5042a8, 0x5042a2, 0x5042a0`) and `analyze-weapon-damage` gained a
`new7` layout with a **DEALT** section: opponent-working drops paired with the
player's own attack timers.

**The original human session does show dealt damage.** Its 10 s work-RAM
snapshots (`von/captures/human-20260909T021757Z/snaps/`), decoded at
`0x503ca0`/`0x5042a0` vs their snapshots:

| t | pl working | pl snapshot | opp working | opp snapshot |
| --- | --- | --- | --- | --- |
| 30 s | 1000 | 1000 | 1000 | 1000 |
| 40 s | 1000 | 1000 | 480 | 1000 |
| 50 s | 1000 | 1000 | 0 | 1000 |
| 60 s | 1000 | 1000 | 520 | 520 |
| 70 s | 1000 | 1000 | 445 | 520 |
| 90 s | 795 | 1000 | 177 | 520 |
| 110 s | 416 | 1000 | 0 | 520 |

The opponent working cell drops while its snapshot holds — exactly the
damage-dealt signal — and later both sides trade damage. This confirms the
corrected map against a real joined bout.

**The macro replay still cannot supply it per frame.** A new capture
(`/home/longjoel/von-scratch/replay-weapons3/record.log`) replays
`human-20260909T021757Z` with the seven-cell layout. Its bout is the attract
demo: the timer timeline is byte-identical with the macro and with no macro,
and unchanged by a scripted coin+start (with either the human capture's
credited cfg or a fresh NVRAM). The macro does reach the ioports
(`macroplay ... read=` changes), but P1 is ignored during attract, so the
opponent working cell never drops. The per-slot damage tensor therefore still
requires a **joined** per-frame session; the capture/analysis harness is now
ready for one.

## Verdict

The reliable deliverable from this data is the **incoming hit-shape catalog**
(30 x4, 32, 34 x2, 63, 80, 115, 150, 207 x2, all single-frame/discrete; one
round-end copy of 330), plus the recovered fire cadence. A per-weapon
damage tensor for the player's three slots is **not estimable** from these
logs: the only clean health series is the local fighter's own incoming
damage, the opponent series is a self-mirror, and the replayed inputs do not
change the logged combat. The slot table above is shown only to satisfy the
requested format and should be read as `confidence = none`.

To close this, a future capture must log the **opponent's** working health
cell (now known: `0x5042a0`) together with the *attacker's* timers, at one
frame resolution, from a **joined** session whose input replay demonstrably
changes the logged state. The remaining blocker is the join: the saved human
macros replay into attract mode (see the update above), so a per-frame joined
capture is still owed.

## Reproduction

```sh
# primary + generated JSON/markdown
von/tools/analyze-weapon-damage /home/longjoel/von-scratch/replay-weapons2/record.log \
  --json /tmp/wd-primary.json --markdown /tmp/wd-primary.md

# seven-cell capture (both working cells) and DEALT section
von/tools/analyze-weapon-damage /home/longjoel/von-scratch/replay-weapons3/record.log

# legacy layout cross-check
von/tools/analyze-weapon-damage /home/longjoel/von-scratch/replay-weapons/record.log --layout legacy

# regression test
python3 von/tools/test_analyze_weapon_damage.py
```

The seven-cell capture was produced with:

```sh
VON_RECORD_LOG=<out>/record.log VON_RECORD_SNAP_DIR=<out>/snaps \
VON_RECORD_MACRO_PLAY=von/captures/human-20260909T021757Z/macro.txt \
VON_RECORD_MACRO_PLAY_PRESERVE_TIMING=1 VON_RECORD_WEAPON_LOG=1 \
  ./bin/von vonj -rompath von/build/disasm/rompath -video none -sound none \
  -skip_gameinfo -seconds_to_run 135 -autoboot_script von/tools/record_human_session.lua
```
