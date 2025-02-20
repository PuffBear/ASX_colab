from .orderbook import Order, OrderBook

def batch_order_matching():
    """Batch order input with matching triggered after 'YES'."""
    order_book = OrderBook()

    print("\n🚀 Welcome to Batch Order Matching!")
    print("👉 Enter orders in the format: BUY/SELL price quantity")
    print("💡 Type 'YES' to start matching all orders.\n")

    order_list = []

    while True:
        user_input = input("Enter Order (or 'YES' to start matching): ").strip()

        if user_input.upper() == "YES":
            print("\n✅ Starting Order Matching...")
            for order in order_list:
                order_book.matchOrder(order)
            print("\n📋 Final Order Book After Matching:")
            print_order_books(order_book)
            break

        try:
            side, price, quantity = user_input.split()
            order = Order(
                orderSide=side.upper(),
                price=float(price),
                quantity=int(quantity),
                orderType="LIMIT"
            )
            order_list.append(order)
            order_book.add_limit_order(order)
            print_order_books(order_book)

        except ValueError:
            print("⚠️ Invalid input. Use: BUY/SELL price quantity")


def print_order_books(order_book):
    """Print Bids and Asks books after each order input."""
    print("\n--- BIDS BOOK ---")
    current = order_book.bids.head.forward[0]
    while current:
        print(f"Price: {current.price}, Quantity: {current.orders.size}")
        current = current.forward[0]

    print("\n--- ASKS BOOK ---")
    current = order_book.asks.head.forward[0]
    while current:
        print(f"Price: {current.price}, Quantity: {current.orders.size}")
        current = current.forward[0]


# ✅ Launch Batch Matching
if __name__ == "__main__":
    batch_order_matching()
