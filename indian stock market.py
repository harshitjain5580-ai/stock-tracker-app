import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import threading

# Use a dark style for matplotlib
plt.style.use("dark_background")  # built-in dark theme [web:60][web:63]


class SimpleStockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Indian Stock Tracker (NSE/BSE)")
        self.root.geometry("950x650")
        self.root.configure(bg="#000000")  # pure black background [web:54]

        # default exchange: NSE (.NS)
        self.default_exchange = ".NS"

        # Colors
        self.bg_main = "#000000"       # main background
        self.bg_card = "#111111"       # card-like panel
        self.bg_button = "#222222"     # buttons
        self.bg_button_active = "#333333"
        self.bg_entry = "#181818"
        self.fg_text = "#FFFFFF"
        self.fg_muted = "#AAAAAA"
        self.accent = "#00E676"        # neon green accent

        # Title
        title_frame = tk.Frame(root, bg=self.bg_main)
        title_frame.pack(pady=15)

        tk.Label(
            title_frame,
            text="Indian Stock Tracker",
            font=("Segoe UI", 22, "bold"),
            bg=self.bg_main,
            fg=self.accent
        ).pack()

        tk.Label(
            title_frame,
            text="NSE / BSE (powered by Yahoo Finance)",
            font=("Segoe UI", 10),
            bg=self.bg_main,
            fg=self.fg_muted
        ).pack(pady=(5, 0))

        # Search Box
        search_frame = tk.Frame(root, bg=self.bg_main)
        search_frame.pack(pady=15)

        self.entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 13),
            width=20,
            bd=0,
            relief="flat",
            bg=self.bg_entry,
            fg=self.fg_text,
            insertbackground=self.fg_text
        )
        self.entry.pack(side=tk.LEFT, padx=(0, 8), ipady=6)
        self.entry.bind('<Return>', lambda e: self.search())
        self.entry.focus()

        self.btn = tk.Button(
            search_frame,
            text="Search",
            font=("Segoe UI", 12, "bold"),
            bg=self.bg_button,
            fg=self.fg_text,
            activebackground=self.bg_button_active,
            activeforeground=self.fg_text,
            bd=0,
            relief="flat",
            padx=20,
            pady=4,
            cursor="hand2",
            command=self.search
        )
        self.btn.pack(side=tk.LEFT)

        # Quick buttons (NSE symbols)
        quick_frame = tk.Frame(root, bg=self.bg_main)
        quick_frame.pack(pady=5)

        stocks = ["RELIANCE", "HDFCBANK", "TCS", "ICICIBANK", "SBIN"]
        for s in stocks:
            tk.Button(
                quick_frame,
                text=s,
                font=("Segoe UI", 9),
                bg=self.bg_button,
                fg=self.fg_muted,
                activebackground=self.bg_button_active,
                activeforeground=self.fg_text,
                bd=0,
                relief="flat",
                padx=12,
                pady=4,
                cursor="hand2",
                command=lambda x=s: self.quick(x)
            ).pack(side=tk.LEFT, padx=4)

        # Info display
        self.info = tk.Label(
            root,
            text="Type an NSE symbol like TCS, RELIANCE, SBIN, etc.",
            font=("Segoe UI", 13),
            bg=self.bg_main,
            fg=self.fg_muted
        )
        self.info.pack(pady=10)

        # Graph "card"
        outer_graph_frame = tk.Frame(root, bg=self.bg_main)
        outer_graph_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)

        self.graph_frame = tk.Frame(outer_graph_frame, bg=self.bg_card, bd=0, relief="flat")
        self.graph_frame.pack(fill=tk.BOTH, expand=True)

    def normalize_ticker(self, symbol: str) -> str:
        symbol = symbol.upper().strip()
        if symbol.endswith(".NS") or symbol.endswith(".BO"):
            return symbol
        return symbol + self.default_exchange

    def quick(self, ticker):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, ticker)
        self.search()

    def search(self):
        raw = self.entry.get().strip()
        if not raw:
            messagebox.showwarning("Error", "Please enter a stock symbol")
            return

        ticker = self.normalize_ticker(raw)

        self.btn.config(state=tk.DISABLED, text="Loading...")
        self.info.config(text="Loading...", fg=self.fg_muted)

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

            self.root.after(
                0,
                lambda: self.show(ticker, data, price, change, percent)
            )

        except Exception as e:
            self.root.after(0, lambda: self.error(str(e)))

    def error(self, msg):
        self.info.config(text="", fg=self.fg_muted)
        messagebox.showerror("Error", msg)
        self.btn.config(state=tk.NORMAL, text="Search")

    def show(self, ticker, data, price, change, percent):
        # Clear graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        display_symbol = ticker.replace(".NS", "").replace(".BO", "")

        color = self.accent if change >= 0 else "#FF5252"
        symbol = "▲" if change >= 0 else "▼"
        self.info.config(
            text=f"{display_symbol}   ₹{price:.2f}   {symbol} {change:.2f} ({percent:+.1f}%)",
            fg=color
        )

        # Dark themed chart
        fig = Figure(figsize=(8.8, 3.8), dpi=100)
        ax = fig.add_subplot(111)

        # Set axis facecolor to match card
        ax.set_facecolor("#000000")
        fig.patch.set_facecolor("#000000")

        ax.plot(
            data.index,
            data['Close'],
            linewidth=2.2,
            color="#42A5F5"
        )
        ax.scatter(
            data.index[-1],
            price,
            color=color,
            s=80,
            zorder=5
        )
        ax.set_title(
            f'{display_symbol} - Last 6 Months',
            fontsize=12,
            pad=10,
            color=self.fg_text
        )
        ax.set_ylabel('Price (₹)', fontsize=10, color=self.fg_muted)
        ax.tick_params(colors=self.fg_muted)
        ax.grid(True, alpha=0.25, color="#444444")

        fig.autofmt_xdate()
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.btn.config(state=tk.NORMAL, text="Search")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleStockApp(root)
    root.mainloop()
