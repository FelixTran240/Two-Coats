
# API Specification

## 1. `POST /users/register`
- **Description:** Register a new user with email and password.
- **Request Body:**
  ```json
  {
    "email": "ftran04@calpoly.edu",
    "password": "strongpassword123",
    "username": "felix_tran"
  }
  ```
- **Responses:**
  - `201 Created`: User successfully registered.
  - `409 Conflict`: Email or username already in use.

---

## 2. `POST /auth/login`
- **Description:** Authenticate a user and return an API token for future requests.
- **Request Body:**
  ```json
  {
    "email": "ftran04@calpoly.edu",
    "password": "strongpassword123"
  }
  ```
- **Response:**
  ```json
  {
    "token": "abcd1234.jwt.token"
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
      "close": 153.50
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
Customer chooses whether they want to buy or sell their stock(s) in dollars ($) or shares.

**Request**:

```json
[
  {
    "userId": "12345",
    "token": "SECURITY-TOKEN-4c7a3b6e-e9f4-4b11-9473-8f29a2f0f021"
    "symbol": "AAPL",
    "transaction_type": "buy"
    "transaction_currency": "shares"
    "quantity": "5.00"
  },
  {
    ...
  }
]
```
**Response**:

```json
{
    "success": "boolean"
}
```
- **Errors:**
  - `400 Bad Request`: Invalid input. (userId DNE, token invalid, symbol DNE, not enough money to buy, not enough shares to sell)
  - `404 Not Found`: No data found for the given parameters.

---

## 12. `POST /account_summary` 
Returns customer's total money and positions in account.

**Request**:

```json
[
  {
    "userId": "12345",
    "token": "SECURITY-TOKEN-4c7a3b6e-e9f4-4b11-9473-8f29a2f0f021"
    ""
  },
  {
    ...
  }
]
```
**Response**:

```json
{
    "total_money": 11000.00,
    "positions_dollars": {
      "AAPL": 1000.00
      "VOO": 6000.00
      "AMZN": 1500.00
      "TSLA": 2000.00
      "GOOG": 500.00
    }
    ""
}
```
- **Errors:**
  - `400 Bad Request`: Invalid input. (userId DNE, token invalid)
  - `404 Not Found`: No data found for the given parameters.

---
