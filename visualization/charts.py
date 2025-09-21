"""
Chart and Visualization Module

This module handles all chart generation and visualization for the trading system.
It provides clean, easy-to-understand charts for strategy analysis and performance.
"""

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from typing import Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class ChartGenerator:
    """Generates charts for trading strategy analysis and performance."""
    
    def __init__(self, style: str = 'seaborn-v0_8'):
        """
        Initialize the chart generator.
        
        Args:
            style (str): Matplotlib style to use
        """
        try:
            plt.style.use(style)
        except:
            plt.style.use('default')
        
        self.colors = {
            'price': '#2E86AB',
            'ma_short': '#A23B72',
            'ma_long': '#F18F01',
            'bollinger_upper': '#C73E1D',
            'bollinger_middle': '#F18F01',
            'bollinger_lower': '#2E86AB',
            'buy_signal': '#2ECC71',
            'sell_signal': '#E74C3C',
            'portfolio': '#3498DB',
            'drawdown': '#E74C3C'
        }
    
    def plot_strategy_signals(self, signals_df: pd.DataFrame, strategy_name: str, 
                            save_path: Optional[str] = None, show: bool = True) -> None:
        """
        Plot strategy signals with entry/exit points.
        
        Args:
            signals_df (pd.DataFrame): DataFrame with price, signals, and indicator data
            strategy_name (str): Name of the strategy for the title
            save_path (str, optional): Path to save the chart
            show (bool): Whether to display the chart
        """
        fig, ax = plt.subplots(figsize=(15, 8))
        
        # Plot price
        ax.plot(signals_df.index, signals_df['price'], 
                label='Price', color=self.colors['price'], linewidth=1.5)
        
        if strategy_name.lower() == 'bollinger bands':
            self._plot_bollinger_bands(ax, signals_df)
        elif strategy_name.lower() == 'moving average crossover':
            self._plot_ma_crossover(ax, signals_df)
        
        # Plot buy signals
        buy_signals = signals_df[signals_df['signal'] == 1.0]
        if not buy_signals.empty:
            ax.scatter(buy_signals.index, buy_signals['price'], 
                      marker='^', s=100, color=self.colors['buy_signal'], 
                      label='Buy Signal', zorder=5)
        
        # Formatting
        ax.set_title(f'{strategy_name} - Trading Signals', fontsize=16, fontweight='bold')
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Price ($)', fontsize=12)
        ax.legend(loc='upper left')
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show:
            plt.show()
        else:
            plt.close()
    
    def _plot_bollinger_bands(self, ax, signals_df: pd.DataFrame) -> None:
        """Plot Bollinger Bands indicators."""
        if 'upper_band' in signals_df.columns:
            ax.plot(signals_df.index, signals_df['upper_band'], 
                   label='Upper Band', color=self.colors['bollinger_upper'], 
                   linestyle='--', alpha=0.7)
        
        if 'middle_band' in signals_df.columns:
            ax.plot(signals_df.index, signals_df['middle_band'], 
                   label='Middle Band (SMA)', color=self.colors['bollinger_middle'], 
                   linestyle='-', alpha=0.8)
        
        if 'lower_band' in signals_df.columns:
            ax.plot(signals_df.index, signals_df['lower_band'], 
                   label='Lower Band', color=self.colors['bollinger_lower'], 
                   linestyle='--', alpha=0.7)
        
        # Fill between bands
        if all(col in signals_df.columns for col in ['upper_band', 'lower_band']):
            ax.fill_between(signals_df.index, 
                          signals_df['upper_band'], signals_df['lower_band'],
                          alpha=0.1, color=self.colors['bollinger_middle'])
    
    def _plot_ma_crossover(self, ax, signals_df: pd.DataFrame) -> None:
        """Plot Moving Average indicators."""
        if 'short_ma' in signals_df.columns:
            ax.plot(signals_df.index, signals_df['short_ma'], 
                   label='50-day MA', color=self.colors['ma_short'], 
                   linewidth=1.5, alpha=0.8)
        
        if 'long_ma' in signals_df.columns:
            ax.plot(signals_df.index, signals_df['long_ma'], 
                   label='200-day MA', color=self.colors['ma_long'], 
                   linewidth=1.5, alpha=0.8)
    
    def plot_performance_summary(self, portfolio_df: pd.DataFrame, trades_df: pd.DataFrame,
                               metrics: dict, strategy_name: str,
                               save_path: Optional[str] = None, show: bool = True) -> None:
        """
        Plot comprehensive performance summary with multiple subplots.
        
        Args:
            portfolio_df (pd.DataFrame): Portfolio value over time
            trades_df (pd.DataFrame): Individual trades data
            metrics (dict): Performance metrics
            strategy_name (str): Strategy name for title
            save_path (str, optional): Path to save the chart
            show (bool): Whether to display the chart
        """
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # 1. Portfolio Value Over Time
        portfolio_col = 'total_value' if 'total_value' in portfolio_df.columns else 'portfolio_value'
        ax1.plot(portfolio_df.index, portfolio_df[portfolio_col], 
                color=self.colors['portfolio'], linewidth=2)
        ax1.set_title('Portfolio Value Over Time', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Portfolio Value ($)')
        ax1.grid(True, alpha=0.3)
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        
        # 2. Drawdown Chart
        portfolio_peak = portfolio_df[portfolio_col].expanding().max()
        drawdown = (portfolio_df[portfolio_col] - portfolio_peak) / portfolio_peak * 100
        
        ax2.fill_between(portfolio_df.index, drawdown, 0, 
                        color=self.colors['drawdown'], alpha=0.7)
        ax2.set_title('Drawdown (%)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Drawdown (%)')
        ax2.grid(True, alpha=0.3)
        ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        
        # 3. Trade Distribution
        if not trades_df.empty:
            # Calculate profit/loss from cash_change for sell trades
            sell_trades = trades_df[trades_df['trade_type'] == 'SELL']
            if not sell_trades.empty and 'cash_change' in trades_df.columns:
                profit_loss = sell_trades['cash_change']
                wins = profit_loss[profit_loss > 0]
                losses = profit_loss[profit_loss < 0]
                
                if len(wins) > 0 or len(losses) > 0:
                    ax3.hist([wins, losses], bins=20, color=[self.colors['buy_signal'], self.colors['sell_signal']], 
                            alpha=0.7, label=['Wins', 'Losses'])
                    ax3.set_title('Trade P&L Distribution', fontsize=14, fontweight='bold')
                    ax3.set_xlabel('Profit/Loss ($)')
                    ax3.set_ylabel('Number of Trades')
                    ax3.legend()
                    ax3.grid(True, alpha=0.3)
                else:
                    ax3.text(0.5, 0.5, 'No completed trades', ha='center', va='center', transform=ax3.transAxes)
                    ax3.set_title('Trade P&L Distribution', fontsize=14, fontweight='bold')
            else:
                ax3.text(0.5, 0.5, 'No trade data available', ha='center', va='center', transform=ax3.transAxes)
                ax3.set_title('Trade P&L Distribution', fontsize=14, fontweight='bold')
        else:
            ax3.text(0.5, 0.5, 'No trades found', ha='center', va='center', transform=ax3.transAxes)
            ax3.set_title('Trade P&L Distribution', fontsize=14, fontweight='bold')
        
        # 4. Key Metrics Text Box
        ax4.axis('off')
        metrics_text = f"""
        PERFORMANCE SUMMARY - {strategy_name.upper()}
        
        Total Return: {metrics.get('total_return', 0):.2f}%
        Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}
        Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%
        
        Win Rate: {metrics.get('win_rate', 0):.1f}%
        Total Trades: {metrics.get('total_trades', 0)}
        
        Final Portfolio Value: ${metrics.get('final_portfolio_value', 0):,.2f}
        """
        
        ax4.text(0.1, 0.7, metrics_text, fontsize=12, 
                bbox=dict(boxstyle="round,pad=0.5", facecolor="lightgray", alpha=0.8),
                verticalalignment='top')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if show:
            plt.show()
        else:
            plt.close()
            
        # Return the figure for potential further use
        return fig