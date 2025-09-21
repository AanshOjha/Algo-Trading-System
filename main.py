#!/usr/bin/env python3
"""
Algorithmic Trading System - Main CLI Interface

A clean, simple command-line interface for running backtests on trading strategies.
This replaces all the previous complex entry points with a single, easy-to-use interface.

Usage:
    python main.py --strategy STRATEGY_NAME --capital AMOUNT [OPTIONS]

Examples:
    python main.py --strategy bollinger_bands --capital 100000
    python main.py --strategy ma_crossover --capital 50000 --show-chart
    python main.py --list-strategies
    python main.py --compare-all --capital 100000
"""

import argparse
import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our modules
from core import BacktestingEngine, DatabaseManager, PerformanceAnalyzer
from strategies.strategy_manager import StrategyManager
from visualization import ChartGenerator
from config import DEFAULT_INITIAL_CAPITAL, DEFAULT_DB_FILE, OUTPUT_DIR


class TradingSystemCLI:
    """Main CLI class for the trading system."""
    
    def __init__(self):
        self.strategy_manager = StrategyManager()
        self.chart_generator = ChartGenerator()
    
    def run_backtest(self, strategy_name: str, initial_capital: float, 
                    show_chart: bool = False, export_csv: bool = False,
                    db_file: Optional[str] = None) -> Dict[str, Any]:
        """
        Run a backtest for the specified strategy.
        
        Args:
            strategy_name (str): Name of the strategy to run
            initial_capital (float): Starting capital
            show_chart (bool): Whether to display charts
            export_csv (bool): Whether to export results to CSV
            db_file (str, optional): Database file path
            
        Returns:
            Dict[str, Any]: Backtest results and metrics
        """
        print(f"🚀 Starting {strategy_name.replace('_', ' ').title()} Backtest")
        print("=" * 60)
        
        try:
            # 1. Validate and get strategy
            strategy = self.strategy_manager.get_strategy(strategy_name)
            print(f"📈 Strategy: {strategy.name}")
            print(f"   Description: {strategy.description}")
            
            # 2. Generate signals
            print(f"🔍 Generating trading signals...")
            signals_df = strategy.generate_signals()
            
            buy_signals = (signals_df['signal'] == 1.0).sum()
            print(f"   Data period: {signals_df.index[0].strftime('%Y-%m-%d')} to {signals_df.index[-1].strftime('%Y-%m-%d')}")
            print(f"   Total data points: {len(signals_df):,}")
            print(f"   Buy signals generated: {buy_signals}")
            
            if buy_signals == 0:
                print("⚠️  Warning: No buy signals generated. Check strategy parameters.")
                return {}
            
            # 3. Set up database
            if db_file is None:
                db_file = f"{strategy_name}_results.db"
            
            # 4. Run backtest
            print(f"⚡ Running backtest with ${initial_capital:,.2f} initial capital...")
            
            engine = BacktestingEngine(
                initial_capital=initial_capital,
                db_file=db_file,
                strategy=strategy
            )
            
            backtest_results = engine.run_backtest(signals_df, verbose=False)
            
            # 5. Analyze performance
            print(f"📊 Analyzing performance...")
            db_manager = DatabaseManager(db_file)
            analyzer = PerformanceAnalyzer(db_manager)
            
            metrics = analyzer.analyze_performance()
            
            # 6. Display results
            self._display_results(strategy_name, metrics, backtest_results)
            
            # 7. Generate charts if requested
            if show_chart:
                print(f"📈 Generating performance charts...")
                self._generate_charts(strategy_name, signals_df, analyzer, metrics)
            
            # 8. Export CSV if requested
            if export_csv:
                print(f"💾 Exporting results to CSV...")
                export_path = OUTPUT_DIR / f"{strategy_name}_detailed_results.csv"
                analyzer.export_results(str(export_path))
                print(f"   Daily portfolio data exported to: {export_path}")
                
                # Export detailed trade analysis
                trade_export_path = OUTPUT_DIR / f"{strategy_name}_trade_analysis.csv"
                analyzer.export_trade_analysis(str(trade_export_path))
                print(f"   Individual trade analysis exported to: {trade_export_path}")
            
            print(f"\\n✅ Backtest completed successfully!")
            print(f"📄 Database: {db_file}")
            
            return {
                'strategy_name': strategy_name,
                'metrics': metrics,
                'backtest_summary': backtest_results,
                'database_file': db_file
            }
            
        except Exception as e:
            print(f"❌ Error during backtest: {str(e)}")
            raise
    
    def _display_results(self, strategy_name: str, metrics: Dict[str, Any], 
                        backtest_results: Dict[str, Any]) -> None:
        """Display formatted results to console."""
        print("\\n" + "=" * 60)
        print(f"🎯 BACKTEST RESULTS - {strategy_name.replace('_', ' ').upper()}")
        print("=" * 60)
        
        # Performance Metrics
        print(f"📊 PERFORMANCE METRICS:")
        print(f"   Final Portfolio Value: ${metrics.get('final_portfolio_value', 0):,.2f}")
        print(f"   Total Return: {metrics.get('total_return', 0):.2f}%")
        print(f"   Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.3f}")
        print(f"   Max Drawdown: {metrics.get('max_drawdown', 0):.2f}%")
        
        # Trading Statistics
        print(f"\\n📈 TRADING STATISTICS:")
        print(f"   Total Trades: {metrics.get('total_trades', 0)}")
        print(f"   Win Rate: {metrics.get('win_rate', 0):.1f}%")
        if metrics.get('total_trades', 0) > 0:
            print(f"   Average Win: ${metrics.get('avg_win', 0):.2f}")
            print(f"   Average Loss: ${metrics.get('avg_loss', 0):.2f}")
            print(f"   Largest Win: ${metrics.get('largest_win', 0):.2f}")
            print(f"   Largest Loss: ${metrics.get('largest_loss', 0):.2f}")
        else:
            print(f"   No completed trade cycles found")
        
        # Risk Metrics
        if 'volatility' in metrics:
            print(f"\\n⚠️  RISK METRICS:")
            print(f"   Volatility: {metrics.get('volatility', 0):.2f}%")
            print(f"   Sortino Ratio: {metrics.get('sortino_ratio', 0):.3f}")
    
    def _generate_charts(self, strategy_name: str, signals_df, analyzer, metrics: Dict[str, Any]) -> None:
        """Generate and display charts."""
        try:
            # 1. Strategy signals chart
            chart_path = OUTPUT_DIR / f"{strategy_name}_signals_chart.png"
            self.chart_generator.plot_strategy_signals(
                signals_df, strategy_name.replace('_', ' ').title(),
                save_path=str(chart_path), show=False
            )
            print(f"   📊 Signals chart saved: {chart_path}")
            
            # 2. Performance summary chart
            portfolio_df = analyzer.portfolio_df
            trades_df = analyzer.trades_df
            
            perf_chart_path = OUTPUT_DIR / f"{strategy_name}_performance_chart.png"
            self.chart_generator.plot_performance_summary(
                portfolio_df, trades_df, metrics, strategy_name.replace('_', ' ').title(),
                save_path=str(perf_chart_path), show=True  # Show the performance chart
            )
            print(f"   📈 Performance chart saved: {perf_chart_path}")
            
        except Exception as e:
            print(f"   ⚠️  Warning: Could not generate charts: {e}")
    
    def list_strategies(self) -> None:
        """List all available strategies."""
        print("\\n" + "=" * 60)
        print("📋 AVAILABLE TRADING STRATEGIES")
        print("=" * 60)
        
        strategies = self.strategy_manager.list_strategies()
        
        for i, (name, description) in enumerate(strategies.items(), 1):
            print(f"\\n{i}. {name.replace('_', ' ').upper()}")
            print(f"   Strategy Name: {name}")
            print(f"   Description: {description}")
            
            # Show example usage
            print(f"   Usage: python main.py --strategy {name} --capital 100000")
        
        print("\\n" + "=" * 60)
    
    def compare_strategies(self, initial_capital: float) -> None:
        """Compare all available strategies."""
        print("\\n" + "=" * 60)
        print("🔄 STRATEGY COMPARISON")
        print("=" * 60)
        
        strategies = list(self.strategy_manager.list_strategies().keys())
        results = {}
        
        for strategy_name in strategies:
            print(f"\\n--- Running {strategy_name.replace('_', ' ').title()} ---")
            
            try:
                result = self.run_backtest(
                    strategy_name=strategy_name,
                    initial_capital=initial_capital,
                    show_chart=False,
                    export_csv=False,
                    db_file=f"comparison_{strategy_name}.db"
                )
                results[strategy_name] = result
                
            except Exception as e:
                print(f"   ❌ Failed: {str(e)}")
                results[strategy_name] = None
        
        # Display comparison summary
        print("\\n" + "=" * 80)
        print("📊 COMPARISON SUMMARY")
        print("=" * 80)
        print(f"{'Strategy':<25} {'Return':<10} {'Sharpe':<8} {'Max DD':<8} {'Trades':<8}")
        print("-" * 80)
        
        for strategy_name, result in results.items():
            if result and 'metrics' in result:
                m = result['metrics']
                print(f"{strategy_name.replace('_', ' ').title():<25} "
                      f"{m.get('total_return', 0):>7.2f}% "
                      f"{m.get('sharpe_ratio', 0):>7.3f} "
                      f"{m.get('max_drawdown', 0):>7.2f}% "
                      f"{m.get('total_trades', 0):>7}")
            else:
                print(f"{strategy_name.replace('_', ' ').title():<25} {'FAILED':<30}")
        
        print("=" * 80)


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Algorithmic Trading System - Clean and Simple CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --strategy bollinger_bands --capital 100000
  python main.py --strategy ma_crossover --capital 50000 --show-chart
  python main.py --list-strategies
  python main.py --compare-all --capital 100000
  python main.py --strategy bollinger_bands --capital 100000 --export-csv
        """
    )
    
    # Strategy selection
    parser.add_argument(
        "--strategy", "-s",
        type=str,
        help="Strategy to run (bollinger_bands, ma_crossover)"
    )
    
    # Utility commands
    parser.add_argument(
        "--list-strategies", "-l",
        action="store_true",
        help="List all available strategies"
    )
    
    parser.add_argument(
        "--compare-all", "-c",
        action="store_true",
        help="Compare all available strategies"
    )
    
    # Backtest parameters
    parser.add_argument(
        "--capital",
        type=float,
        default=DEFAULT_INITIAL_CAPITAL,
        help=f"Initial capital amount (default: {DEFAULT_INITIAL_CAPITAL:,.0f})"
    )
    
    # Output options
    parser.add_argument(
        "--show-chart",
        action="store_true",
        help="Display charts after backtest"
    )
    
    parser.add_argument(
        "--export-csv",
        action="store_true",
        help="Export detailed results to CSV"
    )
    
    parser.add_argument(
        "--db-file",
        type=str,
        help="Custom database file path (auto-generated if not specified)"
    )
    
    args = parser.parse_args()
    
    # Create CLI instance
    cli = TradingSystemCLI()
    
    try:
        # Handle list strategies
        if args.list_strategies:
            cli.list_strategies()
            return 0
        
        # Handle compare all strategies
        if args.compare_all:
            cli.compare_strategies(args.capital)
            return 0
        
        # Handle single strategy backtest
        if args.strategy:
            cli.run_backtest(
                strategy_name=args.strategy,
                initial_capital=args.capital,
                show_chart=args.show_chart,
                export_csv=args.export_csv,
                db_file=args.db_file
            )
            return 0
        
        # If no action specified, show help
        parser.print_help()
        return 0
        
    except KeyboardInterrupt:
        print("\\n⏹️  Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"\\n❌ Error: {str(e)}")
        return 1


if __name__ == "__main__":
    # Check if we're running from the correct directory
    if not os.path.exists("strategies"):
        print("❌ Error: Please run this script from the project root directory")
        print("   The 'strategies' folder should be in the current directory")
        sys.exit(1)
    
    # Run the main function
    exit_code = main()
    sys.exit(exit_code)