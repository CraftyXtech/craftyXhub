"""
Seed posts for each category and subcategory
Run: python seed_posts.py
"""
import asyncio
from datetime import datetime, timedelta
import random
from sqlalchemy import select
from database.connection import get_db_session
from models.user import User
from models.post import Post, Category
from utils.slug_generator import generate_slug


# Sample post templates per category
POSTS_DATA = {
    "blockchain": [
        {"title": "Introduction to Blockchain Technology", "excerpt": "Understanding the fundamentals of blockchain and distributed ledger technology."},
        {"title": "Smart Contracts Explained: A Beginner's Guide", "excerpt": "Learn how smart contracts work and why they're revolutionizing digital agreements."},
        {"title": "Web3 Development: Getting Started", "excerpt": "Your first steps into building decentralized applications on the blockchain."},
    ],
    "ai-machine-learning": [
        {"title": "Machine Learning Fundamentals for Beginners", "excerpt": "A comprehensive introduction to machine learning concepts and algorithms."},
        {"title": "Building Your First Neural Network", "excerpt": "Step-by-step guide to creating a neural network from scratch using Python."},
        {"title": "AI in 2024: Trends and Predictions", "excerpt": "Exploring the latest trends in artificial intelligence and what's coming next."},
    ],
    "cloud-computing": [
        {"title": "AWS vs Azure vs GCP: A Comparison", "excerpt": "Comparing the top three cloud platforms to help you choose the right one."},
        {"title": "Serverless Architecture Best Practices", "excerpt": "How to build scalable applications using serverless computing."},
    ],
    "cybersecurity": [
        {"title": "Cybersecurity Basics Every Developer Should Know", "excerpt": "Essential security practices for writing secure code."},
        {"title": "Protecting Your Application from Common Vulnerabilities", "excerpt": "Understanding OWASP Top 10 and how to prevent security breaches."},
    ],
    "frontend": [
        {"title": "Modern React Patterns and Best Practices", "excerpt": "Advanced React patterns for building maintainable applications."},
        {"title": "CSS Grid vs Flexbox: When to Use Each", "excerpt": "A practical guide to choosing between CSS Grid and Flexbox."},
        {"title": "State Management in 2024: Redux vs Zustand vs Jotai", "excerpt": "Comparing modern state management solutions for React applications."},
    ],
    "backend": [
        {"title": "Building RESTful APIs with Node.js", "excerpt": "Complete guide to creating robust REST APIs using Express.js."},
        {"title": "Python FastAPI: Modern Backend Development", "excerpt": "Why FastAPI is becoming the go-to framework for Python backends."},
        {"title": "Database Design Best Practices", "excerpt": "How to design scalable and efficient database schemas."},
    ],
    "full-stack": [
        {"title": "Full Stack Development Roadmap 2024", "excerpt": "The complete path to becoming a full-stack developer."},
        {"title": "Building a MERN Stack Application", "excerpt": "Step-by-step tutorial for MongoDB, Express, React, and Node.js."},
    ],
    "apis": [
        {"title": "GraphQL vs REST: Choosing the Right API", "excerpt": "Understanding when to use GraphQL and when REST is better."},
        {"title": "API Design Principles for Developers", "excerpt": "Best practices for designing clean and intuitive APIs."},
    ],
    "ui-ux": [
        {"title": "User Research Methods Every Designer Should Know", "excerpt": "Essential techniques for understanding your users better."},
        {"title": "Creating Accessible Web Experiences", "excerpt": "How to design interfaces that work for everyone."},
        {"title": "Design Systems: Building Consistent UIs", "excerpt": "A guide to creating and maintaining design systems."},
    ],
    "graphic-design": [
        {"title": "Color Theory for Digital Designers", "excerpt": "Understanding color psychology and creating effective palettes."},
        {"title": "Typography Best Practices for Web", "excerpt": "How to choose and pair fonts for better readability."},
    ],
    "motion-design": [
        {"title": "Micro-interactions That Delight Users", "excerpt": "Small animations that make big differences in user experience."},
        {"title": "CSS Animations vs JavaScript Animations", "excerpt": "When to use CSS and when to reach for JavaScript."},
    ],
    "beginner-tutorials": [
        {"title": "Your First HTML Page: A Complete Guide", "excerpt": "Start your web development journey with this beginner tutorial."},
        {"title": "Git for Beginners: Version Control Basics", "excerpt": "Understanding Git and GitHub for your first projects."},
        {"title": "JavaScript Basics: Variables, Functions, and Loops", "excerpt": "The fundamental building blocks of JavaScript programming."},
    ],
    "intermediate-tutorials": [
        {"title": "Building a Todo App with React", "excerpt": "A classic project to solidify your React knowledge."},
        {"title": "Working with APIs in JavaScript", "excerpt": "How to fetch data and handle responses in your applications."},
    ],
    "advanced-tutorials": [
        {"title": "Implementing Authentication from Scratch", "excerpt": "Building secure auth systems with JWT and refresh tokens."},
        {"title": "Performance Optimization Techniques", "excerpt": "Advanced strategies for making your applications faster."},
    ],
    "job-search": [
        {"title": "Crafting the Perfect Developer Resume", "excerpt": "Tips for making your resume stand out to recruiters."},
        {"title": "Technical Interview Preparation Guide", "excerpt": "How to prepare for coding interviews at top companies."},
    ],
    "freelancing": [
        {"title": "Starting Your Freelance Development Career", "excerpt": "Everything you need to know about going freelance."},
        {"title": "Pricing Your Services as a Freelancer", "excerpt": "How to set rates that value your skills appropriately."},
    ],
    "leadership": [
        {"title": "Transitioning from Developer to Tech Lead", "excerpt": "Skills you need when moving into leadership roles."},
        {"title": "Building and Managing Engineering Teams", "excerpt": "Best practices for leading technical teams effectively."},
    ],
}

# Generic content template
def generate_content(title, excerpt):
    return f"""# {title}

{excerpt}

## Introduction

This article covers everything you need to know about this topic. Whether you're a beginner or an experienced developer, you'll find valuable insights here.

## Key Concepts

Understanding the fundamentals is crucial for success. Let's break down the main concepts:

### Concept 1: Getting Started

Before diving deep, make sure you have the prerequisites in place. This includes having a solid understanding of the basics and setting up your development environment properly.

### Concept 2: Best Practices

Following industry best practices ensures your work is maintainable and scalable:

- Write clean, readable code
- Document your work properly
- Test thoroughly before deploying
- Keep learning and improving

### Concept 3: Advanced Techniques

Once you've mastered the basics, explore advanced techniques:

1. Optimization strategies
2. Performance improvements
3. Scalability considerations
4. Security best practices

## Practical Example

Here's a simple example to illustrate the concepts:

```javascript
// Example code
const example = () => {{
  console.log('Hello from {title}');
  return 'Success!';
}};
```

## Conclusion

We've covered the essential aspects of this topic. Remember that practice is key to mastering any skill. Start with small projects and gradually take on more complex challenges.

## Further Reading

- Check out our related tutorials
- Join the community discussions
- Explore more advanced topics in this series
"""


async def seed_posts():
    """Create sample posts for each subcategory"""
    
    async for session in get_db_session():
        # Get all subcategories (categories with parent_id)
        stmt = select(Category).where(Category.parent_id.isnot(None))
        result = await session.execute(stmt)
        subcategories = result.scalars().all()
        
        # Get demo users for authors
        stmt = select(User).where(User.email.in_([
            "demo@user.com", 
            "demo@admin.com", 
            "demo@moderator.com"
        ]))
        result = await session.execute(stmt)
        authors = result.scalars().all()
        
        if not authors:
            print("No demo users found. Run seed_demo.py first!")
            return
        
        posts_created = 0
        
        for subcat in subcategories:
            posts_data = POSTS_DATA.get(subcat.slug, [])
            
            for i, post_info in enumerate(posts_data):
                title = post_info["title"]
                slug = generate_slug(title)
                
                # Check if post exists
                stmt = select(Post).where(Post.slug == slug)
                result = await session.execute(stmt)
                if result.scalar_one_or_none():
                    print(f"Post '{title}' already exists, skipping...")
                    continue
                
                # Create post
                author = random.choice(authors)
                published_date = datetime.utcnow() - timedelta(days=random.randint(1, 30))
                
                post = Post(
                    title=title,
                    slug=slug,
                    content=generate_content(title, post_info["excerpt"]),
                    excerpt=post_info["excerpt"],
                    author_id=author.id,
                    category_id=subcat.id,
                    is_published=True,
                    is_featured=(i == 0),  # First post in each category is featured
                    reading_time=random.randint(5, 15),
                    published_at=published_date,
                    view_count=random.randint(50, 500)
                )
                
                session.add(post)
                posts_created += 1
                print(f"Created: [{subcat.name}] {title}")
        
        await session.commit()
        print(f"\nCreated {posts_created} new posts!")


async def main():
    print("=" * 50)
    print("Seeding Posts for Categories")
    print("=" * 50)
    await seed_posts()
    print("=" * 50)
    print("Done!")


if __name__ == "__main__":
    asyncio.run(main())
