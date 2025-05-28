from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/price")
def get_price(stock_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text("SELECT price_per_share FROM stock_state WHERE stock_id = :stock_id"),
        {"stock_id": stock_id}
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Stock not found")
    return {"stock_id": stock_id, "price_per_share": float(result[0])}

@router.get("/prices")
def get_all_prices(db: Session = Depends(get_db)):
    result = db.execute(text("SELECT stock_id, price_per_share FROM stock_state")).fetchall()
    return [
        {"stock_id": row[0], "price_per_share": float(row[1])}
        for row in result
    ]