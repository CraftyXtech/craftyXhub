"""
Fix post images in production database.
Updates posts with broken Unsplash URLs to use the fixed URLs.
Run on VPS: source venv/bin/activate && python fix_post_images.py
"""
import asyncio
from sqlalchemy import select
from database.connection import get_db_session
from models.post import Post

# Map of post titles to their corrected image URLs
IMAGE_FIXES = {
    # Artificial Intelligence
    "Ethical AI: Navigating the Bias Problem": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&q=80",
    
    # Blockchain
    "Smart Contracts: Automating Trust": "https://images.unsplash.com/photo-1639322537228-f710d846310a?w=800&q=80",
    
    # Automation
    "Smart Home Automation for Productivity": "https://images.unsplash.com/photo-1556155092-490a1ba16284?w=800&q=80",
    
    # Programming
    "Why TypeScript is Winning the Web": "https://images.unsplash.com/photo-1587620962725-abab7fe55159?w=800&q=80",
    "The Rise of Rust: Performance Meets Safety": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=800&q=80",
    
    # Cybersecurity
    "Two-Factor Authentication (2FA) Explained": "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80",
    
    # Entrepreneurship
    "Bootstrapping vs. Venture Capital: The Honest Truth": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
    
    # Personal Finance
    "The 50/30/20 Rule: Budgeting Made Simple": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
    "Index Funds vs. Individual Stocks": "https://images.unsplash.com/photo-1633158829585-23ba8f7c8caf?w=800&q=80",
    
    # Creator Economy
    "Monetizing Your Newsletter: Substack and Beyond": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800&q=80",
    "The Economics of YouTube Revenue": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=800&q=80",
    
    # Passive Income
    "Dividend Investing for Beginners": "https://images.unsplash.com/photo-1579621970795-87facc2f976d?w=800&q=80",
    
    # Career Development
    "Navigating a Mid-Career Pivot": "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=800&q=80",
    
    # Productivity
    "The Pomodoro Technique Revisited": "https://images.unsplash.com/photo-1434626881859-194d67b2b86f?w=800&q=80",
    
    # Remote Work
    "Async Work: The Future of Remote Teams": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80",
    "Setting Up an Ergonomic Home Office": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=800&q=80",
    
    # Personal Branding
    "Optimizing Your LinkedIn Profile": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800&q=80",
    "Why You Should Start a Professional Blog": "https://images.unsplash.com/photo-1504805572947-34fad45aed93?w=800&q=80",
    "Networking for Introverts": "https://images.unsplash.com/photo-1552581234-26160f608093?w=800&q=80",
    
    # Minimalism
    "Digital Minimalism: Reclaiming Your Attention": "https://images.unsplash.com/photo-1493723843671-1d655e66ac1c?w=800&q=80",
    "The KonMari Method for Your Digital Files": "https://images.unsplash.com/photo-1449247709967-d4461a6a6103?w=800&q=80",
    "Essentialism: The Disciplined Pursuit of Less": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80",
    
    # Wellness
    "Sleep Hygiene for High Performers": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&q=80",
    
    # Sustainable Living
    "Zero Waste: A Beginner's Guide": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&q=80",
    "Ethical Fashion: Building a Sustainable Wardrobe": "https://images.unsplash.com/photo-1558171813-4c088753af8f?w=800&q=80",
}


async def fix_post_images():
    """Update posts with corrected image URLs by matching on title"""
    print("🔧 Starting image URL fix migration...\n")
    
    updated = 0
    not_found = 0
    
    async for session in get_db_session():
        for title, new_image_url in IMAGE_FIXES.items():
            # Find the post by title (exact match)
            stmt = select(Post).where(Post.title == title)
            result = await session.execute(stmt)
            post = result.scalar_one_or_none()
            
            if post:
                old_url = post.featured_image
                post.featured_image = new_image_url
                updated += 1
                print(f"  ✅ Updated: {title[:50]}...")
                print(f"     Old: {old_url[:60]}...")
                print(f"     New: {new_image_url[:60]}...")
            else:
                not_found += 1
                print(f"  ⏭️ Not found: {title[:50]}...")
        
        await session.commit()
    
    print(f"\n{'='*60}")
    print(f"📊 Results: {updated} updated, {not_found} not found")
    print("🎉 Migration complete!")


if __name__ == "__main__":
    asyncio.run(fix_post_images())
