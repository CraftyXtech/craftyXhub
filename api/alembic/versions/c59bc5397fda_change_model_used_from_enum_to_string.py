"""change_model_used_from_enum_to_string

Revision ID: c59bc5397fda
Revises: 4dc12cce52e1
Create Date: 2026-02-25 16:41:29.552176

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c59bc5397fda'
down_revision = '4dc12cce52e1'
branch_labels = None
depends_on = None

AIMODEL_ENUM = sa.Enum('GROK', 'OPENAI', 'GEMINI', name='aimodel')


def _normalize_models_for_enum_cast() -> None:
    """Map free-form model IDs back to legacy enum values for downgrade safety."""
    op.execute(
        """
        UPDATE ai_drafts
        SET model_used = CASE
            WHEN model_used IS NULL THEN NULL
            WHEN UPPER(model_used) IN ('GROK', 'OPENAI', 'GEMINI') THEN UPPER(model_used)
            WHEN LOWER(model_used) LIKE 'grok%' THEN 'GROK'
            WHEN LOWER(model_used) LIKE 'gemini%' THEN 'GEMINI'
            ELSE 'OPENAI'
        END
        """
    )
    op.execute(
        """
        UPDATE ai_generation_logs
        SET model_used = CASE
            WHEN UPPER(model_used) IN ('GROK', 'OPENAI', 'GEMINI') THEN UPPER(model_used)
            WHEN LOWER(model_used) LIKE 'grok%' THEN 'GROK'
            WHEN LOWER(model_used) LIKE 'gemini%' THEN 'GEMINI'
            ELSE 'OPENAI'
        END
        """
    )


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'postgresql':
        op.alter_column(
            'ai_drafts',
            'model_used',
            existing_type=AIMODEL_ENUM,
            type_=sa.String(length=100),
            existing_nullable=True,
            postgresql_using='model_used::text',
        )
        op.alter_column(
            'ai_generation_logs',
            'model_used',
            existing_type=AIMODEL_ENUM,
            type_=sa.String(length=100),
            existing_nullable=False,
            postgresql_using='model_used::text',
        )
        AIMODEL_ENUM.drop(bind, checkfirst=True)
    else:
        with op.batch_alter_table('ai_drafts') as batch_op:
            batch_op.alter_column(
                'model_used',
                existing_type=AIMODEL_ENUM,
                type_=sa.String(length=100),
                existing_nullable=True,
            )
        with op.batch_alter_table('ai_generation_logs') as batch_op:
            batch_op.alter_column(
                'model_used',
                existing_type=AIMODEL_ENUM,
                type_=sa.String(length=100),
                existing_nullable=False,
            )


def downgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name

    if dialect_name == 'postgresql':
        AIMODEL_ENUM.create(bind, checkfirst=True)
        _normalize_models_for_enum_cast()
        op.alter_column(
            'ai_drafts',
            'model_used',
            existing_type=sa.String(length=100),
            type_=AIMODEL_ENUM,
            existing_nullable=True,
            postgresql_using='model_used::aimodel',
        )
        op.alter_column(
            'ai_generation_logs',
            'model_used',
            existing_type=sa.String(length=100),
            type_=AIMODEL_ENUM,
            existing_nullable=False,
            postgresql_using='model_used::aimodel',
        )
    else:
        _normalize_models_for_enum_cast()
        with op.batch_alter_table('ai_drafts') as batch_op:
            batch_op.alter_column(
                'model_used',
                existing_type=sa.String(length=100),
                type_=AIMODEL_ENUM,
                existing_nullable=True,
            )
        with op.batch_alter_table('ai_generation_logs') as batch_op:
            batch_op.alter_column(
                'model_used',
                existing_type=sa.String(length=100),
                type_=AIMODEL_ENUM,
                existing_nullable=False,
            )
