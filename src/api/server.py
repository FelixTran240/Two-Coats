from fastapi import FastAPI
from src.api.stocks import router as stocks_router
from src.api.user import router as user_router
from src.api.portfolio import router as portfolio_router
from src.api.transactions import router as transactions_router
from src.api.admin import router as admin_router
from starlette.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mini Stock Market",
    description="A miniature stock market API with buy, sell, and price endpoints.",
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

# app.include_router(buy_router, prefix="/stocks", tags=["stocks"])
# app.include_router(sell_router, prefix="/stocks", tags=["stocks"])

app.include_router(stocks_router, prefix="/stocks", tags=["stocks"])
app.include_router(user_router, prefix="/users", tags=["users"])
app.include_router(portfolio_router, prefix="/portfolio", tags=["portfolio"])
app.include_router(transactions_router, prefix="/transactions", tags=["transactions"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "Mini Stock Market is running!"}
