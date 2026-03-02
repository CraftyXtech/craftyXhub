#!/usr/bin/env python3
"""
Live benchmark harness for blog generation reliability and latency.

This script runs real BlogAgentService generations for selected grounding modes
and validates:
  - success rate
  - p95 latency
  - expected tool-grounding behavior per mode

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


VALID_MODES = {"off", "basic"}


@dataclass
class RunRecord:
    mode: str
    run_index: int
    warmup: bool
    ok: bool
    expectation_ok: bool
    generation_time_s: float | None
    phase_total_ms: float | None
    ddg_attempted: bool | None
    ddg_used: bool | None
    online_used: bool | None
    error: str | None


def parse_modes(modes_csv: str) -> list[str]:
    parsed = [m.strip() for m in modes_csv.split(",") if m.strip()]
    if not parsed:
        raise ValueError("No modes provided")
    invalid = [m for m in parsed if m not in VALID_MODES]
    if invalid:
        raise ValueError(
            f"Invalid mode(s): {', '.join(invalid)}. Valid modes: {', '.join(sorted(VALID_MODES))}"
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


def mode_expectation_ok(mode: str, web_grounding: dict[str, Any]) -> bool:
    ddg_attempted = bool(web_grounding.get("ddg_attempted"))

    if mode == "basic":
        return ddg_attempted
    if mode == "off":
        return not ddg_attempted
    return False


def summarize_mode(
    mode: str,
    records: list[RunRecord],
    latency_slo_seconds: float,
    min_success_rate: float,
) -> dict[str, Any]:
    measured = [r for r in records if not r.warmup]
    total = len(measured)
    if total == 0:
        return {
            "mode": mode,
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
        "mode": mode,
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
    mode: str,
    run_index: int,
    warmup: bool,
    model: str,
    word_count: str,
    execution_mode: str,
    per_run_timeout_seconds: float,
) -> RunRecord:
    service = BlogAgentService()
    started = time.perf_counter()

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
                web_search_mode=mode,
                execution_mode=execution_mode,
            ),
            timeout=per_run_timeout_seconds,
        )
        phase_metrics = service.get_last_phase_metrics()
        web_grounding = phase_metrics.get("web_grounding", {})
        expectation_ok = mode_expectation_ok(mode, web_grounding)
        return RunRecord(
            mode=mode,
            run_index=run_index,
            warmup=warmup,
            ok=True,
            expectation_ok=expectation_ok,
            generation_time_s=round(float(generation_time), 3),
            phase_total_ms=(phase_metrics.get("timings_ms") or {}).get("total"),
            ddg_attempted=web_grounding.get("ddg_attempted"),
            ddg_used=web_grounding.get("ddg_used"),
            online_used=web_grounding.get("online_used"),
            error=None if expectation_ok else "tool_expectation_failed",
        )
    except Exception as exc:
        phase_metrics = service.get_last_phase_metrics()
        web_grounding = phase_metrics.get("web_grounding", {})
        elapsed_s = round(time.perf_counter() - started, 3)
        return RunRecord(
            mode=mode,
            run_index=run_index,
            warmup=warmup,
            ok=False,
            expectation_ok=False,
            generation_time_s=elapsed_s,
            phase_total_ms=(phase_metrics.get("timings_ms") or {}).get("total"),
            ddg_attempted=web_grounding.get("ddg_attempted"),
            ddg_used=web_grounding.get("ddg_used"),
            online_used=web_grounding.get("online_used"),
            error=f"{exc.__class__.__name__}: {exc}",
        )


async def run_benchmark(args: argparse.Namespace) -> dict[str, Any]:
    modes = parse_modes(args.modes)
    all_records: list[RunRecord] = []
    mode_summaries: dict[str, Any] = {}

    for mode in modes:
        print(f"\n=== Mode: {mode} ===")
        mode_records: list[RunRecord] = []

        for idx in range(1, args.warmup_runs + 1):
            rec = await execute_run(
                mode=mode,
                run_index=idx,
                warmup=True,
                model=args.model,
                word_count=args.word_count,
                execution_mode=args.execution_mode,
                per_run_timeout_seconds=args.per_run_timeout_seconds,
            )
            mode_records.append(rec)
            print(
                f"[warmup {idx}/{args.warmup_runs}] "
                f"{'OK' if rec.ok else 'FAIL'} {rec.generation_time_s}s"
            )

        for idx in range(1, args.runs_per_mode + 1):
            rec = await execute_run(
                mode=mode,
                run_index=idx,
                warmup=False,
                model=args.model,
                word_count=args.word_count,
                execution_mode=args.execution_mode,
                per_run_timeout_seconds=args.per_run_timeout_seconds,
            )
            mode_records.append(rec)
            status = "OK" if (rec.ok and rec.expectation_ok) else "FAIL"
            print(
                f"[run {idx}/{args.runs_per_mode}] {status} "
                f"{rec.generation_time_s}s "
                f"ddg_attempted={rec.ddg_attempted} online_used={rec.online_used}"
            )
            if rec.error:
                print(f"  error: {rec.error}")

        summary = summarize_mode(
            mode=mode,
            records=mode_records,
            latency_slo_seconds=args.latency_slo_seconds,
            min_success_rate=args.min_success_rate,
        )
        mode_summaries[mode] = summary
        all_records.extend(mode_records)

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

    overall_pass = all(s["pass"] for s in mode_summaries.values())
    report = {
        "config": {
            "runs_per_mode": args.runs_per_mode,
            "warmup_runs": args.warmup_runs,
            "modes": modes,
            "model": args.model,
            "word_count": args.word_count,
            "execution_mode": args.execution_mode,
            "latency_slo_seconds": args.latency_slo_seconds,
            "per_run_timeout_seconds": args.per_run_timeout_seconds,
            "min_success_rate": args.min_success_rate,
        },
        "overall_pass": overall_pass,
        "mode_summaries": mode_summaries,
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
    parser.add_argument("--modes", type=str, default="off,basic")
    parser.add_argument("--model", type=str, default="claude-sonnet-4.6")
    parser.add_argument("--word-count", type=str, default="medium")
    parser.add_argument("--execution-mode", type=str, default="strict")
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
