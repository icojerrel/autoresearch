---
name: strategy-generator
description: Auto-Claude powered trading strategy variant generator. Analyzes baseline strategy, generates parameter tweaks, logic modifications, and multi-strategy combinations. Rationale-driven suggestions with expected impact on metrics.
argument-hint: "[baseline_strategy] [improvement_goal]"
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
user-invocable: true
---

# Strategy Generator Skill

## Overview
Uses Auto-Claude agent to intelligently generate trading strategy variants based on:
- Current baseline performance
- Historical successful patterns
- Market regime analysis
- Risk management constraints

## Arguments
Parse `$ARGUMENTS` as: baseline_strategy improvement_goal

- `$0` = Baseline strategy name. Default: ema-crossover
- `$1` = Improvement goal (sharpe, drawdown, winrate, balanced). Default: balanced

## Generation Process

### Step 1: Analyze Baseline

```python
# Read baseline configuration
baseline = read_strategy_config('ema-crossover')

# Get baseline metrics
baseline_metrics = {
    'sharpe': 1.2,
    'max_dd': 8.5,
    'win_rate': 55,
    'total_return': 12
}

# Analyze weaknesses
weaknesses = identify_weaknesses(baseline_metrics)
# Example: {'high_drawdown', 'low_win_rate'}
```

### Step 2: Query Knowledge Base

```python
# Get successful patterns from continuous-learning
successful_patterns = query_knowledge_base('successful_strategy_params')

# Get market regime
current_regime = detect_market_regime()
# Example: 'trending', 'ranging', 'volatile'
```

### Step 3: Generate Variants

Auto-Claude agent generates 3-5 variants:

```python
variants = []

# Variant 1: Parameter tweak
variants.append({
    'id': 'V001',
    'type': 'parameter_tweak',
    'description': 'Slower EMAs to reduce noise',
    'changes': {'fast_ema': 14, 'slow_ema': 28},
    'expected_impact': {
        'sharpe': '+0.1',
        'max_dd': '-1.5%',
        'win_rate': '+2%'
    },
    'rationale': 'Slower EMAs filter out short-term noise, focusing on larger trends'
})

# Variant 2: Add filter
variants.append({
    'id': 'V002',
    'type': 'filter_addition',
    'description': 'Add RSI filter to avoid overbought entries',
    'changes': {'rsi_filter': True, 'rsi_threshold': 70},
    'expected_impact': {
        'sharpe': '+0.15',
        'max_dd': '-2%',
        'win_rate': '+5%'
    },
    'rationale': 'RSI filter avoids entering when price is overextended, reducing drawdown'
})

# Variant 3: Logic modification
variants.append({
    'id': 'V003',
    'type': 'logic_modification',
    'description': 'Add ADX trend filter',
    'changes': {'adx_filter': True, 'adx_threshold': 25},
    'expected_impact': {
        'sharpe': '+0.2',
        'max_dd': '-3%',
        'win_rate': '+3%'
    },
    'rationale': 'ADX ensures we only trade when there is a strong trend, avoiding whipsaws'
})
```

### Step 4: Prioritize Variants

```python
# Score variants by expected improvement
for variant in variants:
    variant['priority_score'] = calculate_priority_score(
        variant['expected_impact'],
        improvement_goal,
        current_regime
    )

# Sort by priority
variants.sort(key=lambda v: v['priority_score'], reverse=True)
```

## Variant Types

### Type 1: Parameter Tweaks

Modify existing parameters within reasonable ranges:

```python
def generate_parameter_tweaks(baseline):
    """Generate parameter variations."""
    variants = []

    # EMA period variations
    fast_range = range(int(baseline['fast_ema'] * 0.7),
                       int(baseline['fast_ema'] * 1.3), 2)
    slow_range = range(int(baseline['slow_ema'] * 0.8),
                       int(baseline['slow_ema'] * 1.2), 4)

    for fast in fast_range:
        for slow in slow_range:
            if slow > fast:
                variants.append({
                    'fast_ema': fast,
                    'slow_ema': slow,
                    'rationale': f'EMA({fast},{slow}) - '
                               f'{"Faster" if fast < baseline["fast_ema"] else "Slower"} response'
                })

    return variants
```

### Type 2: Filter Additions

Add confirmation filters to existing logic:

```python
def generate_filter_additions(baseline):
    """Generate filter combinations."""
    filters = [
        {
            'name': 'RSI Filter',
            'params': {'rsi_period': 14, 'rsi_min': 30, 'rsi_max': 70},
            'rationale': 'Avoid extremes, trade only in safe RSI zone'
        },
        {
            'name': 'ADX Trend Filter',
            'params': {'adx_period': 14, 'adx_threshold': 25},
            'rationale': 'Only trade when trend is strong (ADX > 25)'
        },
        {
            'name': 'Volume Filter',
            'params': {'volume_ma_period': 20, 'volume_multiplier': 1.2},
            'rationale': 'Trade only when volume confirms the move'
        },
        {
            'name': 'Session Filter',
            'params': {'sessions': ['London', 'NY']},
            'rationale': 'Trade only during high-liquidity sessions'
        },
        {
            'name': 'Volatility Filter',
            'params': {'atr_period': 14, 'atr_multiplier': 1.5},
            'rationale': 'Avoid trading during low volatility (chop)'
        }
    ]

    return filters
```

### Type 3: Logic Modifications

Change the core strategy logic:

```python
def generate_logic_modifications(baseline):
    """Generate logic changes."""
    modifications = [
        {
            'name': 'Triple EMA',
            'description': 'Add third EMA for confirmation',
            'logic': 'Require price > EMA_slow AND EMA_fast > EMA_medium',
            'params': {'fast': 12, 'medium': 18, 'slow': 26}
        },
        {
            'name': 'EMA Crossover with Pullback',
            'description': 'Enter on pullback to EMA after crossover',
            'logic': 'Crossover happened, wait for price to touch EMA',
            'params': {'pullback_pct': 0.5}
        },
        {
            'name': 'Delayed Entry',
            'description': 'Wait N bars after crossover for confirmation',
            'logic': 'Enter on bar 3 after crossover signal',
            'params': {'delay_bars': 3}
        }
    ]

    return modifications
```

### Type 4: Multi-Strategy Combinations

Combine multiple strategies:

```python
def generate_combinations(baseline, available_strategies):
    """Generate strategy combinations."""
    combinations = [
        {
            'name': 'Trend + Mean Reversion',
            'strategies': ['ema_crossover', 'rsi_mean_reversion'],
            'weights': {'ema_crossover': 0.7, 'rsi_mean_reversion': 0.3},
            'rationale': 'Primary trend with counter-trend boost'
        },
        {
            'name': 'Multi-Timeframe',
            'strategies': ['ema_crossover_H1', 'ema_crossover_H4'],
            'logic': 'H1 signal + H4 trend alignment',
            'rationale': 'Trade only when timeframes agree'
        }
    ]

    return combinations
```

## Expected Impact Calculator

```python
def calculate_expected_impact(variant, baseline, goal):
    """
    Estimate expected impact on metrics.

    Returns dict with expected changes.
    """
    impact = {
        'sharpe': 0.0,
        'max_dd': 0.0,
        'win_rate': 0.0,
        'confidence': 'Low'
    }

    # Based on variant type
    if variant['type'] == 'parameter_tweak':
        # Conservative estimate
        impact['sharpe'] = '+0.05 to +0.15'
        impact['max_dd'] = '-0.5% to -2%'
        impact['confidence'] = 'Medium'

    elif variant['type'] == 'filter_addition':
        # Filters typically improve win rate and reduce DD
        impact['sharpe'] = '+0.1 to +0.2'
        impact['max_dd'] = '-1% to -3%'
        impact['win_rate'] = '+3% to +8%'
        impact['confidence'] = 'Medium-High'

    elif variant['type'] == 'logic_modification':
        # Higher risk, higher reward
        impact['sharpe'] = '-0.1 to +0.3'
        impact['max_dd'] = '-2% to +1%'
        impact['confidence'] = 'Low'

    elif variant['type'] == 'combination':
        # More complex, uncertain
        impact['sharpe'] = '+0.0 to +0.25'
        impact['max_dd'] = '-1% to -4%'
        impact['confidence'] = 'Medium'

    return impact
```

## Auto-Claude Prompt Template

```
You are a trading strategy optimization specialist. Your task is to generate
strategy variants that could improve upon the current baseline.

BASELINE STRATEGY: {baseline_name}
BASELINE PARAMETERS: {baseline_params}
BASELINE METRICS:
  - Sharpe Ratio: {sharpe}
  - Max Drawdown: {max_dd}%
  - Win Rate: {win_rate}%
  - Total Return: {total_return}%

CURRENT MARKET REGIME: {market_regime}
IMPROVEMENT GOAL: {goal} (sharpe/drawdown/winrate/balanced)

RECENT SUCCESSFUL PATTERNS:
{successful_patterns}

CONSTRAINTS:
- Max drawdown must stay below 15%
- Strategy must remain explainable
- One significant change per variant
- Must be testable within 1 week

Generate 3-5 variants with:
1. Specific changes (parameters or logic)
2. Rationale (why this might work)
3. Expected impact on each metric
4. Confidence level (Low/Medium/High)

Format each variant as:
---
Variant ID: V###
Type: [parameter_tweak|filter_addition|logic_modification|combination]
Description: [clear description]
Changes: [specific parameter/logic changes]
Rationale: [why this should improve performance]
Expected Impact:
  - Sharpe: [change]
  - Max DD: [change]
  - Win Rate: [change]
Confidence: [Low|Medium|High]
---
```

## Validation Checklist

Before testing a variant, ensure:

- [ ] Parameters are within reasonable bounds
- [ ] Logic is explainable and debuggable
- [ ] Changes align with improvement goal
- [ ] No violation of risk constraints
- [ ] Testable within paper trading duration
- [ ] Compatible with MT5 execution

## Common Patterns by Market Regime

### Trending Market

```python
trending_variants = [
    {'type': 'parameter_tweak', 'change': 'Slower EMAs (14/28)'},
    {'type': 'filter_addition', 'change': 'ADX trend filter'},
    {'type': 'logic_modification', 'change': 'Trailing stop'}
]
```

### Ranging Market

```python
ranging_variants = [
    {'type': 'parameter_tweak', 'change': 'Faster EMAs (8/16)'},
    {'type': 'filter_addition', 'change': 'Bollinger Band mean reversion'},
    {'type': 'logic_modification', 'change': 'Take profit at center'}
]
```

### Volatile Market

```python
volatile_variants = [
    {'type': 'parameter_tweak', 'change': 'Reduce position size'},
    {'type': 'filter_addition', 'change': 'ATR volatility filter'},
    {'type': 'logic_modification', 'change': 'Wider stops (2x ATR)'}
]
```

## Output Format

```python
# Generated variants saved to JSON
import json

variants_output = {
    'baseline': baseline_strategy,
    'generated_at': datetime.now().isoformat(),
    'variants': [
        {
            'id': 'V001',
            'type': 'parameter_tweak',
            'description': 'Slower EMAs reduce whipsaws',
            'changes': {'fast_ema': 14, 'slow_ema': 28},
            'code': generate_strategy_code('ema_crossover', {'fast': 14, 'slow': 28}),
            'expected_impact': {...},
            'rationale': '...',
            'confidence': 'Medium'
        },
        # ... more variants
    ]
}

with open('experiments/variants.json', 'w') as f:
    json.dump(variants_output, f, indent=2)
```

## Related Skills

- autoresearch-trading: Main research methodology
- mt5-backtest: Backtesting engine
- paper-trading-manager: Experiment management
