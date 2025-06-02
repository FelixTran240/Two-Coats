from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

import sqlalchemy
from src.api import auth
from src import database as db


router = APIRouter(
    tags=["transactions"],
    dependencies=[Depends(auth.get_api_key)],
)


class BuyRequest(BaseModel):
    session_token: str
    stock_ticker: str
    num_shares: float

class BuyResponse(BaseModel):
    message: str
    transaction_id: int
    stock_ticker: str
    num_shares_bought: float
    total_cost: float

@router.post("/buy", response_model=BuyResponse)
def buy_stock(request: BuyRequest):
    """
    Allows user to buy a specific stock based on  
    ticker symbol and the current portfolio they are in
    (grabbed from user_current_portfolios). Users can buy fractional shares.
    """

    with db.engine.begin() as connection:
        # Validate session
        logged_in = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens
                WHERE token = :token
                """
            ),
            {"token": request.session_token}
        ).first()

        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session token")

        user_id = logged_in.user_id

        # Get the current portfolio
        current = connection.execute(
            sqlalchemy.text(
                """
                SELECT current_portfolio FROM user_current_portfolio
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_id}
        ).first()

        port_id = current.current_portfolio

        # Get stock_id from ticker
        stock = connection.execute(
            sqlalchemy.text(
                """
                SELECT stock_id, ticker_symbol FROM stocks
                WHERE ticker_symbol = :ticker
                """
            ),
            {"ticker": request.stock_ticker}
        ).first()

        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")

        stock_id = stock.stock_id
        stock_ticker = stock.ticker_symbol

        # Get current stock price
        price_info = connection.execute(
            sqlalchemy.text(
                """
                SELECT price_per_share FROM stock_state
                WHERE stock_id = :stock_id
                """
            ),
            {"stock_id": stock_id}
        ).first()

        if not price_info:
            raise HTTPException(status_code=404, detail="Stock price unavailable")

        price = price_info.price_per_share
        total_cost = price * Decimal(str(request.num_shares))

        # Check if portfolio has enough buying power
        buying_power = connection.execute(
            sqlalchemy.text(
                """
                SELECT buying_power FROM portfolios
                WHERE port_id = :port_id
                """
            ),
            {"port_id": port_id}
        ).first()

        if not buying_power or buying_power.buying_power < total_cost:
            raise HTTPException(status_code=400, detail="Insufficient funds")

        # Deduct funds from portfolio
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE portfolios
                SET buying_power = buying_power - :cost
                WHERE port_id = :port_id
                """
            ),
            {
                "cost": total_cost,
                "port_id": port_id
            }
        )

        # Record stock into portfolio_holdings table
        holding = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO portfolio_holdings (port_id, stock_id, num_shares, total_shares_value)
                VALUES (:port_id, :stock_id, :num_shares, :total_value)
                ON CONFLICT (port_id, stock_id) DO UPDATE
                SET num_shares = portfolio_holdings.num_shares + EXCLUDED.num_shares,
                    total_shares_value = portfolio_holdings.total_shares_value + EXCLUDED.total_shares_value
                """
            ),
            {
                "port_id": port_id,
                "stock_id": stock_id,
                "num_shares": request.num_shares,
                "total_value": total_cost
            }
        )

        # Log transaction into transactions table
        transaction = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO transactions (user_id, stock_id, transaction_type, change)
                VALUES (:user_id, :stock_id, 'buy', :change)
                RETURNING transaction_id
                """
            ),
            {
                "user_id": user_id,
                "stock_id": stock_id,
                "change": total_cost
            }
        ).first()

        return BuyResponse(
            message = "Stock successfully purchased",
            transaction_id = transaction.transaction_id,
            stock_ticker = stock_ticker, 
            num_shares_bought = request.num_shares,
            total_cost = total_cost
        )
