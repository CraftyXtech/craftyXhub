from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import BaseTable


class AIDraft(BaseTable):
    __tablename__ = "ai_drafts"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    tool_id = Column(String(100), nullable=True)
    model_used = Column(String(100), nullable=True)
    favorite = Column(Boolean, default=False)
    draft_metadata = Column(JSON, nullable=True)
    
    user = relationship("User", back_populates="ai_drafts")


class AIGenerationLog(BaseTable):
    __tablename__ = "ai_generation_logs"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    tool_id = Column(String(100), nullable=True)
    model_used = Column(String(100), nullable=False)
    tokens_used = Column(Integer, nullable=True)
    generation_time = Column(Float, nullable=True)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="ai_generation_logs")


