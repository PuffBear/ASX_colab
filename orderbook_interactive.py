from orderbook import Order, OrderBook

def interactive_order_matching():
    """Interactive order input with instant matching and exit on 'YES'."""
    order_book = OrderBook()

    print("\n🚀 Welcome to Interactive Order Matching!")
    print("👉 Enter orders in the format: BUY/SELL price quantity")
    print("💡 Type 'YES' to exit the console.\n")

    while True:
        user_input = input("Enter Order (or 'YES' to exit): ").strip()

        if user_input.upper() == "YES":
            print("\n✅ Exiting Interactive Console. Final Order Book:")
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

            # ✅ Add order to the order boo
            order_book.add_limit_order(order)

            # ✅ Attempt to match the order
            order_book.matchOrder(order)

            # ✅ Always print the order books after each input
            print_order_books(order_book)

        except ValueError:
            print("⚠️ Invalid input. Use: BUY/SELL price quantity")



def print_order_books(order_book):
    """Print Bids and Asks books after each order input."""
    print("\n--- BIDS BOOK ---")
    current = order_book.bids.head.forward[0]
    while current:
        node = current.orders.head
        orders = []
        while node:
            orders.append(f"{node.quantity} @ {node.price} (ID: {node.orderId})")
            node = node.next
        if orders:
            print(f"Price: {current.price} | Orders: {' -> '.join(orders)}")
        current = current.forward[0]

    print("\n--- ASKS BOOK ---")
    current = order_book.asks.head.forward[0]
    while current:
        node = current.orders.head
        orders = []
        while node:
            orders.append(f"{node.quantity} @ {node.price} (ID: {node.orderId})")
            node = node.next
        if orders:
            print(f"Price: {current.price} | Orders: {' -> '.join(orders)}")
        current = current.forward[0]



# ✅ Launch Interactive Matching
if __name__ == "__main__":
    interactive_order_matching()
