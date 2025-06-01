from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database import SessionLocal
from src.api.models import User
from src.api import auth

router = APIRouter(
    tags=["stocks"],
    dependencies=[Depends(auth.get_api_key)],
)

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
