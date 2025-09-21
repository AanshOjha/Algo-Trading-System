# Old Code Archive

This folder contains the original, legacy code files that have been replaced by the new clean implementation in `main.py` and the reorganized module structure.

## Files Moved Here:

### Old Entry Points (Replaced by main.py):
- `backtester.py` - Original Bollinger Bands backtester
- `advanced_backtester.py` - Multi-strategy backtester with complex CLI
- `quick_test.py` - Quick testing utility

### Old Module Structure (Replaced by new organized structure):
- `backtesting/` - Old backtesting modules (now in `core/`)
- `visual/` - Old visualization code (now in `visualization/`)
- `data_feed/` - Old data management (now in `data/`)
- `strategy_selector.py` - Complex strategy selector (now simplified in `strategy_manager.py`)

### Old Result Files:
- `*.db` - Old database files
- `backtest_detailed_results.csv` - Old CSV export

## Why These Files Were Replaced:

1. **Multiple Entry Points**: Had 3 different scripts doing similar things
2. **Complex CLI**: Overly complicated command-line interfaces
3. **Poor Organization**: Files scattered without clear structure
4. **Duplicate Code**: Similar functionality repeated across files
5. **Hard to Maintain**: Complex inheritance and over-engineered design

## New Clean Implementation:

All functionality has been moved to:
- `main.py` - Single, clean entry point
- `core/` - Core backtesting logic
- `strategies/` - Strategy implementations
- `visualization/` - Chart generation
- `data/` - Data management
- `config/` - Configuration

The new implementation provides the same functionality with:
- ✅ Simpler commands
- ✅ Better organization
- ✅ Easier to understand
- ✅ Easier to extend
- ✅ All the same metrics and features

**Note**: These old files are kept for reference only and are no longer used by the system.