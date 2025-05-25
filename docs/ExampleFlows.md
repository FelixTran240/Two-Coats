# Example Flows

## 1. User Registration and Login Flow
Joe, a user interested in tracking stock data, registers for an account on our platform. Here's how the process works:

1. Joe sends a `POST` request to `/users/register` with his details:
    ```json
    {
      "email": "ftran04@calpoly.edu",
      "password": "strongpassword123",
      "username": "Joe_mama"
    }
    ```
    The system responds with:
    ```json
    {
      "message": "User successfully registered.",
      "userId": "12345"
    }
    ```

2. Joe then logs in using the credentials he just registered with. He sends a `POST` request to `/auth/login`:
    ```json
    {
      "email": "ftran04@calpoly.edu",
      "password": "strongpassword123"
    }
    ```
    The system responds with:
    ```json
    {
      "token": "abcd1234.jwt.token"
    }
    ```

Joe is now authenticated and ready to use the system.

---

## 2. Stock History and Watchlist Creation Flow
Joe, now logged in, wants to track Apple Inc. stock data and create a watchlist for future monitoring.

1. Joe sends a `GET` request to `/stocks/AAPL/history` with a date range to retrieve historical stock data:
    ```json
    {
      "start": "2023-01-01",
      "end": "2023-12-31"
    }
    ```
    The system responds with the historical data:
    ```json
    [
      {
        "date": "2023-01-01",
        "close": 150.25
      },
      {
        "date": "2023-01-02",
        "close": 153.50
      }
    ]
    ```

2. Joe decides to create a watchlist to track this stock. He sends a `POST` request to `/watchlists`:
    ```json
    {
      "userId": "12345",
      "name": "Tech Stocks Watchlist",
      "stocks": ["AAPL"]
    }
    ```
    The system responds with:
    ```json
    {
      "watchlistId": "67890",
      "name": "Tech Stocks Watchlist",
      "stocks": ["AAPL"]
    }
    ```

Joe is now able to track Apple stock and can view its price and historical data at any time.

---

## 3. Price and Insight Creation Flow
Joe wants to add a custom insight about Apple stock to his profile after observing a price increase.

1. Joe first retrieves the real-time price for Apple stock by sending a `GET` request to `/stocks/AAPL/real-time`:
    ```json
    {
      "symbol": "AAPL"
    }
    ```
    The system responds with:
    ```json
    {
      "symbol": "AAPL",
      "price": 150.75,
      "timestamp": "2025-04-21T14:30:00Z"
    }
    ```

2. Joe decides to add a custom insight regarding the stock price increase. He sends a `POST` request to `/insights`:
    ```json
    {
      "userId": "12345",
      "stockSymbol": "AAPL",
      "insight": "Apple stock price rose significantly after a strong earnings report."
    }
    ```
    The system responds with:
    ```json
    {
      "insightId": "98765",
      "userId": "12345",
      "stockSymbol": "AAPL",
      "insight": "Apple stock price rose significantly after a strong earnings report."
    }
    ```

Joe now has a record of his custom insight about Apple stock, which he can reference later.
