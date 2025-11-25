from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class GenerateRequest(BaseModel):
    tool_id: str = Field(..., description="ID from AI_TOOLS")
    model: str = Field(default="gpt-5-mini", description="AI model name (e.g., gpt-5-mini, gpt-4o, gemini, grok, deepseek-v3)")
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
    heading: str = Field(..., description="Section heading (H2)")
    body_markdown: str = Field(..., description="Section content in markdown")


class BlogPost(BaseModel):
    """Structured blog post output from the Blog Agent."""
    title: str = Field(..., description="Blog post title")
    slug: str = Field(..., description="URL-friendly slug")
    summary: str = Field(..., description="Brief summary/excerpt (150-200 chars)")
    sections: List[BlogSection] = Field(..., description="List of content sections")
    tags: List[str] = Field(default_factory=list, description="Relevant tags")
    seo_title: str = Field(..., description="SEO meta title (50-60 chars)")
    seo_description: str = Field(..., description="SEO meta description (150-160 chars)")
    hero_image_prompt: Optional[str] = Field(
        default=None, description="AI image generation prompt for hero image"
    )


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
        default="gpt-5-mini",
        description="AI model (gpt-5-mini, gpt-4o, gemini, grok, deepseek-v3)"
    )
    creativity: Optional[float] = Field(
        default=0.7, ge=0.0, le=1.0, description="Creativity/temperature"
    )
    use_web_search: Optional[bool] = Field(
        default=True, description="Enable web search for research (if model supports)"
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

