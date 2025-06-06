# API Specification

## 1. `POST /users/create`

- **Description:** Register a new user with username and password.
- **Request Body:**
  ```json
  {
    "username": "felix_tran",
    "password": "strongpassword123"
  }
  ```
- **Responses:**
  - `201 Created`: User successfully registered.
  - `409 Conflict`:  username already in use.

---

## 2. `POST /users/login`

- **Description:** Authenticate a user and return an API token for future requests.
- **Request Body:**
  ```json
  {
    "Username": "felix",
    "password": "strongpassword123"
  }
  ```
- **Response:**
  ```json
  {
  "message": "Credentials verified",
  "user_id": 2,
  "username": "felix",
  "session_token": "f64e8afa-8550-416b-9c19-6ebec3cc7386"
  }
  ```
- **Errors:**
  - `401 Unauthorized`: Invalid credentials.

---

## 3. `GET /stocks/:symbol/history`

- **Description:** Retrieve historical stock data for a given symbol.
- **Path Parameters:**
  - `symbol`: The stock symbol (e.g., AAPL, TSLA).
- **Query Parameters:**
  - `start`: Start date for the history (ISO format).
  - `end`: End date for the history (ISO format).
- **Response:**
  ```json
  [
    {
      "date": "2024-04-20",
      "close": 150.25
    },
    {
      "date": "2024-04-21",
      "close": 153.5
    }
  ]
  ```
- **Errors:**
  - `404 Not Found`: Stock symbol not found.

---

## 4. `GET /stocks/:symbol/real-time`

- **Description:** Retrieve real-time price for a given stock symbol.
- **Path Parameters:**
  - `symbol`: The stock symbol (e.g., AAPL, TSLA).
- **Response:**
  ```json
  {
    "symbol": "AAPL",
    "price": 150.75,
    "timestamp": "2025-04-21T10:30:00Z"
  }
  ```
- **Errors:**
  - `404 Not Found`: Stock symbol not found.

---

## 5. `POST /watchlists`

- **Description:** Create a new watchlist for a user.
- **Request Body:**
  ```json
  {
    "userId": "12345",
    "name": "Tech Stocks Watchlist",
    "stocks": ["AAPL", "GOOGL", "AMZN"]
  }
  ```
- **Response:**
  ```json
  {
    "watchlistId": "67890",
    "name": "Tech Stocks Watchlist",
    "stocks": ["AAPL", "GOOGL", "AMZN"]
  }
  ```
- **Errors:**
  - `400 Bad Request`: Invalid input.

---

## 6. `GET /watchlists/:userId`

- **Description:** Retrieve all watchlists for a given user.
- **Path Parameters:**
  - `userId`: The user's unique identifier.
- **Response:**
  ```json
  [
    {
      "watchlistId": "67890",
      "name": "Tech Stocks Watchlist",
      "stocks": ["AAPL", "GOOGL", "AMZN"]
    }
  ]
  ```
- **Errors:**
  - `404 Not Found`: User not found.

---

## 7. `POST /insights`

- **Description:** Create a custom insight for a stock.
- **Request Body:**
  ```json
  {
    "userId": "12345",
    "stockSymbol": "AAPL",
    "insight": "Apple stock shows strong growth after quarterly earnings report."
  }
  ```
- **Response:**
  ```json
  {
    "insightId": "98765",
    "userId": "12345",
    "stockSymbol": "AAPL",
    "insight": "Apple stock shows strong growth after quarterly earnings report."
  }
  ```
- **Errors:**
  - `400 Bad Request`: Invalid input.

---

## 8. `GET /insights/:userId`

- **Description:** Retrieve all insights for a user.
- **Path Parameters:**
  - `userId`: The user's unique identifier.
- **Response:**
  ```json
  [
    {
      "insightId": "98765",
      "userId": "12345",
      "stockSymbol": "AAPL",
      "insight": "Apple stock shows strong growth after quarterly earnings report."
    }
  ]
  ```
- **Errors:**
  - `404 Not Found`: User not found.

---

## 9. `DELETE /watchlists/:watchlistId`

- **Description:** Delete a watchlist for a user.
- **Path Parameters:**
  - `watchlistId`: The unique identifier for the watchlist to delete.
- **Response:**
  ```json
  {
    "message": "Watchlist deleted successfully."
  }
  ```
- **Errors:**
  - `404 Not Found`: Watchlist not found.

---

## 10. `GET /trends`

- **Description:** Retrieve stock trends based on market data.
- **Query Parameters:**
  - `start`: Start date for trend analysis (ISO format).
  - `end`: End date for trend analysis (ISO format).
  - `symbol`: Optional filter for a specific stock symbol.
- **Response:**
  ```json
  {
    "symbol": "AAPL",
    "trend": "upward",
    "percentageChange": 5.5,
    "startDate": "2023-01-01",
    "endDate": "2023-12-31"
  }
  ```
- **Errors:**
  - `404 Not Found`: No data found for the given parameters.

---

## 11. `POST /transaction`

- **Description:** Customer chooses whether they want to buy or sell their stock(s) in dollars ($) or shares.
- **Request Body:**
  ```json
  {
    "userId": "12345",
    "token": "SECURITY-TOKEN-4c7a3b6e-e9f4-4b11-9473-8f29a2f0f021",
    "symbol": "AAPL",
    "transaction_type": "buy",
    "transaction_currency": "shares",
    "quantity": "5.00"
  }
  ```
- **Response:**
  ```json
  {
    "success": "boolean"
  }
  ```
- **Errors:**
  - `400 Bad Request`: Invalid input. (userId DNE, token invalid, symbol DNE, not enough money to buy, not enough shares to sell)
  - `404 Not Found`: No data found for the given parameters.

---

## 12. `GET /account_summary`

- **Description:** Returns customer's total money and positions in account.
- **Request Body:**
  ```json
  {
    "userId": "12345",
    "token": "SECURITY-TOKEN-4c7a3b6e-e9f4-4b11-9473-8f29a2f0f021"
  }
  ```
- **Response:**
  ```json
  {
    "total_money": 11000.0,
    "positions_dollars": {
      "AAPL": 1000.0,
      "VOO": 6000.0,
      "AMZN": 1500.0,
      "TSLA": 2000.0,
      "GOOG": 500.0
    }
  }
  ```
- **Errors:**
  - `400 Bad Request`: Invalid input. (userId DNE, token invalid)
  - `404 Not Found`: No data found for the given parameters.

---

## 13. `GET /transactions/net-transaction-summary`

- **Description:** Summarize all transactions for the current user, showing the net (buy - sell) amount for each stock and whether it is positive, negative, or neutral.
- **Query Parameters:**
  - `session_token`: The user's session token (string).
- **Response:**
  ```json
  [
    {
      "stock_id": 1,
      "ticker_symbol": "NVDA",
      "net_amount": 500.0,
      "result": "positive"
    },
    {
      "stock_id": 2,
      "ticker_symbol": "TSM",
      "net_amount": -200.0,
      "result": "negative"
    }
  ]
  ```
- **Errors:**
  - `401 Unauthorized`: Invalid session token.

---

## 14. `GET /transactions/my-transactions`

- **Description:** Returns all transactions for the user, grouped by portfolio.
- **Query Parameters:**
  - `session_token`: The user's session token (string).
- **Response:**
  ```json
  {
    "123": [
      {
        "transaction_id": 1,
        "port_id": 123,
        "stock_id": 1,
        "transaction_type": "buy",
        "change": 10.0
      }
    ],
    "456": [
      {
        "transaction_id": 2,
        "port_id": 456,
        "stock_id": 2,
        "transaction_type": "sell",
        "change": 5.0
      }
    ]
  }
  ```
- **Errors:**
  - `401 Unauthorized`: Invalid session token.

---

## 15. `GET /transactions/current-portfolio-transactions`

- **Description:** Returns all transactions for the user's current portfolio.
- **Query Parameters:**
  - `session_token`: The user's session token (string).
- **Response:**
  ```json
  [
    {
      "transaction_id": 1,
      "port_id": 123,
      "stock_id": 1,
      "transaction_type": "buy",
      "change": 10.0
    }
  ]
  ```
- **Errors:**
  - `401 Unauthorized`: Invalid session token.

---

## 16. `POST /portfolio/get_portfolio_holdings`

- **Description:** Returns all holdings for the user's current portfolio, including buying power.
- **Request Body:**
  ```json
  {
    "session_token": "SECURITY-TOKEN-4c7a3b6e-e9f4-4b11-9473-8f29a2f0f021"
  }
  ```
- **Response:**
  ```json
  {
    "portfolio_id": 123,
    "buying_power": 5000.0,
    "holdings": [
      { "stock_id": 1, "num_shares": 10.0, "total_shares_value": 1500.0 }
    ]
  }
  ```
- **Errors:**
  - `401 Unauthorized`: Invalid session token.

---

## 17. `POST /portfolio/list_portfolios`

- **Description:** List all portfolios owned by the user.
- **Request Body:**
  ```json
  {
    "session_token": "SECURITY-TOKEN-4c7a3b6e-e9f4-4b11-9473-8f29a2f0f021"
  }
  ```
- **Response:**
  ```json
  {
    "portfolios": [
      {
        "port_id": 123,
        "port_name": "Growth",
        "buying_power": 5000.0,
        "portfolio_value": 8000.0
      }
    ]
  }
  ```
- **Errors:**
  - `401 Unauthorized`: Invalid session token.

---

## 18. `POST /portfolio/create`

- **Description:** Create a new portfolio for the user.
- **Request Body:**
  ```json
  {
    "portfolio_name": "New Portfolio",
    "session_token": "SECURITY-TOKEN-4c7a3b6e-e9f4-4b11-9473-8f29a2f0f021"
  }
  ```
- **Response:**
  ```json
  {
    "message": "Portfolio created successfully.",
    "portfolio_id": 456,
    "portfolio_name": "New Portfolio"
  }
  ```
- **Errors:**
  - `401 Unauthorized`: Invalid session token.

---

## 19. `POST /transactions/buy_shares`

- **Description:** Buy shares of a stock for the user's current portfolio.
- **Request Body:**
  ```json
  {
    "session_token": "SECURITY-TOKEN-4c7a3b6e-e9f4-4b11-9473-8f29a2f0f021",
    "stock_ticker": "NVDA",
    "num_shares": 5.0
  }
  ```
- **Response:**
  ```json
  {
    "message": "Shares bought successfully.",
    "transaction_id": 789,
    "stock_ticker": "NVDA",
    "num_shares_bought": 5.0,
    "total_cost": 1500.0
  }
  ```
- **Errors:**
  - `401 Unauthorized`: Invalid session token.
  - `400 Bad Request`: Not enough buying power or invalid input.

---

## 20. `POST /transactions/sell_shares`

- **Description:** Sell shares of a stock from the user's current portfolio.
- **Request Body:**
  ```json
  {
    "session_token": "SECURITY-TOKEN-4c7a3b6e-e9f4-4b11-9473-8f29a2f0f021",
    "stock_ticker": "NVDA",
    "num_shares": 2.0
  }
  ```
- **Response:**
  ```json
  {
    "message": "Shares sold successfully.",
    "transaction_id": 790,
    "stock_ticker": "NVDA",
    "num_shares_sold": 2.0,
    "total_proceeds": 600.0
  }
  ```
- **Errors:**
  - `401 Unauthorized`: Invalid session token.
  - `400 Bad Request`: Not enough shares or invalid input.

---

# Complex Endpoints

## 1. `POST /portfolio/get_portfolio_holdings`

- **Description:** Show all holdings for the user's current portfolio, including buying power.
- **Request Body:**
  ```json
  {
  "session_token": "f64e8afa-8550-416b-9c19-6ebec3cc7386"
  }
  ```
- **Response:**
  ```json
  {
    "portfolio_id": 1,
    "portfolio_value": 100,
    "buying_power": 66.73,
    "holdings": [
      {
        "stock_id": 4,
        "stock_ticker": "NVDA",
        "num_shares": 0.1,
        "total_shares_value": 13.74
      },
      {
        "stock_id": 1,
        "stock_ticker": "AAPL",
        "num_shares": 0.1,
        "total_shares_value": 19.53
      }
    ]
  }
  ```
- **Errors:**
  - `401 Unauthorized`: Invalid session token.
  - `422 Unprocessable Content`: Expecting value.

---

## 2. `POST /transactions/sell_dollars`

- **Description:** Sell a specific stock holding based on dollars (type conversions and calculation of shares to deduct)
- **Request Body:**
  ```json
  {
    "session_token": "2a34256c-d463-49ac-970b-6f9f67132c21",
    "stock_ticker": "nvda",
    "dollars": 13.73
}
  ```
- **Response:**
  ```json
  {
    "message": "Stock successfully sold",
    "transaction_id": 10,
    "stock_ticker": "NVDA",
    "num_shares_sold": 0.09994176736060562,
    "total_proceeds": 13.73
  }
  ```
- **Errors:**
  - `401 Unauthorized`: Invalid session token.
  - `422 Unprocessable Content`: Expecting value.

---

