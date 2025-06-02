"""Add new stock options

Revision ID: dc71e1f5b19d
Revises: 72c320ebdcb7
Create Date: 2025-06-02 16:22:07.350266

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc71e1f5b19d'
down_revision: Union[str, None] = '72c320ebdcb7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            -- Add example NVDA stock
            INSERT INTO stocks (ticker_symbol, stock_name)
            VALUES ('NVDA', 'Nvidia Corporation');

            INSERT INTO stock_state (stock_id, price_per_share)
            VALUES (4, 137.38);

            -- Add example TSM stock
            INSERT INTO stocks (ticker_symbol, stock_name)
            VALUES ('TSM', 'Taiwan Semiconductor Manufacturing Company Limited');

            INSERT INTO stock_state (stock_id, price_per_share)
            VALUES (5, 194.84);

            -- Add example Oracle stock
            INSERT INTO stocks (ticker_symbol, stock_name)
            VALUES ('ORCL', 'Oracle Corporation');

            INSERT INTO stock_state (stock_id, price_per_share)
            VALUES (6, 166.57);

            -- Add example Gamestop stock
            INSERT INTO stocks (ticker_symbol, stock_name)
            VALUES ('GME', 'GameStop Corp.');

            INSERT INTO stock_state (stock_id, price_per_share)
            VALUES (7, 30.64);

            -- Add example Adobe stock
            INSERT INTO stocks (ticker_symbol, stock_name)
            VALUES ('ADBE', 'Adobe Inc.');

            INSERT INTO stock_state (stock_id, price_per_share)
            VALUES (8, 403.40);

            -- Add example Salesforce INC stock
            INSERT INTO stocks (ticker_symbol, stock_name)
            VALUES ('CRM', 'Salesforce, Inc.');

            INSERT INTO stock_state (stock_id, price_per_share)
            VALUES (9, 261.62);

            -- Add example Riotttt stock
            INSERT INTO stocks (ticker_symbol, stock_name)
            VALUES ('RIOT', 'Riot Platforms, Inc.');
            
            INSERT INTO stock_state (stock_id, price_per_share)
            VALUES (10, 8.48);
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE FROM stock_state WHERE stock_id IN (4,5,6,7,8,9,10);
            DELETE FROM stocks WHERE ticker_symbol IN ('NVDA','TSM','ORCL','GME','ADBE','CRM','RIOT');
            """
        )
    )
    