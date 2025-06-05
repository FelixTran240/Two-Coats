from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from typing import List
from collections import defaultdict
from datetime import datetime

import sqlalchemy
from src.api import auth
from src import database as db


router = APIRouter(
    tags=["stocks"],
    dependencies=[Depends(auth.get_api_key)],
)


class GetPriceResponse(BaseModel):
    stock_ticker: str
    stock_name: str
    price_per_share: float

@router.get("/price", response_model=GetPriceResponse)
def get_price(stock_ticker: str) -> GetPriceResponse:
    """
    Returns the info of the specified stock based on ticker symbol
    """
    
    # Retrieve the stock information
    with db.engine.begin() as connection:
        result = connection.execute(
            sqlalchemy.text(
                """
                SELECT s.ticker_symbol, s.stock_name, ss.price_per_share 
                FROM stocks s
                JOIN stock_state ss ON  s.stock_id = ss.stock_id 
                WHERE s.ticker_symbol = :ticker_symbol
                """
            ),
            {"ticker_symbol": stock_ticker.upper()}
        ).first()
        
        if not result:
            raise HTTPException(status_code=404, detail="Stock not found")
        
        stock_ticker = result.ticker_symbol
        stock_name = result.stock_name
        price_per_share = result.price_per_share

        return GetPriceResponse(
            stock_ticker = stock_ticker,
            stock_name = stock_name,
            price_per_share = float(price_per_share)
        )


@router.get("/prices")
def get_all_prices() -> list[GetPriceResponse]:
    """
    Retrieves every stock from the available catalog
    """

    with db.engine.begin() as connection:
        results = connection.execute(
            sqlalchemy.text(
                """
                SELECT s.ticker_symbol, s.stock_name, ss.price_per_share 
                FROM stocks s
                JOIN stock_state ss ON  s.stock_id = ss.stock_id 
                """
            )
        ).fetchall()
        
        return [
            GetPriceResponse( 
                stock_ticker = row.ticker_symbol,
                stock_name = row.stock_name,
                price_per_share = float(row.price_per_share)
            ) 
            for row in results
        ]
