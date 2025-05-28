import threading
import random
import time
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database import SessionLocal

user_holdings = {}
stock_data = {"price": 100.0}

def update_price_periodically():
    while True:
        db: Session = SessionLocal()
        try:
            result = db.execute(text("SELECT id, price FROM stock_state LIMIT 1")).first()
            if result:
                stock_id, current_price = result
                new_price = max(current_price + random.uniform(-5, 5), 1.0)
                db.execute(
                    text("UPDATE stock_state SET price = :price, updated_at = NOW() WHERE id = :id"),
                    {"price": new_price, "id": stock_id}
                )
                db.commit()
        finally:
            db.close()
        time.sleep(3600)  # 1 hour

# Start the background thread
threading.Thread(target=update_price_periodically, daemon=True).start()