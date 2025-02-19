import unittest
from orderbook import Order, OrderBook
'''
Asked GPT to come up with Unit Test Cases for console testing for the 'orderbook.py' file.'''

class TestOrderBook(unittest.TestCase):

    def setUp(self):
        """Initialize a new order book for each test."""
        self.order_book = OrderBook()

    # 1. Test Adding Orders
    def test_add_order(self):
        order = Order(orderSide="BUY", price=100, quantity=10, orderType="LIMIT")
        self.order_book.addOrder(order)
        self.assertEqual(len(self.order_book.orders), 1)
        self.assertEqual(self.order_book.orders[order.orderId].quantity, 10)

    # 2. Test Canceling Orders
    def test_cancel_order(self):
        order = Order(orderSide="SELL", price=101, quantity=5, orderType="LIMIT")
        self.order_book.addOrder(order)
        self.order_book.cancelOrder(order.orderId)
        self.assertEqual(len(self.order_book.orders), 0)

    # 3. Test Market Order Execution
    def test_market_order_execution(self):
        limit_order = Order(orderSide="SELL", price=100, quantity=5, orderType="LIMIT")
        self.order_book.addOrder(limit_order)

        market_order = Order(orderSide="BUY", price=0, quantity=3, orderType="MARKET")
        self.order_book.addOrder(market_order)
        self.order_book.match_orders()

        self.assertEqual(limit_order.quantity, 2)  # Partial fill
        self.assertEqual(len(self.order_book.orders), 1)

    # 4. Test Limit Order Execution
    def test_limit_order_execution(self):
        sell_order = Order(orderSide="SELL", price=100, quantity=5, orderType="LIMIT")
        buy_order = Order(orderSide="BUY", price=100, quantity=5, orderType="LIMIT")

        self.order_book.addOrder(sell_order)
        self.order_book.addOrder(buy_order)
        self.order_book.match_orders()

        self.assertEqual(len(self.order_book.orders), 0)  # Both fully filled

    # 5. Test Partial Fills (Multiple Orders)
    def test_partial_fill(self):
        sell_order1 = Order(orderSide="SELL", price=100, quantity=3, orderType="LIMIT")
        sell_order2 = Order(orderSide="SELL", price=100, quantity=2, orderType="LIMIT")

        self.order_book.addOrder(sell_order1)
        self.order_book.addOrder(sell_order2)

        buy_order = Order(orderSide="BUY", price=100, quantity=4, orderType="MARKET")
        self.order_book.addOrder(buy_order)
        self.order_book.match_orders()

        self.assertEqual(sell_order1.quantity, 0)  # Fully filled
        self.assertEqual(sell_order2.quantity, 1)  # Partially filled

    # 6. Test Stop Order Trigger
    def test_stop_order_trigger(self):
        sell_order = Order(orderSide="SELL", price=105, quantity=5, orderType="LIMIT")
        stop_order = Order(orderSide="BUY", price=105, quantity=5, orderType="STOP")

        self.order_book.addOrder(sell_order)
        self.order_book.addOrder(stop_order)
        self.order_book.match_orders()

        # Stop order should convert to market order and execute
        self.assertEqual(len(self.order_book.orders), 0)

    # 7. Test Removing Fully Filled Orders
    def test_remove_fully_filled_orders(self):
        buy_order = Order(orderSide="BUY", price=100, quantity=5, orderType="LIMIT")
        sell_order = Order(orderSide="SELL", price=100, quantity=5, orderType="LIMIT")

        self.order_book.addOrder(buy_order)
        self.order_book.addOrder(sell_order)
        self.order_book.match_orders()

        self.assertEqual(len(self.order_book.orders), 0)

    # 8. Test Removing Empty Price Levels
    def test_remove_empty_price_levels(self):
        order = Order(orderSide="BUY", price=100, quantity=5, orderType="LIMIT")
        self.order_book.addOrder(order)
        self.order_book.cancelOrder(order.orderId)

        price_level = self.order_book.skiplist.insertPrice(100)
        self.assertEqual(price_level.orders.size, 0)


# Run the tests
if __name__ == "__main__":
    unittest.main()
