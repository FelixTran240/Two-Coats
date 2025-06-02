import time
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator
import bcrypt

import sqlalchemy
from src.api import auth
from src import database as db


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
def create_portfolio(new_portfolio: CreatePortfolio):
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
    # TODO
    pass

@router.post("/list", response_model=ListResponse)
def list_portfolios():
    """
    List the portfolios that users own (and their information) 
    """

    pass


class FindCurrentPortfolio(BaseModel):
    session_token: str

class FindCurrentPortfolioResponse(BaseModel):
    # TODO
    pass

@router.post("/find_current_portfolio", response_model=FindCurrentPortfolioResponse)
def find_current_portfolio(fcp: FindCurrentPortfolio):
    """
    Find what current portfolio user is currently in (like unix pwd)
    """

    pass


class SwitchPortfolio(BaseModel):
    portfolio_name: str
    session_token: str

class SwitchResponse(BaseModel):
    message: str
    user_id: int
    current_portfolio: int
    current_portfolio_name: str

@router.post("/switch", response_model=SwitchResponse)
def switch_portfolio(switch_request: SwitchPortfolio):
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



'''
class BuyRequest(BaseModel):
    user: str
    quantity: int

@router.post("/buy")
def buy_stock(request: BuyRequest, db: Session = Depends(get_db)):
    if request.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    user = db.query(User).filter_by(username=request.user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    price_result = db.execute(text("SELECT price FROM stock_state LIMIT 1")).first()
    price_per_share = float(price_result[0]) if price_result else 100.0
    total_cost = price_per_share * request.quantity
    if user.balance < total_cost:
        raise HTTPException(status_code=400, detail="Insufficient balance")
    user.holdings += request.quantity
    user.balance -= total_cost
    db.commit()
    return {
        "message": f"{request.user} bought {request.quantity} shares.",
        "balance": float(user.balance),
        "holdings": user.holdings
    }


class SellRequest(BaseModel):
    user: str
    quantity: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/sell")
def sell_stock(request: SellRequest, db: Session = Depends(get_db)):
    if request.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    user = db.query(User).filter_by(username=request.user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.holdings < request.quantity:
        raise HTTPException(status_code=400, detail="Not enough shares to sell")
    price_result = db.execute(text("SELECT price FROM stock_state LIMIT 1")).first()
    price_per_share = float(price_result[0]) if price_result else 100.0
    total_earnings = price_per_share * request.quantity
    user.holdings -= request.quantity
    user.balance += total_earnings
    db.commit()
    return {
        "message": f"{request.user} sold {request.quantity} shares.",
        "balance": float(user.balance),
        "holdings": user.holdings
    }
'''
