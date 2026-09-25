#!/usr/bin/env python3
"""Offline contract tests for advisory JEV trace triage."""

from __future__ import annotations

import io
import json
import os
import sys
import tempfile
import urllib.error
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))

from jev_trace_triage import (  # noqa: E402
    build_dossier,
    build_request,
    canonical_bytes,
    make_report,
    parse_env_file,
    post_json,
    provider_settings,
)


def write_events(path: Path, values: list[int]) -> None:
    events = [
        {"seq": 0, "time": 0.0, "frame": 0, "cpu": "maincpu",
         "kind": "checkpoint", "name": "reset"},
        {"seq": 1, "time": 0.1, "frame": 1, "cpu": "maincpu",
         "kind": "direct-call", "pc": "0x1000", "next_pc": "0x2000", "target": "0x2000"},
        {"seq": 2, "time": 0.2, "frame": 2, "cpu": "maincpu",
         "kind": "mmio-write", "address": "0x3000", "value": values[0]},
        {"seq": 3, "time": 0.3, "frame": 3, "cpu": "maincpu",
         "kind": "checkpoint", "name": "scheduler"},
    ]
    path.write_text("".join(json.dumps(event) + "\n" for event in events), encoding="utf-8")


def response_for(dossier: dict, *, sufficient: float = 0.9,
                 supports: list[float] | None = None) -> dict:
    supports = supports or [0.9] + [0.1] * (len(dossier["candidates"]) - 1)
    answers = {
        "divergence_category": {
            "type": "choice", "choice": "mmio_fifo_protocol",
            "probabilities": {"mmio_fifo_protocol": 0.8, "state_update": 0.2},
            "confidence": 0.8,
        },
        "causal_proximity": {
            "type": "score", "score": 3.7, "legend": {"0": "far", "4": "direct"},
            "probabilities": {"3": 0.3, "4": 0.7}, "confidence": 0.7,
        },
        "evidence_sufficient": {"type": "noul", "noul": sufficient},
    }
    for candidate, support in zip(dossier["candidates"], supports):
        answers[f"supports_{candidate['id']}"] = {"type": "noul", "noul": support}
    return {"model": "typesafe/jev-1.13-20260917", "answers": answers,
            "usage": {"input_tokens": 123, "output_tokens": 0}}


class FakeResponse:
    def __init__(self, value: dict) -> None:
        self.value = value

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self) -> bytes:
        return json.dumps(self.value).encode()


def main() -> int:
    with tempfile.TemporaryDirectory() as directory_text:
        directory = Path(directory_text)
        original = directory / "original.ndjson"
        reconstructed = directory / "reconstructed.ndjson"
        write_events(original, [0x11])
        write_events(reconstructed, [0x22])
        disassembly = directory / "maincpu.lst"
        disassembly.write_text(
            "  ff0: 00 00 nop\n 1000: aa bb call 0x2000\n 2000: cc dd ret\n"
            " 3000: 11 22 st 0x3000\n 3010: 00 00 nop\n", encoding="utf-8")
        annotation = directory / "symbols.md"
        annotation.write_text("- `0x3000`: geometry command register\n", encoding="utf-8")
        ledger = directory / "ledger.json"
        ledger.write_text(json.dumps({
            "images": [{"name": "maincpu", "work_units": [{
                "id": "maincpu.command", "name": "command", "stage": "modeled",
                "ranges": [{"start": "0x2ff0", "end": "0x3020"}],
            }]}]
        }), encoding="utf-8")

        dossier = build_dossier(
            original, reconstructed, disassembly=disassembly,
            annotations=[annotation], ledger=ledger, event_radius=1,
        )
        assert dossier["comparison"]["first_divergence_index"] == 2
        assert dossier["candidates"][0]["address"] == "0x00003000"
        assert dossier["disassembly"]["candidate_0"]
        assert dossier["annotations"]["candidate_0"]
        assert dossier["ledger_matches"]["candidate_0"][0]["stage"] == "modeled"
        assert dossier["bounds"]["state_bytes"] == len(canonical_bytes(dossier))
        assert len(dossier["windows"]["original"]) == 3

        request = build_request(dossier, "typesafe/jev-1.13")
        assert request["state"] is dossier
        assert request["questions"]["supports_candidate_0"]["type"] == "noul"
        assert request["questions"]["divergence_category"]["type"] == "choice"

        response = response_for(dossier)
        report = make_report(dossier, request, response, "openrouter")
        assert not report["abstained"]
        assert report["ranked_candidates"][0]["address"] == "0x00003000"
        assert report["classification"] == "advisory-discovery-only"
        assert "api_key" not in json.dumps(report).lower()

        tied = [0.60, 0.55] + [0.1] * max(0, len(dossier["candidates"]) - 2)
        abstained = make_report(dossier, request, response_for(dossier, supports=tied), "openrouter")
        assert abstained["abstained"]
        assert any("separated" in reason for reason in abstained["abstention_reasons"])

        try:
            build_dossier(original, reconstructed, state_byte_limit=10)
        except ValueError as error:
            assert "exceeding --max-state-bytes" in str(error)
        else:
            raise AssertionError("oversize dossier was accepted")

        same = directory / "same.ndjson"
        write_events(same, [0x11])
        try:
            build_dossier(original, same)
        except ValueError as error:
            assert "do not diverge" in str(error)
        else:
            raise AssertionError("matching traces were accepted")

        env_file = directory / ".env.local"
        env_file.write_text(
            "# ignored\nexport OPENROUTER_API_KEY='secret-test-key'\nTYPESAFE_API_KEY=other\n",
            encoding="utf-8",
        )
        assert parse_env_file(env_file)["OPENROUTER_API_KEY"] == "secret-test-key"
        previous = os.environ.pop("OPENROUTER_API_KEY", None)
        try:
            endpoint, model, key = provider_settings("openrouter", None, env_file)
            assert endpoint.endswith("/api/alpha/decisions")
            assert model == "typesafe/jev-1.13" and key == "secret-test-key"
        finally:
            if previous is not None:
                os.environ["OPENROUTER_API_KEY"] = previous

        calls = []

        def retrying_opener(req, timeout):
            calls.append((req, timeout))
            if len(calls) == 1:
                raise urllib.error.HTTPError(req.full_url, 429, "rate limited", {}, io.BytesIO())
            return FakeResponse(response)

        received, retries = post_json(
            "https://example.invalid/decisions", "test-key", request,
            opener=retrying_opener, sleeper=lambda _delay: None,
        )
        assert received == response and retries == [{"attempt": 1, "status": 429}]
        assert calls[0][0].get_header("Authorization") == "Bearer test-key"

        def bad_opener(req, timeout):
            raise urllib.error.HTTPError(req.full_url, 401, "unauthorized", {}, io.BytesIO())

        try:
            post_json("https://example.invalid/decisions", "bad", request, opener=bad_opener)
        except ValueError as error:
            assert "HTTP 401" in str(error)
        else:
            raise AssertionError("authentication failure was accepted")

    print("PASS: bounded JEV dossier, ranking, abstention, credentials, and retry contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
