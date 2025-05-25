from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.api.user import get_or_create_profile
from src.api.state import stock_data

router = APIRouter()

class BuyRequest(BaseModel):
    user: str
    quantity: int

@router.post("/buy")
def buy_stock(request: BuyRequest):
    if request.quantity <= 0:
        raise HTTPException(status_code=400, detail="Quantity must be positive")
    profile = get_or_create_profile(request.user)
    profile["holdings"] += request.quantity
    stock_data["price"] += 0.5 * request.quantity
    return {"message": f"{request.user} bought {request.quantity} shares."}