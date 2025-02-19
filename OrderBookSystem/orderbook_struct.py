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
        self.head.forward = [None]*self.max_level

    def randomLevel(self):
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