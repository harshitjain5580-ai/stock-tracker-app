# Global Stock Tracker

A Streamlit dashboard for exploring Indian and US market data with Yahoo Finance.
The app provides interactive price charts, moving-average indicators, watchlists,
and optional email OTP authentication.

## Features

- Track stocks listed on Indian exchanges (NSE/BSE) and US exchanges.
- View historical prices and candlestick charts for selectable periods.
- Compare the current price with 20-day and 50-day moving averages.
- Maintain a local watchlist.
- Sign in with a one-time password sent through a configured SMTP account.

> This project is for education and market research only. It is not financial
> advice, and the data supplied by Yahoo Finance may be delayed or unavailable.

## Requirements

- Python 3.10 or newer
- Internet access for Yahoo Finance data
- An SMTP account only if email OTP login is enabled

## Setup

```bash
git clone https://github.com/harshitjain5580-ai/stock-tracker-app.git
cd stock-tracker-app
python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

Install dependencies:

```bash
make install
```

If `make` is not installed, run:

```bash
python -m pip install -r requirements.txt
```

## Run the app

```bash
make run
```

Or run Streamlit directly:

```bash
streamlit run app.py
```

The app opens at <http://localhost:8501>.

## Optional email OTP configuration

Create `.streamlit/secrets.toml` locally (do not commit it) with:

```toml
[email]
user = "your-email@example.com"
password = "your-app-password"
smtp_server = "smtp.gmail.com"
smtp_port = 465
```

For Gmail, use an app password rather than your normal account password.
Without this configuration, the dashboard can still be started, but OTP login
will display a configuration message.

## Project structure

```text
app.py                    Streamlit application
requirements.txt          Python dependencies
Makefile                  Common development commands
.streamlit/config.toml   Streamlit settings and theme
```

## Development commands

| Command | Description |
| --- | --- |
| `make install` | Install Python dependencies |
| `make run` | Start the Streamlit dashboard |
| `make check` | Compile-check the application |
| `make clean` | Remove Python cache files |


