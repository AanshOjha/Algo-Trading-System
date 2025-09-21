"""
Performance Analyzer for Trading Backtesting System

This module provides comprehensive performance analysis including:
- Risk metrics (Sharpe ratio, max drawdown, volatility)
- Trade analysis (win rate, profit factor, average returns)
- Visualization (equity curves, drawdown charts, trade distribution)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import warnings

from .database_manager import DatabaseManager


class PerformanceAnalyzer:
    """
    Comprehensive performance analysis for backtesting results.
    
    This class calculates various performance metrics and generates
    visualizations to evaluate trading strategy performance.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize the Performance Analyzer.
        
        Args:
            db_manager (DatabaseManager): Database manager instance for data access
        """
        self.db_manager = db_manager
        self.portfolio_df = None
        self.trades_df = None
        self.metrics = {}
        
    def analyze_performance(self, risk_free_rate: float = 0.02) -> Dict[str, Any]:
        """
        Perform comprehensive performance analysis.
        
        Args:
            risk_free_rate (float): Annual risk-free rate for Sharpe ratio calculation
            
        Returns:
            Dict[str, Any]: Dictionary containing all performance metrics
        """
        # Load data from database
        self.portfolio_df = self.db_manager.get_portfolio_history()
        self.trades_df = self.db_manager.get_trades()
        
        if self.portfolio_df.empty:
            raise ValueError("No portfolio data found. Run backtest first.")
        
        # Calculate all metrics
        basic_metrics = self._calculate_basic_metrics()
        risk_metrics = self._calculate_risk_metrics(risk_free_rate)
        trade_metrics = self._calculate_trade_metrics()
        drawdown_metrics = self._calculate_drawdown_metrics()
        
        # Combine all metrics
        self.metrics = {
            **basic_metrics,
            **risk_metrics,
            **trade_metrics,
            **drawdown_metrics
        }
        
        # Store metrics in database
        self.db_manager.log_performance_metrics(self.metrics)
        
        return self.metrics
    
    def _calculate_basic_metrics(self) -> Dict[str, float]:
        """Calculate basic performance metrics."""
        initial_value = self.portfolio_df['total_value'].iloc[0]
        final_value = self.portfolio_df['total_value'].iloc[-1]
        
        # Calculate returns
        total_return = ((final_value - initial_value) / initial_value) * 100
        
        # Calculate daily returns
        daily_returns = self.portfolio_df['total_value'].pct_change().dropna()
        
        # Annualized return (assuming 252 trading days)
        days = len(self.portfolio_df)
        if days > 1:
            annualized_return = ((final_value / initial_value) ** (252 / days) - 1) * 100
        else:
            annualized_return = 0
        
        return {
            'initial_capital': initial_value,
            'final_portfolio_value': final_value,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'total_days': days,
            'avg_daily_return': daily_returns.mean() * 100,
            'daily_volatility': daily_returns.std() * 100
        }
    
    def _calculate_risk_metrics(self, risk_free_rate: float) -> Dict[str, float]:
        """Calculate risk-adjusted performance metrics."""
        daily_returns = self.portfolio_df['total_value'].pct_change().dropna()
        
        if len(daily_returns) < 2:
            return {'sharpe_ratio': 0, 'annualized_volatility': 0}
        
        # Annualized volatility
        annualized_volatility = daily_returns.std() * np.sqrt(252) * 100
        
        # Sharpe ratio
        if annualized_volatility > 0:
            excess_return = self.metrics.get('annualized_return', 0) - risk_free_rate * 100
            sharpe_ratio = excess_return / annualized_volatility
        else:
            sharpe_ratio = 0
        
        # Sortino ratio (downside deviation)
        negative_returns = daily_returns[daily_returns < 0]
        if len(negative_returns) > 0:
            downside_deviation = negative_returns.std() * np.sqrt(252) * 100
            sortino_ratio = (self.metrics.get('annualized_return', 0) - risk_free_rate * 100) / downside_deviation if downside_deviation > 0 else 0
        else:
            sortino_ratio = float('inf') if self.metrics.get('annualized_return', 0) > risk_free_rate * 100 else 0
        
        return {
            'annualized_volatility': annualized_volatility,
            'sharpe_ratio': sharpe_ratio,
            'sortino_ratio': sortino_ratio
        }
    
    def _calculate_trade_metrics(self) -> Dict[str, Any]:
        """Calculate trade-specific metrics."""
        if self.trades_df.empty:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'largest_win': 0,
                'largest_loss': 0
            }
        
        # Pair buy and sell trades to calculate individual trade P&L
        buy_trades = self.trades_df[self.trades_df['trade_type'] == 'BUY'].copy()
        sell_trades = self.trades_df[self.trades_df['trade_type'] == 'SELL'].copy()
        
        trade_pnl = []
        for i, sell_trade in sell_trades.iterrows():
            # Find the corresponding buy trade (most recent before this sell)
            prev_buys = buy_trades[buy_trades.index < sell_trade.name]
            if not prev_buys.empty:
                buy_trade = prev_buys.iloc[-1]
                pnl = (sell_trade['price'] - buy_trade['price']) * sell_trade['shares']
                trade_pnl.append(pnl)
        
        if not trade_pnl:
            return {
                'total_trades': len(buy_trades),
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'largest_win': 0,
                'largest_loss': 0
            }
        
        trade_pnl = np.array(trade_pnl)
        winning_trades = trade_pnl[trade_pnl > 0]
        losing_trades = trade_pnl[trade_pnl < 0]
        
        total_trades = len(trade_pnl)
        win_count = len(winning_trades)
        loss_count = len(losing_trades)
        win_rate = (win_count / total_trades) * 100 if total_trades > 0 else 0
        
        avg_win = winning_trades.mean() if len(winning_trades) > 0 else 0
        avg_loss = abs(losing_trades.mean()) if len(losing_trades) > 0 else 0
        
        profit_factor = abs(winning_trades.sum() / losing_trades.sum()) if len(losing_trades) > 0 and losing_trades.sum() != 0 else float('inf')
        
        return {
            'total_trades': total_trades,
            'winning_trades': win_count,
            'losing_trades': loss_count,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'largest_win': winning_trades.max() if len(winning_trades) > 0 else 0,
            'largest_loss': abs(losing_trades.min()) if len(losing_trades) > 0 else 0
        }
    
    def _calculate_drawdown_metrics(self) -> Dict[str, float]:
        """Calculate drawdown metrics."""
        portfolio_values = self.portfolio_df['total_value']
        
        # Calculate running maximum (peak)
        peak = portfolio_values.expanding().max()
        
        # Calculate drawdown
        drawdown = (portfolio_values - peak) / peak * 100
        
        # Maximum drawdown
        max_drawdown = drawdown.min()
        
        # Current drawdown
        current_drawdown = drawdown.iloc[-1]
        
        # Average drawdown
        negative_drawdowns = drawdown[drawdown < 0]
        avg_drawdown = negative_drawdowns.mean() if len(negative_drawdowns) > 0 else 0
        
        return {
            'max_drawdown': abs(max_drawdown),
            'current_drawdown': abs(current_drawdown),
            'avg_drawdown': abs(avg_drawdown)
        }
    
    def print_performance_report(self) -> None:
        """Print a comprehensive performance report."""
        if not self.metrics:
            print("No metrics available. Run analyze_performance() first.")
            return
        
        print("\n" + "="*60)
        print("           BACKTESTING PERFORMANCE REPORT")
        print("="*60)
        
        # Basic Performance
        print(f"\n📊 BASIC PERFORMANCE")
        print(f"Initial Capital:      ${self.metrics['initial_capital']:,.2f}")
        print(f"Final Portfolio:      ${self.metrics['final_portfolio_value']:,.2f}")
        print(f"Total Return:         {self.metrics['total_return']:,.2f}%")
        print(f"Annualized Return:    {self.metrics['annualized_return']:.2f}%")
        print(f"Profit/Loss:          ${self.metrics['final_portfolio_value'] - self.metrics['initial_capital']:,.2f}")
        
        # Risk Metrics
        print(f"\n⚠️  RISK METRICS")
        print(f"Annualized Volatility: {self.metrics['annualized_volatility']:.2f}%")
        print(f"Sharpe Ratio:         {self.metrics['sharpe_ratio']:.3f}")
        print(f"Sortino Ratio:        {self.metrics['sortino_ratio']:.3f}")
        print(f"Max Drawdown:         {self.metrics['max_drawdown']:.2f}%")
        
        # Trade Analysis
        print(f"\n🔄 TRADE ANALYSIS")
        print(f"Total Trades:         {self.metrics['total_trades']}")
        print(f"Winning Trades:       {self.metrics['winning_trades']}")
        print(f"Losing Trades:        {self.metrics['losing_trades']}")
        print(f"Win Rate:             {self.metrics['win_rate']:.1f}%")
        print(f"Average Win:          ${self.metrics['avg_win']:,.2f}")
        print(f"Average Loss:         ${self.metrics['avg_loss']:,.2f}")
        print(f"Profit Factor:        {self.metrics['profit_factor']:.2f}")
        
        print("="*60)
    
    def plot_performance(self, save_path: Optional[str] = None, show_plot: bool = True) -> None:
        """
        Create comprehensive performance visualization.
        
        Args:
            save_path (Optional[str]): Path to save the plot
            show_plot (bool): Whether to display the plot
        """
        if self.portfolio_df.empty:
            print("No data available for plotting.")
            return
        
        # Create subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Backtesting Performance Analysis', fontsize=16, fontweight='bold')
        
        # 1. Equity Curve
        ax1.plot(self.portfolio_df.index, self.portfolio_df['total_value'], 'b-', linewidth=2, label='Portfolio Value')
        ax1.axhline(y=self.metrics['initial_capital'], color='gray', linestyle='--', alpha=0.7, label='Initial Capital')
        ax1.set_title('Equity Curve')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. Drawdown Chart
        portfolio_values = self.portfolio_df['total_value']
        peak = portfolio_values.expanding().max()
        drawdown = (portfolio_values - peak) / peak * 100
        
        ax2.fill_between(self.portfolio_df.index, drawdown, 0, color='red', alpha=0.3)
        ax2.plot(self.portfolio_df.index, drawdown, 'r-', linewidth=1)
        ax2.set_title('Drawdown (%)')
        ax2.set_ylabel('Drawdown (%)')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Daily Returns Distribution
        daily_returns = self.portfolio_df['total_value'].pct_change().dropna() * 100
        ax3.hist(daily_returns, bins=30, alpha=0.7, color='skyblue', edgecolor='black')
        ax3.axvline(daily_returns.mean(), color='red', linestyle='--', label=f'Mean: {daily_returns.mean():.3f}%')
        ax3.set_title('Daily Returns Distribution')
        ax3.set_xlabel('Daily Return (%)')
        ax3.set_ylabel('Frequency')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. Trade Analysis
        if not self.trades_df.empty:
            buy_trades = self.trades_df[self.trades_df['trade_type'] == 'BUY']
            sell_trades = self.trades_df[self.trades_df['trade_type'] == 'SELL']
            
            ax4.scatter(buy_trades.index, buy_trades['price'], color='green', marker='^', s=50, label='Buy', alpha=0.7)
            ax4.scatter(sell_trades.index, sell_trades['price'], color='red', marker='v', s=50, label='Sell', alpha=0.7)
            ax4.plot(self.portfolio_df.index, self.portfolio_df['price'], 'b-', alpha=0.5, linewidth=1, label='Price')
            ax4.set_title('Trade Entry/Exit Points')
            ax4.set_ylabel('Price ($)')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            ax4.tick_params(axis='x', rotation=45)
        else:
            ax4.text(0.5, 0.5, 'No trades executed', transform=ax4.transAxes, 
                    ha='center', va='center', fontsize=12)
            ax4.set_title('Trade Entry/Exit Points')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Performance chart saved to: {save_path}")
        
        if show_plot:
            plt.show()
        else:
            plt.close()
    
    def export_results(self, export_path: str = "backtest_results.csv") -> None:
        """
        Export detailed results to CSV file.
        
        Args:
            export_path (str): Path for the exported CSV file
        """
        if self.portfolio_df.empty:
            print("No data available for export.")
            return
        
        # Combine portfolio and trade data
        export_df = self.portfolio_df.copy()
        
        # Add trade indicators
        if not self.trades_df.empty:
            export_df['trade_type'] = ''
            export_df['trade_price'] = np.nan
            export_df['trade_shares'] = np.nan
            
            for date, trade in self.trades_df.iterrows():
                if date in export_df.index:
                    export_df.loc[date, 'trade_type'] = trade['trade_type']
                    export_df.loc[date, 'trade_price'] = trade['price']
                    export_df.loc[date, 'trade_shares'] = trade['shares']
        
        # Calculate additional metrics
        export_df['daily_return'] = export_df['total_value'].pct_change() * 100
        export_df['cumulative_return'] = ((export_df['total_value'] / export_df['total_value'].iloc[0]) - 1) * 100
        
        # Export to CSV
        export_df.to_csv(export_path)
        print(f"Detailed results exported to: {export_path}")
    
    def export_trade_analysis(self, export_path: str = "trade_analysis.csv") -> None:
        """
        Export detailed trade analysis with Entry Date, Entry Price, Exit Date, Exit Price, Shares, and Profit/Loss per trade.
        
        Args:
            export_path (str): Path for the exported CSV file
        """
        if self.trades_df.empty:
            print("No trades available for export.")
            return
        
        # Pair buy and sell trades
        buy_trades = self.trades_df[self.trades_df['trade_type'] == 'BUY'].copy()
        sell_trades = self.trades_df[self.trades_df['trade_type'] == 'SELL'].copy()
        
        trade_analysis = []
        
        for i, sell_trade in sell_trades.iterrows():
            # Find the corresponding buy trade (most recent before this sell)
            prev_buys = buy_trades[buy_trades.index < sell_trade.name]
            if not prev_buys.empty:
                buy_trade = prev_buys.iloc[-1]
                
                # Calculate profit/loss
                profit_loss = (sell_trade['price'] - buy_trade['price']) * sell_trade['shares']
                profit_loss_pct = ((sell_trade['price'] - buy_trade['price']) / buy_trade['price']) * 100
                
                trade_analysis.append({
                    'Trade_Number': len(trade_analysis) + 1,
                    'Entry_Date': buy_trade.name,  # trade_date is the index
                    'Entry_Price': buy_trade['price'],
                    'Exit_Date': sell_trade.name,  # trade_date is the index
                    'Exit_Price': sell_trade['price'],
                    'Shares': sell_trade['shares'],
                    'Profit_Loss_Dollar': profit_loss,
                    'Profit_Loss_Percent': profit_loss_pct,
                    'Trade_Duration_Days': (pd.to_datetime(sell_trade.name) - pd.to_datetime(buy_trade.name)).days,
                    'Trade_Type': 'Win' if profit_loss > 0 else 'Loss'
                })
        
        if trade_analysis:
            trade_df = pd.DataFrame(trade_analysis)
            trade_df.to_csv(export_path, index=False)
            print(f"Trade analysis exported to: {export_path}")
            
            # Display summary
            print(f"\n📋 TRADE ANALYSIS SUMMARY:")
            print(f"   Total Completed Trades: {len(trade_analysis)}")
            if trade_analysis:
                wins = [t for t in trade_analysis if t['Trade_Type'] == 'Win']
                losses = [t for t in trade_analysis if t['Trade_Type'] == 'Loss']
                print(f"   Winning Trades: {len(wins)}")
                print(f"   Losing Trades: {len(losses)}")
                print(f"   Total P&L: ${sum(t['Profit_Loss_Dollar'] for t in trade_analysis):,.2f}")
                print(f"   Best Trade: ${max(t['Profit_Loss_Dollar'] for t in trade_analysis):,.2f}")
                print(f"   Worst Trade: ${min(t['Profit_Loss_Dollar'] for t in trade_analysis):,.2f}")
            
            # Also print summary to console
            print(f"\n📋 INDIVIDUAL TRADE ANALYSIS:")
            print("=" * 80)
            for _, trade in trade_df.iterrows():
                print(f"Trade #{int(trade['Trade_Number'])}: {trade['Entry_Date']} → {trade['Exit_Date']}")
                print(f"   Entry: ${trade['Entry_Price']:.2f} | Exit: ${trade['Exit_Price']:.2f} | Shares: {trade['Shares']:.2f}")
                print(f"   P&L: ${trade['Profit_Loss_Dollar']:.2f} ({trade['Profit_Loss_Percent']:+.2f}%) | Duration: {int(trade['Trade_Duration_Days'])} days")
                print(f"   Result: {trade['Trade_Type']}")
                print()
        else:
            print("No completed trades found for analysis.")
    
    def get_metrics_summary(self) -> str:
        """
        Get a formatted string summary of key metrics.
        
        Returns:
            str: Formatted metrics summary
        """
        if not self.metrics:
            return "No metrics available. Run analyze_performance() first."
        
        return f"""
        Total Return: {self.metrics['total_return']:.2f}%
        Annualized Return: {self.metrics['annualized_return']:.2f}%
        Sharpe Ratio: {self.metrics['sharpe_ratio']:.3f}
        Max Drawdown: {self.metrics['max_drawdown']:.2f}%
        Win Rate: {self.metrics['win_rate']:.1f}%
        Total Trades: {self.metrics['total_trades']}
        """.strip()