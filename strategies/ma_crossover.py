import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Load your historical data from the CSV file
# Skip the first 3 rows (headers/metadata) and set proper column names
try:
    # Get the correct path to the data file
    current_dir = Path(__file__).parent.parent
    data_path = current_dir / "data" / "sample_data" / "reliance_data.csv"
    
    df = pd.read_csv(data_path, 
                     skiprows=3,  # Skip the first 3 rows
                     names=['Date', 'Close', 'High', 'Low', 'Open', 'Volume'],  # Set column names
                     index_col='Date', 
                     parse_dates=True)
except FileNotFoundError:
    print(f"Error: Data file not found at {data_path}. Please check if the data file exists.")
    exit()

# We only need the 'Close' price for these strategies
prices = df['Close'].copy()

print("Data loaded successfully.")

# ========================================================================================
# 1. Calculate the SMAs
short_window = 50
long_window = 200

# Create a new DataFrame to store our signals
signals_ma = pd.DataFrame(index=prices.index)
signals_ma['price'] = prices

signals_ma['short_ma'] = signals_ma['price'].ewm(span=short_window, min_periods=1).mean()
signals_ma['long_ma'] = signals_ma['price'].ewm(span=long_window, min_periods=1).mean()

# 2. Generate the signals
# Create a 'signal' column filled with 0s
signals_ma['signal'] = 0.0

# Generate buy signal (1.0)
# We use .shift(1) to ensure we are comparing the current price to the previous day's price
signals_ma.loc[signals_ma['short_ma'] > signals_ma['long_ma'], 'signal'] = 1.0

# Generate sell signal (-1.0)
signals_ma.loc[signals_ma['short_ma'] < signals_ma['long_ma'], 'signal'] = -1.0

# 3. Find the exact crossover points for trading
# We take the difference of the signals column to find the points where the signal changes
# A change from -1 to 1 is a buy (difference = 2), from 1 to -1 is a sell (difference = -2)
signals_ma['positions'] = signals_ma['signal'].diff()

print("\nMoving Average Crossover signals:")
print(signals_ma.tail())