# Concurrency Control in Two-Coats

## 1. Lost Update

**Scenario:**  
Two users attempt to buy shares from the same portfolio at the same time. Both read the current buying power, both see enough funds, and both update the balance, resulting in one update overwriting the other.

**Sequence Diagram:**


![Lost update diagram](https://github.com/user-attachments/assets/3b5bbe42-14a5-4ed9-9668-dc609a66a43b)


**Phenomenon:** Lost Update

**Solution:**  
Use a transaction with `SERIALIZABLE` isolation or an explicit `SELECT ... FOR UPDATE` lock on the portfolio row before updating. This ensures only one transaction can update the buying power at a time.

---

## 2. Dirty Read

**Scenario:**  
User A starts a transaction to buy shares and deducts buying power, but the transaction is not yet committed. User B reads the buying power and sees the uncommitted deduction, which might be rolled back.

**Sequence Diagram:**



![Screenshot 2025-06-04 232744](https://github.com/user-attachments/assets/9c0f6e5b-9922-43c9-b8ab-25f09d927e68)

**Phenomenon:** Dirty Read

**Solution:**  

Set the isolation level to at least `READ COMMITTED` (the default in PostgreSQL), which prevents reading uncommitted changes.

---

## 3. Phantom Read

**Scenario:**  
User A queries all transactions for a portfolio to calculate a summary. While User A is processing, User B inserts a new transaction for the same portfolio. If User A re-queries, the result set changes.

**Sequence Diagram:**



![Screenshot 2025-06-04 232754](https://github.com/user-attachments/assets/4b58432a-0c59-4587-830e-548307ad3ad8)


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
