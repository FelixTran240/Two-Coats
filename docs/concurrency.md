# Concurrency Control in Two-Coats

## 1. Lost Update

**Scenario:**  

A single user triggers two buy_shares or sell_shares requests simultaneously (e.g., double-clicks a "Buy" button or uses two tabs). Both read the same buying_power and portfolio_holdings, and both try to update the same rows, causing one update to overwrite the other.

**Sequence Diagram:**

```
User         User (tab 2)       App/DB
 |               |                 |
 |---Read------------------------->|
 |               |---Read--------> |
 |               |<----$100-------- 
 |<----$100------------------------|
 |---Sell $30--------------------->|
 |               |---Buy $30-----> |
 |---Write $130------------------->|
 |               |---Write $70---> (Overwrites update)
```

**Phenomenon:** Lost Update

**Solution:**  
Use `SELECT ... FOR UPDATE` on portfolios and portfolio_holdings within a REPEATABLE READ transaction to ensure exclusive row-level locks and prevent race conditions. Can use `SERIALIZABLE` but it could introduce more overhead due to less support for concurrency. This ensures only one transaction can update the buying power at a time.

---

## 2. Dirty Read

**Scenario:**  
A user triggers a buy_shares API call, which begins deducting buying_power, but has not committed yet. At the same time, the user looks at their account summary (or opens a second tab) and sees a partially updated or uncommitted balance which causes wrong info to be returned.

**Sequence Diagram:**

```
User         User (tab 2)       App/DB
 |               |                 |
 |---Buy $30---------------------->|  -- Begins transaction
 |               |                 |  -- Deducts $30 (not yet committed)
 |               |---View Balance->|
 |               |<----$70---------|  - Sees uncommitted state (was $100)
 |                                 |
 |                                 |  -- Buy fails, balance should stay $100

```

**Phenomenon:** Dirty Read

**Solution:**  

Set the isolation level to at least `READ COMMITTED` (the default in PostgreSQL), which prevents reading uncommitted changes.

---

## 3. Phantom Read

**Scenario:**  
A user runs a GET /transactions/my_transactions query to view their entire transaction history. During this process, a new transaction record is inserted by the user (e.g., by a concurrent buy_shares call). Re-running the query gives a different set of rows.

**Sequence Diagram:**

```
User             User (tab 2)         App/DB
 |                   |                  |
 |---Read Transactions----------------->|  -- Query returns 5 rows
 |                   |---Buy Shares---> |  -- INSERT INTO transactions (new row)
 |                   |                  |
 |---Read Transactions----------------->|  -- Query now returns 6 rows (phantom row)

```

**Phenomenon:** Phantom Read

**Solution:**  
Use `REPEATABLE READ` or `SERIALIZABLE` isolation level for the summary calculation transaction, so the set of rows seen does not change during the transaction.

---

## Summary Table

| Phenomenon    | Example Endpoint(s)                | Solution                                      |
|---------------|------------------------------------|-----------------------------------------------|
| Lost Update   | POST /transactions/buy, /sell      | SERIALIZABLE or SELECT ... FOR UPDATE         |
| Dirty Read    | Any read during another's update   | At least READ COMMITTED isolation             |
| Phantom Read  | POST /history/my_transactions      | REPEATABLE READ or SERIALIZABLE isolation     |

---

**Why these solutions:**  
- `SERIALIZABLE` and row-level locks prevent lost updates by ensuring only one transaction can update a row at a time.
- `READ COMMITTED` prevents dirty reads by hiding uncommitted changes.
- `REPEATABLE READ` or `SERIALIZABLE` prevent phantom reads by ensuring a consistent snapshot during a transaction.
