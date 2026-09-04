#!/usr/bin/env python3
"""Contract tests for evidence-workflow metrics."""

from __future__ import annotations

from evidence_metrics import metrics


def main() -> int:
    report = metrics(
        {"images": [{"work_units": [
            {"stage": "modeled"}, {"stage": "integrated"}, {"stage": "trace-validated"},
        ]}]},
        {"discovered_units": 4, "active_modeled_units": ["unit-1"], "modeled_wip_limit": 1},
        {"tier": "A", "possible_static_edge_count": 7, "observed_entry_point_count": 3},
        {"compared_events": 10, "matched_prefix_events": 8, "missed_checkpoints": ["audio"],
         "unexpected_checkpoints": []},
    )
    assert report["stages"]["modeled"] == 1
    assert report["discovery"]["modeled_conversion_percent"] == 25.0
    assert report["discovery"]["integrated_conversion_percent"] == 200.0
    assert report["coverage"]["possible_static_edges"] == 7
    assert report["comparison"]["missed_checkpoints"] == ["audio"]
    print("PASS: evidence metrics report authoritative workflow measures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
