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