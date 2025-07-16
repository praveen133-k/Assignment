from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('mobile', sa.String(20), unique=True, index=True, nullable=False),
        sa.Column('password_hash', sa.String, nullable=True),
        sa.Column('otp', sa.String(6), nullable=True),
        sa.Column('otp_created_at', sa.DateTime, nullable=True),
        sa.Column('is_active', sa.Boolean, default=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
        sa.Column('stripe_customer_id', sa.String, nullable=True),
    )
    op.create_table(
        'chatrooms',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('name', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('chatroom_id', sa.Integer, sa.ForeignKey('chatrooms.id')),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('response', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )
    op.create_table(
        'subscriptions',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('tier', sa.String, default='basic'),
        sa.Column('stripe_subscription_id', sa.String, nullable=True),
        sa.Column('status', sa.String, default='inactive'),
        sa.Column('started_at', sa.DateTime, nullable=True),
        sa.Column('expires_at', sa.DateTime, nullable=True),
    )

def downgrade():
    op.drop_table('subscriptions')
    op.drop_table('messages')
    op.drop_table('chatrooms')
    op.drop_table('users') 