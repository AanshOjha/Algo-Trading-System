"""
Configuration Settings

Central configuration for the trading system.
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "sample_data"
OUTPUT_DIR = PROJECT_ROOT / "output"

# Default settings
DEFAULT_INITIAL_CAPITAL = 100000.0
DEFAULT_DB_FILE = "trading_results.db"

# Chart settings
CHART_STYLE = 'seaborn-v0_8'
CHART_DPI = 300
CHART_SIZE = (15, 8)

# Risk settings
DEFAULT_RISK_FREE_RATE = 0.02

# Database settings
DB_TIMEOUT = 30

# Create output directory if it doesn't exist
OUTPUT_DIR.mkdir(exist_ok=True)