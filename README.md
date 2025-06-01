# Stock-market-analysis

A simple and powerful command-line Python tool to fetch historical stock data, perform basic technical analysis, and optionally visualize it.

Features
- Fetch historical OHLCV data using:
  - Yahoo Finance (via yfinance) — default
  - Alpha Vantage — requires free API key
- Technical Indicators:
  - 50-Day & 200-Day Moving Averages
  - Daily Returns (%)
- Optional plotting of price & indicators

Steps
1. Install the required Python packages
   pip install yfinance pandas matplotlib requests python-dateutil
2. Run the Script uding following code:-
   python stock_analyzer.py --ticker <TICKER> [--start YYYY-MM-DD] [--end YYYY-MM-DD] [--source yahoo|alpha] [--no-plot]
3. You will get the Descriptive statistics of Adjusted Close & Daily Returns and Graph of Price + 50-day and 200-day Moving Averages














































![Screenshot from 2025-05-31 00-05-52](https://github.com/user-attachments/assets/e5753363-9e6d-4afd-b957-a7113f1651a7)
![Screenshot from 2025-05-31 00-06-14](https://github.com/user-attachments/assets/2b2a635a-2308-4281-a059-23aef72af594)
