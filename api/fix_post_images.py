"""
Fix post images in production database.
Updates posts with broken Unsplash URLs to use the fixed URLs.
Run on VPS: python fix_post_images.py
"""
import asyncio
from sqlalchemy import select, update
from database.connection import get_db_session
from models.post import Post

# Map of post slugs to their corrected image URLs
# Generated from the differences between old and new seed_full_posts.py
IMAGE_FIXES = {
    # Artificial Intelligence
    "ethical-ai-navigating-the-bias-problem": "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?w=800&q=80",
    
    # Blockchain
    "smart-contracts-automating-trust": "https://images.unsplash.com/photo-1639322537228-f710d846310a?w=800&q=80",
    
    # Automation
    "smart-home-automation-for-productivity": "https://images.unsplash.com/photo-1556155092-490a1ba16284?w=800&q=80",
    
    # Programming
    "why-typescript-is-winning-the-web": "https://images.unsplash.com/photo-1587620962725-abab7fe55159?w=800&q=80",
    "the-rise-of-rust-performance-meets-safety": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=800&q=80",
    
    # Cybersecurity
    "two-factor-authentication-2fa-explained": "https://images.unsplash.com/photo-1555949963-ff9fe0c870eb?w=800&q=80",
    
    # Entrepreneurship
    "bootstrapping-vs-venture-capital-the-honest-truth": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800&q=80",
    
    # Personal Finance
    "the-50-30-20-rule-budgeting-made-simple": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800&q=80",
    "index-funds-vs-individual-stocks": "https://images.unsplash.com/photo-1633158829585-23ba8f7c8caf?w=800&q=80",
    
    # Creator Economy
    "monetizing-your-newsletter-substack-and-beyond": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800&q=80",
    "the-economics-of-youtube-revenue": "https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0?w=800&q=80",
    
    # Passive Income
    "dividend-investing-for-beginners": "https://images.unsplash.com/photo-1579621970795-87facc2f976d?w=800&q=80",
    
    # Career Development
    "navigating-a-mid-career-pivot": "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=800&q=80",
    
    # Productivity
    "the-pomodoro-technique-revisited": "https://images.unsplash.com/photo-1434626881859-194d67b2b86f?w=800&q=80",
    
    # Remote Work
    "async-work-the-future-of-remote-teams": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=800&q=80",
    "setting-up-an-ergonomic-home-office": "https://images.unsplash.com/photo-1593642702821-c8da6771f0c6?w=800&q=80",
    
    # Personal Branding
    "optimizing-your-linkedin-profile": "https://images.unsplash.com/photo-1611532736597-de2d4265fba3?w=800&q=80",
    "why-you-should-start-a-professional-blog": "https://images.unsplash.com/photo-1504805572947-34fad45aed93?w=800&q=80",
    "networking-for-introverts": "https://images.unsplash.com/photo-1552581234-26160f608093?w=800&q=80",
    
    # Minimalism
    "digital-minimalism-reclaiming-your-attention": "https://images.unsplash.com/photo-1493723843671-1d655e66ac1c?w=800&q=80",
    "the-konmari-method-for-your-digital-files": "https://images.unsplash.com/photo-1449247709967-d4461a6a6103?w=800&q=80",
    "essentialism-the-disciplined-pursuit-of-less": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800&q=80",
    
    # Wellness
    "sleep-hygiene-for-high-performers": "https://images.unsplash.com/photo-1544367567-0f2fcb009e0b?w=800&q=80",
    
    # Sustainable Living
    "zero-waste-a-beginners-guide": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&q=80",
    "ethical-fashion-building-a-sustainable-wardrobe": "https://images.unsplash.com/photo-1558171813-4c088753af8f?w=800&q=80",
}


async def fix_post_images():
    """Update posts with corrected image URLs"""
    print("🔧 Starting image URL fix migration...\n")
    
    updated = 0
    not_found = 0
    
    async for session in get_db_session():
        for slug, new_image_url in IMAGE_FIXES.items():
            # Find the post by slug
            stmt = select(Post).where(Post.slug == slug)
            result = await session.execute(stmt)
            post = result.scalar_one_or_none()
            
            if post:
                old_url = post.featured_image
                post.featured_image = new_image_url
                updated += 1
                print(f"  ✅ Updated: {slug}")
                print(f"     Old: {old_url[:60]}...")
                print(f"     New: {new_image_url[:60]}...")
            else:
                not_found += 1
                print(f"  ⏭️ Not found: {slug}")
        
        await session.commit()
    
    print(f"\n{'='*60}")
    print(f"📊 Results: {updated} updated, {not_found} not found")
    print("🎉 Migration complete!")


if __name__ == "__main__":
    asyncio.run(fix_post_images())
