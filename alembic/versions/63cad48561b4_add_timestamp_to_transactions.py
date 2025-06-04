"""Add timestamp to transactions

Revision ID: 63cad48561b4
Revises: 467a4183df5e
Create Date: 2025-06-03 22:48:42.419098

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '63cad48561b4'
down_revision: Union[str, None] = '467a4183df5e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "transactions",
        sa.Column(
            "timestamp",
            sa.TIMESTAMP,
            server_default=sa.func.now(),
        )
    ) 


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("transactions", "timestamp") 
