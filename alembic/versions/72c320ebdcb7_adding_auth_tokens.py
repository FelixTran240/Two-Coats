"""Adding auth tokens

Revision ID: 72c320ebdcb7
Revises: 8fae169d4733
Create Date: 2025-06-01 01:26:27.283376

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72c320ebdcb7'
down_revision: Union[str, None] = '8fae169d4733'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
            "temp_user_tokens",
            sa.Column(
                "token",
                sa.String,
                primary_key=True
            ),
            sa.Column(
                "user_id",
                sa.Integer,
                sa.ForeignKey("users.id", name="user_id"),
                nullable=False
            ),
            sa.Column(
                "generated_at",
                sa.TIMESTAMP,
                nullable=False,
                server_default=sa.func.now()
            )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "user_id",
        "temp_user_tokens",
        type_="foreignkey"
    )

    op.drop_table("temp_user_tokens")
