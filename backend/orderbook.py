'''
The orderbook structure is as such:
OrderSide
Price (levels)
Quantity
Timestamp ( to be done)
OrderType: Limit; Stop; Market; FillOrKill(FOC); Good-till-Cancelled(GTC)

orders are sent to the order book using such a self built data structure:
# For a limit order
quote = {'type' : 'limit',
         'side' : 'bid', 
         'quantity' : 6, 
         'price' : 108.2, 
         'trade_id' : 001}
         
# and for a market order:
quote = {'type' : 'market',
         'side' : 'ask', 
         'quantity' : 6, 
         'trade_id' : 002}

'''
import time, random, itertools, threading
from threading import Lock

'''
Defining individual orders.
'''
class Order:
    # itertools used to generate unique, incremental Order IDs without explicitly tracking them
    # this process has an efficient O(1) ID generation, its Thread-Safe, No risk of duplicate orders
    # even if we end up using an SQL database, this can be used to avoid generating an idea at the 
    # time of insertion of the order in the database
    order_counter = itertools.count(1)

    def __init__(self, orderSide, price, quantity, orderType):
        # define the order's unique order id
        self.orderId = next(Order.order_counter)
        # is it a BUY or SELL -side order?
        self.side = orderSide
        self.price = price
        self.quantity = quantity
        # is it a Limit, Market, Stop order
        self.orderType = orderType
        # what is the time when the order is placed.
        self.timestamp = time.time()
        # for the DLL-FIFO implementation
        self.next = None
        self.prev = None

    # how to represent an order in the form of a string:
    # keep for debugging, but remove remove if I am logging everything into SQL.
    def __repr__(self):
        return f"Order(ID={self.orderId}, {self.side}, {self.quantity}@{self.price})"
    
    def to_dict(self):
        return {
            "side": self.side,
            "price": self.price,
            "quantity": self.quantity
        }
    
'''
FIFO execution at the DLL level:
'''
class OrderList:
    def __init__(self):
        self.head = None # represents the oldest order with FIFO logic
        self.tail = None # represents the newest order with FIFO logic
        self.size = 0 # to pre-define that initial size of the DLL is 0.

    def addOrder(self, order):
        ''' Add order to the end of the doubly linked list (FIFO queue). '''
        # if DLL is empty:
        if not self.head:
            self.head = self.tail = order # first order entry of the DLL
        else:
            # updating the tail pointer to the newest order.
            self.tail.next = order
            order.prev = self.tail
            self.tail = order
        self.size += 1

    def removeOrder(self, order):
        """ Remove an order from the Doubly Linked List (FIFO). """
        if order == self.head and order == self.tail:  # If it's the only order
            self.head = self.tail = None
        elif order == self.head:  # Removing head
            self.head = order.next
            if self.head:  # Ensure head is not None before updating
                self.head.prev = None
        elif order == self.tail:  # Removing tail
            self.tail = order.prev
            if self.tail:  # Ensure tail is not None before updating
                self.tail.next = None
        else:  # Removing from the middle
            if order.prev:
                order.prev.next = order.next
            if order.next:
                order.next.prev = order.prev

        order.next = order.prev = None  # Clean references
        self.size -= 1

    def getOldestOrder(self):
        """ Get the first (FIFO) order for execution. """
        return self.head
    
    def __repr__(self):
        orders = []
        current = self.head
        while current:
            orders.append(str(current))
            current = current.next
        return " -> ".join(orders) if orders else "No Orders"
    
    def to_list(self):
        """ Convert the linked list into a list of orders. """
        orders = []
        current = self.head
        while current:
            orders.append(current.to_dict())  # Assuming Order class has a to_dict() method
            current = current.next
        return orders
    
'''
Price level storage execution using a skiplist.
Benefits:
O(log n) insert, delete, and lookup (better cache efficiency than BST)
preferred over a BST because, BST needs rebalancing (O(log n) worst case); 
Skip List has better memory locality & simpler structure.
'''
class SkipListNode:
    def __init__(self, price):
        self.price = price
        self.orders = OrderList()
        self.forward = []
        self.lock = threading.Lock() # this is a lock for concurrent access.

class SkipList:
    def __init__(self, max_level = 32, p = 0.5):
        self.max_level = max_level
        self.p = p
        self.head = SkipListNode(-float('inf'))
        self.head.forward = [None]*self.max_level # forward basically stores the 
        # pointer to the next node in the skiplist

    def randomLevel(self):
        ''' Randomly decides on the skiplist based on probabilistic factors. '''
        level = 1
        while random.random()<self.p and level<self.max_level:
            level += 1
        return level
    
    def insertPrice(self, price):
        """Insert a new price level into the skiplist only if it doesn't already exist."""
        update = [None] * self.max_level
        current = self.head

        for i in reversed(range(self.max_level)):
            while current.forward[i] and current.forward[i].price < price:
                current = current.forward[i]
            update[i] = current

        # Return the existing node if found
        if current.forward[0] and current.forward[0].price == price:
            return current.forward[0]

        # Insert a new node if price level doesn't exist
        new_level = self.randomLevel()
        new_node = SkipListNode(price)
        new_node.orders = OrderList()
        new_node.forward = [None] * new_level

        for i in range(new_level):
            new_node.forward[i] = update[i].forward[i]
            update[i].forward[i] = new_node

        return new_node
    
    def getBestBid(self):
        ''' Funciton to get the best bid/buy side order in the skiplist. '''
        current = self.head
        while current.forward[0]:
            current = current.forward[0]
        return current.price if current.price!=-(float('inf')) else None
    
    def getBestAsk(self):
        ''' Function to get the best ask/sell side order in the skiplist. '''
        return self.head.forward[0].price if self.head.forward[0] else None
    
    def removePriceLevel(self, price):
        """ Removes a price level from the Skip List """
        update = [None] * self.max_level
        current = self.head

        for i in reversed(range(self.max_level)):
            while current.forward[i] and current.forward[i].price < price:
                current = current.forward[i]
            update[i] = current

        if current.forward[0] and current.forward[0].price == price:
            node_to_remove = current.forward[0]
            for i in range(len(node_to_remove.forward)):
                if update[i]:  # Ensure update[i] is not None
                    update[i].forward[i] = node_to_remove.forward[i] if i < len(node_to_remove.forward) else None
            print(f"Price level {price} removed from SkipList")
    
    def to_list(self):
        """ Converts SkipList into a list of (price, orders) tuples """
        orders = []
        current = self.head.forward[0]  # Skip the head (-inf)
        while current:
            price_level = current.price
            order_list = current.orders.to_list()  # Now this will work
            orders.append((price_level, order_list))
            current = current.forward[0]
        return orders

'''
Create an OrderBook using a hashset, for efficient lookup addition, deletion. 
O(1) order retrieval.

Only working with Limit orders right now, with the goal of executing partial
order filling.
'''
class OrderBook:
    def __init__(self):
        ''' Initialise the order book with bid and ask skip lists. '''
        self.bids = SkipList() # for buy orders (max price first)
        self.asks = SkipList() # for sell orders (min price first)
        self.orders = {} # create a hashset for orderId lookup.
        self.trades = []
        self.ltp = None # adding an ltp attribute

    def get_bids(self):
        """Return all bid orders as a flat list of dicts."""
        bids = self.bids.to_list()
        flat_bids = []
        for price, orders in bids:
            for order in orders:
                flat_bids.append({
                    "price": order["price"],
                    "quantity": order["quantity"],
                    "side": order["side"]
                })
        return flat_bids

    def get_asks(self):
        """Return all ask orders as a flat list of dicts."""
        asks = self.asks.to_list()
        flat_asks = []
        for price, orders in asks:
            for order in orders:
                flat_asks.append({
                    "price": order["price"],
                    "quantity": order["quantity"],
                    "side": order["side"]
                })
        return flat_asks

    # helper function to add a limit order:
    def add_limit_order(self, order):
        """Add an order to the order book."""
        if order.side == "BUY":
            price_node = self.bids.insertPrice(order.price)
        else:
            price_node = self.asks.insertPrice(order.price)

        # Only add order if it's not already in the order book
        if order.orderId not in self.orders:
            price_node.orders.addOrder(order)
            self.orders[order.orderId] = order
            print(f"Added LIMIT Order: {order.side} {order.quantity} @ {order.price}")

        # Continuously match orders after each insertion
        self.matchAllOrders()

    def process_order(self, stock, quantity, order_type, price):
    # Placeholder logic (Replace with actual order processing)
        return {
            "stock": stock,
            "quantity": quantity,
            "order_type": order_type,
            "price": price,
            "status": "filled"  # or "pending"
        }



    # gives the highest buy price order
    def get_best_bid(self):
        """ Get the best bid price using SkipList """
        return self.bids.getBestBid()
    
    # gives the lowest sell price order
    def get_best_ask(self):
        """ Get the best ask price using SkipList """
        return self.asks.getBestAsk()
    
    def get_ltp(self):
        return self.ltp
    
    def execute_trade(self, order, match_order, trade_qty):
        """Execute a trade between two orders."""
        trade_price = match_order.price
        print(f"Trade Executed: {trade_qty} @ {trade_price}")

        # Update LTP after every trade
        self.ltp = trade_price
        print("-------------------")
        print("|                 |")
        print("|                 |")
        print("|                 |")
        print("======xxxxxxx======")
        print(f"LTP Updated: {self.ltp}")
        print("======xxxxxxx======")
        print("|                 |")
        print("|                 |")
        print("|                 |")
        print("-------------------")

        # Record the trade
        self.trades.append((order.orderId, match_order.orderId, trade_price, trade_qty))

        # Update Quantities
        order.quantity -= trade_qty
        match_order.quantity -= trade_qty

        # Correct Behavior for Partial Fills
        if match_order.quantity == 0:
            self.cancelOrder(match_order.orderId)  # Fully filled, remove from order book
        else:
            self.update_order_quantity(match_order)  # Partial fill, update quantity

        if order.quantity == 0:
            self.cancelOrder(order.orderId)  # Fully filled, remove from order book
        else:
            self.update_order_quantity(order)  # Partial fill, update quantity


    def update_order_quantity(self, order):
        """Update the quantity of an order without removing it."""
        # Locate the correct price node
        if order.side == "BUY":
            price_node = self.bids.insertPrice(order.price)
        else:
            price_node = self.asks.insertPrice(order.price)

        # Traverse FIFO queue to update the order's quantity
        current = price_node.orders.head
        while current:
            if current.orderId == order.orderId:
                current.quantity = order.quantity  # Update quantity in FIFO queue
                return
            current = current.next


    def cancelOrder(self, orderId, check_price_level=False):
        """Cancel an order and remove the price level if empty."""
        if orderId in self.orders:
            order = self.orders[orderId]

            # Identify whether it's a BUY or SELL order
            if order.side == "BUY":
                price_node = self.bids.insertPrice(order.price)
            else:
                price_node = self.asks.insertPrice(order.price)

            # Remove the order from the FIFO queue
            price_node.orders.removeOrder(order)
            del self.orders[orderId]

            # Check if the price level is empty
            if check_price_level:
                self.check_price_level(order.side, order.price)

            print(f"Order {orderId} cancelled")

    
    def check_price_level(self, side, price):
        """Remove the price level from the skip list if it's empty."""
        if side == "BUY":
            price_node = self.bids.insertPrice(price)
            if price_node.orders.size == 0:
                self.bids.removePriceLevel(price)
                print(f"Price level {price} removed from BUY book")
        else:
            price_node = self.asks.insertPrice(price)
            if price_node.orders.size == 0:
                self.asks.removePriceLevel(price)
                print(f"Price level {price} removed from SELL book")


    def matchOrder(self, order):
        """Match limit orders with partial fills, using FIFO logic."""

        # 🔹 BUY Order Logic
        if order.side == "BUY":
            while order.quantity > 0:
                best_ask_price = self.get_best_ask()
                # Exit if no matching SELL orders
                if best_ask_price is None or best_ask_price > order.price:
                    # No match found - add order to the book
                    self.add_limit_order(order)
                    return

                ask_node = self.asks.head.forward[0]
                matched = False  # Track if the order is matched

                while ask_node and ask_node.price <= order.price:
                    if ask_node.orders.size == 0:
                        break

                    with ask_node.lock:
                        ask_orders = ask_node.orders
                        while order.quantity > 0 and ask_orders.size > 0:
                            match_order = ask_orders.getOldestOrder()
                            trade_qty = min(order.quantity, match_order.quantity)
                            self.execute_trade(order, match_order, trade_qty)
                            matched = True

                            if order.quantity == 0:
                                break

                        if ask_orders.size == 0:
                            ask_node = ask_node.forward[0]
                        else:
                            break

                    if order.quantity == 0 or ask_node is None:
                        break

                # If no match found, add order to the book
                if not matched and order.quantity > 0:
                    self.add_limit_order(order)
                    return

        # 🔹 SELL Order Logic
        else:
            while order.quantity > 0:
                best_bid_price = self.get_best_bid()
                # Exit if no matching BUY orders
                if best_bid_price is None or best_bid_price < order.price:
                    # No match found - add order to the book
                    self.add_limit_order(order)
                    return

                bid_node = self.bids.head.forward[0]
                matched = False  # Track if the order is matched

                while bid_node and bid_node.price >= order.price:
                    if bid_node.orders.size == 0:
                        break

                    with bid_node.lock:
                        bid_orders = bid_node.orders
                        while order.quantity > 0 and bid_orders.size > 0:
                            match_order = bid_orders.getOldestOrder()
                            trade_qty = min(order.quantity, match_order.quantity)
                            self.execute_trade(order, match_order, trade_qty)
                            matched = True

                            if order.quantity == 0:
                                break

                        if bid_orders.size == 0:
                            bid_node = bid_node.forward[0]
                        else:
                            break

                    if order.quantity == 0 or bid_node is None:
                        break

                # If no match found, add order to the book
                if not matched and order.quantity > 0:
                    self.add_limit_order(order)
                    return

        # If the order is partially filled, add the remaining volume to the book
        if order.quantity > 0 and order.orderId not in self.orders:
            self.add_limit_order(order)

    def matchAllOrders(self):
        """Continuously match orders until no valid cross exists, with thread safety."""
        while True:
            best_bid_price = self.get_best_bid()
            best_ask_price = self.get_best_ask()

            # Break if no cross exists
            if best_bid_price is None or best_ask_price is None or best_bid_price < best_ask_price:
                break

            # Get the order nodes
            bid_node = self.bids.insertPrice(best_bid_price)
            ask_node = self.asks.insertPrice(best_ask_price)

            # Match FIFO orders at the best price
            while bid_node.orders.size > 0 and ask_node.orders.size > 0:
                bid_order = bid_node.orders.getOldestOrder()
                ask_order = ask_node.orders.getOldestOrder()

                # Match orders with partial fills
                trade_qty = min(bid_order.quantity, ask_order.quantity)
                self.execute_trade(bid_order, ask_order, trade_qty)

                if bid_node.orders.size == 0:
                    self.check_price_level("BUY", best_bid_price)

                if ask_node.orders.size == 0:
                    self.check_price_level("SELL", best_ask_price)

# multi security OrderBook, which basically creates instances of orderbooks for the securities
class MultiSecurityOrderBook:
    def __init__(self):
        """Initialize order books for AAPL, TSLA, and MSFT."""
        # creating instances, using a dictionary for each stock's orderbooks
        self.order_books = {
            "AAPL": OrderBook(),
            "TSLA": OrderBook(),
            "MSFT": OrderBook()
        }

    def get_or_create_order_book(self, symbol):
        """Get the order book for a specific security or return None if it doesn't exist."""
        return self.order_books.get(symbol, None)

    def add_order(self, symbol, order):
        """Add order to the specific order book of a security if it exists."""
        order_book = self.get_or_create_order_book(symbol)
        if order_book:
            order_book.add_limit_order(order)
            order_book.matchAllOrders()
            return f"Order added to {symbol}"
        else:
            return f"Error: {symbol} is not a valid security"

    def get_order_book(self, symbol):
        """Return the order book for a given security or None if it doesn't exist."""
        return self.order_books.get(symbol, None)

    def list_all_securities(self):
        """List all available securities."""
        return list(self.order_books.keys())


        
'''
Dunder main function, so that if you import orderbook.py in your test file, 
it won't execute code.
'''
if __name__ == "__main__":
    print("Order Book Module Loaded. Run tests using `python -m unittest test_orderbook.py`")
