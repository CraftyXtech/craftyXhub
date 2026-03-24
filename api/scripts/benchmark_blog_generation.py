#!/usr/bin/env python3
"""
Live benchmark harness for blog generation reliability and latency.

This script runs real BlogAgentService generations for web-search on/off states
and validates:
  - success rate
  - p95 latency
  - expected DuckDuckGo behavior per state

Run from /api:
  source venv/bin/activate && PYTHONPATH=. python scripts/benchmark_blog_generation.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable


API_DIR = Path(__file__).resolve().parents[1]
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from core.config import settings
from services.ai.blog_agent import BlogAgentService


VALID_SEARCH_STATES = {"off", "on"}


@dataclass
class RunRecord:
    search_state: str
    run_index: int
    warmup: bool
    ok: bool
    expectation_ok: bool
    generation_time_s: float | None
    phase_total_ms: float | None
    ddg_attempted: bool | None
    ddg_used: bool | None
    error: str | None


def parse_search_states(states_csv: str) -> list[str]:
    parsed = [state.strip() for state in states_csv.split(",") if state.strip()]
    if not parsed:
        raise ValueError("No search states provided")
    invalid = [state for state in parsed if state not in VALID_SEARCH_STATES]
    if invalid:
        raise ValueError(
            "Invalid search state(s): "
            f"{', '.join(invalid)}. Valid states: {', '.join(sorted(VALID_SEARCH_STATES))}"
        )
    # Preserve input order while deduplicating.
    return list(dict.fromkeys(parsed))


def percentile(values: Iterable[float], p: float) -> float | None:
    items = sorted(float(v) for v in values)
    n = len(items)
    if n == 0:
        return None
    if n == 1:
        return items[0]

    rank = (n - 1) * (p / 100.0)
    low = int(rank)
    high = min(low + 1, n - 1)
    frac = rank - low
    return items[low] + (items[high] - items[low]) * frac


def search_state_expectation_ok(search_state: str, web_grounding: dict[str, Any]) -> bool:
    ddg_attempted = bool(web_grounding.get("ddg_attempted"))

    if search_state == "on":
        return ddg_attempted
    if search_state == "off":
        return not ddg_attempted
    return False


def summarize_search_state(
    search_state: str,
    records: list[RunRecord],
    latency_slo_seconds: float,
    min_success_rate: float,
) -> dict[str, Any]:
    measured = [r for r in records if not r.warmup]
    total = len(measured)
    if total == 0:
        return {
            "search_state": search_state,
            "runs": 0,
            "validated_successes": 0,
            "success_rate": 0.0,
            "p50_latency_s": None,
            "p95_latency_s": None,
            "max_latency_s": None,
            "tool_expectation_pass_rate": 0.0,
            "pass": False,
            "failure_reasons": ["no measured runs"],
        }

    validated_successes = [r for r in measured if r.ok and r.expectation_ok]
    success_rate = len(validated_successes) / total

    success_latencies = [r.generation_time_s for r in validated_successes if r.generation_time_s is not None]
    p50_latency_s = percentile(success_latencies, 50)
    p95_latency_s = percentile(success_latencies, 95)
    max_latency_s = max(success_latencies) if success_latencies else None

    tool_expectation_pass_rate = (
        sum(1 for r in measured if r.expectation_ok) / total
    )

    reasons: list[str] = []
    if success_rate < min_success_rate:
        reasons.append(
            f"success_rate {success_rate:.2%} below target {min_success_rate:.2%}"
        )
    if p95_latency_s is None or p95_latency_s > latency_slo_seconds:
        reasons.append(
            f"p95_latency {p95_latency_s if p95_latency_s is not None else 'N/A'}s above target {latency_slo_seconds}s"
        )
    if tool_expectation_pass_rate < min_success_rate:
        reasons.append(
            f"tool_expectation_pass_rate {tool_expectation_pass_rate:.2%} below target {min_success_rate:.2%}"
        )

    return {
        "search_state": search_state,
        "runs": total,
        "validated_successes": len(validated_successes),
        "success_rate": round(success_rate, 4),
        "p50_latency_s": round(p50_latency_s, 3) if p50_latency_s is not None else None,
        "p95_latency_s": round(p95_latency_s, 3) if p95_latency_s is not None else None,
        "max_latency_s": round(max_latency_s, 3) if max_latency_s is not None else None,
        "tool_expectation_pass_rate": round(tool_expectation_pass_rate, 4),
        "pass": len(reasons) == 0,
        "failure_reasons": reasons,
    }


async def execute_run(
    search_state: str,
    run_index: int,
    warmup: bool,
    model: str,
    word_count: str,
    per_run_timeout_seconds: float,
) -> RunRecord:
    service = BlogAgentService()
    started = time.perf_counter()
    use_web_search = search_state == "on"

    try:
        _, generation_time, _, _ = await asyncio.wait_for(
            service.generate(
                topic="How to launch and scale a SaaS product in Kenya in 2026",
                blog_type="how-to",
                keywords=["saas kenya", "m-pesa payments", "software go-to-market"],
                audience="startup founders and product teams",
                word_count=word_count,
                tone="professional",
                language="en-US",
                model=model,
                creativity=0.6,
                use_web_search=use_web_search,
            ),
            timeout=per_run_timeout_seconds,
        )
        phase_metrics = service.get_last_phase_metrics()
        web_grounding = phase_metrics.get("web_grounding", {})
        expectation_ok = search_state_expectation_ok(search_state, web_grounding)
        return RunRecord(
            search_state=search_state,
            run_index=run_index,
            warmup=warmup,
            ok=True,
            expectation_ok=expectation_ok,
            generation_time_s=round(float(generation_time), 3),
            phase_total_ms=(phase_metrics.get("timings_ms") or {}).get("total"),
            ddg_attempted=web_grounding.get("ddg_attempted"),
            ddg_used=web_grounding.get("ddg_used"),
            error=None if expectation_ok else "tool_expectation_failed",
        )
    except Exception as exc:
        phase_metrics = service.get_last_phase_metrics()
        web_grounding = phase_metrics.get("web_grounding", {})
        elapsed_s = round(time.perf_counter() - started, 3)
        return RunRecord(
            search_state=search_state,
            run_index=run_index,
            warmup=warmup,
            ok=False,
            expectation_ok=False,
            generation_time_s=elapsed_s,
            phase_total_ms=(phase_metrics.get("timings_ms") or {}).get("total"),
            ddg_attempted=web_grounding.get("ddg_attempted"),
            ddg_used=web_grounding.get("ddg_used"),
            error=f"{exc.__class__.__name__}: {exc}",
        )


async def run_benchmark(args: argparse.Namespace) -> dict[str, Any]:
    search_states = parse_search_states(args.search_states)
    all_records: list[RunRecord] = []
    state_summaries: dict[str, Any] = {}

    for search_state in search_states:
        print(f"\n=== Web Search: {search_state} ===")
        state_records: list[RunRecord] = []

        for idx in range(1, args.warmup_runs + 1):
            rec = await execute_run(
                search_state=search_state,
                run_index=idx,
                warmup=True,
                model=args.model,
                word_count=args.word_count,
                per_run_timeout_seconds=args.per_run_timeout_seconds,
            )
            state_records.append(rec)
            print(
                f"[warmup {idx}/{args.warmup_runs}] "
                f"{'OK' if rec.ok else 'FAIL'} {rec.generation_time_s}s"
            )

        for idx in range(1, args.runs_per_mode + 1):
            rec = await execute_run(
                search_state=search_state,
                run_index=idx,
                warmup=False,
                model=args.model,
                word_count=args.word_count,
                per_run_timeout_seconds=args.per_run_timeout_seconds,
            )
            state_records.append(rec)
            status = "OK" if (rec.ok and rec.expectation_ok) else "FAIL"
            print(
                f"[run {idx}/{args.runs_per_mode}] {status} "
                f"{rec.generation_time_s}s "
                f"ddg_attempted={rec.ddg_attempted} ddg_used={rec.ddg_used}"
            )
            if rec.error:
                print(f"  error: {rec.error}")

        summary = summarize_search_state(
            search_state=search_state,
            records=state_records,
            latency_slo_seconds=args.latency_slo_seconds,
            min_success_rate=args.min_success_rate,
        )
        state_summaries[search_state] = summary
        all_records.extend(state_records)

        print(
            "Summary:",
            f"success_rate={summary['success_rate']:.2%},",
            f"p95={summary['p95_latency_s']}s,",
            f"tool_pass_rate={summary['tool_expectation_pass_rate']:.2%},",
            f"pass={summary['pass']}",
        )
        if summary["failure_reasons"]:
            for reason in summary["failure_reasons"]:
                print(f"  - {reason}")

    overall_pass = all(s["pass"] for s in state_summaries.values())
    report = {
        "config": {
            "runs_per_mode": args.runs_per_mode,
            "warmup_runs": args.warmup_runs,
            "search_states": search_states,
            "model": args.model,
            "word_count": args.word_count,
            "latency_slo_seconds": args.latency_slo_seconds,
            "per_run_timeout_seconds": args.per_run_timeout_seconds,
            "min_success_rate": args.min_success_rate,
        },
        "overall_pass": overall_pass,
        "state_summaries": state_summaries,
        "records": [asdict(r) for r in all_records],
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nReport written to: {output_path}")
    print(f"OVERALL PASS: {overall_pass}")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Benchmark blog generation reliability and latency.")
    parser.add_argument("--runs-per-mode", type=int, default=20)
    parser.add_argument("--warmup-runs", type=int, default=1)
    parser.add_argument("--search-states", type=str, default="off,on")
    parser.add_argument("--model", type=str, default="glm-5")
    parser.add_argument("--word-count", type=str, default="medium")
    parser.add_argument("--latency-slo-seconds", type=float, default=60.0)
    parser.add_argument("--per-run-timeout-seconds", type=float, default=75.0)
    parser.add_argument("--min-success-rate", type=float, default=0.95)
    parser.add_argument("--output-json", type=str, default="/tmp/blog_benchmark_report.json")
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if not settings.OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY is not configured.")
        return 2

    try:
        report = asyncio.run(run_benchmark(args))
    except KeyboardInterrupt:
        print("Interrupted by user.")
        return 130
    except Exception as exc:
        print(f"Benchmark failed: {exc}")
        return 1

    return 0 if report.get("overall_pass") else 1


if __name__ == "__main__":
    raise SystemExit(main())
