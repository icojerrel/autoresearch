---
name: paper-trading-manager
description: Manage MT5 paper trading experiments for autoresearch. Handles experiment deployment, monitoring, data collection, and automated termination after time budget. Tracks performance metrics and generates experiment reports.
argument-hint: "[experiment_id] [duration_days]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
user-invocable: true
---

# Paper Trading Manager Skill

## Overview
Manages the complete paper trading experiment lifecycle: deployment, monitoring, data collection, and reporting. Ensures experiments run for specified duration, collect all relevant metrics, and terminate cleanly.

## Arguments
Parse `$ARGUMENTS` as: experiment_id duration_days

- `$0` = Experiment ID (e.g., E001). Default: auto-generate
- `$1` = Duration in days. Default: 7

## Experiment Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│  1. PREPARATION                                             │
│     - Validate MT5 connection                               │
│     - Check account balance                                 │
│     - Load strategy configuration                           │
│     - Set risk limits                                       │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  2. DEPLOYMENT                                              │
│     - Deploy strategy to MT5 demo account                   │
│     - Set up monitoring                                     │
│     - Start data logging                                    │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  3. MONITORING                                              │
│     - Track positions in real-time                          │
│     - Record equity curve                                   │
│     - Check risk limits                                    │
│     - Detect anomalies                                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  4. COMPLETION                                              │
│     - Terminate after time budget                           │
│     - Or early stop if safety breach                         │
│     - Close all positions                                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│  5. ANALYSIS                                                │
│     - Calculate performance metrics                         │
│     - Generate report                                       │
│     - Compare to baseline                                   │
└─────────────────────────────────────────────────────────────┘
```

## Step 1: Prepare Experiment

```python
import MetaTrader5 as mt5
from datetime import datetime, timedelta
import json

def prepare_experiment(experiment_id, strategy_config, duration_days):
    """Prepare paper trading experiment."""

    # Validate MT5 connection
    if not mt5.initialize():
        raise Exception("Cannot connect to MT5")

    # Check account
    account = mt5.account_info()
    if not account:
        raise Exception("No MT5 account found")

    # Verify demo account
    if account.balance > 10000:  # Arbitrary threshold
        print("⚠️  WARNING: This appears to be a LIVE account!")
        print("    Only use DEMO accounts for paper trading!")
        response = input("Continue anyway? (yes/no): ")
        if response.lower() != 'yes':
            mt5.shutdown()
            raise Exception("User aborted - use demo account")

    # Calculate experiment end time
    start_time = datetime.now()
    end_time = start_time + timedelta(days=duration_days)

    # Create experiment directory
    import os
    exp_dir = f"experiments/{experiment_id}"
    os.makedirs(exp_dir, exist_ok=True)

    # Save experiment config
    config = {
        'experiment_id': experiment_id,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration_days': duration_days,
        'strategy': strategy_config,
        'account': {
            'login': account.login,
            'balance': account.balance,
            'equity': account.equity,
            'currency': account.currency
        }
    }

    with open(f'{exp_dir}/config.json', 'w') as f:
        json.dump(config, f, indent=2)

    print(f"✓ Experiment {experiment_id} prepared")
    print(f"  Start: {start_time}")
    print(f"  End: {end_time}")
    print(f"  Duration: {duration_days} days")

    return config
```

## Step 2: Deploy Strategy

```python
def deploy_strategy_to_mt5(experiment_id, strategy_code):
    """Deploy strategy to MT5 for paper trading."""

    # Option 1: Python script (recommended for autoresearch)
    # Write Python monitoring script
    monitor_script = f"""
import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime
import time

# Initialize MT5
mt5.initialize()

# Load strategy
{strategy_code}

# Main monitoring loop
end_time = datetime.fromisoformat('{config['end_time']}')
while datetime.now() < end_time:
    # Get signals
    entries, exits = strategy_signals()

    # Get current positions
    positions = mt5.positions_get(symbol='EURUSD')

    # Execute trades
    execute_strategy(entries, exits, positions)

    # Log state
    log_state()

    # Sleep until next bar
    time.sleep(60)  # Check every minute

# Cleanup
mt5.shutdown()
"""

    # Save monitor script
    with open(f"experiments/{experiment_id}/monitor.py", 'w') as f:
        f.write(monitor_script)

    print(f"✓ Strategy deployed to experiments/{experiment_id}/")
    return f"experiments/{experiment_id}/monitor.py"
```

## Step 3: Monitor Experiment

```python
def monitor_experiment(experiment_id, check_interval=60):
    """
    Monitor running experiment.

    Args:
        experiment_id: Experiment identifier
        check_interval: Seconds between checks
    """
    import MetaTrader5 as mt5
    import json
    from datetime import datetime

    # Load config
    with open(f"experiments/{experiment_id}/config.json", 'r') as f:
        config = json.load(f)

    end_time = datetime.fromisoformat(config['end_time'])

    # Monitoring data
    equity_curve = []
    trades_log = []

    print(f"Monitoring experiment {experiment_id}...")
    print(f"Ends at: {end_time}")

    while datetime.now() < end_time:
        # Check for early stop signals
        if should_stop_early(experiment_id):
            print("⚠️  Early stop signal detected")
            break

        # Get current state
        mt5.initialize()
        account = mt5.account_info()
        positions = mt5.positions_get()

        # Record equity
        equity_curve.append({
            'timestamp': datetime.now().isoformat(),
            'balance': account.balance,
            'equity': account.equity,
            'margin': account.margin,
            'margin_free': account.margin_free,
            'open_positions': len(positions) if positions else 0,
            'floating_pnl': sum(pos.profit for pos in positions) if positions else 0
        })

        # Check risk limits
        current_dd = calculate_current_drawdown(equity_curve)
        if current_dd > 15:  # Hard limit
            print(f"🚨 STOP: Drawdown exceeded 15%: {current_dd:.2f}%")
            close_all_positions()
            break

        # Log trades
        if positions:
            for pos in positions:
                trades_log.append({
                    'timestamp': datetime.now().isoformat(),
                    'ticket': pos.ticket,
                    'symbol': pos.symbol,
                    'type': 'BUY' if pos.type == mt5.POSITION_TYPE_BUY else 'SAVE',
                    'volume': pos.volume,
                    'price_open': pos.price_open,
                    'price_current': pos.price_current,
                    'profit': pos.profit
                })

        # Save state periodically
        if len(equity_curve) % 10 == 0:  # Every 10 checks
            save_monitoring_data(experiment_id, equity_curve, trades_log)

        # Progress update
        elapsed = (datetime.now() - datetime.fromisoformat(config['start_time'])).total_seconds()
        total = (end_time - datetime.fromisoformat(config['start_time'])).total_seconds()
        progress = (elapsed / total) * 100
        print(f"[{progress:.1f}%] Equity: ${account.equity:.2f} | Positions: {len(positions) if positions else 0}")

        # Wait for next check
        time.sleep(check_interval)

    # Final save
    save_monitoring_data(experiment_id, equity_curve, trades_log)
    print(f"✓ Experiment {experiment_id} monitoring complete")

    return equity_curve, trades_log
```

## Step 4: Complete Experiment

```python
def complete_experiment(experiment_id):
    """Clean up and finalize experiment."""

    import MetaTrader5 as mt5

    print(f"Completing experiment {experiment_id}...")

    # Initialize MT5
    if not mt5.initialize():
        print("⚠️  Cannot connect to MT5 for cleanup")
        return

    # Close all positions
    close_all_positions()

    # Get final account state
    account = mt5.account_info()

    final_state = {
        'timestamp': datetime.now().isoformat(),
        'balance': account.balance,
        'equity': account.equity,
        'total_profit': account.profit,
        'margin_used': account.margin,
    }

    # Save final state
    with open(f"experiments/{experiment_id}/final_state.json", 'w') as f:
        json.dump(final_state, f, indent=2)

    # Shutdown MT5
    mt5.shutdown()

    print(f"✓ Experiment {experiment_id} completed")
    print(f"  Final Balance: ${account.balance:.2f}")
    print(f"  Final Equity: ${account.equity:.2f}")
    print(f"  Total Profit: ${account.profit:.2f}")

    return final_state
```

## Step 5: Analyze Results

```python
def analyze_experiment(experiment_id):
    """Analyze experiment results and calculate metrics."""

    import pandas as pd
    import json

    # Load data
    with open(f"experiments/{experiment_id}/config.json", 'r') as f:
        config = json.load(f)

    with open(f"experiments/{experiment_id}/final_state.json", 'r') as f:
        final_state = json.load(f)

    equity_curve = pd.read_json(f"experiments/{experiment_id}/equity_curve.json")
    trades_log = pd.read_json(f"experiments/{experiment_id}/trades_log.json")

    # Calculate metrics
    initial_equity = config['account']['equity']
    final_equity = final_state['equity']
    total_return = (final_equity - initial_equity) / initial_equity * 100

    # Sharpe ratio (simplified)
    equity_curve['returns'] = equity_curve['equity'].pct_change()
    sharpe = equity_curve['returns'].mean() / equity_curve['returns'].std() * (252**0.5)

    # Max drawdown
    equity_curve['cummax'] = equity_curve['equity'].cummax()
    equity_curve['drawdown'] = (equity_curve['equity'] - equity_curve['cummax']) / equity_curve['cummax'] * 100
    max_dd = equity_curve['drawdown'].min()

    # Win rate
    if len(trades_log) > 0:
        winning_trades = len(trades_log[trades_log['profit'] > 0])
        win_rate = winning_trades / len(trades_log) * 100
        profit_factor = trades_log[trades_log['profit'] > 0]['profit'].sum() / abs(trades_log[trades_log['profit'] < 0]['profit'].sum())
    else:
        win_rate = 0
        profit_factor = 0

    # Compile metrics
    metrics = {
        'experiment_id': experiment_id,
        'total_return': total_return,
        'sharpe_ratio': sharpe,
        'max_drawdown': max_dd,
        'win_rate': win_rate,
        'profit_factor': profit_factor,
        'total_trades': len(trades_log),
        'final_equity': final_equity
    }

    # Save metrics
    with open(f"experiments/{experiment_id}/metrics.json", 'w') as f:
        json.dump(metrics, f, indent=2)

    # Generate report
    generate_experiment_report(experiment_id, config, metrics, equity_curve, trades_log)

    return metrics
```

## Utility Functions

```python
def close_all_positions():
    """Close all open positions."""
    import MetaTrader5 as mt5

    positions = mt5.positions_get()
    if not positions:
        return

    for pos in positions:
        close_request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": pos.symbol,
            "volume": pos.volume,
            "type": mt5.ORDER_TYPE_SELL if pos.type == mt5.POSITION_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": pos.ticket,
            "price": mt5.symbol_info_tick(pos.symbol).bid if pos.type == mt5.POSITION_TYPE_BUY else mt5.symbol_info_tick(pos.symbol).ask,
            "deviation": 20,
            "magic": 234000,
            "comment": "Experiment close",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(close_request)
        if result.retcode == mt5.TRADE_RETCODE_DONE:
            print(f"✓ Closed position {pos.ticket}")
        else:
            print(f"✗ Failed to close position {pos.ticket}")

def calculate_current_drawdown(equity_curve):
    """Calculate current drawdown from equity curve."""
    if len(equity_curve) < 2:
        return 0

    import pandas as pd
    df = pd.DataFrame(equity_curve)
    df['cummax'] = df['equity'].cummax()
    df['drawdown'] = (df['equity'] - df['cummax']) / df['cummax'] * 100

    return df['drawdown'].iloc[-1]

def should_stop_early(experiment_id):
    """Check if experiment should stop early."""
    import os

    # Check for stop file
    stop_file = f"experiments/{experiment_id}/STOP"
    if os.path.exists(stop_file):
        return True

    return False

def save_monitoring_data(experiment_id, equity_curve, trades_log):
    """Save monitoring data to files."""
    import json

    with open(f"experiments/{experiment_id}/equity_curve.json", 'w') as f:
        json.dump(equity_curve, f)

    with open(f"experiments/{experiment_id}/trades_log.json", 'w') as f:
        json.dump(trades_log, f)
```

## Experiment Report

```python
def generate_experiment_report(experiment_id, config, metrics, equity_curve, trades_log):
    """Generate comprehensive experiment report."""

    report = f"""
# Experiment Report: {experiment_id}

## Configuration
- Strategy: {config['strategy']['name']}
- Parameters: {config['strategy']['parameters']}
- Duration: {config['duration_days']} days
- Start: {config['start_time']}
- End: {config['end_time']}

## Performance Metrics
### Primary Metrics
- Total Return: {metrics['total_return']:.2f}%
- Sharpe Ratio: {metrics['sharpe_ratio']:.2f}
- Max Drawdown: {metrics['max_drawdown']:.2f}%

### Secondary Metrics
- Win Rate: {metrics['win_rate']:.1f}%
- Profit Factor: {metrics['profit_factor']:.2f}
- Total Trades: {metrics['total_trades']}

### Safety Check
- Max Drawdown < 15%: {'✓ PASS' if metrics['max_drawdown'] < 15 else '✗ FAIL'}

## Comparison to Baseline
(To be added when baseline is established)

## Notes
- All positions closed at end of experiment
- No unexpected anomalies detected
- Data quality: Good

## Files Generated
- config.json: Experiment configuration
- equity_curve.json: Full equity history
- trades_log.json: All trade records
- metrics.json: Performance metrics
- final_state.json: Final account state
"""

    with open(f"experiments/{experiment_id}/REPORT.md", 'w') as f:
        f.write(report)

    print(f"✓ Report generated: experiments/{experiment_id}/REPORT.md")
```

## Quick Commands

```bash
# Start new experiment
/paper-trading-manager E001 7

# Monitor existing experiment
/paper-trading-manager E001 --monitor

# Get experiment status
/paper-trading-manager E001 --status

# Stop experiment early
/paper-trading-manager E001 --stop

# Generate report
/paper-trading-manager E001 --report
```

## Related Skills

- autoresearch-trading: Main research methodology
- mt5-integration: MT5 API functions
- mt5-backtest: Backtesting validation
