"""add category_id to tags

Revision ID: 7d6b8e4c2f10
Revises: b4f7a2c8d901
Create Date: 2026-03-25 20:05:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7d6b8e4c2f10"
down_revision = "b4f7a2c8d901"
branch_labels = None
depends_on = None


FK_NAME = "fk_tags_category_id"
INDEX_NAME = "ix_tags_category_id"


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("tags")}
    indexes = {index["name"] for index in inspector.get_indexes("tags")}
    foreign_keys = {
        foreign_key["name"]
        for foreign_key in inspector.get_foreign_keys("tags")
        if foreign_key["name"]
    }

    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("tags") as batch_op:
            if "category_id" not in columns:
                batch_op.add_column(sa.Column("category_id", sa.Integer(), nullable=True))
            if INDEX_NAME not in indexes:
                batch_op.create_index(INDEX_NAME, ["category_id"], unique=False)
            if FK_NAME not in foreign_keys:
                batch_op.create_foreign_key(
                    FK_NAME,
                    "categories",
                    ["category_id"],
                    ["id"],
                )
    else:
        if "category_id" not in columns:
            op.add_column("tags", sa.Column("category_id", sa.Integer(), nullable=True))
        if INDEX_NAME not in indexes:
            op.create_index(INDEX_NAME, "tags", ["category_id"], unique=False)
        if FK_NAME not in foreign_keys:
            op.create_foreign_key(
                FK_NAME,
                "tags",
                "categories",
                ["category_id"],
                ["id"],
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("tags")}
    indexes = {index["name"] for index in inspector.get_indexes("tags")}
    foreign_keys = {
        foreign_key["name"]
        for foreign_key in inspector.get_foreign_keys("tags")
        if foreign_key["name"]
    }

    if bind.dialect.name == "sqlite":
        with op.batch_alter_table("tags") as batch_op:
            if FK_NAME in foreign_keys:
                batch_op.drop_constraint(FK_NAME, type_="foreignkey")
            if INDEX_NAME in indexes:
                batch_op.drop_index(INDEX_NAME)
            if "category_id" in columns:
                batch_op.drop_column("category_id")
    else:
        if FK_NAME in foreign_keys:
            op.drop_constraint(FK_NAME, "tags", type_="foreignkey")
        if INDEX_NAME in indexes:
            op.drop_index(INDEX_NAME, table_name="tags")
        if "category_id" in columns:
            op.drop_column("tags", "category_id")
