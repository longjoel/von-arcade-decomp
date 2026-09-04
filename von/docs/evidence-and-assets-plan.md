# Reusable Trace Discovery and Convergence Plan

This playbook turns runtime traces into validated reconstructed behavior. It is
intended for the i960 attract milestone, but the process applies to another CPU,
subsystem, stimulus, or milestone by replacing the objective and checkpoints.

The central rule is that discovery and validation are different activities.
A whole-run PC set identifies territory. It cannot establish call edges,
function semantics, arguments, state transitions, or equivalence.

## 1. Define the objective before capturing

Every trace campaign starts with one observable objective and an ordered list
of checkpoints. A checkpoint must be testable from machine state or an event
stream, not from a source-code or annotation count.

For example:

```yaml
objective: c-only-i960-attract-60s
stimulus: input-free boot for 60 emulated seconds
checkpoints:
  - reset completes in generated code
  - hardware initialization reaches INIT
  - scheduler enters the attract state machine
  - legal/title presentation writes begin
  - audio command activity begins
  - geometry/video state changes for the duration
  - 60 seconds complete without exception or stall
  - every executed i960 PC belongs to generated code
```

Only the earliest failing checkpoint drives detailed discovery. Later
subsystems may be mapped opportunistically, but they do not enter the active
implementation queue.

## 2. Use two trace tiers

### Tier A: coverage sieve

Use the existing PC bitset for a cheap, whole-run inventory. Record:

- distinct visited instructions;
- approximate static function entries containing visited PCs;
- direct call sites and targets that were each visited;
- differences between phase-length captures;
- regions that are definitely outside the active stimulus.

The report must call these edges `possible_static_edges`, never `executed_edges`.
Both endpoints being present in a set does not prove that control flowed across
the edge. Edge counts are static candidate counts, not dynamic invocation
counts.

Tier A answers "where might the active code be?" It may create `discovered`
queue entries, but it cannot promote a work unit to `modeled`, `integrated`, or
`trace-validated`.

### Tier B: causal trace

Capture ordered events around the earliest failing checkpoint. Do not collect a
full 60-second instruction log by default. Bound it by time, phase, address
range, event count, or a trigger followed by a fixed-size window.

The minimum control-flow event is:

```json
{"seq":1842,"time":2.9167,"frame":175,"cpu":"maincpu","pc":"0x000187e4","next_pc":"0x0002b9e0","kind":"indirect-call","target":"0x0002b9e0"}
```

Record these event kinds where available:

- direct call;
- indirect call;
- return;
- exception or reset;
- watched RAM write;
- MMIO read/write;
- command/FIFO submission;
- checkpoint transition.

At function entry and exit, record only the registers and memory windows needed
by the current hypothesis. Avoid an unbounded register dump on every
instruction.

Tier B answers "what happened, in what order, with which state?"

## 3. Make every decisive capture reproducible

A capture used for integration or validation needs a sidecar manifest:

```json
{
  "schema_version": 1,
  "id": "i960-attract-scheduler-entry-v1",
  "objective": "c-only-i960-attract-60s",
  "hypothesis": "startup slot 1 advances the scheduler after status service completion",
  "expected_discriminator": "the indirect call returns with 0x005039f4 incremented",
  "stimulus": {"kind":"input-free-attract","seconds":8,"phase":"scheduler-entry"},
  "checkpoints": ["reset", "hardware-init", "scheduler-entry"],
  "configuration": {
    "set": "vonj",
    "mame_revision": "<commit>",
    "patch_profile": "<profile>",
    "execution_engine": "interpreter",
    "arguments": ["-video","none","-sound","none","-nothrottle"]
  },
  "command": ["mame", "vonj", "-video", "none", "-sound", "none",
    "-cfg_directory", "cfg", "-nvram_directory", "nvram",
    "-state_directory", "state", "-seconds_to_run", "8"],
  "isolation": {
    "cfg_directory": "cfg",
    "cfg_directory_sha256": "<sha256>",
    "nvram_directory": "nvram",
    "nvram_directory_sha256": "<sha256>",
    "state_directory": "state",
    "state_directory_sha256": "<sha256>"
  },
  "inputs": [
    {"path":"inputs/rom-manifest.json","sha256":"<sha256>"}
  ],
  "artifacts": [
    {"path":"events.ndjson.gz","sha256":"<sha256>"},
    {"path":"summary.json","sha256":"<sha256>"}
  ],
  "verifier": "von/tools/verify_<experiment>.py",
  "outcome": "pass"
}
```

Canonical runs use isolated configuration, NVRAM, state, and output
directories. Record the exact MAME revision, applied patch profile, execution
engine, ROM inventory hash, command line, stimulus, duration, and artifact
hashes. A file in an ignored build directory is working evidence, not canonical
evidence, until it is registered in `von/evidence/manifest.json`.

## 4. Compare phases before opening work

Keep short, deterministic phase captures so the whole-run set can be
partitioned:

1. reset to first hardware access;
2. startup through INIT;
3. INIT through scheduler entry;
4. first legal/title frame;
5. stable attract loop;
6. later stimulus-specific phases.

For each phase, compare original and reconstructed execution:

- checkpoint reached or missed;
- last matching ordered event;
- first divergent event;
- dynamic caller and target;
- relevant input state;
- relevant output state or side effect.

The first divergence becomes the active experiment. A longer trace is useful
only when the short trace cannot discriminate the hypothesis.

## 5. Triage by causal proximity

Rank candidates using this order:

1. On the dynamic path to the earliest failed checkpoint.
2. Direct producer of the first mismatching RAM/MMIO/FIFO event.
3. Required dependency of that producer.
4. Confirmed indirect target on that path.
5. Repeatedly executed nearby helper.
6. Static or coverage-only candidate.

Address order is not a priority model. Static caller count is useful as a
secondary estimate of reuse, but it is not dynamic frequency.

Each queue item records:

```yaml
id: maincpu.example-service
objective: c-only-i960-attract-60s
checkpoint: scheduler enters attract
status: discovered
confidence:
  entry: observed
  caller: dynamically-observed
  boundary: statically-proven
  semantics: hypothesis
hypothesis: <one falsifiable statement>
expected_discriminator: <specific event or state difference>
dependencies: []
evidence_ids: []
owner: unassigned
```

Confidence applies independently to entry, caller, boundary, and semantics.
An observed entry must not silently make a semantic name "observed."

## 6. Run one bounded work-unit loop

Limit active work to one integration unit and at most one supporting evidence
experiment. Finish or explicitly block them before opening another modeled
unit.

1. Select the earliest causal candidate.
2. State one hypothesis and its discriminating result.
3. Prove the entry, callers, exits, and relevant data references.
4. Capture a bounded original event/state fixture.
5. Implement readable production C against an explicit hardware boundary.
6. Add a focused deterministic unit or contract test.
7. Link the routine into the replacement image.
8. Capture the same events from the reconstructed image.
9. Compare ordered effects and rerun every earlier checkpoint.
10. Register canonical evidence and update the ledger in the same change.

If the experiment does not change confidence, implementation, queue order, or
a verifier, quarantine it and revise the hypothesis before collecting more
data.

## 7. Enforce lifecycle gates

Use these minimum promotion requirements:

| Stage | Required evidence |
| --- | --- |
| `planned` | Stable ID and reason the unit may matter. |
| `modeled` | Proven boundary, readable C semantics, focused passing test, and explicit unresolved behavior. |
| `integrated` | Generated image links and invokes the implementation on the target path; earlier smoke checkpoints still pass. |
| `trace-validated` | Original and reconstructed ordered effects match for a registered canonical stimulus; verifier passes. |
| `byte-validated` | Reproducible byte comparison matches the declared original range. |
| `blocked` | Named missing fact, failed discriminator, and the smallest next experiment needed to unblock it. |

The ledger validator should reject:

- `integrated` without an integration test/checkpoint reference;
- `trace-validated` without a canonical evidence ID and verifier;
- an evidence path used as if it were an evidence ID;
- milestone membership based only on Tier A coverage;
- stale generated status or worklist files.

## 8. Measure yield, not motion

Generate these metrics for each discovery cohort and objective:

- discovered, modeled, integrated, and trace-validated counts;
- conversion percentage between each stage;
- median age and oldest item at each stage;
- active modeled work-in-progress count;
- checkpoints passed;
- number of original/reconstructed events compared;
- confirmed versus possible dynamic edges;
- experiments that changed a decision versus quarantined experiments;
- newly discovered targets from indirect calls.

Annotation count, documentation lines, test-vector count, and visited-byte count
are supporting measurements. They are not delivery progress.

A useful weekly review asks:

1. Which checkpoint advanced?
2. Which first divergence was removed or narrowed?
3. Which work unit moved to integrated or trace-validated?
4. Which evidence is now canonical and rerunnable?
5. Did the queue shrink faster than discovery expanded it?

If none changed, pause broad discovery.

## 9. Migrate the current attract crawler

Apply the process in this order so existing evidence remains usable:

### Phase 1: correct terminology and provenance

- Rename `executed_direct_edges` to `possible_static_edges` in the coverage
  schema and reports.
- Label direct targets as observed entries, not observed invocations from every
  listed caller.
- Add capture identity and isolated cfg/NVRAM directories.
- Require a non-empty ordered checkpoint list, hypothesis, and expected
  discriminator in each capture sidecar; preserve the phase and sidecar hash
  when registering canonical evidence.
- Register the canonical 60-second coverage artifact or explicitly classify it
  as a noncanonical discovery input.
- Add analyzer and worklist regression tests.

### Phase 2: capture causality

- Add bounded ordered call, indirect-call, return, exception, and checkpoint
  events to the MAME debug instrumentation.
- Add address filters, trigger conditions, and maximum event counts.
- Emit NDJSON for streaming and a compact JSON summary for review.
- Resolve indirect dispatch tables from observed targets.

### Phase 3: compare original and reconstruction

- Define stable checkpoint events and watched state fields.
- Add a tool that identifies the last matching and first divergent event.
- Store small deterministic fixtures in Git; store hashed raw streams in the
  evidence blob area.
- Make the attract test print the first divergence rather than only pass/fail.

### Phase 4: enforce convergence

- Extend ledger validation with stage-specific evidence requirements.
- Generate the queue from checkpoint distance and dynamic dependencies.
- Set modeled WIP to one active unit.
- Regenerate status and worklist outputs as a required clean-tree check.

### Phase 5: pilot before scaling

Use one known startup-to-scheduler boundary as the pilot. The migration is
successful when the process:

1. reproduces the original event sequence;
2. identifies one causal divergence in the reconstructed run;
3. guides one implementation change;
4. promotes that unit through integration and trace validation;
5. reruns from a clean capture configuration with identical verifier results.

Only then apply the causal tracer to later attract or match phases.

## 10. Stop conditions

Stop a discovery run when any of these occurs:

- its stated discriminator has been observed;
- the maximum event or emulated-time bound is reached;
- the trace repeats without adding a new state or edge;
- the capture configuration differs from the declared manifest;
- an earlier checkpoint fails;
- the output cannot be consumed by a verifier or an active work unit.

Stop the campaign when all objective checkpoints pass under isolated,
canonical reproduction and every executed reconstructed PC is within the
approved generated-code boundary. Unrelated ROM understanding remains future
research rather than silently expanding the milestone.

## 11. Clean up from a zero-trust baseline

Assume all existing captures, generated assets, status labels, and derived
documentation are stale until a current producer and verifier reproduce them.
Do not interpret `verified`, `proven`, `authoritative`, or a green UI label in
an old manifest as evidence by itself.

Cleanup begins with an inventory, not deletion. Generate a machine-readable
record for every relevant file containing:

```json
{
  "path": "von/captures/example/output.trace",
  "bytes": 1234,
  "sha256": "<sha256>",
  "tracked": false,
  "producer": "scripts/example-capture.sh",
  "consumers": ["von/tools/example_analyzer.py"],
  "classification": "scratch",
  "decision": "delete-after-review"
}
```

Use five cleanup classes:

| Class | Treatment |
| --- | --- |
| Source and tests | Keep when currently invoked and passing. Consolidate duplicates after consumer analysis. |
| Canonical evidence | Keep a compact fixture in Git or a hashed blob in the evidence store, with manifest and verifier. |
| Reproducible generated output | Remove from source control and regenerate on demand. Keep the recipe and hashes. |
| Legacy or ambiguous output | Move to a dated quarantine index; do not expose it as validated. |
| Private ROM material | Keep ignored and local. Never copy it into a distributable package. |

### Cleanup sequence

1. Freeze the current filesystem inventory and hashes so later provenance
   questions can be answered without retaining every duplicate.
2. Build a producer/consumer graph for scripts, fixtures, manifests, captures,
   models, textures, and audio files.
3. Mark every old asset and capture `legacy-unreviewed` regardless of its old
   label.
4. Deduplicate exact content by SHA-256. Retain the canonical path plus aliases
   in the inventory rather than multiple large copies.
5. Compress canonical raw logs into a content-addressed evidence directory.
6. Remove reproducible build products and failed exploratory captures only
   from an explicit dry-run deletion manifest.
7. Consolidate capture entry points behind one CLI with named scenarios and
   patch profiles. Keep thin compatibility wrappers only while callers remain.
8. Consolidate analyzers that parse the same log grammar and fixtures that
   encode the same observation.
9. Move obsolete narrative snapshots into a legacy archive or replace them
   with generated current reports. Avoid keeping conflicting "current"
   sections in multiple documents.
10. Split the dirty worktree into small commits by concern: evidence schema,
    capture tooling, recovered code, tests, and documentation. Never bulk-reset
    unknown work.
11. Regenerate status/worklists and require a clean regeneration diff in CI.
12. Run unit, contract, trace, smoke, and milestone gates before declaring the
    cleanup baseline complete.

The cleanup report should show bytes retained, compressed, quarantined, and
eligible for deletion. Size reduction is useful, but the primary success
condition is that every retained artifact has a known producer, consumer, and
evidence status.

### What not to preserve as truth

- Existing viewer manifest status labels.
- A model identity established only by visual resemblance.
- A geometry assembly established only by timestamp proximity.
- A WAV called "reconstructed" without an output comparison.
- Trace logs lacking capture configuration and hashes.
- Generated status copied into prose.
- A test count without a current result tied to the test-manifest digest.

## 12. Produce validated multimodal asset packs

The showcase boundary is a new generated evidence pack, not a directory of
loose files and not the legacy viewer manifest. Packs are local products built
from private ROMs and canonical traces. The repository may contain schemas,
tools, compact evidence, and noninfringing test fixtures; derived game media
remains ignored unless its redistribution status is resolved separately.

Use one status vocabulary for every media type:

| Status | Meaning |
| --- | --- |
| `legacy-unreviewed` | Predates the current pipeline or lacks reproducible evidence. |
| `candidate` | Parses or renders, but one or more source/association claims remain open. |
| `observed` | Present in a canonical original execution, with source event recorded. |
| `validated` | Reproducibly regenerated and passed every required modality-specific verifier. |
| `rejected` | Failed a named check; retained only when useful for regression or diagnosis. |
| `reference-capture` | Direct MAME audio/video output; authoritative as an observation, not as a reconstructed asset. |

Validation is claim-specific. An asset can have validated geometry extraction
while its identity, hierarchy, textures, or animation remain candidate. The
pack must expose those claims separately instead of collapsing them into one
ambiguous badge.

### Pack manifest

Each pack has a canonical JSON manifest similar to:

```json
{
  "schema_version": 1,
  "kind": "von-evidence-asset-pack",
  "id": "vonj-player-select-pilot-v1",
  "basis": {
    "romset_hash": "<sha256>",
    "map_revision": "<revision>",
    "capture_id": "<canonical-evidence-id>",
    "tool_revision": "<revision>"
  },
  "assets": [
    {
      "id": "fighter-assembly-001",
      "media_type": "model",
      "status": "validated",
      "payload": "payloads/fighter-assembly-001.glb",
      "sha256": "<sha256>",
      "claims": {
        "geometry": "validated",
        "source_ranges": "validated",
        "transform_association": "validated",
        "identity": "candidate",
        "textures": "candidate",
        "hierarchy": "candidate",
        "animation": "candidate"
      },
      "evidence_ids": ["<canonical-evidence-id>"],
      "verifiers": ["<verifier-id>"]
    }
  ]
}
```

The pack validator checks schema, payload hashes, source ROM identity,
capture identity, tool revision, canonical evidence IDs, and verifier results.
The viewer must consume validator output; it must not assign validation status.

### Geometry and texture gates

A model may claim validated geometry only when all of these pass:

1. Exact private-ROM identity and physical source ranges are recorded.
2. The decoder deterministically re-extracts the same topology and attributes.
3. Object submissions and OBAs are present in a canonical ordered trace.
4. Matrix/object association uses ordered sequence identity, not timestamp
   proximity.
5. Vertex, index, attribute, and source-window hashes match the pack manifest.
6. A reference-frame verifier compares transformed bounds, part count, draw
   order, and a rendered image or raster observations within declared
   tolerances.

Texture validation additionally requires traced header and palette state,
source-range hashes, decoded image hashes, UV/material association, and a
reference pixel or image comparison. A visually convincing textured model
without those checks remains a candidate.

Hierarchy and animation are independent claims. A flat sequence of validated
per-part transforms may be shown as validated motion even while a proposed
parent/child rig remains candidate. Promote hierarchy only after pointer or
equivalent causal provenance is captured.

### Audio gates

Treat audio as three different products:

1. **Reference recordings.** WAV output captured directly from MAME. Label it
   `reference-capture`; store capture configuration, phase timestamps, and
   hashes. It is evidence of heard output, not an independent reconstruction.
2. **Descriptor-validated samples.** Individual PCM windows whose SA/LSA/LEA,
   PCM format, rate, loop mode, and key-on event come from a canonical runtime
   register trace. Verify exact extracted PCM bytes and WAV metadata. Clip
   identity or musical purpose can remain candidate.
3. **Validated sequences or music.** A reconstructed timeline whose key-on and
   key-off order, slots, pitch changes, loop behavior, attenuation, pan,
   envelope, routing, and DSP effects match the original event stream and
   whose rendered output passes declared alignment, duration, RMS, spectral,
   and correlation thresholds.

The current offline music renderer must be treated as candidate while DSP and
envelope behavior are approximate. It can be showcased beside its MAME
reference with a visible `provisional reconstruction` label, but not promoted
to validated audio.

The first audio promotion target should be a small descriptor-validated sample
set, not a complete song. It gives the pack and viewer a rigorous audio path
without pretending the sequencer and DSP are solved.

## 13. Make `von-viewer` an evidence showcase

Keep its folder-backed loose-file mode for inspection, but add a distinct
pack mode. Loose files always begin as `legacy-unreviewed` or `candidate`.
Only a successfully verified pack can populate the validated showcase.

### Backend responsibilities

- Recursively discover `pack.json` and optional per-asset sidecars.
- Validate manifests and payload hashes before returning assets.
- Return validation claims, evidence IDs, capture identity, tool revision, and
  verifier results through `/api/assets`.
- Stream large GLB and WAV payloads with HTTP range support.
- Expose validation failures rather than silently omitting or promoting files.
- Watch or refresh a generated pack directory without writing into it.
- Default to local-only binding and never expose the private ROM directory.

### Viewer layout

Retain the half-viewer, half-form workspace. Add media-aware modes:

- **Models:** 3D view, part tree, source OBA/ranges, transform sequence,
  topology counts, material/texture claims, and reference-frame comparison.
- **Audio:** native playback, waveform, optional spectrogram, loop markers,
  sample rate/channels, SA/LSA/LEA, slot and routing values, and chronological
  event timeline.
- **Evidence:** capture manifest, payload/source hashes, verifier results,
  unresolved claims, and links to compact evidence summaries.

The default collection view shows validated assets and reference captures.
Candidates, rejected items, and legacy files require explicit filters. Badges
must be claim-specific: for example, `GEOMETRY VALIDATED`, `IDENTITY
CANDIDATE`, and `ANIMATION UNRESOLVED` may appear together.

Keep copy/paste useful throughout:

- copy complete asset or evidence JSON;
- copy individual transform, OBA, source range, hash, sample descriptor, or
  event values;
- paste viewer transforms without mutating evidence claims;
- paste a pack or evidence ID to navigate directly to it;
- export a review note as a separate local overlay, never by editing the
  signed/generated evidence manifest.

For a scenario containing both model motion and audio, provide a synchronized
timeline only after both streams share the same canonical capture clock.
Before then, present them as separate assets rather than implying sync.

## 14. Cleanup and showcase rollout

Implement the combined plan in this order:

### Milestone A: quarantine and inventory

- Generate the filesystem and producer/consumer inventory.
- Reclassify all existing viewer assets and manifests as
  `legacy-unreviewed`.
- Identify exact duplicate captures and generated media.
- Produce a reviewed, dry-run cleanup manifest. Do not delete automatically.

Exit condition: every large capture and displayed asset has an owner,
producer, consumer, hash, and disposition.

### Milestone B: pack schema and verifier

- Add `von-evidence-asset-pack` schema and validation CLI.
- Connect it to canonical evidence IDs and private-ROM audit hashes.
- Add corrupt hash, stale tool, missing evidence, and unsupported-claim tests.

Exit condition: invalid or stale packs cannot appear validated.

### Milestone C: one geometry pilot

- Select one small, stable traced object rather than a whole fighter.
- Recapture it canonically with ordered submission and transform identity.
- Re-extract, hash, render-compare, package, and verify it.

Exit condition: a clean machine with the private ROM set can reproduce the
same verified pack and payload hashes.

### Milestone D: one audio pilot

- Recapture one SCSP key-on and complete slot descriptor canonically.
- Extract the exact sample window and verify PCM/WAV hashes and metadata.
- Package the descriptor, WAV, event excerpt, and verifier result.

Exit condition: `von-viewer` plays the sample and shows why its descriptor and
bytes are validated, without claiming a semantic name or complete music path.

### Milestone E: viewer pack mode

- Add validated pack discovery, model/audio/evidence panels, range streaming,
  claim badges, filters, and copy/paste affordances.
- Keep loose-folder inspection clearly separated from validated showcase mode.

Exit condition: a deliberately corrupted payload is rejected, a candidate is
visibly distinct, and both pilot assets are inspectable from their evidence to
their rendered or audible output.

### Milestone F: scale deliberately

- Promote additional static models, then textures, flat transform animation,
  proven hierarchy, audio samples, sequences, and finally reconstructed music.
- Add only one new claim class after its verifier and viewer presentation are
  complete.
- Delete or archive superseded legacy outputs using the reviewed cleanup
  manifest.

Exit condition: showcase growth corresponds to validated claims rather than a
larger loose-file collection.
