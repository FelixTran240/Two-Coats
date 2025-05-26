"""Restoring tables

Revision ID: 7f6fa5471f1b
Revises: 87a015cd3c98
Create Date: 2025-05-25 16:39:01.968179

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '7f6fa5471f1b'
down_revision: Union[str, None] = '87a015cd3c98'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_table("users")

    # Users table
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
            sa.String(50),
            unique=True,
            nullable=False
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.func.now()
        )
    )

    # Stock catalog & stock pricing information
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
            "stock_name",
            sa.String,
            nullable=False
        )
    )

    op.drop_table("stock_state")

    op.create_table(
        "stock_state",
        sa.Column(
            "stock_id",
            sa.Integer,
            sa.ForeignKey("stocks.stock_id", name="stock_id"), 
            primary_key=True
        ),
        sa.Column(
            "price_per_share", sa.Numeric(10, 2), nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.func.now()
        )
    )

    # Insert example stocks (will use for local testing) 
    op.execute(
        sa.text(
            """
        -- Add example AAPL stock
            INSERT INTO stocks (ticker_symbol, stock_name)
            VALUES ('AAPL', 'Apple Inc.');

            INSERT INTO stock_state (stock_id, price_per_share)
            VALUES (1, 195.27);

        -- Add example MSFT stock
            INSERT INTO stocks (ticker_symbol, stock_name)
            VALUES ('MSFT', 'Microsoft Corporation');

            INSERT INTO stock_state (stock_id, price_per_share)
            VALUES (2, 450.18);

        -- Add example TSLA stock
            INSERT INTO stocks (ticker_symbol, stock_name)
            VALUES ('TSLA', 'Tesla, Inc.');

            INSERT INTO stock_state (stock_id, price_per_share)
            VALUES (3, 339.34);
            """
        )
    )

    # Transaction tables
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
    
    # Customer portfolios & holdings:
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
    """Downgrade schema."""
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

    # Drop constraint for stock_state
    op.drop_constraint(
        "stock_id",
        "stock_state",
        type_="foreignkey"
    )

    # Drop tables in reverse order
    op.drop_table("portfolio_holdings")
    op.drop_table("portfolios")
    op.drop_table("transactions")
    op.drop_table("stock_state")
    op.drop_table("stocks")
    op.drop_table("users")

    # Restore tables from previous alembic version 
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("username", sa.String(50), unique=True, nullable=False),
        sa.Column("holdings", sa.Integer, nullable=False, default=0),
        sa.Column("created_at", sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        "stock_state",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP, nullable=False, server_default=sa.func.now()),
    )
