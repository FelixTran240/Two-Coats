from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator
import bcrypt

import sqlalchemy
from src.api import auth
from src import database as db


router = APIRouter(
    tags=["stocks"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.get("/price")
def get_price():
    pass
    """
    result = db.execute(
        text("SELECT price_per_share FROM stock_state WHERE stock_id = :stock_id"),
        {"stock_id": stock_id}
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"stock_id": stock_id, "price_per_share": float(result[0])}
    """

@router.get("/prices")
def get_all_prices():
    pass
    """
    result = db.execute(text("SELECT stock_id, price_per_share FROM stock_state")).fetchall()
    return [
        {"stock_id": row[0], "price_per_share": float(row[1])}
        for row in result
    ]
    """
