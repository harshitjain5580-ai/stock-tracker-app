import streamlit as st
import yfinance as yf
import pandas as pd
import mplfinance as mpf
from datetime import datetime, timedelta
import json
import os
import smtplib
from email.mime.text import MIMEText
import random

# ===================== STREAMLIT PAGE CONFIG =====================
st.set_page_config(
    page_title="Global Stock Tracker (India + USA)",
    layout="wide",
    page_icon="📈"
)

WATCHLIST_FILE = "watchlist.json"

# ===================== EMAIL / OTP HELPERS =====================

# Try to load email configuration with fallback
EMAIL_CONF = None
EMAIL_USER = None
EMAIL_PASSWORD = None
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

try:
    EMAIL_CONF = st.secrets["email"]
    EMAIL_USER = EMAIL_CONF.get("user")
    EMAIL_PASSWORD = EMAIL_CONF.get("password")
    SMTP_SERVER = EMAIL_CONF.get("smtp_server", "smtp.gmail.com")
    SMTP_PORT = int(EMAIL_CONF.get("smtp_port", 587))
    # Check if credentials are placeholder/invalid
    if EMAIL_USER and "your-" in EMAIL_USER.lower():
        EMAIL_CONF = None
except:
    # Secrets not configured - we'll handle this gracefully
    passsmtp_port", 465))


def send_otp_email(to_email: str, otp: str):
    """Send OTP code to the user's email."""
        if not EMAIL_CONF or not EMAIL_USER or not EMAIL_PASSWORD:
        return False, "Email configuration not set up. Please configure email credentials in Streamlit Secrets."
    subject = "Your OTP for Global Stock Tracker"
    body = f"Your one-time password (OTP) is: {otp}\n\nIt is valid for 5 minutes."

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    try:
        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        return True, "OTP sent successfully! Please check your email."
    except Exception as e:
        return False, f"Failed to send OTP: {e}"


def generate_otp():
    """Generate a 6-digit numeric OTP as a string."""
    return f"{random.randint(100000, 999999)}"


def init_auth_state():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = None
    if "otp_code" not in st.session_state:
        st.session_state.otp_code = None
    if "otp_expires_at" not in st.session_state:
        st.session_state.otp_expires_at = None


def show_auth_ui():
    st.title("Sign up / Login 🔐")
    st.write("Use your email to receive a one-time password (OTP).")

    email = st.text_input("Email address", key="email_input")

    col1, col2 = st.columns([1, 1])

    with col1:
        send_otp_btn = st.button("Send OTP")
    with col2:
        pass

    if send_otp_btn:
        if not email:
            st.error("Please enter an email address.")
        else:
            otp = generate_otp()
            success, msg = send_otp_email(email, otp)
            if success:
                st.success(msg)
                st.session_state.otp_code = otp
                st.session_state.user_email = email
                st.session_state.otp_expires_at = datetime.now() + timedelta(minutes=5)
            else:
                st.error(msg)

    st.markdown("---")

    otp_input = st.text_input("Enter OTP", type="password", max_chars=6, key="otp_input")
    verify_btn = st.button("Verify OTP")

    if verify_btn:
        if not st.session_state.otp_code:
            st.error("Please request an OTP first.")
            return

        if not otp_input:
            st.error("Please enter the OTP sent to your email.")
            return

        if datetime.now() > st.session_state.otp_expires_at:
            st.error("OTP has expired. Please request a new one.")
            return

        if otp_input.strip() == st.session_state.otp_code:
            st.session_state.authenticated = True
            st.success("OTP verified! You are now logged in.")
        else:
            st.error("Incorrect OTP. Please try again.")


def show_logout_button():
    with st.sidebar:
        if st.session_state.get("authenticated"):
            st.markdown(f"**Logged in as:** {st.session_state.get('user_email')}")
            if st.button("Logout"):
                st.session_state.authenticated = False
                st.session_state.user_email = None
                st.session_state.otp_code = None
                st.session_state.otp_expires_at = None
                st.experimental_rerun()

# ===================== APP LOGIC (WATCHLIST / CHART) =====================

def load_watchlist_from_file():
    if os.path.exists(WATCHLIST_FILE):
        try:
            with open(WATCHLIST_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return [str(x).upper() for x in data]
        except Exception:
            pass
    return []


def save_watchlist_to_file(watchlist):
    try:
        with open(WATCHLIST_FILE, "w", encoding="utf-8") as f:
            json.dump(watchlist, f)
    except Exception:
        pass


def normalize_ticker(symbol: str, region: str) -> str:
    symbol = symbol.strip()
    if symbol.startswith("^"):
        return symbol
    up = symbol.upper()
    if up.endswith(".NS") or up.endswith(".BO"):
        return up
    if region == "INDIA":
        return up + ".NS"
    return up


def fetch_history(ticker, period, interval):
    stock = yf.Ticker(ticker)
    data = stock.history(period=period, interval=interval)
    if data.empty:
        data = stock.history(period="1y", interval="1d")
    return stock, data


def moving_average_hint(data, price):
    df = data.copy()
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    ma20 = df["MA20"].iloc[-1]
    ma50 = df["MA50"].iloc[-1]
    ma20_val = float(ma20) if pd.notna(ma20) else None
    ma50_val = float(ma50) if pd.notna(ma50) else None

    if ma20_val is not None and ma50_val is not None:
        if price > ma20_val > ma50_val:
            return (
                "Trend strong (Price > MA20 > MA50). Educational hint: BUY / HOLD zone, do your own research.",
                ma20_val,
                ma50_val,
            )
        elif price < ma20_val < ma50_val:
            return (
                "Trend weak (Price < MA20 < MA50). Educational hint: better to WAIT, avoid fresh buying.",
                ma20_val,
                ma50_val,
            )
        else:
            return (
                "Mixed trend (MAs crossing/flat). Educational hint: WAIT and watch; no clear BUY signal.",
                ma20_val,
                ma50_val,
            )
    else:
        return "Not enough past data to compute moving averages.", ma20_val, ma50_val


def approx_live_price(stock, data):
    live_price = None
    try:
        fi = stock.fast_info
        live_price = fi.last_price
    except Exception:
        live_price = None
    if live_price is None:
        live_price = float(data["Close"].iloc[-1])
    return float(live_price)


def main_app():
    # --------- SESSION DEFAULTS ---------
    if "watchlist" not in st.session_state:
        st.session_state.watchlist = load_watchlist_from_file()

    # --------- SIDEBAR SETTINGS ---------
    st.sidebar.title("Global Stock Tracker")

    market = st.sidebar.radio(
        "Market",
        ["India (NSE/BSE)", "USA"],
        index=0
    )

    region = "INDIA" if "India" in market else "USA"

    timeframe = st.sidebar.radio(
        "Timeframe",
        ["1D (1m)", "5D (15m)", "1M (1d)", "6M (1d)", "1Y (1d)", "MAX (1wk)"],
        index=4
    )

    chart_type = st.sidebar.radio(
        "Chart Type",
        ["Line", "Candlestick"],
        index=0
    )

    tf_map = {
        "1D (1m)":  ("1d",  "1m"),
        "5D (15m)": ("5d",  "15m"),
        "1M (1d)":  ("1mo", "1d"),
        "6M (1d)":  ("6mo", "1d"),
        "1Y (1d)":  ("1y",  "1d"),
        "MAX (1wk)":("max", "1wk"),
    }
    current_period, current_interval = tf_map[timeframe]

    # --------- TABS ---------
    tab_chart, tab_watch = st.tabs(["📊 Chart", "⭐ Watchlist"])

    # --------- CHART TAB ---------
    with tab_chart:
        st.header("Chart – India + USA Stocks & Indices")

        col1, col2 = st.columns([2, 1])

        with col1:
            default_symbol = "RELIANCE" if region == "INDIA" else "AAPL"
            symbol_input = st.text_input(
                "Enter symbol or index (e.g., TCS, RELIANCE, AAPL, ^NSEI):",
                value=default_symbol,
                key="symbol_input"
            )

        with col2:
            st.markdown("**Quick Picks (India)**")
            q1_cols = st.columns(5)
            quick_india = ["RELIANCE", "HDFCBANK", "TCS", "ICICIBANK", "SBIN"]
            for i, s in enumerate(quick_india):
                if q1_cols[i].button(s, key=f"qi_{s}"):
                    symbol_input = s

            st.markdown("**Quick Picks (USA)**")
            q2_cols = st.columns(5)
            quick_usa = ["AAPL", "TSLA", "GOOGL", "MSFT", "AMZN"]
            for i, s in enumerate(quick_usa):
                if q2_cols[i].button(s, key=f"qu_{s}"):
                    symbol_input = s

        symbol = symbol_input

        if symbol:
            ticker = normalize_ticker(symbol, region)
            try:
                stock, data = fetch_history(ticker, current_period, current_interval)
                if data.empty:
                    st.error(f"'{ticker}' not found or no data.")
                    data = None
            except Exception as e:
                st.error(str(e))
                data = None

            if data is not None and not data.empty:
                live_price = approx_live_price(stock, data)
                old_price = float(data["Close"].iloc[0])
                change = live_price - old_price
                percent = (change / old_price) * 100

                hint_text, ma20, ma50 = moving_average_hint(data, live_price)

                display_symbol = ticker.replace(".NS", "").replace(".BO", "")
                if region == "INDIA" or ticker in ["^NSEI", "^NSEBANK"]:
                    currency = "₹"
                else:
                    currency = "$"

                st.markdown(
                    f"### {display_symbol} – {currency}{live_price:.2f} "
                    f"({change:+.2f}, {percent:+.2f}%)"
                )
                st.write(hint_text)

                if chart_type == "Line":
                    chart_df = pd.DataFrame({
                        "Close": data["Close"],
                        "MA20": data["Close"].rolling(20).mean(),
                        "MA50": data["Close"].rolling(50).mean(),
                    })
                    st.line_chart(chart_df)
                else:
                    df = data.copy()
                    mc = mpf.make_marketcolors(
                        up="#00E676",
                        down="#FF5252",
                        edge="inherit",
                        wick="inherit",
                        volume="in"
                    )
                    s = mpf.make_mpf_style(
                        base_mpf_style="nightclouds",
                        marketcolors=mc,
                        facecolor="#000000",
                        edgecolor="#444444",
                        gridcolor="#444444"
                    )
                    fig, ax = mpf.plot(
                        df,
                        type="candle",
                        style=s,
                        mav=(20, 50),
                        volume=False,
                        returnfig=True,
                        datetime_format="%d-%b",
                        xrotation=15,
                        show_nontrading=False
                    )
                    st.pyplot(fig, use_container_width=True)

                with st.expander("More info"):
                    try:
                        info = stock.get_info()
                    except Exception:
                        info = {}
                    st.write({
                        "Symbol": display_symbol,
                        "Currency": currency,
                        "Exchange": info.get("exchange", ""),
                        "Sector": info.get("sector", ""),
                        "Industry": info.get("industry", ""),
                        "Market Cap": info.get("marketCap", ""),
                        "52W High": info.get("fiftyTwoWeekHigh", ""),
                        "52W Low": info.get("fiftyTwoWeekLow", ""),
                    })

    # --------- WATCHLIST TAB ---------
    with tab_watch:
        st.header("Watchlist (India + USA)")

        col_add, col_btns = st.columns([2, 2])
        with col_add:
            new_sym = st.text_input(
                "Add symbol (e.g., TCS, RELIANCE, AAPL):",
                key="watch_add"
            )
        with col_btns:
            add_click = st.button("Add to Watchlist")
            clear_all = st.button("Clear All")

        changed = False

        if add_click and new_sym.strip():
            sym_up = new_sym.strip().upper()
            if sym_up not in st.session_state.watchlist:
                st.session_state.watchlist.append(sym_up)
                changed = True

        if clear_all and st.session_state.watchlist:
            st.session_state.watchlist = []
            changed = True

        if changed:
            save_watchlist_to_file(st.session_state.watchlist)

        if not st.session_state.watchlist:
            st.info("Watchlist is empty. Add some symbols above.")
        else:
            if st.button("Refresh Watchlist Prices"):
                st.session_state["watch_refresh"] = datetime.now().isoformat()

            st.write("### Current Watchlist")

            rows = []
            end = datetime.now()
            start = end - timedelta(days=2)

            for sym in st.session_state.watchlist:
                try:
                    stock = yf.Ticker(sym)
                    hist = stock.history(start=start, end=end)
                    if hist.empty:
                        stock = yf.Ticker(sym + ".NS")
                        hist = stock.history(start=start, end=end)
                    if hist.empty or len(hist) < 1:
                        continue
                    last = float(hist["Close"].iloc[-1])
                    if len(hist) >= 2:
                        prev = float(hist["Close"].iloc[0])
                        pct = (last - prev) / prev * 100
                    else:
                        pct = 0.0
                    rows.append((sym, last, pct))
                except Exception:
                    continue

            if rows:
                df_watch = pd.DataFrame(rows, columns=["Symbol", "Last Price", "% Change"])
                st.dataframe(
                    df_watch.style.format({"Last Price": "{:.2f}", "% Change": "{:+.2f}"}),
                    use_container_width=True,
                )
            else:
                st.warning("No data available for current watchlist symbols.")

    st.caption("⚠ This app is for educational purposes only and is NOT financial advice. Always do your own research.")

# ===================== ENTRY POINT =====================

try:
    init_auth_state()
    show_logout_button()
    
    
    # Show setup message if email credentials are not configured
    if EMAIL_CONF is None:
        st.error("⚠️ Email configuration not found!")
        st.info("""
        ### Setup Required
        This app requires Gmail email configuration to send OTP codes for login.
        
        **Steps to configure:**
        1. Go to your app's **Settings → Secrets**
        2. Add the following TOML configuration:
        
        ```toml
        [email]
        email = "your-email@gmail.com"
        user = "your-email@gmail.com"
        password = "your-app-password"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        ```
        
        3. Replace with your actual Gmail address and **Gmail App Password** (not regular password)
        4. Get your App Password from: [Google Account Settings](https://myaccount.google.com/apppasswords)
        5. Click Save and the app will auto-refresh
        """)
    else:
        if not st.session_state.authenticated:
            show_auth_ui()
        else:
            main_app()
            except Exception as e:
                st.error(f"❌ App Error: {str(e)}")
                st.info(f"Please contact support with this error: {type(e).__name__}: {str(e)}")
