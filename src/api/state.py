import threading
import random
import time

user_holdings = {}
stock_data = {"price": 100.0}

def update_price_periodically():
    while True:
        # Randomly change price by -5 to +5
        stock_data["price"] += random.uniform(-5, 5)
        # Ensure price doesn't go below 1
        stock_data["price"] = max(stock_data["price"], 1.0)
        time.sleep(3600)  # 1 hour in seconds

# Start the background thread
threading.Thread(target=update_price_periodically, daemon=True).start()