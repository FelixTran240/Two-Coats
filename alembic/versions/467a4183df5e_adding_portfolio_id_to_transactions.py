"""Adding portfolio_id to transactions

Revision ID: 467a4183df5e
Revises: dc71e1f5b19d
Create Date: 2025-06-03 21:02:43.031863

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '467a4183df5e'
down_revision: Union[str, None] = 'dc71e1f5b19d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "transactions",
        sa.Column(
            "port_id",
            sa.Integer,
            sa.ForeignKey("portfolios.port_id", name="port_id"),
            nullable=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint("port_id", "transactions", type_="foreignkey")
    op.drop_column("transactions", "port_id");
