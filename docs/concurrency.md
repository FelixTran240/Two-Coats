# Concurrency Control in Two-Coats

## 1. Lost Update

**Scenario:**  
Two users attempt to buy shares from the same portfolio at the same time. Both read the current buying power, both see enough funds, and both update the balance, resulting in one update overwriting the other.

**Sequence Diagram:**

User A       User B       App/DB
  |             |            |
  |---Read----->|            |
  |             |---Read---> |
  |             |<--100------|
  |<---100------|            |
  |---Buy $30-->             |
  |             |---Buy $30->|
  |---Write(70)->            |
  |             |---Write(70)->  (Overwrites A’s update)


**Phenomenon:** Lost Update

**Solution:**  
Use a transaction with `SERIALIZABLE` isolation or an explicit `SELECT ... FOR UPDATE` lock on the portfolio row before updating. This ensures only one transaction can update the buying power at a time.

---

## 2. Dirty Read

**Scenario:**  
User A starts a transaction to buy shares and deducts buying power, but the transaction is not yet committed. User B reads the buying power and sees the uncommitted deduction, which might be rolled back.

**Sequence Diagram:**
User A       User B       App/DB
  |             |            |
  |---Begin TX-->            |
  |---Deduct $50------------>|
  |             |---Read BP->|
  |             |<--$50------|   ← sees uncommitted deduction
  |---Rollback----------------|
  |                          |


**Phenomenon:** Dirty Read

**Solution:**  
Set the isolation level to at least `READ COMMITTED` (the default in PostgreSQL), which prevents reading uncommitted changes.

---

## 3. Phantom Read

**Scenario:**  
User A queries all transactions for a portfolio to calculate a summary. While User A is processing, User B inserts a new transaction for the same portfolio. If User A re-queries, the result set changes.

**Sequence Diagram:**
User A       User B       App/DB
  |             |            |
  |---Begin TX-->            |
  |---Query Txns------------>|
  |<--[txn1, txn2]-----------|
  |             |---Insert txn3->|
  |             |<--Success------|
  |---Requery Txns---------->|
  |<--[txn1, txn2, txn3]-----|

**Phenomenon:** Phantom Read

**Solution:**  
Use `REPEATABLE READ` or `SERIALIZABLE` isolation level for the summary calculation transaction, so the set of rows seen does not change during the transaction.

---

## Summary Table

| Phenomenon    | Example Endpoint(s)                | Solution                                      |
|---------------|------------------------------------|-----------------------------------------------|
| Lost Update   | POST /transactions/buy, /sell      | SERIALIZABLE or SELECT ... FOR UPDATE         |
| Dirty Read    | Any read during another's update   | At least READ COMMITTED isolation             |
| Phantom Read  | GET /transactions/my-transactions  | REPEATABLE READ or SERIALIZABLE isolation     |

---

**Why these solutions:**  
- `SERIALIZABLE` and row-level locks prevent lost updates by ensuring only one transaction can update a row at a time.
- `READ COMMITTED` prevents dirty reads by hiding uncommitted changes.
- `REPEATABLE READ` or `SERIALIZABLE` prevent phantom reads by ensuring a consistent snapshot during a transaction.