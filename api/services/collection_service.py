"""
Collection Service
Business logic for My Collection feature: Reading Lists, Reading History, Highlights
"""
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func, delete
from fastapi import HTTPException, status
from typing import List, Optional
import logging

from models import ReadingList, ReadingListItem, ReadingHistory, Highlight, Post, User
from schemas.collection import (
    ReadingListCreate, 
    ReadingListUpdate, 
    ReadingListItemCreate,
    HighlightCreate
)

logger = logging.getLogger(__name__)


class CollectionService:
    """Service for managing user collections"""
    
    # ===== Reading Lists =====
    
    @staticmethod
    async def get_user_lists(
        session: AsyncSession,
        user_id: int
    ) -> List[ReadingList]:
        """Get all reading lists for a user"""
        try:
            query = select(ReadingList).where(
                ReadingList.user_id == user_id
            ).options(
                selectinload(ReadingList.items)
            ).order_by(ReadingList.created_at.desc())
            
            result = await session.execute(query)
            return result.scalars().all()
        except SQLAlchemyError as e:
            logger.error(f"Error fetching user lists: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch reading lists"
            )
    
    @staticmethod
    async def create_list(
        session: AsyncSession,
        user_id: int,
        data: ReadingListCreate
    ) -> ReadingList:
        """Create a new reading list"""
        try:
            reading_list = ReadingList(
                user_id=user_id,
                name=data.name,
                description=data.description,
                is_public=data.is_public,
                cover_image=data.cover_image
            )
            session.add(reading_list)
            await session.commit()
            await session.refresh(reading_list)
            return reading_list
        except SQLAlchemyError as e:
            logger.error(f"Error creating reading list: {e}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create reading list"
            )
    
    @staticmethod
    async def get_list_by_uuid(
        session: AsyncSession,
        list_uuid: str,
        user_id: Optional[int] = None
    ) -> ReadingList:
        """Get a reading list by UUID with items"""
        try:
            query = select(ReadingList).where(
                ReadingList.uuid == list_uuid
            ).options(
                selectinload(ReadingList.items).selectinload(ReadingListItem.post).selectinload(Post.author),
                selectinload(ReadingList.user)
            )
            
            result = await session.execute(query)
            reading_list = result.scalar_one_or_none()
            
            if not reading_list:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Reading list not found"
                )
            
            # Check access if user_id provided
            if user_id and not reading_list.is_public and reading_list.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied to this reading list"
                )
            
            return reading_list
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error fetching reading list: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch reading list"
            )
    
    @staticmethod
    async def update_list(
        session: AsyncSession,
        list_uuid: str,
        user_id: int,
        data: ReadingListUpdate
    ) -> ReadingList:
        """Update a reading list"""
        try:
            reading_list = await CollectionService.get_list_by_uuid(session, list_uuid, user_id)
            
            if reading_list.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to update this list"
                )
            
            if data.name is not None:
                reading_list.name = data.name
            if data.description is not None:
                reading_list.description = data.description
            if data.is_public is not None:
                reading_list.is_public = data.is_public
            if data.cover_image is not None:
                reading_list.cover_image = data.cover_image
            
            await session.commit()
            await session.refresh(reading_list)
            return reading_list
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error updating reading list: {e}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update reading list"
            )
    
    @staticmethod
    async def delete_list(
        session: AsyncSession,
        list_uuid: str,
        user_id: int
    ) -> bool:
        """Delete a reading list"""
        try:
            reading_list = await CollectionService.get_list_by_uuid(session, list_uuid, user_id)
            
            if reading_list.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete this list"
                )
            
            await session.delete(reading_list)
            await session.commit()
            return True
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error deleting reading list: {e}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete reading list"
            )
    
    @staticmethod
    async def add_post_to_list(
        session: AsyncSession,
        list_uuid: str,
        user_id: int,
        post_uuid: str,
        note: Optional[str] = None
    ) -> ReadingListItem:
        """Add a post to a reading list"""
        try:
            reading_list = await CollectionService.get_list_by_uuid(session, list_uuid, user_id)
            
            if reading_list.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to modify this list"
                )
            
            # Get post
            result = await session.execute(select(Post).where(Post.uuid == post_uuid))
            post = result.scalar_one_or_none()
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found"
                )
            
            # Check if already in list
            existing = await session.execute(
                select(ReadingListItem).where(
                    ReadingListItem.list_id == reading_list.id,
                    ReadingListItem.post_id == post.id
                )
            )
            if existing.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Post already in this list"
                )
            
            # Get max position
            max_pos_result = await session.execute(
                select(func.max(ReadingListItem.position)).where(
                    ReadingListItem.list_id == reading_list.id
                )
            )
            max_pos = max_pos_result.scalar() or 0
            
            item = ReadingListItem(
                list_id=reading_list.id,
                post_id=post.id,
                note=note,
                position=max_pos + 1
            )
            session.add(item)
            await session.commit()
            await session.refresh(item)
            
            return item
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error adding post to list: {e}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add post to list"
            )
    
    @staticmethod
    async def remove_post_from_list(
        session: AsyncSession,
        list_uuid: str,
        user_id: int,
        post_uuid: str
    ) -> bool:
        """Remove a post from a reading list"""
        try:
            reading_list = await CollectionService.get_list_by_uuid(session, list_uuid, user_id)
            
            if reading_list.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to modify this list"
                )
            
            # Get post
            result = await session.execute(select(Post).where(Post.uuid == post_uuid))
            post = result.scalar_one_or_none()
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found"
                )
            
            # Find and delete the item
            await session.execute(
                delete(ReadingListItem).where(
                    ReadingListItem.list_id == reading_list.id,
                    ReadingListItem.post_id == post.id
                )
            )
            await session.commit()
            return True
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error removing post from list: {e}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to remove post from list"
            )
    
    # ===== Reading History =====
    
    @staticmethod
    async def get_reading_history(
        session: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[ReadingHistory], int]:
        """Get user's reading history"""
        try:
            # Get total count
            count_result = await session.execute(
                select(func.count()).select_from(ReadingHistory).where(
                    ReadingHistory.user_id == user_id
                )
            )
            total = count_result.scalar()
            
            # Get entries
            query = select(ReadingHistory).where(
                ReadingHistory.user_id == user_id
            ).options(
                selectinload(ReadingHistory.post).selectinload(Post.author)
            ).order_by(ReadingHistory.read_at.desc()).offset(skip).limit(limit)
            
            result = await session.execute(query)
            entries = result.scalars().all()
            
            return entries, total
        except SQLAlchemyError as e:
            logger.error(f"Error fetching reading history: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch reading history"
            )
    
    @staticmethod
    async def record_post_view(
        session: AsyncSession,
        user_id: int,
        post_uuid: str,
        progress: int = 0
    ) -> ReadingHistory:
        """Record or update a post view in history"""
        try:
            # Get post
            result = await session.execute(select(Post).where(Post.uuid == post_uuid))
            post = result.scalar_one_or_none()
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found"
                )
            
            # Check for existing entry
            existing = await session.execute(
                select(ReadingHistory).where(
                    ReadingHistory.user_id == user_id,
                    ReadingHistory.post_id == post.id
                )
            )
            entry = existing.scalar_one_or_none()
            
            if entry:
                # Update existing entry
                entry.read_at = func.now()
                if progress > entry.read_progress:
                    entry.read_progress = progress
            else:
                # Create new entry
                entry = ReadingHistory(
                    user_id=user_id,
                    post_id=post.id,
                    read_progress=progress
                )
                session.add(entry)
            
            await session.commit()
            await session.refresh(entry)
            return entry
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error recording post view: {e}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to record post view"
            )
    
    @staticmethod
    async def clear_reading_history(
        session: AsyncSession,
        user_id: int
    ) -> bool:
        """Clear all reading history for a user"""
        try:
            await session.execute(
                delete(ReadingHistory).where(ReadingHistory.user_id == user_id)
            )
            await session.commit()
            return True
        except SQLAlchemyError as e:
            logger.error(f"Error clearing reading history: {e}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to clear reading history"
            )
    
    # ===== Highlights (Phase 2) =====
    
    @staticmethod
    async def get_user_highlights(
        session: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[Highlight], int]:
        """Get user's highlights"""
        try:
            count_result = await session.execute(
                select(func.count()).select_from(Highlight).where(
                    Highlight.user_id == user_id
                )
            )
            total = count_result.scalar()
            
            query = select(Highlight).where(
                Highlight.user_id == user_id
            ).options(
                selectinload(Highlight.post).selectinload(Post.author)
            ).order_by(Highlight.created_at.desc()).offset(skip).limit(limit)
            
            result = await session.execute(query)
            highlights = result.scalars().all()
            
            return highlights, total
        except SQLAlchemyError as e:
            logger.error(f"Error fetching highlights: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch highlights"
            )
    
    @staticmethod
    async def create_highlight(
        session: AsyncSession,
        user_id: int,
        data: HighlightCreate
    ) -> Highlight:
        """Create a new highlight"""
        try:
            # Get post
            result = await session.execute(select(Post).where(Post.uuid == data.post_uuid))
            post = result.scalar_one_or_none()
            if not post:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Post not found"
                )
            
            highlight = Highlight(
                user_id=user_id,
                post_id=post.id,
                text=data.text,
                note=data.note,
                position_start=data.position_start,
                position_end=data.position_end
            )
            session.add(highlight)
            await session.commit()
            await session.refresh(highlight)
            return highlight
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error creating highlight: {e}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create highlight"
            )
    
    @staticmethod
    async def delete_highlight(
        session: AsyncSession,
        highlight_uuid: str,
        user_id: int
    ) -> bool:
        """Delete a highlight"""
        try:
            result = await session.execute(
                select(Highlight).where(Highlight.uuid == highlight_uuid)
            )
            highlight = result.scalar_one_or_none()
            
            if not highlight:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Highlight not found"
                )
            
            if highlight.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to delete this highlight"
                )
            
            await session.delete(highlight)
            await session.commit()
            return True
        except HTTPException:
            raise
        except SQLAlchemyError as e:
            logger.error(f"Error deleting highlight: {e}")
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete highlight"
            )
