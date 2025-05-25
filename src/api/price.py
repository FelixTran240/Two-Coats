from fastapi import APIRouter
from src.api.state import stock_data

router = APIRouter()

@router.get("/price")
def get_price():
    return {"price": stock_data["price"]}