"""
Strategy Manager for Trading System

This module provides a clean interface for managing trading strategies.
It simplifies strategy selection and signal generation.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import pandas as pd
import numpy as np


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.signals_df = None
        
    @abstractmethod
    def generate_signals(self) -> pd.DataFrame:
        """Generate trading signals. Must return DataFrame with standardized format."""
        pass
    
    @abstractmethod
    def get_exit_condition(self, current_price: float, position_entry_price: float, 
                          row_data: pd.Series) -> bool:
        """Define custom exit conditions for this strategy."""
        pass


class BollingerBandsStrategy(BaseStrategy):
    """Bollinger Bands strategy implementation."""
    
    def __init__(self):
        super().__init__(
            name="Bollinger Bands",
            description="Entry on lower band bounce, exit on middle band cross"
        )
    
    def generate_signals(self) -> pd.DataFrame:
        """Generate Bollinger Bands signals."""
        try:
            from strategies.bollinger_bands import signals_bb
            self.signals_df = signals_bb.copy()
            
            # Ensure required columns exist
            required_cols = ['price', 'middle_band', 'signal']
            for col in required_cols:
                if col not in self.signals_df.columns:
                    raise ValueError(f"Missing required column '{col}' in Bollinger Bands signals")
            
            # Standardize signal format
            self.signals_df['signal'] = self.signals_df['signal'].fillna(0.0)
            self.signals_df['signal'] = np.where(self.signals_df['signal'] == 1.0, 1.0, 0.0)
            
            return self.signals_df
            
        except ImportError as e:
            raise ImportError(f"Could not import Bollinger Bands strategy: {e}")
    
    def get_exit_condition(self, current_price: float, position_entry_price: float, 
                          row_data: pd.Series) -> bool:
        """Exit when price reaches middle band."""
        middle_band = row_data.get('middle_band', 0)
        return current_price >= middle_band


class MACrossoverStrategy(BaseStrategy):
    """Moving Average Crossover strategy implementation."""
    
    def __init__(self):
        super().__init__(
            name="Moving Average Crossover",
            description="Entry on MA crossover, exit on reverse crossover"
        )
    
    def generate_signals(self) -> pd.DataFrame:
        """Generate MA Crossover signals."""
        try:
            from strategies.ma_crossover import signals_ma
            self.signals_df = signals_ma.copy()
            
            # Convert MA crossover signals to standard format
            standardized_df = pd.DataFrame(index=self.signals_df.index)
            standardized_df['price'] = self.signals_df['price']
            standardized_df['short_ma'] = self.signals_df['short_ma']
            standardized_df['long_ma'] = self.signals_df['long_ma']
            
            # Generate entry signals (buy when short MA crosses above long MA)
            ma_diff = self.signals_df['short_ma'] - self.signals_df['long_ma']
            ma_diff_prev = ma_diff.shift(1)
            
            # Entry signal: crossover from negative to positive
            entry_signals = ((ma_diff > 0) & (ma_diff_prev <= 0)).astype(float)
            standardized_df['signal'] = entry_signals
            
            self.signals_df = standardized_df
            return self.signals_df
            
        except ImportError as e:
            raise ImportError(f"Could not import MA Crossover strategy: {e}")
    
    def get_exit_condition(self, current_price: float, position_entry_price: float, 
                          row_data: pd.Series) -> bool:
        """Exit when short MA crosses below long MA."""
        short_ma = row_data.get('short_ma', 0)
        long_ma = row_data.get('long_ma', 0)
        return short_ma < long_ma


class StrategyManager:
    """Main strategy manager for selecting and running strategies."""
    
    def __init__(self):
        self.strategies = {
            'bollinger_bands': BollingerBandsStrategy(),
            'ma_crossover': MACrossoverStrategy()
        }
    
    def list_strategies(self) -> Dict[str, str]:
        """List all available strategies."""
        return {name: strategy.description for name, strategy in self.strategies.items()}
    
    def get_strategy(self, strategy_name: str) -> BaseStrategy:
        """Get a strategy by name."""
        if strategy_name not in self.strategies:
            available = list(self.strategies.keys())
            raise ValueError(f"Strategy '{strategy_name}' not found. Available: {available}")
        
        return self.strategies[strategy_name]
    
    def validate_strategy(self, strategy_name: str) -> bool:
        """Validate that a strategy can generate signals."""
        try:
            strategy = self.get_strategy(strategy_name)
            signals = strategy.generate_signals()
            
            # Check for required columns
            required_cols = ['price', 'signal']
            for col in required_cols:
                if col not in signals.columns:
                    raise ValueError(f"Missing required column '{col}'")
            
            # Check for valid signals
            if signals['signal'].sum() == 0:
                raise ValueError("No buy signals generated")
            
            return True
            
        except Exception as e:
            raise ValueError(f"Strategy validation failed: {e}")