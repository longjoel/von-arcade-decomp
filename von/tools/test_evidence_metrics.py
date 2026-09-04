#!/usr/bin/env python3
"""Contract tests for evidence-workflow metrics."""

from __future__ import annotations

from evidence_metrics import metrics


def main() -> int:
    try:
        metrics([], {}, {}, {})
    except ValueError as error:
        assert "ledger input" in str(error)
    else:
        raise AssertionError("malformed ledger input was accepted")
    try:
        metrics({"images": []}, {}, {}, {})
    except ValueError as error:
        assert "worklist.discovered_units" in str(error)
    else:
        raise AssertionError("incomplete metric inputs were accepted")
    report = metrics(
        {"images": [{"work_units": [
            {"id": "m", "stage": "modeled", "created_at": "2026-09-04T14:00:00Z"},
            {"stage": "integrated"}, {"stage": "trace-validated"},
        ]}]},
        {"discovered_units": 4, "active_modeled_units": ["unit-1"], "modeled_wip_limit": 1,
         "dynamic_targets_added": 2},
        {"tier": "A", "possible_static_edge_count": 7, "confirmed_dynamic_edge_count": 2,
         "observed_entry_point_count": 3},
        {"compared_events": 10, "matched_prefix_events": 8,
         "confirmed_dynamic_edge_count": 2, "observed_indirect_target_count": 1,
         "original_checkpoints": ["reset", "audio"], "missed_checkpoints": ["audio"],
         "unexpected_checkpoints": [], "checkpoint_outcome": "divergence",
         "missing_original_checkpoints": [], "missing_reconstructed_checkpoints": ["audio"]},
        {"changed_decision": 3, "quarantined": 1},
        "2026-09-04T15:00:00Z",
    )
    assert report["stages"]["modeled"] == 1
    assert report["discovery"]["modeled_conversion_percent"] == 25.0
    assert report["discovery"]["integrated_conversion_percent"] == 50.0
    assert report["discovery"]["newly_discovered_dynamic_targets"] == 2
    assert report["coverage"]["possible_static_edges"] == 7
    assert report["coverage"]["confirmed_dynamic_edges"] == 2
    assert report["comparison"]["checkpoints_passed"] == ["reset"]
    assert report["comparison"]["missed_checkpoints"] == ["audio"]
    assert report["comparison"]["checkpoint_outcome"] == "divergence"
    assert report["comparison"]["missing_reconstructed_checkpoints"] == ["audio"]
    assert report["comparison"]["confirmed_dynamic_edges"] == 2
    assert report["comparison"]["observed_indirect_targets"] == 1
    assert report["experiments"] == {"changed_decision": 3, "quarantined": 1}
    assert report["age"]["modeled"]["median_age_seconds"] == 3600.0
    assert report["age"]["modeled"]["oldest_unit_id"] == "m"
    try:
        metrics({"images": [{"work_units": [{"stage": "planned", "created_at": "bad"}]}]},
                {"discovered_units": 0, "modeled_units": 0, "integrated_units": 0},
                {"possible_static_edge_count": 0, "confirmed_dynamic_edge_count": 0,
                 "observed_entry_point_count": 0},
                {"compared_events": 0, "matched_prefix_events": 0,
                 "original_checkpoints": [], "missed_checkpoints": [], "unexpected_checkpoints": []},
                as_of="2026-09-04T15:00:00Z")
    except ValueError as error:
        assert "created_at is invalid" in str(error)
    else:
        raise AssertionError("invalid unit timestamp was accepted")
    print("PASS: evidence metrics report authoritative workflow measures")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
