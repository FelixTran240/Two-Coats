# Peer Review Response

## Code Review - Nicolas Chau

- Added error handling into endpoints, throwing appropriate HTTP exceptions
- Improved documentation by adding step-by-step comments
- Each transaction is logged and can be used to view buy/sell history
- SQL queries used, buying/selling returns a confirmation of purchase w/ description of item
- Improved endpoint naming for clarity
- Ambuguity in README resolved
- Implemented appropriate HTTP Exceptions being raised along with the detail
- Buy/sell transactions are already serialized
- Potential database entry collisions tested
- Catalog returned with stocks/prices endpoint
- User login and session authentication implemented
- Return values in function headers added for clarity

---

## Schema/API Design - Nicolas Chau

- Passwords hashed and session tokens are use to authenticate per-user actions
- Stock table shows both ticker symbol and company name
- User creation has been added
- Appropriate HTTP Execption status codes have been implemented to catch more specific errors
- Made price checking separated from buying/selling, as the checking is a GET while the buy/sell is a POST
- Usernames added to user profiles
- Timestamps added to major tables
- Suggested password changing
- Users can view specific stocks with /price endpoint
- Usernames already have a unique constraint
- Watchlists will help users track companies they are interested in
- Suggested adding contraint to not allowing stock to be negative but no negative stocks exist, although some are priced at $0 per share
- Transactions record user, stock, and portfolio ID

---

## Test Results - Nicolas Chau

### 1. User wants to check price of specific stock:
```
curl -X 'GET' \
  'https://two-coats-jpcx.onrender.com/stocks/price?stock_ticker=nvda' \
  -H 'accept: application/json' \
  -H 'access_token: gluttony'
```
Response: 
```
{
  "stock_ticker": "NVDA",
  "stock_name": "Nvidia Corporation",
  "price_per_share": 137.38
}
```

### 2. User creates a buy transaction without a price
```
curl -X 'POST' \
  'https://two-coats-jpcx.onrender.com/transactions/buy_shares' \
  -H 'accept: application/json' \
  -H 'access_token: gluttony' \
  -H 'Content-Type: application/json' \
  -d '{
  "session_token": "7bdd1ef2-51a7-436e-8395-0e0f9f2a560f",
  "stock_ticker": "nvda",
  "num_shares": 
}'
```
Response: 
```
Error: response status is 422
{
  "detail": [
    {
      "type": "json_invalid",
      "loc": [
        "body",
        104
      ],
      "msg": "JSON decode error",
      "input": {},
      "ctx": {
        "error": "Expecting value"
      }
    }
  ]
}
```

### 3. User wants to check the price of a stock whose symbol does not exist
```
curl -X 'GET' \
  'https://two-coats-jpcx.onrender.com/stocks/price?stock_ticker=junk' \
  -H 'accept: application/json' \
  -H 'access_token: gluttony'
```
Response:
```
Error: response status is 404
{
  "detail": "Stock not found"
}
```

---

## Product Ideas - Nicolas Chau

- Users can look up stock by ticker symbol, suggested more specific filters
- Suggested buying stocks with best trend

---

## Code Review - Rishan Baweja
- Repository restructured and organized
- Documentation to code added
- BaseModels implemented for response models
- Return types for functions added
- Database URL removed from public view
- More specific error handling implemented
- main.py cleaned up
- Class definitions for request and response models written before functions that use them are called
- All buying_power updates are done through REPEATABLE READ isolation level transactions
- Portfolio functionality corrected and fleshed out in portfolio.py
- Input validation done through request models passed into POST functions
- Buy and sell functionality added

---

## Schema/API Design - Rishan Baweja
- User login done through POST /users/login and a session token is returned to use for any per-user transaction endpoints. Session token is deleted from the DB once user uses POST /users/logout.
- The data will stretch back a week
- Suggested consolidating stock history into /stocks/price endpoint
- UserID comes from user /users/create
- Suggested showing more information in watchlist
- Suggested implementing logic that generates insights of a specific stock
- Suggested time-based purchases
- Amount of shares in company show up in POST /portfolio/get_portfolio_holdings
- Suggested displaying principal when user buys stock
- Mock-portfolios start with a default of $100.00
- Table stores username and hashed password for authentication
- Users can look up stocks by ticker symbol


---

## Test Results - Rishan Baweja

### 1. The user creates a bad input when going to buy a stock
```
curl -X 'POST' \
  'https://two-coats-jpcx.onrender.com/transactions/buy_shares' \
  -H 'accept: application/json' \
  -H 'access_token: gluttony' \
  -H 'Content-Type: application/json' \
  -d '{
  "session_token": "7bdd1ef2-51a7-436e-8395-0e0f9f2a560f",
  "stock_ticker": "nvda",
  "num_shares": "hello"
}'
```
Response: 
```
Error: response status is 422
{
  "detail": [
    {
      "type": "float_parsing",
      "loc": [
        "body",
        "num_shares"
      ],
      "msg": "Input should be a valid number, unable to parse string as a number",
      "input": "hello"
    }
  ]
```

### 2. The user creates a bad input when going to sell a stock
```
curl -X 'POST' \
  'https://two-coats-jpcx.onrender.com/transactions/sell_shares' \
  -H 'accept: application/json' \
  -H 'access_token: gluttony' \
  -H 'Content-Type: application/json' \
  -d '{
  "session_token": "7bdd1ef2-51a7-436e-8395-0e0f9f2a560f",
  "stock_ticker": "nvda",
  "num_shares": "price"
}'
```
Response: 
```
422 Unprocessable Content
{
  "detail": [
    {
      "type": "float_parsing",
      "loc": [
        "body",
        "num_shares"
      ],
      "msg": "Input should be a valid number, unable to parse string as a number",
      "input": "price"
    }
  ]
}
```

### 3. User retrieves the list of buy transactions, when they have none
```
curl -X 'GET' \
  'https://two-coats-jpcx.onrender.com/transactions/net-transaction-summary?session_token=7bdd1ef2-51a7-436e-8395-0e0f9f2a560f' \
  -H 'accept: application/json' \
  -H 'access_token: gluttony'
```
Response:
```
[
  {
    "stock_id": 4,
    "ticker_symbol": "NVDA",
    "net_amount": 0,
    "result": "neutral"
  }
]
```

---

## Product Ideas - Rishan Baweja

- Suggested limit orders
- Suggested seeing net amount of stock based on gain/loss

---
