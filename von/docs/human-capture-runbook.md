# Human-instrumented capture runbook (jump-apex lock session)

Goal: a JOINED player (you) performs scripted jump-apex attempts while MAME
traces geometry + RAM. This is the lock-on ground truth the scripted runs
could never produce (bots never joined; every prior battle is CPU-demo
playback with inputs ignored past the latch).

## 0. What changed in MAME

`third_party/mame-master/src/mame/sega/model2_v.cpp` (native incremental
rebuild done 2026-09-08, binary refreshed): the geometry trace window is no
longer hardcoded 138-172. `VON_TRACE_T0`/`VON_TRACE_T1` (machine seconds,
defaults 138/172) gate object + matrix logging, and the count caps are
raised (objects 131072 -> 4194304, matrices 1048576 -> 16777216) for
multi-minute sessions. Verified: T0=0/T1=30 smoke logs times 20.2-30.0
only, then stops. (Patch files 0007/0008 are stale vs the tree -- the tree
is authoritative; polygon tracing stays disabled.)

## 1. Map the gamepad (once -- now preloaded)

The launcher copies the last mapped session's `cfg/` into each new capture
(`VON_HUMAN_CFG` overrides: unset = default preload, set = that dir, empty
= start unmapped), so the below should already hold. Verify in Tab ->
Input Assignments rather than remapping from scratch:

- Left analog stick -> P1 Left Stick Up/Down/Left/Right
- Right analog stick -> P1 Right Stick Up/Down/Left/Right
- 4 face/shoulder buttons -> P1 Left Shot, P1 Left Dash, P1 Right Shot,
  P1 Right Dash (your choice which is which; note it down)
- Start button -> 1 Player Start
- Select/back -> Coin 1
- Gamepad Y -> Coin 2 = MARKER (was d-pad down: hat directions never fire
  on this controller, so taps never reached the script). Tapping it
  only adds a credit; the recorder logs `mark f<frame> #<k>` per tap.
  HOLD it ~0.75s (or TRIPLE-TAP it fast) to toggle macro capture of the
  12 P1 input bits to `macro.txt` (one `start <frame>` section per
  toggle-on, `<frame> <mask>` rows); hold/triple-tap again to stop. The
  toggling press still logs one mark. Every tap flashes a white dot on
  screen so you can see taps register; the red REC circle means capture
  is running.
  Replay a capture hands-free with
  `VON_RECORD_MACRO_PLAY=<macro.txt>` (drives the P1 fields from the rows).
  While capture is active a red REC circle + label shows top-left on the
  game screen. `VON_RECORD_MACRO_START=1` starts capture at boot (skips
  the first hold).

The recorder (`von/tools/record_human_session.lua`) drives NO inputs and
never exits early: dense statelog (transition cells every 2f, workspaces
every 5f), full snapshots every 10s, tilemap flow log.

Writer-PC watch (optional, env-gated, off by default): set
`VON_WATCH_WRITES="0x503CB8,0x4"` (repeat `base,len` windows with `;`)
and the recorder installs one passive write tap per window at session
start. Taps return data unchanged; each write is attributed to the
maincpu CURPC at tap time, and distinct writer PCs per window are counted
(max 64) and summarized as `watch:` lines every 600 frames plus one
`watch: ... final` set at session end, e.g.
`watch: @00503cb8 f600 writers=2 0x1a2b3c(x8) 0x9f0000(x2)`.
Use it to resolve writer PCs for open RAM cells (e.g. 0x503CB8) during
any capture without touching the trace window or inputs.

## 2. Launch

./scripts/record-human.sh
# out: von/captures/human-<UTC>/  budget: 600s  window: [0, 600]

Override per session: VON_HUMAN_OUT, VON_HUMAN_SECONDS,
VON_TRACE_T0/VON_TRACE_T1 (e.g. skip menus: T0=60),
VON_HUMAN_SNAP_EVERY_S.

The launcher passes `-log` and runs MAME from the capture dir, so the C++
geometry trace lands in `<out>/error.log` (~1 MB/s while the window is
open: ~120k matrix + ~125k object events per 40 s of battle). Narrow
VON_TRACE_T0/T1 around the rounds if disk is tight; without `-log` the
trace is silently discarded (this bit two earlier captures).

## 3. Maneuver script (~4 minutes)

0. Pre-flight: at boot, TAP MARKER 3 times, then in another terminal
   `grep -c ^"mark " <out>/record.log` -- expect 3. If 0, the Coin 2
   mapping is dead (remap to a face/shoulder button, not a hat direction)
   and no ground truth will record: fix it before playing.
1. Coin in, 1 Player Start, pick Temjin (or note your pick), confirm,
   wait for round 1. TAP MARKER as the fight starts.
2. Jump-apex attempts x10: jump, TAP MARKER at the top (best effort),
   land, walk back toward the enemy, repeat. Keep some attempts aimed
   (cursor passes over the enemy) and some deliberately aimed away.
3. Dash-throughs x3 with marker taps.
4. TAP MARKER at each round end. Play until the 600s budget or two rounds.

Pause with P anytime (MAME built-in); close the window to end early.

## 4. Hand back

Give back the whole `von/captures/human-<UTC>/` directory. Analysis runs:
extract_frames_json.py -> annotate_bout.py (cpu mode) ->
join_state_segments.py (marks ride along as event timestamps). Apex marks
vs transition-cell flips = the lock test; aimed-vs-away pairs separate
cursor lock from apex lock.
