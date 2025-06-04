import random
from faker import Faker
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

fake = Faker()
# Update the connection string with your local PostgreSQL credentials.
engine = create_engine("postgresql://myuser:mypassword@localhost:5432/mydatabase")
SessionLocal = sessionmaker(bind=engine)

def insert_fake_users(num_users=10000):
    """Insert fake users into the database."""
    session = SessionLocal()
    print("Inserting fake users...")
    for i in range(num_users):
        username = fake.user_name() + str(i)
        session.execute(
            text("""
                INSERT INTO users (username, password_hash, created_at)
                VALUES (:username, 'dummy_hash', NOW())
            """),
            {"username": username}
        )
    session.commit()
    session.close()
    print(f"Total users created: {num_users}")

def insert_fake_portfolios(num_portfolios_per_user=5):
    session = SessionLocal()
    print("Inserting fake portfolios...")
    initial_buying_power = 10000.00
    users = session.execute(text("SELECT id FROM users")).fetchall()
    count = 0
    for row in users:
        user_id = row[0]
        for j in range(num_portfolios_per_user):
            portfolio_name = f"Portfolio_{user_id}_{j+1}"
            session.execute(
                text("""
                    INSERT INTO portfolios (user_id, buying_power, port_name)
                    VALUES (:user_id, :buying_power, :port_name)
                """),
                {"user_id": user_id, "buying_power": initial_buying_power, "port_name": portfolio_name}
            )
            count += 1
        # Set the first portfolio as current for each user
        session.execute(
            text("""
                INSERT INTO user_current_portfolio (user_id, current_portfolio)
                VALUES (:user_id, (SELECT port_id FROM portfolios WHERE user_id = :user_id ORDER BY port_id LIMIT 1))
            """),
            {"user_id": user_id}
        )
    session.commit()
    session.close()
    print(f"Total portfolios created: {count}")

def insert_fake_transactions(transactions_per_user=50):
    """Insert fake transactions into the database."""
    session = SessionLocal()
    print("Inserting fake transactions...")
    users = session.execute(text("SELECT id FROM users")).fetchall()
    tickers = ['NVDA', 'TSM', 'ORCL', 'GME', 'ADBE', 'CRM', 'RIOT']
    ticker_map = {'NVDA': 1, 'TSM': 2, 'ORCL': 3, 'GME': 4, 'ADBE': 5, 'CRM': 6, 'RIOT': 7}
    total = 0
    for user in users:
        user_id = user[0]
        for i in range(transactions_per_user):
            ticker = random.choice(tickers)
            stock_id = ticker_map[ticker]
            transaction_type = random.choice(['buy', 'sell'])
            change = round(random.uniform(0.1, 100), 2)
            session.execute(
                text("""
                    INSERT INTO transactions (user_id, stock_id, transaction_type, change)
                    VALUES (:user_id, :stock_id, :transaction_type, :change)
                """),
                {"user_id": user_id, "stock_id": stock_id, "transaction_type": transaction_type, "change": change}
            )
            total += 1
    session.commit()
    session.close()
    print(f"Total transactions created: {total}")

def insert_fake_portfolio_holdings(num_holdings=10000):
    """Insert fake portfolio holdings into the database."""
    session = SessionLocal()
    print("Inserting fake portfolio holdings...")
    portfolios = session.execute(text("SELECT port_id FROM portfolios")).fetchall()
    tickers = ['NVDA', 'TSM', 'ORCL', 'GME', 'ADBE', 'CRM', 'RIOT']
    ticker_map = {'NVDA': 1, 'TSM': 2, 'ORCL': 3, 'GME': 4, 'ADBE': 5, 'CRM': 6, 'RIOT': 7}
    count = 0
    for i in range(num_holdings):
        port_id = random.choice(portfolios)[0]
        ticker = random.choice(tickers)
        stock_id = ticker_map[ticker]
        num_shares = round(random.uniform(0.1, 200), 2)
        unit_price = random.uniform(10, 500)
        total_shares_value = round(num_shares * unit_price, 2)
        session.execute(
            text("""
                INSERT INTO portfolio_holdings (port_id, stock_id, num_shares, total_shares_value)
                VALUES (:port_id, :stock_id, :num_shares, :total_shares_value)
            """),
            {"port_id": port_id, "stock_id": stock_id, "num_shares": num_shares, "total_shares_value": total_shares_value}
        )
        count += 1
    session.commit()
    session.close()
    print(f"Total portfolio holdings created: {count}")

def reset_database():
    session = SessionLocal()
    # List tables in the order that your table constraints require
    tables = [
        "portfolio_holdings", 
        "transactions", 
        "user_current_portfolio", 
        "portfolios", 
        "users"
    ]
    for table in tables:
        session.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;"))
    session.commit()
    session.close()
    print("Database reset complete!")
    
if __name__ == '__main__':
    reset_database()  # Call this to clear the data
    insert_fake_users()
    insert_fake_portfolios()
    insert_fake_transactions()
    insert_fake_portfolio_holdings()
    print("Fake data insertion complete!")