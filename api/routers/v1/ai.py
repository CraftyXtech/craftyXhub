import re

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from services.user.auth import get_current_active_user
from services.ai import AIGeneratorService, AIDraftService, BlogAgentService, WebSearchService
from services.post import PostService
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
from schemas.post import PostCreate, TagCreate
from models import User
from typing import List
from datetime import datetime, timezone

router = APIRouter(prefix="/ai", tags=["AI Content Generation"])


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
    from services.ai.llm_config import get_models_for_test, AVAILABLE_MODELS

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
            result_type=str,
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
            "response": result.data,
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
    try:
        result = await generator.generate(
            tool_id=request.tool_id,
            model=request.model,
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.post("/generate/excerpt", response_model=ExcerptGenerateResponse)
async def generate_excerpt(
    request: ExcerptGenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session),
):
    del current_user, db

    generator = AIGeneratorService()
    cleaned_content = PostService.extract_plain_text_content(request.content, None)
    if len(cleaned_content) < 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Article content must be at least 50 characters to generate an excerpt.",
        )

    try:
        result = await generator.generate(
            tool_id="post-excerpt",
            model=request.model,
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
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Excerpt generation failed: {str(e)}",
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
            {"value": "how-to", "label": "How-To Guide"},
            {"value": "listicle", "label": "Listicle"},
            {"value": "tutorial", "label": "Tutorial"},
            {"value": "opinion", "label": "Opinion/Editorial"},
            {"value": "news", "label": "News Article"},
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
        "web_search_modes": [
            {"value": "off", "label": "Off"},
            {"value": "basic", "label": "Basic"},
            {"value": "enhanced", "label": "Enhanced"},
            {"value": "full", "label": "Full"},
        ],
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
    - save_draft: Save the generated content as an AI draft
    - publish_post: Create a post directly in the Posts system
    - web_search_mode: Control research grounding (off/basic/enhanced/full)
    """
    try:
        # Initialize the blog agent service
        blog_agent = BlogAgentService()

        # Generate the blog post
        blog_post, generation_time, web_search_used, sources = await blog_agent.generate(
            topic=request.topic,
            blog_type=request.blog_type,
            keywords=request.keywords,
            audience=request.audience,
            word_count=request.word_count or "medium",
            tone=request.tone or "professional",
            language=request.language or "en-US",
            model=request.model,
            creativity=request.creativity or 0.7,
            web_search_mode=request.web_search_mode or "basic",
        )

        quality_report = blog_agent.build_quality_report(
            blog_post=blog_post,
            word_count=request.word_count or "medium",
            keywords=request.keywords,
            phase_metrics=blog_agent.get_last_phase_metrics(),
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
                    model_used=request.model,
                    favorite=False,
                    draft_metadata={
                        "blog_type": request.blog_type,
                        "seo_title": blog_post.seo_title,
                        "seo_description": blog_post.seo_description,
                        "tags": blog_post.tags,
                        "slug": blog_post.slug,
                        "web_search_used": web_search_used,
                        "phase_metrics": blog_agent.get_last_phase_metrics(),
                        "quality_report": quality_report,
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

                # Create tags if they don't exist and get their IDs
                tag_ids = []
                for tag_name in blog_post.tags[:5]:  # Limit to 5 tags
                    try:
                        # Try to create or get existing tag
                        existing_tag = await PostService.get_tag_by_slug(
                            db, tag_name.lower().replace(" ", "-")
                        )
                        if existing_tag:
                            tag_ids.append(existing_tag.id)
                        else:
                            tag_data = TagCreate(name=tag_name)
                            new_tag = await PostService.create_tag(db, tag_data)
                            tag_ids.append(new_tag.id)
                    except Exception:
                        # Skip tag if creation fails
                        pass

                # Create the post
                post_content_blocks = {
                    "ai_generation": {
                        "generator": "blog-agent",
                        "model": request.model,
                        "web_search_mode": request.web_search_mode or "basic",
                        "web_search_used": web_search_used,
                        "search_sources_count": len(sources or []),
                        "generated_at": datetime.now(timezone.utc).isoformat(),
                        "phase_metrics": blog_agent.get_last_phase_metrics(),
                        "quality_report": quality_report,
                    }
                }

                post_data = PostCreate(
                    title=blog_post.title,
                    slug=blog_post.slug,
                    content=html_content,
                    content_blocks=post_content_blocks,
                    excerpt=blog_post.summary,
                    meta_title=blog_post.seo_title,
                    meta_description=blog_post.seo_description,
                    category_id=request.category_id,
                    tag_ids=tag_ids,
                    reading_time=reading_time,
                    is_published=request.is_published if request.is_published is not None else False,
                    is_featured=False,
                )

                created_post = await PostService.create_post(
                    db, post_data, current_user.id
                )
                post_id = created_post.uuid
            except Exception as post_error:
                # Log but don't fail the whole request
                print(f"Warning: Failed to create post: {post_error}")

        return BlogGenerateResponse(
            blog_post=blog_post,
            draft_id=draft_id,
            post_id=post_id,
            model_used=request.model,
            generation_time=round(generation_time, 2),
            web_search_used=web_search_used,
            search_sources=sources if web_search_used else None,
            quality_report=quality_report,
        )

    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Blog generation failed: {str(e)}",
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
