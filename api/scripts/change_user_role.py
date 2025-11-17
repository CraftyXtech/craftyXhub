"""
Script to change user roles in the database.
Usage: python scripts/change_user_role.py <email> <role>
Example: python scripts/change_user_role.py user@example.com admin
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Add parent directory to path to import models
sys.path.insert(0, "/home/wetende/Projects/craftyxhub/api")

from models.user import User, UserRole
from core.config import settings


async def change_user_role(email: str, new_role: str):
    """Change a user's role in the database."""

    # Validate role
    valid_roles = {
        "super_admin": UserRole.SUPER_ADMIN,
        "admin": UserRole.ADMIN,
        "moderator": UserRole.MODERATOR,
        "user": UserRole.USER,
    }

    if new_role.lower() not in valid_roles:
        print(f"❌ Invalid role: {new_role}")
        print(f'   Valid roles: {", ".join(valid_roles.keys())}')
        return False

    role_enum = valid_roles[new_role.lower()]

    # Connect to database
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Find user by email
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user:
            print(f"❌ User not found: {email}")
            await engine.dispose()
            return False

        old_role = user.role.value if hasattr(user.role, "value") else user.role

        # Update role
        user.role = role_enum
        await session.commit()

        print(f"✅ Successfully updated user role")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Old Role: {old_role}")
        print(f"   New Role: {role_enum.value}")
        print(f"\n⚠️  User must log out and log back in for changes to take effect!")

    await engine.dispose()
    return True


async def list_all_users():
    """List all users and their current roles."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()

        if not users:
            print("No users found in database.")
            await engine.dispose()
            return

        print(f'\n{"Email":<30} {"Username":<20} {"Role":<15} {"Active":<10}')
        print("=" * 80)

        for user in users:
            role = user.role.value if hasattr(user.role, "value") else user.role
            active = "✅ Yes" if user.is_active else "❌ No"
            print(f"{user.email:<30} {user.username:<20} {role:<15} {active:<10}")

    await engine.dispose()


def print_usage():
    """Print usage instructions."""
    print("\n📋 User Role Management Script")
    print("=" * 50)
    print("\nUsage:")
    print("  python scripts/change_user_role.py <email> <role>")
    print("  python scripts/change_user_role.py list")
    print("\nExamples:")
    print("  python scripts/change_user_role.py user@example.com super_admin")
    print("  python scripts/change_user_role.py user@example.com admin")
    print("  python scripts/change_user_role.py user@example.com moderator")
    print("  python scripts/change_user_role.py user@example.com user")
    print("  python scripts/change_user_role.py list")
    print("\nValid Roles:")
    print("  - super_admin: Full system access, including management of admins")
    print("  - admin      : Full access to most administrative features")
    print("  - moderator  : Can moderate content, no user management")
    print("  - user       : Basic access to content creation")
    print()


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_usage()
        sys.exit(1)

    if sys.argv[1].lower() == "list":
        asyncio.run(list_all_users())
    elif len(sys.argv) == 3:
        email = sys.argv[1]
        role = sys.argv[2]
        success = asyncio.run(change_user_role(email, role))
        sys.exit(0 if success else 1)
    else:
        print("❌ Invalid arguments")
        print_usage()
        sys.exit(1)
