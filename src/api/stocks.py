from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field
import sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.api import auth
from src import database as db


router = APIRouter(
    tags=["stocks"],
    dependencies=[Depends(auth.get_api_key)],
)


def get_db():
    db_inst = db.SessionLocal()
    try:
        yield db_inst
    finally:
        db_inst.close()


@router.get("/price")
def get_price(stock_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("""
            SELECT s.stock_name, ss.price_per_share 
            FROM stock_state ss
            JOIN stocks s ON ss.stock_id = s.stock_id
            WHERE ss.stock_id = :stock_id
        """),
        {"stock_id": stock_id}
    ).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Stock not found")
    
    stock_name, price_per_share = result
    return {
        "stock_id": stock_id,
        "stock_name": stock_name,
        "price_per_share": float(price_per_share)
    }

@router.get("/prices")
def get_all_prices(db: Session = Depends(get_db)):
    results = db.execute(
        text("""
            SELECT s.stock_name, ss.stock_id, ss.price_per_share 
            FROM stock_state ss
            JOIN stocks s ON ss.stock_id = s.stock_id
        """)
    ).fetchall()
    
    return [
        {
            "stock_id": row[1],
            "stock_name": row[0],
            "price_per_share": float(row[2])
        }
        for row in results
    ]
