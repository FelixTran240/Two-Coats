from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from typing import List, Optional
from collections import defaultdict
from datetime import datetime

import sqlalchemy
from src.api import auth
from src import database as db


router = APIRouter(
    tags=["watchlists"],
    dependencies=[Depends(auth.get_api_key)],
)


class CreateSwitchWatchlistRequest(BaseModel):
    session_token: str
    watchlist_name: str

class CreateSwitchWatchlistResponse(BaseModel):
    message: str
    watchlist_id: int
    watchlist_name: str

@router.post("/create", response_model=CreateSwitchWatchlistResponse)
def create_watchlist(request: CreateSwitchWatchlistRequest) -> CreateSwitchWatchlistResponse:
    """
    Creates a watchlist where users can add specific stocks to monitor
    """
    
    with db.engine.begin() as connection:
        # Authenticate user w/ session token
        logged_in = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens
                WHERE token = :token
                """
            ),
            {"token": request.session_token}
        ).first()
        
        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        # Check for existing watchlist name per user
        existing = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1 from watchlists 
                WHERE user_id = :user_id AND name = :name 
                """
            ),
            {
                "user_id": logged_in.user_id,
                "name": request.watchlist_name
            }
        ).first()

        if existing:
            raise HTTPException(status_code=400, detail="You already have a watchlist with the same name")

        # Insert new entry into watchlist table 
        res = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO watchlists (user_id, name)
                VALUES (:user_id, :name)
                RETURNING watchlist_id, name
                """
            ),
            {
                "user_id": logged_in.user_id,
                "name": request.watchlist_name
            }
        ).first()

        if res:
            return CreateSwitchWatchlistResponse(
                message="Watchlist successfully created!",
                watchlist_id=res.watchlist_id,
                watchlist_name=res.name
            )
        else:
            raise HTTPException(status_code=500, detail="Failed to create portfolio")


class GetSessionToken(BaseModel):
    session_token: str

class Watchlist(BaseModel):
    watchlist_id: int 
    name: str

class ListResponse(BaseModel):
    watchlists: List[Watchlist] 

@router.post("/list_watchlists", response_model=ListResponse)
def list_watchlists(request: GetSessionToken) -> ListResponse:
    """
    List the watchlists under user's ownership
    """

    with db.engine.begin() as connection:
        # Authenticate session token
        logged_in = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens
                WHERE token = :token
                """
            ),
            {"token": request.session_token}
        ).first()
        
        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        # Get all watchlists for user
        watchlists = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                watchlist_id, name
                FROM watchlists
                WHERE user_id = :user_id
                """
            ),
            {"user_id": logged_in.user_id}
        ).fetchall()

        watchlists_list=[
            Watchlist(
                watchlist_id = w.watchlist_id,
                name = w.name
            )
            for w in watchlists
        ]

        return ListResponse(watchlists=watchlists_list)


class FindCurrWatchlistResponse(BaseModel):
    message: str
    watchlist_id: Optional[int] = None
    name: Optional[str] = None

@router.post("/find_current_watchlist", response_model=FindCurrWatchlistResponse)
def find_current_watchlist(request: GetSessionToken) -> FindCurrWatchlistResponse:
    """
    Returns the ID and name of the watchlist the user is currently in
    """

    with db.engine.begin() as connection:
        # Authenticate session token
        logged_in = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens
                WHERE token = :token
                """
            ),
            {"token": request.session_token}
        ).first()
        
        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        user_id = logged_in.user_id

        # Retrieve user's current watchlist
        res = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                ucw.current_watchlist, w.name
                FROM user_current_watchlist ucw
                LEFT JOIN watchlists w ON ucw.current_watchlist = w.watchlist_id
                WHERE ucw.user_id = :user_id
                """
            ),
            {"user_id": user_id}
        ).first()

        if not res.current_watchlist:
            return FindCurrWatchlistResponse(
                message="No current watchlist set",
                watchlist_id=None,
                name=None
            )

        return FindCurrWatchlistResponse(
            message="Current watchlist found",
            watchlist_id=res.current_watchlist,
            name=res.name
        )


@router.post("/switch", response_model=CreateSwitchWatchlistResponse)
def switch_watchlist(request: CreateSwitchWatchlistRequest) -> CreateSwitchWatchlistResponse:
    """
    Allows a user to switch their current active portfolio
    """

    with db.engine.begin() as connection:
        # Authenticate user w/ session token
        logged_in = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens
                WHERE token = :token
                """
            ),
            {"token": request.session_token}
        ).first()
        
        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        user_id = logged_in.user_id

        # Get watchlist_id for given user & watchlist name 
        watchlist = connection.execute(
            sqlalchemy.text(
                """
                SELECT watchlist_id FROM watchlists
                WHERE user_id = :user_id AND name = :name 
                """
            ),
            {
                "user_id": user_id,
                "name": request.watchlist_name
            }
        ).first()

        if not watchlist:
            raise HTTPException(status_code=400, detail="Watchlist not found")

        watchlist_id = watchlist.watchlist_id

        # Update user_current_watchlist
        update = connection.execute(
            sqlalchemy.text(
                """
                UPDATE user_current_watchlist
                SET current_watchlist = :watchlist_id
                WHERE user_id = :user_id
                RETURNING current_watchlist
                """
            ),
            {
                "watchlist_id": watchlist_id,
                "user_id": user_id
            }
        ).first()

        if update:
            return CreateSwitchWatchlistResponse(
                message="Active watchlist switched successfully!",
                watchlist_id=update.current_watchlist,
                watchlist_name=request.watchlist_name
            )
        else:
            raise HTTPException(status_code=400, detail="Failed to switch active watchlist")


class AddRemoveRequest(BaseModel):
    session_token: str
    stock_ticker: str

class AddRemoveResponse(BaseModel):
    message: str
    stock_ticker: str
    stock_name: str

@router.post("/add_stock", response_model=AddRemoveResponse)
def add_stock(request: AddRemoveRequest) -> AddRemoveResponse:
    """
    Allows a user to add a stock into their current watchlist
    Throws an error if stock is already in the watchlist
    """

    with db.engine.begin() as connection:
        # Authenticate session token
        logged_in = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens
                WHERE token = :token
                """
            ),
            {"token": request.session_token}
        ).first()
        
        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session")

        user_id = logged_in.user_id

        # Retrieve user's current watchlist
        watchlist = connection.execute(
            sqlalchemy.text(
                """
                SELECT current_watchlist FROM user_current_watchlist
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_id}
        ).first()

        if not watchlist or not watchlist.current_watchlist:
            raise HTTPException(status_code=400, detail="No current watchlist set")

        watchlist_id = watchlist.current_watchlist

        # Validate existence of requested stock
        stock = connection.execute(
            sqlalchemy.text(
                """
                SELECT stock_id, ticker_symbol, stock_name FROM stocks
                WHERE ticker_symbol = :ticker_symbol
                """
            ),
            {"ticker_symbol": request.stock_ticker.upper()}
        ).first()

        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")

        stock_id = stock.stock_id

        # Checks if stock is already in watchlist
        exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1 FROM watchlist_items
                WHERE watchlist_id = :watchlist_id AND stock_id = :stock_id
                """
            ),
            {
                "watchlist_id": watchlist_id,
                "stock_id": stock_id
            }
        ).first()

        if exists:
            raise HTTPException(status_code=400, detail="Stock is already in watchlist")

        # Add stock into watchlist
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO watchlist_items (watchlist_id, stock_id)
                VALUES (:watchlist_id, :stock_id)
                """
            ),
            {
                "watchlist_id": watchlist_id,
                "stock_id": stock.stock_id
            }
        )

        return AddRemoveResponse(
            message="Stock successfully added to watchlist",
            stock_ticker=stock.ticker_symbol,
            stock_name=stock.stock_name
        )


@router.post("/remove_stock", response_model=AddRemoveResponse)
def remove_stock(request: AddRemoveRequest) -> AddRemoveResponse:
    """
    Allows a user to remove a stock into their current watchlist
    """
    
    with db.engine.begin() as connection:
        # Authenticate session token
        logged_in = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens
                WHERE token = :token
                """
            ),
            {"token": request.session_token}
        ).first()
        
        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session")

        user_id = logged_in.user_id

        # Retrieve user's current watchlist
        watchlist = connection.execute(
            sqlalchemy.text(
                """
                SELECT current_watchlist FROM user_current_watchlist
                WHERE user_id = :user_id
                """
            ),
            {"user_id": user_id}
        ).first()

        if not watchlist or not watchlist.current_watchlist:
            raise HTTPException(status_code=400, detail="No current watchlist set")

        watchlist_id = watchlist.current_watchlist

        # Validate existence of requested stock
        stock = connection.execute(
            sqlalchemy.text(
                """
                SELECT stock_id, ticker_symbol, stock_name FROM stocks
                WHERE ticker_symbol = :ticker_symbol
                """
            ),
            {"ticker_symbol": request.stock_ticker.upper()}
        ).first()

        if not stock:
            raise HTTPException(status_code=404, detail="Stock not found")

        stock_id = stock.stock_id

        # Checks if stock is already in watchlist
        exists = connection.execute(
            sqlalchemy.text(
                """
                SELECT 1 FROM watchlist_items
                WHERE watchlist_id = :watchlist_id AND stock_id = :stock_id
                """
            ),
            {
                "watchlist_id": watchlist_id,
                "stock_id": stock_id
            }
        ).first()

        if not exists:
            raise HTTPException(status_code=400, detail="Stock is not in watchlist")

        # Add stock into watchlist
        connection.execute(
            sqlalchemy.text(
                """
                DELETE FROM watchlist_items 
                WHERE watchlist_id = :watchlist_id AND stock_id = :stock_id
                """
            ),
            {
                "watchlist_id": watchlist_id,
                "stock_id": stock.stock_id
            }
        )

        return AddRemoveResponse(
            message="Stock successfully removed from watchlist",
            stock_ticker=stock.ticker_symbol,
            stock_name=stock.stock_name
        )


class StockItem(BaseModel):
    stock_id: int
    ticker_symbol: str
    stock_name: str
    price_per_share: float

class GetWatchlistItemsResponse(BaseModel):
    message: str
    watchlist_id: int
    watchlist_name: str
    items: List[StockItem]

@router.post("/get_watchlist_items", response_model=GetWatchlistItemsResponse)
def get_watchlist_items(request: GetSessionToken) -> GetWatchlistItemsResponse:
    """
    Returns all stocks in the user's current watchlist
    """

    with db.engine.begin() as connection:
        # Authenticate session token
        logged_in = connection.execute(
            sqlalchemy.text(
                """
                SELECT user_id FROM temp_user_tokens
                WHERE token = :token
                """
            ),
            {"token": request.session_token}
        ).first()
        
        if not logged_in:
            raise HTTPException(status_code=401, detail="Invalid session")

        user_id = logged_in.user_id

        # Retrieve user's current watchlist
        watchlist = connection.execute(
            sqlalchemy.text(
                """
                SELECT ucw.current_watchlist, w.name
                FROM user_current_watchlist ucw
                JOIN watchlists w ON ucw.current_watchlist = w.watchlist_id
                WHERE ucw.user_id = :user_id
                """
            ),
            {"user_id": user_id}
        ).first()

        if not watchlist or not watchlist.current_watchlist:
            raise HTTPException(status_code=400, detail="No current watchlist set")

        watchlist_id = watchlist.current_watchlist
        watchlist_name = watchlist.name

        # Get all stocks in the current watchlist
        rows = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                s.stock_id, s.ticker_symbol, s.stock_name, ss.price_per_share
                FROM watchlist_items wi
                JOIN stocks s ON wi.stock_id = s.stock_id
                JOIN stock_state ss ON s.stock_id = ss.stock_id
                WHERE wi.watchlist_id = :watchlist_id
                ORDER BY s.ticker_symbol
                """
            ),
            {"watchlist_id": watchlist_id}
        ).fetchall()

        # Store watchlist items into StockItem list
        stocks = [
            StockItem(
                stock_id=row.stock_id,
                ticker_symbol=row.ticker_symbol,
                stock_name=row.stock_name,
                price_per_share=row.price_per_share
            )
            for row in rows
        ]
        
        return GetWatchlistItemsResponse(
            message="Stocks retreived successfully",
            watchlist_id=watchlist_id,
            watchlist_name=watchlist_name,
            items=stocks
        )
