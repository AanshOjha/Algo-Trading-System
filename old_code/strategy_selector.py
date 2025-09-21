"""
Strategy Selector Module

This module provides a unified interface for loading and managing different trading strategies.
It handles strategy-specific configurations and normalizes signals for the backtesting engine.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import importlib.util
import sys
from abc import ABC, abstractmethod


class StrategyConfig:
    """Configuration class for trading strategies."""
    
    def __init__(self, name: str, description: str, parameters: Dict[str, Any]):
        self.name = name
        self.description = description
        self.parameters = parameters
        
    def __repr__(self):
        return f"StrategyConfig(name='{self.name}', parameters={self.parameters})"


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""
    
    def __init__(self, config: StrategyConfig):
        self.config = config
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
    
    def generate_signals(self) -> pd.DataFrame:
        """Generate Bollinger Bands signals."""
        # Import and execute the bollinger bands script
        try:
            from strategies.bollinger_bands import signals_bb
            self.signals_df = signals_bb.copy()
            
            # Ensure required columns exist
            required_cols = ['price', 'middle_band', 'signal']
            for col in required_cols:
                if col not in self.signals_df.columns:
                    raise ValueError(f"Missing required column '{col}' in Bollinger Bands signals")
            
            # Standardize signal format (ensure only 1.0 for buy, 0.0 for no signal)
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
    
    def generate_signals(self) -> pd.DataFrame:
        """Generate MA Crossover signals."""
        try:
            from strategies.ma_crossover import signals_ma
            self.signals_df = signals_ma.copy()
            
            # Convert MA crossover signals to standard format
            # MA strategy uses continuous signals (1.0 for uptrend, -1.0 for downtrend)
            # We need discrete entry signals (1.0 for buy entry, 0.0 for no action)
            
            # Create standardized signals DataFrame
            standardized_df = pd.DataFrame(index=self.signals_df.index)
            standardized_df['price'] = self.signals_df['price']
            
            # Add MA data for exit conditions
            standardized_df['short_ma'] = self.signals_df['short_ma']
            standardized_df['long_ma'] = self.signals_df['long_ma']
            
            # Generate entry signals only at crossover points
            # Buy signal: when short MA crosses above long MA (transition from -1 to 1)
            standardized_df['signal'] = 0.0
            
            # Find crossover points using the positions column
            crossover_points = self.signals_df['positions'].fillna(0.0)
            
            # Buy signal when positions == 2.0 (crossover from bearish to bullish)
            buy_signals = crossover_points == 2.0
            standardized_df.loc[buy_signals, 'signal'] = 1.0
            
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


class StrategySelector:
    """Main strategy selector and manager."""
    
    def __init__(self):
        self.strategies = {}
        self.current_strategy = None
        self._load_default_strategies()
    
    def _load_default_strategies(self):
        """Load default strategy configurations."""
        
        # Bollinger Bands configuration
        bb_config = StrategyConfig(
            name="bollinger_bands",
            description="Bollinger Bands strategy with trend filter",
            parameters={
                "window": 20,
                "std_dev": 2,
                "trend_window": 200,
                "entry_condition": "Price bounces from lower band",
                "exit_condition": "Price reaches middle band"
            }
        )
        self.strategies["bollinger_bands"] = BollingerBandsStrategy(bb_config)
        
        # MA Crossover configuration
        ma_config = StrategyConfig(
            name="ma_crossover",
            description="Moving Average Crossover strategy",
            parameters={
                "short_window": 50,
                "long_window": 200,
                "ma_type": "EMA",
                "entry_condition": "Short MA crosses above Long MA",
                "exit_condition": "Short MA crosses below Long MA"
            }
        )
        self.strategies["ma_crossover"] = MACrossoverStrategy(ma_config)
    
    def list_strategies(self) -> Dict[str, StrategyConfig]:
        """List all available strategies."""
        return {name: strategy.config for name, strategy in self.strategies.items()}
    
    def select_strategy(self, strategy_name: str) -> BaseStrategy:
        """Select and return a strategy."""
        if strategy_name not in self.strategies:
            available = list(self.strategies.keys())
            raise ValueError(f"Strategy '{strategy_name}' not found. Available: {available}")
        
        self.current_strategy = self.strategies[strategy_name]
        return self.current_strategy
    
    def get_strategy_signals(self, strategy_name: str) -> pd.DataFrame:
        """Get signals for a specific strategy."""
        strategy = self.select_strategy(strategy_name)
        return strategy.generate_signals()
    
    def get_strategy_info(self, strategy_name: str) -> Dict[str, Any]:
        """Get detailed information about a strategy."""
        if strategy_name not in self.strategies:
            raise ValueError(f"Strategy '{strategy_name}' not found")
        
        strategy = self.strategies[strategy_name]
        config = strategy.config
        
        return {
            "name": config.name,
            "description": config.description,
            "parameters": config.parameters,
            "class": strategy.__class__.__name__
        }
    
    def validate_strategy_signals(self, strategy_name: str) -> Tuple[bool, str]:
        """Validate that a strategy's signals are properly formatted."""
        try:
            signals_df = self.get_strategy_signals(strategy_name)
            
            # Check required columns
            required_columns = ['price', 'signal']
            missing_columns = [col for col in required_columns if col not in signals_df.columns]
            
            if missing_columns:
                return False, f"Missing required columns: {missing_columns}"
            
            # Check for NaN values in critical columns
            if signals_df['price'].isna().all():
                return False, "Price column contains only NaN values"
            
            if signals_df['signal'].isna().all():
                return False, "Signal column contains only NaN values"
            
            # Check signal format (should be 0.0 or 1.0)
            unique_signals = signals_df['signal'].dropna().unique()
            valid_signals = set([0.0, 1.0])
            
            if not set(unique_signals).issubset(valid_signals):
                return False, f"Invalid signal values: {unique_signals}. Expected: {valid_signals}"
            
            # Check for buy signals
            buy_signals = (signals_df['signal'] == 1.0).sum()
            if buy_signals == 0:
                return False, "No buy signals found in the data"
            
            return True, f"Strategy validated successfully. {buy_signals} buy signals found."
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"


def print_strategy_comparison():
    """Print a comparison of available strategies."""
    selector = StrategySelector()
    strategies = selector.list_strategies()
    
    print("\n" + "="*80)
    print("                    AVAILABLE TRADING STRATEGIES")
    print("="*80)
    
    for name, config in strategies.items():
        print(f"\n📈 {config.name.upper().replace('_', ' ')}")
        print(f"   Description: {config.description}")
        print(f"   Entry: {config.parameters.get('entry_condition', 'N/A')}")
        print(f"   Exit: {config.parameters.get('exit_condition', 'N/A')}")
        print(f"   Parameters: {', '.join([f'{k}={v}' for k, v in config.parameters.items() if k not in ['entry_condition', 'exit_condition']])}")
    
    print("="*80)


if __name__ == "__main__":
    # Test the strategy selector
    print_strategy_comparison()
    
    selector = StrategySelector()
    
    # Test each strategy
    for strategy_name in selector.list_strategies().keys():
        print(f"\n🧪 Testing {strategy_name}...")
        is_valid, message = selector.validate_strategy_signals(strategy_name)
        print(f"   {'✅' if is_valid else '❌'} {message}")