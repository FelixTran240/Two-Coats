# Example workflow
The workflow for the buy and sell feature includes the following steps:
1. User creates a buy transaction.
2. User creates a sell transaction.
3. User retrieves the list of buy transactions.
4. User retrieves the list of sell transactions.

# Testing results
1. The curl statement called.
curl -X 'POST' \
  'https://your-service-url/buy' \
  -H 'Content-Type: application/json' \
  -d '{"item": "Laptop", "price": 1000}'
2. The response you received in executing the curl statement.
{
  "message": "Buy transaction created successfully",
  "transaction_id": 1
}

1. The curl statement called.
curl -X 'POST' \
  'https://your-service-url/sell' \
  -H 'Content-Type: application/json' \
  -d '{"item": "Laptop", "price": 1200}'
2. The response you received in executing the curl statement.
{
  "message": "Sell transaction created successfully",
  "transaction_id": 1
}

1. The curl statement called.
curl -X 'GET' \
  'https://your-service-url/buy' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
[
  {
    "transaction_id": 1,
    "item": "Laptop",
    "price": 1000
  }
]

1. The curl statement called.
curl -X 'GET' \
  'https://your-service-url/sell' \
  -H 'accept: application/json'
2. The response you received in executing the curl statement.
[
  {
    "transaction_id": 1,
    "item": "Laptop",
    "price": 1200
  }
]
