"""
Database Manager for Trading Backtesting System

This module handles SQLite database operations for storing:
- Trade logs (buy/sell transactions)
- Portfolio history (daily portfolio values)
- Performance metrics
"""

import sqlite3
import pandas as pd
from typing import Optional, Dict, Any
from datetime import datetime
import os


class DatabaseManager:
    """Manages SQLite database operations for backtesting data storage."""
    
    def __init__(self, db_file: str = "trading_log.db"):
        """
        Initialize the DatabaseManager.
        
        Args:
            db_file (str): Path to the SQLite database file
        """
        self.db_file = db_file
        self.setup_database()
    
    def setup_database(self) -> None:
        """Create the necessary tables if they don't exist."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            
            # Create trades table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_date TEXT NOT NULL,
                    trade_type TEXT NOT NULL,  -- 'BUY' or 'SELL'
                    price REAL NOT NULL,
                    shares REAL NOT NULL,
                    cash_change REAL NOT NULL,
                    portfolio_value REAL NOT NULL
                )
            """)
            
            # Create portfolio_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_history (
                    date TEXT PRIMARY KEY,
                    cash REAL NOT NULL,
                    holdings_value REAL NOT NULL,
                    total_value REAL NOT NULL,
                    shares_held REAL NOT NULL,
                    price REAL NOT NULL
                )
            """)
            
            # Create performance_metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backtest_date TEXT NOT NULL,
                    initial_capital REAL NOT NULL,
                    final_portfolio_value REAL NOT NULL,
                    total_return REAL NOT NULL,
                    total_trades INTEGER NOT NULL,
                    winning_trades INTEGER NOT NULL,
                    losing_trades INTEGER NOT NULL,
                    win_rate REAL NOT NULL,
                    max_drawdown REAL NOT NULL,
                    sharpe_ratio REAL
                )
            """)
            
            conn.commit()
    
    def clear_data(self) -> None:
        """Clear all data from the database tables."""
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM trades")
            cursor.execute("DELETE FROM portfolio_history")
            cursor.execute("DELETE FROM performance_metrics")
            conn.commit()
    
    def log_trade(self, trade_date: str, trade_type: str, price: float, 
                  shares: float, cash_change: float, portfolio_value: float) -> None:
        """
        Log a trade to the database.
        
        Args:
            trade_date (str): Date of the trade
            trade_type (str): 'BUY' or 'SELL'
            price (float): Price per share
            shares (float): Number of shares traded
            cash_change (float): Change in cash position
            portfolio_value (float): Total portfolio value after trade
        """
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO trades (trade_date, trade_type, price, shares, cash_change, portfolio_value)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (trade_date, trade_type, price, shares, cash_change, portfolio_value))
            conn.commit()
    
    def log_portfolio_status(self, date: str, cash: float, holdings_value: float, 
                           total_value: float, shares_held: float, price: float) -> None:
        """
        Log daily portfolio status to the database.
        
        Args:
            date (str): Date of the portfolio snapshot
            cash (float): Cash position
            holdings_value (float): Value of stock holdings
            total_value (float): Total portfolio value
            shares_held (float): Number of shares currently held
            price (float): Current stock price
        """
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO portfolio_history 
                (date, cash, holdings_value, total_value, shares_held, price)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (date, cash, holdings_value, total_value, shares_held, price))
            conn.commit()
    
    def log_performance_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        Log performance metrics to the database.
        
        Args:
            metrics (Dict[str, Any]): Dictionary containing performance metrics
        """
        with sqlite3.connect(self.db_file) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO performance_metrics 
                (backtest_date, initial_capital, final_portfolio_value, total_return,
                 total_trades, winning_trades, losing_trades, win_rate, max_drawdown, sharpe_ratio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                metrics['initial_capital'],
                metrics['final_portfolio_value'],
                metrics['total_return'],
                metrics['total_trades'],
                metrics['winning_trades'],
                metrics['losing_trades'],
                metrics['win_rate'],
                metrics['max_drawdown'],
                metrics.get('sharpe_ratio')
            ))
            conn.commit()
    
    def get_portfolio_history(self) -> pd.DataFrame:
        """
        Retrieve portfolio history as a pandas DataFrame.
        
        Returns:
            pd.DataFrame: Portfolio history with date as index
        """
        with sqlite3.connect(self.db_file) as conn:
            df = pd.read_sql(
                "SELECT * FROM portfolio_history ORDER BY date", 
                conn, 
                index_col='date', 
                parse_dates=['date']
            )
        return df
    
    def get_trades(self) -> pd.DataFrame:
        """
        Retrieve trade history as a pandas DataFrame.
        
        Returns:
            pd.DataFrame: Trade history with trade_date as index
        """
        with sqlite3.connect(self.db_file) as conn:
            df = pd.read_sql(
                "SELECT * FROM trades ORDER BY trade_date", 
                conn, 
                index_col='trade_date', 
                parse_dates=['trade_date']
            )
        return df
    
    def get_performance_metrics(self) -> pd.DataFrame:
        """
        Retrieve performance metrics as a pandas DataFrame.
        
        Returns:
            pd.DataFrame: Performance metrics history
        """
        with sqlite3.connect(self.db_file) as conn:
            df = pd.read_sql("SELECT * FROM performance_metrics ORDER BY backtest_date", conn)
        return df
    
    def database_exists(self) -> bool:
        """Check if the database file exists."""
        return os.path.exists(self.db_file)
    
    def get_last_backtest_summary(self) -> Optional[Dict[str, Any]]:
        """
        Get a summary of the last backtest run.
        
        Returns:
            Optional[Dict[str, Any]]: Dictionary with last backtest summary or None
        """
        try:
            portfolio_df = self.get_portfolio_history()
            trades_df = self.get_trades()
            
            if portfolio_df.empty:
                return None
                
            return {
                'final_portfolio_value': portfolio_df['total_value'].iloc[-1],
                'total_trades': len(trades_df),
                'date_range': f"{portfolio_df.index[0].strftime('%Y-%m-%d')} to {portfolio_df.index[-1].strftime('%Y-%m-%d')}",
                'last_update': portfolio_df.index[-1]
            }
        except Exception:
            return None