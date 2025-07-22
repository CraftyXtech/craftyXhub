from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f288e23a929a'
down_revision = 'a8258ff121a6'
branch_labels = None
depends_on = None

# Define the ENUM type
user_role_enum = sa.Enum('ADMIN', 'MODERATOR', 'USER', name='userrole')

def upgrade() -> None:
    # Create ENUM type first
    user_role_enum.create(op.get_bind(), checkfirst=True)

    # Create the user_follows table
    op.create_table(
        'user_follows',
        sa.Column('follower_id', sa.Integer(), nullable=False),
        sa.Column('followed_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['followed_id'], ['users.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['follower_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('follower_id', 'followed_id')
    )

    # Add follower_notifications column
    op.add_column('profiles', sa.Column('follower_notifications', sa.Boolean(), nullable=True))

    # Add role column with ENUM type
    op.add_column('users', sa.Column('role', user_role_enum, nullable=False, server_default='USER'))

    # Remove server default if you want to make it cleaner
    op.alter_column('users', 'role', server_default=None)

def downgrade() -> None:
    op.drop_column('users', 'role')
    op.drop_column('profiles', 'follower_notifications')
    op.drop_table('user_follows')

    # Drop the ENUM type after removing the column that uses it
    user_role_enum.drop(op.get_bind(), checkfirst=True)
