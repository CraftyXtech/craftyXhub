"""
Post Content Enhancement Script
Updates all seeded posts with richer 500+ word content.
Also fixes dates (Oct 1 2025 - Jan 5 2026) and outdated year references.

EXCLUDES: "Software 2.0: The Future of Coding Without Code" (manually created)

Usage:
    python enhance_posts.py
"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select
from database.connection import get_db_session
from models import Post, Category

# Post to exclude (manually created)
EXCLUDE_SLUGS = ["software-20-the-future-of-coding-without-code"]

# Date range: Oct 1 2025 to Jan 5 2026
START_DATE = datetime(2025, 10, 1, 8, 0, 0)
END_DATE = datetime(2026, 1, 5, 18, 0, 0)

# Title fixes for outdated year references
TITLE_FIXES = {
    "SEO in 2024: Content Clusters and E-E-A-T": "SEO in 2025: Content Clusters and E-E-A-T",
    "Clean Code Principles for 2024": "Clean Code Principles for Modern Codebases"
}


def get_category_type(category_slug: str) -> str:
    """Determine the content type based on category"""
    if not category_slug:
        return "general"
    
    slug = category_slug.lower()
    if any(x in slug for x in ['programming', 'automation', 'artificial-intelligence', 'blockchain', 'cybersecurity', 'web-development']):
        return "tech"
    elif any(x in slug for x in ['finance', 'investing', 'money', 'business', 'startup', 'passive-income', 'crypto', 'freelancing']):
        return "finance"
    elif any(x in slug for x in ['wellness', 'health', 'mindset', 'minimalism', 'living', 'growth', 'sustainable']):
        return "wellness"
    elif any(x in slug for x in ['career', 'remote-work', 'productivity', 'networking']):
        return "career"
    return "general"


def generate_enhanced_content(title: str, excerpt: str, category_type: str) -> str:
    """Generate 500+ word content tailored to the topic and category"""
    
    # Extract main topic from title
    main_topic = title.split(":")[0].strip() if ":" in title else title
    
    content = f"# {title}\n\n"
    
    # Introduction (60-80 words)
    if category_type == "tech":
        content += f"In the rapidly evolving landscape of technology, **{main_topic}** has emerged as a critical area that every developer and tech professional must understand. "
        content += f"The pace of innovation continues to accelerate, and those who master these concepts gain a significant competitive advantage. "
        content += f"This comprehensive guide explores the fundamentals, best practices, and practical applications that will help you excel in this domain.\n\n"
    elif category_type == "finance":
        content += f"Financial literacy is no longer optional—it's essential for building long-term wealth and security. **{main_topic}** represents one of the most impactful areas where informed decisions can dramatically improve your financial outcomes. "
        content += f"Whether you're just starting your wealth-building journey or looking to optimize an existing strategy, understanding these principles is crucial.\n\n"
    elif category_type == "wellness":
        content += f"In our hyper-connected, always-on world, prioritizing well-being has never been more important. **{main_topic}** offers a framework for reclaiming balance and improving your quality of life. "
        content += f"Research consistently shows that small, intentional changes compound into significant transformations over time. This guide will show you how to get started.\n\n"
    elif category_type == "career":
        content += f"The professional landscape is changing faster than ever before. **{main_topic}** has become essential knowledge for anyone looking to advance their career and stay relevant in a competitive job market. "
        content += f"Whether you're climbing the corporate ladder or building your own path, these insights will prove invaluable.\n\n"
    else:
        content += f"**{main_topic}** has gained significant attention in recent years, and for good reason. Understanding this topic can unlock new opportunities and help you make better decisions. "
        content += f"This article breaks down the essential concepts, provides actionable strategies, and offers practical tips you can apply immediately.\n\n"
    
    # Why This Matters Section (100-120 words)
    content += "## Why This Matters Now\n\n"
    content += f"{excerpt} "
    
    if category_type == "tech":
        content += "The technology industry moves at breakneck speed, and staying current isn't just about career advancement—it's about remaining employable in an increasingly automated world. "
        content += "Companies are actively seeking professionals who understand these concepts deeply. "
        content += "Moreover, the principles discussed here have applications far beyond their obvious use cases, making them valuable across multiple domains and industries.\n\n"
    elif category_type == "finance":
        content += "Financial markets are more accessible than ever, but this accessibility comes with risks for the uninformed. "
        content += "Understanding these concepts protects you from common mistakes that cost people thousands of dollars annually. "
        content += "More importantly, applying these principles early creates a compounding effect that can mean the difference between financial freedom and perpetual stress.\n\n"
    elif category_type == "wellness":
        content += "Mental health challenges have reached epidemic proportions, with burnout affecting professionals across every industry. "
        content += "Investing in these practices isn't just about feeling better—it's about performing better and sustaining success long-term. "
        content += "The most successful people in any field understand that peak performance requires holistic well-being.\n\n"
    else:
        content += "The gap between those who understand these principles and those who don't continues to widen. "
        content += "Early adopters and informed practitioners consistently outperform their peers. "
        content += "Taking the time to master these concepts now positions you ahead of the curve for future developments.\n\n"
    
    # Key Concepts Section (150-180 words)
    content += "## Core Concepts and Strategies\n\n"
    content += "Success in this area requires understanding several interconnected principles. Let's break down the most important ones:\n\n"
    
    content += "### 1. Foundation First\n\n"
    if category_type == "tech":
        content += "Before diving into advanced implementations, ensure your fundamentals are rock-solid. "
        content += "This means understanding not just the 'how' but the 'why' behind each concept. "
        content += "Strong foundations enable faster learning of new technologies and better problem-solving when things don't work as expected.\n\n"
    elif category_type == "finance":
        content += "Before chasing high returns, establish an emergency fund and clear high-interest debt. "
        content += "This provides the stability needed to take calculated risks without jeopardizing your financial security. "
        content += "Many investors fail not because of poor strategy, but because they lack this foundational stability.\n\n"
    else:
        content += "Building on solid fundamentals ensures sustainable progress. "
        content += "Rushing past the basics often leads to frustration and failure later. "
        content += "Take the time to truly understand the core principles before advancing to more complex applications.\n\n"
    
    content += "### 2. Consistent Application\n\n"
    if category_type == "wellness":
        content += "Knowledge without practice is worthless. Start with small, manageable daily habits rather than dramatic lifestyle overhauls. "
        content += "Research shows that habits formed gradually are significantly more likely to stick long-term. "
        content += "The goal is progress, not perfection.\n\n"
    elif category_type == "tech":
        content += "Reading documentation isn't enough—you need hands-on practice. Build projects, contribute to open source, and apply concepts in real scenarios. "
        content += "The gap between theoretical understanding and practical skill is bridged only through consistent application. "
        content += "Aim to code or practice every day, even if just for 30 minutes.\n\n"
    else:
        content += "Theory transforms into results only through consistent action. Create systems and routines that make application automatic. "
        content += "The compound effect of small daily improvements dramatically outperforms sporadic bursts of intense effort.\n\n"
    
    content += "### 3. Continuous Learning\n\n"
    content += "The landscape evolves constantly, and yesterday's best practices may become tomorrow's anti-patterns. "
    content += "Dedicate time each week to learning—whether through articles, courses, podcasts, or conversations with experts. "
    content += "The most successful individuals are perpetual students, always open to updating their mental models.\n\n"
    
    # Practical Tips (80-100 words)
    content += "## Practical Tips for Getting Started\n\n"
    content += "Ready to take action? Here are concrete steps you can implement today:\n\n"
    
    if category_type == "tech":
        content += "- **Set up a learning environment**: Create a dedicated workspace with the tools you need.\n"
        content += "- **Build a portfolio project**: Apply what you learn immediately in a real project.\n"
        content += "- **Join a community**: Connect with others learning the same skills for support and accountability.\n"
        content += "- **Document your journey**: Writing about what you learn reinforces understanding.\n\n"
    elif category_type == "finance":
        content += "- **Audit your current situation**: Know exactly where your money goes each month.\n"
        content += "- **Automate savings**: Remove willpower from the equation by making contributions automatic.\n"
        content += "- **Start with low-cost index funds**: Don't overcomplicate early investing.\n"
        content += "- **Review quarterly**: Schedule time to assess and adjust your strategy.\n\n"
    elif category_type == "wellness":
        content += "- **Start with five minutes daily**: Small habits build momentum.\n"
        content += "- **Stack new habits on existing ones**: Link new behaviors to established routines.\n"
        content += "- **Track your progress**: What gets measured gets improved.\n"
        content += "- **Find an accountability partner**: Social commitment significantly improves follow-through.\n\n"
    else:
        content += "- **Define clear, measurable goals**: Vague intentions lead to vague results.\n"
        content += "- **Create a simple action plan**: Break down goals into weekly and daily tasks.\n"
        content += "- **Remove friction**: Make the right behaviors as easy as possible.\n"
        content += "- **Celebrate small wins**: Positive reinforcement sustains motivation.\n\n"
    
    # Common Mistakes (60-80 words)
    content += "## Common Mistakes to Avoid\n\n"
    content += "Learning from others' errors accelerates your progress. Watch out for these pitfalls:\n\n"
    
    if category_type == "tech":
        content += "- **Tutorial hell**: Watching tutorials without building anything. Practice is essential.\n"
        content += "- **Premature optimization**: Perfect is the enemy of done. Ship early, improve later.\n"
        content += "- **Working in isolation**: Feedback from others accelerates learning tremendously.\n\n"
    elif category_type == "finance":
        content += "- **Emotional decision-making**: Fear and greed are your worst enemies.\n"
        content += "- **Timing the market**: Time in the market beats timing the market.\n"
        content += "- **Ignoring fees**: Small percentages compound into massive costs over time.\n\n"
    else:
        content += "- **All-or-nothing thinking**: Small progress is still progress.\n"
        content += "- **Comparing to others**: Your journey is unique; focus on your own improvement.\n"
        content += "- **Neglecting fundamentals**: Advanced tactics can't compensate for weak basics.\n\n"
    
    # Conclusion (50-70 words)
    content += "## Moving Forward\n\n"
    content += f"Mastering **{main_topic}** is a journey, not a destination. "
    content += "The key is to start—imperfect action beats perfect planning every time. "
    content += "Take one concept from this article and apply it today. Build from there. "
    content += "The compound effect of consistent effort will surprise you. "
    content += "Your future self will thank you for the investment you make now.\n"
    
    return content


async def enhance_posts():
    """Update all seeded posts with enhanced content"""
    
    async for session in get_db_session():
        print("🚀 Starting post enhancement...")
        
        # Get all posts with their categories
        stmt = select(Post, Category).join(Category, Post.category_id == Category.id)
        result = await session.execute(stmt)
        posts_with_categories = result.all()
        
        total_posts = len(posts_with_categories)
        print(f"📊 Found {total_posts} posts to process")
        
        # Calculate date distribution
        total_days = (END_DATE - START_DATE).days
        posts_to_update = [p for p, c in posts_with_categories if p.slug not in EXCLUDE_SLUGS]
        num_posts = len(posts_to_update)
        
        if num_posts == 0:
            print("⚠️ No posts to update!")
            return
        
        days_between = total_days / num_posts
        
        updated_count = 0
        skipped_count = 0
        
        for idx, (post, category) in enumerate(posts_with_categories):
            # Skip excluded posts
            if post.slug in EXCLUDE_SLUGS:
                print(f"  ⏭️ Skipping (excluded): {post.title}")
                skipped_count += 1
                continue
            
            # Fix title if needed
            original_title = post.title
            if post.title in TITLE_FIXES:
                post.title = TITLE_FIXES[post.title]
                print(f"  📝 Fixed title: {original_title} → {post.title}")
            
            # Generate enhanced content
            category_type = get_category_type(category.slug if category else None)
            new_content = generate_enhanced_content(post.title, post.excerpt or "", category_type)
            post.content = new_content
            
            # Redistribute date
            post_index = updated_count  # Use update count for even distribution
            new_date = START_DATE + timedelta(days=int(post_index * days_between))
            post.published_at = new_date
            
            session.add(post)
            updated_count += 1
            
            print(f"  ✅ Enhanced: {post.title[:50]}... ({len(new_content)} chars, {new_date.strftime('%Y-%m-%d')})")
        
        await session.commit()
        print(f"\n🎉 SUCCESS: Enhanced {updated_count} posts, skipped {skipped_count}")
        
        # Verification
        result = await session.execute(
            select(Post).where(Post.slug.not_in(EXCLUDE_SLUGS))
        )
        all_posts = result.scalars().all()
        
        avg_length = sum(len(p.content) for p in all_posts) / len(all_posts) if all_posts else 0
        print(f"📈 Average content length: {avg_length:.0f} chars (~{avg_length/5:.0f} words)")


if __name__ == "__main__":
    asyncio.run(enhance_posts())
