"""add_tagline_cover_image_to_categories

Revision ID: 5825e8dbdfb8
Revises: e7f8a9b0c1d2
Create Date: 2026-04-29 09:25:12.545923

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5825e8dbdfb8'
down_revision = 'e7f8a9b0c1d2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('categories', sa.Column('tagline', sa.String(length=200), nullable=True))
    op.add_column('categories', sa.Column('cover_image', sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column('categories', 'cover_image')
    op.drop_column('categories', 'tagline')