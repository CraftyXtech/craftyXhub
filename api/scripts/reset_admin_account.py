"""
Utility script to reset the primary admin account.

Behavior:
- Deletes any existing user with email admin@craftyxhub.com
- Creates a fresh SUPER_ADMIN with the same email and a known password.

Usage:
  cd api && source venv/bin/activate
  python scripts/reset_admin_account.py
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select

# Ensure project imports work when this script is executed directly.
sys.path.insert(0, "/home/wetende/Projects/craftyxhub/api")

from models.user import User, UserRole  # type: ignore
from core.config import settings  # type: ignore
from services.user.auth import AuthService  # type: ignore


ADMIN_EMAIL = "admin@craftyxhub.com"
ADMIN_PASSWORD = "admin@123"


async def reset_admin_account() -> None:
  """Delete existing admin@craftyxhub.com user(s) and seed a fresh SUPER_ADMIN."""

  engine = create_async_engine(settings.DATABASE_URL, echo=False)
  async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

  async with async_session() as session:
    # Delete any existing users with this email
    result = await session.execute(select(User).where(User.email == ADMIN_EMAIL))
    existing_users = result.scalars().all()

    if existing_users:
      print(f"Found {len(existing_users)} existing user(s) with email {ADMIN_EMAIL}. Deleting...")
      for user in existing_users:
        await session.delete(user)
      await session.commit()
      print("✅ Existing admin account(s) deleted (including related data via cascades).")
    else:
      print(f"No existing user found with email {ADMIN_EMAIL}. Seeding a fresh account...")

    # Create fresh SUPER_ADMIN user
    hashed_password = AuthService.get_password_hash(ADMIN_PASSWORD)

    new_user = User(
      email=ADMIN_EMAIL,
      username="admin",
      full_name="Super Admin",
      password=hashed_password,
      is_active=True,
      is_verified=True,
      role=UserRole.SUPER_ADMIN,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    print("\n✅ Seeded fresh SUPER_ADMIN account:")
    print(f"   Email     : {new_user.email}")
    print(f"   Username  : {new_user.username}")
    print(f"   Role      : {new_user.role.value}")
    print(f"   Active    : {new_user.is_active}")
    print(f"   Verified  : {new_user.is_verified}")
    print("\n🔐 Login credentials:")
    print(f"   Email    : {ADMIN_EMAIL}")
    print(f"   Password : {ADMIN_PASSWORD}")
    print("\n⚠️  IMPORTANT: Log out and log back in to ensure the new role is reflected in your JWT.")

  await engine.dispose()


if __name__ == "__main__":
  asyncio.run(reset_admin_account())



