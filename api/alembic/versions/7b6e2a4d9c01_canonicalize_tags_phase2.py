"""canonicalize tags phase 2

Revision ID: 7b6e2a4d9c01
Revises: 4a8b2f6d9c10
Create Date: 2026-04-07 15:10:00.000000

"""

from alembic import op
import sqlalchemy as sa
import re
import unicodedata


# revision identifiers, used by Alembic.
revision = "7b6e2a4d9c01"
down_revision = "4a8b2f6d9c10"
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
    sa.column("name", sa.String(length=50)),
    sa.column("slug", sa.String(length=50)),
    sa.column("category_id", sa.Integer()),
    sa.column("is_active", sa.Boolean()),
    sa.column("canonical_tag_id", sa.Integer()),
)

tag_slug_history = sa.table(
    "tag_slug_history",
    sa.column("tag_id", sa.Integer()),
    sa.column("slug", sa.String(length=50)),
)

post_tags = sa.table(
    "post_tags",
    sa.column("post_id", sa.Integer()),
    sa.column("tag_id", sa.Integer()),
)


CANONICAL_TAG_DEFINITIONS = {
    "Artificial Intelligence": "Artificial Intelligence",
    "Large Language Models": "Artificial Intelligence",
    "AI Assistants": "Artificial Intelligence",
    "Remote Work": "Productivity & Remote Work",
    "Decentralized Finance": "Blockchain & Crypto",
    "Identity & Access Security": "Cybersecurity & Privacy",
    "Privacy Tools": "Cybersecurity & Privacy",
    "Frontend Development": "Software Development",
    "Backend Development": "Software Development",
    "Databases": "Software Development",
    "Cloud Infrastructure": "Software Development",
    "Containerization": "Software Development",
    "APIs": "Software Development",
    "Web Development": "Software Development",
    "DevOps": "Software Development",
    "Open Source": "Software Development",
    "SaaS": "Entrepreneurship & Startups",
}

TAG_MAPPINGS = {
    "AI": "Artificial Intelligence",
    "LLMs": "Large Language Models",
    "AI Tools": "AI Assistants",
    "ChatGPT": "AI Assistants",
    "Async Work": "Remote Work",
    "Home Office": "Remote Work",
    "DeFi": "Decentralized Finance",
    "Password Security": "Identity & Access Security",
    "2FA": "Identity & Access Security",
    "VPN": "Privacy Tools",
    "Python": "Backend Development",
    "JavaScript": "Frontend Development",
    "TypeScript": "Frontend Development",
    "React": "Frontend Development",
    "Node.js": "Backend Development",
    "Cloud Computing": "Cloud Infrastructure",
    "SQL": "Databases",
    "AWS": "Cloud Infrastructure",
    "Docker": "Containerization",
}

RETIRED_TAGS = {
    "Tech Trends",
    "Git",
}

DOWNGRADE_CATEGORY_REASSIGNMENTS = {
    "SaaS": "Software Development",
}


def _slugify(value: str, *, max_length: int = 50) -> str:
    slug = unicodedata.normalize("NFKD", value.strip().lower())
    slug = "".join(char for char in slug if not unicodedata.combining(char))
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = re.sub(r"-{2,}", "-", slug).strip("-")
    return slug[:max_length].strip("-")


def _fetch_category_id(connection, name: str):
    return connection.execute(
        sa.select(categories.c.id).where(categories.c.name == name)
    ).scalar_one_or_none()


def _fetch_tag(connection, name: str):
    return connection.execute(
        sa.select(
            tags.c.id,
            tags.c.name,
            tags.c.slug,
            tags.c.category_id,
            tags.c.is_active,
            tags.c.canonical_tag_id,
        ).where(tags.c.name == name)
    ).mappings().first()


def _ensure_tag_slug_history(connection, *, tag_id: int, slug: str | None) -> None:
    if not slug:
        return
    connection.execute(
        sa.text(
            """
            INSERT INTO tag_slug_history (tag_id, slug)
            SELECT :tag_id, :slug
            WHERE NOT EXISTS (
                SELECT 1
                FROM tag_slug_history
                WHERE tag_id = :tag_id
                  AND slug = :slug
            )
            """
        ),
        {"tag_id": tag_id, "slug": slug},
    )


def _ensure_canonical_tag(connection, tag_name: str) -> int | None:
    target_category_name = CANONICAL_TAG_DEFINITIONS.get(tag_name)
    if target_category_name is None:
        return None

    category_id = _fetch_category_id(connection, target_category_name)
    if category_id is None:
        return None

    existing = _fetch_tag(connection, tag_name)
    if existing is not None:
        connection.execute(
            tags.update()
            .where(tags.c.id == existing["id"])
            .values(
                category_id=category_id,
                is_active=True,
                canonical_tag_id=None,
            )
        )
        _ensure_tag_slug_history(
            connection,
            tag_id=existing["id"],
            slug=existing["slug"] or _slugify(tag_name),
        )
        return existing["id"]

    slug = _slugify(tag_name)
    result = connection.execute(
        tags.insert()
        .values(
            name=tag_name,
            slug=slug,
            category_id=category_id,
            is_active=True,
            canonical_tag_id=None,
        )
        .returning(tags.c.id)
    )
    tag_id = result.scalar_one()
    _ensure_tag_slug_history(connection, tag_id=tag_id, slug=slug)
    return tag_id


def _merge_tag(connection, old_tag_name: str, canonical_tag_name: str) -> None:
    old_tag = _fetch_tag(connection, old_tag_name)
    canonical_id = _ensure_canonical_tag(connection, canonical_tag_name)
    if old_tag is None or canonical_id is None or old_tag["id"] == canonical_id:
        return

    connection.execute(
        sa.text(
            """
            INSERT INTO post_tags (post_id, tag_id)
            SELECT pt.post_id, :canonical_tag_id
            FROM post_tags pt
            WHERE pt.tag_id = :old_tag_id
              AND NOT EXISTS (
                SELECT 1
                FROM post_tags existing
                WHERE existing.post_id = pt.post_id
                  AND existing.tag_id = :canonical_tag_id
              )
            """
        ),
        {"old_tag_id": old_tag["id"], "canonical_tag_id": canonical_id},
    )
    connection.execute(
        post_tags.delete().where(post_tags.c.tag_id == old_tag["id"])
    )
    connection.execute(
        tags.update()
        .where(tags.c.id == old_tag["id"])
        .values(is_active=False, canonical_tag_id=canonical_id)
    )


def _retire_tag(connection, tag_name: str) -> None:
    tag = _fetch_tag(connection, tag_name)
    if tag is None:
        return
    connection.execute(
        tags.update()
        .where(tags.c.id == tag["id"])
        .values(is_active=False, canonical_tag_id=None)
    )


def _reassign_tag_category(connection, tag_name: str, category_name: str) -> None:
    tag = _fetch_tag(connection, tag_name)
    category_id = _fetch_category_id(connection, category_name)
    if tag is None or category_id is None:
        return
    connection.execute(
        tags.update()
        .where(tags.c.id == tag["id"])
        .values(category_id=category_id)
    )


def upgrade() -> None:
    connection = op.get_bind()

    for canonical_tag_name in CANONICAL_TAG_DEFINITIONS:
        _ensure_canonical_tag(connection, canonical_tag_name)

    for old_tag_name, canonical_tag_name in TAG_MAPPINGS.items():
        _merge_tag(connection, old_tag_name, canonical_tag_name)

    for retired_tag_name in RETIRED_TAGS:
        _retire_tag(connection, retired_tag_name)


def downgrade() -> None:
    connection = op.get_bind()

    for retired_tag_name in RETIRED_TAGS:
        retired_tag = _fetch_tag(connection, retired_tag_name)
        if retired_tag is None:
            continue
        connection.execute(
            tags.update()
            .where(tags.c.id == retired_tag["id"])
            .values(is_active=True, canonical_tag_id=None)
        )

    for old_tag_name, canonical_tag_name in TAG_MAPPINGS.items():
        old_tag = _fetch_tag(connection, old_tag_name)
        canonical_tag = _fetch_tag(connection, canonical_tag_name)
        if old_tag is None:
            continue

        if canonical_tag is not None:
            connection.execute(
                sa.text(
                    """
                    INSERT INTO post_tags (post_id, tag_id)
                    SELECT pt.post_id, :old_tag_id
                    FROM post_tags pt
                    WHERE pt.tag_id = :canonical_tag_id
                      AND NOT EXISTS (
                        SELECT 1
                        FROM post_tags existing
                        WHERE existing.post_id = pt.post_id
                          AND existing.tag_id = :old_tag_id
                      )
                    """
                ),
                {
                    "old_tag_id": old_tag["id"],
                    "canonical_tag_id": canonical_tag["id"],
                },
            )

        connection.execute(
            tags.update()
            .where(tags.c.id == old_tag["id"])
            .values(is_active=True, canonical_tag_id=None)
        )

    for tag_name, category_name in DOWNGRADE_CATEGORY_REASSIGNMENTS.items():
        _reassign_tag_category(connection, tag_name, category_name)
