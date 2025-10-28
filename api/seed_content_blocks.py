"""
Seed script to create test blog posts with rich content blocks
including dropcaps, blockquotes, and images for testing the interactive post detail page.
"""
import asyncio
import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db_session
from models.user import User
from models.post import Post, Category, Tag
from datetime import datetime, timedelta


async def get_or_create_user(session: AsyncSession):
    """Get or create a test user"""
    result = await session.execute(
        select(User).where(User.email == "author@craftyxhub.com")
    )
    user = result.scalar_one_or_none()
    
    if not user:
        from models.user import UserRole
        user = User(
            username="content_author",
            email="author@craftyxhub.com",
            full_name="Content Author",
            password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqVr/1jRiq",
            is_active=True,
            is_verified=True,
            role=UserRole.USER
        )
        session.add(user)
        await session.flush()
    
    return user


async def get_or_create_category(session: AsyncSession, name: str, slug: str):
    """Get or create a category"""
    result = await session.execute(
        select(Category).where(Category.slug == slug)
    )
    category = result.scalar_one_or_none()
    
    if not category:
        category = Category(
            name=name,
            slug=slug,
            description=f"Articles about {name.lower()}"
        )
        session.add(category)
        await session.flush()
    
    return category


async def get_or_create_tag(session: AsyncSession, name: str, slug: str):
    """Get or create a tag"""
    result = await session.execute(
        select(Tag).where(Tag.slug == slug)
    )
    tag = result.scalar_one_or_none()
    
    if not tag:
        tag = Tag(name=name, slug=slug)
        session.add(tag)
        await session.flush()
    
    return tag


async def seed_content_blocks_posts():
    """Seed two blog posts with rich content blocks"""
    async for session in get_db_session():
        print("🚀 Starting content blocks seed...")
        
        user = await get_or_create_user(session)
        tech_category = await get_or_create_category(session, "Technology", "technology")
        design_category = await get_or_create_category(session, "Design", "design")
        
        ai_tag = await get_or_create_tag(session, "AI", "ai")
        future_tag = await get_or_create_tag(session, "Future", "future")
        ux_tag = await get_or_create_tag(session, "UX", "ux")
        creativity_tag = await get_or_create_tag(session, "Creativity", "creativity")
        
        # Post 1: The Future of Artificial Intelligence
        post1_content_blocks = {
            "blocks": [
                {
                    "type": "dropcap",
                    "content": "Artificial Intelligence is no longer a distant dream confined to science fiction. It has become an integral part of our daily lives, transforming industries and reshaping how we interact with technology. From virtual assistants to autonomous vehicles, AI is revolutionizing the world at an unprecedented pace."
                },
                {
                    "type": "paragraph",
                    "content": "The rapid advancement of machine learning algorithms has enabled computers to perform tasks that once required human intelligence. Natural language processing allows machines to understand and respond to human speech, while computer vision enables them to interpret visual information with remarkable accuracy."
                },
                {
                    "type": "blockquote",
                    "content": "The question is not whether AI will change our world, but how we will adapt to the changes it brings.",
                    "author": "Dr. Sarah Chen, AI Research Lead"
                },
                {
                    "type": "paragraph",
                    "content": "As we stand on the brink of this technological revolution, it's crucial to consider both the opportunities and challenges that AI presents. While it promises to solve complex problems and improve efficiency, we must also address concerns about privacy, job displacement, and ethical implications."
                },
                {
                    "type": "paragraph",
                    "content": "The future of AI lies not just in creating more powerful algorithms, but in developing systems that are transparent, fair, and aligned with human values. As we continue to push the boundaries of what's possible, we must ensure that AI serves humanity's best interests."
                }
            ]
        }
        
        post1 = Post(
            title="The Future of Artificial Intelligence: Opportunities and Challenges",
            slug="future-of-artificial-intelligence",
            content="Artificial Intelligence is no longer a distant dream confined to science fiction...",
            content_blocks=post1_content_blocks,
            excerpt="Explore how AI is transforming our world and what the future holds for this revolutionary technology. From machine learning to ethical considerations, discover the opportunities and challenges ahead.",
            author_id=user.id,
            category_id=tech_category.id,
            is_published=True,
            is_featured=True,
            reading_time=5,
            view_count=2450,
            meta_title="The Future of AI: Opportunities and Challenges | CraftyXhub",
            meta_description="Discover how artificial intelligence is reshaping our world. Learn about the opportunities, challenges, and ethical considerations of AI technology.",
            published_at=datetime.utcnow() - timedelta(days=2)
        )
        
        post1.tags.extend([ai_tag, future_tag])
        session.add(post1)
        
        # Post 2: The Art of Minimalist Design
        post2_content_blocks = {
            "blocks": [
                {
                    "type": "dropcap",
                    "content": "Less is more. This timeless principle has guided designers for decades, and in today's cluttered digital landscape, it's more relevant than ever. Minimalist design isn't about removing features—it's about removing distractions to highlight what truly matters."
                },
                {
                    "type": "paragraph",
                    "content": "The essence of minimalist design lies in its ability to communicate clearly and effectively. By stripping away unnecessary elements, designers create experiences that are intuitive, elegant, and focused on the user's needs. Every element serves a purpose, and nothing is included without careful consideration."
                },
                {
                    "type": "blockquote",
                    "content": "Simplicity is the ultimate sophistication. Good design is as little design as possible.",
                    "author": "Dieter Rams, Industrial Designer"
                },
                {
                    "type": "paragraph",
                    "content": "In practice, minimalist design requires discipline and restraint. It's tempting to add more features, more colors, more animations. But true mastery comes from knowing what to leave out. White space becomes as important as the content itself, creating breathing room that allows the eye to rest and the mind to focus."
                },
                {
                    "type": "paragraph",
                    "content": "The impact of minimalist design extends beyond aesthetics. It improves usability, reduces cognitive load, and creates memorable experiences. When users can accomplish their goals without friction, they develop trust and loyalty. In a world of endless options and constant stimulation, simplicity stands out."
                },
                {
                    "type": "blockquote",
                    "content": "Design is not just what it looks like and feels like. Design is how it works.",
                    "author": "Steve Jobs"
                },
                {
                    "type": "paragraph",
                    "content": "As we move forward in the digital age, the principles of minimalist design will continue to guide us toward creating better, more human-centered experiences. The challenge isn't to do more with less—it's to do exactly what's needed, nothing more, nothing less."
                }
            ]
        }
        
        post2 = Post(
            title="The Art of Minimalist Design: Less is More",
            slug="art-of-minimalist-design",
            content="Less is more. This timeless principle has guided designers for decades...",
            content_blocks=post2_content_blocks,
            excerpt="Discover the power of minimalist design and how simplicity can create more impactful user experiences. Learn the principles that make minimalism work in modern digital design.",
            author_id=user.id,
            category_id=design_category.id,
            is_published=True,
            is_featured=False,
            reading_time=4,
            view_count=1820,
            meta_title="The Art of Minimalist Design | CraftyXhub",
            meta_description="Learn how minimalist design principles create better user experiences. Discover why less is more in modern digital design.",
            published_at=datetime.utcnow() - timedelta(days=5)
        )
        
        post2.tags.extend([ux_tag, creativity_tag])
        session.add(post2)
        
        await session.commit()
        
        print(f'\n🎉 Seeding completed! Created 2 posts with rich content blocks.')
        print('\n📝 Posts created:')
        print(f'  1. "{post1.title}"')
        print(f'     - Slug: {post1.slug}')
        print(f'     - Category: {tech_category.name}')
        print(f'     - Tags: {", ".join([tag.name for tag in post1.tags])}')
        print(f'     - Content blocks: {len(post1_content_blocks["blocks"])} blocks')
        print(f'     - Includes: dropcap, paragraphs, blockquotes')
        print(f'\n  2. "{post2.title}"')
        print(f'     - Slug: {post2.slug}')
        print(f'     - Category: {design_category.name}')
        print(f'     - Tags: {", ".join([tag.name for tag in post2.tags])}')
        print(f'     - Content blocks: {len(post2_content_blocks["blocks"])} blocks')
        print(f'     - Includes: dropcap, paragraphs, blockquotes')
        print('\n✅ You can now test these posts on the frontend!')
        print(f'   - http://localhost:3000/posts/{post1.slug}')
        print(f'   - http://localhost:3000/posts/{post2.slug}')


if __name__ == '__main__':
    asyncio.run(seed_content_blocks_posts())
