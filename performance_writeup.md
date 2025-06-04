# Performance Writeup

## 1. Fake Data Modeling

- **Script:** [fake_data.py](./test/fake_data.py)
- **Distribution:**
  - **users:** 10,000
  - **portfolios:** 50,000 (5 per user)
  - **transactions:** 2500000 (50 per user)
  - **portfolio_holdings:** 50,000 (1 per portfolio)
- **Justification:**
  - The fake data script was designed to simulate a realistic multi-user trading platform. Each user has multiple portfolios and a large number of transactions, which is typical for active trading applications. This setup ensures that queries are tested under heavy load and that the database structure can scale horizontally as more users and portfolios are added. The distribution also allows us to test performance bottlenecks and optimize for the most common access patterns.

## 2. Performance Results of Hitting Endpoints

| Endpoint                                         | Avg Time (ms) |
| ------------------------------------------------ | :-----------: |
| GET /stocks/price                                |     0.040     |
| POST /transactions/buy                           |     0.342     |
| GET /users/details                               |     0.033     |
| GET /portfolio/get_portfolio_holdings            |     0.174     |
| GET /transactions/my-transactions                |    16.233     |
| GET /transactions/current-portfolio-transactions |    13.806     |
| POST /portfolio/list_portfolios                  |     2.735     |
| POST /portfolio/create                           |     0.171     |

**Slowest Endpoint Identified:** POST /transactions/buy

## 3. Performance Tuning

### Initial Query Plan for My Transactions Endpoint

```sql
EXPLAIN ANALYZE
SELECT transaction_id, port_id, stock_id, transaction_type, change
FROM transactions
WHERE user_id = 100
ORDER BY transaction_id DESC;
```

_Result:_

```
Gather Merge  (cost=6789.65..6794.55 rows=42 width=22) (actual time=13.470..16.167 rows=50 loops=1)
  Workers Planned: 2
  Workers Launched: 2
  ->  Sort  (cost=5789.63..5789.68 rows=21 width=22) (actual time=11.436..11.437 rows=17 loops=3)
        Sort Key: transaction_id DESC
        Sort Method: quicksort  Memory: 26kB
        Worker 0:  Sort Method: quicksort  Memory: 25kB
        Worker 1:  Sort Method: quicksort  Memory: 25kB
        ->  Parallel Seq Scan on transactions  (cost=0.00..5789.17 rows=21 width=22) (actual time=7.122..11.393 rows=17 loops=3)
              Filter: (user_id = 100)
              Rows Removed by Filter: 166650
Planning Time: 0.223 ms
Execution Time: 16.233 ms
```

**Interpretation:**  
The query is performing a parallel sequential scan on the `transactions` table and filtering by `user_id`, which is slow because it must scan the entire table for each request.

**Optimization:**  
Add an index on `user_id` to speed up filtering.

```sql
CREATE INDEX idx_transactions_user_id ON transactions(user_id);
```

### Query Plan After Adding Index

```sql
EXPLAIN ANALYZE

```

_Result (example):_

```



```

**Conclusion:**
