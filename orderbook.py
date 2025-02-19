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
        self.prev = None # represents the newest order with FIFO logic
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
        ''' Remove order from anywhere in the list. '''
        # simple pointer updation after node removals
        if order.prev:
            order.prev.next = order.next
        if order.next:
            order,next.prev = order.prev
        if order == self.head:
            self.head = order.next
        if order ==self.tail:
            self.tail = order.prev
        # implement complete order removal
        order.next = order.prev = None
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
    def __init__(self, price, OrderList):
        self.price = price
        self.orders = OrderList
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

        new_level = self._random_level()
        new_node = SkipListNode(price)
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
    
    def getbestBid(self):
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

    def addOrder(self, order):
        ''' Add an order to the OrderBook. '''
        price_node = self.skip_list.insert_price(order.price) # instantiate a node for the skiplist
        price_node.orders.add_order(order) # like a vector pushback function call
        self.orders[order.orderId] = order  # Store in HashMap

    def cancelOrder(self, orderId):
        ''' Remove an order with a given referrence orderId. '''
        if orderId in self.orders: # if the order actually exists in the set. o(1) lookup
            order = self.orders[orderId]
            price_node = self.skip_list.insert_price(order.price)
            price_node.orders.remove_order(order)
            del self.orders[orderId]  # Remove from HashMap

    def matchOrders(self):
        """ Match orders while considering order types (Limit, Market, Stop). """
    
        best_bid = self.skip_list.get_best_bid()
        best_ask = self.skip_list.get_best_ask()

        # 1. Market Orders: Execute Immediately at Best Price Available
        for order in list(self.orders.values()):  # Loop through all active orders
            if order.order_type == "MARKET":
                if order.side == "BUY":
                    if best_ask is None:
                        print(f"Market BUY order {order.orderId} rejected: No available sellers")
                        continue
                    match_order = self.orders[best_ask]
                else:  # SELL Market Order
                    if best_bid is None:
                        print(f"Market SELL order {order.orderId} rejected: No available buyers")
                        continue
                    match_order = self.orders[best_bid]

                # Execute Market Order at best price
                trade_qty = min(order.quantity, match_order.quantity)
                print(f"Market Order Executed: {trade_qty} @ {match_order.price}")

                # Update order quantities or remove fully filled orders
                order.quantity -= trade_qty
                match_order.quantity -= trade_qty

                if order.quantity == 0:
                    self.cancel_order(order.orderId)
                if match_order.quantity == 0:
                    self.cancel_order(match_order.orderId)

        # 2. Limit Orders: Execute Only at Set Price or Better
        if best_bid and best_ask and best_bid >= best_ask:
            bid_order = self.orders[best_bid]
            ask_order = self.orders[best_ask]

            trade_qty = min(bid_order.quantity, ask_order.quantity)
            print(f"Limit Order Executed: {trade_qty} @ {best_bid}")

            bid_order.quantity -= trade_qty
            ask_order.quantity -= trade_qty

            if bid_order.quantity == 0:
                self.cancel_order(bid_order.orderId)
            if ask_order.quantity == 0:
                self.cancel_order(ask_order.orderId)

        # 3. Stop Orders: Convert to Market Orders When Triggered
        for order in list(self.orders.values()):
            if order.order_type == "STOP":
                if order.side == "BUY" and best_ask and order.price <= best_ask:
                    print(f"Stop BUY triggered @ {order.price}, converting to MARKET order")
                    order.order_type = "MARKET"
                elif order.side == "SELL" and best_bid and order.price >= best_bid:
                    print(f"Stop SELL triggered @ {order.price}, converting to MARKET order")
                    order.order_type = "MARKET"