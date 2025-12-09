import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import threading

class SimpleStockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Tracker")
        self.root.geometry("900x600")
        self.root.configure(bg="white")
        
        # Title
        tk.Label(
            root, 
            text="Stock Tracker", 
            font=("Arial", 20, "bold"),
            bg="white",
            fg="#333"
        ).pack(pady=20)
        
        # Search Box
        search_frame = tk.Frame(root, bg="white")
        search_frame.pack(pady=10)
        
        self.entry = tk.Entry(
            search_frame, 
            font=("Arial", 14), 
            width=20,
            bd=2
        )
        self.entry.pack(side=tk.LEFT, padx=5)
        self.entry.bind('<Return>', lambda e: self.search())
        self.entry.focus()
        
        self.btn = tk.Button(
            search_frame,
            text="Search",
            font=("Arial", 14),
            bg="#4CAF50",
            fg="white",
            padx=20,
            command=self.search
        )
        self.btn.pack(side=tk.LEFT)
        
        # Quick buttons
        quick_frame = tk.Frame(root, bg="white")
        quick_frame.pack(pady=10)
        
        stocks = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN"]
        for s in stocks:
            tk.Button(
                quick_frame,
                text=s,
                font=("Arial", 10),
                bg="#f0f0f0",
                padx=15,
                pady=5,
                command=lambda x=s: self.quick(x)
            ).pack(side=tk.LEFT, padx=5)
        
        # Info display
        self.info = tk.Label(
            root,
            text="",
            font=("Arial", 16),
            bg="white",
            fg="#333"
        )
        self.info.pack(pady=10)
        
        # Graph area
        self.graph_frame = tk.Frame(root, bg="white")
        self.graph_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
    def quick(self, ticker):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, ticker)
        self.search()
    
    def search(self):
        ticker = self.entry.get().upper().strip()
        if not ticker:
            messagebox.showwarning("Error", "Please enter a stock symbol")
            return
        
        self.btn.config(state=tk.DISABLED, text="Loading...")
        self.info.config(text="Loading...")
        
        thread = threading.Thread(target=self.get_data, args=(ticker,))
        thread.daemon = True
        thread.start()
    
    def get_data(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            end = datetime.now()
            start = end - timedelta(days=180)
            data = stock.history(start=start, end=end)
            
            if data.empty:
                data = stock.history(period="6mo")
            
            if data.empty:
                self.root.after(0, lambda: self.error(f"'{ticker}' not found"))
                return
            
            price = data['Close'].iloc[-1]
            old_price = data['Close'].iloc[0]
            change = price - old_price
            percent = (change / old_price) * 100
            
            self.root.after(0, lambda: self.show(ticker, data, price, change, percent))
            
        except Exception as e:
            self.root.after(0, lambda: self.error(str(e)))
    
    def error(self, msg):
        self.info.config(text="")
        messagebox.showerror("Error", msg)
        self.btn.config(state=tk.NORMAL, text="Search")
    
    def show(self, ticker, data, price, change, percent):
        # Clear graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # Show info
        color = "green" if change >= 0 else "red"
        symbol = "▲" if change >= 0 else "▼"
        self.info.config(
            text=f"{ticker}   ${price:.2f}   {symbol} {change:.2f} ({percent:+.1f}%)",
            fg=color
        )
        
        # Draw graph
        fig = Figure(figsize=(8, 3.5), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(data.index, data['Close'], linewidth=2, color='#2196F3')
        ax.scatter(data.index[-1], price, color='red', s=80, zorder=5)
        ax.set_title(f'{ticker} - Last 6 Months', fontsize=12, pad=10)
        ax.set_ylabel('Price ($)', fontsize=10)
        ax.grid(True, alpha=0.3)
        fig.autofmt_xdate()
        fig.tight_layout()
        
        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.btn.config(state=tk.NORMAL, text="Search")

root = tk.Tk()
app = SimpleStockApp(root)
root.mainloop()
