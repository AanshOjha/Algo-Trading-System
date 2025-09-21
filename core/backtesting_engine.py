"""
Backtesting Engine for Trading Strategies

This module implements the core backtesting logic based on the provided pseudocode.
It handles portfolio management, trade execution, and signal processing.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
import warnings

from .database_manager import DatabaseManager


class BacktestingEngine:
    """
    Core backtesting engine that executes trading strategies and tracks portfolio performance.
    
    This engine follows the pseudocode logic:
    1. Check for exits first (if holding position)
    2. Check for entries (if not holding position)
    3. Log all trades and portfolio status to database
    """
    
    def __init__(self, initial_capital: float = 100000.0, db_file: str = "trading_log.db", strategy=None):
        """
        Initialize the backtesting engine.
        
        Args:
            initial_capital (float): Starting capital for the backtest
            db_file (str): Database file for storing results
            strategy: Strategy object with exit condition logic
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.position_shares = 0.0
        self.last_portfolio_value = initial_capital
        
        # Initialize database manager
        self.db_manager = DatabaseManager(db_file)
        
        # Strategy for custom exit conditions
        self.strategy = strategy
        
        # Tracking variables
        self.current_date = None
        self.current_price = 0.0
        self.current_row = None
        
        # Performance tracking
        self.trades_executed = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.entry_price = 0.0
        
    def run_backtest(self, signals_df: pd.DataFrame, verbose: bool = True) -> Dict[str, Any]:
        """
        Run the complete backtest on the provided signals DataFrame.
        
        Args:
            signals_df (pd.DataFrame): DataFrame with columns: 'price', 'middle_band', 'signal'
            verbose (bool): Whether to print trade execution details
            
        Returns:
            Dict[str, Any]: Summary of backtest results
        """
        if verbose:
            print("Starting backtest...")
            print(f"Initial capital: ${self.initial_capital:,.2f}")
        
        # Clear previous data
        self.db_manager.clear_data()
        
        # Reset portfolio state
        self.cash = self.initial_capital
        self.position_shares = 0.0
        self.trades_executed = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
        # Validate required columns
        required_columns = ['price', 'signal']
        missing_columns = [col for col in required_columns if col not in signals_df.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns: {missing_columns}")
        
        # Main backtesting loop - start from second day to avoid NaN values
        for i, (date, row) in enumerate(signals_df.iloc[1:].iterrows(), 1):
            self.current_date = date.strftime('%Y-%m-%d') if hasattr(date, 'strftime') else str(date)
            self.current_price = row['price']
            self.current_row = row
            middle_band = row.get('middle_band', None)
            entry_signal = row['signal']
            
            # Skip if we have NaN values
            if pd.isna(self.current_price):
                continue
            
            # --- 4. CHECK FOR EXITS FIRST (if we hold a position) ---
            if self.position_shares > 0:
                self._check_exit_conditions(row, verbose)
            
            # --- 5. CHECK FOR ENTRIES (if we DO NOT hold a position) ---
            elif entry_signal == 1.0:  # BUY signal
                self._execute_buy(verbose)
            
            # --- 6. END-OF-DAY PORTFOLIO UPDATE ---
            self._update_portfolio_status()
        
        # Generate final summary
        summary = self._generate_summary(verbose)
        
        if verbose:
            print("Backtest complete!")
            
        return summary
    
    def _check_exit_conditions(self, row_data: pd.Series, verbose: bool) -> None:
        """
        Check if exit conditions are met and execute sell if necessary.
        
        Args:
            row_data (pd.Series): Current row data containing price and indicators
            verbose (bool): Whether to print execution details
        """
        should_exit = False
        
        if self.strategy and hasattr(self.strategy, 'get_exit_condition'):
            # Use strategy-specific exit condition
            should_exit = self.strategy.get_exit_condition(
                current_price=self.current_price,
                position_entry_price=self.entry_price,
                row_data=row_data
            )
        else:
            # Default exit condition: price >= middle_band (for Bollinger Bands)
            middle_band = row_data.get('middle_band', None)
            if middle_band is not None and not pd.isna(middle_band):
                should_exit = self.current_price >= middle_band
        
        if should_exit:
            self._execute_sell(verbose)
    
    def _execute_buy(self, verbose: bool) -> None:
        """
        Execute a BUY order with all available cash.
        
        Args:
            verbose (bool): Whether to print execution details
        """
        if self.cash <= 0:
            return
            
        # Calculate shares to buy with all available cash
        shares_to_buy = self.cash / self.current_price
        cash_spent = shares_to_buy * self.current_price
        
        # Update position
        self.position_shares = shares_to_buy
        self.cash = 0.0  # Invest all available cash
        self.entry_price = self.current_price
        
        # Calculate portfolio value after trade
        portfolio_value = self.cash + (self.position_shares * self.current_price)
        
        # Log the trade
        self.db_manager.log_trade(
            trade_date=self.current_date,
            trade_type='BUY',
            price=self.current_price,
            shares=shares_to_buy,
            cash_change=-cash_spent,
            portfolio_value=portfolio_value
        )
        
        self.trades_executed += 1
        
        if verbose:
            print(f"Executing BUY at ${self.current_price:.2f} on {self.current_date}")
            print(f"  Shares bought: {shares_to_buy:.2f}")
            print(f"  Cash spent: ${cash_spent:.2f}")
    
    def _execute_sell(self, verbose: bool) -> None:
        """
        Execute a SELL order for all held shares.
        
        Args:
            verbose (bool): Whether to print execution details
        """
        if self.position_shares <= 0:
            return
            
        # Calculate cash received
        cash_received = self.position_shares * self.current_price
        shares_sold = self.position_shares
        
        # Track win/loss
        if self.current_price > self.entry_price:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        # Update position
        self.cash += cash_received
        self.position_shares = 0.0
        
        # Calculate portfolio value after trade
        portfolio_value = self.cash + (self.position_shares * self.current_price)
        
        # Log the trade
        self.db_manager.log_trade(
            trade_date=self.current_date,
            trade_type='SELL',
            price=self.current_price,
            shares=shares_sold,
            cash_change=cash_received,
            portfolio_value=portfolio_value
        )
        
        self.trades_executed += 1
        
        if verbose:
            print(f"Executing SELL at ${self.current_price:.2f} on {self.current_date}")
            print(f"  Shares sold: {shares_sold:.2f}")
            print(f"  Cash received: ${cash_received:.2f}")
            print(f"  Trade P&L: ${cash_received - (shares_sold * self.entry_price):.2f}")
    
    def _update_portfolio_status(self) -> None:
        """Update and log the current portfolio status."""
        current_holdings_value = self.position_shares * self.current_price
        total_portfolio_value = self.cash + current_holdings_value
        
        # Log daily portfolio status
        self.db_manager.log_portfolio_status(
            date=self.current_date,
            cash=self.cash,
            holdings_value=current_holdings_value,
            total_value=total_portfolio_value,
            shares_held=self.position_shares,
            price=self.current_price
        )
        
        self.last_portfolio_value = total_portfolio_value
    
    def _generate_summary(self, verbose: bool) -> Dict[str, Any]:
        """
        Generate a summary of the backtest results.
        
        Args:
            verbose (bool): Whether to print summary details
            
        Returns:
            Dict[str, Any]: Summary statistics
        """
        final_portfolio_value = self.last_portfolio_value
        total_return = ((final_portfolio_value - self.initial_capital) / self.initial_capital) * 100
        win_rate = (self.winning_trades / max(self.trades_executed, 1)) * 100 if self.trades_executed > 0 else 0
        
        summary = {
            'initial_capital': self.initial_capital,
            'final_portfolio_value': final_portfolio_value,
            'total_return': total_return,
            'total_trades': self.trades_executed,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'profit_loss': final_portfolio_value - self.initial_capital
        }
        
        if verbose:
            print(f"\n--- BACKTEST SUMMARY ---")
            print(f"Initial Capital: ${summary['initial_capital']:,.2f}")
            print(f"Final Portfolio Value: ${summary['final_portfolio_value']:,.2f}")
            print(f"Total Return: {summary['total_return']:.2f}%")
            print(f"Profit/Loss: ${summary['profit_loss']:,.2f}")
            print(f"Total Trades: {summary['total_trades']}")
            print(f"Winning Trades: {summary['winning_trades']}")
            print(f"Losing Trades: {summary['losing_trades']}")
            print(f"Win Rate: {summary['win_rate']:.1f}%")
        
        return summary
    
    def get_portfolio_history(self) -> pd.DataFrame:
        """Get the portfolio history from database."""
        return self.db_manager.get_portfolio_history()
    
    def get_trades(self) -> pd.DataFrame:
        """Get the trade history from database."""
        return self.db_manager.get_trades()
    
    def get_current_position(self) -> Dict[str, float]:
        """
        Get current position information.
        
        Returns:
            Dict[str, float]: Current cash, shares, and portfolio value
        """
        return {
            'cash': self.cash,
            'shares': self.position_shares,
            'portfolio_value': self.cash + (self.position_shares * self.current_price)
        }