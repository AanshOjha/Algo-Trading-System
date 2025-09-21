"""
Enhanced Backtester Script with Strategy Selection

This script provides a command-line interface to select and run backtests on different strategies:
- Bollinger Bands
- Moving Average Crossover

Usage:
    python advanced_backtester.py --strategy STRATEGY_NAME [--capital AMOUNT] [--db-file PATH] [--export] [--plot]
"""

import sys
import os
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Import our custom modules
from backtesting import DatabaseManager, BacktestingEngine, PerformanceAnalyzer
from strategies.strategy_selector import StrategySelector, print_strategy_comparison


def run_strategy_backtest(strategy_name: str,
                         initial_capital: float = 100000, 
                         db_file: str = None,
                         export_results: bool = False,
                         create_plots: bool = False,
                         verbose: bool = True) -> dict:
    """
    Run backtest for a specific strategy.
    
    Args:
        strategy_name (str): Name of the strategy to run
        initial_capital (float): Starting capital for the backtest
        db_file (str): Database file path (auto-generated if None)
        export_results (bool): Whether to export results to CSV
        create_plots (bool): Whether to generate performance plots
        verbose (bool): Whether to print detailed output
    
    Returns:
        dict: Backtest results and metrics
    """
    if verbose:
        print("🚀 Starting Multi-Strategy Backtesting System")
        print("=" * 60)
    
    try:
        # 1. Initialize strategy selector
        selector = StrategySelector()
        
        # 2. Validate strategy exists
        available_strategies = list(selector.list_strategies().keys())
        if strategy_name not in available_strategies:
            raise ValueError(f"Strategy '{strategy_name}' not found. Available: {available_strategies}")
        
        # 3. Get strategy information
        strategy_info = selector.get_strategy_info(strategy_name)
        if verbose:
            print(f"📈 Selected Strategy: {strategy_info['name'].replace('_', ' ').title()}")
            print(f"   Description: {strategy_info['description']}")
            print(f"   Entry: {strategy_info['parameters'].get('entry_condition', 'N/A')}")
            print(f"   Exit: {strategy_info['parameters'].get('exit_condition', 'N/A')}")
        
        # 4. Validate strategy signals
        if verbose:
            print(f"🔍 Validating strategy signals...")
        
        is_valid, validation_message = selector.validate_strategy_signals(strategy_name)
        if not is_valid:
            raise ValueError(f"Strategy validation failed: {validation_message}")
        
        if verbose:
            print(f"   ✅ {validation_message}")
        
        # 5. Load strategy and signals
        strategy = selector.select_strategy(strategy_name)
        signals_df = strategy.generate_signals()
        
        if verbose:
            print(f"📊 Strategy Data Loaded")
            print(f"   Data shape: {signals_df.shape}")
            print(f"   Date range: {signals_df.index[0]} to {signals_df.index[-1]}")
            print(f"   Buy signals: {(signals_df['signal'] == 1.0).sum()}")
        
        # 6. Set up database file
        if db_file is None:
            db_file = f"{strategy_name}_backtest.db"
        
        # 7. Initialize backtesting engine with strategy
        if verbose:
            print(f"⚡ Initializing backtesting engine with ${initial_capital:,.2f} capital...")
        
        engine = BacktestingEngine(
            initial_capital=initial_capital, 
            db_file=db_file,
            strategy=strategy
        )
        
        # 8. Run the backtest
        if verbose:
            print(f"🔄 Running {strategy_name} backtest...")
            print("-" * 40)
        
        backtest_results = engine.run_backtest(signals_df, verbose=verbose)
        
        if verbose:
            print("-" * 40)
        
        # 9. Analyze performance
        if verbose:
            print(f"📊 Analyzing performance...")
        
        db_manager = DatabaseManager(db_file)
        analyzer = PerformanceAnalyzer(db_manager)
        
        # Perform comprehensive analysis
        performance_metrics = analyzer.analyze_performance(risk_free_rate=0.02)
        
        # 10. Generate performance report
        if verbose:
            analyzer.print_performance_report()
        
        # 11. Create visualizations
        if create_plots:
            if verbose:
                print(f"📈 Generating performance charts...")
            plot_filename = f"{strategy_name}_backtest_performance.png"
            analyzer.plot_performance(
                save_path=plot_filename,
                show_plot=True
            )
        
        # 12. Export detailed results
        if export_results:
            if verbose:
                print(f"💾 Exporting detailed results...")
            export_filename = f"{strategy_name}_backtest_results.csv"
            analyzer.export_results(export_filename)
        
        # 13. Combine results
        results = {
            'strategy_name': strategy_name,
            'strategy_info': strategy_info,
            'backtest_summary': backtest_results,
            'performance_metrics': performance_metrics,
            'database_file': db_file
        }
        
        if verbose:
            print(f"\n✅ {strategy_name} backtesting completed successfully!")
            print(f"📄 Results saved to database: {db_file}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during {strategy_name} backtesting: {str(e)}")
        raise e


def compare_strategies(strategies: list, initial_capital: float = 100000, verbose: bool = True):
    """
    Run and compare multiple strategies.
    
    Args:
        strategies (list): List of strategy names to compare
        initial_capital (float): Starting capital for each backtest
        verbose (bool): Whether to print detailed output
    """
    if verbose:
        print("🔄 Running Strategy Comparison")
        print("=" * 60)
    
    results = {}
    
    for strategy_name in strategies:
        if verbose:
            print(f"\n--- Running {strategy_name.replace('_', ' ').title()} ---")
        
        try:
            result = run_strategy_backtest(
                strategy_name=strategy_name,
                initial_capital=initial_capital,
                db_file=f"comparison_{strategy_name}.db",
                export_results=False,
                create_plots=False,
                verbose=False
            )
            results[strategy_name] = result
            
            # Print key metrics
            metrics = result['performance_metrics']
            print(f"   Final Value: ${metrics['final_portfolio_value']:,.2f}")
            print(f"   Return: {metrics['total_return']:.2f}%")
            print(f"   Sharpe: {metrics['sharpe_ratio']:.3f}")
            print(f"   Max DD: {metrics['max_drawdown']:.2f}%")
            print(f"   Win Rate: {metrics['win_rate']:.1f}%")
            
        except Exception as e:
            print(f"   ❌ Failed: {str(e)}")
            results[strategy_name] = None
    
    # Print comparison summary
    if verbose:
        print(f"\n📊 STRATEGY COMPARISON SUMMARY")
        print("-" * 60)
        print(f"{'Strategy':<20} {'Return':<10} {'Sharpe':<8} {'MaxDD':<8} {'WinRate':<8}")
        print("-" * 60)
        
        for strategy_name, result in results.items():
            if result:
                m = result['performance_metrics']
                print(f"{strategy_name.replace('_', ' ').title():<20} "
                      f"{m['total_return']:>7.2f}% "
                      f"{m['sharpe_ratio']:>7.3f} "
                      f"{m['max_drawdown']:>7.2f}% "
                      f"{m['win_rate']:>7.1f}%")
            else:
                print(f"{strategy_name.replace('_', ' ').title():<20} {'FAILED':<30}")
    
    return results


def main():
    """Main function with enhanced command-line interface."""
    parser = argparse.ArgumentParser(
        description="Multi-Strategy Backtesting System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python advanced_backtester.py --list                                    # List available strategies
  python advanced_backtester.py --strategy bollinger_bands               # Run Bollinger Bands
  python advanced_backtester.py --strategy ma_crossover --capital 50000  # Run MA Crossover with $50k
  python advanced_backtester.py --compare                                 # Compare all strategies
  python advanced_backtester.py --strategy bollinger_bands --export --plot # Export and plot results
        """
    )
    
    # Strategy selection
    parser.add_argument(
        "--strategy", "-s",
        type=str,
        help="Strategy to run (bollinger_bands, ma_crossover)"
    )
    
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List all available strategies"
    )
    
    parser.add_argument(
        "--compare", "-c",
        action="store_true",
        help="Compare all available strategies"
    )
    
    # Backtest parameters
    parser.add_argument(
        "--capital", 
        type=float, 
        default=100000,
        help="Initial capital amount (default: 100000)"
    )
    
    parser.add_argument(
        "--db-file", 
        type=str, 
        default=None,
        help="Database file path (auto-generated if not specified)"
    )
    
    # Output options
    parser.add_argument(
        "--export", 
        action="store_true",
        help="Export detailed results to CSV"
    )
    
    parser.add_argument(
        "--plot", 
        action="store_true",
        help="Generate performance plots"
    )
    
    parser.add_argument(
        "--quiet", 
        action="store_true",
        help="Run in quiet mode (minimal output)"
    )
    
    args = parser.parse_args()
    
    # Handle list strategies
    if args.list:
        print_strategy_comparison()
        return 0
    
    # Handle compare strategies
    if args.compare:
        selector = StrategySelector()
        available_strategies = list(selector.list_strategies().keys())
        compare_strategies(
            strategies=available_strategies,
            initial_capital=args.capital,
            verbose=not args.quiet
        )
        return 0
    
    # Handle single strategy
    if args.strategy:
        try:
            results = run_strategy_backtest(
                strategy_name=args.strategy,
                initial_capital=args.capital,
                db_file=args.db_file,
                export_results=args.export,
                create_plots=args.plot,
                verbose=not args.quiet
            )
            
            if not args.quiet:
                print(f"\n🎯 Quick Summary for {args.strategy.replace('_', ' ').title()}:")
                metrics = results['performance_metrics']
                print(f"   Final Portfolio Value: ${metrics['final_portfolio_value']:,.2f}")
                print(f"   Total Return: {metrics['total_return']:.2f}%")
                print(f"   Sharpe Ratio: {metrics['sharpe_ratio']:.3f}")
                print(f"   Max Drawdown: {metrics['max_drawdown']:.2f}%")
                print(f"   Win Rate: {metrics['win_rate']:.1f}%")
            
            return 0
            
        except KeyboardInterrupt:
            print("\n⏹️  Backtesting interrupted by user")
            return 1
        except Exception as e:
            print(f"\n❌ Backtesting failed: {str(e)}")
            return 1
    
    # If no action specified, show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    # Check if we're running from the correct directory
    if not os.path.exists("strategies"):
        print("❌ Error: Please run this script from the project root directory")
        print("   The 'strategies' folder should be in the current directory")
        sys.exit(1)
    
    # Run the main function
    exit_code = main()
    sys.exit(exit_code)