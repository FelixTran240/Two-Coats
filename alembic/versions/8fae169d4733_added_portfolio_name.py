"""Added portfolio name

Revision ID: 8fae169d4733
Revises: d80a0035b28c
Create Date: 2025-06-01 00:54:07.980825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fae169d4733'
down_revision: Union[str, None] = 'd80a0035b28c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "portfolios",
        sa.Column(
            "port_name",
            sa.String,
            nullable=False,
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("portfolios", "port_name")
