"""
Core Trading System Components

This package contains the main components of the algorithmic trading system:
- BacktestingEngine: Core backtesting logic
- DatabaseManager: Database operations and storage
- PerformanceAnalyzer: Performance metrics and analysis
"""

from .backtesting_engine import BacktestingEngine
from .database_manager import DatabaseManager
from .performance_analyzer import PerformanceAnalyzer

__all__ = ['BacktestingEngine', 'DatabaseManager', 'PerformanceAnalyzer']