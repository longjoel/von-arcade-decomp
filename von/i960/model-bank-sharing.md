# Model bank sharing (0xC9100 directory)

The i960 program image holds a 10-entry model directory at `0xC9100`, one entry
per roster slot (roster order). Each entry is `[range_end, range_start,
struct_a, aux0, struct_b, aux1]`, all `0x02xxxxxx` main-data pointers.

## Fighters share asset banks

Grouping the 10 entries by their four bank pointers gives four groups:

| group | fighters | struct_a | struct_b |
| --- | --- | --- | --- |
| A | TEMJIN, VIPER2, **APHARMD** | `0x021a48f0` | `0x021bbfc8` |
| B | BELGDOR, RAIDEN, DORKAS | `0x025fb254` | `0x02610ddc` |
| C | FEIYEN, JAGUARANDI | `0x02941144` | `0x0295a7b4` |
| D | BAL-BAS-BOW, Z-GRADT | `0x02a90e64` | `0x02ab50bc` |

So **Apharmd borrows Temjin's (and Viper2's) model asset bank** — the user's
hypothesis. The bank body (`struct_a` at `0x021a48f0`) is packed float/vertex
data (04xx/3xxx/bfxx patterns), i.e. shared polygon geometry, not a part list.

## OBA prefixes are not fighter ids

- Shared-prefix parts reused across families: `0086aca1`, `008964ba`,
  `008ad656`. `008964ba`/`008ad656` appear in both Temjin's and Apharmd's model
  segments (Temjin's rig tree chains them too).
- Temjin's profile part-groups reference `0x009f...` parts (`009f594d`,
  `009f5cc4`, `009f603b`) — the nominal Raiden prefix.
- Apharmd's own parts span `0x00a7` (arms/torso) and `0x00a8` (legs), and its
  runtime legs carry `tpa` `0x001208fa..0x00120f72`, contiguous with its torso
  parts (`tpa` `0x00120000+`) — one runtime allocation, not FeiYen's
  (`tpa` `0x0012a...`).

Consequence: a fighter cannot be identified by `oba >> 16`. The kernel/test
invariant is instead "the clip covers every node of the fighter's staged
model".

## Why the offline extractor under-reports parts

`extract_fighter.py:model_tables` scans one region and keeps the **longest**
segment per OBA-prefix. For Apharmd that yields 8 parts (`0xa7`), but the walk4
capture renders **17** (the extra leg chain `a803e0..a80b83` plus `a7f213`).
The directory `directory_parts` adds two more (10 total), and profile
part-groups add `a8009b`. The runtime model is assembled from all of these
plus the shared bank, so no single table lists the full set.

Evidence commands:
- bank grouping: `model_directory(maincpu)` in `von/tools/extract_fighter.py`
- rigidity check (walk4 is one body): `von/tools/bake_fighter_animation.py`
  inference; relative-offset stdev from torso grows down each leg chain
  (upper leg ~0.2-0.8, foot ~3-5) — articulated limbs, not a second mech.
