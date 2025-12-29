"""
Seed script for demo users and subcategories
Run: python seed_demo.py
"""
import asyncio
from sqlalchemy import select
from database.connection import get_db_session
from models.user import User, Profile, UserRole
from models.post import Category
from services.user.auth import AuthService


async def create_demo_users():
    """Create demo users: user, admin, moderator"""
    demo_users = [
        {
            "email": "demo@user.com",
            "username": "demouser",
            "full_name": "Demo User",
            "password": "demo1234",
            "role": UserRole.USER,
            "is_verified": True,
            "profile": {
                "bio": "Demo user account for testing purposes.",
                "location": "Demo City",
            }
        },
        {
            "email": "demo@admin.com",
            "username": "demoadmin",
            "full_name": "Demo Admin",
            "password": "demo1234",
            "role": UserRole.ADMIN,
            "is_verified": True,
            "profile": {
                "bio": "Demo admin account for testing purposes.",
                "location": "Admin City",
            }
        },
        {
            "email": "demo@moderator.com",
            "username": "demomoderator",
            "full_name": "Demo Moderator",
            "password": "demo1234",
            "role": UserRole.MODERATOR,
            "is_verified": True,
            "profile": {
                "bio": "Demo moderator account for testing purposes.",
                "location": "Moderator City",
            }
        }
    ]
    
    created_users = []
    
    async for session in get_db_session():
        for user_data in demo_users:
            # Check if user exists
            existing_user = await AuthService.get_user_by_email(session, user_data["email"])
            if existing_user:
                print(f"User {user_data['email']} already exists, skipping...")
                created_users.append(existing_user)
                continue
            
            # Create user
            hashed_password = AuthService.get_password_hash(user_data["password"])
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                password=hashed_password,
                role=user_data["role"],
                is_verified=user_data["is_verified"],
                is_active=True
            )
            
            session.add(user)
            await session.flush()
            
            # Create profile
            profile = Profile(
                user_id=user.id,
                bio=user_data["profile"]["bio"],
                location=user_data["profile"]["location"],
            )
            
            session.add(profile)
            created_users.append(user)
            print(f"Created demo user: {user.full_name} ({user.role.value}) - {user.email}")
        
        await session.commit()
    
    return created_users


async def create_subcategories():
    """Create subcategories for existing categories"""
    
    subcategories_map = {
        "technology": [
            {"name": "Blockchain", "slug": "blockchain", "description": "Blockchain technology, crypto, and Web3"},
            {"name": "AI & Machine Learning", "slug": "ai-machine-learning", "description": "Artificial Intelligence and Machine Learning articles"},
            {"name": "Cloud Computing", "slug": "cloud-computing", "description": "AWS, Azure, GCP and cloud infrastructure"},
            {"name": "Cybersecurity", "slug": "cybersecurity", "description": "Security best practices and threat prevention"},
        ],
        "web-development": [
            {"name": "Frontend", "slug": "frontend", "description": "React, Vue, Angular and frontend development"},
            {"name": "Backend", "slug": "backend", "description": "Node.js, Python, Go backend development"},
            {"name": "Full Stack", "slug": "full-stack", "description": "End-to-end web development"},
            {"name": "APIs", "slug": "apis", "description": "REST, GraphQL, and API design"},
        ],
        "design": [
            {"name": "UI/UX", "slug": "ui-ux", "description": "User interface and user experience design"},
            {"name": "Graphic Design", "slug": "graphic-design", "description": "Visual design and branding"},
            {"name": "Motion Design", "slug": "motion-design", "description": "Animation and motion graphics"},
        ],
        "tutorials": [
            {"name": "Beginner", "slug": "beginner-tutorials", "description": "Tutorials for beginners"},
            {"name": "Intermediate", "slug": "intermediate-tutorials", "description": "Mid-level skill tutorials"},
            {"name": "Advanced", "slug": "advanced-tutorials", "description": "Advanced and expert-level tutorials"},
        ],
        "career": [
            {"name": "Job Search", "slug": "job-search", "description": "Finding jobs and interview prep"},
            {"name": "Freelancing", "slug": "freelancing", "description": "Freelance and remote work tips"},
            {"name": "Leadership", "slug": "leadership", "description": "Management and leadership skills"},
        ]
    }
    
    created_subcategories = []
    
    async for session in get_db_session():
        for parent_slug, subcats in subcategories_map.items():
            # Find parent category
            stmt = select(Category).where(Category.slug == parent_slug)
            result = await session.execute(stmt)
            parent = result.scalar_one_or_none()
            
            if not parent:
                print(f"Parent category '{parent_slug}' not found, skipping subcategories...")
                continue
            
            for subcat_data in subcats:
                # Check if subcategory exists
                stmt = select(Category).where(Category.slug == subcat_data["slug"])
                result = await session.execute(stmt)
                existing = result.scalar_one_or_none()
                
                if existing:
                    print(f"Subcategory '{subcat_data['name']}' already exists, skipping...")
                    created_subcategories.append(existing)
                    continue
                
                # Create subcategory
                subcat = Category(
                    name=subcat_data["name"],
                    slug=subcat_data["slug"],
                    description=subcat_data["description"],
                    parent_id=parent.id
                )
                
                session.add(subcat)
                created_subcategories.append(subcat)
                print(f"Created subcategory: {parent.name} → {subcat.name}")
        
        await session.commit()
    
    return created_subcategories


async def main():
    print("=" * 50)
    print("Seeding Demo Users and Subcategories")
    print("=" * 50)
    
    print("\n--- Creating Demo Users ---")
    await create_demo_users()
    
    print("\n--- Creating Subcategories ---")
    await create_subcategories()
    
    print("\n" + "=" * 50)
    print("Demo seeding complete!")
    print("=" * 50)
    print("\nDemo Users Created:")
    print("  - demo@user.com / demo1234 (User)")
    print("  - demo@admin.com / demo1234 (Admin)")
    print("  - demo@moderator.com / demo1234 (Moderator)")


if __name__ == "__main__":
    asyncio.run(main())
