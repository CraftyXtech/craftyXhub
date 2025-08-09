"""fix_sqlite_timestamp_functions

Revision ID: 284a182ead1d
Revises: 4210f21b0a6b
Create Date: 2025-08-09 22:33:33.768024

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '284a182ead1d'
down_revision = '4210f21b0a6b'
branch_labels = None
depends_on = None


def upgrade():
    for table in ['users', 'posts', 'comments', 'tags', 'categories', 'reports']:  # list all your tables
        with op.batch_alter_table(table) as batch_op:
            batch_op.alter_column('created_at', 
                                server_default=sa.text("CURRENT_TIMESTAMP"))
            batch_op.alter_column('updated_at',
                                server_default=sa.text("CURRENT_TIMESTAMP"),
                                onupdate=sa.text("CURRENT_TIMESTAMP"))

def downgrade() -> None:
    pass 