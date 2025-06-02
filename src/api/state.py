import threading
import random
import time
from sqlalchemy.orm import Session
from sqlalchemy import text
from src.database import SessionLocal

def update_price_periodically():
    while True:
        db: Session = SessionLocal()
        try:
            # Fetch all stocks already in the DB
            results = db.execute(text("SELECT id, price FROM stock_state")).fetchall()
            for row in results:
                stock_id, current_price = row
                # Random change between -5 and +5; new price will be at least 1.0
                change = random.uniform(-5, 5)
                new_price = max(current_price + change, 1.0)
                db.execute(
                    text("UPDATE stock_state SET price = :new_price, updated_at = NOW() WHERE id = :stock_id"),
                    {"new_price": new_price, "stock_id": stock_id}
                )
            db.commit()
        except Exception as e:
            print("Error updating prices:", e)
        finally:
            db.close()
        # Sleep for 10 minutes
        time.sleep(600)

# Start the background thread to update prices periodically
threading.Thread(target=update_price_periodically, daemon=True).start()