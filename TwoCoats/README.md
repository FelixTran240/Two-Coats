# Buy and Sell Service

This project is a simple buy and sell service built using Flask and SQLAlchemy. It allows users to create and retrieve buy and sell transactions.

## Project Structure

```
buy-sell-service
├── src
│   ├── app.py                # Entry point of the application
│   ├── models                # Contains database models
│   │   └── __init__.py
│   ├── routes                # Contains route definitions
│   │   ├── buy.py            # Buy functionality routes
│   │   ├── sell.py           # Sell functionality routes
│   │   └── __init__.py
│   ├── services              # Contains services for database interaction
│   │   ├── database.py       # Database connection and functions
│   │   └── __init__.py
│   └── tests                 # Contains unit tests
│       ├── test_buy.py       # Tests for buy functionality
│       ├── test_sell.py      # Tests for sell functionality
│       └── __init__.py
├── alembic                   # Contains migration scripts
│   ├── versions
│   │   └── [timestamp]_create_schema.py
│   └── env.py
├── requirements.txt          # Project dependencies
├── alembic.ini              # Alembic configuration
├── v1_manual_test_results.md # Test results for the example workflow
├── README.md                 # Project documentation
└── .gitignore                # Git ignore file
```

## Setup Instructions

1. Clone the repository:
   ```
   git clone <repository-url>
   cd TwoCoats
   ```

2. Create your own virtual environment:
   ```
   python3 -m venv venv
   ```

3. Activate virtual environment:
      For macOS/Linux:
   ```
   source venv/bin/activate
   ```

      For Windows:
   ```
   venv\Scripts\activate
   ```

4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

5. Set up the database:
   - Ensure you have a PostgreSQL database running.
   - Update the database connection settings in `src/services/database.py`.
   - Run the Alembic migrations to create the necessary schema:
     ```
     alembic upgrade head
     ```

6. Run the application:
   ```
   python run.py
   ```

## Usage

- To create a buy transaction, send a POST request to `/buy` with the necessary data.
- To retrieve buy transactions, send a GET request to `/buy`.
- To create a sell transaction, send a POST request to `/sell` with the necessary data.
- To retrieve sell transactions, send a GET request to `/sell`.

## Testing

Unit tests are provided for both buy and sell functionalities. To run the tests, use:
```
pytest src/tests
```

## License

This project is licensed under the MIT License.
