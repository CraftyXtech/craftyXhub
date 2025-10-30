from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from services.user.auth import get_current_active_user
from services.ai import AIGeneratorService, AIDraftService
from schemas.ai import (
    GenerateRequest,
    GenerateResponse,
    DraftSaveRequest,
    DraftUpdateRequest,
    DraftResponse,
    DraftListResponse
)
from models import User
from typing import List

router = APIRouter(prefix="/ai", tags=["AI Content Generation"])


@router.get("/test")
async def test_ai_models():
    """
    Test endpoint to check which AI models are configured and available.
    No authentication required - for quick testing only.
    """
    from core.config import settings
    
    available_models = []
    
    if settings.FREE_CHATGPT_TOKEN:
        available_models.append({
            "name": "chatgpt-free",
            "model": "gpt-3.5-turbo",
            "provider": "OpenAI (via ChatAnywhere proxy)",
            "status": "configured"
        })
    
    if settings.FREE_DEEPSEEK_TOKEN:
        available_models.append({
            "name": "deepseek-free",
            "model": "deepseek-chat",
            "provider": "DeepSeek (via ChatAnywhere proxy)",
            "status": "configured"
        })
    
    if settings.OPENAI_API_KEY:
        available_models.append({
            "name": "openai",
            "model": "gpt-3.5-turbo",
            "provider": "OpenAI",
            "status": "configured"
        })
    
    if settings.GROK_API_KEY:
        available_models.append({
            "name": "grok",
            "model": "grok-2-1212",
            "provider": "xAI",
            "status": "configured"
        })
    
    if settings.GEMINI_API_KEY:
        available_models.append({
            "name": "gemini",
            "model": "gemini-2.0-flash-exp",
            "provider": "Google",
            "status": "configured"
        })
    
    return {
        "message": "AI Service is running",
        "available_models": available_models,
        "total_models": len(available_models)
    }


@router.post("/test/chat")
async def test_chat(message: str = Query(default="hi", description="Your message to the AI")):
    """
    Simple chat endpoint - send any message and get a response!
    No authentication required - for quick testing only.
    
    Examples:
    - POST /test/chat?message=hi
    - POST /test/chat?message=tell me a joke
    - POST /test/chat?message=what can you do?
    """
    from pydantic_ai import Agent
    from pydantic_ai.models.openai import OpenAIModel
    from core.config import settings
    import time
    
    if not settings.FREE_CHATGPT_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Free ChatGPT API not configured. Add FREE_CHATGPT_TOKEN to .env"
        )
    
    try:
        start_time = time.time()
        
        # Create a simple chat agent
        agent = Agent(
            OpenAIModel(
                "gpt-3.5-turbo",
                api_key=settings.FREE_CHATGPT_TOKEN,
                base_url="https://api.chatanywhere.tech/v1"
            ),
            result_type=str,
            system_prompt="You are a friendly and helpful AI assistant. Keep responses concise and engaging."
        )
        
        # Get response
        result = await agent.run(
            message,
            model_settings={
                "temperature": 0.8,
                "max_tokens": 500
            }
        )
        
        response_time = time.time() - start_time
        
        # Get token usage if available
        tokens_used = None
        if hasattr(result, 'usage') and result.usage():
            usage = result.usage()
            if hasattr(usage, 'total_tokens'):
                tokens_used = usage.total_tokens
        
        return {
            "message": message,
            "response": result.data,
            "model": "chatgpt-free (gpt-3.5-turbo)",
            "response_time": round(response_time, 2),
            "tokens_used": tokens_used
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Chat failed: {str(e)}"
        )


@router.post("/generate", response_model=GenerateResponse)
async def generate_content(
    request: GenerateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    generator = AIGeneratorService()
    try:
        result = await generator.generate(
            template_id=request.template_id,
            model=request.model,
            params=request.params,
            tone=request.tone,
            length=request.length,
            language=request.language,
            creativity=request.creativity,
            variant_count=request.variant_count
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/drafts", response_model=DraftResponse, status_code=status.HTTP_201_CREATED)
async def save_draft(
    draft: DraftSaveRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        saved = await AIDraftService.create_draft(draft, current_user.id, db)
        return saved
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save draft: {str(e)}"
        )


@router.get("/drafts", response_model=DraftListResponse)
async def get_drafts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        drafts = await AIDraftService.get_drafts(current_user.id, skip, limit, db)
        total = await AIDraftService.get_drafts_count(current_user.id, db)
        return {
            "drafts": drafts,
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve drafts: {str(e)}"
        )


@router.get("/drafts/{draft_id}", response_model=DraftResponse)
async def get_draft(
    draft_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    draft = await AIDraftService.get_draft_by_id(draft_id, current_user.id, db)
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    return draft


@router.put("/drafts/{draft_id}", response_model=DraftResponse)
async def update_draft(
    draft_id: int,
    updates: DraftUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    draft = await AIDraftService.update_draft(draft_id, current_user.id, updates, db)
    if not draft:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    return draft


@router.delete("/drafts/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    deleted = await AIDraftService.delete_draft(draft_id, current_user.id, db)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    return None


@router.get("/drafts/favorites", response_model=DraftListResponse)
async def get_favorite_drafts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db_session)
):
    try:
        drafts = await AIDraftService.get_favorite_drafts(current_user.id, skip, limit, db)
        total = len(drafts)
        return {
            "drafts": drafts,
            "total": total,
            "page": (skip // limit) + 1,
            "size": limit
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve favorite drafts: {str(e)}"
        )

