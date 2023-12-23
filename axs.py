import requests
import pandas as pd
import datetime
import time

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

def fetch_historical_data(coin_id, days='max', currency='usd'):
    """ Fetch historical data from CoinGecko API
        If days = 1, time = 5 min
         If days = 2-90, time = 1 hr 
         If days > 90, time = 1 day"""
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {
        'vs_currency': currency,
        'days': days,
    }
    response = requests.get(url, params=params)
    return response.json()



# Number of days for the data
def date_price(days_diff):
    # Fetch historical data
    eth_data = fetch_historical_data('ethereum', days=days_diff)
    axs_data = fetch_historical_data('axie-infinity', days=days_diff)
    # sleep for 1 second to avoid rate limit
    time.sleep(2)
    # print(f"Keys in ETH data: {eth_data.keys()}, over {days_diff} days")

    # Extracting prices and timestamps
    eth_prices = [item[1] for item in eth_data['prices']]
    axs_prices = [item[1] for item in axs_data['prices']]
    timestamps = [item[0] for item in eth_data['prices']]
    # date_labels = [datetime.datetime.fromtimestamp(time/1000).date() for time in timestamps]

    # Convert the hourly data to daily averages
    def convert_to_daily(timestamps, prices):
        df = pd.DataFrame({'Timestamp': timestamps, 'Price': prices})
        df['Date'] = pd.to_datetime(df['Timestamp'], unit='ms').dt.date
        df_daily = df.groupby('Date').mean()  # Group by Date and take the average
        return df_daily.index, df_daily['Price'].values

    eth_dates, eth_daily_prices = convert_to_daily(timestamps, eth_prices)
    axs_dates, axs_daily_prices = convert_to_daily(timestamps, axs_prices)

    return eth_dates, eth_daily_prices, axs_dates, axs_daily_prices


def main():
    try:
        eth_dates, eth_daily_prices, axs_dates, axs_daily_prices = date_price(91)
    except:
        eth_dates, eth_daily_prices, axs_dates, axs_daily_prices = date_price(90)

    # Calculate the ETH to AXS price ratio on daily data
    eth_to_axs_ratio = [eth/axs for eth, axs in zip(eth_daily_prices, axs_daily_prices)]

    # Convert to a DataFrame for easier calculations
    df = pd.DataFrame({
        'Date': eth_dates,
        'ETH_to_AXS_Ratio': eth_to_axs_ratio
    })

    # Calculate 7-day and 30-day SMA on daily data
    df['7_Day_SMA'] = df['ETH_to_AXS_Ratio'].rolling(window=7).mean()
    df['30_Day_SMA'] = df['ETH_to_AXS_Ratio'].rolling(window=30).mean()

    # Plotting
    plt.figure(figsize=(15, 7))
    plt.plot(df['Date'], df['ETH_to_AXS_Ratio'], label='ETH to AXS Ratio', color='blue')
    plt.plot(df['Date'], df['7_Day_SMA'], label='7 Day SMA', color='green')
    plt.plot(df['Date'], df['30_Day_SMA'], label='30 Day SMA', color='red')
    plt.title('ETH to AXS Ratio with 7-Day and 30-Day SMA')
    plt.xlabel('Date')
    plt.ylabel('Ratio')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    # convert plot to html and return
    figfile = io.BytesIO()
    plt.savefig(figfile, format='png')
    figfile.seek(0)  # rewind to beginning of file
    figdata_png = base64.b64encode(figfile.getvalue())
    plt.close()

    return figdata_png
