import asyncio
import random
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from models.user import User
from models.post import Post, Category, Tag
from services.user.auth import AuthService
from utils.slug_generator import generate_slug
from sqlalchemy import select, func

async def get_or_create_user(session: AsyncSession, email: str, username: str, full_name: str, password: str):
    user = await AuthService.get_user_by_email(session, email)
    if user:
        return user
    hashed_password = AuthService.get_password_hash(password)
    user = User(email=email, username=username, full_name=full_name, password=hashed_password, is_active=True, is_verified=True)
    session.add(user)
    await session.flush()
    await session.refresh(user)
    return user

async def get_or_create_category(session: AsyncSession, name: str, slug: str):
    stmt = select(Category).where(Category.slug == slug)
    result = await session.execute(stmt)
    category = result.scalar_one_or_none()
    if category:
        return category
    category = Category(name=name, slug=slug)
    session.add(category)
    await session.flush()
    await session.refresh(category)
    return category

async def seed_popular_posts():
    async for session in get_db_session():
        print("🚀 Starting popular posts seed...")
        
        # Get or create a test user
        user = await get_or_create_user(
            session,
            email='test@craftyx.com',
            username='testuser',
            full_name='Test User',
            password='test123'
        )
        
        # Get or create a test category
        category = await get_or_create_category(
            session,
            name='Popular Content',
            slug='popular-content'
        )
        
        # Create 10 sample posts with varying popularity (ordered by view_count DESC)
        popular_posts_data = [
            {"title": "Ultimate Guide to React Hooks", "views": 15000},
            {"title": "Top Tips for JavaScript Performance", "views": 12500},
            {"title": "Best Practices for API Design", "views": 11200},
            {"title": "Beginner Tutorial: CSS Grid Layout", "views": 9800},
            {"title": "Advanced Python Techniques", "views": 8900},
            {"title": "Modern Web Development Workflow", "views": 7600},
            {"title": "Database Optimization Strategies", "views": 6400},
            {"title": "Frontend Testing Best Practices", "views": 5300},
            {"title": "Docker for Development", "views": 4200},
            {"title": "Git Workflow for Teams", "views": 3100}
        ]
        
        for i, post_data in enumerate(popular_posts_data, 1):
            title = post_data["title"]
            view_count = post_data["views"]
            
            # Check if post already exists
            existing_slug = generate_slug(title)
            stmt = select(Post).where(Post.slug == existing_slug)
            result = await session.execute(stmt)
            existing_post = result.scalar_one_or_none()
            
            if existing_post:
                print(f"⏭️  Post '{title}' already exists, skipping...")
                continue
            
            content = f"""# {title}

This is sample content for popular post {i}. This post has gained significant traction with {view_count} views from our community.

## Introduction

Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris.

## Key Points

- Point 1: Important concept
- Point 2: Practical application  
- Point 3: Best practices
- Point 4: Common pitfalls to avoid

## Conclusion

This comprehensive guide provides valuable insights for developers at all levels. The high engagement metrics demonstrate the community's interest in quality content.

*Published {random.randint(1, 30)} days ago*
"""
            
            post = Post(
                title=title,
                slug=existing_slug,
                content=content,
                excerpt=f'Comprehensive guide with {view_count} views - {title[:100]}...',
                author_id=user.id,
                category_id=category.id,
                is_published=True,
                is_featured=random.choice([True, False]),
                reading_time=random.randint(5, 15),
                published_at=datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                view_count=view_count  # This is what determines "popularity" in the API
            )
            
            session.add(post)
            await session.flush()
            
            print(f'✅ Created popular post: {title} ({view_count} views)')
        
        await session.commit()
        print(f'\n🎉 Seeding completed! Created {len(popular_posts_data)} popular posts with realistic view counts.')
        print('📊 Posts are ordered by view_count for the /posts/popular endpoint.')
        print('🔥 The post with 15,000 views will appear first in popular posts!')

if __name__ == '__main__':
    asyncio.run(seed_popular_posts()) 