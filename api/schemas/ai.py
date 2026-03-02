import re

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class GenerateRequest(BaseModel):
    tool_id: str = Field(..., description="ID from AI_TOOLS")
    model: str = Field(default="claude-sonnet-4.6", description="AI model name (e.g., claude-sonnet-4.6, gpt-5.2)")
    params: Dict[str, Any] = Field(..., description="Tool-specific fields")
    prompt: Optional[str] = Field(default=None, description="Freeform prompt to use when tool params are incomplete or for generic generation")
    keywords: Optional[List[str] | str] = Field(default=None, description="Primary keywords to guide generation; list or comma-separated string")
    
    tone: Optional[str] = Field(default="professional", description="From TONE_OPTIONS")
    length: Optional[str] = Field(default="medium", description="From LENGTH_OPTIONS")
    language: Optional[str] = Field(default="en-US", description="From LANGUAGE_OPTIONS")
    creativity: Optional[float] = Field(default=0.7, ge=0.0, le=1.0, description="Maps to temperature")
    variant_count: Optional[int] = Field(default=1, ge=1, le=5)
    stream: Optional[bool] = Field(default=False)


class DraftSaveRequest(BaseModel):
    id: Optional[str] = Field(default=None, description="Frontend UUID")
    name: str = Field(..., min_length=1, max_length=255)
    content: str = Field(...)
    tool_id: Optional[str] = None
    model_used: Optional[str] = None
    favorite: Optional[bool] = Field(default=False)
    draft_metadata: Optional[Dict[str, Any]] = None


class DraftUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    favorite: Optional[bool] = None
    draft_metadata: Optional[Dict[str, Any]] = None


class GenerationVariant(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(..., description="{words, characters, model, tokens}")


class GenerateResponse(BaseModel):
    variants: List[GenerationVariant]
    tool_id: str
    model_used: str
    generation_time: float


class DraftResponse(BaseModel):
    id: int
    uuid: str
    user_id: int
    name: str
    content: str
    tool_id: Optional[str]
    model_used: Optional[str]
    favorite: bool
    draft_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DraftListResponse(BaseModel):
    drafts: List[DraftResponse]
    total: int
    page: int
    size: int


# ============================================================================
# Blog Agent Schemas
# ============================================================================

class BlogSection(BaseModel):
    """A single section of a blog post."""
    heading: str = Field(..., min_length=3, max_length=120, description="Section heading (H2)")
    body_markdown: str = Field(
        ...,
        min_length=30,      # Lowered to accept LLM variance; real quality floor is in blog_agent.py
        max_length=8000,
        description="Section content in markdown",
    )

    @field_validator("heading")
    @classmethod
    def normalize_heading(cls, value: str) -> str:
        heading = value.strip()
        if heading.startswith("#"):
            heading = heading.lstrip("#").strip()
        if not heading:
            raise ValueError("Section heading cannot be empty")
        return heading


class BlogPost(BaseModel):
    """Structured blog post output from the Blog Agent."""
    title: str = Field(..., min_length=5, max_length=200, description="Blog post title")
    slug: str = Field(..., min_length=3, max_length=200, description="URL-friendly slug")
    summary: str = Field(..., min_length=20, max_length=600, description="Brief summary/excerpt")
    sections: List[BlogSection] = Field(..., min_length=2, max_length=15, description="List of content sections")
    tags: List[str] = Field(default_factory=list, min_length=1, max_length=15, description="Relevant tags")
    seo_title: str = Field(..., min_length=5, max_length=120, description="SEO meta title")
    seo_description: str = Field(..., min_length=20, max_length=350, description="SEO meta description")
    hero_image_prompt: Optional[str] = Field(
        default=None, description="AI image generation prompt for hero image"
    )
    sources: Optional[List[dict]] = Field(
        default=None, description="Web sources used during research [{title, url, snippet}]"
    )

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value: str) -> str:
        slug = value.strip().lower()
        # Allow underscores, consecutive hyphens, etc. — blog_agent normalizes later
        slug = re.sub(r"[^a-z0-9\-_]", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        if not slug:
            raise ValueError("slug cannot be empty")
        return slug

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: List[str]) -> List[str]:
        normalized = list(dict.fromkeys(
            tag.strip().lower() for tag in value if tag and tag.strip()
        ))
        if not normalized:
            raise ValueError("at least 1 tag is required")
        return normalized

    # NOTE: conclusion/CTA check is enforced as a soft quality issue in
    # blog_agent.py._collect_quality_issues() — not as a hard validator here,
    # because failing a model_validator exhausts pydantic-ai structured retries.


class BlogGenerateRequest(BaseModel):
    """Request to generate a complete blog post."""
    topic: str = Field(..., min_length=3, max_length=500, description="Blog topic or title idea")
    blog_type: Literal[
        "how-to", "listicle", "tutorial", "opinion", "case-study", "news", "review", "comparison"
    ] = Field(default="how-to", description="Type of blog post to generate")
    keywords: Optional[List[str]] = Field(
        default=None, description="Target SEO keywords"
    )
    audience: Optional[str] = Field(
        default=None, description="Target audience description"
    )
    word_count: Optional[Literal["short", "medium", "long", "very-long"]] = Field(
        default="medium", description="Target length"
    )
    tone: Optional[str] = Field(default="professional", description="Writing tone")
    language: Optional[str] = Field(default="en-US", description="Output language")
    model: str = Field(
        default="claude-sonnet-4.6",
        description="AI model (claude-sonnet-4.6, gpt-5.2, deepseek-v3.2)"
    )
    creativity: Optional[float] = Field(
        default=0.7, ge=0.0, le=1.0, description="Creativity/temperature"
    )
    web_search_mode: Optional[Literal["off", "basic", "enhanced"]] = Field(
        default="basic",
        description="Web search mode: off, basic (DuckDuckGo), enhanced (OpenRouter :online)"
    )
    execution_mode: Literal["strict", "resilient"] = Field(
        default="strict",
        description="Execution mode: strict (selected model only) or resilient (model chain failover)"
    )
    # Save/publish options
    save_draft: Optional[bool] = Field(
        default=True, description="Save as AI draft"
    )
    publish_post: Optional[bool] = Field(
        default=False, description="Publish directly to Posts"
    )
    category_id: Optional[int] = Field(
        default=None, description="Category ID for publishing"
    )
    is_published: Optional[bool] = Field(
        default=False, description="Set published status when creating post"
    )


class BlogGenerateResponse(BaseModel):
    """Response from blog generation."""
    blog_post: BlogPost = Field(..., description="Generated blog post")
    draft_id: Optional[str] = Field(
        default=None, description="AI Draft UUID if saved"
    )
    post_id: Optional[str] = Field(
        default=None, description="Post UUID if published"
    )
    model_used: str = Field(..., description="AI model used")
    requested_model: str = Field(..., description="Requested model from client")
    effective_model: str = Field(..., description="Final model that produced the output")
    execution_path: Literal["structured", "compat_json"] = Field(
        ..., description="Execution path used for generation"
    )
    attempted_models: List[str] = Field(
        default_factory=list,
        description="Ordered list of attempted model ids",
    )
    generation_time: float = Field(..., description="Time taken in seconds")
    web_search_used: bool = Field(
        default=False, description="Whether web search was used"
    )
    search_sources: Optional[List[dict]] = Field(
        default=None, description="Sources found via web search"
    )
    quality_report: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Deterministic quality analysis report (readability, SEO, style)",
    )
