"""
Main Backtester Script

This script orchestrates the complete backtesting process by:
1. Loading signals from the bollinger_bands strategy
2. Running the backtest using the BacktestingEngine
3. Analyzing performance using the PerformanceAnalyzer
4. Generating comprehensive reports and visualizations

Usage:
    python backtester.py [--capital AMOUNT] [--db-file PATH] [--export] [--plot]
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

# Import the bollinger bands strategy
from strategies.bollinger_bands import signals_bb


def run_backtest(initial_capital: float = 100000, 
                db_file: str = "trading_log.db",
                export_results: bool = False,
                create_plots: bool = False,
                verbose: bool = True) -> dict:
    """
    Run the complete backtesting process.
    
    Args:
        initial_capital (float): Starting capital for the backtest
        db_file (str): Database file path
        export_results (bool): Whether to export results to CSV
        create_plots (bool): Whether to generate performance plots
        verbose (bool): Whether to print detailed output
    
    Returns:
        dict: Backtest results and metrics
    """
    if verbose:
        print("🚀 Starting Bollinger Bands Backtesting System")
        print("=" * 60)
    
    try:
        # 1. Initialize the backtesting engine
        if verbose:
            print(f"📊 Initializing backtesting engine with ${initial_capital:,.2f} capital...")
        
        engine = BacktestingEngine(initial_capital=initial_capital, db_file=db_file)
        
        # 2. Validate signals data
        if verbose:
            print(f"📈 Loading strategy signals...")
            print(f"   Signal data shape: {signals_bb.shape}")
            print(f"   Date range: {signals_bb.index[0]} to {signals_bb.index[-1]}")
            print(f"   Buy signals: {(signals_bb['signal'] == 1.0).sum()}")
        
        # Check for required columns
        required_columns = ['price', 'middle_band', 'signal']
        missing_columns = [col for col in required_columns if col not in signals_bb.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns in signals_bb: {missing_columns}")
        
        # 3. Run the backtest
        if verbose:
            print(f"⚡ Running backtest...")
            print("-" * 40)
        
        backtest_results = engine.run_backtest(signals_bb, verbose=verbose)
        
        if verbose:
            print("-" * 40)
        
        # 4. Analyze performance
        if verbose:
            print(f"📊 Analyzing performance...")
        
        db_manager = DatabaseManager(db_file)
        analyzer = PerformanceAnalyzer(db_manager)
        
        # Perform comprehensive analysis
        performance_metrics = analyzer.analyze_performance(risk_free_rate=0.02)
        
        # 5. Generate performance report
        if verbose:
            analyzer.print_performance_report()
        
        # 6. Create visualizations
        if create_plots:
            if verbose:
                print(f"📈 Generating performance charts...")
            analyzer.plot_performance(
                save_path="backtest_performance.png",
                show_plot=True
            )
        
        # 7. Export detailed results
        if export_results:
            if verbose:
                print(f"💾 Exporting detailed results...")
            analyzer.export_results("backtest_detailed_results.csv")
        
        # 8. Combine results
        results = {
            'backtest_summary': backtest_results,
            'performance_metrics': performance_metrics,
            'database_file': db_file
        }
        
        if verbose:
            print(f"\n✅ Backtesting completed successfully!")
            print(f"📄 Results saved to database: {db_file}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during backtesting: {str(e)}")
        raise e


def main():
    """Main function with command-line interface."""
    parser = argparse.ArgumentParser(
        description="Run Bollinger Bands backtesting system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python backtester.py                          # Run with default settings
  python backtester.py --capital 50000         # Start with $50,000
  python backtester.py --export --plot         # Export results and create plots
  python backtester.py --db-file my_test.db    # Use custom database file
        """
    )
    
    parser.add_argument(
        "--capital", 
        type=float, 
        default=100000,
        help="Initial capital amount (default: 100000)"
    )
    
    parser.add_argument(
        "--db-file", 
        type=str, 
        default="trading_log.db",
        help="Database file path (default: trading_log.db)"
    )
    
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
    
    # Run the backtesting system
    try:
        results = run_backtest(
            initial_capital=args.capital,
            db_file=args.db_file,
            export_results=args.export,
            create_plots=args.plot,
            verbose=not args.quiet
        )
        
        if not args.quiet:
            print(f"\n🎯 Quick Summary:")
            print(f"   Final Portfolio Value: ${results['performance_metrics']['final_portfolio_value']:,.2f}")
            print(f"   Total Return: {results['performance_metrics']['total_return']:.2f}%")
            print(f"   Sharpe Ratio: {results['performance_metrics']['sharpe_ratio']:.3f}")
            print(f"   Max Drawdown: {results['performance_metrics']['max_drawdown']:.2f}%")
            print(f"   Win Rate: {results['performance_metrics']['win_rate']:.1f}%")
        
        return 0
        
    except KeyboardInterrupt:
        print("\n⏹️  Backtesting interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Backtesting failed: {str(e)}")
        return 1


if __name__ == "__main__":
    # Check if we're running from the correct directory
    if not os.path.exists("strategies/bollinger_bands.py"):
        print("❌ Error: Please run this script from the project root directory")
        print("   The 'strategies' folder should be in the current directory")
        sys.exit(1)
    
    # Run the main function
    exit_code = main()
    sys.exit(exit_code)