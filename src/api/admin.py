from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy.orm import Session
from src import database as db
from src.database import SessionLocal
from src.api import auth

router = APIRouter(
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

class AdminResetPortfolioRequest(BaseModel):
    session_token: str

class AdminResetPortfolioResponse(BaseModel):
    message: str
    user_id: int

def get_db():
    db_inst = SessionLocal()
    try:
        yield db_inst
    finally:
        db_inst.close()


@router.post("/reset_portfolios", response_model=AdminResetPortfolioResponse)
def admin_reset_portfolios(request: AdminResetPortfolioRequest):
    """
    Admin endpoint to reset (delete) all portfolio information for a user.
    This deletes records from:
      - portfolio_holdings (related to the user's portfolios)
      - user_current_portfolio (the user's current portfolio selection)
      - portfolios (all portfolios belonging to the user)
    The user is identified via the provided session token.
    """
    with db.engine.begin() as connection:
        # Verify session token using raw SQL
        logged_in = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens
                WHERE token = :session_token
                """
            ),
            {"session_token": request.session_token}
        ).first()

        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session token")

        user_id = logged_in[0]

        # Delete portfolio holdings for portfolios that belong to this user.
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM portfolio_holdings 
                WHERE port_id IN (SELECT port_id FROM portfolios WHERE user_id = :user_id)
                """
            ),
            {"user_id": user_id}
        )
        
        # Delete the user's current portfolio selection.
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM user_current_portfolio
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_id}
        )

        # Delete all portfolios for this user.
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM portfolios
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_id}
        )

    return AdminResetPortfolioResponse(
        message="All portfolio data for the user has been reset.", 
        user_id=user_id
    )
