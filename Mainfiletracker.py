import time
import requests
import matplotlib.pyplot as plt
import pandas as pd

# Configuration
api_key  = '6SHWDZG9PIG0D571'
TICKER = "ADANIPOWER.BSE"
RETRY_COUNT = 3
INITIAL_RETRY_DELAY = 60


def fetch_data(ticker, api_key, count=200):
    """Fetch historical stock data from Alpha Vantage API."""
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&apikey={api_key}&outputsize=full'
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        if 'Note' in data:
            raise ValueError(f"API Rate Limit: {data['Note']}")
        if 'Error Message' in data:
            raise ValueError(f"API Error: {data['Error Message']}")
        if 'Time Series (Daily)' not in data:
            raise ValueError("Unexpected API response format")

        df = pd.DataFrame(data['Time Series (Daily)']).T
        df = df[['1. open','2. high', '3. low', '4. close', '5. volume']]
        df.columns = ['open', 'high', 'low', 'close', 'volume']
        df = df.astype(float)
        df.index = pd.to_datetime(df.index)
        df = df.sort_index().iloc[-count:]
        
        return df

    except requests.exceptions.RequestException as e:
        raise SystemExit(f"Request failed: {e}")

def calculate_indicators(data):
    """Calculate technical indicators and add them to the DataFrame."""
    data['SMA_200'] = data['close'].rolling(200).mean()
    data['EMA_50'] = data['close'].ewm(span=50, adjust=False).mean()
    
    #RSI
    delta = data['close'].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    data['RSI_14'] = 100 - (100 / (1 + rs))
    
    #MACD
    ema12 = data['close'].ewm(span=12, adjust=False).mean()
    ema26 = data['close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = ema12 - ema26
    data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    
    return data

def plot_data(data, ticker):
    """Create visualization of stock data and indicators."""
    plt.figure(figsize=(14, 12))
    plt.suptitle(f"{ticker} Technical Analysis", y=0.95)

    #Price and Moving Averages
    ax1 = plt.subplot(3, 1, 1)
    ax1.plot(data['close'], label='Close Price', color='navy')
    ax1.plot(data['SMA_200'], label='SMA 200', color='orange', linestyle='--')
    ax1.plot(data['EMA_50'], label='EMA 50', color='purple', linestyle='--')
    ax1.set_title('Price & Moving Averages')
    ax1.legend()
    ax1.grid(True)

    #RSI
    ax2 = plt.subplot(3, 1, 2, sharex=ax1)
    ax2.plot(data['RSI_14'], label='RSI 14', color='green')
    ax2.axhline(70, color='red', linestyle='--')
    ax2.axhline(30, color='blue', linestyle='--')
    ax2.set_title('Relative Strength Index (RSI)')
    ax2.legend()
    ax2.grid(True)

    #MACD
    ax3 = plt.subplot(3, 1, 3, sharex=ax1)
    ax3.plot(data['MACD'], label='MACD', color='darkred')
    ax3.plot(data['MACD_Signal'], label='Signal Line', color='darkgreen')
    ax3.bar(data.index, data['MACD'] - data['MACD_Signal'], 
            label='Histogram', color='gray', alpha=0.3)
    ax3.axhline(0, color='black', linestyle='--')
    ax3.set_title('MACD')
    ax3.legend()
    ax3.grid(True)

    plt.tight_layout()
    plt.show()

def main():
    """Main execution function with retry logic."""
    retry_delay = INITIAL_RETRY_DELAY
    for attempt in range(1, RETRY_COUNT + 1):
        try:
            print(f"\nAttempt {attempt} of {RETRY_COUNT}")
            data = fetch_data(TICKER, api_key)
            
            if data.empty:
                raise ValueError(f"No data available for {TICKER}")
                
            if len(data) < 200:
                print(f"Warning: Only {len(data)} trading days available (200 recommended)")
                
            data = calculate_indicators(data)
            
            # Printing the last values
            latest = data.iloc[-1]
            print(f"\nLatest Technical Indicators:")
            print(f"Close Price: {latest['close']:.2f}")
            print(f"SMA 200: {latest['SMA_200']:.2f}")
            print(f"EMA 50: {latest['EMA_50']:.2f}")
            print(f"RSI 14: {latest['RSI_14']:.2f}")
            print(f"MACD: {latest['MACD']:.2f}")
            print(f"Signal Line: {latest['MACD_Signal']:.2f}")
            
            plot_data(data, TICKER)
            return
            
        except Exception as e:
            print(f"Error: {e}")
            if "Rate Limit" in str(e):
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            elif attempt == RETRY_COUNT:
                print("Max retry attempts reached. Exiting.")
            else:
                continue

if __name__ == "__main__":
    main()
