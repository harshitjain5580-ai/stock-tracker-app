import yfinance as yf
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import messagebox
import threading

# Dark style for matplotlib
plt.style.use("dark_background")


class SimpleStockApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Global Stock Tracker (India + USA)")
        self.root.geometry("1000x680")
        self.root.configure(bg="#000000")  # black background

        # default for Indian single-word tickers
        self.default_india_suffix = ".NS"

        # Colors
        self.bg_main = "#000000"
        self.bg_card = "#111111"
        self.bg_button = "#222222"
        self.bg_button_active = "#333333"
        self.bg_entry = "#181818"
        self.fg_text = "#FFFFFF"
        self.fg_muted = "#AAAAAA"
        self.accent_india = "#00E676"   # green
        self.accent_usa = "#42A5F5"     # blue

        # Track current region for styling text (India / US / Index)
        self.current_region = "INDEX"

        # Title
        title_frame = tk.Frame(root, bg=self.bg_main)
        title_frame.pack(pady=15)

        tk.Label(
            title_frame,
            text="Global Stock Tracker",
            font=("Segoe UI", 22, "bold"),
            bg=self.bg_main,
            fg=self.accent_usa
        ).pack()

        tk.Label(
            title_frame,
            text="Indian (NSE/BSE) + US Stocks + Major Indices",
            font=("Segoe UI", 10),
            bg=self.bg_main,
            fg=self.fg_muted
        ).pack(pady=(5, 0))

        # Region selector
        region_frame = tk.Frame(root, bg=self.bg_main)
        region_frame.pack(pady=(5, 0))

        tk.Label(
            region_frame,
            text="Market: ",
            font=("Segoe UI", 10),
            bg=self.bg_main,
            fg=self.fg_muted
        ).pack(side=tk.LEFT)

        self.region_var = tk.StringVar(value="INDIA")  # INDIA or USA

        tk.Radiobutton(
            region_frame,
            text="India (NSE/BSE)",
            variable=self.region_var,
            value="INDIA",
            font=("Segoe UI", 9),
            bg=self.bg_main,
            fg=self.fg_muted,
            selectcolor=self.bg_main,
            activebackground=self.bg_main,
            activeforeground=self.fg_text
        ).pack(side=tk.LEFT, padx=5)

        tk.Radiobutton(
            region_frame,
            text="USA",
            variable=self.region_var,
            value="USA",
            font=("Segoe UI", 9),
            bg=self.bg_main,
            fg=self.fg_muted,
            selectcolor=self.bg_main,
            activebackground=self.bg_main,
            activeforeground=self.fg_text
        ).pack(side=tk.LEFT, padx=5)

        # Search Box
        search_frame = tk.Frame(root, bg=self.bg_main)
        search_frame.pack(pady=15)

        self.entry = tk.Entry(
            search_frame,
            font=("Segoe UI", 13),
            width=24,
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

        # Quick buttons row 1 – India
        quick_frame1 = tk.Frame(root, bg=self.bg_main)
        quick_frame1.pack(pady=4)

        india_stocks = ["RELIANCE", "HDFCBANK", "TCS", "ICICIBANK", "SBIN"]
        for s in india_stocks:
            tk.Button(
                quick_frame1,
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
                command=lambda x=s: self.quick(x, "INDIA")
            ).pack(side=tk.LEFT, padx=3)

        # Quick buttons row 2 – USA
        quick_frame2 = tk.Frame(root, bg=self.bg_main)
        quick_frame2.pack(pady=4)

        usa_stocks = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN"]
        for s in usa_stocks:
            tk.Button(
                quick_frame2,
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
                command=lambda x=s: self.quick(x, "USA")
            ).pack(side=tk.LEFT, padx=3)

        # Quick buttons row 3 – major indices
        quick_frame3 = tk.Frame(root, bg=self.bg_main)
        quick_frame3.pack(pady=4)

        index_buttons = [
            ("NIFTY 50", "^NSEI"),
            ("BANK NIFTY", "^NSEBANK"),
            ("NASDAQ", "^IXIC"),
        ]
        for label, code in index_buttons:
            tk.Button(
                quick_frame3,
                text=label,
                font=("Segoe UI", 9, "bold"),
                bg="#263238",
                fg="#FFEE58",
                activebackground="#37474F",
                activeforeground=self.fg_text,
                bd=0,
                relief="flat",
                padx=12,
                pady=4,
                cursor="hand2",
                command=lambda c=code: self.quick_index(c)
            ).pack(side=tk.LEFT, padx=4)

        # Info display
        self.info = tk.Label(
            root,
            text="Type symbol like TCS / RELIANCE (India) or AAPL / TSLA (USA) or use quick buttons.",
            font=("Segoe UI", 12),
            bg=self.bg_main,
            fg=self.fg_muted
        )
        self.info.pack(pady=10)

        # Graph card
        outer_graph_frame = tk.Frame(root, bg=self.bg_main)
        outer_graph_frame.pack(fill=tk.BOTH, expand=True, padx=25, pady=15)

        self.graph_frame = tk.Frame(outer_graph_frame, bg=self.bg_card, bd=0, relief="flat")
        self.graph_frame.pack(fill=tk.BOTH, expand=True)

    def normalize_ticker(self, symbol: str, region: str) -> str:
        symbol = symbol.strip()
        if symbol.startswith("^"):
            self.current_region = "INDEX"
            return symbol

        up = symbol.upper()
        if up.endswith(".NS") or up.endswith(".BO"):
            self.current_region = "INDIA"
            return up

        if region == "INDIA":
            self.current_region = "INDIA"
            return up + self.default_india_suffix
        else:
            self.current_region = "USA"
            return up

    def quick(self, ticker, region):
        self.region_var.set(region)
        self.entry.delete(0, tk.END)
        self.entry.insert(0, ticker)
        self.search()

    def quick_index(self, code):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, code)
        self.search()

    def search(self):
        raw = self.entry.get().strip()
        if not raw:
            messagebox.showwarning("Error", "Please enter a symbol or index code")
            return

        region = self.region_var.get()
        ticker = self.normalize_ticker(raw, region)

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
        for widget in self.graph_frame.winfo_children():
            widget.destroy()

        display_symbol = ticker.replace(".NS", "").replace(".BO", "")

        if self.current_region == "INDIA":
            accent = self.accent_india
            currency = "₹"
        elif self.current_region == "USA":
            accent = self.accent_usa
            currency = "$"
        else:
            accent = "#FFEE58"
            if ticker in ["^NSEI", "^NSEBANK"]:
                currency = "₹"
            else:
                currency = "$"

        color = accent if change >= 0 else "#FF5252"
        symbol_ch = "▲" if change >= 0 else "▼"
        self.info.config(
            text=f"{display_symbol}   {currency}{price:.2f}   {symbol_ch} {change:.2f} ({percent:+.1f}%)",
            fg=color
        )

        fig = Figure(figsize=(9.2, 4.0), dpi=100)
        ax = fig.add_subplot(111)

        ax.set_facecolor("#000000")
        fig.patch.set_facecolor("#000000")

        ax.plot(data.index, data['Close'], linewidth=2.2, color=accent)
        ax.scatter(data.index[-1], price, color=color, s=80, zorder=5)

        ax.set_title(f'{display_symbol} - Last 6 Months', fontsize=12, pad=10, color=self.fg_text)
        ax.set_ylabel(f'Price ({currency})', fontsize=10, color=self.fg_muted)
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
