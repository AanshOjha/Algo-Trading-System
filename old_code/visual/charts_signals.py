import sys
import os
# Add the parent directory to the Python path so we can import from strategies
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.ma_crossover import signals_ma
from strategies.bollinger_bands import signals_bb
import matplotlib.pyplot as plt

# --- Plotting Moving Average Crossover ---
fig, ax = plt.subplots(figsize=(14, 7))

# Plot price and MAs
ax.plot(signals_ma['price'], label='Price')
ax.plot(signals_ma['short_ma'], label='50-Day SMA', color='orange')
ax.plot(signals_ma['long_ma'], label='200-Day SMA', color='purple')

# Plot Buy signals
ax.plot(signals_ma[signals_ma['positions'] == 2.0].index, 
         signals_ma.short_ma[signals_ma['positions'] == 2.0],
         '^', markersize=10, color='g', label='Buy Signal')

# Plot Sell signals
ax.plot(signals_ma[signals_ma['positions'] == -2.0].index, 
         signals_ma.short_ma[signals_ma['positions'] == -2.0],
         'v', markersize=10, color='r', label='Sell Signal')

ax.set_title('Moving Average Crossover Strategy')
ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.legend()
plt.show()



# --- Plotting Bollinger Bands ---
fig, ax = plt.subplots(figsize=(14, 7))

# Plot price and Bollinger Bands
ax.plot(signals_bb['price'], label='Price', color='black', alpha=0.8)
ax.plot(signals_bb['middle_band'], label='20-Day SMA', color='orange', linestyle='--')
ax.plot(signals_bb['upper_band'], label='Upper Band', color='blue', alpha=0.3)
ax.plot(signals_bb['lower_band'], label='Lower Band', color='blue', alpha=0.3)

# Plot the trend filter MA
ax.plot(signals_bb['long_ma'], label='200-Day SMA (Trend)', color='purple', alpha=0.5)

# Plot Buy signals
ax.plot(signals_bb[signals_bb['signal'] == 1.0].index, 
         signals_bb.price[signals_bb['signal'] == 1.0],
         '^', markersize=12, color='g', label='Buy Signal (Confirmed Dip)')

# Plot Sell signals
ax.plot(signals_bb[signals_bb['signal'] == -1.0].index, 
         signals_bb.price[signals_bb['signal'] == -1.0],
         'v', markersize=12, color='r', label='Sell Signal (Confirmed Peak)')

ax.set_title('Refined Bollinger Bands Strategy (with Confirmation & Trend Filter)')
ax.set_xlabel('Date')
ax.set_ylabel('Price')
ax.legend()
plt.show()