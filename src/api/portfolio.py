import time
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator

import sqlalchemy
from src.api import auth
from src import database as db
from typing import List


router = APIRouter(
    tags=["portfolio"],
    dependencies=[Depends(auth.get_api_key)],
)


class CreatePortfolio(BaseModel):
    portfolio_name: str
    session_token: str

class CreationResponse(BaseModel):
    message: str
    portfolio_id: int
    portfolio_name: str

@router.post("/create", response_model=CreationResponse)
def create_portfolio(new_portfolio: CreatePortfolio) -> CreationResponse:
    """
    Creates a new portfolio under a user's ownership after authentication
    """

    with db.engine.begin() as connection:
        # Authenticate w/ session token
        user = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens 
                WHERE token = :token
                """
            ),
            {
                "token": new_portfolio.session_token
            }
        ).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid session")

        # Check for existing portfolio name per user
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1 from portfolios
                WHERE user_id = :user_id AND port_name = :port_name
                """
            ),
            {
                "user_id": user.user_id,
                "port_name": new_portfolio.portfolio_name
            }
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="You already own a portfolio with the same name")
        

        # Insert new entry into portfolio table
        res = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO portfolios (user_id, port_name)
                VALUES (:user_id, :port_name)
                RETURNING port_id, port_name
                """
            ),
            {
                "user_id": user.user_id,
                "port_name": new_portfolio.portfolio_name
            }
        ).first()

        return CreationResponse(
            message="Portfolio successfully created!",
            portfolio_id=res.port_id,
            portfolio_name=res.port_name
        )


class ListPortfolios(BaseModel):
    session_token: str

class ListResponse(BaseModel):
    portfolios: list[dict]

@router.post("/list_portfolios", response_model=ListResponse)
def list_portfolios(list_req: ListPortfolios) -> ListResponse:
    """
    List the portfolios that users own (and their information) 
    """

    with db.engine.begin() as connection:
        # Authenticate session token
        user = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens
                WHERE token = :token
                """
            ),
            {"token": list_req.session_token}
        ).first()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid session token")

        # Get all portfolios for this user
        portfolios = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                p.port_id, p.port_name, p.buying_power,
                p.buying_power + COALESCE(SUM(ph.total_shares_value), 0) AS portfolio_value
                FROM portfolios p
                LEFT JOIN portfolio_holdings ph ON p.port_id = ph.port_id
                WHERE user_id = :user_id
                GROUP BY
                p.port_id, p.port_name, p.buying_power
                """
            ),
            {"user_id": user.user_id}
        ).fetchall()

        portfolios_list=[
            {
                "portfolio_id": p.port_id,
                "portfolio_name": p.port_name,
                "buying_power": float(p.buying_power),
                "portfolio_value": float(p.portfolio_value)
            }
            for p in portfolios
        ]

        return ListResponse(portfolios=portfolios_list)


class FindCurrentPortfolio(BaseModel):
    session_token: str

class FindCurrentPortfolioResponse(BaseModel):
    message: str
    portfolio_id: int
    portfolio_name: str
    buying_power: float 
    portfolio_value: float

@router.post("/find_current_portfolio", response_model=FindCurrentPortfolioResponse)
def find_current_portfolio(fcp: FindCurrentPortfolio) -> FindCurrentPortfolioResponse:
    """
    Return the current portfolio the user is in.
    """

    with db.engine.begin() as connection:
        # Verify session token
        logged_in = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens
                WHERE token = :session_token
                """
            ),
            {"session_token": fcp.session_token}
        ).first()

        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session token")

        user_id = logged_in.user_id

        # Retrieve user's current portfolio
        res = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                p.port_id, p.port_name, p.buying_power,
                p.buying_power + COALESCE(SUM(ph.total_shares_value), 0) AS portfolio_value
                FROM user_current_portfolio ucp
                JOIN portfolios p ON ucp.current_portfolio = p.port_id
                LEFT JOIN portfolio_holdings ph ON p.port_id = ph.port_id
                WHERE ucp.user_id = :user_id
                GROUP BY p.port_id, p.port_name, p.buying_power
                """
            ),
            {"user_id": user_id}
        ).first()

        # Instead of returning null values, throw a 404 error.
        if not res:
            raise HTTPException(status_code=404, detail="No current portfolio set for this user")

        return FindCurrentPortfolioResponse(
            message = "Current portfolio found",
            portfolio_id = res.port_id,
            portfolio_name = res.port_name,
            buying_power = float(res.buying_power),
            portfolio_value = float(res.portfolio_value)
        ) 


class SwitchPortfolio(BaseModel):
    portfolio_name: str
    session_token: str

class SwitchResponse(BaseModel):
    message: str
    user_id: int
    current_portfolio: int

    # type is str for formatting reasons
    current_portfolio_name: str

@router.post("/switch", response_model=SwitchResponse)
def switch_portfolio(switch_request: SwitchPortfolio) -> SwitchResponse:
    """
    Updates value that represents the user's current active portfolio
    """

    with db.engine.begin() as connection:
        # Validate active session 
        logged_in = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens
                WHERE token = :session_token
                """
            ),
            {"session_token": switch_request.session_token}
        ).first()

        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session token")

        user_id = logged_in.user_id

        # Get portfolio_id for given user & portfolio_name
        portfolio = connection.execute(
            sqlalchemy.text(
                """
                SELECT port_id FROM portfolios
                WHERE user_id = :user_id AND port_name = :port_name
                """
            ),
            {
                "user_id": user_id,
                "port_name": switch_request.portfolio_name
            }
        ).first()

        if not portfolio:
            raise HTTPException(status_code=400, detail="Portfolio not found")

        portfolio_id = portfolio.port_id

        # Update user_current_portfolio
        update = connection.execute(
            sqlalchemy.text(
                """
                UPDATE user_current_portfolio
                SET current_portfolio = :port_id
                WHERE user_id = :user_id
                RETURNING user_id, current_portfolio
                """
            ),
            {
                "port_id": portfolio_id,
                "user_id": user_id
            }
        ).first()

        if not update:
            raise HTTPException(status_code=400, detail="Failed to switch active portfolio")

        return SwitchResponse(
            message="Current portfolio successfully switched",
            user_id=update.user_id,
            current_portfolio=update.current_portfolio,
            current_portfolio_name=switch_request.portfolio_name
        )


class HoldingOut(BaseModel):
    stock_id: int
    stock_ticker: str
    num_shares: float
    total_shares_value: float

class HoldingsResponse(BaseModel):
    portfolio_id: int
    portfolio_value: float
    buying_power: float
    holdings: List[HoldingOut]

@router.post("/get_portfolio_holdings", response_model=HoldingsResponse)
def get_portfolio_holdings(fcp: FindCurrentPortfolio) -> HoldingsResponse:
    """
    Show all holdings for the user's current portfolio, including buying power.
    """

    with db.engine.begin() as connection:
        # Verify session token
        logged_in = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens
                WHERE token = :session_token
                """
            ),
            {"session_token": fcp.session_token}
        ).first()

        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session token")

        user_id = logged_in.user_id

        # Get current portfolio id
        res = connection.execute(
            sqlalchemy.text(
                """
                SELECT current_portfolio FROM user_current_portfolio
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_id}
        ).first()

        if not res:
            raise HTTPException(status_code=404, detail="No current portfolio set for this user")

        portfolio_id = res.current_portfolio

        # Get buying power for this portfolio
        bp_res = connection.execute(
            sqlalchemy.text(
                """
                SELECT buying_power FROM portfolios
                WHERE port_id = :portfolio_id
                """
            ),
            {"portfolio_id": portfolio_id}
        ).first()

        buying_power = bp_res.buying_power if bp_res else 0.0

        # Get holdings for this portfolio
        holdings = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                ph.stock_id, ph.num_shares, ph.total_shares_value, s.ticker_symbol
                FROM portfolio_holdings ph
                JOIN stocks s ON ph.stock_id = s.stock_id
                WHERE ph.port_id = :portfolio_id
                """
            ),
            {"portfolio_id": portfolio_id}
        ).fetchall()

        # Store list of holdings
        holdings_list = [
            HoldingOut(
                stock_id=h.stock_id,
                stock_ticker=h.ticker_symbol,
                num_shares=h.num_shares,
                total_shares_value=h.total_shares_value
            ) for h in holdings
        ]

        # Get overall value of portfolio (buying power + total_shares_value)
        value = connection.execute(
            sqlalchemy.text(
                """
                SELECT 
                p.buying_power + COALESCE(SUM(ph.total_shares_value), 0) AS portfolio_value
                FROM portfolios p
                LEFT JOIN portfolio_holdings ph ON p.port_id = ph.port_id
                WHERE p.port_id = :portfolio_id 
                GROUP BY p.port_id, p.buying_power
                """
            ),
            {"portfolio_id": portfolio_id}
        ).first()

        portfolio_value = value.portfolio_value

        return HoldingsResponse(
            portfolio_id=portfolio_id,
            portfolio_value=portfolio_value,
            buying_power=buying_power,
            holdings=holdings_list
        )

