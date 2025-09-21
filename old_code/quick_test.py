"""
Quick Backtest Utility

A simple script for running quick backtests with common configurations.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from backtester import run_backtest


def quick_backtest():
    """Run a quick backtest with standard settings."""
    print("🚀 Running Quick Backtest")
    print("=" * 40)
    
    results = run_backtest(
        initial_capital=100000,
        db_file="quick_backtest.db",
        export_results=True,
        create_plots=False,
        verbose=True
    )
    
    return results


def comparison_backtest():
    """Run multiple backtests with different capital amounts for comparison."""
    print("🔄 Running Comparison Backtests")
    print("=" * 40)
    
    capitals = [50000, 100000, 200000]
    results = {}
    
    for capital in capitals:
        print(f"\n--- Testing with ${capital:,} ---")
        result = run_backtest(
            initial_capital=capital,
            db_file=f"backtest_{capital}.db",
            export_results=False,
            create_plots=False,
            verbose=False
        )
        results[capital] = result
        
        # Print key metrics
        metrics = result['performance_metrics']
        print(f"Final Value: ${metrics['final_portfolio_value']:,.2f}")
        print(f"Return: {metrics['total_return']:.2f}%")
        print(f"Sharpe: {metrics['sharpe_ratio']:.3f}")
        print(f"Max DD: {metrics['max_drawdown']:.2f}%")
    
    return results


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        comparison_backtest()
    else:
        quick_backtest()