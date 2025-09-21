"""
Trading Strategies Module

This module contains all trading strategy implementations and management utilities.
"""

from .strategy_manager import StrategyManager, BaseStrategy, BollingerBandsStrategy, MACrossoverStrategy

__all__ = ['StrategyManager', 'BaseStrategy', 'BollingerBandsStrategy', 'MACrossoverStrategy']