# Advisory JEV trace triage

JEV may rank locally generated candidates for the first difference between two
bounded ordered-event streams. It is a discovery aid, not a trace parser or an
evidence verifier. Its output must not promote a reconstruction ledger entry or
replace an original/reconstructed deterministic comparison.

## Prepare and inspect a dossier

Preparation is offline and writes beneath the ignored build tree by default:

```sh
./bin/vonctl trace jev-triage --prepare \
  --original <original.ndjson> \
  --reconstructed <reconstructed.ndjson> \
  --disassembly von/build/disasm/vonj-maincpu.lst \
  --annotation von/i960/symbols.md \
  --annotation von/i960/disassembly-annotations.md \
  --ledger von/reconstruction_ledger.json
```

The tool finds the first ordered-event divergence, generates address candidates
from its dynamic context, and adds bounded event and disassembly windows. The
default state limit is 80,000 UTF-8 bytes, conservatively below JEV's 32K-token
context after allowing for the questions. Oversize inputs fail; they are never
silently truncated.

## Submit through OpenRouter

OpenRouter is the default provider and the benchmark model is pinned to
`typesafe/jev-1.13`:

```sh
./bin/vonctl trace jev-triage --submit \
  --original <original.ndjson> \
  --reconstructed <reconstructed.ndjson> \
  --disassembly von/build/disasm/vonj-maincpu.lst \
  --env-file /home/longjoel/Work/von-godot/.env.local
```

The explicit env file must contain `OPENROUTER_API_KEY`. The command does not
search sibling repositories, and reports never contain the key. Use
`--provider typesafe` with `TYPESAFE_API_KEY` for the direct API. Network calls
are opt-in; the normal test suites remain offline.

Every run preserves `dossier.json`, `request.json`, `response.json`, and
`report.json`. Replay a saved response without spending credits:

```sh
./bin/vonctl trace jev-triage --replay <response.json> \
  --dossier <dossier.json> --output-dir <output-directory>
```

Reports abstain when evidence sufficiency is below `0.5`, no candidate reaches
`0.55` support, or the top two candidates are separated by less than `0.10`.

## Benchmark before routine use

Benchmark manifests point at saved reports and keep confirmed answers outside
the submitted dossier:

```json
{
  "schema_version": 1,
  "cases": [
    {
      "id": "scheduler-first-divergence",
      "expected_addresses": ["0x0002b9e0"],
      "baseline_ranked_addresses": ["0x000187e4", "0x0002b9e0"],
      "reports": ["run-1/report.json", "run-2/report.json", "run-3/report.json"]
    }
  ]
}
```

Run the offline scorer with:

```sh
./bin/vonctl trace jev-benchmark <benchmark.json> \
  --root <report-root> --output <benchmark-report.json>
```

Recommendation requires at least 20 real resolved cases, top-three recall no
worse than the deterministic baseline, a 10% mean-reciprocal-rank improvement,
at most 10% high-confidence errors, and 90% stable top choices over three runs.
The repository does not yet contain enough canonical ordered-event pairs to
meet the 20-case gate; do not synthesize labels to satisfy it.
