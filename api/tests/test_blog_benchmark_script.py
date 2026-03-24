import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "benchmark_blog_generation.py"
)
SPEC = importlib.util.spec_from_file_location("benchmark_blog_generation", SCRIPT_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


RunRecord = MODULE.RunRecord


def test_parse_modes_deduplicates_and_preserves_order():
    search_states = MODULE.parse_search_states("off,on,off")
    assert search_states == ["off", "on"]


def test_search_state_expectation_ok_rules():
    assert MODULE.search_state_expectation_ok(
        "on", {"ddg_attempted": True}
    )
    assert MODULE.search_state_expectation_ok(
        "off", {"ddg_attempted": False}
    )


def test_summarize_search_state_passes_when_thresholds_met():
    records = [
        RunRecord(
            search_state="on",
            run_index=i + 1,
            warmup=False,
            ok=True,
            expectation_ok=True,
            generation_time_s=10.0 + (i * 0.1),
            phase_total_ms=10000.0,
            ddg_attempted=True,
            ddg_used=True,
            error=None,
        )
        for i in range(20)
    ]

    summary = MODULE.summarize_search_state(
        search_state="on",
        records=records,
        latency_slo_seconds=60.0,
        min_success_rate=0.95,
    )

    assert summary["pass"] is True
    assert summary["validated_successes"] == 20
    assert summary["success_rate"] == 1.0
    assert summary["p95_latency_s"] <= 60.0


def test_summarize_search_state_fails_when_success_rate_below_threshold():
    records = []
    for i in range(20):
        ok = i < 18  # 18/20 => 90%
        records.append(
            RunRecord(
                search_state="off",
                run_index=i + 1,
                warmup=False,
                ok=ok,
                expectation_ok=ok,
                generation_time_s=20.0,
                phase_total_ms=20000.0,
                ddg_attempted=False,
                ddg_used=False,
                error=None if ok else "RuntimeError: failed",
            )
        )

    summary = MODULE.summarize_search_state(
        search_state="off",
        records=records,
        latency_slo_seconds=60.0,
        min_success_rate=0.95,
    )

    assert summary["pass"] is False
    assert summary["success_rate"] == 0.9
    assert any("success_rate" in reason for reason in summary["failure_reasons"])
