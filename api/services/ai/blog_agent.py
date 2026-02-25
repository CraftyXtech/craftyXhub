"""
Blog Agent Service - PydanticAI-powered blog post generation with web search.

This service generates complete, structured blog posts using PydanticAI agents
with optional web search capabilities for research-backed content.
"""

import json
import re
import time
from typing import Optional

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel

from core.config import settings
from schemas.ai import BlogPost, BlogSection
from .tools import ToolHandler
from .llm_config import get_model, DEFAULT_MODEL



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
            "short": "800-1200 words",
            "medium": "1500-2500 words",
            "long": "2500-4000 words",
            "very-long": "4000+ words",
        }

        params = {
            "topic": topic,
            "blog_type": blog_type,
            "keywords": ", ".join(keywords) if keywords else "Not specified",
            "audience": audience or "General audience",
            "word_count": word_count_map.get(word_count, "1500-2500 words"),
            "tone": tone,
        }

        # Build the prompt from tool config
        prompt = self.tool_config["prompt"].format(**params)

        # Add language instruction if not English
        if language != "en-US":
            prompt += f"\n\nIMPORTANT: Write all content in {language}."

        return prompt

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

    def _validate_and_create_blog_post(self, data: dict) -> BlogPost:
        """
        Validate parsed data and create a BlogPost instance.
        """
        # Ensure sections is a list of BlogSection objects
        sections = []
        for section_data in data.get("sections", []):
            if isinstance(section_data, dict):
                sections.append(BlogSection(**section_data))
            elif isinstance(section_data, BlogSection):
                sections.append(section_data)

        return BlogPost(
            title=data.get("title", "Untitled"),
            slug=data.get("slug", self._generate_slug(data.get("title", "untitled"))),
            summary=data.get("summary", ""),
            sections=sections,
            tags=data.get("tags", []),
            seo_title=data.get("seo_title", data.get("title", "")[:60]),
            seo_description=data.get("seo_description", data.get("summary", "")[:160]),
            hero_image_prompt=data.get("hero_image_prompt"),
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
        model: str = "kimi-k2.5",
        creativity: float = 0.7,
        use_web_search: bool = True,
    ) -> tuple[BlogPost, float, bool]:
        """
        Generate a complete blog post.
        
        Args:
            topic: The blog topic or title idea
            blog_type: Type of blog (how-to, listicle, tutorial, etc.)
            keywords: Target SEO keywords
            audience: Target audience description
            word_count: Target length (short, medium, long, very-long)
            tone: Writing tone
            language: Output language
            model: AI model to use
            creativity: Temperature/creativity level (0.0-1.0)
            use_web_search: Whether to enable web search (if supported)
            
        Returns:
            Tuple of (BlogPost, generation_time, web_search_used)
        """
        start_time = time.time()

        # Build the prompt
        prompt = self._build_blog_prompt(
            topic=topic,
            blog_type=blog_type,
            keywords=keywords,
            audience=audience,
            word_count=word_count,
            tone=tone,
            language=language,
        )

        # Get the model
        pydantic_model = self._get_model_for_name(model)

        # Try structured output first, fall back to text parsing
        try:
            # Create agent with structured output
            agent = Agent(
                pydantic_model,
                result_type=BlogPost,
                system_prompt=self.system_prompt,
            )

            result = await agent.run(
                prompt,
                model_settings={
                    "temperature": creativity,
                    "max_tokens": self._get_max_tokens(word_count),
                },
            )

            blog_post = result.data
            
        except Exception as structured_error:
            # Fall back to text generation with JSON parsing
            try:
                agent = Agent(
                    pydantic_model,
                    result_type=str,
                    system_prompt=self.system_prompt,
                )

                result = await agent.run(
                    prompt,
                    model_settings={
                        "temperature": creativity,
                        "max_tokens": self._get_max_tokens(word_count),
                    },
                )

                # Parse JSON from text output
                parsed_data = self._parse_json_from_text(result.data)
                blog_post = self._validate_and_create_blog_post(parsed_data)
                
            except Exception as text_error:
                raise ValueError(
                    f"Failed to generate blog post. "
                    f"Structured output error: {structured_error}. "
                    f"Text parsing error: {text_error}"
                )

        generation_time = time.time() - start_time
        return blog_post, generation_time, False

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







