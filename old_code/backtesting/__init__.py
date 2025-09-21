"""
Backtesting module for algorithmic trading strategies.

This module provides a comprehensive backtesting framework with the following components:
- Database management for trade and portfolio logging
- Backtesting engine for strategy execution simulation
- Performance analysis and reporting tools
"""

__version__ = "1.0.0"
__author__ = "Trading System"

from .database_manager import DatabaseManager
from .backtesting_engine import BacktestingEngine
from .performance_analyzer import PerformanceAnalyzer

__all__ = ['DatabaseManager', 'BacktestingEngine', 'PerformanceAnalyzer']