# Weapon-family map: mech mounts and effect/projectile OBA families

Scope: attribute ranged-weapon geometry (projectiles, beams, muzzle flashes) to
the mech part OBA that fires it, and inventory the non-mech / non-stage effect
OBA families seen in the geometry captures.

Confidence legend:

- **KNOWN** — confirmed by a static ROM table, an emitter/GDB map, or a
  controlled trace and consistent across captures.
- **LIKELY** — the same reading is supported by two independent captures or by
  an asset table plus one capture; a small ambiguity remains.
- **SPECULATIVE** — single-capture nearest-mount evidence or a name/side
  inference; treat as a hypothesis to confirm.

Method and tooling:

- Static asset tables: `von/oba_registry.json` (family -> mech, part roles),
  `von/oba_texmap.json` (OBA -> tpa/tha identity pairs), and the roster part
  lists decoded by `von-godot/tools/decode_roster_tables.py`.
- Emitter anchors: `von/i960/emitter-g2-oba.json` /
  `emitter-r6-oba.json` (`probe_emitter_obas.py`); the body emitter `0x8e164`
  carries the part OBA in `g4`, the limb/option emitter `0x8d488` in `r6`. The
  probe mech was Temjin (`0x9e`) versus Fei-Yen (`0x00a8`).
- Geometry corroboration: `von/tools/classify_weapon_effects.py` (motion class)
  and the new `von/tools/attribute_weapon_effects.py` (nearest persistent mech
  part at each effect spawn; `--sides` estimates left/center/right). Captures
  used: `attract-20260912T` (Temjin/Viper II/Fei-Yen/Bal-Bas-Bow),
  `walk4-20260912T010526Z`, `fighter-belgador-20260912T`,
  `fighter-feiyen-20260912T`, `fighter-raiden-20260912T`, and the human/menu
  capture `human-20260911T201031Z`.

Note: the task references `von/obu_texmap.json`; the file in the tree is
`von/oba_texmap.json`, which is what was used.

## 1. Mech -> weapon mount -> candidate effect/projectile family

Each mech carries three weapon slots (left/center/right). Geometry identifies
the firing part as the persistent mech part whose position is nearest the effect
at its spawn frame; a mount is only listed when the same part recurs across
captures with a small median spawn distance (counts are merged over the listed
captures; the median distance is for the capture named in the evidence column,
attract by default). Left/center/right labels come from the effect
travel direction (`attribute_weapon_effects.py --sides`) and are **SPECULATIVE**
unless noted; the geometry is camera-relative and the labels are noisy.

### Temjin (`0x9e`)

| slot | mount part OBA(s) | candidate family | evidence | conf |
| --- | --- | --- | --- | --- |
| center | `009e3300`, `009e332f` | `0098xxxx` (fast shot/beam segment) | `009e3300` 92 hits / median dist 15.8 u and `009e332f` 24; both are `g4` body-emitter parts (`504730->009e3300`, `504748->009e332f`); anchor classifies `0098` as a ~29 u/f, 4-5 f beam segment | LIKELY |
| right | `009e3531`, `009e2853` | `0099d57b` (fast projectile/missile) | `009e3531` 28 hits / 10.1 u, `009e2853` 14 / 11.4 u; `0099` is 89 projectile runs of 104; anchor speed ~58 u/f, travel to 827 u; `009e3531` is an in-battle-only part (`r6` map `02079184`) absent from the roster list | LIKELY |
| left | `009e3c34`, `009e410d` | `009b` (Temjin projectile) | `009e3c34` 70 hits / 13.8 u, `009e410d` 34 / 5.4 u; `009b` is 108 projectile runs of 128 with mechfam `9e:128` (Temjin only); both are `g4` body-emitter parts (`5047xx`) | LIKELY |

`009e27fc` recurs as the nearest part for all three families (21/11/12 hits) and
has no texture entry; it is the **SPECULATIVE** shared muzzle/emitter mesh, not
a distinct weapon. The battle-only Temjin parts not present in the roster list
(`009e27fc`, `009e2853`, `009e3054`, `009e3531`, `009e5xxx`) are the strongest
weapon-mesh candidates; `009e5xxx` (21 single-range meshes at tpa
`0x0009c7xx`) is a per-frame effect stream rather than a mount.

### Viper II (`0xa1`)

| slot | mount part OBA(s) | candidate family | evidence | conf |
| --- | --- | --- | --- | --- |
| center | `00a1c5ac` | `00a3xxxx` (slow homing missile) | 50 hits / median dist 1.7 u (attract); `00a3` is `a1:114` of 134 runs (Viper II only); anchor classifies `00a3` as ~8 u/f, ~335 u homing missile | KNOWN |
| right | `00a1d44c` | `00a3xxxx` | 33 hits / ~4.6 u; side label `R` (10/…); also the top mount for the flash family `00bb` | LIKELY |
| left | `00a1d96b` | `00a3xxxx` + `009c` | 22 hits / ~2.4 u for `a3`; 59 hits for `009c`; side label center/left | LIKELY |
| — | `00a1c96d`, `00a1cd5d` | `009a` | `00a1c96d` 85 hits, but `009a` is mostly static/drift (249 static of 475) so this is an attached stream, not clearly ordnance | SPECULATIVE |

### Fei-Yen (`0xa8`)

| slot | mount part OBA(s) | candidate family | evidence | conf |
| --- | --- | --- | --- | --- |
| L/C/R | `00a8c353`, `00a8c4ae`, `00a8c62b` | `00a9` | 84 / 80 / 68 hits, median dist 1.4-1.9 u; `00a9` is `a8:275` of 279 runs (Fei-Yen only), 112 projectile; all three are on the second-mech body emitter base `0x504930` (`4960->00a8c353`, `493c->00a8c4ae`, `4990->00a8c62b`) | KNOWN |
| — | `00a8cb55`, `00a8b68e` | `00ab` | `00a8cb55` 24 hits / 2.3 u, `00a8b68e` 9 / 2.0 u; `00ab` mechfam `a8:48`, 22 projectile of 59 | LIKELY |
| — | `00a8ce01` | `009a` | 42 hits; `009a` static/drift | SPECULATIVE |

### Raiden (`0x9f`)

| slot | mount part OBA(s) | candidate family | evidence | conf |
| --- | --- | --- | --- | --- |
| C + pair | `009f8434`, `009f815c`, `009f8a2c` | `00a0` | `a0` is `9f:104` of 104 runs (Raiden only); 33 / 33 / 16 hits, median dist 3.7 / 3.6 / 22.2 u; `009f8a2c` is `009f` roster/texmap part `706350` | LIKELY |
| — | `009f7e06` | `0095`, `009a`, `00b2`, `00b3` | `009f7e06` is the top mount for many static families (62/104/38/30 hits, dist ~0); a part-attached emitter overlay, **not** ordnance | LIKELY |
| — | `009f8de0`, `009f8cd5` | `0091` | `0091` is a stage family that doubles as stage-launched effects; attribution to Raiden parts is via nearest-part only | SPECULATIVE |

### Bal-Bas-Bow (`0xad`)

| slot | mount part OBA(s) | candidate family | evidence | conf |
| --- | --- | --- | --- | --- |
| — | `00ad1379` | `008f` | 33 hits / 5.1 u; `008f` mechfam `ad:38` in attract; `008f` is mostly linger/static (impact/dust), not a travelling round | LIKELY |
| — | `00ad17af`, `00ad187e` | `009a` | 31 / 17 hits; `009a` static/drift | SPECULATIVE |
| — | `00ad2e45` | `00bb` | 136 hits / 4.8 u; `00bb` is the generic muzzle/impact family, **not** ordnance | LIKELY |
| — | `00ad1163`, `00ad2bc1` | `00af`, `00b0` | 30 / 15 hits at ~0.4-2.2 u; span-1 static part-attached effects | LIKELY |

### Apharmd (`0xa7`)

| slot | mount part OBA(s) | candidate family | evidence | conf |
| --- | --- | --- | --- | --- |
| — | `00a7ff39` | `008d` | 17 hits / 0.3 u (walk4); `008d` is 18 projectile of 64; `00a7ff39` is an in-battle-only part (absent from the 17-part roster list) | LIKELY |
| — | `00a7fcab`, `00a7f9b5` | `008f` | 52 / 28 hits; `008f` impact/dust linger, not ordnance | LIKELY |
| — | `00a7fbc8` | `0096`, `0091` | 62 / 39 hits; `0096` linger + some projectile, `0091` shared stage-launched | SPECULATIVE |

### Belgador (`0xa4`)

| slot | mount part OBA(s) | candidate family | evidence | conf |
| --- | --- | --- | --- | --- |
| — | `00a47a39`, `00a47c73` | `0081` | 20 / 13 hits, median dist 19.6-32.5 u (walk4); `0081` is largely a shared fast projectile/drift family, so this is a weak attribution | SPECULATIVE |
| — | `00a4661c`, `00a46507` | `0091` | 11 / 3 hits, ~412 u (attract) — likely a stage-launched effect, not the mech's own | SPECULATIVE |
| — | `00a45001`, `00a4542c`, `00a458e1`, `00a45c8b` | `00a5` | 16 / 8 / 8 / 8 hits, 3-5 u; `00a5` is `a4:42` of 42 runs, 36 linger — a Belgador part-attached linger effect, not ordnance | LIKELY |
| — | `00a46eac`, `00a47cdb`, `00a47299` | `00b7`; `00a47383`, `00a466a5` -> `00b8` | static span-1 effects coincident with parts, `a4`-only | LIKELY |

### Dorkas (`0xa6`)

Dorkas is barely present in the captures (registry notes it never fights in the
demo/mirror traces). Only weak single-capture attributions exist:

| slot | mount part OBA | candidate family | evidence | conf |
| --- | --- | --- | --- | --- |
| — | `00a66368` | `0086` / `00ab` | 2 / 4 hits; small, mixed families | SPECULATIVE |
| — | `00a63934` | `00b6` | 7 hits, shared static effect | SPECULATIVE |

### Summary of the highest-confidence rows

- **Viper II `00a1c5ac` -> `00a3xxxx` slow homing missile** (KNOWN; 50 hits at
  1.7 u; `00a3` is Viper-II-only).
- **Fei-Yen `00a8c353` / `00a8c4ae` / `00a8c62b` -> `00a9`** (KNOWN; 84/80/68
  hits at 1.4-1.9 u; parts are on the `0x504930` emitter map).
- **Temjin `009e3531`/`009e2853` -> `0099d57b` fast missile**, **`009e3c34`/
  `009e410d` -> `009b`**, **`009e3300`/`009e332f` -> `0098` fast beam**
  (LIKELY).

## 2. Non-mech, non-stage effect OBA families

Behaviour classes are the merged counts from
`attribute_weapon_effects.py` over the captures above
(`proj`/`ling`/`stat`/`drift` = contiguous spawn-run counts). "Ordnance" means
the family travels and is a fired round; "effect" means muzzle flash, impact,
explosion, thruster, or a part-attached overlay. Mech attribution is the
registry/emitter owner plus the capture's `mechfam` count.

### Ordnance / travelling families

| family | class (proj/ling/stat/drift) | ordnance? | per-mech attribution | conf |
| --- | --- | --- | --- | --- |
| `0098` | 63 / 92 / 88 / 17 | yes — fast shot / beam segment (~29 u/f, 4-5 f) | Temjin (`9e:230`) | KNOWN |
| `0099` | 89 / 3 / 10 / 2 | yes — fast projectile / missile (~58 u/f, up to 827 u) | Temjin (`9e:64`); `9f`/`a1`/`a8` are nearest-part noise | KNOWN |
| `009b` | 108 / 0 / 20 / 0 | yes — projectile | Temjin only (`9e:128`) | LIKELY |
| `0092` | 10 / 0 / 0 / 0 | yes — fast projectile (`009237e5`, ~59 u/f) | shared (single OBA; appears for Temjin/Fei-Yen/Viper II/Raiden/Belgador) | KNOWN |
| `00a3` | 60 / 3 / 25 / 46 | yes — slow homing missile (~8 u/f, ~335 u) | Viper II (`a1:114`); `9f` is noise | KNOWN |
| `00a9` | 112 / 58 / 40 / 69 | yes — projectile + linger | Fei-Yen (`a8:275`) | KNOWN |
| `00a0` | 40 / 0 / 64 / 0 | yes — projectile plus attached glow | Raiden only (`9f:104`) | LIKELY |
| `008d` | 18 / 6 / 2 / 38 | partly (18 projectile) — Apharmd/Temjin shot | Apharmd (`a7:20`), Temjin (`9e:26`) | LIKELY |
| `0081` | 393 / 31 / 0 / 292 | yes — fast projectile / drift stream | shared; mounts land on Fei-Yen (`00a8225c`), Temjin (`009e410d`), Belgador (`00a47a39`), Raiden (`009f8a2c`), Apharmd (`00a7ff90`) | LIKELY |
| `0091` | 235 / 5 / 2 / 9 | yes — shared/stage-launched rounds | stage family per registry; nearest-part attribution spans every mech with large distances, so **not** a clean per-mech weapon | LIKELY |
| `009a` | 43 / 50 / 249 / 133 | mostly effect — per-mech attached stream/thruster | Raiden (`009f7e06`), Viper II (`00a1c96d`), Fei-Yen (`00a8ce01`), Bal-Bas-Bow (`00ad17af`) | LIKELY |
| `009c` | 74 / 29 / 72 / 4 | mixed — Viper II projectile | Viper II (`a1:78`) + Temjin (`9e:65`) + Bal-Bas-Bow (`ad:26`) | SPECULATIVE |
| `0095` | 42 / 0 / 110 / 14 | partly — mostly attached effect | Raiden (`009f7e06`), Viper II (`00a1c96d`), Bal-Bas-Bow (`00ad17af`) | SPECULATIVE |
| `008f` | 84 / 353 / 205 / 23 | no — impact / dust / muzzle linger | shared: Temjin (`009e30ab`/`3300`/`5320`), Apharmd (`00a7fcab`), Bal-Bas-Bow (`00ad1379`), Fei-Yen (`00a80559`) | LIKELY |
| `0089` | 12 / 1 / 2 / 16 | yes — shared ordnance (registry) | shared; near Temjin (`009e43a8`), Apharmd (`00a7fdb6`), Viper II (`00a1cc84`) | KNOWN |
| `008a` | 11 / 1 / 3 / 10 | yes — shared ordnance in flight (registry) | shared; near Temjin (`009e2f5d`) | KNOWN |
| `0096` | 48 / 114 / 20 / 131 | mixed — some projectile, many effects | Apharmd (`00a7fbc8`), Temjin (`009e27fc`/`2f5d`), Fei-Yen (`00a809a6`) | SPECULATIVE |
| `0097` | 34 / 0 / 100 / 0 | mostly attached static effect | Temjin (`009e3531`), Fei-Yen (`00a8c7f1`) | SPECULATIVE |
| `0086` | 1 / 0 / 0 / 7 | effect/unknown | Fei-Yen (`00a8b2bf`), Temjin (`009e2ea2`), Dorkas (`00a66368`) | SPECULATIVE |
| `0087` | 0 / 1 / 1 / 3 | effect/unknown | Temjin (`009e343a`), Viper II (`00a1c429`), Apharmd (`00a7fdb6`) | SPECULATIVE |
| `0088` | 1 / 0 / 14 / 3 | effect — registry lists it as a mirror-only effect | Temjin (`009e343a`), Apharmd (`00a7fdb6`), Viper II (`00a1cc84`) | LIKELY |
| `008b` | 0 / 0 / 4 / 2 | effect | Belgador (`00a45ac8`), Viper II (`00a15c09`), Raiden (`009f8340`) | SPECULATIVE |
| `008c` | 3 / 6 / 1 / 7 | effect | Belgador (`00a45ac8`), Apharmd (`00a7f9b5`), Raiden (`009f8de0`) | SPECULATIVE |
| `00ab` | 22 / 10 / 0 / 27 | partly projectile | Fei-Yen (`a8:48`), Dorkas (`00a66368`) | LIKELY |
| `00aa` | 4 / 0 / 0 / 0 | projectile | Fei-Yen (`00a8b164`) | SPECULATIVE |
| `00ac` | 0 / 1 / 0 / 0 | effect | Fei-Yen (`00a8b68e`) | SPECULATIVE |

### Pure / part-attached effect families (not ordnance)

| family | class | behaviour | per-mech attribution | conf |
| --- | --- | --- | --- | --- |
| `00bb` | 385 / 1981 / 5327 / 1054 | generic muzzle flash / impact / explosion; anchor explicitly says NOT ordnance | shared: Temjin (`009e3c34`, `009e55bf`), Fei-Yen (`00a80559`, `00a809a6`), Viper II (`00a1d44c`, `00a1d96b`), Bal-Bas-Bow (`00ad2e45`), Raiden (`009f7e06`) | KNOWN |
| `00af` | 0 / 38 / 581 / 0 | span-1 part-attached overlay | Temjin (`009e55bf`/`332f`/`35b7`), Bal-Bas-Bow (`00ad1163`), Apharmd (`00a7f213`), Fei-Yen (`00a8b3b0`) | LIKELY |
| `00b0` | 0 / 19 / 294 / 0 | span-1 part-attached overlay | Temjin (`009e4fab`/`3ecf`/`3aa7`), Bal-Bas-Bow (`00ad2bc1`), Fei-Yen (`00a80559`), Apharmd (`00a7f213`) | LIKELY |
| `00b1` | 0 / 3 / 96 / 2 | span-1 part-attached overlay | Raiden (`009f7e06`), Viper II (`00a1c429`), Fei-Yen (`00a8e818`), Temjin (`009e332f`) | LIKELY |
| `00b2` | 0 / 0 / 75 / 0 | span-1 part-attached overlay | Raiden (`009f7e06`/`009fb22d`), Viper II (`00a1c429`) | LIKELY |
| `00b3` | 0 / 0 / 30 / 0 | span-1 part-attached overlay | Raiden (`009f7e06`) | LIKELY |
| `00b6` | 0 / 0 / 55 / 0 | span-1 part-attached overlay | Belgador (`00a45bdd`/`00a45c5c`), Dorkas (`00a63934`) | LIKELY |
| `00b7` | 0 / 0 / 85 / 0 | span-1 part-attached overlay | Belgador only (`00a46eac`/`00a47cdb`/`00a47299`/`00a472c8`) | LIKELY |
| `00b8` | 0 / 0 / 44 / 0 | span-1 part-attached overlay | Belgador only (`00a47383`/`00a466a5`/`00a46a62`) | LIKELY |
| `00a5` | 4 / 36 / 0 / 2 | Belgador linger effect (shield/anti-grav plume) | Belgador only (`a4:42`) | LIKELY |
| `009d` | 0 / 2 / 24 / 15 | attached static/drift effect | Temjin (`009e27fc`), Raiden (`009f7e06`) | SPECULATIVE |

### Families observed only as per-frame churn (no >=2-frame runs)

`008e`, `0094`, `00b9`, `00bc`, `009e5xxx` and the `009e6xxx-009efxxx`,
`00a4cxxx`, `00ad2xxx` / `00ad3xxx` suffix runs are per-frame OBA streams
(attack-animation or effect meshes): each frame submits a different OBA with a
4-byte tpa stride, so they never form a run. They are animation/effect assets,
not spawnable weapons. (`00ad0xxx` is the Bal-Bas-Bow base body, not a stream.)
`00ae` is an unmapped fighter-prefix family (present in the census, never with
accepted launches).

## 3. Static anchors and open gaps

- Temjin body-emitter map (KNOWN, `emitter-g2-oba.json`):
  `5046d0->009e410d`, `5046dc->009e35b7`, `5046e8->009e2ea2`,
  `5046f4->009e30ab`, `504700->009e343a`, `50470c->009e3588`,
  `504718->009e3531`, `504724->009e2f5d`, `504730->009e3300`,
  `50473c->009e3054`, `504748->009e332f`, `504754->009e2cb1`.
- Second-mech (Fei-Yen) body base `0x504930 -> 00a8xxxx` (KNOWN):
  `00a8ca04`, `00a8c4ae`, `00a8c5fc`, `00a8c519`, `00a8c353`, `00a8c786`,
  `00a8c848`, `00a8c7f1`, `00a8c62b`, `00a8bd4b`. Three of these
  (`00a8c4ae`, `00a8c353`, `00a8c62b`) are the `00a9` weapon mounts.
- Roster/select part lists and in-battle part lists differ: Temjin's roster
  model lacks `009e3531`, `009e2853`, `009e3054`, `009e27fc`, and the
  `009e5xxx` stream; those are exactly the battle-weapon candidates. Selection
  screens therefore cannot be used alone to enumerate mounts.
- Open: exact left/center/right slot assignment. The nearest-mount sides are
  camera-relative and noisy, so the L/C/R column above is SPECULATIVE. A
  decisive test is to de-rotate the mech root (or probe the SHARC transform for
  the mount's local matrix) and read the mount's local x-offset.
- Open: Dorkas, and Belgador/Apharmd/Bal-Bas-Bow ranged signatures, have too
  few accepted launches in the current captures. A per-mech joined firing
  capture (one mech, each of the three inputs) would promote the SPECULATIVE
  rows to KNOWN.
