"""
Data Management Module

Utilities for loading and managing trading data.
"""

import pandas as pd
import os
from pathlib import Path
from typing import Optional


def load_sample_data(data_file: str = "reliance_data.csv") -> pd.DataFrame:
    """
    Load sample trading data.
    
    Args:
        data_file (str): Name of the data file to load
        
    Returns:
        pd.DataFrame: Loaded data with date index
    """
    # Get the path to the sample data directory
    current_dir = Path(__file__).parent
    data_path = current_dir / "sample_data" / data_file
    
    if not data_path.exists():
        raise FileNotFoundError(f"Data file not found: {data_path}")
    
    # Load the data
    df = pd.read_csv(data_path)
    
    # Convert date column to datetime and set as index if needed
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
    elif not isinstance(df.index, pd.DatetimeIndex):
        # If no Date column and index is not datetime, try to convert index
        try:
            df.index = pd.to_datetime(df.index)
        except:
            pass
    
    return df


def validate_data(df: pd.DataFrame) -> bool:
    """
    Validate that data has the required columns for backtesting.
    
    Args:
        df (pd.DataFrame): Data to validate
        
    Returns:
        bool: True if data is valid
    """
    required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    if df.empty:
        raise ValueError("Data is empty")
    
    if not isinstance(df.index, pd.DatetimeIndex):
        raise ValueError("Data must have a datetime index")
    
    return True