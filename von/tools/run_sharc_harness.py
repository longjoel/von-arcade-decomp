#!/usr/bin/env python3
"""Run the isolated SHARC handler harness and judge trials against goldens.

Design (see von/tools/sharc_harness.lua): one MAME boot executes every
trial in --spec. The attract-mode i960 keeps a constant background stream
of idempotent init words on the shared COP FIFO, so a single boot's DM
diff mixes background churn with injection effects. The wrapper therefore
runs THREE boots -- two injected, one no-inject baseline with the same
trial count -- and keeps only per-address effects that agree across both
injected runs and differ from the baseline:

    effect(addr) <=> postA(addr) == postB(addr) != postBase(addr)

Frames are never compared (attract timing dependent). A trial whose two
injected runs disagree is UNSTABLE (a foreign real command landed
mid-trial) and fails closed.

Usage:
  run_sharc_harness.py --spec "08;00:3f800000,40000000" [--goldens ...]
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAME_BIN = Path(os.environ.get("VON_MAME_BIN", ROOT / "bin/von"))
ROMPATH = ROOT / "von/build/disasm/rompath"
HARNESS_LUA = ROOT / "von/tools/sharc_harness.lua"
LISTING = ROOT / "von/build/disasm/vonj-sharc-bootstrap.lst"
DEFAULT_GOLDENS = ROOT / "von/tools/sharc_harness_goldens.json"

BASELINE_OP = "fe"


def trial_count(spec: str) -> int:
    return sum(1 for item in spec.split(";") if item.strip())


def run_boot(spec: str, tag: str, settle: int, run_frames: int) -> Path:
    log_path = Path(f"/tmp/sharc_harness_{os.getpid()}_{tag}.jsonl")
    oslog_path = Path(f"/tmp/sharc_harness_{os.getpid()}_{tag}.oslog")
    env = dict(os.environ)
    env["SDL_VIDEODRIVER"] = "dummy"
    env["SDL_AUDIODRIVER"] = "dummy"
    env["VON_SHARC_OPCODES"] = spec
    env["VON_SHARC_LOG"] = str(log_path)
    env["VON_SHARC_SETTLE_FRAMES"] = str(settle)
    env["VON_SHARC_RUN_FRAMES"] = str(run_frames)
    trials = trial_count(spec)
    cmd = [str(MAME_BIN), "vonj", "-rompath", str(ROMPATH),
           "-video", "none", "-sound", "none", "-oslog",
           "-autoboot_script", str(HARNESS_LUA),
           "-seconds_to_run",
           str((settle + run_frames * trials + 1800) // 60 + 5),
           "-skip_gameinfo", "-nothrottle"]
    with oslog_path.open("w", encoding="utf-8") as sink:
        proc = subprocess.run(cmd, stdout=sink, stderr=subprocess.STDOUT,
                              env=env, timeout=1200)
    print(f"[{tag}] mame_exit={proc.returncode} spec={spec!r}")
    return log_path


def load_trials(log_path: Path) -> tuple[list[dict], list[str]]:
    trials, problems = [], []
    if not log_path.exists():
        return trials, ["missing harness log"]
    for line in log_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            problems.append(f"unparsable log line: {line[:80]}")
            continue
        if obj.get("type") == "trial":
            trials.append(obj)
        elif obj.get("type") == "abort":
            problems.append(f"harness abort: {obj}")
    return trials, problems


def post_map(trial: dict) -> dict[int, str]:
    """Flatten post-snapshot blobs to {dm_address: hex_word}."""
    out: dict[int, str] = {}
    for blob in trial.get("post", []):
        base_s, _, hexdata = blob.partition(":")
        base = int(base_s, 16)
        for i in range(0, len(hexdata), 8):
            out[base + i // 8] = hexdata[i:i + 8]
    return out


def flag_wait_slots() -> set[int]:
    """PM addresses whose listing line is a FLAG-input self-loop wait."""
    slots: set[int] = set()
    lines = LISTING.read_text(encoding="utf-8").splitlines()
    body_by_slot = {}
    for line in lines:
        if ":" not in line:
            continue
        slot, body = line.split(":", 1)
        if len(slot) == 3 and all(c in "0123456789abcdef" for c in slot):
            body_by_slot[slot] = body
    for slot, body in body_by_slot.items():
        for flag in ("FLAG0_IN", "FLAG1_IN"):
            if flag in body and f"JUMP (0x00020{slot.upper()})" in body.replace(" ", ""):
                slots.add(0x20000 + int(slot, 16))
    return slots


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--goldens", default=str(DEFAULT_GOLDENS))
    ap.add_argument("--out", default=None)
    ap.add_argument("--settle", type=int, default=400)
    ap.add_argument("--run-frames", type=int, default=600)
    ap.add_argument("--no-judge", action="store_true")
    args = ap.parse_args()

    n = trial_count(args.spec)
    base_spec = ";".join([BASELINE_OP] * n)
    log_a = run_boot(args.spec, "injA", args.settle, args.run_frames)
    log_b = run_boot(args.spec, "injB", args.settle, args.run_frames)
    log_base = run_boot(base_spec, "base", args.settle, args.run_frames)

    trials_a, prob_a = load_trials(log_a)
    trials_b, prob_b = load_trials(log_b)
    trials_base, prob_base = load_trials(log_base)
    problems = prob_a + prob_b + prob_base
    waits = flag_wait_slots()

    goldens: dict = {}
    if not args.no_judge:
        goldens = json.loads(Path(args.goldens).read_text(encoding="utf-8"))

    verdicts = []
    ok_counts = {"agree": 0, "trials": 0}
    for i in range(n):
        ok_counts["trials"] += 1
        if i >= len(trials_a) or i >= len(trials_b) or i >= len(trials_base):
            verdicts.append({"index": i, "verdict": "MISSING",
                             "note": "harness emitted fewer trials than spec"})
            continue
        t_a, t_b, t_base = trials_a[i], trials_b[i], trials_base[i]
        opcode = t_a.get("opcode", "??")
        post_a, post_b, post_base = (post_map(t) for t in (t_a, t_b, t_base))
        effects: dict[str, str] = {}
        unstable: list[str] = []
        for addr in post_a.keys() | post_b.keys():
            va, vb = post_a.get(addr), post_b.get(addr)
            if va != vb:
                unstable.append(f"{addr:05x}")
            elif va != post_base.get(addr):
                effects[f"{addr:05x}"] = f"{post_base.get(addr)}->{va}"
        verdict: dict = {"index": i, "opcode": opcode,
                         "outcome_a": t_a.get("outcome"),
                         "outcome_b": t_b.get("outcome"),
                         "effect_count": len(effects), "effects": effects}
        if t_a.get("outcome") != t_b.get("outcome"):
            verdict["verdict"] = "UNSTABLE"
            verdict["note"] = "outcomes disagree across injected runs"
        elif unstable:
            verdict["verdict"] = "UNSTABLE"
            verdict["note"] = (f"{len(unstable)} addresses disagree across "
                               f"injected runs (e.g. {unstable[:5]})")
        else:
            ok_counts["agree"] += 1
            outcome = t_a.get("outcome", "")
            if outcome.startswith("blocked-"):
                pc = int(outcome.split("-")[1], 16)
                verdict["blocked_pc_in_flag_wait"] = pc in waits
            golden = goldens.get(opcode)
            scoped_out = False
            if golden is not None and "only_when_preceded_by" in golden:
                prev = verdicts[-1].get("opcode") if verdicts else None
                if prev not in golden["only_when_preceded_by"]:
                    scoped_out = True
                    verdict["verdict"] = "UNJUDGED"
                    verdict["note"] = (f"golden scoped to specs preceded by "
                                       f"{golden['only_when_preceded_by']}")
            if golden is None or scoped_out:
                if "verdict" not in verdict:
                    verdict["verdict"] = "UNJUDGED"
            else:
                failures = []
                if outcome != golden.get("outcome"):
                    failures.append(
                        f"outcome {outcome} != {golden.get('outcome')}")
                if golden.get("effects_empty") and effects:
                    failures.append(f"expected no effects, got {len(effects)}")
                if golden.get("effects_exact") is not None:
                    if effects != golden["effects_exact"]:
                        failures.append("effects differ from golden")
                need_drain = golden.get("drain_must_contain")
                if need_drain is not None:
                    drain = t_a.get("drain") or []
                    if isinstance(drain, str):
                        drain = []
                    missing = [w for w in need_drain if w not in drain]
                    if missing:
                        failures.append(
                            f"drain missing {missing} (got {drain})")
                verdict["verdict"] = "PASS" if not failures else "FAIL"
                verdict["failures"] = failures
        verdicts.append(verdict)

    report = {"spec": args.spec, "agreement": ok_counts,
              "problems": problems, "verdicts": verdicts}
    if args.out:
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=1), encoding="utf-8")
        print(f"report: {out_path}")
    for verdict in verdicts:
        print(f"trial {verdict['index']} opcode {verdict.get('opcode')}: "
              f"{verdict['verdict']} outcomes={verdict.get('outcome_a')}/"
              f"{verdict.get('outcome_b')} effects={verdict.get('effect_count')}")
        for failure in verdict.get("failures", []):
            print(f"    - {failure}")
        if verdict.get("note"):
            print(f"    note: {verdict['note']}")
    if problems:
        print(f"harness problems: {problems}")
    print(f"run agreement: {ok_counts['agree']}/{ok_counts['trials']}")
    if problems and not verdicts:
        return 2
    if any(v["verdict"] in ("FAIL", "UNSTABLE", "MISSING") for v in verdicts):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
