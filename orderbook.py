'''
The orderbook structure is as such:
OrderSide
Price (levels)
Quantity
Timestamp
MarketDepth
Total Traded Volume
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
import time, random, itertools

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
        if order == self.head and order == self.tail:  # If it's the only order
            self.head = self.tail = None
        elif order == self.head:  # Removing head
            self.head = order.next
            self.head.prev = None
        elif order == self.tail:  # Removing tail
            self.tail = order.prev
            self.tail.next = None
        else:  # Removing from the middle
            order.prev.next = order.next
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

class SkipList:
    def __init__(self, max_level = 16, p = 0.5):
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
        ''' Insert a new prive level into the skiplist. '''
        update = [None] * self.max_level
        current = self.head

        for i in reversed(range(self.max_level)):
            while current.forward[i] and current.forward[i].price < price:
                current = current.forward[i]
            update[i] = current

        if current.forward[0] and current.forward[0].price == price:
            return current.forward[0]  # Price already exists

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
    
'''
Create an OrderBook using a hashset, for efficient lookup addition, deletion. 
O(1) order retrieval.
'''
class OrderBook:
    def __init__(self):
        self.skiplist = SkipList()
        self.orders = {} # create a hashset for orderId lookup.

    def get_best_bid(self):
        """ Get the best bid price using SkipList """
        return self.skiplist.getBestBid()

    def get_best_ask(self):
        """ Get the best ask price using SkipList """
        return self.skiplist.getBestAsk()

    def addOrder(self, order):
        ''' Add an order to the OrderBook. '''
        price_node = self.skiplist.insertPrice(order.price) # instantiate a node for the skiplist
        price_node.orders.addOrder(order) # like a vector pushback function call
        self.orders[order.orderId] = order  # Store in HashMap

    def cancelOrder(self, orderId):
        ''' Remove an order and clean up price levels. '''
        if orderId in self.orders:
            order = self.orders[orderId]
            price_node = self.skiplist.insertPrice(order.price)

            # Remove order
            price_node.orders.removeOrder(order)
            del self.orders[orderId]

            # If no more orders exist at this price, remove the price level
            if price_node.orders.size == 0:
                self.removePriceLevel(order.price)

    def removePriceLevel(self, price):
        ''' Removes a price level from the Skip List '''
        update = [None] * self.skiplist.max_level
        current = self.skiplist.head

        for i in reversed(range(self.skiplist.max_level)):
            while current.forward[i] and current.forward[i].price < price:
                current = current.forward[i]
            update[i] = current

        if current.forward[0] and current.forward[0].price == price:
            for i in range(len(current.forward[0].forward)):
                update[i].forward[i] = current.forward[0].forward[i]


    def match_orders(self):
        """ 
        Match orders with:
            - Partial fills (across multiple orders in FIFO order)
            - Limit orders
            - Market orders
            - Stop orders
        """

        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()

        if best_bid is None or best_ask is None:
            return  # No trades possible

        # 1. Convert STOP Orders to Market Orders if Triggered
        """ Convert Stop Orders to Market Orders when triggered """
        best_bid = self.get_best_bid()
        best_ask = self.get_best_ask()

        for order in list(self.orders.values()):
            if order.orderType == "STOP":
                if order.side == "BUY" and best_ask and order.price <= best_ask:
                    print(f"Stop BUY Order {order.orderId} triggered at {order.price}, converting to MARKET")
                    order.orderType = "MARKET"
                elif order.side == "SELL" and best_bid and order.price >= best_bid:
                    print(f"Stop SELL Order {order.orderId} triggered at {order.price}, converting to MARKET")
                    order.orderType = "MARKET"

        # 2. Execute MARKET Orders Immediately at Best Price (with partial fills)
        for order in list(self.orders.values()):
            if order.orderType == "MARKET":
                """ 
                Execute Market Orders:
                    - Sweep through multiple price levels until fully filled
                    - Execute partial fills across multiple orders
                """
                while order.quantity > 0:
                    if order.side == "BUY":
                        best_ask = self.get_best_ask()
                        if best_ask is None:
                            print(f"Market BUY Order {order.orderId} partially filled, remaining: {order.quantity}")
                            break
                        match_orders = self.skiplist.insertPrice(best_ask).orders
                    else:
                        best_bid = self.get_best_bid()
                        if best_bid is None:
                            print(f"Market SELL Order {order.orderId} partially filled, remaining: {order.quantity}")
                            break
                        match_orders = self.skiplist.insertPrice(best_bid).orders

                    # Match against FIFO orders until fully filled or no liquidity
                    while order.quantity > 0 and match_orders.size > 0:
                        match_order = match_orders.getOldestOrder()
                        trade_qty = min(order.quantity, match_order.quantity)
                        print(f"Market Order Executed: {trade_qty} @ {match_order.price}")

                        # Update quantities
                        order.quantity -= trade_qty
                        match_order.quantity -= trade_qty

                        # Remove fully filled orders
                        if match_order.quantity == 0:
                            match_orders.removeOrder(match_order)
                            self.cancelOrder(match_order.orderId)

                    # Remove the Market Order if fully executed
                    if order.quantity == 0:
                        self.cancelOrder(order.orderId)


                # If the order is fully executed, remove it
                if order.quantity == 0:
                    self.cancelOrder(order.orderId)

        # 3. Execute LIMIT Orders Only at Set Price or Better (Partial Fills + FIFO)
        """ 
        Execute Limit Orders:
            - Fill orders at the limit price or better
            - Execute partial fills across multiple orders
        """
        if order.side == "BUY":
            while order.quantity > 0:
                best_ask = self.get_best_ask()
                if best_ask is None or best_ask > order.price:
                    break
                ask_orders = self.skiplist.insertPrice(best_ask).orders

                # Match until order is fully filled or no more orders available
                while order.quantity > 0 and ask_orders.size > 0:
                    match_order = ask_orders.getOldestOrder()
                    trade_qty = min(order.quantity, match_order.quantity)
                    print(f"Limit Order Executed: {trade_qty} @ {best_ask}")

                    # Update quantities
                    order.quantity -= trade_qty
                    match_order.quantity -= trade_qty

                    # Remove fully filled orders
                    if match_order.quantity == 0:
                        ask_orders.removeOrder(match_order)
                        self.cancelOrder(match_order.orderId)

                if order.quantity == 0:
                    self.cancelOrder(order.orderId)
        else:
            while order.quantity > 0:
                best_bid = self.get_best_bid()
                if best_bid is None or best_bid < order.price:
                    break
                bid_orders = self.skiplist.insertPrice(best_bid).orders

                # Match until order is fully filled or no more orders available
                while order.quantity > 0 and bid_orders.size > 0:
                    match_order = bid_orders.getOldestOrder()
                    trade_qty = min(order.quantity, match_order.quantity)
                    print(f"Limit Order Executed: {trade_qty} @ {best_bid}")

                    # Update quantities
                    order.quantity -= trade_qty
                    match_order.quantity -= trade_qty

                    # Remove fully filled orders
                    if match_order.quantity == 0:
                        bid_orders.removeOrder(match_order)
                        self.cancelOrder(match_order.orderId)

                if order.quantity == 0:
                    self.cancelOrder(order.orderId)

'''
Dunder main function, so that if you import orderbook.py in your test file, 
it won't execute code.
'''
if __name__ == "__main__":
    print("Order Book Module Loaded. Run tests using `python -m unittest test_orderbook.py`")
