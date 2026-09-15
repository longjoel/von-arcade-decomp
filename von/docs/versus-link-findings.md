# Virtual-On versus/link findings

Updated 2026-08-28.

## Confirmed result

The `vonj` twin-cabinet path now passes a 60-second deterministic versus
smoke test. Both cabinets establish a link, exchange handshake and frame
traffic, accept independently injected credit/start inputs, reach battle, and
remain linked while scripted movement and firing inputs run.

Passing capture:

`von/captures/twin-diagnostic-vonj-20260828T204801Z/results.csv`

Reproduce it with:

```sh
VON_TWIN_PREFLIGHT=1 VON_TWIN_SECONDS=60 ./scripts/test-twin.sh
```

The documented service-manual setup is one Master seat and one Slave seat.
The harness applies that explicit role assignment while leaving the eight
`SW3` bits unnamed/unknown. The manual also indicates that versus settings
are controlled from the Master side.

## Communication evidence

The successful trace shows:

- P1 shared RAM role byte `0x01` = Master.
- P2 shared RAM role byte `0x02` = Slave.
- Both boards report `link-state=established`.
- Handshake packets `0xff` and `0xfe` are exchanged.
- Frame synchronization packet `0xfc` is exchanged.
- Cabinet data packets use IDs `01` and `02`.
- Shared RAM changes to link state `01`, with cabinet IDs `01/02` and count
  `02`.

The earlier apparent failure was partly environmental: sandboxed runs showed
`Operation not permitted` when opening loopback sockets. Runs that test the
link must permit local TCP sockets.

## Changes made

- Updated the Virtual-On MAME status flags: `von`, `vonu`, and `vonj` are
  imperfect in graphics and sound; `vonjdev` remains not working.
- Added `-comm_master` and `-comm_diagnostics` MAME options.
- Set the communication role byte from the explicit Master/Slave option.
- Added isolated communication diagnostics for link state, shared RAM
  `00..03`, role, handshake/frame packet IDs, and TX/RX failures.
- Added deterministic twin execution with isolated config, NVRAM, input, and
  snapshot directories per cabinet and reproducible `SW3` case values.
- Added scripted MAME input-field resolution, credit/start injection, and
  battle input/screen-change logging.
- Added Test Menu preflight automation for the documented game-assignment and
  network-link setup.
- Fixed the remote build workflow so the modified communication source is
  synchronized before compiling, and the resulting binary is copied back to
  `bin/von`.
- Made the harness work without `rg`, run headlessly with SDL's dummy video
  driver, reject stale diagnostic binaries, and avoid false link failures from
  asymmetric cabinet shutdown.

## Current scope

This validates the first milestone—synchronized battle startup and stable
communication—not a complete match or physical DIP-switch identification.
No core communication behavior was changed based only on the successful
result; the next DIP work remains a staged, evidence-driven matrix.
