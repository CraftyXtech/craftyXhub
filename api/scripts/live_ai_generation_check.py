#!/usr/bin/env python3
"""Run live OpenRouter-backed AI generation checks.

This script intentionally calls real LLMs. Keep the default timeouts modest so
provider or network issues surface as failures instead of hanging the run.
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


API_DIR = Path(__file__).resolve().parents[1]
if str(API_DIR) not in sys.path:
    sys.path.insert(0, str(API_DIR))

from services.ai.blog_agent import BlogAgentService
from services.ai.generator import AIGeneratorService
from services.ai.llm_config import DEFAULT_MODEL, get_blog_model_keys


BLOG_TYPES: dict[str, str] = {
    "news": "Major cloud providers launch practical AI safety dashboards for small businesses",
    "how-to": "How creators can build a simple paid newsletter workflow with automation",
    "listicle": "Seven affordable tools remote teams can use to improve async collaboration",
    "tutorial": "Build a beginner friendly SEO checklist for a new ecommerce blog",
    "opinion": "Why transparent AI labeling can improve trust without hurting creativity",
    "review": "Review the latest all-in-one project management platforms for solo founders",
    "comparison": "Compare password managers for families, freelancers, and small teams",
    "case-study": "How a local retailer improved repeat purchases with email segmentation",
}

GENERIC_PARAMS: dict[str, dict[str, Any]] = {
    "blog-ideas": {
        "category": "Technology",
        "keywords": "AI productivity, automation",
        "audience": "small business owners",
    },
    "outline-generator": {
        "title": "AI Productivity Systems for Small Teams",
        "keywords": "AI productivity, workflow automation",
        "sections": "5",
        "cta_goal": "download checklist",
    },
    "section-draft": {
        "outline": "## Introduction\n- Explain the problem\n## Workflow\n- Describe the process",
    },
    "title-variants": {
        "topic": "AI productivity for small teams",
        "keywords": "AI productivity, small teams",
        "style": "practical",
    },
    "intro-conclusion-cta": {
        "title": "AI Productivity Systems for Small Teams",
        "summary": "A practical guide to adopting AI workflows without overwhelming staff.",
        "cta_goal": "download checklist",
    },
    "seo-pack": {
        "content": (
            "Small teams can use AI to document tasks, summarize meetings, and "
            "improve publishing workflows without adding complexity."
        ),
        "focus_keyword": "AI productivity",
        "audience": "small teams",
    },
    "image-alt-text": {
        "image_context": "A small team reviewing AI workflow dashboards on laptops",
        "caption_style": "editorial",
    },
    "internal-link-suggester": {
        "content": (
            "This article explains AI productivity workflows for small teams and "
            "links to automation and SEO guides."
        ),
        "available_slugs": "/ai-productivity,/seo-checklist,/automation-tools",
    },
    "content-refiner": {
        "content": "AI tools help teams do work faster. This draft needs clearer structure and better examples.",
    },
    "summarizer-brief": {
        "content": (
            "AI productivity systems help small teams summarize meetings, assign "
            "tasks, improve content workflows, and reduce repetitive work while "
            "keeping human review in place."
        ),
    },
    "fact-checklist": {
        "content": "AI tools always double revenue in 30 days and replace the need for project managers.",
    },
    "style-adapter": {
        "content": "AI productivity tools can improve operations when teams define boundaries and review outputs.",
        "reading_level": "High School",
    },
    "social-media-post": {
        "platform": "linkedin",
        "topic": "AI productivity for small teams",
        "cta_goal": "comment with favorite workflow",
    },
    "email-campaign": {
        "campaign_type": "educational",
        "audience": "small business owners",
        "offer": "free AI workflow checklist",
    },
    "product-description": {
        "product_name": "WorkflowPilot",
        "features": "AI summaries, task routing, calendar reminders",
        "benefits": "save time and keep teams aligned",
        "target_audience": "small teams",
    },
    "ad-copy-generator": {
        "platform": "google_rsa",
        "objective": "lead generation",
        "audience": "small business owners",
        "offer": "free AI workflow checklist",
    },
}

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass
class Result:
    test: str
    status: str
    generation_time: float | None
    model: str
    notes: str


def validate_blog_post(post: Any) -> list[str]:
    problems: list[str] = []
    if len(post.title or "") < 10:
        problems.append("title < 10 chars")
    if not SLUG_RE.match(post.slug or ""):
        problems.append(f"invalid slug {post.slug!r}")
    if len(post.summary or "") < 50:
        problems.append("summary < 50 chars")
    if not (3 <= len(post.sections or []) <= 10):
        problems.append(f"sections count {len(post.sections or [])}")
    for idx, section in enumerate(post.sections or [], 1):
        if not (3 <= len(section.heading or "") <= 120):
            problems.append(f"section {idx} heading length invalid")
        if len(section.body_markdown or "") < 30:
            problems.append(f"section {idx} body < 30 chars")
    tags = post.tags or []
    if not (2 <= len(tags) <= 12):
        problems.append(f"tags count {len(tags)}")
    if len(set(tags)) != len(tags):
        problems.append("duplicate tags")
    if not (15 <= len(post.seo_title or "") <= 80):
        problems.append(f"seo_title length {len(post.seo_title or '')}")
    if not (50 <= len(post.seo_description or "") <= 250):
        problems.append(f"seo_description length {len(post.seo_description or '')}")
    return problems


def _contains_any(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return any(term.lower() in lowered for term in terms)


def score_editorial_quality(
    post: Any,
    *,
    blog_type: str,
    topic: str,
    keywords: list[str],
    use_web_search: bool,
    source_count: int,
    quality_report: dict[str, Any],
) -> tuple[int, dict[str, int]]:
    headings = [section.heading for section in post.sections or []]
    full_text = " ".join(
        [
            post.title or "",
            post.summary or "",
            " ".join(headings),
            " ".join(section.body_markdown or "" for section in post.sections or []),
        ]
    )
    topic_tokens = [token for token in topic.lower().split() if len(token) > 3]
    topic_hits = sum(1 for token in topic_tokens if token in full_text.lower())
    keyword_hits = sum(1 for keyword in keywords if keyword.lower() in full_text.lower())
    topic_relevance = 3
    if keyword_hits >= 1 and topic_hits >= max(2, min(5, len(topic_tokens) // 3)):
        topic_relevance = 4
    if keyword_hits >= min(2, len(keywords)) and topic_hits >= max(4, min(8, len(topic_tokens) // 2)):
        topic_relevance = 5

    expected_by_type = {
        "how-to": ["why", "step", "mistake", "next"],
        "tutorial": ["why", "step", "mistake", "next", "checklist"],
        "comparison": ["compare", "versus", "criteria", "best", "which"],
        "review": ["review", "criteria", "pros", "cons", "verdict"],
        "listicle": ["tool", "way", "use", "seven", "best"],
        "case-study": ["problem", "approach", "result", "lesson"],
        "news": ["what", "why", "means", "context", "next"],
        "opinion": ["why", "argument", "trust", "creativity", "case"],
    }
    heading_blob = " ".join(headings).lower()
    structure_hits = sum(1 for term in expected_by_type.get(blog_type, []) if term in heading_blob)
    structure_match = 3 + min(2, structure_hits // 2)

    source_grounding = 5
    if use_web_search:
        source_grounding = 2
        if source_count >= 1:
            source_grounding = 4
        if source_count >= 3:
            source_grounding = 5

    readability = quality_report.get("readability") or {}
    voice = 5
    if readability.get("is_hard_to_read"):
        voice -= 2
    voice -= min(2, len(quality_report.get("ai_trope_hits") or []))
    voice = max(1, voice)

    actionability = 3
    if _contains_any(full_text, ["step", "check", "use", "call", "compare", "choose", "start", "next", "measure"]):
        actionability = 4
    if _contains_any(heading_blob, ["step", "next", "checklist", "what to do", "before you"]):
        actionability = 5

    scores = {
        "topic_relevance": topic_relevance,
        "structure_match": structure_match,
        "source_grounding": source_grounding,
        "voice": voice,
        "actionability": actionability,
    }
    return sum(scores.values()), scores


class LiveAiChecker:
    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.results: list[Result] = []

    def add(
        self,
        name: str,
        status: str,
        generation_time: float | None,
        model: str,
        notes: str,
    ) -> None:
        result = Result(name, status, generation_time, model, notes)
        self.results.append(result)
        print(
            f"{status:4} | {name} | model={model} | "
            f"time={generation_time} | {notes}",
            flush=True,
        )

    async def timed(self, coro, seconds: int):
        return await asyncio.wait_for(coro, timeout=seconds)

    async def run_blog_type(self, blog_type: str, topic: str) -> None:
        service = BlogAgentService()
        started = time.perf_counter()
        try:
            post, generation_time, web_used, sources = await self.timed(
                service.generate(
                    topic=topic,
                    blog_type=blog_type,
                    keywords=[blog_type, "AI tools", "small business"],
                    word_count="medium",
                    tone="professional",
                    language="en-US",
                    model=DEFAULT_MODEL,
                    creativity=0.6,
                    use_web_search=True,
                ),
                self.args.blog_timeout,
            )
            problems = validate_blog_post(post)
            quality_report = service.build_quality_report(
                blog_post=post,
                word_count="medium",
                keywords=[blog_type, "AI tools", "small business"],
                phase_metrics=service.get_last_phase_metrics(),
            )
            editorial_total, editorial_scores = score_editorial_quality(
                post,
                blog_type=blog_type,
                topic=topic,
                keywords=[blog_type, "AI tools", "small business"],
                use_web_search=True,
                source_count=len(sources or []),
                quality_report=quality_report,
            )
            if not quality_report.get("passed"):
                problems.append("quality_report failed: " + "; ".join(quality_report.get("issues") or []))
            if editorial_total < 18:
                problems.append(f"editorial_score={editorial_total}/25 {editorial_scores}")
            notes = f"web_used={web_used}; sources={len(sources or [])}; editorial={editorial_total}/25"
            self.add(
                f"blog_type:{blog_type}",
                "FAIL" if problems else "PASS",
                round(generation_time or (time.perf_counter() - started), 2),
                DEFAULT_MODEL,
                "; ".join(problems) or notes,
            )
        except Exception as exc:
            self.add(
                f"blog_type:{blog_type}",
                "FAIL",
                round(time.perf_counter() - started, 2),
                DEFAULT_MODEL,
                f"{type(exc).__name__}: {exc}",
            )

    async def run_generic(self, tool_id: str, params: dict[str, Any]) -> None:
        service = AIGeneratorService()
        started = time.perf_counter()
        try:
            result = await self.timed(
                service.generate(
                    tool_id=tool_id,
                    model=DEFAULT_MODEL,
                    params=params,
                    tone="professional",
                    length="medium",
                    language="en-US",
                    creativity=0.4,
                    variant_count=1,
                ),
                self.args.generic_timeout,
            )
            variants = result.get("variants") or []
            problems: list[str] = []
            if not variants:
                problems.append("no variants")
            elif not str(variants[0].get("content") or "").strip():
                problems.append("empty content")
            if result.get("model_used") != DEFAULT_MODEL:
                problems.append(f"model_used={result.get('model_used')!r}")
            self.add(
                f"generic:{tool_id}",
                "FAIL" if problems else "PASS",
                round(result.get("generation_time") or (time.perf_counter() - started), 2),
                DEFAULT_MODEL,
                "; ".join(problems) or "variant ok",
            )
        except Exception as exc:
            self.add(
                f"generic:{tool_id}",
                "FAIL",
                round(time.perf_counter() - started, 2),
                DEFAULT_MODEL,
                f"{type(exc).__name__}: {exc}",
            )

    async def run_excerpt(self) -> None:
        service = AIGeneratorService()
        started = time.perf_counter()
        try:
            result = await self.timed(
                service.generate(
                    tool_id="post-excerpt",
                    model=DEFAULT_MODEL,
                    params={
                        "title": "AI Workflow Testing for Editorial Teams",
                        "content": (
                            "Editorial teams need reliable AI workflow tests that "
                            "validate structure, quality, taxonomy, and publishing "
                            "metadata before generated articles reach production readers."
                        ),
                    },
                    tone="professional",
                    length="short",
                    language="en-US",
                    creativity=0.3,
                    variant_count=1,
                ),
                self.args.generic_timeout,
            )
            content = (result.get("variants") or [{}])[0].get("content", "").strip()
            problems: list[str] = []
            if not content:
                problems.append("empty excerpt")
            if len(content) > 500:
                problems.append(f"excerpt length {len(content)}")
            self.add(
                "excerpt:post-excerpt",
                "FAIL" if problems else "PASS",
                round(result.get("generation_time") or (time.perf_counter() - started), 2),
                DEFAULT_MODEL,
                "; ".join(problems) or f"chars={len(content)}",
            )
        except Exception as exc:
            self.add(
                "excerpt:post-excerpt",
                "FAIL",
                round(time.perf_counter() - started, 2),
                DEFAULT_MODEL,
                f"{type(exc).__name__}: {exc}",
            )

    async def run_model_switch(self, model: str) -> None:
        service = BlogAgentService()
        started = time.perf_counter()
        try:
            post, generation_time, web_used, _sources = await self.timed(
                service.generate(
                    topic="Latest AI developments in 2026",
                    blog_type="news",
                    keywords=["AI developments", "2026"],
                    word_count="short",
                    tone="professional",
                    language="en-US",
                    model=model,
                    creativity=0.5,
                    use_web_search=False,
                ),
                self.args.blog_timeout,
            )
            problems = validate_blog_post(post)
            quality_report = service.build_quality_report(
                blog_post=post,
                word_count="short",
                keywords=["AI developments", "2026"],
                phase_metrics=service.get_last_phase_metrics(),
            )
            editorial_total, editorial_scores = score_editorial_quality(
                post,
                blog_type="news",
                topic="Latest AI developments in 2026",
                keywords=["AI developments", "2026"],
                use_web_search=False,
                source_count=0,
                quality_report=quality_report,
            )
            if not quality_report.get("passed"):
                problems.append("quality_report failed: " + "; ".join(quality_report.get("issues") or []))
            if editorial_total < 18:
                problems.append(f"editorial_score={editorial_total}/25 {editorial_scores}")
            self.add(
                f"model_switch:{model}",
                "FAIL" if problems else "PASS",
                round(generation_time or (time.perf_counter() - started), 2),
                model,
                "; ".join(problems) or f"web_used={web_used}; editorial={editorial_total}/25",
            )
        except Exception as exc:
            self.add(
                f"model_switch:{model}",
                "FAIL",
                round(time.perf_counter() - started, 2),
                model,
                f"{type(exc).__name__}: {exc}",
            )

    async def run_web_search(self, flag: bool) -> None:
        service = BlogAgentService()
        started = time.perf_counter()
        try:
            post, generation_time, web_used, _sources = await self.timed(
                service.generate(
                    topic="How small teams can evaluate AI writing tools responsibly",
                    blog_type="how-to",
                    keywords=["AI writing tools", "responsible AI"],
                    word_count="short",
                    tone="professional",
                    language="en-US",
                    model=DEFAULT_MODEL,
                    creativity=0.5,
                    use_web_search=flag,
                ),
                self.args.blog_timeout,
            )
            metrics = service.get_last_phase_metrics() or {}
            attempted = metrics.get("web_grounding", {}).get("ddg_attempted")
            problems = validate_blog_post(post)
            if attempted != bool(flag):
                problems.append(f"ddg_attempted={attempted}, expected={bool(flag)}")
            report = service.build_quality_report(
                blog_post=post,
                word_count="short",
                keywords=["AI writing tools", "responsible AI"],
                phase_metrics=metrics,
            )
            editorial_total, editorial_scores = score_editorial_quality(
                post,
                blog_type="how-to",
                topic="How small teams can evaluate AI writing tools responsibly",
                keywords=["AI writing tools", "responsible AI"],
                use_web_search=flag,
                source_count=len(_sources or []),
                quality_report=report,
            )
            if not report.get("passed"):
                problems.append("quality_report failed: " + "; ".join(report.get("issues") or []))
            if editorial_total < 18:
                problems.append(f"editorial_score={editorial_total}/25 {editorial_scores}")
            self.add(
                f"web_search:{flag}",
                "FAIL" if problems else "PASS",
                round(generation_time or (time.perf_counter() - started), 2),
                DEFAULT_MODEL,
                "; ".join(problems) or f"ddg_attempted={attempted}; web_used={web_used}; editorial={editorial_total}/25",
            )
        except Exception as exc:
            self.add(
                f"web_search:{flag}",
                "FAIL",
                round(time.perf_counter() - started, 2),
                DEFAULT_MODEL,
                f"{type(exc).__name__}: {exc}",
            )

    async def run_quality_report(self) -> None:
        service = BlogAgentService()
        started = time.perf_counter()
        try:
            post, generation_time, _web_used, _sources = await self.timed(
                service.generate(
                    topic="Quality checks for AI generated editorial workflows",
                    blog_type="tutorial",
                    keywords=["AI quality checks", "editorial workflow"],
                    word_count="short",
                    tone="professional",
                    language="en-US",
                    model=DEFAULT_MODEL,
                    creativity=0.5,
                    use_web_search=False,
                ),
                self.args.blog_timeout,
            )
            report = service.build_quality_report(
                blog_post=post,
                word_count="short",
                keywords=["AI quality checks", "editorial workflow"],
                phase_metrics=service.get_last_phase_metrics(),
            )
            editorial_total, editorial_scores = score_editorial_quality(
                post,
                blog_type="tutorial",
                topic="Quality checks for AI generated editorial workflows",
                keywords=["AI quality checks", "editorial workflow"],
                use_web_search=False,
                source_count=0,
                quality_report=report,
            )
            required = {
                "target_length",
                "body_word_count",
                "section_count",
                "section_word_counts",
                "readability",
                "ai_trope_hits",
                "seo_issues",
                "issues",
                "passed",
                "phase_metrics",
            }
            missing = sorted(required - set(report.keys()))
            if not report.get("passed"):
                missing.append("quality_report.passed")
            if editorial_total < 18:
                missing.append(f"editorial_score={editorial_total}/25 {editorial_scores}")
            self.add(
                "quality_report",
                "FAIL" if missing else "PASS",
                round(generation_time or (time.perf_counter() - started), 2),
                DEFAULT_MODEL,
                f"missing={missing}" if missing else f"passed={report.get('passed')}",
            )
        except Exception as exc:
            self.add(
                "quality_report",
                "FAIL",
                round(time.perf_counter() - started, 2),
                DEFAULT_MODEL,
                f"{type(exc).__name__}: {exc}",
            )

    async def run(self) -> int:
        print(
            f"LIVE_AI_CHECK default_model={DEFAULT_MODEL} "
            f"models={','.join(get_blog_model_keys())}",
            flush=True,
        )
        for blog_type, topic in BLOG_TYPES.items():
            await self.run_blog_type(blog_type, topic)
        for tool_id, params in GENERIC_PARAMS.items():
            await self.run_generic(tool_id, params)
        await self.run_excerpt()
        for model in get_blog_model_keys():
            await self.run_model_switch(model)
        await self.run_web_search(True)
        await self.run_web_search(False)
        await self.run_quality_report()

        passed = sum(1 for result in self.results if result.status == "PASS")
        failed = sum(1 for result in self.results if result.status == "FAIL")
        print("\nSUMMARY")
        print(f"attempted={len(self.results)} pass={passed} fail={failed}")
        for result in self.results:
            if result.status == "FAIL":
                print(
                    "FAIL_DETAIL | "
                    f"{result.test} | model={result.model} | "
                    f"time={result.generation_time} | {result.notes}"
                )
        return 1 if failed else 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--blog-timeout", type=int, default=75)
    parser.add_argument("--generic-timeout", type=int, default=30)
    return parser.parse_args()


def main() -> int:
    return asyncio.run(LiveAiChecker(parse_args()).run())


if __name__ == "__main__":
    raise SystemExit(main())
