#!/usr/bin/env python3
"""
Evaluate configured blog-generation models on reliability, grounding quality,
deterministic quality checks, latency, and token usage.

Run from /api:
  source venv/bin/activate && PYTHONPATH=. python scripts/eval_blog_models.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from statistics import mean
from typing import Any


API_DIR = Path(__file__).resolve().parents[1]
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from core.config import settings
from services.ai.blog_agent import BlogAgentService
from services.ai.llm_config import AVAILABLE_MODELS


DEFAULT_CASES: list[dict[str, Any]] = [
    {
        "topic": "How to Quit Smoking for Men",
        "blog_type": "how-to",
        "keywords": ["quit smoking", "men health", "smoking cessation"],
        "audience": "general adult men",
    },
    {
        "topic": "AI Wars Reach the Pentagon: OpenAI, xAI, and New Red Lines",
        "blog_type": "opinion",
        "keywords": ["AI policy", "defense AI", "AI governance"],
        "audience": "general audience",
    },
    {
        "topic": "Best Budget Smartphones in 2026: Which One Should You Buy?",
        "blog_type": "comparison",
        "keywords": ["budget smartphones", "best phones 2026", "phone comparison"],
        "audience": "tech-savvy consumers",
    },
]


@dataclass
class EvalRun:
    model: str
    topic: str
    blog_type: str
    run_index: int
    ok: bool
    generation_time_s: float | None
    web_search_used: bool | None
    source_count: int | None
    quality_passed: bool | None
    issues_count: int | None
    ai_trope_count: int | None
    seo_issue_count: int | None
    hard_to_read: bool | None
    body_word_count: int | None
    total_tokens: int | None
    title: str | None
    error: str | None


def _safe_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _safe_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except Exception:
        return None


def _load_cases(path: str | None) -> list[dict[str, Any]]:
    if not path:
        return DEFAULT_CASES

    content = Path(path).read_text(encoding="utf-8")
    data = json.loads(content)
    if not isinstance(data, list) or not data:
        raise ValueError("cases JSON must be a non-empty list")
    for idx, case in enumerate(data, start=1):
        if not isinstance(case, dict):
            raise ValueError(f"Case {idx} must be an object")
        if not case.get("topic"):
            raise ValueError(f"Case {idx} missing 'topic'")
    return data


def _extract_total_tokens(phase_metrics: dict[str, Any]) -> int | None:
    usage = phase_metrics.get("usage") or {}
    parts: list[dict[str, Any]] = []
    draft = usage.get("draft")
    editorial = usage.get("editorial")
    if isinstance(draft, dict):
        parts.append(draft)
    if isinstance(editorial, dict):
        parts.append(editorial)

    totals = []
    for part in parts:
        value = _safe_int(part.get("total_tokens"))
        if value is not None:
            totals.append(value)
    return sum(totals) if totals else None


async def _run_one(
    *,
    model: str,
    case: dict[str, Any],
    run_index: int,
    args: argparse.Namespace,
) -> EvalRun:
    service = BlogAgentService()
    started = time.perf_counter()

    try:
        blog_post, generation_time, web_search_used, sources = await asyncio.wait_for(
            service.generate(
                topic=case["topic"],
                blog_type=case.get("blog_type", "how-to"),
                keywords=case.get("keywords"),
                audience=case.get("audience"),
                word_count=args.word_count,
                tone=args.tone,
                language=args.language,
                model=model,
                creativity=args.creativity,
                use_web_search=args.use_web_search,
            ),
            timeout=args.per_run_timeout_seconds,
        )

        phase_metrics = service.get_last_phase_metrics()
        quality_report = service.build_quality_report(
            blog_post=blog_post,
            word_count=args.word_count,
            keywords=case.get("keywords"),
            phase_metrics=phase_metrics,
        )

        return EvalRun(
            model=model,
            topic=case["topic"],
            blog_type=case.get("blog_type", "how-to"),
            run_index=run_index,
            ok=True,
            generation_time_s=_safe_float(generation_time),
            web_search_used=bool(web_search_used),
            source_count=len(sources or []),
            quality_passed=bool(quality_report.get("passed")),
            issues_count=len(quality_report.get("issues") or []),
            ai_trope_count=len(quality_report.get("ai_trope_hits") or []),
            seo_issue_count=len(quality_report.get("seo_issues") or []),
            hard_to_read=bool((quality_report.get("readability") or {}).get("is_hard_to_read")),
            body_word_count=_safe_int(quality_report.get("body_word_count")),
            total_tokens=_extract_total_tokens(phase_metrics),
            title=blog_post.title,
            error=None,
        )
    except Exception as exc:
        elapsed = _safe_float(time.perf_counter() - started)
        return EvalRun(
            model=model,
            topic=case["topic"],
            blog_type=case.get("blog_type", "how-to"),
            run_index=run_index,
            ok=False,
            generation_time_s=elapsed,
            web_search_used=None,
            source_count=None,
            quality_passed=None,
            issues_count=None,
            ai_trope_count=None,
            seo_issue_count=None,
            hard_to_read=None,
            body_word_count=None,
            total_tokens=None,
            title=None,
            error=f"{exc.__class__.__name__}: {exc}",
        )


def _avg(values: list[int | float | None]) -> float | None:
    clean = [float(v) for v in values if v is not None]
    return mean(clean) if clean else None


def _build_model_summary(
    model: str,
    runs: list[EvalRun],
    *,
    latency_ceiling_s: float,
    token_ceiling: int,
) -> dict[str, Any]:
    total = len(runs)
    oks = [r for r in runs if r.ok]
    total_ok = len(oks)

    success_rate = (total_ok / total) if total else 0.0
    quality_pass_rate = (
        sum(1 for r in oks if r.quality_passed) / total_ok
        if total_ok
        else 0.0
    )
    web_search_used_rate = (
        sum(1 for r in oks if r.web_search_used) / total_ok
        if total_ok
        else 0.0
    )
    hard_to_read_rate = (
        sum(1 for r in oks if r.hard_to_read) / total_ok
        if total_ok
        else 0.0
    )

    avg_latency = _avg([r.generation_time_s for r in oks])
    avg_sources = _avg([r.source_count for r in oks])
    avg_issues = _avg([r.issues_count for r in oks])
    avg_tropes = _avg([r.ai_trope_count for r in oks])
    avg_tokens = _avg([r.total_tokens for r in oks])

    # Composite score in [0, 1]
    issue_score = 1.0 - min((avg_issues or 10.0) / 10.0, 1.0)
    trope_score = 1.0 - min((avg_tropes or 10.0) / 10.0, 1.0)
    latency_score = 1.0 - min((avg_latency or latency_ceiling_s) / latency_ceiling_s, 1.0)
    token_score = 1.0 - min((avg_tokens or token_ceiling) / token_ceiling, 1.0)
    readability_score = 1.0 - hard_to_read_rate

    overall_score = (
        0.25 * success_rate
        + 0.20 * quality_pass_rate
        + 0.15 * issue_score
        + 0.10 * web_search_used_rate
        + 0.10 * readability_score
        + 0.10 * latency_score
        + 0.05 * trope_score
        + 0.05 * token_score
    )

    return {
        "model": model,
        "runs": total,
        "ok_runs": total_ok,
        "success_rate": round(success_rate, 4),
        "quality_pass_rate": round(quality_pass_rate, 4),
        "web_search_used_rate": round(web_search_used_rate, 4),
        "hard_to_read_rate": round(hard_to_read_rate, 4),
        "avg_latency_s": round(avg_latency, 3) if avg_latency is not None else None,
        "avg_source_count": round(avg_sources, 3) if avg_sources is not None else None,
        "avg_issues_count": round(avg_issues, 3) if avg_issues is not None else None,
        "avg_ai_trope_count": round(avg_tropes, 3) if avg_tropes is not None else None,
        "avg_total_tokens": round(avg_tokens, 1) if avg_tokens is not None else None,
        "overall_score": round(overall_score, 4),
        "failed_runs": [asdict(r) for r in runs if not r.ok],
    }


def _render_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Blog Model Evaluation Report",
        "",
        "## Config",
        f"- models: {', '.join(report['config']['models'])}",
        f"- cases: {report['config']['cases_count']}",
        f"- runs_per_case: {report['config']['runs_per_case']}",
        f"- use_web_search: {report['config']['use_web_search']}",
        f"- word_count: {report['config']['word_count']}",
        "",
        "## Ranking",
        "",
        "| Rank | Model | Score | Success | Quality Pass | Avg Latency(s) | Avg Issues | Avg Tokens |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]

    for idx, summary in enumerate(report["ranking"], start=1):
        lines.append(
            f"| {idx} | {summary['model']} | {summary['overall_score']:.4f} | "
            f"{summary['success_rate']:.2%} | {summary['quality_pass_rate']:.2%} | "
            f"{summary['avg_latency_s']} | {summary['avg_issues_count']} | {summary['avg_total_tokens']} |"
        )

    return "\n".join(lines) + "\n"


async def run_eval(args: argparse.Namespace) -> dict[str, Any]:
    cases = _load_cases(args.cases_json)
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if not models:
        raise ValueError("No models supplied")

    unknown = [m for m in models if m not in AVAILABLE_MODELS]
    if unknown:
        raise ValueError(f"Unknown model(s): {', '.join(unknown)}")

    all_runs: list[EvalRun] = []
    for model in models:
        print(f"\n=== Model: {model} ===")
        for case in cases:
            for run_index in range(1, args.runs_per_case + 1):
                run = await _run_one(
                    model=model,
                    case=case,
                    run_index=run_index,
                    args=args,
                )
                all_runs.append(run)
                status = "OK" if run.ok else "FAIL"
                print(
                    f"[{status}] case='{case['topic']}' run={run_index} "
                    f"time={run.generation_time_s}s quality={run.quality_passed} "
                    f"search_used={run.web_search_used}"
                )
                if run.error:
                    print(f"  error: {run.error}")

    by_model: dict[str, list[EvalRun]] = {}
    for run in all_runs:
        by_model.setdefault(run.model, []).append(run)

    summaries = [
        _build_model_summary(
            model=model,
            runs=by_model.get(model, []),
            latency_ceiling_s=args.latency_ceiling_s,
            token_ceiling=args.token_ceiling,
        )
        for model in models
    ]
    ranking = sorted(summaries, key=lambda item: item["overall_score"], reverse=True)

    report = {
        "config": {
            "models": models,
            "cases_count": len(cases),
            "runs_per_case": args.runs_per_case,
            "word_count": args.word_count,
            "tone": args.tone,
            "language": args.language,
            "creativity": args.creativity,
            "use_web_search": args.use_web_search,
            "latency_ceiling_s": args.latency_ceiling_s,
            "token_ceiling": args.token_ceiling,
        },
        "cases": cases,
        "ranking": ranking,
        "model_summaries": {item["model"]: item for item in summaries},
        "runs": [asdict(run) for run in all_runs],
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    out_json = Path(args.output_json)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nJSON report: {out_json}")

    if args.output_md:
        out_md = Path(args.output_md)
        out_md.parent.mkdir(parents=True, exist_ok=True)
        out_md.write_text(_render_markdown(report), encoding="utf-8")
        print(f"Markdown summary: {out_md}")

    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate blog models with web grounding enabled.")
    parser.add_argument(
        "--models",
        type=str,
        default=",".join(AVAILABLE_MODELS.keys()),
        help="Comma-separated model keys from llm_config.py",
    )
    parser.add_argument("--runs-per-case", type=int, default=1)
    parser.add_argument("--cases-json", type=str, default=None)
    parser.add_argument("--word-count", type=str, default="long")
    parser.add_argument("--tone", type=str, default="conversational")
    parser.add_argument("--language", type=str, default="en-US")
    parser.add_argument("--creativity", type=float, default=0.7)
    parser.add_argument(
        "--use-web-search",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable DuckDuckGo research during generation.",
    )
    parser.add_argument("--per-run-timeout-seconds", type=float, default=120.0)
    parser.add_argument("--latency-ceiling-s", type=float, default=120.0)
    parser.add_argument("--token-ceiling", type=int, default=12000)
    parser.add_argument("--output-json", type=str, default="/tmp/blog_model_eval.json")
    parser.add_argument("--output-md", type=str, default="/tmp/blog_model_eval.md")
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if not settings.OPENROUTER_API_KEY:
        print("ERROR: OPENROUTER_API_KEY is not configured.")
        return 2

    try:
        asyncio.run(run_eval(args))
        return 0
    except KeyboardInterrupt:
        print("Interrupted by user.")
        return 130
    except Exception as exc:
        print(f"Model eval failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
