"""rename taxonomy subcategories phase 1

Revision ID: f1c9e7a4b2d0
Revises: 7d6b8e4c2f10
Create Date: 2026-04-06 18:40:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f1c9e7a4b2d0"
down_revision = "7d6b8e4c2f10"
branch_labels = None
depends_on = None


categories = sa.table(
    "categories",
    sa.column("id", sa.Integer()),
    sa.column("name", sa.String(length=100)),
)

tags = sa.table(
    "tags",
    sa.column("id", sa.Integer()),
    sa.column("category_id", sa.Integer()),
)


CATEGORY_RENAMES_UP = {
    46: "Blockchain & Crypto",
    47: "Automation",
    48: "Software Development",
    49: "Cybersecurity & Privacy",
    53: "Creator Business",
    54: "Online Business & Marketing",
    57: "Career Growth & Job Search",
    58: "Learning & Skill Building",
    59: "Productivity & Remote Work",
    60: "Freelancing",
    61: "Personal Brand & Audience",
    63: "Mental Health",
    64: "Personal Growth",
    65: "Intentional Living",
    66: "Work-Life Balance",
}


CATEGORY_RENAMES_DOWN = {
    46: "Blockchain & Cryptocurrencies",
    47: "Automation & Smart Tools",
    48: "Programming & Development",
    49: "Cybersecurity Basics",
    53: "Creator Economy & Monetization",
    54: "Online Business Strategies",
    57: "Career Development & Skills",
    58: "Online Learning Platforms",
    59: "Productivity Hacks & Tools",
    60: "Remote Work & Digital Nomad",
    61: "Personal Branding",
    63: "Mental Health & Psychology",
    64: "Personal Growth & Self-Improvement",
    65: "Minimalism & Intentional Living",
    66: "Wellness & Work-Life Balance",
}


TAG_CATEGORY_UPDATES_UP = {
    205: 59,  # Remote Work -> Productivity & Remote Work
    206: 59,  # Work From Home -> Productivity & Remote Work
    207: 59,  # Digital Nomad -> Productivity & Remote Work
    208: 59,  # Async Work -> Productivity & Remote Work
    209: 59,  # Home Office -> Productivity & Remote Work
    240: 60,  # Freelancing -> Freelancing
    241: 60,  # Upwork -> Freelancing
    242: 60,  # Fiverr -> Freelancing
    243: 60,  # Consulting -> Freelancing
    244: 60,  # Copywriting -> Freelancing
    245: 60,  # UX Design -> Freelancing
}


TAG_CATEGORY_UPDATES_DOWN = {
    205: 60,
    206: 60,
    207: 60,
    208: 60,
    209: 60,
    240: 57,
    241: 57,
    242: 57,
    243: 57,
    244: 57,
    245: 57,
}


def _apply_category_renames(rename_map: dict[int, str]) -> None:
    connection = op.get_bind()
    for category_id, new_name in rename_map.items():
        connection.execute(
            categories.update()
            .where(categories.c.id == category_id)
            .values(name=new_name)
        )


def _apply_tag_category_updates(update_map: dict[int, int]) -> None:
    connection = op.get_bind()
    for tag_id, category_id in update_map.items():
        connection.execute(
            tags.update()
            .where(tags.c.id == tag_id)
            .values(category_id=category_id)
        )


def upgrade() -> None:
    # Preserve existing category slugs and ids. Only rename the rows in place.
    _apply_category_renames(CATEGORY_RENAMES_UP)
    _apply_tag_category_updates(TAG_CATEGORY_UPDATES_UP)


def downgrade() -> None:
    _apply_tag_category_updates(TAG_CATEGORY_UPDATES_DOWN)
    _apply_category_renames(CATEGORY_RENAMES_DOWN)
