from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '[timestamp]'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create the buy_transactions table
    op.create_table(
        'buy_transactions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('item_name', sa.String(length=255), nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

    # Create the sell_transactions table
    op.create_table(
        'sell_transactions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('item_name', sa.String(length=255), nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now()),
    )

def downgrade():
    # Drop the buy_transactions table
    op.drop_table('buy_transactions')

    # Drop the sell_transactions table
    op.drop_table('sell_transactions')