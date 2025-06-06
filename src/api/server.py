from fastapi import FastAPI
from src.api.stocks import router as stocks_router
from src.api.user import router as user_router
from src.api.watchlists import router as watchlists_router
from src.api.portfolio import router as portfolio_router
from src.api.transactions import router as transactions_router
from src.api.history import router as history_router 
from src.api.admin import router as admin_router
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mini Stock Market",
    description="A miniature stock market API with buy, sell, and price endpoints. Create a user, login, and you will receive a session token that will be used for any endpoints you plan to use that involve your account. Once you log out, the session token will no longer be active and you will have to log back in to receive another active token.",
    version="0.1.0",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.include_router(stocks_router, prefix="/stocks", tags=["stocks"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(watchlists_router, prefix="/watchlists", tags=["watchlists"])
app.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])
app.include_router(transactions_router, prefix="/transactions", tags=["transactions"])
app.include_router(history_router, prefix="/history", tags=["history"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "Mini Stock Market is running!"}
