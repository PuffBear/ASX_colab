from flask import Flask, request, jsonify  # type: ignore
from orderbook import MultiSecurityOrderBook, Order
from flask_cors import CORS  # type: ignore
import random
import time
import threading

app = Flask(__name__)
CORS(app)

# Global instance of MultiSecurityOrderBook
multi_security_order_book = MultiSecurityOrderBook()

# Set initial LTPs for AAPL, TSLA, MSFT
# IPO Listings lmao
stock_initial_ltps = {
    "AAPL": 213,
    "TSLA": 249,
    "MSFT": 388
}

for stock, initial_ltp in stock_initial_ltps.items():
    order_book = multi_security_order_book.get_order_book(stock)
    initial_buy = Order("BUY", initial_ltp, 1, "LIMIT", "INITIAL_USER")
    initial_sell = Order("SELL", initial_ltp, 1, "LIMIT", "INITIAL_USER")
    order_book.add_limit_order(initial_buy)
    order_book.add_limit_order(initial_sell)
    order_book.matchAllOrders()  # Sets LTP to initial value

# making a function for the market making trading bot
# no need for an extra file
def market_maker_bot(multi_order_book, stock_symbol, trader_id):
    """Market-making bot with wider range, aggressive matching, and consistent order placement."""
    order_book = multi_order_book.get_order_book(stock_symbol)
    max_orders = 10
    active_orders = {}
    range_width = 15  # ±15 from LTP for larger range

    while True:
        ltp = order_book.get_ltp()
        if ltp is None:
            ltp = random.uniform(30, 50)

        # Check and remove matched/canceled orders from active_orders
        orders_to_remove = []
        for order_id in active_orders:
            if order_id not in order_book.orders:  # Order no longer in the order book
                orders_to_remove.append(order_id)
        for order_id in orders_to_remove:
            del active_orders[order_id]
            print(f"Market Maker ({trader_id}) removed matched/canceled order ID {order_id} from active_orders")

        if len(active_orders) < max_orders and random.random() < 0.7:
            side = random.choice(["BUY", "SELL"])
            min_price = max(1, int(ltp - range_width))
            max_price = int(ltp + range_width)
            base_price = random.randint(min_price, max_price)

            best_bid_price = order_book.get_best_bid()
            best_ask_price = order_book.get_best_ask()
            price = base_price

            # Very aggressive matching bias (exact match)
            if side == "BUY" and best_ask_price is not None:
                price = int(best_ask_price)  # Exact match with best ask
            elif side == "SELL" and best_bid_price is not None:
                price = int(best_bid_price)  # Exact match with best bid

            price = max(1, price)
            quantity = random.randint(1, 20)

            order = Order(side, price, quantity, "LIMIT", trader_id)
            order_book.add_limit_order(order)
            order_book.matchAllOrders()
            active_orders[order.orderId] = order
            print(f"Market Maker ({trader_id}) placed {side} order on {stock_symbol}: {quantity} @ {price} (LTP: {ltp})")

        elif active_orders and random.random() < 0.3:  # Increased cancellation probability
            order_id = random.choice(list(active_orders.keys()))
            order_book.cancelOrder(order_id)
            del active_orders[order_id]
            print(f"Market Maker ({trader_id}) canceled order ID {order_id} on {stock_symbol}")

        time.sleep(random.uniform(1, 3))

@app.route('/place_trade', methods=['POST'])
def process_order():
    try:
        data = request.json
        stock = data.get("stock")
        order_side = data.get("order_side")
        price = data.get("price")
        quantity = data.get("quantity")
        order_type = "limit"  # Enforcing limit orders only

        # Validate input
        if not stock:
            return jsonify({"error": "Stock symbol is required"}), 400
        
        # Ensure order book exists for the given stock
        if stock not in multi_security_order_book.list_all_securities():
            return jsonify({"error": "Invalid stock symbol"}), 400

        if order_side not in ["BUY", "SELL"]:
            return jsonify({"error": "Invalid order side (must be 'BUY' or 'SELL')"}), 400

        if not isinstance(price, (int, float)) or not isinstance(quantity, int) or price <= 0 or quantity <= 0:
            return jsonify({"error": "Price must be positive float and quantity must be positive integer"}), 400

        # Create limit order object
        order = Order(order_side, price, quantity, order_type)

        # Add order to the specific stock's order book and attempt matching
        response = multi_security_order_book.add_order(stock, order)

        return jsonify({"message": response})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_orderbook/<symbol>', methods=['GET'])
def get_orderbook(symbol):
    try:
        # Get the order book for the specified symbol
        order_book = multi_security_order_book.get_order_book(symbol)
        if not order_book:
            return jsonify({"error": "Invalid stock symbol"}), 400
        
        # Get bids and asks
        bids = order_book.get_bids()
        asks = order_book.get_asks()

        ltp = order_book.get_ltp()
        
        return jsonify({
            "bids": bids,
            "asks": asks,
            "ltp": ltp,
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# start the bot when the app launches. 
if __name__ == '__main__':
    # Start a market-making bot for each stock
    bot_threads = [
        threading.Thread(
            target=market_maker_bot,
            args=(multi_security_order_book, "AAPL", "BOT_MM_AAPL"),
            daemon=True
        ),
        threading.Thread(
            target=market_maker_bot,
            args=(multi_security_order_book, "TSLA", "BOT_MM_TSLA"),
            daemon=True
        ),
        threading.Thread(
            target=market_maker_bot,
            args=(multi_security_order_book, "MSFT", "BOT_MM_MSFT"),
            daemon=True
        )
    ]
    for thread in bot_threads:
        thread.start()

    app.run(debug=True, threaded=True)
