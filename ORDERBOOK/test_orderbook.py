import unittest
from ORDERBOOK.orderbook import Order, OrderBook

class TestOrderBook(unittest.TestCase):

    def test_fifo_execution(self):
        """Test FIFO execution with multiple orders at same and different price levels"""
        
        # ✅ Initialize OrderBook
        order_book = OrderBook()

        # ✅ Add BUY Orders (Random Order)
        order_book.add_limit_order(Order(orderSide="BUY", price=100, quantity=5, orderType="LIMIT"))
        order_book.add_limit_order(Order(orderSide="BUY", price=101, quantity=3, orderType="LIMIT"))
        order_book.add_limit_order(Order(orderSide="BUY", price=100, quantity=4, orderType="LIMIT"))
        order_book.add_limit_order(Order(orderSide="BUY", price=102, quantity=2, orderType="LIMIT"))

        # ✅ Add SELL Orders (Random Order)
        order_book.add_limit_order(Order(orderSide="SELL", price=100, quantity=6, orderType="LIMIT"))
        order_book.add_limit_order(Order(orderSide="SELL", price=101, quantity=5, orderType="LIMIT"))
        order_book.add_limit_order(Order(orderSide="SELL", price=102, quantity=3, orderType="LIMIT"))

        # ✅ Match Orders
        order_book.matchOrder(Order(orderSide="BUY", price=102, quantity=14, orderType="LIMIT"))

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
