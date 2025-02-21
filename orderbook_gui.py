import tkinter as tk
from tkinter import ttk
from orderbook import Order, OrderBook, MultiSecurityOrderBook

# matplotlib 
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time

class OrderBookGUI:
    def __init__(self, root, multi_security_order_book):
        self.multi_security_order_book = multi_security_order_book
        self.root = root
        self.root.title("Stock Xchange")

        # Input fields
        self.side_var = tk.StringVar(value="BUY")
        self.price_var = tk.StringVar()
        self.quantity_var = tk.StringVar()

        self.ltp_data = [] # stores ltp values
        self.ltp_times = [] # stores timestamps

        self.tradde_id_counter = 1 # track

        self.create_widgets()

    def create_widgets(self):
        # Input Frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=5)

        # Security Dropdown
        tk.Label(input_frame, text="Security:").grid(row=0, column=0, padx=5, pady=5)
        self.security_var = tk.StringVar(value="AAPL")
        self.security_entry = ttk.Combobox(input_frame, textvariable=self.security_var, 
                                        values=["AAPL", "MSFT", "TSLA"], width=10)
        self.security_entry.grid(row=0, column=1, padx=5, pady=5)
        self.security_entry.bind("<<ComboboxSelected>>", lambda event: self.update_display())  # ✅ Update on selection

        # Side Dropdown
        tk.Label(input_frame, text="Side (BUY/SELL):").grid(row=0, column=2, padx=5, pady=5)
        self.side_entry = ttk.Combobox(input_frame, textvariable=self.side_var, values=["BUY", "SELL"], width=10)
        self.side_entry.grid(row=0, column=3, padx=5, pady=5)

        # Price Input
        tk.Label(input_frame, text="Price:").grid(row=0, column=4, padx=5, pady=5)
        self.price_entry = tk.Entry(input_frame, textvariable=self.price_var, width=10)
        self.price_entry.grid(row=0, column=5, padx=5, pady=5)

        # Quantity Input
        tk.Label(input_frame, text="Quantity:").grid(row=0, column=6, padx=5, pady=5)
        self.quantity_entry = tk.Entry(input_frame, textvariable=self.quantity_var, width=10)
        self.quantity_entry.grid(row=0, column=7, padx=5, pady=5)

        # Add Order Button
        self.add_button = tk.Button(input_frame, text="Add Order", command=self.add_order)
        self.add_button.grid(row=0, column=8, padx=10, pady=5)

        # Tables for Bids and Asks
        self.bid_tree = ttk.Treeview(self.root, columns=("Price", "Quantity", "Order ID"), show="headings")
        self.bid_tree.heading("Price", text="Price")
        self.bid_tree.heading("Quantity", text="Quantity")
        self.bid_tree.heading("Order ID", text="Order ID")
        self.bid_tree.pack(side=tk.LEFT, padx=10, pady=10)

        self.ask_tree = ttk.Treeview(self.root, columns=("Price", "Quantity", "Order ID"), show="headings")
        self.ask_tree.heading("Price", text="Price")
        self.ask_tree.heading("Quantity", text="Quantity")
        self.ask_tree.heading("Order ID", text="Order ID")
        self.ask_tree.pack(side=tk.RIGHT, padx=10, pady=10)

        # LTP Label
        self.ltp_label = tk.Label(self.root, text="LTP: -")
        self.ltp_label.pack(pady=20)

        # LTP Chart
        self.fig = Figure(figsize=(6, 2), dpi=100)
        self.ax = self.fig.add_subplot(1, 1, 1)
        self.ax.set_title("LTP Trend")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price")

        # Embed the chart into Tkinter window
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.get_tk_widget().pack(pady=10)


    def add_order(self):
        """Add order manually from GUI."""
        # Get selected security
        symbol = self.security_var.get()
        side = self.side_var.get()
        price = float(self.price_var.get())
        quantity = int(self.quantity_var.get())

        order = Order(orderSide=side, price=price, quantity=quantity, orderType="LIMIT")
        self.multi_security_order_book.add_order(symbol, order)  # ✅ Route to correct security

        # Use after() for GUI update
        if self.root.winfo_exists():
            self.root.after(0, self.update_display)  # ✅ Display updates for the selected security


    def update_display(self):
        """Update the GUI tables and LTP label based on the selected security."""
        # Get the order book of the selected security
        symbol = self.security_var.get()
        order_book = self.multi_security_order_book.get_order_book(symbol)

        if order_book and self.root.winfo_exists():
            # Clear tables
            self.bid_tree.delete(*self.bid_tree.get_children())
            self.ask_tree.delete(*self.ask_tree.get_children())

            # ✅ Populate BIDS
            current = order_book.bids.head.forward[0]
            while current:
                for order in self.iterate_orders(current.orders.head):
                    self.bid_tree.insert("", "end", values=(order.price, order.quantity, order.orderId))
                current = current.forward[0] if current.forward else None

            # ✅ Populate ASKS
            current = order_book.asks.head.forward[0]
            while current:
                for order in self.iterate_orders(current.orders.head):
                    self.ask_tree.insert("", "end", values=(order.price, order.quantity, order.orderId))
                current = current.forward[0] if current.forward else None

            # ✅ Update LTP
            ltp = getattr(order_book, 'ltp', None)
            self.ltp_label.config(text=f"LTP: {ltp if ltp else '-'}")

            # ✅ Update LTP Chart if LTP exists
            if ltp:
                self.update_ltp_chart(symbol, ltp)


    def iterate_orders(self, head):
        current = head
        while current:
            yield current
            current = current.next

    # UPDATE LTP CHART
    def update_ltp_chart(self, symbol, price):
        """Update the LTP chart for the selected security."""
        if symbol not in self.ltp_data:
            self.ltp_data[symbol] = []
            self.ltp_times[symbol] = []

        # Append LTP Data
        self.ltp_data[symbol].append(price)
        self.ltp_times[symbol].append(time.strftime("%H:%M:%S"))

        # Keep Only Last 10 Trades
        if len(self.ltp_data[symbol]) > 10:
            self.ltp_data[symbol].pop(0)
            self.ltp_times[symbol].pop(0)

        # Update Chart
        self.ax.clear()
        self.ax.plot(self.ltp_times[symbol], self.ltp_data[symbol], marker='o', linestyle='-', color='cyan', label="LTP")
        self.ax.set_title(f"{symbol} - LTP Trend")
        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("Price")
        self.ax.legend()

        # Refresh Canvas
        self.canvas.draw()



if __name__ == "__main__":
    from orderbook import MultiSecurityOrderBook  # Import MultiSecurityOrderBook

    # Initialize Multi-Security Order Book
    multi_security_order_book = MultiSecurityOrderBook()

    # Start GUI 
    root = tk.Tk()
    app = OrderBookGUI(root, multi_security_order_book)  # Pass Multi-Security Order Book
    root.mainloop()
