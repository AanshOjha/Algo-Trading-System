"""
Utility Functions

Common helper functions used across the trading system.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any
from datetime import datetime


def format_currency(amount: float) -> str:
    """Format a number as currency."""
    return f"${amount:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format a number as percentage."""
    return f"{value:.{decimals}f}%"


def calculate_returns(prices: pd.Series) -> pd.Series:
    """Calculate returns from price series."""
    return prices.pct_change().dropna()


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero."""
    if denominator == 0 or pd.isna(denominator):
        return default
    return numerator / denominator


def validate_dataframe(df: pd.DataFrame, required_columns: List[str]) -> bool:
    """
    Validate that a DataFrame has required columns.
    
    Args:
        df (pd.DataFrame): DataFrame to validate
        required_columns (List[str]): List of required column names
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If validation fails
    """
    if df.empty:
        raise ValueError("DataFrame is empty")
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")
    
    return True


def print_section_header(title: str, char: str = "=", width: int = 60) -> None:
    """Print a formatted section header."""
    print("\n" + char * width)
    print(f"{title.center(width)}")
    print(char * width)