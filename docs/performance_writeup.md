# Performance Writeup

## 1. Fake Data Modeling

- **Script:** [fake_data.py](./test/fake_data.py)
- **Distribution:**

- **Justification:**

## 2. Performance Results of Hitting Endpoints

| Endpoint               | Avg Time (ms) |
| ---------------------- | ------------- |
| GET /stocks/price      | ms            |
| POST /transactions/buy | ms            |
| GET /users/details     | ms            |
| ...                    | ...           |

**Slowest Endpoint Identified:** POST /transactions/buy

## 3. Performance Tuning

### Initial Query Plan for Buy Endpoint Query:

```sql
EXPLAIN ANALYZE
SELECT s.stock_name, ss.price_per_share
FROM stock_state ss
JOIN stocks s ON ss.stock_id = s.stock_id
WHERE ss.stock_id = 4;
```

_Result:_

```
Seq Scan on stock_state ... Execution Time: ms
```
