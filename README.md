# Clean Algorithmic Trading System# Clean Algorithmic Trading System# Bollinger Bands Backtesting System



A thoroughly reorganized, modular backtesting system for algorithmic trading strategies with a clean command-line interface.



## 🚀 Quick StartA thoroughly reorganized, modular backtesting system for algorithmic trading strategies with a clean command-line interface.A comprehensive, modular backtesting system for algorithmic trading strategies, specifically designed for Bollinger Bands strategy analysis.



### Simple Command Format

```bash

# Basic usage - run a strategy with initial capital## 🚀 Quick Start## 📁 Project Structure

python main.py --strategy STRATEGY_NAME --capital AMOUNT



# Example: Run MA Crossover with $100,000

python main.py --strategy ma_crossover --capital 100000### Simple Command Format```



# With chart generation```bashNew-Algo-Trading/

python main.py --strategy bollinger_bands --capital 50000 --show-chart

# Basic usage - run a strategy with initial capital├── data_feed/                  # Market data storage

# Export detailed results

python main.py --strategy ma_crossover --capital 100000 --exportpython main.py --strategy STRATEGY_NAME --capital AMOUNT│   ├── fetch_data.py          # Data downloading script

```

│   ├── reliance_data.csv      # Historical price data

## 📊 Available Strategies

# Example: Run MA Crossover with $100,000│   └── reliance_data.parquet  # Optimized data format

```bash

# List all available strategiespython main.py --strategy ma_crossover --capital 100000├── strategies/                 # Trading strategies

python main.py --list-strategies

│   ├── __init__.py

# Compare all strategies

python main.py --compare-all --capital 100000# With chart generation│   ├── bollinger_bands.py     # Bollinger Bands strategy

```

python main.py --strategy bollinger_bands --capital 50000 --show-chart│   └── ma_crossover.py        # Moving average crossover

### Supported Strategies:

- **Bollinger Bands**: Entry on lower band bounce, exit on middle band cross├── backtesting/               # Backtesting framework

- **Moving Average Crossover**: Entry on MA crossover, exit on reverse crossover

# Export detailed results│   ├── __init__.py

## 📈 Output and Metrics

python main.py --strategy ma_crossover --capital 100000 --export│   ├── database_manager.py    # SQLite database operations

### Command Line Output

For each backtest, you'll see:```│   ├── backtesting_engine.py  # Core backtesting logic

- **Total PnL (%)**: Overall return percentage

- **Sharpe Ratio**: Risk-adjusted returns│   └── performance_analyzer.py # Performance metrics & visualization

- **Max Drawdown (%)**: Maximum portfolio decline

- **Total Trades**: Number of completed trades## 📊 Available Strategies├── visual/                    # Visualization utilities

- **Win Rate**: Percentage of profitable trades

│   ├── __init__.py

### Generated Files

```bash│   └── charts_signals.py      # Chart generation

When using `--show-chart`:

- **Signals Chart**: Price with buy/sell signals and indicators# List all available strategies├── backtester.py             # Main backtesting script

- **Performance Chart**: Portfolio value, drawdown, trade distribution, and metrics summary

python main.py --list-strategies├── requirements.txt          # Python dependencies

When using `--export`:

- **Detailed CSV**: Daily portfolio values with Entry Date, Entry Price, Exit Date, Exit Price, Shares, and Profit/Loss per trade└── README.md                # This file



### Database Storage# Compare all strategies```

- SQLite database with complete trade history

- Portfolio snapshots for each trading daypython main.py --compare-all --capital 100000

- Performance metrics storage

```## 🚀 Quick Start

## 📁 Project Structure



```

New-Algo-Trading/### Supported Strategies:### 1. Install Dependencies

├── main.py                    # Single entry point CLI

├── requirements.txt           # Dependencies- **Bollinger Bands**: Entry on lower band bounce, exit on middle band cross```bash

├── README.md                 # This file

├── core/                     # Core backtesting logic- **Moving Average Crossover**: Entry on MA crossover, exit on reverse crossoverpip install -r requirements.txt

│   ├── backtesting_engine.py # Main backtesting engine

│   ├── database_manager.py   # Database operations```

│   └── performance_analyzer.py # Performance metrics

├── strategies/               # Trading strategies## 📈 Output and Metrics

│   ├── bollinger_bands.py    # Bollinger Bands implementation

│   ├── ma_crossover.py       # Moving Average Crossover### 2. Run Basic Backtest

│   └── strategy_manager.py   # Strategy management

├── data/                     # Data management### Command Line Output```bash

│   └── sample_data/

│       └── reliance_data.csv # Sample stock dataFor each backtest, you'll see:python backtester.py

├── visualization/            # Chart generation

│   └── charts.py            # All chart functionality- **Total PnL (%)**: Overall return percentage```

├── output/                   # Generated files

│   ├── *.png                # Chart images- **Sharpe Ratio**: Risk-adjusted returns

│   ├── *.csv                # Detailed results

│   └── *.db                 # Database files- **Max Drawdown (%)**: Maximum portfolio decline### 3. Run with Custom Options

├── config/                   # Configuration

│   └── settings.py          # System settings- **Total Trades**: Number of completed trades```bash

└── old_code/                 # Legacy code archive

    └── ...                  # Old files (no longer used)- **Win Rate**: Percentage of profitable trades# Start with $50,000 capital

```

python backtester.py --capital 50000

## 🔧 Installation

### Generated Files

1. **Install Dependencies**

```bash# Export results and generate plots

pip install -r requirements.txt

```When using `--show-chart`:python backtester.py --export --plot



2. **Run Your First Backtest**- **Signals Chart**: Price with buy/sell signals and indicators

```bash

python main.py --strategy ma_crossover --capital 100000 --show-chart- **Performance Chart**: Portfolio value, drawdown, trade distribution, and metrics summary# Use custom database file

```

python backtester.py --db-file my_backtest.db

## 💡 Examples

When using `--export`:

### Basic Strategy Test

```bash- **Detailed CSV**: Daily portfolio values with Entry Date, Entry Price, Exit Date, Exit Price, Shares, and Profit/Loss per trade# Quiet mode (minimal output)

python main.py --strategy bollinger_bands --capital 50000

```python backtester.py --quiet



### Full Analysis with Charts and Export### Database Storage```

```bash

python main.py --strategy ma_crossover --capital 100000 --show-chart --export- SQLite database with complete trade history

```

- Portfolio snapshots for each trading day## 📊 Features

### Strategy Comparison

```bash- Performance metrics storage

python main.py --compare-all --capital 100000

```### Core Backtesting Engine



### List Available Strategies## 📁 Project Structure- **Realistic Trade Execution**: Follows pseudocode logic with proper entry/exit rules

```bash

python main.py --list-strategies- **Portfolio Management**: Tracks cash, positions, and portfolio value over time

```

```- **Database Logging**: Stores all trades and portfolio snapshots in SQLite

## 📊 Key Features

New-Algo-Trading/- **Modular Design**: Separate components for easy testing and maintenance

- **Clean CLI**: Simple command structure

- **Multiple Strategies**: Easy to add new strategies├── main.py                    # Single entry point CLI

- **Rich Visualizations**: Professional charts with signals and performance

- **Detailed Exports**: Complete trade history and daily portfolio data├── requirements.txt           # Dependencies### Performance Analysis

- **Database Storage**: SQLite for reliable data persistence

- **Performance Metrics**: Comprehensive risk and return analysis├── README.md                 # This file- **Risk Metrics**: Sharpe ratio, Sortino ratio, maximum drawdown

- **Modular Design**: Easy to extend and maintain

├── core/                     # Core backtesting logic- **Trade Analysis**: Win rate, profit factor, average win/loss

## 🧹 What Was Cleaned Up

│   ├── backtesting_engine.py # Main backtesting engine- **Visualizations**: Equity curves, drawdown charts, trade distribution

### Moved to `old_code/` folder:

- `backtester.py` → Functionality moved to `main.py`│   ├── database_manager.py   # Database operations- **Export Capabilities**: CSV export for detailed analysis

- `advanced_backtester.py` → Functionality moved to `main.py`

- `quick_test.py` → Functionality moved to `main.py`│   └── performance_analyzer.py # Performance metrics

- `visual/` → Replaced by `visualization/`

- `backtesting/` → Moved to `core/`├── strategies/               # Trading strategies### Strategy Implementation

- `data_feed/` → Moved to `data/sample_data/`

- `strategy_selector.py` → Replaced by `strategy_manager.py`│   ├── bollinger_bands.py    # Bollinger Bands implementation- **Bollinger Bands**: Entry on lower band bounce, exit on middle band cross



### New Clean Structure:│   ├── ma_crossover.py       # Moving Average Crossover- **Trend Filter**: Uses 200-day moving average for trend confirmation

- Single entry point: `main.py`

- Proper module organization with `__init__.py` files│   └── strategy_manager.py   # Strategy management- **Signal Generation**: Clear buy/sell signals with confirmation logic

- Clear separation of concerns

- Eliminated duplicate code├── data/                     # Data management



## 🚀 Command Reference│   └── sample_data/## 🔧 Usage Examples



| Command | Description |│       └── reliance_data.csv # Sample stock data

|---------|-------------|

| `--strategy STRATEGY` | Run specific strategy |├── visualization/            # Chart generation### Basic Backtesting

| `--capital AMOUNT` | Set initial capital |

| `--show-chart` | Generate and display charts |│   └── charts.py            # All chart functionality```python

| `--export` | Export detailed results to CSV |

| `--list-strategies` | List all available strategies |├── output/                   # Generated filesfrom backtesting import BacktestingEngine, PerformanceAnalyzer, DatabaseManager

| `--compare-all` | Compare all strategies |

│   ├── *.png                # Chart imagesfrom strategies.bollinger_bands import signals_bb

## 📈 Performance Metrics Explained

│   ├── *.csv                # Detailed results

- **Total Return**: Overall percentage gain/loss

- **Sharpe Ratio**: Return per unit of risk (higher is better)│   └── *.db                 # Database files# Initialize and run backtest

- **Max Drawdown**: Largest peak-to-trough decline

- **Win Rate**: Percentage of profitable trades└── config/                   # Configurationengine = BacktestingEngine(initial_capital=100000)

- **Total Trades**: Number of complete buy-sell cycles

    └── settings.py          # System settingsresults = engine.run_backtest(signals_bb)

The system provides all the requested metrics:

- ✅ Total PnL (%)```

- ✅ Sharpe Ratio  

- ✅ Max Drawdown (%)# Analyze performance

- ✅ Total Trades

- ✅ Entry Date, Entry Price, Exit Date, Exit Price, Shares, and Profit/Loss per trade## 🔧 Installationdb_manager = DatabaseManager()



Everything is now clean, organized, and easy to use with a single command!analyzer = PerformanceAnalyzer(db_manager)

1. **Install Dependencies**metrics = analyzer.analyze_performance()

```bashanalyzer.print_performance_report()

pip install -r requirements.txt```

```

### Custom Analysis

2. **Run Your First Backtest**```python

```bash# Load specific data

python main.py --strategy ma_crossover --capital 100000 --show-chartportfolio_df = db_manager.get_portfolio_history()

```trades_df = db_manager.get_trades()



## 💡 Examples# Generate plots

analyzer.plot_performance(save_path="my_analysis.png")

### Basic Strategy Test

```bash# Export detailed results

python main.py --strategy bollinger_bands --capital 50000analyzer.export_results("detailed_backtest.csv")

``````



### Full Analysis with Charts and Export## 📈 Strategy Logic

```bash

python main.py --strategy ma_crossover --capital 100000 --show-chart --export### Entry Conditions (BUY)

```1. **Price crosses above lower Bollinger Band** (bounce confirmation)

2. **Price is above 200-day moving average** (uptrend filter)

### Strategy Comparison3. **No current position held**

```bash

python main.py --compare-all --capital 100000### Exit Conditions (SELL)

```1. **Price reaches or exceeds middle Bollinger Band**

2. **Currently holding a position**

### List Available Strategies

```bash### Risk Management

python main.py --list-strategies- **Full Position Sizing**: Invests all available cash on entry

```- **Single Position**: Only one position at a time

- **Systematic Exits**: No discretionary decisions

## 📊 Key Features

## 📊 Performance Metrics

- **Clean CLI**: Simple command structure

- **Multiple Strategies**: Easy to add new strategiesThe system calculates comprehensive performance metrics:

- **Rich Visualizations**: Professional charts with signals and performance

- **Detailed Exports**: Complete trade history and daily portfolio data### Returns

- **Database Storage**: SQLite for reliable data persistence- Total Return (%)

- **Performance Metrics**: Comprehensive risk and return analysis- Annualized Return (%)

- **Modular Design**: Easy to extend and maintain- Daily/Monthly Returns



## 🧹 What Was Cleaned Up### Risk Metrics

- Sharpe Ratio

### Removed Files (Redundant/Unused):- Sortino Ratio

- `backtester.py` → Functionality moved to `main.py`- Maximum Drawdown

- `advanced_backtester.py` → Functionality moved to `main.py`- Volatility (annualized)

- `quick_test.py` → Functionality moved to `main.py`

- `visual/charts_signals.py` → Replaced by `visualization/charts.py`### Trade Analysis

- `data_feed/` → Moved to `data/sample_data/`- Total Number of Trades

- Win Rate (%)

### Reorganized:- Profit Factor

- `backtesting/` → `core/`- Average Win/Loss

- `strategies/` → Cleaned and streamlined- Largest Win/Loss

- Added proper module structure with `__init__.py` files

- Single entry point for all functionality## 🗃️ Database Schema



## 🚀 Command Reference### Tables Created

1. **trades**: Individual buy/sell transactions

| Command | Description |2. **portfolio_history**: Daily portfolio snapshots

|---------|-------------|3. **performance_metrics**: Calculated performance statistics

| `--strategy STRATEGY` | Run specific strategy |

| `--capital AMOUNT` | Set initial capital |### Data Persistence

| `--show-chart` | Generate and display charts |All results are automatically saved to SQLite database for:

| `--export` | Export detailed results to CSV |- Historical analysis

| `--list-strategies` | List all available strategies |- Strategy comparison

| `--compare-all` | Compare all strategies |- Performance tracking over time



## 📈 Performance Metrics Explained## 🎯 Command Line Options



- **Total Return**: Overall percentage gain/loss```bash

- **Sharpe Ratio**: Return per unit of risk (higher is better)python backtester.py [OPTIONS]

- **Max Drawdown**: Largest peak-to-trough decline

- **Win Rate**: Percentage of profitable tradesOptions:

- **Total Trades**: Number of complete buy-sell cycles  --capital AMOUNT     Initial capital (default: 100000)

  --db-file PATH       Database file path (default: trading_log.db)

The system provides all the metrics you requested:  --export            Export results to CSV

- Total PnL (%)  --plot              Generate performance charts

- Sharpe Ratio    --quiet             Minimal output mode

- Max Drawdown (%)  --help              Show help message

- Total Trades```

- Entry Date, Entry Price, Exit Date, Exit Price, Shares, and Profit/Loss per trade

## 📁 Output Files

Everything is now clean, organized, and easy to use with a single command!
When running with export/plot options:
- `trading_log.db`: SQLite database with all results
- `backtest_performance.png`: Performance visualization charts
- `backtest_detailed_results.csv`: Detailed daily results
- Console output: Comprehensive performance report

## 🔍 Troubleshooting

### Common Issues
1. **Missing Data**: Ensure `reliance_data.csv` exists in `data_feed/` folder
2. **Import Errors**: Run from project root directory
3. **Database Locked**: Close any existing database connections

### Debug Mode
Use `--export` and `--plot` flags to generate detailed outputs for analysis.

## 🚀 Next Steps

1. **Add More Strategies**: Implement additional strategies in the `strategies/` folder
2. **Parameter Optimization**: Add grid search capabilities
3. **Live Trading**: Extend for real-time trading implementation
4. **Portfolio Analytics**: Add portfolio-level analysis for multiple strategies

## 📞 Support

For issues or questions, check:
1. Console output for error messages
2. Database contents using SQLite browser
3. Generated CSV files for data validation


# Basic backtest with chart display
python main.py --strategy ma_crossover --capital 50000

# With detailed trade analysis export
python main.py --strategy ma_crossover --capital 50000 --export

# Bollinger Bands strategy
python main.py --strategy bollinger_bands --capital 100000 --export