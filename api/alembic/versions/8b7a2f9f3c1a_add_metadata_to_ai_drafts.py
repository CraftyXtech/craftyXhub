"""add_metadata_to_ai_drafts

Revision ID: 8b7a2f9f3c1a
Revises: 51994986c29a
Create Date: 2025-10-31 06:15:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b7a2f9f3c1a'
down_revision = '51994986c29a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('ai_drafts', sa.Column('draft_metadata', sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column('ai_drafts', 'draft_metadata')
