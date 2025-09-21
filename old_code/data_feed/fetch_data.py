import yfinance as yf
import pandas as pd

# Parameters for the data download
ticker = 'RELIANCE.NS'
start_date = '2018-01-01'
end_date = '2023-12-31'
interval = '1D'

print(f"Downloading data for {ticker} from {start_date} to {end_date}...")

try:
    # Download the historical data using yfinance
    data = yf.download(
        tickers=ticker,
        start=start_date,
        end=end_date,
        interval=interval
    )

    # Check if data was downloaded successfully
    if data.empty:
        print(f"No data found for {ticker}. Please check the ticker symbol and date range.")
    else:
        print(f"Successfully downloaded {data.shape[0]} rows and {data.shape[1]} columns of data.")
        
        # --- Method 1: Save as CSV (Recommended for Beginners) ---
        csv_filename = 'reliance_data.csv'
        data.to_csv(csv_filename)
        print(f"✅ Data successfully saved to '{csv_filename}'")

        # --- Method 2: Save as Parquet (Recommended for Performance) ---
        parquet_filename = 'reliance_data.parquet'
        data.to_parquet(parquet_filename)
        print(f"✅ Data successfully saved to '{parquet_filename}'")

except Exception as e:
    print(f"An error occurred: {e}")