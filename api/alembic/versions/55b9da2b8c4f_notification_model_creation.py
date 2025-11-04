"""notification model creation

Revision ID: 55b9da2b8c4f
Revises: 927e78da30ba
Create Date: 2025-11-04 13:06:17.448348
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '55b9da2b8c4f'
down_revision = '927e78da30ba'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create notifications table (no manual enum creation!)
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('uuid', sa.String(length=36), nullable=False),
        sa.Column('recipient_id', sa.Integer(), nullable=False),
        sa.Column('sender_id', sa.Integer(), nullable=True),
        sa.Column(
            'notification_type',
            sa.Enum(
                'post_like',
                'post_comment',
                'post_bookmark',
                'comment_reply',
                'new_follower',
                'new_post_from_following',
                'post_published',
                'post_flagged',
                'post_unflagged',
                'post_reported',
                'welcome',
                'email_verified',
                name='notificationtype'
            ),
            nullable=False
        ),
        sa.Column('post_id', sa.Integer(), nullable=True),
        sa.Column('comment_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('action_url', sa.String(length=500), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('email_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['recipient_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['comment_id'], ['comments.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('ix_notifications_uuid', 'notifications', ['uuid'], unique=True)
    op.create_index('ix_notifications_recipient_id', 'notifications', ['recipient_id'])
    op.create_index('ix_notifications_notification_type', 'notifications', ['notification_type'])
    op.create_index('ix_notifications_is_read', 'notifications', ['is_read'])
    op.create_index('ix_notifications_created_at', 'notifications', ['created_at'])
    
    # Composite index for common query patterns
    op.create_index(
        'ix_notifications_recipient_unread',
        'notifications',
        ['recipient_id', 'is_read', 'created_at']
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_notifications_recipient_unread', table_name='notifications')
    op.drop_index('ix_notifications_created_at', table_name='notifications')
    op.drop_index('ix_notifications_is_read', table_name='notifications')
    op.drop_index('ix_notifications_notification_type', table_name='notifications')
    op.drop_index('ix_notifications_recipient_id', table_name='notifications')
    op.drop_index('ix_notifications_uuid', table_name='notifications')
    
    # Drop table
    op.drop_table('notifications')

    # Drop enum type manually
    notification_type_enum = postgresql.ENUM(
        'post_like',
        'post_comment',
        'post_bookmark',
        'comment_reply',
        'new_follower',
        'new_post_from_following',
        'post_published',
        'post_flagged',
        'post_unflagged',
        'post_reported',
        'welcome',
        'email_verified',
        name='notificationtype'
    )
    notification_type_enum.drop(op.get_bind(), checkfirst=True)
