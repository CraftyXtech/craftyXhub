import asyncio
import logging
import re

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from core.config import settings
from database.connection import get_db_session
from services.user.auth import get_current_active_user
from services.ai import (
    AIGeneratorService,
    AIDraftService,
    BlogAgentService,
    BlogTaxonomyService,
    WebSearchService,
)
from services.ai.seo_keywords import resolve_seo_keywords
from services.post import PostService
from services.ai.llm_config import DEFAULT_MODEL, ensure_blog_model_enabled
from schemas.ai import (
    GenerateRequest,
    GenerateResponse,
    ExcerptGenerateRequest,
    ExcerptGenerateResponse,
    DraftSaveRequest,
    DraftUpdateRequest,
    DraftResponse,
    DraftListResponse,
    BlogGenerateRequest,
    BlogGenerateResponse,
    BlogPost,
)
from schemas.post import PostCreate
from models import Post, User
from typing import List
from datetime import datetime, timezone

router = APIRouter(prefix="/ai", tags=["AI Content Generation"])
logger = logging.getLogger(__name__)


def _resolve_model_name(model_name: str | None) -> str:
    return model_name or DEFAULT_MODEL


def _resolve_blog_model_name(model_name: str | None) -> str:
    return ensure_blog_model_enabled(_resolve_model_name(model_name))


def _iter_exception_messages(exc: Exception) -> list[str]:
    messages: list[str] = []
    current: BaseException | None = exc
    seen: set[int] = set()

    while current and id(current) not in seen:
        seen.add(id(current))
        message = str(current).strip()
        if message:
            messages.append(message)
        current = current.__cause__ or current.__context__

    return messages


def _is_timeout_error(exc: Exception) -> bool:
    if isinstance(exc, (TimeoutError, asyncio.TimeoutError)):
        return True

    timeout_markers = (
        "timeout",
        "timed out",
        "readtimeout",
        "connecttimeout",
        "deadline exceeded",
    )
    return any(
        marker in message.lower()
        for marker in timeout_markers
        for message in _iter_exception_messages(exc)
    )


def _sanitize_provider_error(exc: Exception) -> str:
    messages = _iter_exception_messages(exc)
    if not messages:
        return "The upstream model provider returned an unexpected error."

    primary = messages[0]
    lower_primary = primary.lower()
    if any(marker in lower_primary for marker in ("empty model response", "usable excerpt")):
        return "The model returned an incomplete response. Please retry or switch models."
    if "rate limit" in lower_primary:
        return "The model provider is rate-limiting requests right now. Please retry shortly."
    if "api key" in lower_primary or "authentication" in lower_primary:
        return "The model provider rejected the request configuration."
    return primary


def _raise_ai_http_exception(
    exc: Exception,
    *,
    model_name: str,
    operation: str,
) -> None:
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    if _is_timeout_error(exc):
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail=(
                f"{operation} with {model_name} timed out after about "
                f"{settings.AI_MODEL_REQUEST_TIMEOUT_SECONDS} seconds. "
                "Try again, shorten the request, or switch to another enabled model."
            ),
        )

    logger.exception("%s failed for model %s", operation, model_name, exc_info=exc)
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=(
            f"{operation} with {model_name} failed at the AI provider. "
            f"{_sanitize_provider_error(exc)}"
        ),
    )


def _clean_generated_excerpt(raw_excerpt: str) -> str:
    excerpt = (raw_excerpt or "").strip()
    excerpt = re.sub(r"^```(?:text)?|```$", "", excerpt, flags=re.IGNORECASE | re.MULTILINE)
    excerpt = re.sub(r"^(excerpt|summary)\s*:\s*", "", excerpt, flags=re.IGNORECASE)
    excerpt = re.sub(r"^\s*[-*•]\s*", "", excerpt)
    excerpt = excerpt.replace("**", "").replace("__", "")
    excerpt = excerpt.strip().strip('"').strip("'").strip()
    excerpt = PostService.normalize_excerpt(excerpt) or ""
    if len(excerpt) > 500:
        excerpt = excerpt[:497].rstrip(" ,;:") + "..."
    return excerpt


@router.get("/test")
async def test_ai_models():
    """
    Test endpoint to check which AI models are configured and available.
    No authentication required - for quick testing only.
    """
    from services.ai.llm_config import get_models_for_test

    available_models = get_models_for_test()

    return {
        "message": "AI Service is running",
        "available_models": available_models,
        "total_models": len(available_models),
        "note": "All models route through OpenRouter. Use the 'model' field value when making generation requests.",
    }


@router.post("/test/chat")
async def test_chat(
    message: str = Query(default="hi", description="Your message to the AI")
):
    """
    Simple chat endpoint - send any message and get a response!
    No authentication required - for quick testing only.
    """
    from pydantic_ai import Agent
    from services.ai.llm_config import get_model, DEFAULT_MODEL
    import time

    try:
        start_time = time.time()

        pydantic_model = get_model(DEFAULT_MODEL)
        agent = Agent(
            pydantic_model,
            output_type=str,
            system_prompt="You are a friendly and helpful AI assistant. Keep responses concise and engaging.",
        )

        result = await agent.run(
            message, model_settings={"temperature": 0.8, "max_tokens": 500}
        )

        response_time = time.time() - start_time

        tokens_used = None
        if hasattr(result, "usage") and result.usage():
            usage = result.usage()
            if hasattr(usage, "total_tokens"):
                tokens_used = usage.total_tokens

        return {
            "message": message,
            "response": result.output,
            "model": DEFAULT_MODEL,
            "response_time": round(response_time, 2),
            "tokens_used": tokens_used,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Chat failed: {str(e)}",
        )


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
    request: GenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    generator = AIGeneratorService()
    resolved_model = _resolve_model_name(request.model)
    try:
        result = await generator.generate(
            tool_id=request.tool_id,
            model=resolved_model,
            params=request.params,
            prompt=request.prompt,
            keywords=request.keywords,
            tone=request.tone,
            length=request.length,
            language=request.language,
            creativity=request.creativity,
            variant_count=request.variant_count,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        _raise_ai_http_exception(
            e,
            model_name=resolved_model,
            operation="Content generation",
        )


@router.post("/generate/excerpt", response_model=ExcerptGenerateResponse)
async def generate_excerpt(
    request: ExcerptGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    del current_user, db

    generator = AIGeneratorService()
    resolved_model = _resolve_model_name(request.model)
    cleaned_content = PostService.extract_plain_text_content(request.content, None)
    if len(cleaned_content) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article content must be at least 50 characters to generate an excerpt.",
        )

    try:
        result = await generator.generate(
            tool_id="post-excerpt",
            model=resolved_model,
            params={
                "title": request.title or "Untitled article",
                "content": cleaned_content,
            },
            tone=request.tone or "professional",
            language=request.language or "en-US",
            length="short",
            creativity=request.creativity or 0.4,
            variant_count=1,
        )
        raw_excerpt = result["variants"][0]["content"] if result.get("variants") else ""
        excerpt = _clean_generated_excerpt(raw_excerpt)
        if not excerpt:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="AI did not return a usable excerpt.",
            )

        return ExcerptGenerateResponse(
            excerpt=excerpt,
            model_used=result["model_used"],
            generation_time=result["generation_time"],
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        _raise_ai_http_exception(
            e,
            model_name=resolved_model,
            operation="Excerpt generation",
        )


@router.post(
    "/drafts", response_model=DraftResponse, status_code=status.HTTP_201_CREATED
)
async def save_draft(
    draft: DraftSaveRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    try:
        saved = await AIDraftService.create_draft(draft, current_user.id, db)
        return saved
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save draft: {str(e)}",
        )


@router.get("/drafts", response_model=DraftListResponse)
async def get_drafts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    try:
        drafts = await AIDraftService.get_drafts(current_user.id, skip, limit, db)
        total = await AIDraftService.get_drafts_count(current_user.id, db)
        return {
            "drafts": drafts,
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve drafts: {str(e)}",
        )


@router.get("/drafts/favorites", response_model=DraftListResponse)
async def get_favorite_drafts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    try:
        drafts = await AIDraftService.get_favorite_drafts(
            current_user.id, skip, limit, db
        )
        total = len(drafts)
        return {
            "drafts": drafts,
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve favorite drafts: {str(e)}",
        )


@router.get("/drafts/{draft_uuid}", response_model=DraftResponse)
async def get_draft(
    draft_uuid: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    draft = await AIDraftService.get_draft_by_uuid(draft_uuid, current_user.id, db)
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found"
        )
    return draft


@router.put("/drafts/{draft_uuid}", response_model=DraftResponse)
async def update_draft(
    draft_uuid: str,
    updates: DraftUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    draft = await AIDraftService.update_draft_by_uuid(
        draft_uuid, current_user.id, updates, db
    )
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found"
        )
    return draft


@router.delete("/drafts/{draft_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_uuid: str,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    deleted = await AIDraftService.delete_draft_by_uuid(draft_uuid, current_user.id, db)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Draft not found"
        )
    return None


# ============================================================================
# Blog Options Endpoint
# ============================================================================


@router.get("/blog/options")
async def get_blog_options():
    """
    Return available blog generation options for the frontend dropdowns.
    No authentication required - these are static configuration options.
    """
    from services.ai.llm_config import get_models_for_frontend

    models = get_models_for_frontend()

    return {
        "blog_types": [
            {"value": "news", "label": "News Article"},
            {"value": "how-to", "label": "How-To Guide"},
            {"value": "listicle", "label": "Listicle"},
            {"value": "tutorial", "label": "Tutorial"},
            {"value": "opinion", "label": "Opinion/Editorial"},
            {"value": "review", "label": "Product Review"},
            {"value": "comparison", "label": "Comparison"},
            {"value": "case-study", "label": "Case Study"},
        ],
        "tones": [
            {"value": "professional", "label": "Professional"},
            {"value": "casual", "label": "Casual"},
            {"value": "friendly", "label": "Friendly"},
            {"value": "authoritative", "label": "Authoritative"},
            {"value": "humorous", "label": "Humorous"},
            {"value": "educational", "label": "Educational"},
        ],
        "audiences": [
            {"value": "general", "label": "General Audience"},
            {"value": "beginners", "label": "Beginners"},
            {"value": "developers", "label": "Developers"},
            {"value": "marketers", "label": "Marketers"},
            {"value": "business-owners", "label": "Business Owners"},
            {"value": "students", "label": "Students"},
            {"value": "professionals", "label": "Professionals"},
            {"value": "tech-enthusiasts", "label": "Tech Enthusiasts"},
            {"value": "entrepreneurs", "label": "Entrepreneurs"},
            {"value": "content-creators", "label": "Content Creators"},
        ],
        "lengths": [
            {"value": "short", "label": "Short (~300 words)"},
            {"value": "medium", "label": "Medium (~500 words)"},
            {"value": "long", "label": "Long (~1000 words)"},
            {"value": "very-long", "label": "Very Long (~1500+ words)"},
        ],
        "models": models,
        "use_web_search_default": True,
    }


# ============================================================================
# Blog Agent Endpoints
# ============================================================================


@router.post("/generate/blog", response_model=BlogGenerateResponse)
async def generate_blog(
    request: BlogGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    """
    Generate a complete, structured blog post using the Blog Agent.
    
    This endpoint uses PydanticAI to generate publication-ready blog posts with:
    - Structured sections with headings and markdown content
    - SEO-optimized title and meta description
    - Relevant tags
    - Optional hero image prompt
    
    Options:
    - save_draft: Optionally save the generated content as an AI draft
    - publish_post: Create a post directly in the Posts system
    - use_web_search: Enable or disable DuckDuckGo grounding
    """
    try:
        # Initialize the blog agent service
        blog_agent = BlogAgentService()
        use_web_search = request.use_web_search
        resolved_model = _resolve_blog_model_name(request.model)
        seed_keywords = resolve_seo_keywords(
            topic=request.topic,
            provided_keywords=request.keywords,
        )
        published_posts = []
        if db is not None:
            published_posts = await PostService.get_internal_link_targets(
                db,
                category_id=request.category_id,
                limit=50,
            )

        # Generate the blog post
        blog_post, generation_time, web_search_used, sources = await blog_agent.generate(
            topic=request.topic,
            blog_type=request.blog_type,
            keywords=seed_keywords,
            audience=request.audience,
            word_count=request.word_count or "medium",
            tone=request.tone or "professional",
            language=request.language or "en-US",
            model=resolved_model,
            creativity=request.creativity or 0.7,
            use_web_search=use_web_search,
            published_posts=published_posts,
        )

        taxonomy_suggestion = await BlogTaxonomyService.suggest_for_generated_post(
            db,
            topic=request.topic,
            blog_post=blog_post,
            keywords=seed_keywords,
            preferred_category_id=request.category_id,
        )
        resolved_keywords = resolve_seo_keywords(
            topic=request.topic,
            provided_keywords=seed_keywords,
            blog_post=blog_post,
            taxonomy_suggestion=taxonomy_suggestion,
        )
        quality_report = blog_agent.build_quality_report(
            blog_post=blog_post,
            word_count=request.word_count or "medium",
            keywords=resolved_keywords,
            phase_metrics=blog_agent.get_last_phase_metrics(),
            published_posts_available=bool(published_posts),
        )

        draft_id = None
        post_id = None

        # Save as AI draft if requested
        if request.save_draft:
            try:
                # Convert blog post to markdown for draft content
                draft_content = blog_agent.blog_post_to_markdown(blog_post)
                
                draft_data = DraftSaveRequest(
                    name=blog_post.title,
                    content=draft_content,
                    tool_id="blog-agent",
                    model_used=resolved_model,
                    favorite=False,
                    draft_metadata={
                        "blog_type": request.blog_type,
                        "seo_title": blog_post.seo_title,
                        "seo_description": blog_post.seo_description,
                        "resolved_keywords": resolved_keywords,
                        "tags": blog_post.tags,
                        "slug": blog_post.slug,
                        "use_web_search": use_web_search,
                        "web_search_used": web_search_used,
                        "phase_metrics": blog_agent.get_last_phase_metrics(),
                        "quality_report": quality_report,
                        "internal_link_targets_count": len(published_posts),
                        "taxonomy_suggestion": taxonomy_suggestion.model_dump(
                            exclude_none=True
                        ),
                        "resolved_category_id": taxonomy_suggestion.category.id
                        if taxonomy_suggestion.category
                        else None,
                        "resolved_tag_ids": [tag.id for tag in taxonomy_suggestion.tags],
                    },
                )
                saved_draft = await AIDraftService.create_draft(
                    draft_data, current_user.id, db
                )
                draft_id = saved_draft.uuid
            except Exception as draft_error:
                # Log but don't fail the whole request
                print(f"Warning: Failed to save draft: {draft_error}")

        # Publish as post if requested
        if request.publish_post:
            try:
                # Convert blog post to HTML for post content
                html_content = blog_agent.blog_post_to_html(blog_post)

                # Calculate reading time (average 200 words per minute)
                word_count = sum(
                    len(section.body_markdown.split())
                    for section in blog_post.sections
                )
                reading_time = max(1, word_count // 200)
                tag_ids = [
                    tag.id for tag in taxonomy_suggestion.tags[: BlogTaxonomyService.MAX_TAGS]
                ]
                category_id = request.category_id
                if category_id is None and taxonomy_suggestion.category is not None:
                    category_id = taxonomy_suggestion.category.id

                # Create the post
                final_slug = blog_post.slug
                existing_post = await PostService.get_post_by_slug(
                    db,
                    final_slug,
                    include_deleted=True,
                )
                if existing_post:
                    final_slug = await PostService.generate_unique_slug(
                        db,
                        blog_post.title,
                        Post,
                    )
                    blog_post.slug = final_slug

                post_content_blocks = {
                    "ai_generation": {
                        "generator": "blog-agent",
                        "model": resolved_model,
                        "use_web_search": use_web_search,
                        "web_search_used": web_search_used,
                        "search_sources_count": len(sources or []),
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "resolved_keywords": resolved_keywords,
                        "phase_metrics": blog_agent.get_last_phase_metrics(),
                        "quality_report": quality_report,
                        "internal_link_targets_count": len(published_posts),
                        "taxonomy_suggestion": taxonomy_suggestion.model_dump(
                            exclude_none=True
                        ),
                    }
                }

                post_data = PostCreate(
                    title=blog_post.title,
                    slug=final_slug,
                    content=html_content,
                    content_blocks=post_content_blocks,
                    excerpt=blog_post.summary,
                    meta_title=blog_post.seo_title,
                    meta_description=blog_post.seo_description,
                    seo_keywords=resolved_keywords,
                    category_id=category_id,
                    tag_ids=tag_ids,
                    reading_time=reading_time,
                    is_published=False,
                    is_featured=False,
                )

                created_post = await PostService.create_post(
                    db, post_data, current_user.id
                )
                if request.is_published:
                    created_post = await PostService.publish_post(
                        db,
                        created_post.uuid,
                        current_user,
                        override_quality_gate=True,
                        override_reason="Approved AI-generated post during generation.",
                    )
                post_id = created_post.uuid
            except Exception as post_error:
                # Log but don't fail the whole request
                print(f"Warning: Failed to create post: {post_error}")

        return BlogGenerateResponse(
            blog_post=blog_post,
            resolved_keywords=resolved_keywords,
            taxonomy_suggestion=taxonomy_suggestion,
            draft_id=draft_id,
            post_id=post_id,
            model_used=resolved_model,
            generation_time=round(generation_time, 2),
            web_search_used=web_search_used,
            search_sources=sources if web_search_used else None,
            quality_report=quality_report,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        _raise_ai_http_exception(
            e,
            model_name=_resolve_model_name(request.model),
            operation="Blog generation",
        )


# ============================================================================
# Web Search Preview Endpoint
# ============================================================================


@router.get("/search/preview")
async def preview_web_search(
    topic: str = Query(..., min_length=3, description="Topic to search for"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Preview web search results for a topic before blog generation.
    Returns text and news results from DuckDuckGo.
    """
    try:
        search_svc = WebSearchService(max_results=5)
        results = search_svc.search_for_topic(topic)
        return results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )
