### Development approach

* Designed a clean, modular backtesting system with a single entry point (main.py) orchestrating clearly separated components: core/backtesting_engine.py (execution, portfolio accounting), core/performance_analyzer.py (metrics, reporting), core/database_manager.py (SQLite persistence), strategies/ (signal generation), visualization/charts.py (plots), config/ (settings), and data/sample_data/ (inputs).
* Strategies (e.g., strategies/bollinger_bands.py, strategies/ma_crossover.py) expose simple signal functions; the engine owns the trade lifecycle, cash/position management, and daily portfolio snapshots.
* A CLI utility enables discoverability and repeatability: --strategy, --list-strategies, --compare-all, --capital, --export, --show-chart. Legacy scripts were consolidated into main.py and archived under old_code/ to eliminate duplication and reduce complexity.

### Technologies used

* Python with pandas and numpy for time series handling and indicator computation; yfinance for data ingestion; pyarrow for fast columnar storage; matplotlib for charting; SQLite (via sqlite3-utils) for durable, queryable results.
* Artifacts: CSV/Parquet inputs, SQLite database for trades/portfolio/performance, PNG charts, and CSV exports for detailed analysis.
* Project structure and dependencies are codified in requirements.txt and the organized folders noted above.

### Challenges & learnings
  - I was new to algorithmic trading, so I spent time learning core ideas like Bollinger Bands, moving averages, trend filters, entries/exits, and risk rules.
  - I tried each idea multiple times on sample data, adjusted the logic, and only then coded it into Python. This helped me avoid mistakes and understand why a rule works.
- What I learned
  - Keep strategies simple and rules explicit.
  - Separate responsibilities: signals, engine, performance, storage, and visuals.
