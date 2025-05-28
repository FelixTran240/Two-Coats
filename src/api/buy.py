from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database import SessionLocal
from src.api.models import User

router = APIRouter()

class BuyRequest(BaseModel):
    user: str
    quantity: int

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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