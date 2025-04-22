# Stock-Price-Tracker-With-Technical-Factors-

# Stock Technical Analysis Tool

A Python script that fetches stock market data and visualizes key technical indicators like **SMA, EMA, RSI, and MACD** using the Alpha Vantage API.

![image](https://github.com/user-attachments/assets/ac47e139-b863-40ac-9413-72e46eedfe27) ![image](https://github.com/user-attachments/assets/60546aaf-ded8-44df-a566-5ed86f33603a)



## Features
- **Fetches historical stock data** from Alpha Vantage API
- **Calculates technical indicators**:
  - Simple Moving Average (SMA 200)
  - Exponential Moving Average (EMA 50)
  - Relative Strength Index (RSI 14)
  - Moving Average Convergence Divergence (MACD)
- **Visualizes data** with matplotlib:
  - Price chart with moving averages
  - RSI with overbought/oversold levels
  - MACD with signal line and histogram
- **Robust error handling** with retry logic for API rate limits

## Prerequisites
- Python 3.8+
- Alpha Vantage API key (free tier available)
- Required Python packages:
