"""rename_template_id_to_tool_id

Revision ID: 927e78da30ba
Revises: 8b7a2f9f3c1a
Create Date: 2025-10-31 19:36:33.375090

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '927e78da30ba'
down_revision = '8b7a2f9f3c1a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column('ai_drafts', 'template_id', new_column_name='tool_id')
    op.alter_column('ai_generation_logs', 'template_id', new_column_name='tool_id')


def downgrade() -> None:
    op.alter_column('ai_drafts', 'tool_id', new_column_name='template_id')
    op.alter_column('ai_generation_logs', 'tool_id', new_column_name='template_id') 