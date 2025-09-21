import pandas as pd
import matplotlib.pyplot as plt
import os
from pathlib import Path

# Load your historical data from the CSV file
# We make 'Date' the index and tell pandas to treat it as a date object
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


# 1. Calculate Bollinger Bands
window = 20  # Standard window for Bollinger Bands
std_dev = 2  # Standard deviations

# Create a new DataFrame for this strategy
signals_bb = pd.DataFrame(index=prices.index)
signals_bb['price'] = prices

# Bollinger Bands parameters
signals_bb['middle_band'] = signals_bb['price'].rolling(window=window).mean()
price_std = signals_bb['price'].rolling(window=window).std()
signals_bb['upper_band'] = signals_bb['middle_band'] + (price_std * std_dev)
signals_bb['lower_band'] = signals_bb['middle_band'] - (price_std * std_dev)

# Trend Filter parameter
long_window = 200
signals_bb['long_ma'] = signals_bb['price'].rolling(window=long_window).mean()


# --- 3. GENERATE REFINED SIGNALS (THE ONLY SIGNAL LOGIC) ---
print("Generating refined signals with confirmation and trend filter...")
signals_bb['signal'] = 0.0 # Reset signals column

# BUY Condition: Must cross back above lower band AND be in an uptrend
buy_condition = (signals_bb['price'].shift(1) < signals_bb['lower_band'].shift(1)) & \
                (signals_bb['price'] > signals_bb['lower_band']) & \
                (signals_bb['price'] > signals_bb['long_ma']) # Trend filter

signals_bb.loc[buy_condition, 'signal'] = 1.0

# SELL Condition: Must cross back below upper band AND be in a downtrend
sell_condition = (signals_bb['price'].shift(1) > signals_bb['upper_band'].shift(1)) & \
                 (signals_bb['price'] < signals_bb['upper_band']) & \
                 (signals_bb['price'] < signals_bb['long_ma']) # Trend filter

signals_bb.loc[sell_condition, 'signal'] = -1.0