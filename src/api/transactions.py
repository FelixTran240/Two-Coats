from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN
from typing import List, ClassVar
from collections import defaultdict

import sqlalchemy
from src.api import auth
from src import database as db


router = APIRouter(
    tags=["transactions"],
    dependencies=[Depends(auth.get_api_key)],
)


class BuySharesRequest(BaseModel):
    session_token: str
    stock_ticker: str
    num_shares: float 

    @field_validator("num_shares")
    @classmethod
    def validate_num_shares_decimal(cls, value: float) -> float:
        if value <= 0:
            raise HTTPException(status_code=400, detail="Number of shares must be greater than 0")
        decimal_places = abs(Decimal(str(value)).as_tuple().exponent)
        if decimal_places > 2:
            raise HTTPException(status_code=400, detail="Number of shares cannot exceed 2 decimal places")
        return value

class BuyResponse(BaseModel):
    message: str
    transaction_id: int
    stock_ticker: str
    num_shares_bought: float
    total_cost: float

@router.post("/buy_shares", response_model=BuyResponse)
def buy_shares(request: BuySharesRequest) -> BuyResponse:
    """
    Allows user to buy a stock based on shares (can go up to 2 decimal places), 
    the ticker symbol, and the current portfolio they are in. 
    """

    with db.engine.connect() as connection:
        with connection.execution_options(isolation_level="REPEATABLE READ").begin():
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
                {"ticker": request.stock_ticker.upper()}
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
            num_shares = Decimal(str(request.num_shares))
            total_cost = (num_shares * price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            # Check if portfolio has enough buying power
            buying_power = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT buying_power FROM portfolios 
                    WHERE port_id = :port_id
                    FOR UPDATE
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

            # Temporarily lock row to avoid a lost update
            connection.execute(
                sqlalchemy.text(
                    """
                    SELECT * FROM portfolio_holdings 
                    WHERE port_id = :port_id AND stock_id = :stock_id
                    FOR UPDATE
                    """
                ),
                {
                    "port_id": port_id,
                    "stock_id": stock_id
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
                    INSERT INTO transactions (port_id, user_id, stock_id, transaction_type, change)
                    VALUES (:port_id, :user_id, :stock_id, 'buy', :change)
                    RETURNING transaction_id
                    """
                ),
                {
                    "port_id": port_id,
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


class BuyDollarsRequest(BaseModel):
    session_token: str
    stock_ticker: str
    dollars: float

    @field_validator("dollars")
    @classmethod
    def validate_dollars_decimal(cls, value: float) -> float:
        if value <= 0:
            raise HTTPException(status_code=400, detail="Amount of dollars must be greater than 0")
        decimal_places = abs(Decimal(str(value)).as_tuple().exponent)
        if decimal_places > 2:
            raise HTTPException(status_code=400, detail="Amount of dollars cannot exceed 2 decimal places")
        return value

@router.post("/buy_dollars", response_model=BuyResponse)
def buy_dollars(request: BuyDollarsRequest) -> BuyResponse:
    """
    Allows user to buy a stock based on dollars (can go up to 2 decimal places),
    the ticker symbol, and the current portfolio they are in.
    """

    with db.engine.connect() as connection:
        with connection.execution_options(isolation_level="REPEATABLE READ").begin():
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
                {"ticker": request.stock_ticker.upper()}
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

            dollars = Decimal(str(request.dollars))
            price = Decimal(price_info.price_per_share)
            num_shares = (dollars / price)
            total_cost = (price * num_shares).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            # Check if portfolio has enough buying power
            buying_power = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT buying_power FROM portfolios 
                    WHERE port_id = :port_id
                    FOR UPDATE
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

            # Lock portfolio_holdings row to prevent lost update
            connection.execute(
                sqlalchemy.text(
                    """
                    SELECT * FROM portfolio_holdings 
                    WHERE port_id = :port_id AND stock_id = :stock_id
                    FOR UPDATE
                    """
                ),
                {
                    "port_id": port_id,
                    "stock_id": stock_id
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
                    "num_shares": num_shares,
                    "total_value": total_cost
                }
            )

            # Log transaction into transactions table
            transaction = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO transactions (port_id, user_id, stock_id, transaction_type, change)
                    VALUES (:port_id, :user_id, :stock_id, 'buy', :change)
                    RETURNING transaction_id
                    """
                ),
                {
                    "port_id": port_id,
                    "user_id": user_id,
                    "stock_id": stock_id,
                    "change": total_cost
                }
            ).first()

            return BuyResponse(
                message = "Stock successfully purchased",
                transaction_id = transaction.transaction_id,
                stock_ticker = stock_ticker, 
                num_shares_bought = num_shares,
                total_cost = total_cost
            )
        

class SellSharesRequest(BaseModel):
    session_token: str
    stock_ticker: str
    num_shares: float

    @field_validator("num_shares")
    @classmethod
    def validate_num_shares_decimal(cls, value: float) -> float:
        if value <= 0:
            raise HTTPException(status_code=400, detail="Number of shares must be greater than 0")
        decimal_places = abs(Decimal(str(value)).as_tuple().exponent)
        if decimal_places > 2:
            raise HTTPException(status_code=400, detail="Number of shares cannot exceed 2 decimal places")
        return value


class SellResponse(BaseModel):
    message: str
    transaction_id: int
    stock_ticker: str
    num_shares_sold: float
    total_proceeds: float

@router.post("/sell_shares", response_model=SellResponse)
def sell_shares(request: SellSharesRequest) -> SellResponse:
    """
    Allows user to buy a stock based on shares (can go up to 2 decimal places),
    the ticker symbol, and the current portfolio they are in.
    """

    with db.engine.connect() as connection:
        with connection.execution_options(isolation_level="REPEATABLE READ").begin():
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
                    SELECT ss.stock_id, ss.price_per_share, s.ticker_symbol
                    FROM stock_state ss
                    JOIN stocks s ON ss.stock_id = s.stock_id
                    WHERE s.ticker_symbol = :ticker
                    """
                ),
                {"ticker": request.stock_ticker.upper()}
            ).first()

            if not stock:
                raise HTTPException(status_code=404, detail="Stock not found")

            stock_id = stock.stock_id
            stock_ticker = stock.ticker_symbol

            price = Decimal(stock.price_per_share)
            num_shares = Decimal(str(request.num_shares))
            total_proceeds = (price * num_shares).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            # Check portfolio holdings
            holding = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT num_shares FROM portfolio_holdings
                    WHERE port_id = :port_id AND stock_id = :stock_id
                    FOR UPDATE
                    """
                ),
                {
                    "port_id": port_id,
                    "stock_id": stock_id
                }
            ).first()

            if not holding or holding.num_shares < num_shares:
                raise HTTPException(status_code=400, detail="Not enough shares to sell")

            # Subtract shares or delete row if shares reach zero
            new_share_count = holding.num_shares - num_shares
            if new_share_count > 0: 
                # Adjust total_shares_value
                connection.execute(
                    sqlalchemy.text(
                        """
                        UPDATE portfolio_holdings
                        SET num_shares = num_shares - :requested_shares,
                            total_shares_value = total_shares_value - :value
                        WHERE port_id = :port_id AND stock_id = :stock_id
                        """
                    ),
                    {
                        "requested_shares": num_shares,
                        "value": total_proceeds,
                        "port_id": port_id,
                        "stock_id": stock_id
                    }
                )
            else:
                # Cleanup for absence of stock ownership 
                connection.execute(
                    sqlalchemy.text(
                        """
                        DELETE FROM portfolio_holdings
                        WHERE
                        port_id = :port_id
                        AND stock_id = :stock_id
                        AND num_shares <= 0.001
                        """
                    ),
                    {
                        "port_id": port_id,
                        "stock_id": stock_id
                    }
                )

            # Lock portfolio to prevent lost update
            connection.execute(
                sqlalchemy.text(
                    """
                    SELECT buying_power FROM portfolios
                    WHERE port_id = :port_id
                    FOR UPDATE
                    """
                ),
                {"port_id": port_id}
            )

            # Add funds to buying power
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE portfolios
                    SET buying_power = buying_power + :proceeds
                    WHERE port_id = :port_id
                    """
                ),
                {
                    "proceeds": total_proceeds,
                    "port_id": port_id
                }
            )

            # Log transaction
            transaction = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO transactions (port_id, user_id, stock_id, transaction_type, change)
                    VALUES (:port_id, :user_id, :stock_id, 'sell', :change)
                    RETURNING transaction_id
                    """
                ),
                {
                    "port_id": port_id,
                    "user_id": user_id,
                    "stock_id": stock_id,
                    "change": total_proceeds
                }
            ).first()

            return SellResponse(
                message="Stock successfully sold",
                transaction_id=transaction.transaction_id,
                stock_ticker=stock_ticker,
                num_shares_sold=request.num_shares,
                total_proceeds=total_proceeds
            )


class SellDollarsRequest(BaseModel):
    session_token: str
    stock_ticker: str
    dollars: float

    @field_validator("dollars")
    @classmethod
    def validate_dollars_decimal(cls, value: float) -> float:
        if value <= 0:
            raise HTTPException(status_code=400, detail="Amount of dollars must be greater than 0")
        decimal_places = abs(Decimal(str(value)).as_tuple().exponent)
        if decimal_places > 2:
            raise HTTPException(status_code=400, detail="Amount of dollars cannot exceed 2 decimal places")
        return value

@router.post("/sell_dollars", response_model=SellResponse)
def sell_dollars(request: SellDollarsRequest) -> SellResponse:
    """
    Allows user to buy a stock based on shares (can go up to 2 decimal places),
    the ticker symbol, and the current portfolio they are in.
    """

    with db.engine.connect() as connection:
        with connection.execution_options(isolation_level="REPEATABLE READ").begin():
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
                    SELECT ss.stock_id, ss.price_per_share, s.ticker_symbol
                    FROM stock_state ss
                    JOIN stocks s ON ss.stock_id = s.stock_id
                    WHERE s.ticker_symbol = :ticker
                    """
                ),
                {"ticker": request.stock_ticker.upper()}
            ).first()

            if not stock:
                raise HTTPException(status_code=404, detail="Stock not found")

            stock_id = stock.stock_id
            stock_ticker = stock.ticker_symbol

            dollars = Decimal(str(request.dollars))
            price = Decimal(stock.price_per_share)
            num_shares = (dollars / price)
            total_proceeds = (price * num_shares).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            # Check portfolio holdings
            holding = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT num_shares FROM portfolio_holdings
                    WHERE port_id = :port_id AND stock_id = :stock_id
                    FOR UPDATE
                    """
                ),
                {
                    "port_id": port_id,
                    "stock_id": stock_id
                }
            ).first()

            if not holding or holding.num_shares < num_shares:
                raise HTTPException(status_code=400, detail="Not enough shares to sell")

            # Subtract shares or delete row if shares reach zero
            new_share_count = (holding.num_shares - num_shares)
            if new_share_count > 0: 
                # Adjust total_shares_value
                connection.execute(
                    sqlalchemy.text(
                        """
                        UPDATE portfolio_holdings
                        SET num_shares = num_shares - :requested_shares,
                            total_shares_value = total_shares_value - :total_proceeds
                        WHERE port_id = :port_id AND stock_id = :stock_id
                        """
                    ),
                    {
                        "requested_shares": num_shares, 
                        "total_proceeds": total_proceeds,
                        "port_id": port_id,
                        "stock_id": stock_id
                    }
                )
            else:
                # Cleanup for absence of stock ownership 
                connection.execute(
                    sqlalchemy.text(
                        """
                        DELETE FROM portfolio_holdings
                        WHERE
                        port_id = :port_id
                        AND stock_id = :stock_id
                        AND num_shares <= 0.001
                        """
                    ),
                    {
                        "port_id": port_id,
                        "stock_id": stock_id
                    }
                )

            # Lock portfolio row to prevent lost update
            connection.execute(
                sqlalchemy.text(
                    """
                    SELECT buying_power FROM portfolios
                    WHERE port_id = :port_id
                    FOR UPDATE
                    """
                ),
                {"port_id": port_id}
            )

            # Add funds to buying power
            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE portfolios
                    SET buying_power = buying_power + :proceeds
                    WHERE port_id = :port_id
                    """
                ),
                {
                    "proceeds": total_proceeds,
                    "port_id": port_id
                }
            )

            # Log transaction
            transaction = connection.execute(
                sqlalchemy.text(
                    """
                    INSERT INTO transactions (port_id, user_id, stock_id, transaction_type, change)
                    VALUES (:port_id, :user_id, :stock_id, 'sell', :change)
                    RETURNING transaction_id
                    """
                ),
                {
                    "port_id": port_id,
                    "user_id": user_id,
                    "stock_id": stock_id,
                    "change": total_proceeds
                }
            ).first()

            return SellResponse(
                message="Stock successfully sold",
                transaction_id=transaction.transaction_id,
                stock_ticker=stock_ticker,
                num_shares_sold=num_shares,
                total_proceeds=total_proceeds
            )


