# Claude Skills - Project Overview

## Beschikbare Skills

Dit project heeft 6 gespecialiseerde Claude skills die automatisch geactiveerd worden tijdens development.

---

## 🎯 Core Skills (MT5 Autoresearch)

### 1. mt5-integration
**Trigger:** "MT5 verbinden", "data ophalen", "EURUSD fetchen"

MetaTrader 5 Python API integration. Handles:
- MT5 terminal connecties
- Historical data export
- Real-time data streaming
- Order execution
- Account management

**Key Functions:**
```python
# Connect to MT5
mt5.initialize()

# Fetch data
df = fetch_mt5_data('EURUSD', 'H1', 1000)

# Place order
mt5.order_send(request)
```

---

### 2. autoresearch-trading
**Trigger:** "experiment uitvoeren", "strategy verbeteren", "autoresearch"

Autonome strategy research loop gebaseerd op autoresearch methodology:

1. **Planning** - Auto-Claude agent proposeert varianten
2. **Validation** - decapod safety gates
3. **Experiment** - 1-week paper trading
4. **Evaluation** - Compound score (Sharpe 50% + DD 30% + Win Rate 20%)
5. **Decision** - Keep if improved, discard if worse
6. **Learning** - continuous-learning extractie

**Key Concept:**
```
autoresearch (LLM) → MT5 Trading
5-min training → 1-week paper trading
val_bPB metric → Compound score
```

---

### 3. strategy-generator
**Trigger:** "nieuwe variant", "parameter suggestie", "strategy idee"

Auto-Claude powered strategy variant generator:

**Variant Types:**
- **Parameter Tweaks** - EMA periodes, RSI levels
- **Filter Additions** - RSI filter, ADX trend filter
- **Logic Modifications** - Triple EMA, pullback entries
- **Combinations** - Multi-strategy ensembles

**Output:**
```json
{
  "id": "V001",
  "type": "parameter_tweak",
  "changes": {"fast_ema": 14, "slow_ema": 28},
  "expected_impact": {
    "sharpe": "+0.1",
    "max_dd": "-1.5%"
  }
}
```

---

### 4. paper-trading-manager
**Trigger:** "paper trading starten", "experiment monitoren", "resultaten ophalen"

Complete experiment lifecycle management:

**Workflow:**
1. **Prepare** - Valideer MT5, check account
2. **Deploy** - Start strategy op demo account
3. **Monitor** - Track equity, positions, risk limits
4. **Complete** - Terminate na time budget
5. **Analyze** - Calculate metrics, generate report

**Safety Features:**
- Max drawdown monitoring (auto-stop at 15%)
- Position limit checks
- Early stop capability
- Comprehensive logging

---

### 5. mt5-backtest
**Trigger:** "backtest EMA", "test strategie", "optimaliseer parameters"

VectorBT backtesting aangepast voor MT5 forex data:

**Workflow:**
```python
# 1. Fetch MT5 data
df = fetch_mt5_data('EURUSD', 'H1', 1000)

# 2. Generate signals
entries, exits = ema_crossover_signals(df['Close'])

# 3. Run backtest
pf = vbt.Portfolio.from_signals(df['Close'], entries, exits)

# 4. Calculate metrics
metrics = calculate_metrics(pf)
```

**Metrics:**
- Primary: Sharpe Ratio, Max DD, Compound Score
- Secondary: Win Rate, Profit Factor, Calmar Ratio
- Safety: Gates (Max DD < 15%, Sharpe > 0)

---

## 🔄 Geïntegreerde Skills

### vectorbt-skills (from subrepo)
**Locatie:** `vectorbt-backtesting-skills/.claude/skills/`

5 skills voor India-focused backtesting:
- `/backtest` - Quick backtest scripts
- `/optimize` - Parameter optimization met heatmaps
- `/quick-stats` - Inline performance statistics
- `/strategy-compare` - Multi-strategy vergelijking
- `vectorbt-expert` - Reference patterns

**Note:** Deze zijn geoptimaliseerd voor OpenAlgo (Indiase markten). MT5 varianten zijn in mt5-backtest.

---

## 🎓 When to Use Which Skill

### Quick Validation
```
Idee: "Wat als ik EMA(14,28) probeer?"
→ /mt5-backtest ema-crossover EURUSD H1 1000
→ Resultaat in 30 seconden
```

### Full Experiment
```
Idee: "Autonoom strategy verbeteren"
→ /autoresearch-trading ema-crossover EURUSD 1
→ Volledige loop: varianten → backtest → paper trading → evaluatie
→ Duurt: 1 week per experiment
```

### Generate Ideas
```
Idee: "Ik wil betere varianten"
→ /strategy-generator ema-crossover balanced
→ Auto-Claude proposeert 3-5 varianten met rationale
```

### Monitor Progress
```
Idee: "Hoe gaat het experiment?"
→ /paper-trading-manager E001 --status
→ Real-time equity curve, open posities, PnL
```

---

## 📊 Skill Synergies

```
┌─────────────────────────────────────────────────────────────┐
│                    AUTORESEARCH LOOP                         │
│                                                                │
│  /autoresearch-trading (main orchestrator)                   │
│         ↓                                                      │
│  /strategy-generator (propose variants)                       │
│         ↓                                                      │
│  /mt5-backtest (quick validation)                             │
│         ↓                                                      │
│  /paper-trading-manager (real test)                           │
│         ↓                                                      │
│  Compare metrics → Keep/Discard                               │
│         ↓                                                      │
│  /continuous-learning (extract patterns)                     │
│         ↓                                                      │
│  [REPEAT]                                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Test MT5 Connection
```bash
# Activeer automatisch
Ik wil MT5 data ophalen voor EURUSD

→ mt5-integration skill activeert
→ Fetch 1000 bars H1 data
→ Returns pandas DataFrame
```

### 2. Quick Backtest
```bash
/mt5-backtest ema-crossover EURUSD H1 1000

→ Fetch data from MT5
→ Run EMA(12,26) crossover
→ Returns metrics + plots
```

### 3. Generate Variants
```bash
/strategy-generator ema-crossover sharpe

→ Auto-Claude analyzes baseline
→ Generates 3-5 variants
→ Each with rationale + expected impact
```

### 4. Start Experiment
```bash
/autoresearch-trading ema-crossover EURUSD 1

→ Full research loop
→ 1 week paper trading
→ Automated evaluation
→ Git versioning
```

---

## 🔧 Skill Configuration

Skills zijn geconfigureerd in `.claude/skills/[skill-name]/SKILL.md`

Elke skill bevat:
- **Description** - Wanneer activeert
- **Arguments** - Expected parameters
- **Instructions** - Exacte stappen
- **Code Templates** - Herbruikbare code
- **Error Handling** - Common issues

---

## 📝 Adding New Skills

### Template
```markdown
---
name: your-skill
description: What it does
argument-hint: "[param1] [param2]"
allowed-tools: Read, Write, Edit, Bash
user-invocable: true
---

# Skill Description

## When to Trigger
- User asks for X
- User mentions Y

## Instructions
1. Do this
2. Then that

## Code Example
```python
# Example code
```
```

### Location
```
.claude/skills/your-skill/SKILL.md
```

---

## 🐛 Troubleshooting

### Skill niet activerend?
- Check trigger phrases in description
- Verify SKILL.md syntax
- Restart Claude Code

### Foutmeldingen?
- Check allowed-tools in skill
- Verify dependencies installed
- See DEPENDENCIES.md

---

## 🔗 Related Documentation

- [docs/README.md](docs/README.md) - Project documentation
- [research.md](research.md) - Live research log
- [docs/ARCHITECTUUR.md](docs/ARCHITECTUUR.md) - System architecture
- [docs/COMPONENTEN.md](docs/COMPONENTEN.md) - Reusable components

---

**Last Updated:** 2026-03-14
**Skills Version:** 1.0
