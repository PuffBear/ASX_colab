'''
An order matching engine (OME) is a software system that matches buy and sell orders 
from market participants to facilitate the execution of trades.

Attributes of the OME:
- Multi-threaded OME
- Matching Algo = Price,Time priority
- OrderExecution Process = Validate order; Check available liquidity; Match against 
existing orders; Execute trade & update book.

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