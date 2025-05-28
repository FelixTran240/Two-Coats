"""Added portfolio selection schema

Revision ID: 12af749640be
Revises: 7f6fa5471f1b
Create Date: 2025-05-27 01:21:50.933256

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '12af749640be'
down_revision: Union[str, None] = '7f6fa5471f1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Table recording which portfolio the user is currently in
    op.create_table(
            "user_current_portfolio",
            sa.Column(
                "user_id",
                sa.String,
                sa.ForeignKey("users.id", name="user_id"),
                primary_key=True
            ),
            sa.Column(
                "current_portfolio",
                sa.Integer,
                sa.ForeignKey("portfolios.port_id", name="port_id"),
                nullable=True,
                server_default=sa.text("NULL")
            )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "user_id", "user_current_portfolio",
        type_="foreignkey"
    )
    op.drop_table("user_current_portfolio")
