from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete
from models.ai_draft import AIDraft
from schemas.ai import DraftSaveRequest, DraftUpdateRequest
from typing import List, Optional
import uuid


class AIDraftService:
    @staticmethod
    async def create_draft(
        draft_data: DraftSaveRequest,
        user_id: int,
        db: AsyncSession
    ) -> AIDraft:
        draft = AIDraft(
            user_id=user_id,
            name=draft_data.name,
            content=draft_data.content,
            template_id=draft_data.template_id,
            model_used=draft_data.model_used,
            favorite=draft_data.favorite or False
        )
        db.add(draft)
        await db.commit()
        await db.refresh(draft)
        return draft
    
    @staticmethod
    async def get_drafts(
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        db: AsyncSession = None
    ) -> List[AIDraft]:
        stmt = (
            select(AIDraft)
            .where(AIDraft.user_id == user_id)
            .order_by(AIDraft.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()
    
    @staticmethod
    async def get_draft_by_id(
        draft_id: int,
        user_id: int,
        db: AsyncSession
    ) -> Optional[AIDraft]:
        stmt = select(AIDraft).where(
            AIDraft.id == draft_id,
            AIDraft.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_draft_by_uuid(
        draft_uuid: str,
        user_id: int,
        db: AsyncSession
    ) -> Optional[AIDraft]:
        stmt = select(AIDraft).where(
            AIDraft.uuid == draft_uuid,
            AIDraft.user_id == user_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_draft(
        draft_id: int,
        user_id: int,
        updates: DraftUpdateRequest,
        db: AsyncSession
    ) -> Optional[AIDraft]:
        stmt = select(AIDraft).where(
            AIDraft.id == draft_id,
            AIDraft.user_id == user_id
        )
        result = await db.execute(stmt)
        draft = result.scalar_one_or_none()
        
        if not draft:
            return None
        
        update_data = updates.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(draft, key, value)
        
        await db.commit()
        await db.refresh(draft)
        return draft
    
    @staticmethod
    async def delete_draft(
        draft_id: int,
        user_id: int,
        db: AsyncSession
    ) -> bool:
        stmt = delete(AIDraft).where(
            AIDraft.id == draft_id,
            AIDraft.user_id == user_id
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def get_drafts_count(
        user_id: int,
        db: AsyncSession
    ) -> int:
        stmt = select(func.count(AIDraft.id)).where(AIDraft.user_id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one()
    
    @staticmethod
    async def get_favorite_drafts(
        user_id: int,
        skip: int = 0,
        limit: int = 50,
        db: AsyncSession = None
    ) -> List[AIDraft]:
        stmt = (
            select(AIDraft)
            .where(AIDraft.user_id == user_id, AIDraft.favorite == True)
            .order_by(AIDraft.updated_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        return result.scalars().all()

