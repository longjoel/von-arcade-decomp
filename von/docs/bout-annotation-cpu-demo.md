# Bout annotation: CPU-demo tail (attract, coinless run)

Source: 20 s geometry tap (`demo.json`, 791 frames, t=138.0-158.0 s of a
coinless attract run). Produced by `von/tools/annotate_bout.py --mode cpu`.

## What the window contains

- 138-149 s: tail of a CPU-vs-CPU round, mech A (`00845` family, mobile,
  ~19 parts) vs mech B (`00851` family, static turret, ~19 parts), ~11 u
  apart, close strafe battle. Constant 38-sprite ambient layer (`0093cc0a`,
  likely stage weather/snow).
- ~149 s: A dies. No part-count spike marks it (wreckage shares the family
  prefix, counts stay flat at ~92-126); the mobile track ends and family
  `00845` unloads. Ten `009e` (Temjin) parts prefetch during the death.
- 155.7 s: scene cut (`bout_end_cut`: `00845` count 1 vs median 92).
  Temjin (`009e`, 17 parts) vs `00a6` foe (15 parts) on a `0091` stage.
  Temjin root enters; trace ends at 158 s mid-intro.

## Machine timeline (`--mode cpu` output, 7 events)

| t (s) | event | detail |
|---|---|---|
| 138.0 | combat_window_start | A 18 mobile chains, B 17 chains |
| 138.0 | ordnance_linger | `008a`, 1.1 s, hovers ~11 u from mechs |
| 139.2 | ordnance_linger | `0089`, 2.1 s, spawns 5.5 u from A |
| 141.2 | ordnance_linger | `008a`, 4.2 s, longest carry window |
| 145.4 | ordnance_linger | `0089`, 2.1 s, spawns 5.5 u from A |
| 147.5 | ordnance_linger | `008a`, 1.9 s, last action before death |
| 155.7 | bout_end_cut | `00845` count collapses, Temjin scene loads |

No `dash_candidate` fires: max member-chain speed is 7.3 u/s (median 1.5).
An early single-part "dash" reading (12 u flips on `00845828`) did not
survive full-rate chaining -- it was a limb/trail excursion, not body
translation. A advances ~12 u over 11 s; B never translates.

## Lock-on check (geometry only)

- Both `0089` bursts spawn 5.5 u from A's centroid, drift <2.5 u over 2 s
  (they linger, they do not fly), with 8-frame OBA cycling. Read: impact
  flashes / dropped ordnance near A, not outgoing missiles.
- Initial burst direction vs bearing A->B: 64 deg and 71 deg off-axis, with
  no homing curvature (angle constant +-2 deg over the linger). Firing in
  this sample is NOT bearing-locked.
- B's weapon family (`0088`) has zero records in the window, so B's aim
  cannot be tested from geometry. Torso yaw vs bearing needs part identity
  from RAM (see below).

## Method notes (built into the tool)

- OBA ids churn per animation segment, so parts are chained by position
  continuity (greedy nearest-neighbour, 8 u gate, median-count seed frame),
  then split by mobility: static chains = stage architecture, mobile chains
  = mech. Centroid is median + per-frame 20 u outlier rejection.
- Bursts are classified by own motion (travel > 15 u = projectile,
  near-mech linger = ordnance, else ambient), not by exact spawn distance,
  because centroid conventions carry a few units of membership noise.

## Tap frame caveat (found 2026-09-08, corrected same day)

The tap positions are NOT world-fixed: camera yaw plus translation drift.
The first de-yaw (persistent >80%-presence refs, farthest-from-centroid
star) was FALSIFIED on review: on demo.json its star was a mech part
travelling 25u with arms disagreeing 15-27 deg (median of garbage), and on
mirror.json its star travelled 672u and missed frame 0, silently degrading
to yaw=0. Persistence does not imply rigidity.

The replacement (`annotate_bout.estimate_yaw_track`, shared by
`export_match_playthrough_gltf.py`) selects the rig by rigidity: candidate
OBAs (>20% presence) scored by pairwise-distance stability, grouped into
rigidity-graph components, tried largest-diameter-first, accepted only on
arm agreement (spread <=5 deg) and non-blindness (span >=2 deg when the
scene moves -- a screen-fixed HUD reports zero yaw while everything else
flies). Refusals yield translation-only tracks with yaw_trusted False.

Verified on demo.json: trusted rig (24 arms, spread 3.0 deg, span 19.6 deg
off a posing mech during an intro sweep). Cross-family proof: 59 parts
across 6 families (0084/0089/008a/0091/009e/00a6) collapse under 1.0u RMS
post-stab while the two fighters (61x0084 + 8x0085 + 0093) keep moving --
a shared rotation across independent bodies can only be camera. Mirror.json
honestly refuses (HUD overlay + pitching torso + scrollers, no world rig).

WARNING: bout/mirror gallery assets were exported with the falsified
estimator. The bout clip has independent visual confirmation (still stage,
moving mechs) so it stands provisionally; both clips need re-export on the
next capture. Do not quote the old 37.8 deg demo span -- it was fiction.

## Next (needs RAM, not geometry)

State IDs, HP, and true torso yaw come from the warp + AI-off + fuzz setup
(fuzz_battle_ram.lua), not from more geometry. That is the path to the
per-unit state-ID tables and a decisive lock-on test.

## OBA registry + bout-mech identification (found 2026-09-08)

`von/oba_registry.json` maps OBA families to mechs, seeded from the viewer
roster catalog (node-name OBA census: Dorkas 00a6, Fei-Yen 00a8, Belgdor
00a4, Viper II 00a1, Bal-Bas-Bow 00ad, Apharmd 00a7, Temjin 009e, Raiden
009f) plus trace censuses. Families are mech-stable across captures, not
load slots (00a6 = Dorkas in step02, versus-lineup, demo, and mirror).

Negative result: the demo/bout fighters 0084/0085 are UNCATALOGUED -- zero
4-hex suffix overlap with any roster family, absent from all 8 roster
assets. 0085's 11-part core is smaller than any catalog mech (min 15).
Naming them needs ROM identity pairs (oba_texmap has 2/87) or a
select-screen capture, not more geometry comparison.

Byproducts for the lock-on task: annotation v2 emits per-mech
`state_change` events with cumulative `pose_segments`: the geometry half
of the state-ID tables. (0093cc0a was a lock-marker candidate; FALSIFIED
2026-09-08 -- it is menu/showcase scene decoration, static at origin,
hidden through combat.)

## State table v0: joint geometry+RAM run (found 2026-09-08)

First joint capture (/tmp/fuzzjoin): twin versus (Temjin 009e vs Viper II
00a1, P2 idle = AI off), coin 7200 / start2 7400 / 9 scripted holds
9200-10019, geometry 138.0-165.9s (135168 objects) + 230 workspace
statelog rows @12Hz + 116 snapshots/side. Tools: fuzz_battle_ram.lua
VON_FUZZ_STATELOG (new), extract_frames_json.py (new),
join_state_segments.py (new).

Findings:
- Player workspaces (0x5039c0) carry NO animation-state bytes: dense 12Hz
  join gives 0 candidates (one pointer-churn marginal). 0x515000 object
  table is fully static (0/4096 words change pre->post): not live slots.
- Transition cells (0x504c80) DO: 00504e24/00504f24/00505020 flip 5<->3,
  00504f80 cycles 9/24/28, 00504fc8 is a 1<->0 flag, all tracking POSE
  SEGMENTS not held inputs (flips land in settle windows; values hold
  across different inputs). 00504e24 and 00504f24 flip identically = the
  same per-fighter field in two slots (local + link mirror).
- Workspace 0x503ca0 walks 03760376 -> 03160304 -> 030c0304 -> 03040304
  -> 02c902c9: nibble-structured paired state bytes.
- Anchor events: t~154.75 both mechs load full fresh overlay sets
  (round/fight start, RAM 5->3); t~157.7+ Temjin streams alternating
  009e0xxx/009e28xx overlay pairs every ~0.02s (double-buffered attack
  animation frames, RAM 3->5).
- Lock-on proper is still open: aim holds produced no distinguishing RAM
  signature (cells track segments, not aim direction), and no lock-engage
  ground truth exists yet. Next: dense statelog on 0x504c80 across a
  lock-transition capture (approach to melee range), then read the
  per-frame state bytes through the transition.

## Lock-on hunt: jump apex, dash flag, interactivity verdict (2026-09-08)

Player rules under test: visual cursor over enemy ~= locked; jump apex
auto-locks; dash can lock. Four more captures (twin + solo start2 flows,
proven single-player flow, walk/jump/dash probes) plus idle controls give
a decisive negative on method and two positive IDs:

- INTERACTIVITY VERDICT: P1 inputs never take effect in any flow tried.
  5s RIGHT-hold walk tests (twin start2 flow AND proven single-player
  flow) show root tracks bit-identical to no-input controls; only the
  input-latch word (0x503bbc) echoes. Every battle captured is CPU-demo /
  attract playback. Lock work NEEDS a real join (still open: multi-press
  select navigation with walk-test verification).
- 0x504e2c = P1 AIRBORNE/HIT-STUN flag, not dash or lock: set at launch
  onset, 1 through a full 83u flight, cleared ~1s after landing; 2-frame
  blips match brief stuns. Its twin 0x504f2c follows with a 1-frame stagger
  (compute-order echo). Jump-apex (158.9) itself flips nothing in 0x504c80.
- Cursor not found in polygon traces (no fresh OBA at dashes or the
  launch apex) and not in tile text (match-entry tilemap is blank):
  implicated layer is sprites, which needs sprite-VRAM capture.
- Determinism bonus: identical flows replay bit-identically (traces AND
  cells), so twin-vs-solo cell diffs isolate input effects cleanly --
  the method works, it just needs a joined player.

## OBA→texture identity map (found 2026-09-08)

The GL export mines (OBA)→(TPA,THA) identity pairs from P2DATAWT flushes and
commits them to `von/oba_texmap.json` (276 entries from 5 traces). Re-exports
improve as the map grows: the mirror Temjins are textured, the bout mechs stay
gray (2/87 hits). Mine future traces to extend it.
