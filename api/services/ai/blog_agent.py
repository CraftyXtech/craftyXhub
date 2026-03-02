"""
Blog Agent Service - PydanticAI-powered blog post generation with web search.

V2 architecture:
- Capability-routed execution paths (structured / compat_json)
- Strict vs resilient execution mode
- Unified length profiles for prompt + token + quality checks
- No legacy JSON repair loop
"""

from __future__ import annotations

import httpx
import json
import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.fallback import FallbackModel
from pydantic_ai.settings import ModelSettings

from core.config import settings
from schemas.ai import BlogPost, BlogSection
from .llm_config import (
    DEFAULT_MODEL,
    build_blog_model_chain,
    get_blog_model_capabilities,
    get_model,
    get_model_with_online,
    get_model_from_id,
)
from .observability import ai_event, ai_span, configure_observability
from .pydantic_compat import (
    get_pydantic_ai_capabilities,
    supports_native_fallback_model,
)
from .quality_tools import (
    analyze_readability,
    extract_blog_plaintext,
    find_ai_tropes,
    seo_quality_issues,
)
from .tools import ToolHandler
from .web_search import WebSearchService

logger = logging.getLogger(__name__)


LENGTH_CONFIG: dict[str, dict[str, Any]] = {
    "short": {
        "words_label": "~300 words",
        "sections_label": "2-3",
        "sections_min": 2,
        "sections_max": 3,
        "max_tokens": 1500,
        "quality_word_range": (180, 650),
        "min_section_words": 35,
    },
    "medium": {
        "words_label": "~500 words",
        "sections_label": "3-4",
        "sections_min": 3,
        "sections_max": 4,
        "max_tokens": 2500,
        "quality_word_range": (320, 950),
        "min_section_words": 55,
    },
    "long": {
        "words_label": "~1000 words",
        "sections_label": "5-6",
        "sections_min": 5,
        "sections_max": 6,
        "max_tokens": 4000,
        "quality_word_range": (760, 1800),
        "min_section_words": 90,
    },
    "very-long": {
        "words_label": "1500+ words",
        "sections_label": "7-9",
        "sections_min": 7,
        "sections_max": 9,
        "max_tokens": 6000,
        "quality_word_range": (1200, 8500),
        "min_section_words": 110,
    },
}


@dataclass(frozen=True)
class BlogGenerationDeps:
    current_date_utc: str
    current_year: int
    topic: str
    blog_type: str
    keywords_text: str
    tone: str
    language: str
    length_tier: str
    section_guidance: str
    search_context: str
    timeliness_rules: str
    markdown_rules: str


class BlogAgentService:
    """
    Service for generating complete, structured blog posts using PydanticAI.
    """

    def __init__(self):
        self.tool_config = ToolHandler.get_tool("blog-agent")
        if not self.tool_config:
            raise ValueError("blog-agent tool configuration not found")

        self.system_prompt = self.tool_config["system_prompt"]
        self._last_phase_metrics: dict[str, Any] = {}
        self._structured_retries = 2
        self._compat_json_attempts = 2
        self._runtime_caps = get_pydantic_ai_capabilities()

        configure_observability()
        self._assert_runtime_capabilities()

    def _assert_runtime_capabilities(self) -> None:
        """
        Startup/runtime self-check for required pydantic-ai capabilities.
        """
        caps = self._runtime_caps
        if settings.BLOG_AGENT_V2_REQUIRE_NATIVE:
            missing: list[str] = []
            if not caps.get("output_api", False):
                missing.append("output_type/output_retries")
            if not caps.get("fallback_model", False):
                missing.append("FallbackModel")
            if missing:
                raise RuntimeError(
                    "Blog Agent V2 native mode requires newer pydantic-ai features: "
                    + ", ".join(missing)
                    + ". Upgrade dependencies (see api/requirements.txt)."
                )

        # Non-fatal advisory when running in compatibility mode.
        if not caps.get("fallback_model", False):
            logger.info(
                "pydantic-ai native FallbackModel unavailable; using compatibility"
                " failover loop for resilient mode"
            )

    def get_last_phase_metrics(self) -> dict[str, Any]:
        return dict(self._last_phase_metrics)

    @staticmethod
    def _get_length_profile(word_count: str) -> dict[str, Any]:
        return LENGTH_CONFIG.get(word_count, LENGTH_CONFIG["medium"])

    @staticmethod
    def _resolve_execution_mode(execution_mode: Optional[str]) -> str:
        if execution_mode in ("strict", "resilient"):
            return execution_mode
        return "strict"

    @staticmethod
    def _with_online_suffix(model_id: str, online: bool) -> str:
        return f"{model_id}:online" if online else model_id

    @staticmethod
    def _error_type(exc: Exception) -> str:
        if isinstance(exc, httpx.TimeoutException):
            return "timeout_error"
        if isinstance(exc, httpx.HTTPStatusError):
            if exc.response.status_code >= 500:
                return "provider_error"
            if exc.response.status_code in (400, 404):
                body = ""
                try:
                    body = exc.response.text.lower()
                except Exception:
                    body = str(exc).lower()
                if "tool_choice" in body or "response_format" in body:
                    return "compatibility_error"
            return "provider_error"

        text = str(exc).lower()
        if "validation" in text or "schema" in text or "output" in text:
            return "schema_validation_error"
        if "tool_choice" in text or "response_format" in text:
            return "compatibility_error"
        if "timeout" in text:
            return "timeout_error"
        return "provider_error"

    @staticmethod
    def _is_transient_provider_error(exc: Exception) -> bool:
        if isinstance(exc, httpx.TimeoutException):
            return True
        if isinstance(exc, httpx.HTTPStatusError):
            return exc.response.status_code >= 500 or exc.response.status_code == 429
        text = str(exc).lower()
        return "timeout" in text or "temporarily" in text

    def _build_timeliness_rules(self) -> str:
        current_dt = datetime.now(timezone.utc)
        current_year = current_dt.year
        return (
            "TIMELINESS REQUIREMENT:\n"
            f"- Today's date is {current_dt.strftime('%B %d, %Y')} (UTC).\n"
            f"- Treat the current year as {current_year}.\n"
            f"- Do not label the piece as a {current_year - 1} or older guide/trend report"
            " unless explicitly historical.\n"
            f"- If you include a year in title or SEO title, use {current_year} unless"
            " the topic is historical."
        )

    @staticmethod
    def _build_markdown_rules() -> str:
        return (
            "MARKDOWN FORMATTING RULES:\n"
            "- For numbered processes, each item MUST be on its own line.\n"
            "- Use valid ordered-list markdown exactly like:\n"
            "  1. First step\n"
            "  2. Second step\n"
            "  3. Third step\n"
            "- Never place multiple numbered items in a single paragraph."
        )

    def _build_outline_guidance(
        self,
        topic: str,
        blog_type: str,
        keywords: Optional[list[str]],
        sources: Optional[list[dict]],
        word_count: str = "medium",
    ) -> str:
        """
        Build explicit outline guidance for deterministic structure control.
        """
        profile = self._get_length_profile(word_count)
        keywords_text = ", ".join(keywords or []) if keywords else "not specified"

        if blog_type in ("how-to", "tutorial"):
            sections = [
                "Introduction",
                "Foundations and Key Concepts",
                "Step-by-Step Implementation",
                "Common Mistakes and Fixes",
                "Conclusion and Next Steps",
                "Action Checklist",
                "Resources and References",
            ]
        elif blog_type in ("comparison", "review"):
            sections = [
                "Introduction",
                "Evaluation Criteria",
                "Side-by-Side Analysis",
                "Pros and Cons",
                "Recommendations",
                "Decision Framework",
                "Conclusion and Call to Action",
            ]
        else:
            sections = [
                "Introduction",
                "Core Insights",
                "Practical Applications",
                "Strategic Recommendations",
                "Implementation Roadmap",
                "Risk and Mitigation",
                "Conclusion and Next Steps",
            ]

        target_max = int(profile["sections_max"])
        selected_sections = sections[:target_max]

        source_titles: list[str] = []
        for source in (sources or [])[:4]:
            title = source.get("title") if isinstance(source, dict) else None
            if isinstance(title, str) and title.strip():
                source_titles.append(title.strip())

        lines = [
            "\n\nSTRUCTURE GUIDANCE:",
            f"- Topic focus: {topic}",
            f"- Blog type: {blog_type}",
            f"- Primary keywords: {keywords_text}",
            f"- Section count target: {profile['sections_label']}",
            "- Use these section headings (or close equivalents):",
        ]
        lines.extend([f"  - {section}" for section in selected_sections])

        if source_titles:
            lines.append("- Ground examples or claims in these source themes:")
            lines.extend([f"  - {title}" for title in source_titles])

        return "\n".join(lines)

    def _build_blog_prompt(
        self,
        topic: str,
        blog_type: str,
        keywords: Optional[list[str]] = None,
        audience: Optional[str] = None,
        word_count: str = "medium",
        tone: str = "professional",
        language: str = "en-US",
    ) -> str:
        """
        Build the user prompt for generation.
        """
        profile = self._get_length_profile(word_count)
        keywords_text = ", ".join(keywords) if keywords else "Not specified"

        return (
            "Write a complete, publication-ready blog post that satisfies the BlogPost"
            " output schema.\n\n"
            f"Topic: {topic}\n"
            f"Blog Type: {blog_type}\n"
            f"Target Keywords: {keywords_text}\n"
            f"Target Audience: {audience or 'General audience'}\n"
            f"Tone: {tone}\n"
            f"Language: {language}\n"
            f"Length Tier: {word_count} ({profile['words_label']})\n"
            f"Required Section Count: {profile['sections_label']}\n"
            "\nOutput must be high quality, specific, and production-ready."
        )

    def _research_phase(
        self,
        topic: str,
        keywords: Optional[list[str]],
        web_search_mode: str,
        blog_type: str,
    ) -> tuple[str, list[dict] | None, bool]:
        """
        Research phase: gather external context using DuckDuckGo when enabled.
        """
        use_ddg = web_search_mode == "basic"
        web_context = ""
        web_search_used = False
        sources: list[dict] | None = None

        if not use_ddg:
            return web_context, sources, web_search_used

        try:
            search_svc = WebSearchService(max_results=3)
            include_news = blog_type == "news"
            search_results = search_svc.search_for_topic(
                topic,
                keywords,
                include_news=include_news,
            )
            web_context = search_svc.format_as_context(search_results)
            sources = search_results.get("sources", [])
            if sources:
                web_search_used = True
                logger.info(
                    "DuckDuckGo found %s sources for topic: %s",
                    len(sources),
                    topic,
                )
        except Exception as e:
            logger.warning("DuckDuckGo search failed, proceeding without: %s", e)

        return web_context, sources, web_search_used

    def _select_model_phase(self, model: str, web_search_mode: str):
        """
        Backward-compatible helper retained for tests and callers that inspect
        :online behavior before draft execution.
        """
        use_online = web_search_mode == "enhanced"
        if use_online:
            try:
                logger.info("Using OpenRouter :online model for: %s", model)
                return get_model_with_online(model), True
            except Exception as e:
                logger.warning(":online model failed, falling back to standard: %s", e)
                return get_model(model), False
        return get_model(model), False

    def _resolve_execution_path(self, model: str) -> str:
        capabilities = get_blog_model_capabilities(model)
        if not capabilities["blog_enabled"]:
            raise ValueError(f"Model '{model}' is disabled for blog generation")
        if capabilities["supports_structured"]:
            return "structured"
        if capabilities["supports_compat_json"]:
            return "compat_json"
        raise ValueError(
            f"Model '{model}' is not compatible with blog generation. "
            "It supports neither structured nor compat_json execution."
        )

    def _build_structured_blog_agent(self, model_obj: Any):
        agent = Agent(
            model=model_obj,
            output_type=BlogPost,
            system_prompt=self.system_prompt,
            deps_type=BlogGenerationDeps,
            retries=self._structured_retries,
            output_retries=self._structured_retries,
        )

        @agent.system_prompt
        def structured_constraints(ctx: RunContext[BlogGenerationDeps]) -> str:
            deps = ctx.deps
            profile = self._get_length_profile(deps.length_tier)
            parts = [
                "STRICT OUTPUT REQUIREMENTS:",
                f"- Current UTC date: {deps.current_date_utc}.",
                f"- Current year: {deps.current_year}.",
                f"- Topic: {deps.topic}.",
                f"- Blog type: {deps.blog_type}.",
                f"- Primary keywords: {deps.keywords_text}.",
                f"- Tone: {deps.tone}.",
                f"- Language: {deps.language}.",
                f"- Length tier: {deps.length_tier} ({profile['words_label']}).",
                f"- Section count MUST be within {profile['sections_label']}.",
                "- Output must satisfy the BlogPost schema exactly.",
                "- Use concise, valid markdown in section bodies.",
                deps.timeliness_rules,
                deps.markdown_rules,
                deps.section_guidance,
            ]
            if deps.search_context:
                parts.extend([
                    "WEB RESEARCH CONTEXT:",
                    deps.search_context,
                ])
            return "\n".join(parts)

        return agent

    @staticmethod
    def _extract_usage_payload(run_result: Any) -> dict[str, Any] | None:
        if not hasattr(run_result, "usage"):
            return None

        try:
            usage = run_result.usage()
        except Exception:
            return None

        if usage is None:
            return None

        payload: dict[str, Any] = {}
        for field in (
            "input_tokens",
            "output_tokens",
            "total_tokens",
            "requests",
            "tool_calls",
        ):
            value = getattr(usage, field, None)
            if value is not None:
                payload[field] = value

        return payload or None

    @staticmethod
    def _extract_effective_model_name(run_result: Any) -> str | None:
        """
        Best-effort extraction of the final model name from run messages.
        """
        messages_getter = getattr(run_result, "all_messages", None)
        if callable(messages_getter):
            try:
                messages = messages_getter()
                for message in reversed(messages):
                    model_name = getattr(message, "model_name", None)
                    if model_name:
                        return str(model_name)
            except Exception:
                pass
        return None

    @staticmethod
    def _coerce_structured_data(result_data: Any) -> dict[str, Any]:
        if isinstance(result_data, BlogPost):
            return result_data.model_dump()
        if hasattr(result_data, "model_dump"):
            return result_data.model_dump()
        if isinstance(result_data, dict):
            return result_data
        raise ValueError("Structured output is not a valid BlogPost payload")

    async def _run_structured_runner(
        self,
        model_ids: list[str],
        prompt: str,
        deps: BlogGenerationDeps,
        creativity: float,
        max_tokens: int,
        execution_mode: str,
    ) -> tuple[BlogPost, dict[str, Any] | None, str, list[str], list[dict[str, str]]]:
        attempted_models: list[str] = []
        errors: list[dict[str, str]] = []

        # Native fallback model path (when available) for resilient mode.
        if (
            execution_mode == "resilient"
            and len(model_ids) > 1
            and supports_native_fallback_model()
        ):
            attempted_models = list(model_ids)
            model_chain = [get_model_from_id(model_id) for model_id in model_ids]
            fallback_model = FallbackModel(*model_chain)
            try:
                agent = self._build_structured_blog_agent(fallback_model)
                result = await agent.run(
                    prompt,
                    deps=deps,
                    model_settings=ModelSettings(
                        temperature=creativity,
                        max_tokens=max_tokens,
                    ),
                )
                usage_payload = self._extract_usage_payload(result)
                blog_post = self._validate_and_create_blog_post(
                    self._coerce_structured_data(result.output)
                )
                effective_model = (
                    self._extract_effective_model_name(result) or model_ids[0]
                )
                return blog_post, usage_payload, effective_model, attempted_models, errors
            except Exception as exc:
                err_type = self._error_type(exc)
                errors.append(
                    {
                        "type": err_type,
                        "model": model_ids[0],
                        "message": str(exc),
                    }
                )
                logger.warning(
                    "Structured generation failed on fallback-model chain: %s", exc
                )

        for model_id in model_ids:
            attempted_models.append(model_id)
            try:
                model_obj = get_model_from_id(model_id)
                agent = self._build_structured_blog_agent(model_obj)
                result = await agent.run(
                    prompt,
                    deps=deps,
                    model_settings=ModelSettings(
                        temperature=creativity,
                        max_tokens=max_tokens,
                    ),
                )
                usage_payload = self._extract_usage_payload(result)
                blog_post = self._validate_and_create_blog_post(
                    self._coerce_structured_data(result.output)
                )
                return blog_post, usage_payload, model_id, attempted_models, errors
            except Exception as exc:
                err_type = self._error_type(exc)
                errors.append(
                    {
                        "type": err_type,
                        "model": model_id,
                        "message": str(exc),
                    }
                )
                logger.warning("Structured generation failed on %s: %s", model_id, exc)
                ai_event(
                    "blog_agent.structured_failure",
                    model=model_id,
                    error_type=err_type,
                    error=str(exc),
                )
                if execution_mode == "strict":
                    break

        raise ValueError(
            "Structured generation failed. "
            + " | ".join(f"{e['model']}: {e['message']}" for e in errors)
        )

    async def _run_compat_json_runner(
        self,
        model_ids: list[str],
        prompt: str,
        deps: BlogGenerationDeps,
        creativity: float,
        max_tokens: int,
        execution_mode: str,
    ) -> tuple[BlogPost, dict[str, Any] | None, str, list[str], list[dict[str, str]]]:
        attempted_models: list[str] = []
        errors: list[dict[str, str]] = []
        schema = BlogPost.model_json_schema()

        system_message = "\n\n".join(
            [
                self.system_prompt,
                deps.timeliness_rules,
                deps.markdown_rules,
                deps.section_guidance,
                f"Length tier: {deps.length_tier} ({self._get_length_profile(deps.length_tier)['words_label']}).",
                f"Keywords: {deps.keywords_text}",
                deps.search_context or "",
            ]
        ).strip()

        for model_id in model_ids:
            attempted_models.append(model_id)
            attempt = 0
            while attempt < self._compat_json_attempts:
                attempt += 1
                try:
                    timeout = httpx.Timeout(connect=20.0, read=70.0, write=20.0, pool=20.0)
                    async with httpx.AsyncClient(timeout=timeout) as client:
                        response = await client.post(
                            "https://openrouter.ai/api/v1/chat/completions",
                            headers={
                                "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
                                "Content-Type": "application/json",
                            },
                            json={
                                "model": model_id,
                                "messages": [
                                    {"role": "system", "content": system_message},
                                    {"role": "user", "content": prompt},
                                ],
                                "temperature": creativity,
                                "max_tokens": max_tokens,
                                "response_format": {
                                    "type": "json_schema",
                                    "json_schema": {
                                        "name": "blog_post",
                                        "strict": True,
                                        "schema": schema,
                                    },
                                },
                            },
                        )

                    response.raise_for_status()
                    payload = response.json()

                    if payload.get("error"):
                        raise ValueError(f"OpenRouter API error: {payload['error']}")

                    content = ""
                    if payload.get("choices"):
                        content = (
                            payload["choices"][0]
                            .get("message", {})
                            .get("content", "")
                        )

                    if not content.strip():
                        raise ValueError("Received empty model response")

                    parsed = json.loads(content)
                    validated = BlogPost.model_validate(parsed)
                    blog_post = self._validate_and_create_blog_post(validated.model_dump())

                    usage = payload.get("usage")
                    usage_payload = (
                        {
                            "input_tokens": usage.get("prompt_tokens"),
                            "output_tokens": usage.get("completion_tokens"),
                            "total_tokens": usage.get("total_tokens"),
                            "requests": 1,
                        }
                        if usage
                        else None
                    )

                    return blog_post, usage_payload, model_id, attempted_models, errors
                except Exception as exc:
                    err_type = self._error_type(exc)
                    errors.append(
                        {
                            "type": err_type,
                            "model": model_id,
                            "message": str(exc),
                        }
                    )
                    logger.warning(
                        "Compat JSON generation failed on %s (attempt %s/%s): %s",
                        model_id,
                        attempt,
                        self._compat_json_attempts,
                        exc,
                    )
                    ai_event(
                        "blog_agent.compat_json_failure",
                        model=model_id,
                        error_type=err_type,
                        attempt=attempt,
                        error=str(exc),
                    )

                    retryable = self._is_transient_provider_error(exc)
                    if retryable and attempt < self._compat_json_attempts:
                        continue
                    break

            if execution_mode == "strict":
                break

        raise ValueError(
            "Compat JSON generation failed. "
            + " | ".join(f"{e['model']}: {e['message']}" for e in errors)
        )

    def _count_total_words(self, blog_post: BlogPost) -> int:
        return sum(len(section.body_markdown.split()) for section in blog_post.sections)

    def _collect_quality_issues(
        self,
        blog_post: BlogPost,
        word_count: str,
        keywords: Optional[list[str]] = None,
    ) -> list[str]:
        issues: list[str] = []
        profile = self._get_length_profile(word_count)

        min_words, max_words = profile["quality_word_range"]
        total_words = self._count_total_words(blog_post)
        if total_words < min_words or total_words > max_words:
            issues.append(
                f"Total body word count must be between {min_words}-{max_words}. Current: {total_words}."
            )

        sections_count = len(blog_post.sections)
        if sections_count < profile["sections_min"] or sections_count > profile["sections_max"]:
            issues.append(
                f"Section count should be within {profile['sections_label']}. Current: {sections_count}."
            )

        min_section_words = profile["min_section_words"]
        for idx, section in enumerate(blog_post.sections, start=1):
            section_words = len(section.body_markdown.split())
            if section_words < min_section_words:
                issues.append(
                    f"Section {idx} ('{section.heading}') is too short ({section_words} words). "
                    f"Minimum is {min_section_words} words."
                )

        heading_text = " ".join(section.heading.lower() for section in blog_post.sections)
        if not any(
            marker in heading_text
            for marker in (
                "conclusion",
                "final thoughts",
                "next steps",
                "call to action",
                "cta",
            )
        ):
            issues.append("Include a clear conclusion or call-to-action section heading.")

        blog_text = extract_blog_plaintext(blog_post)
        current_year = datetime.now(timezone.utc).year
        stale_year_hits = sorted(
            {
                int(y)
                for y in re.findall(r"\b20\d{2}\b", blog_text)
                if int(y) < current_year
            }
        )
        if stale_year_hits:
            issues.append(
                f"Avoid outdated year references ({', '.join(map(str, stale_year_hits[:4]))}); "
                f"use {current_year} for current guidance unless explicitly historical."
            )

        readability = analyze_readability(blog_text)
        if readability.get("is_hard_to_read"):
            issues.append(
                "Improve readability: simplify sentence structure and reduce complexity."
            )

        trope_hits = find_ai_tropes(blog_text)
        if trope_hits:
            issues.append(
                "Remove AI-sounding clichés/tropes: " + ", ".join(trope_hits[:5])
            )

        issues.extend(seo_quality_issues(blog_post, keywords))

        return issues

    def build_quality_report(
        self,
        blog_post: BlogPost,
        word_count: str,
        keywords: Optional[list[str]] = None,
        phase_metrics: Optional[dict[str, Any]] = None,
    ) -> dict:
        """
        Build a deterministic quality report for API consumers.
        """
        body_word_count = self._count_total_words(blog_post)
        full_text = extract_blog_plaintext(blog_post)
        readability = analyze_readability(full_text)
        trope_hits = find_ai_tropes(full_text)
        seo_issues = seo_quality_issues(blog_post, keywords)
        all_issues = self._collect_quality_issues(
            blog_post=blog_post,
            word_count=word_count,
            keywords=keywords,
        )

        section_word_counts = [
            {
                "heading": section.heading,
                "word_count": len(section.body_markdown.split()),
            }
            for section in blog_post.sections
        ]

        return {
            "target_length": word_count,
            "body_word_count": body_word_count,
            "section_count": len(blog_post.sections),
            "section_word_counts": section_word_counts,
            "readability": readability,
            "ai_trope_hits": trope_hits,
            "seo_issues": seo_issues,
            "issues": all_issues,
            "passed": len(all_issues) == 0,
            "phase_metrics": phase_metrics or {},
        }

    @staticmethod
    def _clamp_str(value: str, min_len: int, max_len: int, pad_suffix: str = ".") -> str:
        """
        Clamp a string to [min_len, max_len].
        """
        value = value.strip()
        if len(value) > max_len:
            truncated = value[:max_len]
            last_space = truncated.rfind(" ")
            value = (
                truncated[:last_space].rstrip(" .,;:")
                if last_space > max_len // 2
                else truncated
            )
        while len(value) < min_len:
            value += pad_suffix
        return value

    def _validate_and_create_blog_post(self, data: dict) -> BlogPost:
        """
        Normalise and clamp parsed LLM data, then create a validated BlogPost.
        """
        title = (data.get("title") or "").strip()
        if not title:
            raise ValueError("Generated JSON is missing required field: title")

        summary = (data.get("summary") or "").strip()
        if not summary:
            raise ValueError("Generated JSON is missing required field: summary")

        seo_title = (data.get("seo_title") or "").strip()
        if not seo_title:
            seo_title = title

        seo_description = (data.get("seo_description") or "").strip()
        if not seo_description:
            seo_description = summary

        title = self._normalize_timeliness_title(title)
        seo_title = self._normalize_timeliness_title(seo_title)

        title = self._clamp_str(title, 10, 150)
        summary = self._clamp_str(summary, 50, 500)
        seo_title = self._clamp_str(seo_title, 15, 80)
        seo_description = self._clamp_str(seo_description, 50, 250)

        raw_slug = (data.get("slug") or "").strip()
        slug = self._generate_slug(raw_slug or title)

        sections = []
        for section_data in data.get("sections", []):
            if isinstance(section_data, dict):
                heading = (section_data.get("heading") or "").strip()
                body = (section_data.get("body_markdown") or "").strip()
                if heading and body:
                    sections.append(
                        BlogSection(
                            heading=heading,
                            body_markdown=self._normalize_section_markdown(body),
                        )
                    )
            elif isinstance(section_data, BlogSection):
                sections.append(
                    BlogSection(
                        heading=section_data.heading,
                        body_markdown=self._normalize_section_markdown(
                            section_data.body_markdown
                        ),
                    )
                )

        if not sections:
            raise ValueError("Generated JSON has no valid sections")

        raw_tags = data.get("tags") or []
        tags = list(
            dict.fromkeys(
                t.strip().lower() for t in raw_tags if isinstance(t, str) and t.strip()
            )
        )
        if len(tags) < 2:
            fallback = [w.lower() for w in re.split(r"\W+", title) if len(w) > 3][:3]
            tags = list(dict.fromkeys(tags + fallback))[:8]

        return BlogPost(
            title=title,
            slug=slug,
            summary=summary,
            sections=sections,
            tags=tags,
            seo_title=seo_title,
            seo_description=seo_description,
            hero_image_prompt=data.get("hero_image_prompt"),
            sources=data.get("sources"),
        )

    def _generate_slug(self, title: str) -> str:
        """Generate a URL-friendly slug from title."""
        slug = title.lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        return slug.strip("-")[:50]

    @staticmethod
    def _normalize_timeliness_title(text: str) -> str:
        """
        Replace stale year labels in titles (e.g., "2024 Guide") with current year.
        """
        if not text:
            return text

        current_year = datetime.now(timezone.utc).year
        if not re.search(
            r"\b(guide|trends?|forecast|strategy|playbook|tips|best|complete)\b",
            text,
            flags=re.IGNORECASE,
        ):
            return text

        def _repl(match: re.Match[str]) -> str:
            yr = int(match.group(0))
            if yr < current_year:
                return str(current_year)
            return match.group(0)

        return re.sub(r"\b20\d{2}\b", _repl, text)

    @staticmethod
    def _normalize_inline_ordered_lists(text: str) -> str:
        """
        Convert collapsed inline ordered lists to proper markdown list lines.
        """
        if not text or text.count(". ") < 2:
            return text

        paragraphs = re.split(r"\n\s*\n", text.strip())
        normalized_paragraphs: list[str] = []

        for para in paragraphs:
            markers = list(re.finditer(r"(?<!\d)(\d{1,2})\.\s+", para))
            if len(markers) < 2:
                normalized_paragraphs.append(para)
                continue

            line_start_markers = re.findall(r"(?m)^\s*\d+\.\s+", para)
            if len(line_start_markers) >= 2:
                normalized_paragraphs.append(para)
                continue

            first_idx = markers[0].start()
            prefix = para[:first_idx].rstrip()
            if first_idx > 30 and not prefix.endswith(":"):
                normalized_paragraphs.append(para)
                continue

            items: list[str] = []
            for i, marker in enumerate(markers):
                start = marker.start()
                end = markers[i + 1].start() if i + 1 < len(markers) else len(para)
                item = para[start:end].strip()
                item = re.sub(r"[ \t]+", " ", item)
                items.append(item)

            list_block = "\n".join(items)
            if prefix:
                normalized_paragraphs.append(f"{prefix}\n\n{list_block}")
            else:
                normalized_paragraphs.append(list_block)

        return "\n\n".join(normalized_paragraphs)

    def _normalize_section_markdown(self, body_markdown: str) -> str:
        text = body_markdown.strip()
        text = self._normalize_inline_ordered_lists(text)
        return text

    async def generate(
        self,
        topic: str,
        blog_type: str = "how-to",
        keywords: Optional[list[str]] = None,
        audience: Optional[str] = None,
        word_count: str = "medium",
        tone: str = "professional",
        language: str = "en-US",
        model: str = DEFAULT_MODEL,
        creativity: float = 0.7,
        web_search_mode: str = "basic",
        execution_mode: str = "strict",
    ) -> tuple[BlogPost, float, bool, list[dict] | None]:
        """
        Generate a complete blog post with configurable web search.

        Returns:
            Tuple of (BlogPost, generation_time, web_search_used, sources)
        """
        start_time = time.time()
        perf_start = time.perf_counter()

        effective_execution_mode = self._resolve_execution_mode(
            execution_mode=execution_mode,
        )

        self._last_phase_metrics = {
            "timings_ms": {},
            "usage": {},
            "revision_applied": False,
            "web_grounding": {
                "ddg_attempted": web_search_mode == "basic",
                "ddg_used": False,
                "online_used": False,
            },
            "model_runtime": {
                "requested_model": model,
                "model_used": None,
                "effective_model": None,
                "execution_mode": effective_execution_mode,
                "execution_path": None,
                "attempted_models": [],
                "fallback_used": False,
            },
            "errors": [],
            "runtime_capabilities": self._runtime_caps,
        }

        sources: list[dict] | None = None
        web_search_used = False

        with ai_span("blog_agent.generate", model=model, mode=effective_execution_mode):
            # ── Phase 1: Research ───────────────────────────────────────
            phase_start = time.perf_counter()
            with ai_span("blog_agent.research", web_search_mode=web_search_mode):
                web_context, sources, ddg_used = self._research_phase(
                    topic=topic,
                    keywords=keywords,
                    web_search_mode=web_search_mode,
                    blog_type=blog_type,
                )
            web_search_used = web_search_used or ddg_used
            self._last_phase_metrics["timings_ms"]["research"] = round(
                (time.perf_counter() - phase_start) * 1000, 2
            )
            self._last_phase_metrics["web_grounding"]["ddg_used"] = ddg_used

            # ── Phase 2: Prompt Preparation ─────────────────────────────
            phase_start = time.perf_counter()
            use_online = web_search_mode == "enhanced"
            web_search_used = web_search_used or use_online
            self._last_phase_metrics["web_grounding"]["online_used"] = use_online

            execution_path = self._resolve_execution_path(model)
            model_chain = build_blog_model_chain(
                selected_model=model,
                execution_mode=effective_execution_mode,
                path=execution_path,
                use_online=use_online,
            )
            if not model_chain:
                raise ValueError(
                    f"Model '{model}' is incompatible with execution path '{execution_path}'."
                )

            profile = self._get_length_profile(word_count)
            keywords_text = ", ".join(keywords or []) if keywords else "not specified"
            section_guidance = self._build_outline_guidance(
                topic=topic,
                blog_type=blog_type,
                keywords=keywords,
                sources=sources,
                word_count=word_count,
            )
            prompt = self._build_blog_prompt(
                topic=topic,
                blog_type=blog_type,
                keywords=keywords,
                audience=audience,
                word_count=word_count,
                tone=tone,
                language=language,
            )

            deps = BlogGenerationDeps(
                current_date_utc=datetime.now(timezone.utc).isoformat(),
                current_year=datetime.now(timezone.utc).year,
                topic=topic,
                blog_type=blog_type,
                keywords_text=keywords_text,
                tone=tone,
                language=language,
                length_tier=word_count,
                section_guidance=section_guidance,
                search_context=web_context,
                timeliness_rules=self._build_timeliness_rules(),
                markdown_rules=self._build_markdown_rules(),
            )
            self._last_phase_metrics["timings_ms"]["outline"] = round(
                (time.perf_counter() - phase_start) * 1000, 2
            )
            self._last_phase_metrics["model_runtime"]["execution_path"] = execution_path

            # ── Phase 3: Draft Generation ──────────────────────────────
            phase_start = time.perf_counter()
            with ai_span(
                "blog_agent.draft",
                execution_path=execution_path,
                execution_mode=effective_execution_mode,
            ):
                if execution_path == "structured":
                    draft_post, draft_usage, effective_model_id, attempted_models, errors = (
                        await self._run_structured_runner(
                            model_ids=model_chain,
                            prompt=prompt,
                            deps=deps,
                            creativity=creativity,
                            max_tokens=int(profile["max_tokens"]),
                            execution_mode=effective_execution_mode,
                        )
                    )
                else:
                    draft_post, draft_usage, effective_model_id, attempted_models, errors = (
                        await self._run_compat_json_runner(
                            model_ids=model_chain,
                            prompt=prompt,
                            deps=deps,
                            creativity=creativity,
                            max_tokens=int(profile["max_tokens"]),
                            execution_mode=effective_execution_mode,
                        )
                    )

            self._last_phase_metrics["timings_ms"]["draft"] = round(
                (time.perf_counter() - phase_start) * 1000, 2
            )
            self._last_phase_metrics["usage"]["draft"] = draft_usage
            self._last_phase_metrics["errors"] = errors
            self._last_phase_metrics["model_runtime"].update(
                {
                    "attempted_models": attempted_models,
                    "model_used": effective_model_id,
                    "effective_model": effective_model_id,
                    "fallback_used": (
                        len(attempted_models) > 1 and effective_model_id != attempted_models[0]
                    ),
                }
            )

            # ── Phase 4: Editorial Review ───────────────────────────────
            phase_start = time.perf_counter()
            quality_issues = self._collect_quality_issues(
                blog_post=draft_post,
                word_count=word_count,
                keywords=keywords,
            )
            if quality_issues:
                logger.info("Quality advisory (no revision): %s", quality_issues)
            self._last_phase_metrics["timings_ms"]["editorial"] = round(
                (time.perf_counter() - phase_start) * 1000, 2
            )
            self._last_phase_metrics["usage"]["editorial"] = None
            self._last_phase_metrics["revision_applied"] = False
            self._last_phase_metrics["timings_ms"]["total"] = round(
                (time.perf_counter() - perf_start) * 1000, 2
            )

            # Attach sources to the blog post if web search was used
            if web_search_used and sources:
                draft_post.sources = sources

            generation_time = time.time() - start_time
            return draft_post, generation_time, web_search_used, sources

    def _get_max_tokens(self, word_count: str) -> int:
        profile = self._get_length_profile(word_count)
        return int(profile["max_tokens"])

    def blog_post_to_html(self, blog_post: BlogPost) -> str:
        """
        Convert a BlogPost to HTML content for publishing.
        """
        import markdown

        html_parts = []

        if blog_post.summary:
            html_parts.append(f"<p class='lead'>{blog_post.summary}</p>")

        for section in blog_post.sections:
            html_parts.append(f"<h2>{section.heading}</h2>")
            normalized_section = self._normalize_section_markdown(
                section.body_markdown
            )
            section_html = markdown.markdown(
                normalized_section,
                extensions=["extra", "codehilite", "toc"],
            )
            html_parts.append(section_html)

        return "\n".join(html_parts)

    def blog_post_to_markdown(self, blog_post: BlogPost) -> str:
        """
        Convert a BlogPost to full markdown content.
        """
        md_parts = []

        md_parts.append(f"# {blog_post.title}\n")

        if blog_post.summary:
            md_parts.append(f"*{blog_post.summary}*\n")

        for section in blog_post.sections:
            md_parts.append(f"## {section.heading}\n")
            md_parts.append(section.body_markdown)
            md_parts.append("")

        return "\n".join(md_parts)
