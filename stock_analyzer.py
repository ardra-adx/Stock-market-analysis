#!/usr/bin/env python3
"""
stock_analyzer.py
-----------------
A simple command‑line application that

1. Fetches historical OHLCV data for one or more tickers
   • Source can be Yahoo Finance (via yfinance) **or**
     Alpha Vantage (requires FREE API key)
2. Performs basic technical analysis
   • 50‑day & 200‑day Moving Averages
   • Daily returns
3. Optionally plots the price series + moving averages

Usage examples
--------------
# Yahoo Finance (default source)
python stock_analyzer.py --ticker AAPL --start 2023-01-01 --end 2024-01-01 --plot

# Alpha Vantage (set your API key once:  export AV_API_KEY=YOURKEY)
python stock_analyzer.py -t MSFT --source alpha --plot

Dependencies
------------
pip install yfinance pandas matplotlib requests python-dateutil
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime
from typing import List

import pandas as pd
import matplotlib.pyplot as plt
import requests
import yfinance as yf


# ---------- Data‑fetch helpers ------------------------------------------------
def fetch_yahoo(ticker: str, start: str, end: str) -> pd.DataFrame:
    data = yf.download(ticker, start=start, end=end, auto_adjust=False)
    if data.empty:
        raise ValueError(f"No Yahoo Finance data returned for {ticker}")
    data.index = pd.to_datetime(data.index)
    return data


def fetch_alpha_vantage(
    ticker: str,
    start: str,
    end: str,
    api_key: str,
    function: str = "TIME_SERIES_DAILY_ADJUSTED",
    outputsize: str = "full",
) -> pd.DataFrame:
    url = (
        "https://www.alphavantage.co/query"
        f"?function={function}&symbol={ticker}&outputsize={outputsize}&apikey={api_key}"
    )
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    raw = resp.json()

    # JSON always has exactly one key that contains the timeseries
    key = [k for k in raw.keys() if "Time Series" in k]
    if not key:
        raise ValueError(f"Unexpected Alpha Vantage payload: {json.dumps(raw)[:200]}")

    records = (
        pd.DataFrame(raw[key[0]])
        .T.sort_index()
        .rename(
            columns={
                "1. open": "Open",
                "2. high": "High",
                "3. low": "Low",
                "4. close": "Close",
                "5. adjusted close": "Adj Close",
                "6. volume": "Volume",
            }
        )
        .astype(float)
    )

    records.index = pd.to_datetime(records.index)
    mask = (records.index >= pd.to_datetime(start)) & (records.index <= pd.to_datetime(end))
    return records.loc[mask]


# ---------- Analysis helpers --------------------------------------------------
def add_indicators(df: pd.DataFrame, windows: List[int] = (50, 200)) -> pd.DataFrame:
    out = df.copy()
    for w in windows:
        out[f"MA_{w}"] = out["Adj Close"].rolling(window=w).mean()
    out["Daily_Return_%"] = out["Adj Close"].pct_change().mul(100)
    return out


# ---------- Plotting ----------------------------------------------------------
def plot_price(df: pd.DataFrame, ticker: str) -> None:
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df["Adj Close"], label="Adj Close")
    if "MA_50" in df.columns:
        plt.plot(df.index, df["MA_50"], label="50‑Day MA")
    if "MA_200" in df.columns:
        plt.plot(df.index, df["MA_200"], label="200‑Day MA")
    plt.title(f"{ticker} | Price & Moving Averages")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()


# ---------- CLI ---------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    today = datetime.now().date().isoformat()
    p = argparse.ArgumentParser(description="Fetch and analyze stock data")
    p.add_argument("-t", "--ticker", required=True, help="Ticker symbol, e.g. AAPL")
    p.add_argument("--start", default="2023-01-01", help="YYYY-MM-DD")
    p.add_argument("--end", default=today, help="YYYY-MM-DD")
    p.add_argument(
        "-s",
        "--source",
        choices=["yahoo", "alpha"],
        default="yahoo",
        help="Data source (default: yahoo)",
    )
    p.add_argument("--no-plot", action="store_true", help="Skip plotting")
    return p.parse_args()


def main() -> None:
    args = parse_args()

    if args.source == "yahoo":
        df = fetch_yahoo(args.ticker, args.start, args.end)
    else:
        api_key = os.getenv("AV_API_KEY")
        if not api_key:
            raise EnvironmentError(
                "Alpha Vantage selected but AV_API_KEY env var not set."
            )
        df = fetch_alpha_vantage(args.ticker, args.start, args.end, api_key)

    df = add_indicators(df)

    # Print a quick statistical summary to stdout
    print("\n=== Summary Stats ===")
    print(df[["Adj Close", "Daily_Return_%"]].describe().round(2))

    # Plot unless user disables
    if not args.no_plot:
        plot_price(df, args.ticker)


if __name__ == "__main__":
    main()
