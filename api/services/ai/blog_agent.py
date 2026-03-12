"""
Blog Agent Service - PydanticAI-powered blog post generation with web search.

This service generates complete, structured blog posts using PydanticAI agents
with optional web search capabilities for research-backed content.
"""

import asyncio
import json
import logging
import re
import time
from typing import Any, Optional

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from core.config import settings
from schemas.ai import BlogPost, BlogSection
from .tools import ToolHandler
from .llm_config import get_model, get_model_with_online, DEFAULT_MODEL
from .quality_tools import (
    analyze_readability,
    extract_blog_plaintext,
    find_ai_tropes,
    seo_quality_issues,
)
from .web_search import WebSearchService

logger = logging.getLogger(__name__)


class BlogAgentService:
    """
    Service for generating complete, structured blog posts using PydanticAI.
    Models are provided by the centralized LLM config (llm_config.py).
    """

    def __init__(self):
        self.tool_config = ToolHandler.get_tool("blog-agent")
        if not self.tool_config:
            raise ValueError("blog-agent tool configuration not found")
        
        self.system_prompt = self.tool_config["system_prompt"]
        self._last_phase_metrics: dict[str, Any] = {}
        self._structured_retries = 2
        self._text_fallback_attempts = 2

    def get_last_phase_metrics(self) -> dict[str, Any]:
        return dict(self._last_phase_metrics)

    def _get_model_for_name(self, model_name: str):
        """Delegate to centralized LLM config (single source of truth)."""
        return get_model(model_name)

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
        Build the prompt for blog generation using the tool config.
        """
        # Map word_count to descriptive text
        word_count_map = {
            "short": "around 300 words",
            "medium": "around 500 words",
            "long": "around 1000 words",
            "very-long": "1500+ words",
        }

        params = {
            "topic": topic,
            "blog_type": blog_type,
            "keywords": ", ".join(keywords) if keywords else "Not specified",
            "audience": audience or "General audience",
            "word_count": word_count_map.get(word_count, "around 500 words"),
            "tone": tone,
        }

        # Build the prompt from tool config
        prompt = self.tool_config["prompt"].format(**params)

        # Add language instruction if not English
        if language != "en-US":
            prompt += f"\n\nIMPORTANT: Write all content in {language}."

        return prompt

    def _build_outline_guidance(
        self,
        topic: str,
        blog_type: str,
        keywords: Optional[list[str]],
        sources: Optional[list[dict]],
    ) -> str:
        """
        Build explicit outline guidance for the draft phase.
        This is a lightweight "outline phase" that improves structure deterministically.
        """
        keywords_text = ", ".join(keywords or []) if keywords else "not specified"
        source_titles: list[str] = []
        for source in (sources or [])[:4]:
            title = source.get("title") if isinstance(source, dict) else None
            if isinstance(title, str) and title.strip():
                source_titles.append(title.strip())

        if blog_type in ("how-to", "tutorial"):
            sections = [
                "Introduction",
                "Foundations and Key Concepts",
                "Step-by-Step Implementation",
                "Common Mistakes and Fixes",
                "Conclusion and Next Steps",
            ]
        elif blog_type in ("comparison", "review"):
            sections = [
                "Introduction",
                "Evaluation Criteria",
                "Side-by-Side Analysis",
                "Recommendations",
                "Conclusion and Call to Action",
            ]
        else:
            sections = [
                "Introduction",
                "Core Insights",
                "Practical Applications",
                "Strategic Recommendations",
                "Conclusion and Next Steps",
            ]

        lines = [
            "\n\nSTRUCTURE GUIDANCE:",
            f"- Topic focus: {topic}",
            f"- Blog type: {blog_type}",
            f"- Primary keywords: {keywords_text}",
            "- Use these section headings (or close equivalents):",
        ]
        lines.extend([f"  - {section}" for section in sections])

        if source_titles:
            lines.append("- Ground examples or claims in these source themes:")
            lines.extend([f"  - {title}" for title in source_titles])

        return "\n".join(lines)

    def _research_phase(
        self,
        topic: str,
        keywords: Optional[list[str]],
        web_search_mode: str,
    ) -> tuple[str, list[dict] | None, bool]:
        """
        Research phase: gather external context using DuckDuckGo when enabled.
        """
        use_ddg = web_search_mode in ("basic", "full")
        web_context = ""
        web_search_used = False
        sources: list[dict] | None = None

        if not use_ddg:
            return web_context, sources, web_search_used

        try:
            search_svc = WebSearchService(max_results=5)
            search_results = search_svc.search_for_topic(topic, keywords)
            web_context = search_svc.format_as_context(search_results)
            sources = search_results.get("sources", [])
            if sources:
                web_search_used = True
                logger.info(
                    f"DuckDuckGo found {len(sources)} sources for topic: {topic}"
                )
        except Exception as e:
            logger.warning(f"DuckDuckGo search failed, proceeding without: {e}")

        return web_context, sources, web_search_used

    def _select_model_phase(self, model: str, web_search_mode: str):
        """
        Model selection phase: optionally enable OpenRouter online grounding.
        """
        use_online = web_search_mode in ("enhanced", "full")
        if use_online:
            try:
                logger.info(f"Using OpenRouter :online model for: {model}")
                return get_model_with_online(model), True
            except Exception as e:
                logger.warning(f":online model failed, falling back to standard: {e}")
                return self._get_model_for_name(model), False
        return self._get_model_for_name(model), False

    async def _draft_phase(
        self,
        pydantic_model,
        prompt: str,
        creativity: float,
        word_count: str,
    ) -> tuple[BlogPost, dict[str, Any] | None]:
        """
        Draft phase: perform the initial full article generation.
        """
        return await self._run_generation_once(
            pydantic_model=pydantic_model,
            prompt=prompt,
            creativity=creativity,
            word_count=word_count,
        )

    async def _editorial_phase(
        self,
        pydantic_model,
        base_prompt: str,
        blog_post: BlogPost,
        creativity: float,
        word_count: str,
        keywords: Optional[list[str]],
        draft_elapsed_s: float = 0.0,
    ) -> tuple[BlogPost, dict[str, Any] | None, bool]:
        """
        Editorial phase: deterministic quality checks and one corrective revision.

        If draft_elapsed_s is already above 60 s we skip the editorial revision
        to stay well within the 300 s frontend timeout.
        """
        quality_issues = self._collect_quality_issues(
            blog_post=blog_post,
            word_count=word_count,
            keywords=keywords,
        )
        if not quality_issues:
            return blog_post, None, False

        if draft_elapsed_s >= 60.0:
            logger.warning(
                "Skipping editorial revision — draft already took %.1fs (issues: %s)",
                draft_elapsed_s,
                quality_issues,
            )
            return blog_post, None, False

        revision_prompt = self._build_quality_revision_prompt(
            base_prompt=base_prompt,
            previous_output=blog_post,
            issues=quality_issues,
        )
        revised_blog_post, editorial_usage = await self._run_generation_once(
            pydantic_model=pydantic_model,
            prompt=revision_prompt,
            creativity=max(0.2, min(creativity, 0.8)),
            word_count=word_count,
        )
        revised_issues = self._collect_quality_issues(
            blog_post=revised_blog_post,
            word_count=word_count,
            keywords=keywords,
        )
        if revised_issues:
            # Return the revised post anyway — the issues are logged for
            # visibility but we don't hard-fail after a single retry.
            logger.warning(
                "Editorial revision still has issues (returning revised post): %s",
                revised_issues,
            )

        return revised_blog_post, editorial_usage, True

    def _parse_json_from_text(self, text: str) -> dict:
        """
        Extract and parse JSON from model output text.
        Handles cases where the model wraps JSON in markdown code blocks.
        """
        # Try to find JSON in code blocks first
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if json_match:
            text = json_match.group(1)

        # Clean up common issues
        text = text.strip()
        
        # Try to find JSON object boundaries
        start_idx = text.find("{")
        end_idx = text.rfind("}")
        
        if start_idx != -1 and end_idx != -1:
            text = text[start_idx : end_idx + 1]

        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON from model output: {e}")

    def _count_total_words(self, blog_post: BlogPost) -> int:
        return sum(len(section.body_markdown.split()) for section in blog_post.sections)

    def _collect_quality_issues(
        self,
        blog_post: BlogPost,
        word_count: str,
        keywords: Optional[list[str]] = None,
    ) -> list[str]:
        issues: list[str] = []

        # Target word-count ranges by requested length.
        # These are intentionally generous — the model regularly lands above
        # the old tight ceilings and we prefer content over strict trimming.
        target_ranges = {
            "short": (200, 600),
            "medium": (350, 900),
            "long": (700, 1600),
            "very-long": (1100, 8000),
        }
        min_words, max_words = target_ranges.get(word_count, target_ranges["medium"])
        total_words = self._count_total_words(blog_post)
        if total_words < min_words or total_words > max_words:
            issues.append(
                f"Total body word count must be between {min_words}-{max_words}. Current: {total_words}."
            )

        # Per-section quality floor (adaptive by target size)
        section_minimums = {
            "short": 30,
            "medium": 45,
            "long": 70,
            "very-long": 90,
        }
        min_section_words = section_minimums.get(word_count, 45)

        for idx, section in enumerate(blog_post.sections, start=1):
            section_words = len(section.body_markdown.split())
            if section_words < min_section_words:
                issues.append(
                    f"Section {idx} ('{section.heading}') is too short ({section_words} words). Minimum is {min_section_words} words."
                )

        heading_text = " ".join(section.heading.lower() for section in blog_post.sections)
        if not any(marker in heading_text for marker in ("conclusion", "final thoughts", "next steps", "call to action", "cta")):
            issues.append("Include a clear conclusion or call-to-action section heading.")

        blog_text = extract_blog_plaintext(blog_post)

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

    def _build_quality_revision_prompt(
        self,
        base_prompt: str,
        previous_output: BlogPost,
        issues: list[str],
    ) -> str:
        issue_lines = "\n".join(f"- {issue}" for issue in issues)
        previous_json = json.dumps(previous_output.model_dump(), ensure_ascii=False)
        return (
            f"{base_prompt}\n\n"
            "QUALITY REVISION REQUIRED:\n"
            "Your previous output failed these checks:\n"
            f"{issue_lines}\n\n"
            "Rewrite the entire blog post and fix every issue while preserving the topic and style. "
            "Return only valid JSON matching the required schema.\n\n"
            f"Previous output JSON:\n{previous_json}"
        )

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

    async def _run_generation_once(
        self,
        pydantic_model,
        prompt: str,
        creativity: float,
        word_count: str,
    ) -> tuple[BlogPost, dict[str, Any] | None]:
        # ── Attempt 1: structured output (tool_choice / function-calling) ──
        # Some OpenRouter-routed models return 404 for tool_choice; we catch
        # that gracefully and fall back to plain-text + JSON-parse.
        try:
            agent = Agent(
                pydantic_model,
                result_type=BlogPost,
                system_prompt=self.system_prompt,
                retries=self._structured_retries,
            )

            result = await agent.run(
                prompt,
                model_settings={
                    "temperature": creativity,
                    "max_tokens": self._get_max_tokens(word_count),
                },
            )
            return result.data, self._extract_usage_payload(result)
        except Exception as structured_error:
            # Log the structured-output failure (often a tool_choice 404 from
            # OpenRouter) and proceed to text-based fallback.
            logger.warning(
                "Structured output failed, falling back to text parsing: %s",
                structured_error,
            )

        # ── Attempt 2: plain-text generation + JSON extraction ──
        # Build an explicit, terse JSON-only prompt for the text fallback so
        # the model doesn't wrap its reply in prose or code fences.
        text_fallback_prompt = (
            f"{prompt}\n\n"
            "CRITICAL — OUTPUT FORMAT:\n"
            "Reply with ONLY a raw JSON object. No markdown fences, no explanatory"
            " text, no trailing commentary. Start your reply with `{` and end with `}`.\n"
            "Required top-level keys: title, slug, summary, sections, tags, "
            "seo_title, seo_description."
        )

        last_text_error: Exception | None = None
        for attempt in range(1, self._text_fallback_attempts + 1):
            try:
                # Brief back-off before each attempt: prevents hitting the
                # provider rate-limit that causes empty responses.
                if attempt > 1:
                    await asyncio.sleep(attempt * 2)

                agent = Agent(
                    pydantic_model,
                    result_type=str,
                    system_prompt=self.system_prompt,
                    retries=1,
                )

                result = await agent.run(
                    text_fallback_prompt,
                    model_settings={
                        "temperature": creativity,
                        "max_tokens": self._get_max_tokens(word_count),
                    },
                )

                raw = result.data if isinstance(result.data, str) else ""
                if not raw.strip():
                    raise ValueError("Received empty model response")

                parsed_data = self._parse_json_from_text(raw)
                return (
                    self._validate_and_create_blog_post(parsed_data),
                    self._extract_usage_payload(result),
                )
            except Exception as text_error:
                last_text_error = text_error
                logger.warning(
                    "Text fallback attempt %s/%s failed: %s",
                    attempt,
                    self._text_fallback_attempts,
                    text_error,
                )

        raise ValueError(
            "Blog generation failed after both structured and text-based attempts. "
            f"Text parsing error: {last_text_error}"
        )

    @staticmethod
    def _clamp_str(value: str, min_len: int, max_len: int, pad_suffix: str = ".") -> str:
        """
        Clamp a string to [min_len, max_len].
        - Truncate at max_len (at a word boundary where possible).
        - Pad with pad_suffix if shorter than min_len (shouldn't happen in
          practice after the model call, but guards against edge cases).
        """
        value = value.strip()
        if len(value) > max_len:
            # Try to truncate at the last space before max_len
            truncated = value[:max_len]
            last_space = truncated.rfind(" ")
            value = truncated[:last_space].rstrip(" .,;:") if last_space > max_len // 2 else truncated
        while len(value) < min_len:
            value += pad_suffix
        return value

    def _validate_and_create_blog_post(self, data: dict) -> BlogPost:
        """
        Normalise and clamp parsed LLM data, then create a validated BlogPost.

        This layer handles near-misses — e.g. a seo_title that is 82 chars
        instead of ≤80 — without throwing away otherwise good content.
        """
        title = (data.get("title") or "").strip()
        if not title:
            raise ValueError("Generated JSON is missing required field: title")

        summary = (data.get("summary") or "").strip()
        if not summary:
            raise ValueError("Generated JSON is missing required field: summary")

        seo_title = (data.get("seo_title") or "").strip()
        if not seo_title:
            # Fall back to the post title if seo_title is absent
            seo_title = title

        seo_description = (data.get("seo_description") or "").strip()
        if not seo_description:
            # Fall back to the summary if seo_description is absent
            seo_description = summary

        # Clamp strings to schema bounds so near-misses don't fail validation
        title = self._clamp_str(title, 10, 150)
        summary = self._clamp_str(summary, 50, 500)
        seo_title = self._clamp_str(seo_title, 15, 80)
        seo_description = self._clamp_str(seo_description, 50, 250)

        # Normalise slug
        raw_slug = (data.get("slug") or "").strip()
        slug = self._generate_slug(raw_slug or title)

        # Build sections
        sections = []
        for section_data in data.get("sections", []):
            if isinstance(section_data, dict):
                heading = (section_data.get("heading") or "").strip()
                body = (section_data.get("body_markdown") or "").strip()
                if heading and body:
                    sections.append(BlogSection(heading=heading, body_markdown=body))
            elif isinstance(section_data, BlogSection):
                sections.append(section_data)

        if not sections:
            raise ValueError("Generated JSON has no valid sections")

        # Normalise tags: ensure at least 2 unique lower-cased tags
        raw_tags = data.get("tags") or []
        tags = list(dict.fromkeys(
            t.strip().lower() for t in raw_tags if isinstance(t, str) and t.strip()
        ))
        if len(tags) < 2:
            # Derive fallback tags from the title words
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
    ) -> tuple[BlogPost, float, bool, list[dict] | None]:
        """
        Generate a complete blog post with configurable web search.

        web_search_mode:
            - "off"      — no web search
            - "basic"    — DuckDuckGo context injection (free)
            - "enhanced" — OpenRouter :online native grounding
            - "full"     — both DuckDuckGo + :online
        
        Returns:
            Tuple of (BlogPost, generation_time, web_search_used, sources)
        """
        start_time = time.time()
        perf_start = time.perf_counter()
        web_search_used = False
        sources: list[dict] | None = None
        self._last_phase_metrics = {
            "timings_ms": {},
            "usage": {},
            "revision_applied": False,
            "web_grounding": {
                "ddg_used": False,
                "online_used": False,
            },
        }

        # ── Phase 1: Research ───────────────────────────────────────
        phase_start = time.perf_counter()
        web_context, sources, ddg_used = self._research_phase(
            topic=topic,
            keywords=keywords,
            web_search_mode=web_search_mode,
        )
        web_search_used = web_search_used or ddg_used
        self._last_phase_metrics["timings_ms"]["research"] = round(
            (time.perf_counter() - phase_start) * 1000, 2
        )
        self._last_phase_metrics["web_grounding"]["ddg_used"] = ddg_used

        # ── Phase 2: Outline Guidance ───────────────────────────────
        phase_start = time.perf_counter()
        prompt = self._build_blog_prompt(
            topic=topic,
            blog_type=blog_type,
            keywords=keywords,
            audience=audience,
            word_count=word_count,
            tone=tone,
            language=language,
        )

        prompt += self._build_outline_guidance(
            topic=topic,
            blog_type=blog_type,
            keywords=keywords,
            sources=sources,
        )

        # Append web research context if available
        if web_context:
            prompt += web_context
        self._last_phase_metrics["timings_ms"]["outline"] = round(
            (time.perf_counter() - phase_start) * 1000, 2
        )

        # ── Phase 3: Model Selection + Draft ────────────────────────
        phase_start = time.perf_counter()
        pydantic_model, online_used = self._select_model_phase(
            model=model,
            web_search_mode=web_search_mode,
        )
        web_search_used = web_search_used or online_used
        self._last_phase_metrics["timings_ms"]["model_selection"] = round(
            (time.perf_counter() - phase_start) * 1000, 2
        )
        self._last_phase_metrics["web_grounding"]["online_used"] = online_used

        phase_start = time.perf_counter()
        draft_post, draft_usage = await self._draft_phase(
            pydantic_model=pydantic_model,
            prompt=prompt,
            creativity=creativity,
            word_count=word_count,
        )
        self._last_phase_metrics["timings_ms"]["draft"] = round(
            (time.perf_counter() - phase_start) * 1000, 2
        )
        self._last_phase_metrics["usage"]["draft"] = draft_usage

        # ── Phase 4: Editorial Review ───────────────────────────────
        draft_elapsed_s = time.perf_counter() - perf_start
        phase_start = time.perf_counter()
        blog_post, editorial_usage, revision_applied = await self._editorial_phase(
            pydantic_model=pydantic_model,
            base_prompt=prompt,
            blog_post=draft_post,
            creativity=creativity,
            word_count=word_count,
            keywords=keywords,
            draft_elapsed_s=draft_elapsed_s,
        )
        self._last_phase_metrics["timings_ms"]["editorial"] = round(
            (time.perf_counter() - phase_start) * 1000, 2
        )
        self._last_phase_metrics["usage"]["editorial"] = editorial_usage
        self._last_phase_metrics["revision_applied"] = revision_applied
        self._last_phase_metrics["timings_ms"]["total"] = round(
            (time.perf_counter() - perf_start) * 1000, 2
        )

        # Attach sources to the blog post if web search was used
        if web_search_used and sources:
            blog_post.sources = sources

        generation_time = time.time() - start_time
        return blog_post, generation_time, web_search_used, sources

    def _get_max_tokens(self, word_count: str) -> int:
        """Get max tokens based on target word count."""
        return {
            "short": 2000,
            "medium": 4000,
            "long": 6000,
            "very-long": 8000,
        }.get(word_count, 4000)

    def blog_post_to_html(self, blog_post: BlogPost) -> str:
        """
        Convert a BlogPost to HTML content for publishing.
        """
        import markdown

        html_parts = []

        # Add summary as intro paragraph
        if blog_post.summary:
            html_parts.append(f"<p class='lead'>{blog_post.summary}</p>")

        # Convert each section
        for section in blog_post.sections:
            html_parts.append(f"<h2>{section.heading}</h2>")
            # Convert markdown body to HTML
            section_html = markdown.markdown(
                section.body_markdown,
                extensions=["extra", "codehilite", "toc"],
            )
            html_parts.append(section_html)

        return "\n".join(html_parts)

    def blog_post_to_markdown(self, blog_post: BlogPost) -> str:
        """
        Convert a BlogPost to full markdown content.
        """
        md_parts = []

        # Title
        md_parts.append(f"# {blog_post.title}\n")

        # Summary
        if blog_post.summary:
            md_parts.append(f"*{blog_post.summary}*\n")

        # Sections
        for section in blog_post.sections:
            md_parts.append(f"## {section.heading}\n")
            md_parts.append(section.body_markdown)
            md_parts.append("")  # Empty line between sections

        return "\n".join(md_parts)
