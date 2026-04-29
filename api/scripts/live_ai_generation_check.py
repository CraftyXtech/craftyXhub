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
from services.ai.llm_config import AVAILABLE_MODELS, DEFAULT_MODEL


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
            notes = f"web_used={web_used}; sources={len(sources or [])}"
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
            self.add(
                f"model_switch:{model}",
                "FAIL" if problems else "PASS",
                round(generation_time or (time.perf_counter() - started), 2),
                model,
                "; ".join(problems) or f"web_used={web_used}",
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
            self.add(
                f"web_search:{flag}",
                "FAIL" if problems else "PASS",
                round(generation_time or (time.perf_counter() - started), 2),
                DEFAULT_MODEL,
                "; ".join(problems) or f"ddg_attempted={attempted}; web_used={web_used}",
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
            f"models={','.join(AVAILABLE_MODELS.keys())}",
            flush=True,
        )
        for blog_type, topic in BLOG_TYPES.items():
            await self.run_blog_type(blog_type, topic)
        for tool_id, params in GENERIC_PARAMS.items():
            await self.run_generic(tool_id, params)
        await self.run_excerpt()
        for model in AVAILABLE_MODELS.keys():
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
