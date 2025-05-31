"""New columns

Revision ID: d80a0035b28c
Revises: 12af749640be
Create Date: 2025-05-31 16:33:25.734244

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd80a0035b28c'
down_revision: Union[str, None] = '12af749640be'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add password hash to users
    op.add_column(
        "users",
        sa.Column(
            "password_hash",
            sa.String,
            nullable=False
        )
    )

    # Add buying power per portfolio
    op.add_column(
        "portfolios",
        sa.Column(
            "buying_power",
            sa.Numeric(15, 2),
            nullable=False,
            server_default="100.00"
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "password_hash")
    op.drop_column("portfolios", "buying_power")
