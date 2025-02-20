import threading
import tkinter as tk
from orderbook import Order, OrderBook
from orderbook_gui import OrderBookGUI
import random
import time

def buy_bot(order_book, gui):
    """Continuously places random BUY orders and matches them."""
    while True:
        with order_book.lock:  # ✅ Lock when adding an order
            price = random.uniform(30, 50)
            quantity = random.randint(1, 10)
            order_book.add_limit_order(Order(orderSide="BUY", price=price, quantity=quantity, orderType="LIMIT"))
            order_book.matchAllOrders()

        # ✅ Use after() to update GUI
        if gui.root.winfo_exists():
            gui.root.after(0, gui.update_display)

        time.sleep(random.uniform(0.5, 1.5))


def sell_bot(order_book, gui):
    """Continuously places random SELL orders and matches them."""
    while True:
        with order_book.lock:  # ✅ Lock when adding an order
            price = random.uniform(30, 50)
            quantity = random.randint(1, 10)
            order_book.add_limit_order(Order(orderSide="SELL", price=price, quantity=quantity, orderType="LIMIT"))
            order_book.matchAllOrders()

        # ✅ Use after() to update GUI
        if gui.root.winfo_exists():
            gui.root.after(0, gui.update_display)

        time.sleep(random.uniform(0.5, 1.5))


if __name__ == "__main__":
    # ✅ Initialize Order Book
    order_book = OrderBook()

    # ✅ Start GUI
    root = tk.Tk()
    app = OrderBookGUI(root, order_book)  # ✅ Pass the shared order book

    # ✅ Start BUY Bot (Thread)
    buy_bot_thread = threading.Thread(target=buy_bot, args=(order_book, app))
    buy_bot_thread.daemon = True  # ✅ Allows the program to exit when GUI is closed
    buy_bot_thread.start()

    # ✅ Start SELL Bot (Thread)
    sell_bot_thread = threading.Thread(target=sell_bot, args=(order_book, app))
    sell_bot_thread.daemon = True  # ✅ Allows the program to exit when GUI is closed
    sell_bot_thread.start()

    # ✅ Run GUI
    root.mainloop()
