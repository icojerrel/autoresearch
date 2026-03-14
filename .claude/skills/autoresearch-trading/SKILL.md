---
name: autoresearch-trading
description: Autonomous trading strategy research using autoresearch methodology. 5-minute AI training loops adapted for 1-week paper trading experiments. Generates strategy variants, tests them, keeps what works, discards what doesn't. Git-based versioning with compound scoring (Sharpe + Max DD + Win Rate).
argument-hint: "[baseline_strategy] [symbol] [weeks_per_experiment]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, TaskCreate, TaskUpdate
user-invocable: true
---

# Autoresearch Trading Skill

## Vision
Apply Andrej Karpathy's autoresearch methodology to trading strategy development. AI agents autonomously experiment with strategy variants, test them via backtesting + paper trading, and continuously improve performance.

## Core Concept: LLM Training → Trading

| autoresearch (LLM) | Trading (MT5) |
|-------------------|---------------|
| Model architecture | Trading strategy |
| 5-min training loop | 1-week paper trading |
| val_bPB metric | Compound score (Sharpe 50% + DD safety 30% + Win Rate 20%) |
| Git commits per experiment | Strategy versions in git |
| AI modifies train.py | AI modifies strategy.py |
| GPU memory monitoring | Trading capital tracking |
| Keep if val_bPB improves | Keep if score improves |

## Arguments
Parse `$ARGUMENTS` as: baseline_strategy symbol weeks_per_experiment

- `$0` = Baseline strategy (ema-crossover, rsi, etc.). Default: ema-crossover
- `$1` = Symbol to trade (EURUSD, GBPUSD, etc.). Default: EURUSD
- `$2` = Weeks per experiment (paper trading duration). Default: 1

If no arguments, ask user to specify.

## Research Loop Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                   AUTORESEARCH ENGINE                           │
│                                                                  │
│  1. PLANNING (Auto-Claude)                                      │
│     Agent proposes strategy variant                              │
│     - Parameter tweaks (EMA periods, RSI levels)                │
│     - Logic modifications (add filters, combine signals)        │
│     - Multi-strategy combinations                               │
│                                                                  │
│  2. VALIDATION (decapod)                                        │
│     Safety checks before execution                              │
│     - Risk limits respected?                                    │
│     - No dangerous logic?                                       │
│     - Within experimental bounds?                               │
│                                                                  │
│  3. EXPERIMENT (MT5 Paper Trading)                             │
│     Fixed time budget: 1 week                                   │
│     - Historical backtest (vectorbt) → quick validation         │
│     - Forward test (paper trading) → real validation            │
│                                                                  │
│  4. EVALUATION                                                  │
│     Calculate metrics                                           │
│     - Primary: Compound score                                   │
│     - Safety: Max DD, Daily VaR                                 │
│     - Secondary: Win Rate, Profit Factor                        │
│                                                                  │
│  5. DECISION                                                    │
│     Compare vs baseline                                         │
│     - Improved? → Keep & commit                                 │
│     - Worse? → Discard                                          │
│     - Similar? → Note & continue                                │
│                                                                  │
│  6. LEARNING (continuous-learning-skill)                       │
│     Extract patterns from successful experiments                │
│     - What parameter ranges work?                               │
│     - What market conditions?                                   │
│     - Store in knowledge base                                   │
│                                                                  │
│  7. REPEAT                                                      │
│     Continue until improvement plateaus or manual stop           │
└─────────────────────────────────────────────────────────────────┘
```

## Metrics

### Primary: Compound Score

```python
def calculate_strategy_score(sharpe, max_dd, win_rate):
    """
    Calculate compound score (higher = better)
    Used as primary metric for strategy comparison

    Weights:
    - Sharpe Ratio: 50% (risk-adjusted returns)
    - Max Drawdown: 30% (capital preservation)
    - Win Rate: 20% (consistency)
    """
    # Normalize components (0-1 scale)
    sharpe_norm = max(0, min(sharpe / 3, 1))  # Assume 3.0 is excellent
    dd_norm = 1 - max(0, min(max_dd / 50, 1))  # 50% DD = 0
    win_norm = win_rate  # Already 0-1

    # Calculate weighted score
    score = (sharpe_norm * 0.5 +
             dd_norm * 0.3 +
             win_norm * 0.2)

    return score
```

### Safety Gates (Must Pass)

```python
def safety_gates(metrics):
    """
    Hard safety limits. Strategy fails ANY of these = DISCARD.
    """
    checks = {
        'max_dd_acceptable': metrics['max_dd'] < 15,  # Max 15% drawdown
        'daily_var_acceptable': metrics['daily_var'] < 2,  # Max 2% daily VaR
        'consecutive_losses': metrics['consecutive_losses'] < 5,  # Max 5 losing trades
        'min_trades': metrics['total_trades'] >= 10,  # Minimum sample size
        'sharpe_positive': metrics['sharpe'] > 0,  # Must have positive risk-adjusted return
    }

    return all(checks.values()), checks
```

## Experiment Workflow

### Step 1: Initialize Experiment

```python
from datetime import datetime
import subprocess

experiment_id = f"E{datetime.now().strftime('%Y%m%d_%H%M%S')}"

# Create experiment branch
subprocess.run(['git', 'checkout', '-b', f'experiment/{experiment_id}'])

# Log experiment start
with open('experiments/log.tsv', 'a') as f:
    f.write(f"{experiment_id}\t{datetime.now()}\tSTART\t\t\n")
```

### Step 2: Generate Strategy Variant

Auto-Claude agent proposes modification:

```python
# Example: Modify EMA periods
variant = {
    'base_strategy': 'ema_crossover',
    'fast_ema': 14,  # Changed from 12
    'slow_ema': 28,  # Changed from 26
    'modification_type': 'parameter_tweak',
    'rationale': 'Slower EMAs to reduce noise'
}
```

### Step 3: Run Backtest (Quick Validation)

```python
import vectorbt as vbt

# Fetch historical data
df = fetch_mt5_data('EURUSD', 'H1', bars=1000)
close = df['Close']

# Generate signals
ema_fast = vbt.MA.run(close, variant['fast_ema'], ewm=True)
ema_slow = vbt.MA.run(close, variant['slow_ema'], ewm=True)
entries = ema_fast.ma_crossed_above(ema_slow)
exits = ema_fast.ma_crossed_below(ema_slow)

# Backtest
pf = vbt.Portfolio.from_signals(close, entries, exits,
                                  init_cash=10000, fees=0.001)

# Calculate metrics
metrics = {
    'sharpe': pf.sharpe_ratio(),
    'max_dd': pf.max_drawdown() * 100,
    'win_rate': pf.trades.win_rate(),
    'total_return': pf.total_return() * 100,
}

# Quick safety check
passed, checks = safety_gates(metrics)
if not passed:
    # Fail fast - don't proceed to paper trading
    return "FAILED_SAFETY", checks
```

### Step 4: Paper Trading (Real Test)

```python
import MetaTrader5 as mt5
from datetime import timedelta

# Initialize MT5
mt5.initialize()

# Paper trading duration
duration_weeks = 1
end_time = datetime.now() + timedelta(weeks=duration_weeks)

# Deploy to MT5 demo account
deploy_strategy_to_mt5(variant)

# Monitor for duration
while datetime.now() < end_time:
    # Check for stop signals
    if should_stop_experiment():
        break

    # Record performance
    record_paper_trading_metrics()

    # Sleep
    time.sleep(3600)  # Check hourly

# Get paper trading results
paper_metrics = get_paper_trading_results()

# Shutdown MT5
mt5.shutdown()
```

### Step 5: Evaluate and Decide

```python
# Compare with baseline
baseline_score = calculate_strategy_score(
    baseline_metrics['sharpe'],
    baseline_metrics['max_dd'],
    baseline_metrics['win_rate']
)

variant_score = calculate_strategy_score(
    paper_metrics['sharpe'],
    paper_metrics['max_dd'],
    paper_metrics['win_rate']
)

# Decision
if variant_score > baseline_score * 1.05:  # 5% improvement threshold
    decision = "KEEP"
    action = "commit_and_update_baseline"
elif variant_score < baseline_score * 0.95:  # 5% worse threshold
    decision = "DISCARD"
    action = "abandon_branch"
else:
    decision = "SIMILAR"
    action = "note_and_continue"
```

### Step 6: Update Knowledge Base

```python
# Extract learnings
if decision == "KEEP":
    learning = {
        'experiment_id': experiment_id,
        'successful_params': variant,
        'score_improvement': variant_score - baseline_score,
        'market_conditions': get_market_regime(),
        'timestamp': datetime.now()
    }

    # Store in continuous-learning knowledge base
    store_knowledge('successful_strategy_params', learning)
```

## Strategy Templates

### EMA Crossover (Baseline)

```python
# strategy/ema_crossover.py
def ema_crossover_signals(close, fast=12, slow=26):
    """
    Generate EMA crossover signals.

    Args:
        close: Price series
        fast: Fast EMA period
        slow: Slow EMA period

    Returns:
        entries: Boolean series for buy signals
        exits: Boolean series for sell signals
    """
    import vectorbt as vbt

    ema_fast = vbt.MA.run(close, fast, ewm=True)
    ema_slow = vbt.MA.run(close, slow, ewm=True)

    entries = ema_fast.ma_crossed_above(ema_slow)
    exits = ema_fast.ma_crossed_below(ema_slow)

    return entries, exits
```

### RSI Mean Reversion

```python
# strategy/rsi_mean_reversion.py
def rsi_signals(close, period=14, oversold=30, overbought=70):
    """
    Generate RSI mean reversion signals.

    Args:
        close: Price series
        period: RSI period
        oversold: Oversold threshold (buy signal)
        overbought: Overbought threshold (sell signal)

    Returns:
        entries: Boolean series for buy signals
        exits: Boolean series for sell signals
    """
    import vectorbt as vbt

    rsi = vbt.RSI.run(close, window=period)

    entries = rsi.rsi_crossed_below(oversold)
    exits = rsi.rsi_crossed_above(overbought)

    return entries, exits
```

## Experiment Tracking

### Log Format (experiments/results.tsv)

```tsv
experiment_id	timestamp	strategy	variant	modification	sharpe	max_dd	win_rate	total_return	score	decision	notes
E001	2026-03-14 10:00	ema_crossover	{"fast":12,"slow":26}	baseline	1.2	8.5	55	12	0.65	BASELINE	Initial baseline
E002	2026-03-14 12:00	ema_crossover	{"fast":14,"slow":28}	parameter_tweak	1.3	7.8	57	14	0.68	KEEP	5% improvement
E003	2026-03-14 14:00	ema_crossover	{"fast":10,"slow":20}	parameter_tweak	0.9	12	48	8	0.52	DISCARD	Too much noise
```

## Auto-Claude Integration

### Agent Prompt Template

```
You are a trading strategy researcher. Your task is to propose a strategy variant
that could improve upon the current baseline.

Baseline Strategy: {baseline_strategy}
Baseline Metrics: {baseline_metrics}
Recent Successful Patterns: {knowledge_base_patterns}

Propose a variant with:
1. Specific parameter changes or logic modifications
2. Rationale for why this might improve performance
3. Expected impact on Sharpe ratio, Max DD, Win Rate

Constraints:
- Max drawdown must stay below 15%
- Strategy must be testable within 1 week
- Logic must be explainable and debuggable
```

## Common Experiment Patterns

### Pattern 1: Parameter Sweep

```python
# Systematically test parameter ranges
fast_ema_range = range(8, 20, 2)  # 8, 10, 12, 14, 16, 18
slow_ema_range = range(20, 40, 4)  # 20, 24, 28, 32, 36

for fast in fast_ema_range:
    for slow in slow_ema_range:
        if slow > fast:
            run_experiment(fast_ema=fast, slow_ema=slow)
```

### Pattern 2: Filter Addition

```python
# Add confirmation filter to reduce false signals
def ema_with_rsi_filter(close, fast=12, slow=26, rsi_period=14):
    # EMA signals
    ema_entries, ema_exits = ema_crossover_signals(close, fast, slow)

    # RSI filter (only trade when RSI is not extreme)
    rsi = vbt.RSI.run(close, rsi_period)
    rsi_safe = (rsi.rsi > 30) & (rsi.rsi < 70)

    # Combine
    entries = ema_entries & rsi_safe
    exits = ema_exits

    return entries, exits
```

### Pattern 3: Multi-Strategy Ensemble

```python
def ensemble_signals(close, weights=None):
    """Combine multiple strategies."""
    if weights is None:
        weights = {
            'ema_crossover': 0.5,
            'rsi_mean_reversion': 0.3,
            'momentum': 0.2
        }

    # Get signals from each strategy
    ema_entries, ema_exits = ema_crossover_signals(close)
    rsi_entries, rsi_exits = rsi_signals(close)
    mom_entries, mom_exits = momentum_signals(close)

    # Weighted voting
    entry_score = (
        ema_entries.astype(int) * weights['ema_crossover'] +
        rsi_entries.astype(int) * weights['rsi_mean_reversion'] +
        mom_entries.astype(int) * weights['momentum']
    )

    # Threshold for entry
    entries = entry_score > 0.5

    return entries, ema_exits  # Use EMA for exits
```

## Best Practices

1. **Start Simple**: EMA crossover is sufficient for baseline
2. **One Change at a Time**: Test one variable per experiment
3. **Statistical Significance**: Minimum 10 trades per experiment
4. **Out-of-Sample Testing**: Keep final test data separate
5. **Risk Management**: Never risk > 2% per trade
6. **Paper Trading Mandatory**: Never skip paper trading phase
7. **Document Everything**: Log rationale, not just results
8. **Know When to Stop**: Stop if 10 consecutive experiments fail

## Troubleshooting

### Problem: No improvement after 20 experiments
**Solution**:
- Check if market regime has changed
- Review if baseline is already optimal
- Consider different strategy class
- Expand parameter search space

### Problem: All experiments failing safety gates
**Solution**:
- Reduce position size
- Add stop-loss to strategy
- Check data quality
- Review market conditions (high volatility?)

### Problem: Paper trading differs greatly from backtest
**Solution**:
- Check for slippage in execution
- Verify data feed quality
- Review order execution timing
- Consider spread impact (especially for scalping)

## Related Skills

- mt5-integration: MT5 Python API
- mt5-backtest: Backtesting with vectorbt
- paper-trading-manager: Manage paper trading experiments
- strategy-generator: Auto-Claude strategy variant generation
