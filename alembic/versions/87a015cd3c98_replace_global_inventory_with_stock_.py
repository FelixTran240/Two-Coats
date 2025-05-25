"""replace global inventory with stock market tables

Revision ID: 87a015cd3c98
Revises: e91d0c24f7d0
Create Date: 2025-05-25 16:09:45.513850

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "87a015cd3c98"  # <-- Use a short hash (max 32 chars)
down_revision = "e91d0c24f7d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Drop the old global_inventory table
    op.drop_table("global_inventory")

    # Create users table
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(50), unique=True, nullable=False),
        sa.Column("holdings", sa.Integer, nullable=False, default=0),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
    )

    # Create stock_state table (single row for global price)
    op.create_table(
        "stock_state",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
    )

    # Insert initial stock price
    op.execute(sa.text("INSERT INTO stock_state (price) VALUES (100.00)"))

def downgrade() -> None:
    # Drop the stock_state table
    op.drop_table("stock_state")

    # Drop the users table
    op.drop_table("users")

    # Recreate the global_inventory table
    op.create_table(
        "global_inventory",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("item_name", sa.String(50), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False, default=0),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
    )
    # Note: The global_inventory table is recreated without any initial data.