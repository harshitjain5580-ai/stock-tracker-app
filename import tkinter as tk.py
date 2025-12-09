import tkinter as tk
from tkinter import messagebox
from datetime import datetime, timedelta
import threading

import yfinance as yf
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


class StockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Stock Tracker")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        # DARK COLORS
        self.bg_main = "#000000"     # pure black background
        self.bg_panel = "#111111"    # slightly lighter black
        self.fg_text = "#ffffff"     # white text

        self.root.configure(bg=self.bg_main)

        # Title
        title = tk.Label(
            root,
            text="Stock Tracker",
            font=("Segoe UI", 20, "bold"),
            bg=self.bg_main,
            fg=self.fg_text
        )
        title.pack(pady=10)

        # Search frame
        self.search_frame = tk.Frame(root, bg=self.bg_panel)
        self.search_frame.pack(pady=10)

        self.entry = tk.Entry(
            self.search_frame,
            font=("Segoe UI", 12),
            bg="#222222",
            fg=self.fg_text,
            insertbackground=self.fg_text,
            relief="flat",
            width=15
        )
        self.entry.grid(row=0, column=0, padx=5)
        self.entry.focus()
        self.entry.bind("<Return>", lambda e: self.search())

        self.search_button = tk.Button(
            self.search_frame,
            text="Search",
            command=self.search,
            bg="#333333",
            fg=self.fg_text,
            activebackground="#444444",
            activeforeground=self.fg_text,
            relief="flat"
        )
        self.search_button.grid(row=0, column=1, padx=5)

        # Quick buttons
        quick_frame = tk.Frame(self.search_frame, bg=self.bg_panel)
        quick_frame.grid(row=0, column=2, padx=10)
        for sym in ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN"]:
            tk.Button(
                quick_frame,
                text=sym,
                command=lambda s=sym: self.quick(s),
                bg="#222222",
                fg=self.fg_text,
                activebackground="#444444",
                activeforeground=self.fg_text,
                relief="flat"
            ).pack(side="left", padx=2)

        # Info label
        self.info_label = tk.Label(
            root,
            text="Enter a symbol to begin",
            font=("Segoe UI", 11),
            bg=self.bg_main,
            fg="#cccccc"
        )
        self.info_label.pack(pady=5)

        # Graph frame
        self.graph_frame = tk.Frame(root, bg=self.bg_main)
        self.graph_frame.pack(fill="both", expand=True, padx=10, pady=10)

        self.canvas = None

    def quick(self, ticker):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, ticker)
        self.search()

    def search(self):
        ticker = self.entry.get().strip().upper()
        if not ticker:
            messagebox.showwarning("Missing symbol", "Please enter a stock symbol.")
            return

        self.search_button.config(text="Loading…", state="disabled", bg="#222222")
        self.info_label.config(text=f"Loading data for {ticker} …", fg="#cccccc")

        t = threading.Thread(target=self.get_data, args=(ticker,), daemon=True)
        t.start()

    def get_data(self, ticker):
        try:
            stock = yf.Ticker(ticker)
            end = datetime.now()
            start = end - timedelta(days=180)

            data = stock.history(start=start, end=end)
            if data.empty:
                data = stock.history(period="6mo")

            if data.empty:
                self.root.after(0, lambda: self.error(f"No data for '{ticker}'"))
                return

            price = float(data["Close"].iloc[-1])
            old_price = float(data["Close"].iloc[0])
            change = price - old_price
            percent = (change / old_price) * 100 if old_price != 0 else 0.0

            self.root.after(0, lambda: self.show(ticker, data, price, change, percent))

        except Exception as e:
            self.root.after(0, lambda: self.error(str(e)))

    def error(self, msg):
        self.info_label.config(text="", fg="#cccccc")
        messagebox.showerror("Error", msg)
        self.search_button.config(text="Search", state="normal", bg="#333333")

    def show(self, ticker, data, price, change, percent):
        for w in self.graph_frame.winfo_children():
            w.destroy()

        if change >= 0:
            arrow = "▲"
            color = "#22c55e"
            sign = "+"
        else:
            arrow = "▼"
            color = "#f97316"
            sign = ""

        self.info_label.config(
            text=f"{ticker}  {arrow}  {price:.2f}  ({sign}{change:.2f}, {sign}{percent:.2f}%)",
            fg=color
        )

        fig = Figure(figsize=(7.5, 4.5), dpi=100)
        fig.patch.set_facecolor(self.bg_main)
        ax = fig.add_subplot(111)
        ax.set_facecolor("#050505")

        ax.plot(data.index, data["Close"], color="#60a5fa", linewidth=1.8)
        ax.scatter(data.index[-1], data["Close"].iloc[-1], color="#f97316", s=35, zorder=3)

        ax.set_title(f"{ticker} - Last 6 Months", color="#ffffff", fontsize=11)
        ax.set_ylabel("Price", color="#cccccc")
        ax.tick_params(colors="#cccccc")
        ax.grid(True, linestyle="--", linewidth=0.4, color="#222222", alpha=0.7)

        for spine in ax.spines.values():
            spine.set_color("#444444")

        fig.autofmt_xdate()

        self.canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.search_button.config(text="Search", state="normal", bg="#333333")


if __name__ == "__main__":
    root = tk.Tk()
    app = StockApp(root)
    root.mainloop()
