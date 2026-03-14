# MT5 Strategy Autoresearcher

> Autonomous trading strategy improvement using AI-powered research methodology

**Vision:** Apply Andrej Karpathy's autoresearch concept to trading strategies - AI agents that autonomously experiment, test, and improve trading systems on MT5.

---

## 🎯 What This Does

Builds a system where AI agents:
1. **Generate strategy variants** (parameter tweaks, logic changes, combinations)
2. **Backtest quickly** (VectorBT with MT5 historical data)
3. **Paper trade for 1 week** (real market conditions, no risk)
4. **Evaluate automatically** (compound score: Sharpe + Drawdown + Win Rate)
5. **Keep what works, discard what doesn't** (git-based versioning)
6. **Learn patterns** (continuous knowledge extraction)
7. **Repeat** (until improvement plateaus)

### The Key Innovation

Instead of manually tweaking strategies and hoping for the best, this system:
- Runs 100+ autonomous experiments per strategy
- Tests each in real market conditions (paper trading)
- Objectively compares results using standardized metrics
- Accumulates knowledge about what works
- Continuously improves baseline performance

---

## 📊 Current Status

| Metric | Target | Current |
|--------|--------|---------|
| Experiments Run | 100+ | 🔄 Starting |
| Baseline Sharpe | > 1.5 | TBD |
| Max Acceptable DD | < 15% | Enforced |
| Paper Trading Weeks | 52 | 0 |
| Autonomy Level | 90%+ | Manual → Auto |

**Phase:** 🟡 Foundation | **Confidence:** Growing

---

## 🚀 Quick Start

### Prerequisites

- MT5 Terminal installed
- Python 3.12+
- Demo MT5 account (for paper trading)

### Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install MetaTrader5 pandas numpy vectorbt plotly
```

### First Experiment

```bash
# 1. Connect to MT5 and fetch data
# (Trigger: "MT5 data ophalen EURUSD")

# 2. Run quick backtest
# (Trigger: "/mt5-backtest ema-crossover EURUSD H1 1000")

# 3. Generate strategy variants
# (Trigger: "/strategy-generator ema-crossover balanced")

# 4. Start autonomous research
# (Trigger: "/autoresearch-trading ema-crossover EURUSD 1")
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTROL LAYER                             │
│  Auto-Claude (agents) ←→ decapod (safety) ←→ Learning      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    RESEARCH LOOP                             │
│  1. Generate variants (strategy-generator)                  │
│  2. Quick backtest (mt5-backtest)                           │
│  3. Paper trading (paper-trading-manager)                   │
│  4. Evaluate (compound score)                                │
│  5. Keep/Discard (git versioning)                            │
│  6. Learn (continuous-learning)                              │
│  7. Repeat                                                  │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    EXECUTION LAYER                           │
│  MT5 Terminal (demo) ←→ Paper Trading ←→ Live (future)     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📁 Project Structure

```
mt5-autoresearcher/
├── .claude/
│   └── skills/              # Claude Code skills (auto-activated)
│       ├── mt5-integration/ # MT5 Python API
│       ├── autoresearch-trading/  # Main research loop
│       ├── strategy-generator/     # Variant generation
│       ├── paper-trading-manager/  # Experiment lifecycle
│       └── mt5-backtest/           # VectorBT backtesting
│
├── docs/                   # Documentation
│   ├── README.md          # Documentation index
│   ├── SAMENVATTING.md    # Repository overview
│   ├── ARCHITECTUUR.md    # System architecture
│   ├── COMPONENTEN.md    # Reusable components
│   └── DEPENDENCIES.md   # Install guide
│
├── experiments/            # Experiment results (git ignored)
│
├── strategy/               # Strategy implementations (to create)
│
├── research.md            # Live research log (dynamic!)
├── SKILLS.md             # Skills reference
└── README.md             # This file
```

---

## 🤖 Claude Skills

This project includes 5 specialized Claude Code skills:

### Core Skills
- **mt5-integration** - MT5 API, data fetching, order execution
- **autoresearch-trading** - Main research orchestrator
- **strategy-generator** - AI-powered variant generation
- **paper-trading-manager** - Experiment lifecycle
- **mt5-backtest** - Quick backtesting with VectorBT

### How They Work
Skills auto-activate based on context:
```
User: "Test EMA crossover with faster parameters"
↓
mt5-backtest skill activates
↓
Fetches MT5 data, runs backtest, returns metrics
```

**See:** [SKILLS.md](SKILLS.md) for complete skill reference

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [research.md](research.md) | **Live research log** - experiments, insights, decisions |
| [docs/README.md](docs/README.md) | Documentation index |
| [docs/SAMENVATTING.md](docs/SAMENVATTING.md) | 8 repositories overview |
| [docs/ARCHITECTUUR.md](docs/ARCHITECTUUR.md) | Integration patterns |
| [docs/COMPONENTEN.md](docs/COMPONENTEN.md) | Reusable modules |
| [docs/DEPENDENCIES.md](docs/DEPENDENCIES.md) | Installation guide |
| [SKILLS.md](SKILLS.md) | Claude skills reference |

---

## 🎯 Research Goals

### Phase 1: Foundation (Weeks 1-4)
- [ ] MT5 integration working
- [ ] Baseline EMA strategy backtested
- [ ] First 10 experiments completed
- [ ] Auto-Claude generating suggestions

**Milestone:** Fully autonomous experiment loop running

### Phase 2: Optimization (Weeks 5-8)
- [ ] 100+ experiments completed
- [ ] Best strategy identified
- [ ] Paper trading validated (4 weeks)
- [ ] continuous-learning extracting patterns

**Milestone:** Strategy beats baseline significantly

### Phase 3: Expansion (Weeks 9-12)
- [ ] Multiple strategies (RSI, Donchian)
- [ ] Multiple pairs (GBP, JPY)
- [ ] Ensemble research

**Milestone:** Diversified strategy portfolio

### Phase 4: Live Trading (Week 13+)
- [ ] Small live test (1% capital)
- [ ] Performance validation
- [ ] Scale up gradually

**Milestone:** Profitable live trading

---

## 🔬 Methodology

### The autoresearch Approach

Adapted from [autoresearch](https://github.com/karpathy/autoresearch):

| LLM Research | Trading Research |
|--------------|-----------------|
| 5-min training | 1-week paper trading |
| val_bPB metric | Compound score (Sharpe + DD + Win Rate) |
| GPU memory | Trading capital |
| Git commits | Strategy versions |

### Key Metrics

**Primary (for comparison):**
```python
score = sharpe_normalized * 0.5 + drawdown_normalized * 0.3 + win_rate * 0.2
```

**Safety Gates (must pass):**
- Max DD < 15%
- Sharpe > 0
- Min 10 trades
- Win rate > 30%

---

## 🛡️ Safety

### Risk Management
- **Paper trading mandatory** before live
- **Hard position limits** (max 2% equity)
- **Auto-stop on excessive drawdown** (15%)
- **Human override** always available
- **Demo accounts only** for research

### AI Safety
- **decapod enforcement layers** validate all actions
- **No autonomous live trading** without approval
- **Transparent logging** of all decisions
- **Kill switches** for emergency stops

---

## 🔗 Related Projects

This project integrates code/concepts from:

| Repository | Purpose | Usage |
|------------|---------|-------|
| [autoresearch](https://github.com/karpathy/autoresearch) | Methodology inspiration | Research loop pattern |
| [Auto-Claude](https://github.com/icojerrel/Auto-Claude) | Multi-agent framework | Strategy generation |
| [decapod](https://github.com/icojerrel/decapod) | Control plane | Safety enforcement |
| [QuantMuse](https://github.com/icojerrel/QuantMuse) | Trading system | Factor analysis |
| [vectorbt-backtesting-skills](https://github.com/icojerrel/vectorbt-backtesting-skills) | Backtesting | VectorBT patterns |

---

## 📊 Progress

### Latest Updates
- **2026-03-14**: Project initialized, documentation created
- **2026-03-14**: 5 Claude skills created
- **2026-03-14**: Git repository setup
- **Pending**: First MT5 connection test

### Next Steps
1. Open MT5 demo account
2. Test first data fetch
3. Run baseline backtest
4. Start autonomous experiments

---

## 📄 License

MIT License

---

**Happy Autonomous Trading!** 🚀📈
