import re

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class GenerateRequest(BaseModel):
    tool_id: str = Field(..., description="ID from AI_TOOLS")
    model: str = Field(default="glm-5", description="AI model name (e.g., glm-5, claude-sonnet-4.6, gpt-5.2)")
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

    model_config = ConfigDict(from_attributes=True)


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
    title: str = Field(..., min_length=10, max_length=150, description="Blog post title")
    slug: str = Field(..., min_length=5, max_length=160, description="URL-friendly slug")
    summary: str = Field(..., min_length=50, max_length=500, description="Brief summary/excerpt")
    sections: List[BlogSection] = Field(..., min_length=3, max_length=10, description="List of content sections")
    tags: List[str] = Field(default_factory=list, min_length=2, max_length=12, description="Relevant tags")
    seo_title: str = Field(..., min_length=15, max_length=80, description="SEO meta title")
    seo_description: str = Field(..., min_length=50, max_length=250, description="SEO meta description")
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
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug):
            raise ValueError("slug must use lowercase letters, numbers, and hyphens only")
        return slug

    @field_validator("tags")
    @classmethod
    def normalize_tags(cls, value: List[str]) -> List[str]:
        normalized = [tag.strip().lower() for tag in value if tag and tag.strip()]
        if len(normalized) < 2:
            raise ValueError("at least 2 tags are required")
        if len(normalized) != len(set(normalized)):
            raise ValueError("tags must be unique")
        return normalized

    @model_validator(mode="after")
    def ensure_conclusion_or_cta_section(self):
        heading_text = " ".join(section.heading.lower() for section in self.sections)
        quality_markers = ("conclusion", "final thoughts", "next steps", "call to action", "cta")
        if not any(marker in heading_text for marker in quality_markers):
            raise ValueError("include at least one conclusion or call-to-action section")
        return self


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
        default="glm-5",
        description="AI model (claude-sonnet-4.6, gpt-5.2, glm-5, kimi-k2.5)"
    )
    creativity: Optional[float] = Field(
        default=0.7, ge=0.0, le=1.0, description="Creativity/temperature"
    )
    web_search: Optional[bool] = Field(
        default=True,
        description="Enable web search grounding (DuckDuckGo) when true"
    )
    web_search_mode: Optional[Literal["off", "basic"]] = Field(
        default=None,
        description="Deprecated mode field. Use web_search boolean instead."
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
