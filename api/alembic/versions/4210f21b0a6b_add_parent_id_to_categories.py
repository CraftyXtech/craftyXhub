from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4210f21b0a6b'
down_revision = 'd5ea00a97b18'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        # SQLite needs batch mode to alter tables
        with op.batch_alter_table("categories") as batch_op:
            batch_op.add_column(sa.Column('parent_id', sa.Integer(), nullable=True))
            batch_op.create_foreign_key(
                "fk_categories_parent_id",
                "categories",
                ["parent_id"],
                ["id"]
            )
    else:
        # PostgreSQL and others can just alter normally
        op.add_column('categories', sa.Column('parent_id', sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_categories_parent_id",
            'categories',
            'categories',
            ['parent_id'],
            ['id']
        )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("categories") as batch_op:
            batch_op.drop_constraint("fk_categories_parent_id", type_='foreignkey')
            batch_op.drop_column('parent_id')
    else:
        op.drop_constraint("fk_categories_parent_id", 'categories', type_='foreignkey')
        op.drop_column('categories', 'parent_id')
