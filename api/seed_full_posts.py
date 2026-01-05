"""
Seed posts for all 24 categories with images
Run: python seed_full_posts.py
"""
import asyncio
from datetime import datetime, timedelta
import random
from sqlalchemy import select
from database.connection import get_db_session
from models.user import User
from models.post import Post, Category
from utils.slug_generator import generate_slug

# Comprehensive post data for all 20 subcategories
POSTS_DATA = {
    # --- Tech & Innovation ---
    "artificial-intelligence": [
        {
            "title": "The Evolution of Generative AI: From GPT-3 to Today",
            "excerpt": "Tracing the rapid rise of Large Language Models and how they are reshaping creativity and work.",
            "img": "https://images.unsplash.com/photo-1677442136019-21780ecad995?w=800&q=80"
        },
        {
            "title": "Machine Learning in Healthcare: Saving Lives with Data",
            "excerpt": "How AI algorithms are predicting diseases earlier and personalizing patient treatment plans.",
            "img": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=800&q=80"
        },
        {
            "title": "Ethical AI: Navigating the Bias Problem",
            "excerpt": "Understanding the challenges of bias in AI systems and how developers are working to solve them.",
            "img": "https://images.unsplash.com/photo-1620712943543-bcc4638d71d0?w=800&q=80"
        }
    ],
    "blockchain-and-cryptocurrencies": [
        {
            "title": "DeFi Explained: The Future of Banking without Banks",
            "excerpt": "A deep dive into Decentralized Finance and how it's disrupting traditional financial institutions.",
            "img": "https://images.unsplash.com/photo-1639762681485-074b7f938ba0?w=800&q=80"
        },
        {
            "title": "Understanding NFTs Beyond the Hype",
            "excerpt": "How Non-Fungible Tokens are changing digital ownership, gaming, and intellectual property.",
            "img": "https://images.unsplash.com/photo-1642104704074-907c0698cbd9?w=800&q=80"
        },
        {
            "title": "Smart Contracts: Automating Trust",
            "excerpt": "How self-executing contracts on the blockchain are removing the need for intermediaries.",
            "img": "https://images.unsplash.com/photo-1621504450181-5d356f63d3ee?w=800&q=80"
        }
    ],
    "automation-and-smart-tools": [
        {
            "title": "Zapier vs. Make: Choosing the Right Automation Platform",
            "excerpt": "A comprehensive comparison of the two leading no-code automation tools for your business.",
            "img": "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800&q=80"
        },
        {
            "title": "Automating Your Email Inbox: A Guide to Zero Unread",
            "excerpt": "Strategies and tools to automatically sort, label, and respond to emails.",
            "img": "https://images.unsplash.com/photo-1557200134-90327ee9fafa?w=800&q=80"
        },
        {
            "title": "Smart Home Automation for Productivity",
            "excerpt": "Using IoT devices to create an environment that fosters focus and efficiency.",
            "img": "https://images.unsplash.com/photo-1558002038-1091a1661116?w=800&q=80"
        }
    ],
    "programming-and-development": [
        {
            "title": "Why TypeScript is Winning the Web",
            "excerpt": "Exploring the benefits of static typing and why major frameworks are adopting TypeScript.",
            "img": "https://images.unsplash.com/photo-1629904853716-64f48d8e1ef1?w=800&q=80"
        },
        {
            "title": "The Rise of Rust: Performance Meets Safety",
            "excerpt": "Why developers love Rust and where it fits in the modern development stack.",
            "img": "https://images.unsplash.com/photo-1610986603166-f78428626276?w=800&q=80"
        },
        {
            "title": "Clean Code Principles for 2024",
            "excerpt": "Timeless practices for writing readable, maintainable, and scalable software.",
            "img": "https://images.unsplash.com/photo-1542831371-29b0f74f9713?w=800&q=80"
        }
    ],
    "cybersecurity-basics": [
        {
            "title": "Password Managers: Your First Line of Defense",
            "excerpt": "Why you need a password manager and how to set one up securely.",
            "img": "https://images.unsplash.com/photo-1614064641938-3bbee52942c7?w=800&q=80"
        },
        {
            "title": "Recognizing Phishing: Anatomy of a Scam",
            "excerpt": "How to spot sophisticated email scams and protect your personal data.",
            "img": "https://images.unsplash.com/photo-1563986768609-322da13575f3?w=800&q=80"
        },
        {
            "title": "Two-Factor Authentication (2FA) Explained",
            "excerpt": "Why passwords aren't enough and which 2FA methods are the most secure.",
            "img": "https://images.unsplash.com/photo-1550751827-4bd377958b?w=800&q=80"
        }
    ],

    # --- Business & Finance ---
    "entrepreneurship-and-startups": [
        {
            "title": "Validation First: Don't Build Until You Sell",
            "excerpt": "How to test your startup idea with minimal MVP before writing a line of code.",
            "img": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800&q=80"
        },
        {
            "title": "Bootstrapping vs. Venture Capital: The Honest Truth",
            "excerpt": "Weighing the pros and cons of self-funding versus seeking investor money.",
            "img": "https://images.unsplash.com/photo-1553729459-efe149f505d?w=800&q=80"
        },
        {
            "title": "The Lean Startup Method in Practice",
            "excerpt": "Applying Eric Ries's principles to build a sustainable business efficiently.",
            "img": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800&q=80"
        }
    ],
    "personal-finance-and-investing": [
        {
            "title": "The 50/30/20 Rule: Budgeting Made Simple",
            "excerpt": "A straightforward framework for managing your needs, wants, and savings.",
            "img": "https://images.unsplash.com/photo-1554224155-6726f3ff858f?w=800&q=80"
        },
        {
            "title": "Index Funds vs. Individual Stocks",
            "excerpt": "Why passive investing often beats active trading for long-term wealth building.",
            "img": "https://images.unsplash.com/photo-1590283603385-17ff93a7f29f?w=800&q=80"
        },
        {
            "title": "Understanding Compound Interest: The 8th Wonder",
            "excerpt": "How starting early can exponentially increase your retirement savings.",
            "img": "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=800&q=80"
        }
    ],
    "creator-economy-and-monetization": [
        {
            "title": "1,000 True Fans: The Blueprint for Creators",
            "excerpt": "Why you don't need millions of followers to make a living online.",
            "img": "https://images.unsplash.com/photo-1552664730-d307ca884978?w=800&q=80"
        },
        {
            "title": "Monetizing Your Newsletter: Substack and Beyond",
            "excerpt": "How writers are turning their email lists into sustainable businesses.",
            "img": "https://images.unsplash.com/photo-1563986768427-4a572a5a5462?w=800&q=80"
        },
        {
            "title": "The Economics of YouTube Revenue",
            "excerpt": "Understanding AdSense, sponsorships, and merchandise for video creators.",
            "img": "https://images.unsplash.com/photo-1611162617474-5b211626113?w=800&q=80"
        }
    ],
    "online-business-strategies": [
        {
            "title": "SEO in 2024: Content Clusters and E-E-A-T",
            "excerpt": "How to rank on Google by demonstrating Experience, Expertise, Authoritativeness, and Trust.",
            "img": "https://images.unsplash.com/photo-1432888498266-38ffec3eaf0a?w=800&q=80"
        },
        {
            "title": "Building a Sales Funnel that Converts",
            "excerpt": "Mapping the customer journey from awareness to purchase.",
            "img": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=800&q=80"
        },
        {
            "title": "Dropshipping vs. Print on Demand",
            "excerpt": "Comparing two popular low-risk e-commerce business models.",
            "img": "https://images.unsplash.com/photo-1523474253046-8cd2748b5fd2?w=800&q=80"
        }
    ],
    "passive-income": [
        {
            "title": "Dividend Investing for Beginners",
            "excerpt": "Building a portfolio that pays you regular cash flow.",
            "img": "https://images.unsplash.com/photo-1611974765270-ca12586343bb?w=800&q=80"
        },
        {
            "title": "Creating and Selling Digital Products",
            "excerpt": "How to turn your knowledge into ebooks, courses, and templates.",
            "img": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800&q=80"
        },
        {
            "title": "Affiliate Marketing: Authentic Recommendations",
            "excerpt": "Earning commissions by recommending products you actually use and love.",
            "img": "https://images.unsplash.com/photo-1595675024853-0f3ec9098ac7?w=800&q=80"
        }
    ],

    # --- Career & Growth ---
    "career-development-and-skills": [
        {
            "title": "Negotiating Your Salary: A Developer's Guide",
            "excerpt": "Scripts and strategies to get paid what you're worth.",
            "img": "https://images.unsplash.com/photo-1573497019940-1c28c88b4f3e?w=800&q=80"
        },
        {
            "title": "Soft Skills for Hard Tech Roles",
            "excerpt": "Why communication, empathy, and leadership matter more than code.",
            "img": "https://images.unsplash.com/photo-1517048676732-d65bc937f952?w=800&q=80"
        },
        {
            "title": "Navigating a Mid-Career Pivot",
            "excerpt": "How to transfer your skills to a completely new industry.",
            "img": "https://images.unsplash.com/photo-1454165833767-151c4a92c31e?w=800&q=80"
        }
    ],
    "online-learning-platforms": [
        {
            "title": "Coursera vs. Udemy vs. edX",
            "excerpt": "A detailed comparison of the top massive open online course providers.",
            "img": "https://images.unsplash.com/photo-1501504905252-473c47e087f8?w=800&q=80"
        },
        {
            "title": "The Art of Self-Directed Learning",
            "excerpt": "How to build your own curriculum and stick to it without a classroom.",
            "img": "https://images.unsplash.com/photo-1434030216411-0b793f4b4173?w=800&q=80"
        },
        {
            "title": "Certifications That Actually Matter",
            "excerpt": "Which tech certifications impress recruiters and which are a waste of time.",
            "img": "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?w=800&q=80"
        }
    ],
    "productivity-hacks-and-tools": [
        {
            "title": "Deep Work in a Distracted World",
            "excerpt": "Applying Cal Newport's principles to achieve peak cognitive performance.",
            "img": "https://images.unsplash.com/photo-1497032628192-86f99bcd76bc?w=800&q=80"
        },
        {
            "title": "The Pomodoro Technique Revisited",
            "excerpt": "Using time-blocking to prevent burnout and maintain focus.",
            "img": "https://images.unsplash.com/photo-1495914747574-050c93273658?w=800&q=80"
        },
        {
            "title": "Building a Second Brain with Notion",
            "excerpt": "How to organize your digital life, notes, and projects in one place.",
            "img": "https://images.unsplash.com/photo-1484480974693-6ca0a78fb36b?w=800&q=80"
        }
    ],
    "remote-work-and-digital-nomad": [
        {
            "title": "Top Digital Nomad Destinations for 2025",
            "excerpt": "Cities with the best wifi, community, and cost of living for remote workers.",
            "img": "https://images.unsplash.com/photo-1523906834658-6e24ef2386f9?w=800&q=80"
        },
        {
            "title": "Async Work: The Future of Remote Teams",
            "excerpt": "Why asynchronous communication beats constant meetings for distributed teams.",
            "img": "https://images.unsplash.com/photo-1593642632823-8f78536788c6?w=800&q=80"
        },
        {
            "title": "Setting Up an Ergonomic Home Office",
            "excerpt": "Protecting your health with the right chair, desk, and monitor setup.",
            "img": "https://images.unsplash.com/photo-1497215728101-856f4ea449174?w=800&q=80"
        }
    ],
    "personal-branding": [
        {
            "title": "Optimizing Your LinkedIn Profile",
            "excerpt": "Turning your profile from a static resume into a lead-generating landing page.",
            "img": "https://images.unsplash.com/photo-1611926653458-39295b41c9b5?w=800&q=80"
        },
        {
            "title": "Why You Should Start a Professional Blog",
            "excerpt": "How writing online establishes authority and attracts career opportunities.",
            "img": "https://images.unsplash.com/photo-1455390582262-054a68d771df?w=800&q=80"
        },
        {
            "title": "Networking for Introverts",
            "excerpt": "Building meaningful professional connections without the awkward small talk.",
            "img": "https://images.unsplash.com/photo-1515169067750-d51a73b0512c?w=800&q=80"
        }
    ],

    # --- Wellness & Living ---
    "mental-health-and-psychology": [
        {
            "title": "Imposter Syndrome in Tech",
            "excerpt": "Recognizing and overcoming feelings of inadequacy in high-performance environments.",
            "img": "https://images.unsplash.com/photo-1493839523149-2864fca44919?w=800&q=80"
        },
        {
            "title": "Cognitive Biases That Affect Decision Making",
            "excerpt": "How to spot mental shortcuts that lead to poor choices.",
            "img": "https://images.unsplash.com/photo-1506126613408-eca07ce68773?w=800&q=80"
        },
        {
            "title": "The Science of Burnout",
            "excerpt": "Understanding the physiological signs of burnout and how to reverse them.",
            "img": "https://images.unsplash.com/photo-1474418397713-7ede21d49118?w=800&q=80"
        }
    ],
    "personal-growth-and-self-improvement": [
        {
            "title": "Atomic Habits: Making Small Changes Stick",
            "excerpt": "Implementing James Clear's framework for building good habits and breaking bad ones.",
            "img": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=800&q=80"
        },
        {
            "title": "Journaling for Mental Clarity",
            "excerpt": "Different journaling techniques to process emotions and solve problems.",
            "img": "https://images.unsplash.com/photo-1517842645767-c639042777db?w=800&q=80"
        },
        {
            "title": "Growth Mindset vs. Fixed Mindset",
            "excerpt": "How your beliefs about intelligence determine your success.",
            "img": "https://images.unsplash.com/photo-1494178270175-e96de2971df9?w=800&q=80"
        }
    ],
    "minimalism-and-intentional-living": [
        {
            "title": "Digital Minimalism: Reclaiming Your Attention",
            "excerpt": "Strategies to reduce screen time and improve focus in a distracted world.",
            "img": "https://images.unsplash.com/photo-1494438639946-1ebd1d10bf85?w=800&q=80"
        },
        {
            "title": "The KonMari Method for Your Digital Files",
            "excerpt": "Organizing your computer and cloud storage for peace of mind.",
            "img": "https://images.unsplash.com/photo-1505691938895-1758d7eaa511?w=800&q=80"
        },
        {
            "title": "Essentialism: The Disciplined Pursuit of Less",
            "excerpt": "How to say no to the trivial many so you can focus on the vital few.",
            "img": "https://images.unsplash.com/photo-1462002271871-36ba957d607e?w=800&q=80"
        }
    ],
    "wellness-and-work-life-balance": [
        {
            "title": "Sleep Hygiene for High Performers",
            "excerpt": "Why sleep is your most important productivity tool and how to get more of it.",
            "img": "https://images.unsplash.com/photo-1511296933631-18b5f07a8bb8?w=800&q=80"
        },
        {
            "title": "The Benefits of Meditation for Developers",
            "excerpt": "How mindfulness practice improves code quality and reduces stress.",
            "img": "https://images.unsplash.com/photo-1445510491599-c391e8046a68?w=800&q=80"
        },
        {
            "title": "Setting Boundaries in an Always-On Culture",
            "excerpt": "How to disconnect from work without losing your edge.",
            "img": "https://images.unsplash.com/photo-1499750310107-5fef28a66643?w=800&q=80"
        }
    ],
    "sustainable-living": [
        {
            "title": "Zero Waste: A Beginner's Guide",
            "excerpt": "Practical steps to reduce your household waste and environmental footprint.",
            "img": "https://images.unsplash.com/photo-1532629545422-7515f3d16bb8?w=800&q=80"
        },
        {
            "title": "Ethical Fashion: Building a Sustainable Wardrobe",
            "excerpt": "How to choose quality over quantity and support fair labor practices.",
            "img": "https://images.unsplash.com/photo-1483985988355-78377a5a54b?w=800&q=80"
        },
        {
            "title": "Reducing Your Carbon Footprint at Home",
            "excerpt": "Energy-saving tips that are good for the planet and your wallet.",
            "img": "https://images.unsplash.com/photo-1542601906990-b4d3fb778b09?w=800&q=80"
        }
    ]
}

def generate_content(title, excerpt, slug):
    """
    Generates tailored content based on the category slug.
    Only includes code blocks for technical categories.
    """
    
    # Determine category type for tailored sections
    is_tech = any(x in slug for x in ['programming', 'automation', 'artificial-intelligence', 'blockchain', 'cybersecurity'])
    is_finance = any(x in slug for x in ['finance', 'investing', 'money', 'business', 'startup', 'passive-income', 'crypto'])
    is_wellness = any(x in slug for x in ['wellness', 'health', 'mindset', 'minimalism', 'living', 'growth'])
    
    # Intro
    content = f"# {title}\n\n"
    content += f"**{excerpt}**\n\n"
    content += "## The Current Landscape\n\n"
    
    if is_tech:
        content += "In the rapidly evolving world of technology, staying ahead of the curve is not just an advantage—it's a necessity. "
        content += f"Recent developments in **{title.split(':')[0]}** have fundamentally shifted how developers and engineers approach their work. "
        content += "Industry leaders are seeing a massive transition towards more efficient, scalable, and secure systems.\n\n"
    elif is_finance:
        content += "The economic environment is shifting, and traditional strategies are being challenged by new market dynamics. "
        content += f"Whether you are building a startup or managing a personal portfolio, understanding **{title.split(':')[0]}** is critical for long-term financial health. "
        content += "Experts suggest that adaptability is the single most important factor in today's market.\n\n"
    elif is_wellness:
        content += "In our fast-paced, always-on culture, finding balance has never been more challenging or more important. "
        content += f"The concept of **{title.split(':')[0]}** offers a refreshing perspective on how we can reclaim our time and mental energy. "
        content += "Research increasingly shows that sustainable habits beat radical transformations every time.\n\n"
    else:
        content += f"Understanding **{title}** is becoming increasingly important in today's context. "
        content += "This guide explores the fundamental concepts and practical applications you need to know.\n\n"

    # Core Content
    content += "## Key Insights & Strategies\n\n"
    content += "To truly master this subject, we need to look beyond the surface level. Here are the core pillars that define success in this area:\n\n"
    
    content += "### 1. The Foundation\n"
    content += "Success starts with a strong understanding of the basics. "
    if is_tech:
        content += "Before optimizing for performance, ensure your architecture is sound and your code is clean.\n\n"
    elif is_finance:
        content += "Before seeking high returns, ensure your risk management strategy and emergency funds are in place.\n\n"
    else:
        content += "Focus on the fundamental principles before attempting advanced techniques.\n\n"

    content += "### 2. Strategic Implementation\n"
    content += "Theory is useless without action. "
    if is_finance:
        content += "The best investors don't just read charts; they execute disciplined strategies regardless of market emotion.\n\n"
    elif is_wellness:
        content += "Reading about mindfulness won't reduce stress—practicing it daily will. Consistency is the secret sauce.\n\n"
    else:
        content += "It's about applying what you learn in real-world scenarios to see tangible results.\n\n"

    # Conditional Code Block (ONLY for Tech)
    if is_tech:
        content += "## Technical Implementation\n\n"
        content += "Here is a practical example of how this concept might look in code:\n\n"
        content += "```javascript\n"
        content += "// efficient implementation pattern\n"
        content += "const optimizeWorkflow = async (data) => {\n"
        content += "  try {\n"
        content += "    const result = await processData(data);\n"
        content += "    return { success: true, payload: result };\n"
        content += "  } catch (error) {\n"
        content += "    console.error('Optimization failed:', error);\n"
        content += "    return { success: false, error };\n"
        content += "  }\n"
        content += "};\n"
        content += "```\n\n"

    # Conclusion
    content += "## Looking Ahead\n\n"
    content += "As we move forward, the importance of this topic will likely grow. "
    content += "The key takeaway is to remain curious and adaptable. "
    
    if is_tech:
        content += "Technology waits for no one. Keep building, keep learning, and stay updated with the latest documentation.\n\n"
    elif is_finance:
        content += "The market rewards patience and discipline. Review your strategy regularly, but don't react to every headline.\n\n"
    elif is_wellness:
        content += "Your well-being is a marathon, not a sprint. Small, intentional changes today will yield massive dividends in your future quality of life.\n\n"
    else:
        content += "Take these insights and apply them to your daily life for immediate impact.\n\n"

    return content

async def seed_full_posts():
    """Create sample posts for all 24 subcategories"""
    
    async for session in get_db_session():
        print("🚀 Starting full database seed...")
        
        # Get the specific user 'Wetende'
        stmt = select(User).where(User.username == "Wetende")
        result = await session.execute(stmt)
        wetende = result.scalar_one_or_none()
        
        if not wetende:
            print("❌ User 'Wetende' not found! Please ensure the user exists in the database.")
            return

        print(f"👤 Author assigned: {wetende.full_name} (@{wetende.username})")
        posts_created = 0
        
        # Iterate through the data dictionary
        for slug, posts in POSTS_DATA.items():
            # Find the category by slug
            stmt = select(Category).where(Category.slug == slug)
            result = await session.execute(stmt)
            category = result.scalar_one_or_none()
            
            if not category:
                print(f"⚠️ Category not found for slug: {slug}. Skipping...")
                continue
            
            print(f"📂 Processing category: {category.name} ({slug})")
            
            for i, post_info in enumerate(posts):
                title = post_info["title"]
                post_slug = generate_slug(title)
                
                # Check if post exists
                stmt = select(Post).where(Post.slug == post_slug)
                result = await session.execute(stmt)
                if result.scalar_one_or_none():
                    print(f"  ⏭️ Post '{title}' already exists, skipping...")
                    continue
                
                # Randomize data
                published_date = datetime.utcnow() - timedelta(days=random.randint(1, 60))
                view_count = random.randint(100, 5000)
                reading_time = random.randint(3, 12)
                
                # Generate specific content
                post_content = generate_content(title, post_info["excerpt"], slug)

                # Create post
                post = Post(
                    title=title,
                    slug=post_slug,
                    content=post_content,
                    excerpt=post_info["excerpt"],
                    featured_image=post_info["img"],
                    author_id=wetende.id,
                    category_id=category.id,
                    is_published=True,
                    is_featured=(i == 0),  # First post in category is featured
                    reading_time=reading_time,
                    published_at=published_date,
                    view_count=view_count,
                    meta_title=f"{title} | CraftyXHub",
                    meta_description=post_info["excerpt"]
                )
                
                session.add(post)
                posts_created += 1
                print(f"  ✅ Created: {title}")
        
        await session.commit()
        print(f"\n🎉 SUCCESS: Created {posts_created} new posts assigned to {wetende.full_name}!")

if __name__ == "__main__":
    asyncio.run(seed_full_posts())
