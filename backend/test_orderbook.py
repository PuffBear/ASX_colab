import unittest
from orderbook import Order, OrderBook


class TestOrderBook(unittest.TestCase):

    def print_order_books(self, order_book):
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

    def test_fifo_execution(self):
        """Test FIFO execution with multiple orders at same and different price levels"""
        
        # ✅ Initialize OrderBook
        order_book = OrderBook()

        # ✅ Add BUY Orders (Random Order)
        order_book.add_limit_order(Order(orderSide="BUY", price=100, quantity=5, orderType="LIMIT"))
        self.print_order_books(order_book)

        order_book.add_limit_order(Order(orderSide="BUY", price=101, quantity=3, orderType="LIMIT"))
        self.print_order_books(order_book)

        order_book.add_limit_order(Order(orderSide="BUY", price=100, quantity=4, orderType="LIMIT"))
        self.print_order_books(order_book)

        order_book.add_limit_order(Order(orderSide="BUY", price=102, quantity=2, orderType="LIMIT"))
        self.print_order_books(order_book)

        # ✅ Add SELL Orders (Random Order)
        order_book.add_limit_order(Order(orderSide="SELL", price=100, quantity=6, orderType="LIMIT"))
        self.print_order_books(order_book)

        order_book.add_limit_order(Order(orderSide="SELL", price=101, quantity=5, orderType="LIMIT"))
        self.print_order_books(order_book)

        order_book.add_limit_order(Order(orderSide="SELL", price=102, quantity=3, orderType="LIMIT"))
        self.print_order_books(order_book)

        # ✅ Match Orders
        order_book.matchOrder(Order(orderSide="BUY", price=102, quantity=14, orderType="LIMIT"))
        self.print_order_books(order_book)

        # ✅ Verify Trades:
        # - Orders @ 100: BUY (5 + 4) vs SELL (6) → Trades: 5 + 1
        # - Orders @ 101: BUY (3) vs SELL (5) → Trade: 3
        # - Orders @ 102: BUY (2) vs SELL (3) → Trade: 2

        # ✅ Check Trades
        self.assertEqual(len(order_book.trades), 4)  # 4 Trades in Total
        self.assertEqual(order_book.trades[0][3], 5)  # First Trade: 5 @ 100
        self.assertEqual(order_book.trades[1][3], 1)  # Second Trade: 1 @ 100
        self.assertEqual(order_book.trades[2][3], 3)  # Third Trade: 3 @ 101
        self.assertEqual(order_book.trades[3][3], 2)  # Fourth Trade: 2 @ 102

        # ✅ Check Remaining Orders
        self.assertEqual(len(order_book.orders), 1)  # One SELL order at 102 remains with 1 share


# ✅ Run the tests
if __name__ == "__main__":
    unittest.main()
