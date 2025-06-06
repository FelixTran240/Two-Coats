"""Adding tables for watchlists

Revision ID: 80cecdbd8ece
Revises: 63cad48561b4
Create Date: 2025-06-05 23:49:51.632246

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '80cecdbd8ece'
down_revision: Union[str, None] = '63cad48561b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Tables to accomodate watchlist endpoints (same structure as portfolios)
    op.create_table(
        "watchlists",
        sa.Column(
            "watchlist_id",
            sa.Integer,
            autoincrement=True,
            primary_key=True
        ),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", name="user_id"),
            nullable=False
        ),
        sa.Column(
            "name",
            sa.String,
            nullable=False
        )
    )

    op.create_table(
        "watchlist_items",
        sa.Column(
            "watchlist_id",
            sa.Integer,
            sa.ForeignKey("watchlists.watchlist_id", name="watchlist_id"),
            nullable=False
        ),
        sa.Column(
            "stock_id",
            sa.Integer,
            sa.ForeignKey("stocks.stock_id", name="stock_id"),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("watchlist_id", "stock_id", name="wi_comp_key"),
    )

    op.create_table(
        "user_current_watchlist",
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", name="user_id"),
            primary_key=True
        ),
        sa.Column(
            "current_watchlist",
            sa.Integer,
            sa.ForeignKey("watchlists.watchlist_id", name="watchlist_id"),
            nullable=True,
            server_default=sa.text("NULL")
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("wi_comp_key", "watchlist_items", type_="primary")
    op.drop_table("user_current_watchlist")
    op.drop_table("watchlist_items")
    op.drop_table("watchlists") 
