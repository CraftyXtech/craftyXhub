"""
Dangerous utility script to wipe all user accounts and their content.

Behavior:
- Permanently deletes ALL rows from:
  - notifications, comments, reports
  - ai_generation_logs, ai_drafts
  - post_likes, post_bookmarks, user_follows
  - posts, profiles, media, user_role_changes
  - users
- Uses TRUNCATE ... CASCADE so that any dependent rows are also removed.

Intended usage:
- Run ONLY in development or a throwaway environment.
- After running this script, run `reset_admin_account.py` to seed a fresh
  SUPER_ADMIN account (admin@craftyxhub.com / admin@123).

Usage:
  cd api && source venv/bin/activate
  python scripts/wipe_user_data.py
"""

import asyncio
import sys

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Ensure project imports work when this script is executed directly.
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # points to the `api/` directory
sys.path.insert(0, str(PROJECT_ROOT))

from core.config import settings  # type: ignore


TARGET_TABLES = [
    "notifications",
    "comments",
    "reports",
    "ai_generation_logs",
    "ai_drafts",
    "post_likes",
    "post_bookmarks",
    "user_follows",
    "posts",
    "profiles",
    "media",
    "user_role_changes",
    "users",
]


async def wipe_user_data() -> None:
    """
    Truncate all user- and post-related tables.

    This is irreversible. Use only in development.
    """
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        print("DANGER: This will permanently delete ALL users and their content.")
        print("    Target tables (will skip any that do not exist):")
        for name in TARGET_TABLES:
            print(f"      - {name}")
        print()
        confirm = input("Type DELETE to continue (anything else to abort): ").strip()
        if confirm != "DELETE":
            print("Aborted. No data was removed.")
            await engine.dispose()
            return

        # Filter to only tables that actually exist in the current database.
        existing_tables: list[str] = []
        for name in TARGET_TABLES:
            # to_regclass returns NULL if the relation does not exist
            result = await session.execute(text("SELECT to_regclass(:name)"), {"name": name})
            if result.scalar():
                existing_tables.append(name)

        if not existing_tables:
            print("No matching tables found in this database. Nothing to truncate.")
            await engine.dispose()
            return

        table_list = ", ".join(existing_tables)
        sql = text(f"TRUNCATE TABLE {table_list} RESTART IDENTITY CASCADE;")

        print("\nTruncating tables:")
        for name in existing_tables:
            print(f"  - {name}")

        await session.execute(sql)
        await session.commit()
        print("All user data and related content has been wiped.")
        print("Next step: run `python scripts/reset_admin_account.py` to seed a fresh SUPER_ADMIN.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(wipe_user_data())


