"""
Blog Agent Service - PydanticAI-powered blog post generation with optional
DuckDuckGo research.
"""

import asyncio
import json
import logging
import re
import time
from typing import Any, Optional

from pydantic_ai import Agent, NativeOutput

from core.config import settings
from schemas.ai import BlogPost, BlogSection
from .tools import ToolHandler
from .llm_config import get_model, get_blog_model_capabilities, DEFAULT_MODEL
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

    def _get_model_capabilities(self, model_name: str) -> dict[str, bool]:
        return get_blog_model_capabilities(model_name)

    def _build_blog_prompt(
        self,
        topic: str,
        blog_type: str,
        keywords: Optional[list[str]] = None,
        audience: Optional[str] = None,
        word_count: str = "medium",
        tone: str = "professional",
        language: str = "en-US",
        internal_linking_context: str = "",
    ) -> str:
        """
        Build the prompt for blog generation using the tool config.
        """
        # Map word_count to explicit body budgets. The quality checker uses
        # these same ranges, so the prompt should speak in the same terms.
        word_count_map = {
            "short": "200-600 total body words",
            "medium": "350-900 total body words",
            "long": "700-1600 total body words",
            "very-long": "1100-2500 total body words",
        }

        params = {
            "topic": topic,
            "blog_type": blog_type,
            "keywords": ", ".join(keywords) if keywords else "Not specified",
            "audience": audience or "General audience",
            "word_count": word_count_map.get(word_count, "around 500 words"),
            "tone": tone,
            "internal_linking_context": internal_linking_context,
        }

        # Build the prompt from tool config
        prompt = self.tool_config["prompt"].format(**params)
        if keywords:
            prompt += (
                "\n\nSEO REQUIREMENT: Use the primary keyword "
                f"'{keywords[0]}' naturally in both seo_title and seo_description. "
                "Do not keyword-stuff; one natural mention is enough."
            )

        # Add language instruction if not English
        if language != "en-US":
            prompt += f"\n\nIMPORTANT: Write all content in {language}."

        return prompt

    @staticmethod
    def _format_internal_linking_context(
        published_posts: list[dict] | None,
    ) -> str:
        if not published_posts:
            return (
                "## Existing Articles You Can Reference\n"
                "No existing published articles were provided. Do not invent internal /blog/ links."
            )

        grouped_posts: dict[str, list[dict]] = {}
        for post in published_posts:
            if not isinstance(post, dict):
                continue

            title = str(post.get("title") or "").strip()
            slug = str(post.get("slug") or "").strip().strip("/")
            if not title or not slug:
                continue

            category_name = str(
                post.get("category_name")
                or post.get("category")
                or (
                    f"Category {post.get('category_id')}"
                    if post.get("category_id") is not None
                    else "Uncategorized"
                )
            ).strip()
            grouped_posts.setdefault(category_name or "Uncategorized", []).append(
                {"title": title, "slug": slug}
            )

        if not grouped_posts:
            return (
                "## Existing Articles You Can Reference\n"
                "No valid published article targets were provided. Do not invent internal /blog/ links."
            )

        lines = [
            "## Existing Articles You Can Reference",
            "When the content naturally relates to one of these articles, add an internal link using <a href=\"/blog/{slug}\">natural anchor text</a>. Aim for 2-4 contextual internal links total.",
        ]
        for category_name in sorted(grouped_posts):
            lines.append(f"Category: {category_name}")
            for post in grouped_posts[category_name]:
                lines.append(f'- "{post["title"]}" -> /blog/{post["slug"]}')

        return "\n".join(lines)

    @staticmethod
    def _count_internal_links(blog_post: BlogPost) -> int:
        body = "\n".join(section.body_markdown for section in blog_post.sections)
        return len(
            re.findall(
                r"""href=["']/blog/[^"']+["']|\]\(/blog/[^)\s]+(?:\s+["'][^"']+["'])?\)""",
                body,
                flags=re.IGNORECASE,
            )
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
        Build explicit outline guidance for the draft phase.
        This is a lightweight "outline phase" that improves structure deterministically.
        """
        keywords_text = ", ".join(keywords or []) if keywords else "not specified"
        source_titles: list[str] = []
        for source in (sources or [])[:4]:
            title = source.get("title") if isinstance(source, dict) else None
            if isinstance(title, str) and title.strip():
                source_titles.append(title.strip())

        if word_count == "short":
            section_budget = "Use 3-4 sections. Keep each section body tight, roughly 60-140 words."
        elif word_count == "medium":
            section_budget = "Use 4-5 sections. Keep each section body roughly 80-180 words."
        elif word_count == "long":
            section_budget = "Use 5-7 sections. Develop each section with useful specifics."
        else:
            section_budget = "Use 6-8 sections. Keep depth high without repeating ideas."

        if blog_type in ("how-to", "tutorial"):
            sections = [
                "Why This Matters",
                "Step-by-Step Implementation",
                "Common Mistakes and Fixes",
                "What to Do Next",
            ]
        elif blog_type in ("comparison", "review"):
            sections = [
                "What Actually Matters",
                "Evaluation Criteria",
                "Side-by-Side Analysis",
                "Recommendations",
                "Final Verdict",
            ]
        else:
            sections = [
                "The Setup",
                "Core Insights",
                "Practical Applications",
                "Strategic Recommendations",
                "The Bottom Line",
            ]

        lines = [
            "\n\nSTRUCTURE GUIDANCE:",
            f"- Topic focus: {topic}",
            f"- Blog type: {blog_type}",
            f"- Primary keywords: {keywords_text}",
            f"- Length discipline: {section_budget}",
            "- Prefer specific, editorial headings over generic labels like 'Introduction' or 'Conclusion'.",
            "- Use headings in this spirit (adapt them to the topic):",
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
        use_web_search: bool,
    ) -> tuple[str, list[dict] | None, bool, bool]:
        """
        Research phase: gather external context using DuckDuckGo when enabled.
        """
        web_context = ""
        web_search_used = False
        ddg_attempted = False
        sources: list[dict] | None = None

        if not use_web_search:
            return web_context, sources, web_search_used, ddg_attempted

        ddg_attempted = True
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

        return web_context, sources, web_search_used, ddg_attempted

    async def _draft_phase(
        self,
        pydantic_model,
        model_capabilities: dict[str, bool],
        prompt: str,
        creativity: float,
        word_count: str,
    ) -> tuple[BlogPost, dict[str, Any] | None]:
        """
        Draft phase: perform the initial full article generation.
        """
        return await self._run_generation_once(
            pydantic_model=pydantic_model,
            model_capabilities=model_capabilities,
            prompt=prompt,
            creativity=creativity,
            word_count=word_count,
        )

    async def _editorial_phase(
        self,
        pydantic_model,
        model_capabilities: dict[str, bool],
        base_prompt: str,
        blog_post: BlogPost,
        creativity: float,
        word_count: str,
        keywords: Optional[list[str]],
        draft_elapsed_s: float = 0.0,
        published_posts_available: bool = False,
    ) -> tuple[BlogPost, dict[str, Any] | None, bool]:
        """
        Editorial phase: deterministic quality checks and one corrective revision.

        If draft_elapsed_s is already above the configured threshold, skip the editorial revision
        to stay well within the 300 s frontend timeout.
        """
        blog_post = self._enforce_body_word_ceiling(
            self._apply_quality_repairs(blog_post, keywords),
            word_count,
        )
        quality_issues = self._collect_quality_issues(
            blog_post=blog_post,
            word_count=word_count,
            keywords=keywords,
            published_posts_available=published_posts_available,
        )
        if not quality_issues:
            return blog_post, None, False

        if not settings.BLOG_AGENT_EDITORIAL_REVISION_ENABLED:
            logger.info(
                "Skipping editorial revision because BLOG_AGENT_EDITORIAL_REVISION_ENABLED=false "
                "(issues: %s)",
                quality_issues,
            )
            return blog_post, None, False

        if draft_elapsed_s >= settings.BLOG_AGENT_EDITORIAL_SKIP_AFTER_SECONDS:
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
            model_capabilities=model_capabilities,
            prompt=revision_prompt,
            creativity=max(0.2, min(creativity, 0.8)),
            word_count=word_count,
        )
        revised_blog_post = self._enforce_body_word_ceiling(
            self._apply_quality_repairs(revised_blog_post, keywords),
            word_count,
        )
        revised_issues = self._collect_quality_issues(
            blog_post=revised_blog_post,
            word_count=word_count,
            keywords=keywords,
            published_posts_available=published_posts_available,
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

    @staticmethod
    def _target_word_range(word_count: str) -> tuple[int, int]:
        target_ranges = {
            "short": (200, 600),
            "medium": (350, 900),
            "long": (700, 1600),
            "very-long": (1100, 8000),
        }
        return target_ranges.get(word_count, target_ranges["medium"])

    @staticmethod
    def _minimum_section_words(word_count: str) -> int:
        section_minimums = {
            "short": 30,
            "medium": 45,
            "long": 70,
            "very-long": 90,
        }
        return section_minimums.get(word_count, 45)

    def _enforce_body_word_ceiling(
        self,
        blog_post: BlogPost,
        word_count: str,
    ) -> BlogPost:
        _, max_words = self._target_word_range(word_count)
        excess_words = self._count_total_words(blog_post) - max_words
        if excess_words <= 0:
            return blog_post

        min_section_words = self._minimum_section_words(word_count)
        for section in reversed(blog_post.sections):
            if excess_words <= 0:
                break
            words = section.body_markdown.split()
            removable = max(0, len(words) - min_section_words)
            if removable <= 0:
                continue
            remove_count = min(removable, excess_words)
            remaining = words[:-remove_count]
            section.body_markdown = " ".join(remaining).rstrip(" ,;:")
            if section.body_markdown and section.body_markdown[-1] not in ".!?":
                section.body_markdown += "."
            excess_words -= remove_count

        return blog_post

    def _collect_quality_issues(
        self,
        blog_post: BlogPost,
        word_count: str,
        keywords: Optional[list[str]] = None,
        published_posts_available: bool = False,
    ) -> list[str]:
        issues: list[str] = []

        # Target word-count ranges by requested length.
        # These are intentionally generous — the model regularly lands above
        # the old tight ceilings and we prefer content over strict trimming.
        min_words, max_words = self._target_word_range(word_count)
        total_words = self._count_total_words(blog_post)
        if total_words < min_words or total_words > max_words:
            issues.append(
                f"Total body word count must be between {min_words}-{max_words}. Current: {total_words}."
            )

        # Per-section quality floor (adaptive by target size)
        min_section_words = self._minimum_section_words(word_count)

        for idx, section in enumerate(blog_post.sections, start=1):
            section_words = len(section.body_markdown.split())
            if section_words < min_section_words:
                issues.append(
                    f"Section {idx} ('{section.heading}') is too short ({section_words} words). Minimum is {min_section_words} words."
                )

        heading_text = " ".join(section.heading.lower() for section in blog_post.sections)
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

        if re.search(r"(?<=\S)\s+(?:—|–|--)\s+(?=\S)", blog_text):
            issues.append(
                "Avoid em dashes or dash-aside punctuation. Use commas, full stops, or parentheses instead."
            )

        issues.extend(seo_quality_issues(blog_post, keywords))

        if published_posts_available and self._count_internal_links(blog_post) == 0:
            issues.append(
                "Add 2-4 contextual internal links to the provided existing articles using /blog/{slug} URLs."
            )

        return issues

    def build_quality_report(
        self,
        blog_post: BlogPost,
        word_count: str,
        keywords: Optional[list[str]] = None,
        phase_metrics: Optional[dict[str, Any]] = None,
        published_posts_available: bool = False,
    ) -> dict:
        """
        Build a deterministic quality report for API consumers.
        """
        body_word_count = self._count_total_words(blog_post)
        full_text = extract_blog_plaintext(blog_post)
        readability = analyze_readability(full_text)
        trope_hits = find_ai_tropes(full_text)
        seo_issues = seo_quality_issues(blog_post, keywords)
        internal_link_count = self._count_internal_links(blog_post)
        all_issues = self._collect_quality_issues(
            blog_post=blog_post,
            word_count=word_count,
            keywords=keywords,
            published_posts_available=published_posts_available,
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
            "internal_link_count": internal_link_count,
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

    @staticmethod
    def _run_result_output(run_result: Any) -> Any:
        if hasattr(run_result, "output"):
            return run_result.output
        return getattr(run_result, "data", None)

    @staticmethod
    def _retry_delay_seconds(
        model_capabilities: dict[str, Any],
        attempt: int,
    ) -> float:
        configured_delay = model_capabilities.get("transient_retry_delay_seconds")
        try:
            delay = float(configured_delay)
        except (TypeError, ValueError):
            delay = 0.0
        if delay > 0:
            return delay
        return float(attempt * 2)

    def _build_model_settings(
        self,
        model_capabilities: dict[str, Any],
        creativity: float,
        word_count: str,
        *,
        force_json_object: bool = False,
    ) -> dict[str, Any]:
        settings_payload: dict[str, Any] = {
            "max_tokens": self._get_max_tokens(word_count, model_capabilities),
            "timeout": settings.AI_MODEL_REQUEST_TIMEOUT_SECONDS,
        }

        reasoning = model_capabilities.get("reasoning")
        if isinstance(reasoning, dict) and reasoning:
            settings_payload["openrouter_reasoning"] = reasoning

        provider_routing = model_capabilities.get("openrouter_provider")
        if isinstance(provider_routing, dict) and provider_routing:
            settings_payload["openrouter_provider"] = provider_routing

        if model_capabilities.get("send_temperature", True):
            settings_payload["temperature"] = creativity

        configured_extra_body = model_capabilities.get("extra_body")
        if isinstance(configured_extra_body, dict) and configured_extra_body:
            settings_payload["extra_body"] = self._deep_merge_dicts(
                settings_payload.get("extra_body", {}),
                configured_extra_body,
            )

        if force_json_object and model_capabilities.get("json_object_fallback", True):
            settings_payload["extra_body"] = self._deep_merge_dicts(
                settings_payload.get("extra_body", {}),
                {"response_format": {"type": "json_object"}},
            )

        return settings_payload

    @staticmethod
    def _deep_merge_dicts(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
        merged = dict(base)
        for key, value in overlay.items():
            existing = merged.get(key)
            if isinstance(existing, dict) and isinstance(value, dict):
                merged[key] = BlogAgentService._deep_merge_dicts(existing, value)
            else:
                merged[key] = value
        return merged

    async def _run_generation_once(
        self,
        pydantic_model,
        model_capabilities: dict[str, bool],
        prompt: str,
        creativity: float,
        word_count: str,
    ) -> tuple[BlogPost, dict[str, Any] | None]:
        # ── Attempt 1: native provider JSON schema ───────────────────
        # Use provider-enforced structured output where OpenRouter and the
        # model profile support it. This avoids the PromptedOutput validation
        # retry loop that can fail on reasoning models such as GPT-5.5.
        output_mode = str(model_capabilities.get("output_mode") or "")
        supports_native_schema = (
            output_mode == "native_json_schema"
            or bool(model_capabilities.get("supports_structured", False))
        )
        if supports_native_schema:
            try:
                agent = Agent(
                    pydantic_model,
                    output_type=NativeOutput(
                        BlogPost,
                        strict=False,
                        description=(
                            "A complete publication-ready blog post as JSON."
                        ),
                    ),
                    system_prompt=self.system_prompt,
                    retries=self._structured_retries,
                )

                result = await agent.run(
                    prompt,
                    model_settings=self._build_model_settings(
                        model_capabilities,
                        creativity,
                        word_count,
                    ),
                )
                structured_output = self._run_result_output(result)
                if isinstance(structured_output, BlogPost):
                    normalized_output = self._validate_and_create_blog_post(
                        structured_output.model_dump()
                    )
                elif isinstance(structured_output, dict):
                    normalized_output = self._validate_and_create_blog_post(structured_output)
                else:
                    raise ValueError(
                        f"Structured output returned unsupported payload type: {type(structured_output).__name__}"
                    )
                return normalized_output, self._extract_usage_payload(result)
            except Exception as structured_error:
                logger.warning(
                    "Native JSON schema output failed, falling back to raw JSON parsing: %s",
                    structured_error,
                )
        else:
            logger.info("Skipping native JSON schema for model without support")

        # ── Attempt 2: raw text JSON + local validation ──────────────
        # This deliberately avoids PromptedOutput. PromptedOutput asks
        # PydanticAI to validate/retry model outputs, which is the failure
        # path seen with GPT-5.5 through OpenRouter. Here the model returns
        # plain text, then we parse and normalize it locally.
        text_fallback_prompt = (
            f"{prompt}\n\n"
            "CRITICAL — OUTPUT FORMAT:\n"
            "Reply with ONLY a raw JSON object. No markdown fences, no explanatory"
            " text, no trailing commentary. Start your reply with `{` and end with `}`.\n"
            "Required top-level keys: title, slug, summary, sections, tags, "
            "seo_title, seo_description, hero_image_prompt."
        )

        last_text_error: Exception | None = None
        for attempt in range(1, self._text_fallback_attempts + 1):
            try:
                # Brief back-off before each attempt: prevents hitting the
                # provider rate-limit that causes empty responses.
                if attempt > 1:
                    await asyncio.sleep(
                        self._retry_delay_seconds(model_capabilities, attempt)
                    )

                agent = Agent(
                    pydantic_model,
                    output_type=str,
                    system_prompt=self.system_prompt,
                    retries=0,
                )

                result = await agent.run(
                    text_fallback_prompt,
                    model_settings=self._build_model_settings(
                        model_capabilities,
                        creativity,
                        word_count,
                        force_json_object=bool(
                            model_capabilities.get("supports_compat_json", False)
                        ),
                    ),
                )

                fallback_output = self._run_result_output(result)
                if isinstance(fallback_output, BlogPost):
                    parsed_data = fallback_output.model_dump()
                elif isinstance(fallback_output, dict):
                    parsed_data = fallback_output
                else:
                    raw = fallback_output if isinstance(fallback_output, str) else ""
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

    @staticmethod
    def _normalize_dash_punctuation(value: str) -> str:
        if not value:
            return value
        return re.sub(r"(?<=\S)\s+(?:—|–|--)\s+(?=\S)", ", ", value).strip()

    @staticmethod
    def _normalize_whitespace(value: str) -> str:
        return re.sub(r"\s+", " ", value).strip()

    def _normalize_seo_title(self, seo_title: str, fallback_title: str) -> str:
        normalized = self._normalize_whitespace(
            self._normalize_dash_punctuation(seo_title or fallback_title)
        )
        normalized = re.sub(
            r"\s*[\|\-–—:]\s*craftyxhub\s*$",
            "",
            normalized,
            flags=re.IGNORECASE,
        ).strip()
        fallback = self._normalize_whitespace(self._normalize_dash_punctuation(fallback_title))
        if len(normalized) < 45 and len(fallback) > len(normalized):
            normalized = fallback
        if len(normalized) < 45:
            for suffix in (" Guide", ": Practical Guide", " Tips", " Insights"):
                candidate = f"{normalized}{suffix}".strip()
                if 45 <= len(candidate) <= 65:
                    normalized = candidate
                    break
                if len(normalized) < len(candidate) <= 65:
                    normalized = candidate
        return self._clamp_str(normalized or fallback_title, 45, 65)

    def _normalize_seo_description(self, seo_description: str, fallback_summary: str) -> str:
        normalized = self._normalize_whitespace(
            self._normalize_dash_punctuation(seo_description or fallback_summary)
        )
        fallback = self._normalize_whitespace(self._normalize_dash_punctuation(fallback_summary))
        if len(normalized) < 110 and len(fallback) > len(normalized):
            normalized = fallback
        return self._clamp_str(normalized or fallback_summary, 90, 155)

    def _normalize_hero_image_prompt(
        self,
        hero_image_prompt: Optional[str],
        title: str,
        summary: str,
    ) -> str:
        prompt = self._normalize_whitespace(
            self._normalize_dash_punctuation(hero_image_prompt or "")
        )

        if not prompt:
            prompt = (
                f"Create a clean editorial hero image for '{title}'. "
                f"Visually represent this idea: {summary.rstrip('.')}."
            )

        requirements: list[str] = []
        lowered = prompt.lower()
        if not any(token in lowered for token in ("1200x630", "1.91:1", "1.91 to 1", "social card")):
            requirements.append("Use a 1200x630 landscape composition for social sharing")
        if not any(token in lowered for token in ("no logos", "without logos", "avoid logos")):
            requirements.append("no logos")
        if not any(token in lowered for token in ("no watermarks", "without watermarks", "avoid watermarks")):
            requirements.append("no watermarks")
        if not any(token in lowered for token in ("no text overlay", "no text", "without text overlay")):
            requirements.append("no text overlay")
        if "strong focal subject" not in lowered:
            requirements.append("strong focal subject")
        if "editorial" not in lowered:
            requirements.append("editorial style")

        if requirements:
            prompt = f"{prompt.rstrip('. ')}. {', '.join(requirements)}."

        return prompt

    @staticmethod
    def _replace_ai_tropes(value: str) -> str:
        replacements = {
            r"\bleveraging\b": "using",
            r"\bleveraged\b": "used",
            r"\bleverage\b": "use",
            r"\bdelve into\b": "examine",
            r"\bin the realm of\b": "in",
            r"\bit is worth noting\b": "note",
            r"\bgame[- ]changer\b": "major shift",
            r"\bgroundbreaking\b": "important",
            r"\bseamlessly\b": "smoothly",
            r"\bcutting[- ]edge\b": "modern",
            r"\bparamount\b": "essential",
            r"\bcomprehensive guides\b": "practical guides",
            r"\bcomprehensive guide\b": "practical guide",
        }
        cleaned = value
        for pattern, replacement in replacements.items():
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)
        return cleaned

    def _ensure_primary_keyword_in_seo(
        self,
        blog_post: BlogPost,
        keywords: Optional[list[str]],
    ) -> BlogPost:
        primary_keyword = (keywords or [None])[0]
        if not primary_keyword:
            return blog_post

        keyword = primary_keyword.strip()
        if not keyword:
            return blog_post

        if keyword.lower() not in blog_post.seo_title.lower():
            blog_post.seo_title = self._normalize_seo_title(
                f"{keyword.title()}: {blog_post.seo_title}",
                blog_post.title,
            )

        if keyword.lower() not in blog_post.seo_description.lower():
            blog_post.seo_description = self._normalize_seo_description(
                f"{keyword}: {blog_post.seo_description}",
                blog_post.summary,
            )

        return blog_post

    def _apply_quality_repairs(
        self,
        blog_post: BlogPost,
        keywords: Optional[list[str]] = None,
    ) -> BlogPost:
        blog_post.title = self._replace_ai_tropes(
            self._normalize_dash_punctuation(blog_post.title)
        )
        blog_post.summary = self._replace_ai_tropes(
            self._normalize_dash_punctuation(blog_post.summary)
        )
        blog_post.seo_title = self._replace_ai_tropes(
            self._normalize_dash_punctuation(blog_post.seo_title)
        )
        blog_post.seo_description = self._replace_ai_tropes(
            self._normalize_dash_punctuation(blog_post.seo_description)
        )
        blog_post.hero_image_prompt = self._replace_ai_tropes(
            self._normalize_dash_punctuation(blog_post.hero_image_prompt or "")
        )
        blog_post.sections = [
            BlogSection(
                heading=self._replace_ai_tropes(
                    self._normalize_dash_punctuation(section.heading)
                ),
                body_markdown=self._replace_ai_tropes(
                    self._normalize_dash_punctuation(section.body_markdown)
                ),
            )
            for section in blog_post.sections
        ]
        blog_post.seo_title = self._normalize_seo_title(
            blog_post.seo_title,
            blog_post.title,
        )
        blog_post.seo_description = self._normalize_seo_description(
            blog_post.seo_description,
            blog_post.summary,
        )
        return self._ensure_primary_keyword_in_seo(blog_post, keywords)

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
        title = self._clamp_str(self._normalize_dash_punctuation(title), 10, 150)
        summary = self._clamp_str(self._normalize_dash_punctuation(summary), 50, 500)
        seo_title = self._normalize_seo_title(seo_title, title)
        seo_description = self._normalize_seo_description(seo_description, summary)

        # Normalise slug
        raw_slug = (data.get("slug") or "").strip()
        slug = self._generate_slug(raw_slug or title)

        # Build sections
        sections = []
        for section_data in data.get("sections", []):
            if isinstance(section_data, dict):
                heading = (section_data.get("heading") or "").strip()
                body = self._normalize_dash_punctuation(
                    (section_data.get("body_markdown") or "").strip()
                )
                if heading and body:
                    sections.append(BlogSection(heading=heading, body_markdown=body))
            elif isinstance(section_data, BlogSection):
                sections.append(
                    BlogSection(
                        heading=section_data.heading,
                        body_markdown=self._normalize_dash_punctuation(section_data.body_markdown),
                    )
                )

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

        hero_image_prompt = self._normalize_hero_image_prompt(
            data.get("hero_image_prompt"),
            title=title,
            summary=summary,
        )

        blog_post = BlogPost(
            title=title,
            slug=slug,
            summary=summary,
            sections=sections,
            tags=tags,
            seo_title=seo_title,
            seo_description=seo_description,
            hero_image_prompt=hero_image_prompt,
            sources=data.get("sources"),
        )
        return self._apply_quality_repairs(blog_post)

    def _generate_slug(self, title: str) -> str:
        """Generate a URL-friendly slug from title."""
        slug = title.lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_]+", "-", slug)
        slug = re.sub(r"-+", "-", slug)
        slug = slug.strip("-")[:50]
        return slug.rstrip("-")

    async def generate(
        self,
        topic: str,
        blog_type: str = "news",
        keywords: Optional[list[str]] = None,
        audience: Optional[str] = None,
        word_count: str = "medium",
        tone: str = "professional",
        language: str = "en-US",
        model: str = DEFAULT_MODEL,
        creativity: float = 0.7,
        use_web_search: bool = True,
        published_posts: list[dict] | None = None,
    ) -> tuple[BlogPost, float, bool, list[dict] | None]:
        """
        Generate a complete blog post with configurable web search.

        use_web_search:
            - False — no web search
            - True  — use DuckDuckGo context injection
        
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
            "internal_linking": {
                "provided_targets": len(published_posts or []),
            },
            "web_grounding": {
                "requested": bool(use_web_search),
                "ddg_attempted": False,
                "ddg_used": False,
            },
        }

        # ── Phase 1: Research ───────────────────────────────────────
        phase_start = time.perf_counter()
        web_context, sources, ddg_used, ddg_attempted = self._research_phase(
            topic=topic,
            keywords=keywords,
            use_web_search=use_web_search,
        )
        web_search_used = web_search_used or ddg_used
        self._last_phase_metrics["timings_ms"]["research"] = round(
            (time.perf_counter() - phase_start) * 1000, 2
        )
        self._last_phase_metrics["web_grounding"]["ddg_attempted"] = ddg_attempted
        self._last_phase_metrics["web_grounding"]["ddg_used"] = ddg_used

        # ── Phase 2: Outline Guidance ───────────────────────────────
        phase_start = time.perf_counter()
        internal_linking_context = self._format_internal_linking_context(published_posts)
        prompt = self._build_blog_prompt(
            topic=topic,
            blog_type=blog_type,
            keywords=keywords,
            audience=audience,
            word_count=word_count,
            tone=tone,
            language=language,
            internal_linking_context=internal_linking_context,
        )

        prompt += self._build_outline_guidance(
            topic=topic,
            blog_type=blog_type,
            keywords=keywords,
            sources=sources,
            word_count=word_count,
        )

        # Append web research context if available
        if web_context:
            prompt += web_context
        self._last_phase_metrics["timings_ms"]["outline"] = round(
            (time.perf_counter() - phase_start) * 1000, 2
        )

        # ── Phase 3: Model Selection + Draft ────────────────────────
        phase_start = time.perf_counter()
        pydantic_model = self._get_model_for_name(model)
        model_capabilities = self._get_model_capabilities(model)
        self._last_phase_metrics["timings_ms"]["model_selection"] = round(
            (time.perf_counter() - phase_start) * 1000, 2
        )

        phase_start = time.perf_counter()
        draft_post, draft_usage = await self._draft_phase(
            pydantic_model=pydantic_model,
            model_capabilities=model_capabilities,
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
            model_capabilities=model_capabilities,
            base_prompt=prompt,
            blog_post=draft_post,
            creativity=creativity,
            word_count=word_count,
            keywords=keywords,
            draft_elapsed_s=draft_elapsed_s,
            published_posts_available=bool(published_posts),
        )
        self._last_phase_metrics["timings_ms"]["editorial"] = round(
            (time.perf_counter() - phase_start) * 1000, 2
        )
        self._last_phase_metrics["usage"]["editorial"] = editorial_usage
        self._last_phase_metrics["revision_applied"] = revision_applied
        self._last_phase_metrics["timings_ms"]["total"] = round(
            (time.perf_counter() - perf_start) * 1000, 2
        )
        self._last_phase_metrics["internal_linking"]["generated_link_count"] = (
            self._count_internal_links(blog_post)
        )

        # Attach sources to the blog post if web search was used
        if web_search_used and sources:
            blog_post.sources = sources

        generation_time = time.time() - start_time
        return blog_post, generation_time, web_search_used, sources

    def _get_max_tokens(
        self,
        word_count: str,
        model_capabilities: dict[str, Any] | None = None,
    ) -> int:
        """Get max tokens based on target word count.

        Blog responses include JSON structure, headings, summaries, SEO fields,
        and multiple section bodies, so they need a larger ceiling than plain
        prose prompts. The previous caps were low enough for some models to
        truncate the JSON object before the closing brace.
        """
        default_tokens = {
            "short": 2200,
            "medium": 3200,
            "long": 5200,
            "very-long": 7000,
        }.get(word_count, 3200)
        model_token_caps = (
            model_capabilities.get("max_tokens_by_word_count")
            if isinstance(model_capabilities, dict)
            else None
        )
        if isinstance(model_token_caps, dict):
            try:
                override = int(model_token_caps.get(word_count))
            except (TypeError, ValueError):
                override = 0
            if override > 0:
                return override
        return default_tokens

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
