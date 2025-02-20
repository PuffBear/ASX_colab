import tkinter as tk
from tkinter import ttk
from orderbook import Order, OrderBook

class OrderBookGUI:
    def __init__(self, root):
        self.order_book = OrderBook()
        self.root = root
        self.root.title("Stock Xchange")

        # Input fields
        self.side_var = tk.StringVar(value="BUY")
        self.price_var = tk.StringVar()
        self.quantity_var = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        # Input Frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=5)

        tk.Label(input_frame, text="Side (BUY/SELL):").grid(row=0, column=0)
        self.side_entry = ttk.Combobox(input_frame, textvariable=self.side_var, values=["BUY", "SELL"], width=10)
        self.side_entry.grid(row=0, column=1)

        tk.Label(input_frame, text="Price:").grid(row=0, column=2)
        self.price_entry = tk.Entry(input_frame, textvariable=self.price_var, width=10)
        self.price_entry.grid(row=0, column=3)

        tk.Label(input_frame, text="Quantity:").grid(row=0, column=4)
        self.quantity_entry = tk.Entry(input_frame, textvariable=self.quantity_var, width=10)
        self.quantity_entry.grid(row=0, column=5)

        self.add_button = tk.Button(input_frame, text="Add Order", command=self.add_order)
        self.add_button.grid(row=0, column=6)

        # Tables for Bids and Asks
        self.bid_tree = ttk.Treeview(self.root, columns=("Price", "Quantity", "Order ID"), show="headings")
        self.bid_tree.heading("Price", text="Price")
        self.bid_tree.heading("Quantity", text="Quantity")
        self.bid_tree.heading("Order ID", text="Order ID")
        self.bid_tree.pack(side=tk.LEFT, padx=10)

        self.ask_tree = ttk.Treeview(self.root, columns=("Price", "Quantity", "Order ID"), show="headings")
        self.ask_tree.heading("Price", text="Price")
        self.ask_tree.heading("Quantity", text="Quantity")
        self.ask_tree.heading("Order ID", text="Order ID")
        self.ask_tree.pack(side=tk.RIGHT, padx=10)

        # LTP Label
        self.ltp_label = tk.Label(self.root, text="LTP: -")
        self.ltp_label.pack(pady=5)

    def add_order(self):
        side = self.side_var.get()
        price = float(self.price_var.get())
        quantity = int(self.quantity_var.get())

        order = Order(orderSide=side, price=price, quantity=quantity, orderType="LIMIT")
        self.order_book.add_limit_order(order)
        self.order_book.matchAllOrders()

        self.update_display()

    def update_display(self):
        # Clear Trees
        self.bid_tree.delete(*self.bid_tree.get_children())
        self.ask_tree.delete(*self.ask_tree.get_children())

        # Populate Bids
        current = self.order_book.bids.head.forward[0]
        while current:
            for order in self.iterate_orders(current.orders.head):
                self.bid_tree.insert("", "end", values=(order.price, order.quantity, order.orderId))
            current = current.forward[0] if current.forward else None

        # Populate Asks
        current = self.order_book.asks.head.forward[0]
        while current:
            for order in self.iterate_orders(current.orders.head):
                self.ask_tree.insert("", "end", values=(order.price, order.quantity, order.orderId))
            current = current.forward[0] if current.forward else None

        # Update LTP
        ltp = getattr(self.order_book, 'ltp', None)
        self.ltp_label.config(text=f"LTP: {ltp if ltp else '-'}")

    def iterate_orders(self, head):
        current = head
        while current:
            yield current
            current = current.next


if __name__ == "__main__":
    root = tk.Tk()
    app = OrderBookGUI(root)
    root.mainloop()
