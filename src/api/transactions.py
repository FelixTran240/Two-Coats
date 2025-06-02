import time
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator
import bcrypt

import sqlalchemy
from src.api import auth
from src import database as db


router = APIRouter(
    tags=["transactions"],
    dependencies=[Depends(auth.get_api_key)],
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
