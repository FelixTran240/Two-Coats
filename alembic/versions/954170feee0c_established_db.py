"""Established DB

Revision ID: 954170feee0c
Revises: [timestamp]
Create Date: 2025-05-17 02:00:48.181232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '954170feee0c'
down_revision: Union[str, None] = '[timestamp]'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer,
            autoincrement=True,
            primary_key=True
        ),
        sa.Column(
            "username",
            sa.String,
            nullable=False
        )
    )

    op.create_table(
        "stocks",
        sa.Column(
            "stock_id",
            sa.Integer,
            autoincrement=True,
            primary_key=True
        ),
        sa.Column(
            "ticker_symbol",
            sa.String,
            unique=True,
            nullable=False
        ),
        sa.Column(
            "price_per_share",
            sa.Numeric(20, 2),
            nullable=False,
            server_default="0"
        )
    )

    op.create_table(
        "transactions",
        sa.Column(
            "transaction_id",
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
            "stock_id",
            sa.Integer,
            sa.ForeignKey("stocks.stock_id", name="stock_id"),
            nullable=False
        ),
        sa.Column(
            "transaction_type",
            sa.String,
            nullable=False
        ),
        sa.Column(
            "change",
            sa.Numeric(20, 2),
            nullable=False,
            server_default="0"
        )
    )

    op.create_table(
        "portfolios",
        sa.Column(
            "port_id",
            sa.Integer,
            autoincrement=True,
            primary_key=True
        ),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", name="user_id"),
            nullable=False
        )
    )

    op.create_table(
        "portfolio_holdings",
        sa.Column(
            "port_id",
            sa.Integer,
            sa.ForeignKey("portfolios.port_id", name="port_id"),
            nullable=False
        ),
        sa.Column(
            "stock_id",
            sa.Integer,
            sa.ForeignKey("stocks.stock_id", name="stock_id"),
            nullable=False
        ),
        sa.PrimaryKeyConstraint("port_id", "stock_id", name="ph_comp_key"),
        sa.Column(
            "num_shares",
            sa.Numeric(20, 2),
            nullable=False,
            server_default="0"
        ),
        sa.Column(
            "total_shares_value",
            sa.Numeric(20, 2),
            nullable=False,
            server_default="0"
        )
    )

def downgrade() -> None:
    # Drop constraints for portfolio_holdings
    op.drop_constraint("ph_comp_key", "portfolio_holdings", type_="primary")
    op.drop_constraint(
        "port_id",
        "portfolio_holdings",
        type_="foreignkey"
    )
    op.drop_constraint(
        "stock_id",
        "portfolio_holdings",
        type_="foreignkey"
    )

    # Drop constraints for portfolios
    op.drop_constraint(
        "user_id",
        "portfolios",
        type_="foreignkey"
    )

    # Drop constraints for transactions
    op.drop_constraint(
        "user_id",
        "transactions",
        type_="foreignkey"
    )
    op.drop_constraint(
        "stock_id",
        "transactions",
        type_="foreignkey"
    )

    # Finally, drop tables in reverse order
    op.drop_table("portfolio_holdings")
    op.drop_table("portfolios")
    op.drop_table("transactions")
    op.drop_table("stocks")
    op.drop_table("users")
