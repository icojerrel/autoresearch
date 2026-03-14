---
name: mt5-backtest
description: VectorBT backtesting adapted for MT5 forex data. Fetch data from MT5, run strategy backtests, calculate metrics (Sharpe, Max DD, Win Rate), generate equity curves and trade lists. Optimized for EUR/USD and other FX pairs.
argument-hint: "[strategy] [symbol] [timeframe] [bars]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
user-invocable: true
---

# MT5 Backtest Skill

## Overview
Backtesting with VectorBT adapted for MT5 forex data. Quick validation of strategies before paper trading.

## Arguments
Parse `$ARGUMENTS` as: strategy symbol timeframe bars

- `$0` = Strategy (ema-crossover, rsi, etc.). Default: ema-crossover
- `$1` = Symbol (EURUSD, GBPUSD, USDJPY). Default: EURUSD
- `$2` = Timeframe (M1, M5, M15, M30, H1, H4, D1). Default: H1
- `$3` = Bars count (500-5000). Default: 1000

## Complete Backtest Workflow

### Step 1: Fetch MT5 Data

```python
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import pandas as pd
import vectorbt as vbt

def fetch_mt5_data(symbol, timeframe, bars):
    """Fetch OHLCV data from MT5 terminal."""

    # Initialize MT5
    if not mt5.initialize():
        raise Exception(f"Cannot connect to MT5: {mt5.last_error()}")

    # Timeframe mapping
    tf_map = {
        'M1': mt5.TIMEFRAME_M1,
        'M5': mt5.TIMEFRAME_M5,
        'M15': mt5.TIMEFRAME_M15,
        'M30': mt5.TIMEFRAME_M30,
        'H1': mt5.TIMEFRAME_H1,
        'H4': mt5.TIMEFRAME_H4,
        'D1': mt5.TIMEFRAME_D1,
    }

    if timeframe not in tf_map:
        raise ValueError(f"Invalid timeframe: {timeframe}")

    # Calculate start time
    utc_from = datetime.now() - timedelta(days=bars // 24)

    # Fetch rates
    rates = mt5.copy_rates_from(symbol, tf_map[timeframe], utc_from, bars)

    if rates is None:
        raise Exception(f"No data for {symbol}: {mt5.last_error()}")

    # Convert to DataFrame
    df = pd.DataFrame(rates)

    # Rename for vectorbt
    df = df.rename(columns={
        'open': 'Open',
        'high': 'High',
        'low': 'Low',
        'close': 'Close',
        'volume': 'Volume',
        'tick_volume': 'Volume',
        'spread': 'Spread',
        'time': 'datetime'
    })

    # Set datetime index
    df['datetime'] = pd.to_datetime(df['time'], unit='s')
    df.set_index('datetime', inplace=True)

    # Shutdown MT5
    mt5.shutdown()

    return df

# Usage
df = fetch_mt5_data('EURUSD', 'H1', 1000)
close = df['Close']
print(f"Fetched {len(df)} bars")
```

### Step 2: Generate Strategy Signals

```python
def ema_crossover_signals(close, fast=12, slow=26):
    """Generate EMA crossover signals."""
    ema_fast = vbt.MA.run(close, fast, ewm=True)
    ema_slow = vbt.MA.run(close, slow, ewm=True)

    entries = ema_fast.ma_crossed_above(ema_slow)
    exits = ema_fast.ma_crossed_below(ema_slow)

    return entries, exits

def rsi_signals(close, period=14, oversold=30, overbought=70):
    """Generate RSI mean reversion signals."""
    rsi = vbt.RSI.run(close, window=period)

    entries = rsi.rsi_crossed_below(oversold)
    exits = rsi.rsi_crossed_above(overbought)

    return entries, exits

def donchian_signals(high, low, period=20):
    """Generate Donchian channel breakout signals."""
    # Donchian channels
    upper = high.rolling(window=period).max()
    lower = low.rolling(window=period).min()

    # Use shifted channels to avoid lookahead
    upper_shifted = upper.shift(1)
    lower_shifted = lower.shift(1)

    # Entries: break above upper band
    entries = (close > upper_shifted) & (close.shift(1) <= upper_shifted.shift(1))

    # Exits: break below lower band
    exits = (close < lower_shifted) & (close.shift(1) >= lower_shifted.shift(1))

    return entries, exits

# Usage
entries, exits = ema_crossover_signals(close, fast=12, slow=26)
```

### Step 3: Run Backtest

```python
def run_backtest(close, entries, exits, init_cash=10000, fees=0.001):
    """Run VectorBT backtest with MT5 data."""

    # Create portfolio
    pf = vbt.Portfolio.from_signals(
        close=close,
        entries=entries,
        exits=exits,
        init_cash=init_cash,
        fees=fees,  # 0.1% per trade (typical for forex)
        slippage=0.0005,  # 0.05% slippage
        size=0.5,  # 50% of equity per trade
        size_type="percent",
        direction="longonly",  # Only long trades for now
        freq="1H" if "H1" in str(close.index.freq) else "1D",
    )

    return pf

# Usage
pf = run_backtest(close, entries, exits, init_cash=10000, fees=0.001)
```

### Step 4: Calculate Metrics

```python
def calculate_metrics(pf):
    """Calculate performance metrics."""

    metrics = {
        # Primary metrics
        'sharpe_ratio': pf.sharpe_ratio(),
        'max_drawdown': pf.max_drawdown() * 100,  # As percentage
        'total_return': pf.total_return() * 100,  # As percentage

        # Secondary metrics
        'sortino_ratio': pf.sortino_ratio(),
        'calmar_ratio': pf.total_return() / abs(pf.max_drawdown()) if pf.max_drawdown() != 0 else 0,
        'win_rate': pf.trades.win_rate() * 100,
        'profit_factor': pf.trades.profit_factor(),
        'total_trades': pf.trades.count(),

        # Trade statistics
        'avg_trade': pf.trades.cash().mean(),
        'best_trade': pf.trades.cash().max(),
        'worst_trade': pf.trades.cash().min(),

        # Time statistics
        'start_date': pf.value().index[0],
        'end_date': pf.value().index[-1],
        'duration_days': (pf.value().index[-1] - pf.value().index[0]).days,
    }

    return metrics

# Usage
metrics = calculate_metrics(pf)
print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
print(f"Total Return: {metrics['total_return']:.2f}%")
print(f"Win Rate: {metrics['win_rate']:.1f}%")
```

### Step 5: Compound Score (Primary Metric)

```python
def calculate_compound_score(sharpe, max_dd, win_rate):
    """
    Calculate compound score for autoresearch comparison.

    This is the primary metric used to compare strategies.
    Higher = better.
    """
    # Normalize components (0-1 scale)
    sharpe_norm = max(0, min(sharpe / 3, 1))  # 3.0 = excellent
    dd_norm = 1 - max(0, min(abs(max_dd) / 50, 1))  # 50% DD = 0
    win_norm = win_rate / 100  # Already 0-1

    # Weighted score
    score = (sharpe_norm * 0.5 +
             dd_norm * 0.3 +
             win_norm * 0.2)

    return score

# Usage
compound_score = calculate_compound_score(
    metrics['sharpe_ratio'],
    metrics['max_drawdown'],
    metrics['win_rate']
)
print(f"Compound Score: {compound_score:.3f}")
```

### Step 6: Safety Gates

```python
def check_safety_gates(metrics):
    """
    Check if strategy passes safety gates.

    Returns (passed, checks_dict)
    """
    checks = {
        'max_drawdown_ok': metrics['max_drawdown'] < 15,
        'sharpe_positive': metrics['sharpe_ratio'] > 0,
        'min_trades': metrics['total_trades'] >= 10,
        'win_rate_reasonable': metrics['win_rate'] > 30,
    }

    passed = all(checks.values())

    return passed, checks

# Usage
passed, checks = check_safety_gates(metrics)
if not passed:
    print("⚠️  Strategy FAILED safety gates:")
    for check, result in checks.items():
        if not result:
            print(f"  ✗ {check}")
else:
    print("✓ Strategy PASSED safety gates")
```

### Step 7: Generate Report

```python
def generate_backtest_report(strategy, symbol, timeframe, metrics, pf, save_path=None):
    """Generate comprehensive backtest report."""

    report = f"""
# Backtest Report: {strategy} on {symbol}

## Parameters
- Symbol: {symbol}
- Timeframe: {timeframe}
- Period: {metrics['start_date']} to {metrics['end_date']}
- Duration: {metrics['duration_days']} days

## Performance Metrics

### Primary Metrics (for autoresearch)
- **Sharpe Ratio**: {metrics['sharpe_ratio']:.2f}
- **Max Drawdown**: {metrics['max_drawdown']:.2f}%
- **Total Return**: {metrics['total_return']:.2f}%
- **Compound Score**: {calculate_compound_score(metrics['sharpe_ratio'], metrics['max_drawdown'], metrics['win_rate']):.3f}

### Secondary Metrics
- Sortino Ratio: {metrics['sortino_ratio']:.2f}
- Calmar Ratio: {metrics['calmar_ratio']:.2f}
- Win Rate: {metrics['win_rate']:.1f}%
- Profit Factor: {metrics['profit_factor']:.2f}

### Trade Statistics
- Total Trades: {metrics['total_trades']}
- Average Trade: ${metrics['avg_trade']:.2f}
- Best Trade: ${metrics['best_trade']:.2f}
- Worst Trade: ${metrics['worst_trade']:.2f}

## Safety Check
"""

    # Add safety gates
    passed, checks = check_safety_gates(metrics)
    report += "\n### Safety Gates\n"
    for check, result in checks.items():
        status = "✓ PASS" if result else "✗ FAIL"
        report += f"- {check}: {status}\n"

    if not passed:
        report += "\n⚠️  **WARNING**: Strategy FAILED safety gates!\n"
    else:
        report += "\n✓ Strategy PASSED all safety gates\n"

    # Save or print
    if save_path:
        with open(save_path, 'w') as f:
            f.write(report)
        print(f"Report saved to: {save_path}")
    else:
        print(report)

    return report

# Usage
generate_backtest_report(
    strategy='EMA Crossover (12, 26)',
    symbol='EURUSD',
    timeframe='H1',
    metrics=metrics,
    pf=pf,
    save_path='backtest_report.md'
)
```

### Step 8: Export Trades

```python
def export_trades(pf, filename='trades.csv'):
    """Export trade list to CSV."""
    trades = pf.trades.records_readable

    # Select relevant columns
    export_cols = [
        'Entry Index', 'Exit Index',
        'Entry Price', 'Exit Price',
        'Size', 'Return', 'PnL'
    ]

    # Filter available columns
    avail_cols = [col for col in export_cols if col in trades.columns]

    trades[avail_cols].to_csv(filename, index=False)
    print(f"✓ Trades exported to: {filename}")

    return trades

# Usage
export_trades(pf, 'eurusd_ema_trades.csv')
```

### Step 9: Plot Results

```python
def plot_backtest(pf, save_path=None):
    """Plot backtest results."""

    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    # Create subplots
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.5, 0.25, 0.25],
        subplot_titles=('Equity Curve', 'Drawdown', 'Cumulative Returns')
    )

    # Equity curve
    equity = pf.value()
    equity_norm = equity / equity.iloc[0] * 100
    fig.add_trace(
        go.Scatter(x=equity.index, y=equity_norm, name='Equity', line=dict(color='#2ECC40')),
        row=1, col=1
    )

    # Drawdown
    equity['cummax'] = equity.cummax()
    dd = (equity - equity['cummax']) / equity['cummax'] * 100
    fig.add_trace(
        go.Scatter(x=dd.index, y=dd, name='Drawdown', fill='tozeroy', line=dict(color='#E74C3C')),
        row=2, col=1
    )

    # Cumulative returns
    cum_ret = (equity / equity.iloc[0] - 1) * 100
    fig.add_trace(
        go.Scatter(x=cum_ret.index, y=cum_ret, name='Returns %', line=dict(color='#3498DB')),
        row=3, col=1
    )

    # Layout
    fig.update_yaxes(title_text='Equity ($)', row=1, col=1)
    fig.update_yaxes(title_text='Drawdown (%)', row=2, col=1)
    fig.update_yaxes(title_text='Returns (%)', row=3, col=1)
    fig.update_layout(
        title='Backtest Results',
        template='plotly_dark',
        height=800,
        showlegend=True
    )

    if save_path:
        fig.write_html(save_path)
        print(f"Plot saved to: {save_path}")
    else:
        fig.show()

    return fig

# Usage
plot_backtest(pf, save_path='backtest_plots.html')
```

## Quick Backtest Function

```python
def quick_backtest(strategy, symbol='EURUSD', timeframe='H1', bars=1000):
    """Complete quick backtest workflow."""

    print(f"Running backtest: {strategy} on {symbol} ({timeframe})")

    # Fetch data
    df = fetch_mt5_data(symbol, timeframe, bars)
    close = df['Close']
    high = df['High']
    low = df['Low']

    # Generate signals
    if strategy == 'ema-crossover':
        entries, exits = ema_crossover_signals(close)
    elif strategy == 'rsi':
        entries, exits = rsi_signals(close)
    elif strategy == 'donchian':
        entries, exits = donchian_signals(high, low)
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    # Run backtest
    pf = run_backtest(close, entries, exits)

    # Calculate metrics
    metrics = calculate_metrics(pf)

    # Print summary
    print(f"\n{'='*50}")
    print(f"Results: {strategy}")
    print(f"{'='*50}")
    print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
    print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
    print(f"Total Return: {metrics['total_return']:.2f}%")
    print(f"Win Rate: {metrics['win_rate']:.1f}%")
    print(f"Compound Score: {calculate_compound_score(metrics['sharpe_ratio'], metrics['max_drawdown'], metrics['win_rate']):.3f}")

    # Safety check
    passed, checks = check_safety_gates(metrics)
    print(f"\nSafety Gates: {'✓ PASS' if passed else '✗ FAIL'}")

    return pf, metrics

# Usage
pf, metrics = quick_backtest('ema-crossover', 'EURUSD', 'H1', 1000)
```

## Optimization (Parameter Sweep)

```python
def optimize_ema_parameters(close, fast_range, slow_range):
    """Optimize EMA parameters using grid search."""

    import numpy as np

    best_score = -1
    best_params = None
    results = []

    for fast in fast_range:
        for slow in slow_range:
            if slow <= fast:
                continue

            # Generate signals
            entries, exits = ema_crossover_signals(close, fast=fast, slow=slow)

            # Run backtest
            pf = run_backtest(close, entries, exits)
            metrics = calculate_metrics(pf)

            # Calculate score
            score = calculate_compound_score(
                metrics['sharpe_ratio'],
                metrics['max_drawdown'],
                metrics['win_rate']
            )

            # Check safety
            passed, _ = check_safety_gates(metrics)

            # Store results
            results.append({
                'fast': fast,
                'slow': slow,
                'score': score,
                'sharpe': metrics['sharpe_ratio'],
                'max_dd': metrics['max_drawdown'],
                'return': metrics['total_return'],
                'safe': passed
            })

            # Track best
            if passed and score > best_score:
                best_score = score
                best_params = {'fast': fast, 'slow': slow}

    return pd.DataFrame(results), best_params

# Usage
results_df, best_params = optimize_ema_parameters(
    close,
    fast_range=range(8, 20, 2),
    slow_range=range(20, 40, 4)
)

print(f"Best parameters: EMA({best_params['fast']}, {best_params['slow']})")
print(results_df.sort_values('score', ascending=False).head(10))
```

## Related Skills

- mt5-integration: MT5 data fetching
- autoresearch-trading: Research methodology
- vectorbt-skills: Advanced VectorBT patterns
