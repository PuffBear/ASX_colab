from flask import Flask, request, jsonify  # type: ignore
from orderbook import MultiSecurityOrderBook, Order
from flask_cors import CORS  # type: ignore

app = Flask(__name__)
CORS(app)

# Global instance of MultiSecurityOrderBook
multi_security_order_book = MultiSecurityOrderBook()

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
        
        return jsonify({
            "bids": bids,
            "asks": asks,
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

if __name__ == '__main__':
    app.run(debug=True)
