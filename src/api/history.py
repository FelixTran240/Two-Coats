from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from typing import List
from collections import defaultdict
from datetime import datetime

import sqlalchemy
from src.api import auth
from src import database as db


router = APIRouter(
    tags=["history"],
    dependencies=[Depends(auth.get_api_key)],
)


class TransactionHistoryIn(BaseModel):
    session_token: str

class TransactionOut(BaseModel):
    transaction_id: int
    port_id: int
    stock_id: int
    transaction_type: str
    change: float
    timestamp: datetime 

@router.post("/current_portfolio_transactions")
def get_current_portfolio_transactions(request: TransactionHistoryIn) -> list[TransactionOut]:
    """
    Returns transactions for the user's current portfolio only.
    """

    with db.engine.begin() as connection:
        # Validate session and get user_id
        logged_in = connection.execute(
            sqlalchemy.text(
                "SELECT user_id FROM temp_user_tokens WHERE token = :token"
            ),
            {"token": request.session_token}
        ).first()
        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session token")
        user_id = logged_in.user_id

        # Get current portfolio
        current = connection.execute(
            sqlalchemy.text(
                "SELECT current_portfolio FROM user_current_portfolio WHERE user_id = :user_id"
            ),
            {"user_id": user_id}
        ).first()
        if not current:
            raise HTTPException(status_code=404, detail="Current portfolio not found")
        port_id = current.current_portfolio

        # Fetch transactions for current portfolio
        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                transaction_id,
                port_id,
                stock_id,
                transaction_type,
                change,
                timestamp
                FROM transactions
                WHERE user_id = :user_id AND port_id = :port_id
                ORDER BY transaction_id DESC
                """
            ),
            {"user_id": user_id, "port_id": port_id}
        ).fetchall()

        return [
            TransactionOut(
                transaction_id=row.transaction_id,
                port_id=row.port_id,
                stock_id=row.stock_id,
                transaction_type=row.transaction_type,
                change=float(row.change),
                timestamp=row.timestamp

            )
            for row in results
        ]

@router.post("/my_transactions")
def get_my_transactions(request: TransactionHistoryIn) -> dict:
    """
    Returns all transactions for the user, grouped by portfolio (port_id).
    """

    with db.engine.begin() as connection:
        # Validate session and get user_id
        logged_in = connection.execute(
            sqlalchemy.text(
                "SELECT user_id FROM temp_user_tokens WHERE token = :token"
            ),
            {"token": request.session_token}
        ).first()
        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session token")
        user_id = logged_in.user_id

        # Fetch transactions for this user
        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                transaction_id,
                port_id,
                stock_id,
                transaction_type,
                change,
                timestamp
                FROM transactions
                WHERE user_id = :user_id AND port_id IS NOT NULL
                ORDER BY transaction_id DESC
                """
            ),
            {"user_id": user_id}
        ).fetchall()


        # Group transactions by port_id
        grouped = defaultdict(list)
        for row in results:
            grouped[row.port_id].append(TransactionOut(
                transaction_id=row.transaction_id,
                port_id=row.port_id,
                stock_id=row.stock_id,
                transaction_type=row.transaction_type,
                change=float(row.change),
                timestamp=row.timestamp
            ))

        return {str(port_id): [t.dict() for t in txns] for port_id, txns in grouped.items()}
