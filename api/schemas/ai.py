from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime


class GenerateRequest(BaseModel):
    template_id: str = Field(..., description="ID from AI_TEMPLATES")
    model: Literal["grok", "openai", "gemini", "chatgpt-free", "deepseek-free"] = Field(default="chatgpt-free")
    params: Dict[str, Any] = Field(..., description="Template-specific fields")
    
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
    template_id: Optional[str] = None
    model_used: Optional[str] = None
    favorite: Optional[bool] = Field(default=False)
    metadata: Optional[Dict[str, Any]] = None


class DraftUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = None
    favorite: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None


class GenerationVariant(BaseModel):
    content: str
    metadata: Dict[str, Any] = Field(..., description="{words, characters, model, tokens}")


class GenerateResponse(BaseModel):
    variants: List[GenerationVariant]
    template_id: str
    model_used: str
    generation_time: float


class DraftResponse(BaseModel):
    id: int
    uuid: str
    user_id: int
    name: str
    content: str
    template_id: Optional[str]
    model_used: Optional[str]
    favorite: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DraftListResponse(BaseModel):
    drafts: List[DraftResponse]
    total: int
    page: int
    size: int

