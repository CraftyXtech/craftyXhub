#!/usr/bin/env python3
"""
Evaluate configured blog-generation models with Pydantic Evals.

Run from /api:
  source venv/bin/activate && PYTHONPATH=. python scripts/eval_blog_models.py

Fast smoke run:
  source venv/bin/activate && PYTHONPATH=. python scripts/eval_blog_models.py \
    --models qwen-3.6-max-preview --case-limit 1 --word-count short --no-use-web-search

Final campaign examples:
  source venv/bin/activate && PYTHONPATH=. python scripts/eval_blog_models.py \
    --case-word-count short --word-count case --no-use-web-search \
    --output-json /tmp/blog_eval_short_no_web.json \
    --output-md /tmp/blog_eval_short_no_web.md
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from statistics import mean
from typing import Any

from pydantic import BaseModel, Field
from pydantic_evals import Case, Dataset
from pydantic_evals.evaluators import (
    EvaluationReason,
    Evaluator,
    EvaluatorContext,
    EvaluatorOutput,
)


API_DIR = Path(__file__).resolve().parents[1]
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from core.config import settings
from services.ai.blog_agent import BlogAgentService
from services.ai.llm_config import AVAILABLE_MODELS, get_blog_model_keys
from schemas.ai import BlogPost


DEFAULT_CASES: list[dict[str, Any]] = [
    {
        "name": "health_how_to_short",
        "topic": "How to Quit Smoking for Men",
        "blog_type": "how-to",
        "keywords": ["quit smoking", "men health", "smoking cessation"],
        "audience": "general adult men",
        "word_count": "short",
        "quality_focus": ["practicality", "clarity", "nonjudgmental tone"],
    },
    {
        "name": "ai_policy_news_medium",
        "topic": "AI Wars Reach the Pentagon: OpenAI, xAI, and New Red Lines",
        "blog_type": "news",
        "keywords": ["AI policy", "defense AI", "AI governance"],
        "audience": "general audience",
        "word_count": "medium",
        "quality_focus": ["freshness", "nuance", "source grounding", "factual caution"],
    },
    {
        "name": "consumer_comparison_medium",
        "topic": "Best Budget Smartphones in 2026: Which One Should You Buy?",
        "blog_type": "comparison",
        "keywords": ["budget smartphones", "best phones 2026", "phone comparison"],
        "audience": "tech-savvy consumers",
        "word_count": "medium",
        "quality_focus": ["comparison criteria", "specific recommendations", "SEO"],
    },
    {
        "name": "creator_tutorial_short",
        "topic": "Build a Simple Paid Newsletter Workflow With Automation",
        "blog_type": "tutorial",
        "keywords": ["paid newsletter", "newsletter automation", "creator workflow"],
        "audience": "independent creators",
        "word_count": "short",
        "quality_focus": ["steps", "tools", "actionability"],
    },
    {
        "name": "seo_local_service_short",
        "topic": "Best Emergency Plumbers in Melbourne: What to Check Before You Call",
        "blog_type": "how-to",
        "keywords": ["emergency plumbers Melbourne", "plumber callout", "local plumbing"],
        "audience": "Melbourne homeowners and renters",
        "word_count": "short",
        "quality_focus": ["local intent", "service SEO", "concise advice", "avoid fake claims"],
    },
    {
        "name": "product_review_medium",
        "topic": "Review the Latest All-in-One Project Management Platforms for Solo Founders",
        "blog_type": "review",
        "keywords": ["project management platforms", "solo founders", "productivity software"],
        "audience": "solo founders",
        "word_count": "medium",
        "quality_focus": ["review format", "evaluation criteria", "neutral tone"],
    },
    {
        "name": "listicle_short",
        "topic": "Seven Affordable Tools Remote Teams Can Use to Improve Async Collaboration",
        "blog_type": "listicle",
        "keywords": ["async collaboration tools", "remote teams", "affordable tools"],
        "audience": "remote team leads",
        "word_count": "short",
        "quality_focus": ["scannability", "concise sections", "duplicate idea avoidance"],
    },
    {
        "name": "case_study_medium",
        "topic": "How a Local Retailer Improved Repeat Purchases With Email Segmentation",
        "blog_type": "case-study",
        "keywords": ["email segmentation", "repeat purchases", "local retailer"],
        "audience": "small business owners",
        "word_count": "medium",
        "quality_focus": ["realistic business details", "measured outcomes", "no fake certainty"],
    },
    {
        "name": "technical_tutorial_long",
        "topic": "Build a Beginner-Friendly SEO Checklist for a New Ecommerce Blog",
        "blog_type": "tutorial",
        "keywords": ["SEO checklist", "ecommerce blog", "beginner SEO"],
        "audience": "new ecommerce operators",
        "word_count": "long",
        "quality_focus": ["long-form structure", "depth", "markdown consistency"],
    },
    {
        "name": "opinion_editorial_medium",
        "topic": "Why Transparent AI Labeling Can Improve Trust Without Hurting Creativity",
        "blog_type": "opinion",
        "keywords": ["AI labeling", "creative trust", "transparent AI"],
        "audience": "creative professionals and technology readers",
        "word_count": "medium",
        "quality_focus": ["voice", "nuance", "non-generic arguments"],
    },
]


class BlogEvalInput(BaseModel):
    model: str
    case_name: str
    topic: str
    blog_type: str = "news"
    keywords: list[str] = Field(default_factory=list)
    audience: str | None = None
    word_count: str = "medium"
    tone: str = "professional"
    language: str = "en-US"
    creativity: float = 0.7
    use_web_search: bool = True
    run_index: int = 1
    timeout_seconds: float = 120.0
    quality_focus: list[str] = Field(default_factory=list)


class BlogEvalOutput(BaseModel):
    model: str
    case_name: str
    topic: str
    blog_type: str
    ok: bool
    generation_time_s: float | None = None
    web_search_used: bool | None = None
    source_count: int | None = None
    quality_report: dict[str, Any] = Field(default_factory=dict)
    phase_metrics: dict[str, Any] = Field(default_factory=dict)
    title: str | None = None
    slug: str | None = None
    summary: str | None = None
    seo_title: str | None = None
    seo_description: str | None = None
    section_count: int | None = None
    section_headings: list[str] = Field(default_factory=list)
    body_word_count: int | None = None
    tags: list[str] = Field(default_factory=list)
    editorial_scores: dict[str, int] = Field(default_factory=dict)
    editorial_score_total: int | None = None
    total_tokens: int | None = None
    error: str | None = None


def _contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def _score_editorial_quality(
    *,
    blog_post: BlogPost,
    blog_type: str,
    topic: str,
    keywords: list[str],
    use_web_search: bool,
    source_count: int,
    quality_report: dict[str, Any],
) -> dict[str, int]:
    headings = [section.heading for section in blog_post.sections]
    full_text = " ".join(
        [
            blog_post.title,
            blog_post.summary,
            " ".join(headings),
            " ".join(section.body_markdown for section in blog_post.sections),
        ]
    )
    topic_tokens = [token for token in topic.lower().split() if len(token) > 3]
    keyword_hits = sum(1 for keyword in keywords if keyword.lower() in full_text.lower())
    topic_hits = sum(1 for token in topic_tokens if token in full_text.lower())

    instruction = 3
    if keyword_hits >= 1 and topic_hits >= max(2, min(5, len(topic_tokens) // 3)):
        instruction = 4
    if keyword_hits >= min(2, len(keywords)) and topic_hits >= max(4, min(8, len(topic_tokens) // 2)):
        instruction = 5

    heading_blob = " ".join(headings).lower()
    structure_terms = {
        "how-to": ["why", "step", "mistake", "next"],
        "tutorial": ["why", "step", "mistake", "next", "checklist"],
        "comparison": ["compare", "versus", "criteria", "best", "which"],
        "review": ["review", "criteria", "pros", "cons", "verdict"],
        "listicle": ["tool", "way", "use", "seven", "best"],
        "case-study": ["problem", "approach", "result", "lesson"],
        "news": ["what", "why", "means", "context", "next"],
        "opinion": ["why", "argument", "trust", "creativity", "case"],
    }
    expected = structure_terms.get(blog_type, [])
    structure_hits = sum(1 for term in expected if term in heading_blob)
    structure = 3 + min(2, structure_hits // 2)
    if len(headings) < 3:
        structure = 1

    grounding = 5
    if use_web_search:
        grounding = 2
        if source_count >= 1:
            grounding = 4
        if source_count >= 3:
            grounding = 5

    readability = quality_report.get("readability") or {}
    trope_hits = quality_report.get("ai_trope_hits") or []
    voice = 5
    if readability.get("is_hard_to_read"):
        voice -= 2
    if trope_hits:
        voice -= min(2, len(trope_hits))
    voice = max(1, voice)

    action_terms = ["step", "check", "use", "call", "compare", "choose", "start", "next", "ask", "measure"]
    actionability = 3
    if _contains_any(full_text, action_terms):
        actionability = 4
    if _contains_any(heading_blob, ["step", "next", "checklist", "what to do", "before you"]):
        actionability = 5

    return {
        "topic_relevance": instruction,
        "structure_match": structure,
        "source_grounding": grounding,
        "voice": voice,
        "actionability": actionability,
    }


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


def _extract_total_tokens(phase_metrics: dict[str, Any]) -> int | None:
    usage = phase_metrics.get("usage") or {}
    totals: list[int] = []
    for key in ("draft", "editorial"):
        part = usage.get(key)
        if isinstance(part, dict):
            value = _safe_int(part.get("total_tokens"))
            if value is not None:
                totals.append(value)
    return sum(totals) if totals else None


def _split_csv(value: str | None) -> set[str]:
    if not value:
        return set()
    return {item.strip() for item in value.split(",") if item.strip()}


def _load_cases(
    path: str | None,
    case_limit: int | None,
    *,
    case_word_count: str | None = None,
    case_names: str | None = None,
) -> list[dict[str, Any]]:
    if path:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(data, list) or not data:
            raise ValueError("cases JSON must be a non-empty list")
        cases = data
    else:
        cases = DEFAULT_CASES

    for idx, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise ValueError(f"Case {idx} must be an object")
        if not case.get("topic"):
            raise ValueError(f"Case {idx} missing 'topic'")
        if not case.get("name"):
            raise ValueError(f"Case {idx} missing 'name'")

    names = _split_csv(case_names)
    if names:
        cases = [case for case in cases if str(case.get("name")) in names]

    if case_word_count:
        cases = [
            case
            for case in cases
            if str(case.get("word_count", "medium")) == case_word_count
        ]

    if case_limit is not None:
        cases = cases[: max(0, case_limit)]
    if not cases:
        raise ValueError("No cases selected")
    return cases


async def run_blog_case(inputs: BlogEvalInput) -> BlogEvalOutput:
    service = BlogAgentService()
    started = time.perf_counter()

    try:
        blog_post, generation_time, web_search_used, sources = await asyncio.wait_for(
            service.generate(
                topic=inputs.topic,
                blog_type=inputs.blog_type,
                keywords=inputs.keywords,
                audience=inputs.audience,
                word_count=inputs.word_count,
                tone=inputs.tone,
                language=inputs.language,
                model=inputs.model,
                creativity=inputs.creativity,
                use_web_search=inputs.use_web_search,
            ),
            timeout=inputs.timeout_seconds,
        )
        phase_metrics = service.get_last_phase_metrics()
        quality_report = service.build_quality_report(
            blog_post=blog_post,
            word_count=inputs.word_count,
            keywords=inputs.keywords,
            phase_metrics=phase_metrics,
        )
        editorial_scores = _score_editorial_quality(
            blog_post=blog_post,
            blog_type=inputs.blog_type,
            topic=inputs.topic,
            keywords=inputs.keywords,
            use_web_search=inputs.use_web_search,
            source_count=len(sources or []),
            quality_report=quality_report,
        )

        return BlogEvalOutput(
            model=inputs.model,
            case_name=inputs.case_name,
            topic=inputs.topic,
            blog_type=inputs.blog_type,
            ok=True,
            generation_time_s=_safe_float(generation_time),
            web_search_used=bool(web_search_used),
            source_count=len(sources or []),
            quality_report=quality_report,
            phase_metrics=phase_metrics,
            title=blog_post.title,
            slug=blog_post.slug,
            summary=blog_post.summary,
            seo_title=blog_post.seo_title,
            seo_description=blog_post.seo_description,
            section_count=len(blog_post.sections or []),
            section_headings=[section.heading for section in blog_post.sections or []],
            body_word_count=_safe_int(quality_report.get("body_word_count")),
            tags=blog_post.tags or [],
            editorial_scores=editorial_scores,
            editorial_score_total=sum(editorial_scores.values()),
            total_tokens=_extract_total_tokens(phase_metrics),
        )
    except Exception as exc:
        return BlogEvalOutput(
            model=inputs.model,
            case_name=inputs.case_name,
            topic=inputs.topic,
            blog_type=inputs.blog_type,
            ok=False,
            generation_time_s=_safe_float(time.perf_counter() - started),
            error=f"{exc.__class__.__name__}: {exc}",
        )


@dataclass
class BlogQualityEvaluator(Evaluator[BlogEvalInput, BlogEvalOutput, dict[str, Any]]):
    latency_ceiling_s: float = 120.0
    token_ceiling: int = 12000

    def evaluate(
        self, ctx: EvaluatorContext[BlogEvalInput, BlogEvalOutput, dict[str, Any]]
    ) -> EvaluatorOutput:
        output = ctx.output
        if not output.ok:
            return {
                "generated": EvaluationReason(False, reason=output.error),
                "overall_quality_score": 0.0,
            }

        quality = output.quality_report or {}
        issues = quality.get("issues") or []
        seo_issues = quality.get("seo_issues") or []
        trope_hits = quality.get("ai_trope_hits") or []
        readability = quality.get("readability") or {}

        primary_keyword = (ctx.inputs.keywords[0] if ctx.inputs.keywords else "").lower()
        seo_blob = f"{output.seo_title or ''} {output.seo_description or ''}".lower()
        primary_keyword_in_seo = bool(primary_keyword and primary_keyword in seo_blob)

        latency = output.generation_time_s or self.latency_ceiling_s
        latency_score = 1.0 - min(latency / self.latency_ceiling_s, 1.0)
        issue_score = 1.0 - min(len(issues) / 8.0, 1.0)
        seo_score = 1.0 - min(len(seo_issues) / 4.0, 1.0)
        style_score = 1.0 - min(len(trope_hits) / 6.0, 1.0)
        if readability.get("is_hard_to_read"):
            style_score = min(style_score, 0.5)

        token_score = 1.0
        if output.total_tokens:
            token_score = 1.0 - min(output.total_tokens / self.token_ceiling, 1.0)

        grounding_score = 1.0
        if ctx.inputs.use_web_search:
            grounding_score = min(float(output.source_count or 0) / 3.0, 1.0)

        structure_ok = bool(
            output.title
            and output.slug
            and output.summary
            and output.section_count
            and 3 <= output.section_count <= 10
            and len(output.tags) >= 2
        )

        deterministic_quality = bool(quality.get("passed"))
        editorial_total = output.editorial_score_total or 0
        editorial_passed = editorial_total >= 18
        overall_score = (
            0.15 * float(structure_ok)
            + 0.15 * float(deterministic_quality)
            + 0.13 * issue_score
            + 0.12 * seo_score
            + 0.11 * style_score
            + 0.10 * grounding_score
            + 0.12 * min(editorial_total / 25.0, 1.0)
            + 0.07 * latency_score
            + 0.05 * token_score
        )

        return {
            "generated": EvaluationReason(True, reason="Blog generation returned a validated BlogPost"),
            "structure_valid": EvaluationReason(
                structure_ok,
                reason=f"sections={output.section_count}, tags={len(output.tags)}",
            ),
            "deterministic_quality_passed": EvaluationReason(
                deterministic_quality,
                reason="; ".join(issues[:4]) if issues else "No deterministic quality issues",
            ),
            "primary_keyword_in_seo": EvaluationReason(
                primary_keyword_in_seo,
                reason=f"primary_keyword={primary_keyword!r}",
            ),
            "editorial_quality_passed": EvaluationReason(
                editorial_passed,
                reason=f"editorial_score_total={editorial_total}/25; scores={output.editorial_scores}",
            ),
            "seo_score": round(seo_score, 4),
            "style_score": round(style_score, 4),
            "grounding_score": round(grounding_score, 4),
            "editorial_score": editorial_total,
            "latency_score": round(latency_score, 4),
            "token_efficiency_score": round(token_score, 4),
            "overall_quality_score": round(overall_score, 4),
            "issue_count": len(issues),
            "seo_issue_count": len(seo_issues),
            "ai_trope_count": len(trope_hits),
            "body_word_count": output.body_word_count or 0,
            "source_count": output.source_count or 0,
        }


def _build_cases(args: argparse.Namespace) -> list[Case[BlogEvalInput, BlogEvalOutput, dict[str, Any]]]:
    raw_cases = _load_cases(
        args.cases_json,
        args.case_limit,
        case_word_count=args.case_word_count,
        case_names=args.case_names,
    )
    models = [m.strip() for m in args.models.split(",") if m.strip()]
    if not models:
        raise ValueError("No models supplied")

    unknown = [model for model in models if model not in AVAILABLE_MODELS]
    if unknown:
        raise ValueError(f"Unknown model(s): {', '.join(unknown)}")

    cases: list[Case[BlogEvalInput, BlogEvalOutput, dict[str, Any]]] = []
    for model in models:
        for raw_case in raw_cases:
            case_name = raw_case.get("name") or raw_case["topic"].lower().replace(" ", "_")[:40]
            for run_index in range(1, args.runs_per_case + 1):
                word_count = (
                    str(raw_case.get("word_count", "medium"))
                    if args.word_count == "case"
                    else args.word_count
                )
                inputs = BlogEvalInput(
                    model=model,
                    case_name=str(case_name),
                    topic=raw_case["topic"],
                    blog_type=raw_case.get("blog_type", "news"),
                    keywords=raw_case.get("keywords") or [],
                    audience=raw_case.get("audience"),
                    word_count=word_count,
                    tone=args.tone,
                    language=args.language,
                    creativity=args.creativity,
                    use_web_search=args.use_web_search,
                    run_index=run_index,
                    timeout_seconds=args.per_run_timeout_seconds,
                    quality_focus=raw_case.get("quality_focus") or [],
                )
                cases.append(
                    Case(
                        name=f"{model}:{case_name}:run-{run_index}",
                        inputs=inputs,
                        metadata={
                            "model": model,
                            "blog_type": inputs.blog_type,
                            "word_count": inputs.word_count,
                            "quality_focus": inputs.quality_focus,
                        },
                    )
                )
    return cases


def _case_to_dict(case: Any) -> dict[str, Any]:
    output = case.output
    output_data = output.model_dump() if isinstance(output, BaseModel) else output

    return {
        "name": case.name,
        "inputs": case.inputs.model_dump() if isinstance(case.inputs, BaseModel) else case.inputs,
        "metadata": case.metadata,
        "output": output_data,
        "task_duration": case.task_duration,
        "total_duration": case.total_duration,
        "scores": {
            key: {"value": result.value, "reason": result.reason}
            for key, result in case.scores.items()
        },
        "assertions": {
            key: {"value": result.value, "reason": result.reason}
            for key, result in case.assertions.items()
        },
        "labels": {
            key: {"value": result.value, "reason": result.reason}
            for key, result in case.labels.items()
        },
        "evaluator_failures": [str(item) for item in case.evaluator_failures],
    }


def _avg(values: list[int | float | None]) -> float | None:
    clean = [float(value) for value in values if value is not None]
    return mean(clean) if clean else None


def _summarize_by_model(case_dicts: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for case in case_dicts:
        model = case["inputs"]["model"]
        grouped.setdefault(model, []).append(case)

    summaries: list[dict[str, Any]] = []
    for model, cases in grouped.items():
        outputs = [case["output"] for case in cases]
        ok_outputs = [output for output in outputs if output.get("ok")]

        def score(name: str) -> list[float]:
            return [
                float(case["scores"][name]["value"])
                for case in cases
                if name in case["scores"] and case["scores"][name]["value"] is not None
            ]

        generated = [
            bool(case["assertions"].get("generated", {}).get("value"))
            for case in cases
            if "generated" in case["assertions"]
        ]
        quality_passed = [
            bool(case["assertions"].get("deterministic_quality_passed", {}).get("value"))
            for case in cases
            if "deterministic_quality_passed" in case["assertions"]
        ]
        editorial_passed = [
            bool(case["assertions"].get("editorial_quality_passed", {}).get("value"))
            for case in cases
            if "editorial_quality_passed" in case["assertions"]
        ]
        structure_valid = [
            bool(case["assertions"].get("structure_valid", {}).get("value"))
            for case in cases
            if "structure_valid" in case["assertions"]
        ]
        short_runs = [
            case
            for case in cases
            if case["inputs"].get("word_count") == "short" and case["output"].get("ok")
        ]
        short_in_range = [
            200 <= int(case["output"].get("body_word_count") or 0) <= 600
            for case in short_runs
        ]
        provider_errors = [
            output.get("error")
            for output in outputs
            if output.get("error")
            and any(marker in str(output.get("error")).lower() for marker in ("429", "rate", "timeout"))
        ]

        summary = {
            "model": model,
            "runs": len(cases),
            "ok_runs": len(ok_outputs),
            "success_rate": round(sum(generated) / len(generated), 4) if generated else 0.0,
            "structure_valid_rate": round(sum(structure_valid) / len(structure_valid), 4)
            if structure_valid
            else 0.0,
            "quality_pass_rate": round(sum(quality_passed) / len(quality_passed), 4)
            if quality_passed
            else 0.0,
            "editorial_pass_rate": round(sum(editorial_passed) / len(editorial_passed), 4)
            if editorial_passed
            else 0.0,
            "short_length_pass_rate": round(sum(short_in_range) / len(short_in_range), 4)
            if short_in_range
            else None,
            "avg_overall_quality_score": round(_avg(score("overall_quality_score")) or 0.0, 4),
            "avg_seo_score": round(_avg(score("seo_score")) or 0.0, 4),
            "avg_style_score": round(_avg(score("style_score")) or 0.0, 4),
            "avg_grounding_score": round(_avg(score("grounding_score")) or 0.0, 4),
            "avg_editorial_score": round(_avg(score("editorial_score")) or 0.0, 2),
            "avg_latency_score": round(_avg(score("latency_score")) or 0.0, 4),
            "avg_latency_s": round(_avg([output.get("generation_time_s") for output in ok_outputs]) or 0.0, 3),
            "avg_body_word_count": round(_avg([output.get("body_word_count") for output in ok_outputs]) or 0.0, 1),
            "avg_source_count": round(_avg([output.get("source_count") for output in ok_outputs]) or 0.0, 2),
            "errors": [output.get("error") for output in outputs if output.get("error")],
            "provider_error_count": len(provider_errors),
        }
        summary["production_smooth"] = bool(
            summary["success_rate"] >= 0.95
            and summary["structure_valid_rate"] >= 1.0
            and summary["quality_pass_rate"] >= 0.75
            and summary["editorial_pass_rate"] >= 0.75
            and summary["avg_editorial_score"] >= 18
            and summary["avg_overall_quality_score"] >= 0.80
            and summary["avg_seo_score"] >= 0.85
            and summary["avg_style_score"] >= 0.90
            and (
                summary["short_length_pass_rate"] is None
                or summary["short_length_pass_rate"] >= 0.80
            )
        )
        summaries.append(summary)

    return sorted(summaries, key=lambda item: item["avg_overall_quality_score"], reverse=True)


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
        f"- case_word_count: {report['config']['case_word_count']}",
        f"- case_names: {report['config']['case_names'] or 'all'}",
        f"- pydantic_evals: true",
        "",
        "## Ranking",
        "",
        "| Rank | Model | Smooth | Overall | Success | Structure | Quality Pass | Editorial | Avg Editorial | Short Length | SEO | Style | Avg Latency(s) | Avg Words |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]

    for idx, summary in enumerate(report["ranking"], start=1):
        short_length = (
            "n/a"
            if summary["short_length_pass_rate"] is None
            else f"{summary['short_length_pass_rate']:.2%}"
        )
        lines.append(
            f"| {idx} | {summary['model']} | {'yes' if summary['production_smooth'] else 'no'} | "
            f"{summary['avg_overall_quality_score']:.4f} | "
            f"{summary['success_rate']:.2%} | {summary['structure_valid_rate']:.2%} | "
            f"{summary['quality_pass_rate']:.2%} | "
            f"{summary['editorial_pass_rate']:.2%} | {summary['avg_editorial_score']} | "
            f"{short_length} | "
            f"{summary['avg_seo_score']:.4f} | {summary['avg_style_score']:.4f} | "
            f"{summary['avg_latency_s']} | "
            f"{summary['avg_body_word_count']} |"
        )

    failures = [
        case
        for case in report["cases"]
        if not case["output"].get("ok")
        or not case["assertions"].get("deterministic_quality_passed", {}).get("value", True)
        or not case["assertions"].get("editorial_quality_passed", {}).get("value", True)
    ]
    if failures:
        lines.extend(["", "## Notable Issues", ""])
        for case in failures[:12]:
            output = case["output"]
            quality = output.get("quality_report") or {}
            issues = quality.get("issues") or []
            reason = (
                output.get("error")
                or "; ".join(issues[:3])
                or case["assertions"].get("editorial_quality_passed", {}).get("reason")
                or "Quality assertion failed"
            )
            lines.append(f"- `{case['name']}`: {reason}")

    return "\n".join(lines) + "\n"


async def run_eval(args: argparse.Namespace) -> dict[str, Any]:
    cases = _build_cases(args)
    models = [m.strip() for m in args.models.split(",") if m.strip()]

    dataset = Dataset(
        name="craftyxhub_blog_model_quality",
        cases=cases,
        evaluators=[
            BlogQualityEvaluator(
                latency_ceiling_s=args.latency_ceiling_s,
                token_ceiling=args.token_ceiling,
            )
        ],
    )

    eval_report = await dataset.evaluate(
        run_blog_case,
        name="blog_model_quality",
        max_concurrency=args.max_concurrency,
        progress=not args.no_progress,
    )
    if not args.no_print_report:
        eval_report.print()

    case_dicts = [_case_to_dict(case) for case in eval_report.cases]
    ranking = _summarize_by_model(case_dicts)

    report = {
        "config": {
            "models": models,
            "cases_count": len({case.inputs.case_name for case in cases}),
            "runs_per_case": args.runs_per_case,
            "word_count": args.word_count,
            "case_word_count": args.case_word_count,
            "case_names": args.case_names,
            "tone": args.tone,
            "language": args.language,
            "creativity": args.creativity,
            "use_web_search": args.use_web_search,
            "latency_ceiling_s": args.latency_ceiling_s,
            "token_ceiling": args.token_ceiling,
            "max_concurrency": args.max_concurrency,
        },
        "ranking": ranking,
        "model_summaries": {item["model"]: item for item in ranking},
        "cases": case_dicts,
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
    parser = argparse.ArgumentParser(
        description="Evaluate configured blog models with Pydantic Evals."
    )
    parser.add_argument(
        "--models",
        type=str,
        default=",".join(get_blog_model_keys()),
        help="Comma-separated model keys from llm_config.py. Defaults to blog-enabled models.",
    )
    parser.add_argument("--runs-per-case", type=int, default=1)
    parser.add_argument("--case-limit", type=int, default=None)
    parser.add_argument("--case-word-count", type=str, default=None)
    parser.add_argument(
        "--case-names",
        type=str,
        default=None,
        help="Comma-separated default case names to include.",
    )
    parser.add_argument("--cases-json", type=str, default=None)
    parser.add_argument(
        "--word-count",
        type=str,
        default="medium",
        help="Length for all selected cases, or 'case' to use each case's configured word_count.",
    )
    parser.add_argument("--tone", type=str, default="professional")
    parser.add_argument("--language", type=str, default="en-US")
    parser.add_argument("--creativity", type=float, default=0.6)
    parser.add_argument(
        "--use-web-search",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable DuckDuckGo research during generation.",
    )
    parser.add_argument("--per-run-timeout-seconds", type=float, default=120.0)
    parser.add_argument("--latency-ceiling-s", type=float, default=120.0)
    parser.add_argument("--token-ceiling", type=int, default=12000)
    parser.add_argument("--max-concurrency", type=int, default=1)
    parser.add_argument("--no-progress", action="store_true")
    parser.add_argument("--no-print-report", action="store_true")
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
