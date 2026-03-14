# Research Log - MT5 Strategy Autoresearcher

> **Vision**: Autonomous trading strategy improvement using autoresearch methodology
> **Focus**: MT5 (MetaTrader 5) Forex Trading → Backtesting → Paper Trading → Live
> **Last Updated**: 2026-03-14 15:42
> **Phase**: 🟡 Foundation | **Confidence**: Growing

---

## 🎯 Research Vision

### Kernconcept
**De autoresearch repository toepassen op trading strategieën**

Net als Andrej Karpathy's autoresearch AI agents autonomie LLM architecturen experimenteert en verbetert, willen we een systeem bouwen dat:

1. **Autonoom strategie varianten uitprobeert** (parameter changes, logic modifications)
2. **Fixed time budget per experiment** (bijv. 1 week paper trading)
3. **Evalueert op consistente metric** (bijv. Sharpe ratio in plaats van val_bPB)
4. **Houdt wat werkt, discardt wat niet** (git-based versioning)
5. **Continueert tot verbetering stopt** of menselijke interventie

### Analogie: autoresearch → Trading

| autoresearch (LLM) | MT5 Trading |
|-------------------|-------------|
| Model architecture | Trading strategy |
| Training loop (5 min) | Paper trading (1 week) |
| val_bPB metric | Sharpe ratio / Max DD |
| Git commits | Strategy versions |
| GPU memory | Trading capital |
| Experiment: test architecture | Experiment: test strategy |

---

## 📊 Research Dashboard

| Metric | Target | Current | Trend |
|--------|--------|---------|-------|
| Strategies Tested | 100+ | 0 | 🔄 |
| Best Sharpe Ratio | > 1.5 | - | - |
| Max Acceptable DD | < 15% | - | - |
| Paper Trading Weeks | 52 | 0 | ⬆️ |
| Live Trading Months | 6 | 0 | - |
| Autonomy Level | 90%+ | Manual | → |

**Experiment Progress:** `░░░░░░░░░░░░░░░░░░░░ 0/100 experiments`

---

## 🏗️ System Architecture

### Core: autoresearch Methodology

```
┌─────────────────────────────────────────────────────────────────┐
│                   AUTORESEARCH ENGINE                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  1. PLANNING (Auto-Claude)                              │   │
│  │     Agent proposes strategy variant                      │   │
│  │     - Parameter tweaks                                   │   │
│  │     - Logic modifications                                │   │
│  │     - Multi-strategy combinations                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  2. VALIDATION (decapod)                                 │   │
│  │     Safety checks before execution                       │   │
│  │     - Risk limits respected?                             │   │
│  │     - No dangerous logic?                                │   │
│  │     - Within experimental bounds?                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  3. EXPERIMENT (MT5 Paper Trading)                      │   │
│  │     Fixed time budget: 1 week                           │   │
│  │     - Historical backtest (vectorbt)                    │   │
│  │     - Forward test (paper trading)                      │   │
│  │     - Real-time data (QuantMuse)                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  4. EVALUATION                                          │   │
│  │     Calculate metrics                                   │   │
│  │     - Sharpe Ratio (primary)                            │   │
│  │     - Max Drawdown (safety)                             │   │
│  │     - Win Rate, Profit Factor                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  5. DECISION                                            │   │
│  │     Compare vs baseline                                 │   │
│  │     - Improved? → Keep & commit                         │   │
│  │     - Worse? → Discard                                   │   │
│  │     - Similar? → Note & continue                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  6. LEARNING (continuous-learning-skill)                │   │
│  │     Extract patterns from successful experiments        │   │
│  │     - What parameter ranges work?                       │   │
│  │     - What market conditions?                           │   │
│  │     - What combinations?                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                              ↓                                  │
│                       [REPEAT]                                │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Market Data (MT5)
    ↓
Feature Engine (QuantMuse)
    ↓
Strategy Template (modifiable)
    ↓
Backtest (vectorbt) ← Quick validation
    ↓
Paper Trading (MT5) ← Real test
    ↓
Performance Metrics
    ↓
Compare → Keep/Discard
    ↓
Knowledge Base (continuous-learning)
```

---

## 🔬 Active Research Questions

### Q1: Hoe vertalen we autoresearch naar trading?
**Status:** 🟡 In Progress | **Created:** 2026-03-14

**Challenge:**
- autoresearch traint LLM's in 5 min
- Trading heeft weken/maanden voor significante resultaten
- Hoe maken we dit praktisch?

**Current Approach:**
1. **Fase 1:** Snelle backtesting (vectorbt) → snelle feedback
2. **Fase 2:** Paper trading (MT5) → echte validatie
3. **Fase 3:** Live trading (klein) → uiteindelijke test

**Time Budgets:**
- Quick test: 1 uur (historische data)
- Paper test: 1 week (live demo)
- Live test: 1 maand (klein capital)

**Confidence:** 🔍 Medium | **Evidence:** Theoretisch sterk

---

### Q2: Wat is onze "val_bPB" equivalent?
**Status:** 🟡 In Progress | **Created:** 2026-03-14

**Original:** val_bPB = validation bits per byte (lager = beter)
**Challenge:** Trading heeft meerdere metrics, wat is primary?

**Proposed Metrics:**
```python
# Primary metric (like val_bPB)
def strategy_score(sharpe, max_dd, win_rate):
    # Normalized score (higher = better)
    score = sharpe * 0.5 + (1 - max_dd/100) * 0.3 + win_rate * 0.2
    return score

# Safety gates (must pass)
safety_checks = {
    'max_dd': 15,           # Max drawdown percentage
    'daily_var': 2,         # Daily value at risk
    'consecutive_losses': 5  # Max losing streak
}
```

**Decision:** Compound score met safety gates
**Confidence:** 🔍 Medium | **Needs:** Backtesting validatie

---

### Q3: Hoe genereren we strategy variants?
**Status:** 🟢 Planning | **Created:** 2026-03-14

**Approach Options:**

1. **Parameter Sweeps** (simpel)
   ```python
   # Grid search over parameter space
   param_space = {
       'fast_ema': [10, 12, 14, 16, 18],
       'slow_ema': [20, 24, 28, 32, 36],
       'rsi_period': [14, 21, 28]
   }
   ```

2. **Logic Modifications** (Auto-Claude)
   ```python
   # Agent suggests logic changes
   "What if we add volume confirmation?"
   "What if we only trade in London session?"
   ```

3. **Multi-Strategy Ensembles**
   ```python
   # Combine multiple strategies
   portfolio = Strategy([
       TrendFollowing(weight=0.4),
       MeanReversion(weight=0.3),
       Momentum(weight=0.3)
   ])
   ```

**Decision:** Start met (1), evolve to (2), experiment met (3)
**Confidence:** ✅ High

---

## 🧪 Hypothesis Tracker

### H1: Parameter Optimization > Random
**Status:** ⏳ Not Started | **Priority:** High

**Hypothesis:**
> Systematische parameter optimization presteert beter dan random search

**Test Design:**
```
Baseline: Random sampling of 100 parameter sets
Autoresearch: Guided search with learning

Metric: Best strategy_score after 100 iterations
```

**Expected Outcome:**
- Autoresearch vindt betere parameters in minder iteraties
- Learning from previous experiments guides search

**Acceptance Criteria:**
- [ ] Autoresearch score > Random score (p < 0.05)
- [ ] Convergeert in < 50 iteraties
- [ ] Robuust over verschillende market regimes

**Evidence Log:**
*No data yet*

**Verdict:** ⏳ Pending

---

### H2: Paper Trading voorspelt Live Performance
**Status:** ⏳ Not Started | **Priority:** Critical

**Hypothesis:**
> Paper trading metrics correleren met live trading (R > 0.7)

**Test Design:**
```
1. Top 10 strategies uit backtest
2. 1 maand paper trading
3. Correlatie paper vs live
4. Voorspellende waarde bepalen
```

**Rationale:**
- Paper trading gebruikt real data, geen real money
- Slippage/execution realistisch
- Psychologische factor ontbreekt (voordeel!)

**Risks:**
- Liquidity issues in live niet captured
- Platform risk verschilt
- Market impact groter met real size

**Acceptance Criteria:**
- [ ] Correlatie > 0.7 tussen paper/live Sharpe
- [ ] Max DD within 20% van voorspelling
- [ ] Win rate within 10% van voorspelling

**Evidence Log:**
*No data yet*

**Verdict:** ⏳ Critical - moet getest worden voor live

---

### H3: Multi-Strategy Ensemble > Single Strategy
**Status:** 📊 Design | **Priority:** Medium

**Hypothesis:**
> Gediversifieerde portfolio van strategieën is robuuster dan enkele beste

**Test Design:**
```
Single: Beste individuele strategie
Ensemble: Top 5 strategieën gewogen

Compare over 6 maanden:
- Sharpe ratio
- Max drawdown
- Consistency (maand-op-maand)
```

**Approach:**
```python
# Dynamic weighting based on recent performance
weights = recency_weighted_performance(strategies, lookback=4)
portfolio = WeightedEnsemble(strategies, weights)
```

**Expected Outcome:**
- Lagere drawdown door diversificatie
- Meer stabiele returns
- Meer werk om te onderhouden

**Acceptance Criteria:**
- [ ] Portfolio Sharpe > beste single Sharpe
- [ ] Portfolio Max DD < beste single Max DD
- [ ] Niet te complex (max 5 strategieën)

**Evidence Log:**
*No data yet*

**Verdict:** ⏳ Test na single strategy werkt

---

### H4: Regime Detection verbetert Performance
**Status:** 🔬 Research | **Priority:** Medium

**Hypothesis:**
> Strategie die adapt aan market regime presteert beter dan statische

**Test Design:**
```
Static: Eerst beste strategie, altijd aan
Adaptive: Regime detection, strategie wisselt

Regimes: Trending, Ranging, Volatile, Quiet
Detection: LLM news analysis + QuantMuse factors
```

**Implementation:**
```python
# Pseudo-code
regime = detect_regime(news, market_data)
if regime == 'trending':
    strategy = TrendFollowing()
elif regime == 'ranging':
    strategy = MeanReversion()
# etc.
```

**Expected Outcome:**
- Adaptive strategie heeft minder drawdowns
- Betere performance in regime transitions
- Meer complexiteit

**Acceptance Criteria:**
- [ ] Adaptive Sharpe > Static Sharpe
- [ ] Regime transitions handled gracefully
- [ ] False positive rate < 20%

**Evidence Log:**
*No data yet*

**Verdict:** ⏳ Nice-to-have, fase 2+

---

## 💡 Insights Log

### 2026-03-14

**🆕 autoresearch methodiek is direct toepasbaar**
```
5-min time budget → 1-week paper trading
val_bPB metric → strategy_score (compound)
Git commits → Strategy versions
AI modifies train.py → AI modifies strategy.py
```
**Impact:** Valideert onze aanpak
**Confidence:** ✅ High
**Action:** Implementeer exacte pattern

---

**🆕 MT5 heeft Python API!**
```python
import MetaTrader5 as mt5

# Real-time data
rates = mt5.copy_rates_from(symbol, timeframe, start, count)

# Order execution
mt5.order_send(order_request)

# Account info
account = mt5.account_info()
```
**Impact:** Maakt integratie veel makkelijker dan verwacht
**Confidence:** ✅ High (documentatie bekeken)
**Action:** Prioriteit: MT5 Python wrapper module

---

**🆕 vectorbt kan niet direct MT5 data gebruiken**
```
vectorbt verwijdert pandas DataFrame
MT5 geeft numpy arrays of propriëtair format

Need: Converter MT5 → pandas → vectorbt
```
**Impact:** Extra module nodig
**Confidence:** ✅ High
**Action:** Bouw MT5DataFetcher class

---

**🆕 Paper trading is live trading zonder risico**
```
MT5 demo accounts:
- Real data feeds
- Real execution
- Fake money
- PERFECT voor autoresearch!
```
**Impact:** Onze "1 week experiment" kan echt!
**Confidence:** ✅ High
**Action:** Open demo account als eerste stap

---

**🆕 QuantMuse heeft factor calculator**
```python
# data_service/factor_calculator.py
momentum, value, quality, size, volatility factors
```
**Impact:** Kan gebruiken voor regime detection
**Confidence:** ✅ High
**Action:** Integreer in phase 2

---

**🆕 decapod is essentieel voor safe autonomous trading**
```
Autonomous trading kan gevaarlijk zijn:
- Bugs kunnen veel geld kosten
- Risk limits moeten hard coded
- Kill switches moeten werken

decapod provides:
- Interlock: Hard policy boundaries
- Attestation: Verification of execution
- Advisory: Next action guidance
```
**Impact:** Critical - niet skippen
**Confidence:** ✅ High
**Action:** Implementeer decapod gates in phase 1

---

## 🚫 Dead Ends & Avoided Mistakes

### 2026-03-14

**❌ Gedachte: NinjaTrader als primaire platform**
**Problem:**
- Vereist volumetric data license ($$$)
- orderflowbot-warm is C# (minder portable)
- Minder flexibel dan Python ecosystem

**Lesson:** MT5 is betere start - gratis, Python API, forex focus
**Time Saved:** ~1 week platform eval + $$$ licenses
**Confidence:** ✅ High

---

**❌ Gedachte: Alles tegelijk bouwen**
**Problem:**
- Te complex voor vroege fase
- Moeilijk te debuggen
- Geen duidelijke baseline

**Lesson:** Start met 1 strategie, 1 currency pair
**Simplification Strategy:**
1. Phase 1: EMA crossover op EUR/USD
2. Phase 2: Meerdere strategieën
3. Phase 3: Meerdere pairs
4. Phase 4: Full automation

**Time Saved:** Weekjes van complexiteit
**Confidence:** ✅ High

---

**❌ Gedachte: Direct naar live trading**
**Problem:**
- Te veel risico
- Geen validation van systeem
- Fouten zijn duur

**Lesson:** Paper trading is niet optioneel
**Mandatory Gates:**
1. Backtest passed
2. Paper trading passed (4 weken min)
3. Small live test (1% capital)
4. Scale up gradual

**Money Saved:** Potentieel duizenden
**Confidence:** ✅ Critical

---

## 🔄 Decision Log

### Decision 001: MT5 als primaire platform
**Date:** 2026-03-14
**Context:** Moest kiezen tussen NinjaTrader, MT5, of custom

**Options:**
1. **NinjaTrader + orderflowbot**
   - ✅ Geavanceerde order flow analytics
   - ❌ Duur (volumetric license)
   - ❌ C# ecosystem (minder flexibiliteit)
   - ❌ Steilere leercurve

2. **MT5 (MetaTrader 5)**
   - ✅ Gratis (demo accounts)
   - ✅ Python API (MetaTrader5 package)
   - ✅ Industriestandaard voor forex
   - ✅ Direct broker integratie
   - ❌ Minder geavanceerd dan NinjaTrader

3. **Custom oplossing**
   - ✅ Volledige controle
   - ❌ Maanden development tijd
   - ❌ Broker integratie complex

**Decision:** **MT5**

**Rationale:**
- Snelste time-to-market
- Past bij Python ecosystem (autoresearch, QuantMuse, etc.)
- Gratis demo accounts perfect voor autoresearch
- Industriestandaard = betere documentatie/community

**Confidence:** ✅ High
**Reversibility:** Medium (code is Python dus portbaar)

---

### Decision 002: EMA Crossover als eerste strategie
**Date:** 2026-03-14
**Context:** Eerste strategie kiezen voor baseline

**Options:**
1. **EMA Crossover** (simpel, trend-following)
2. **RSI Mean Reversion** (simpel, counter-trend)
3. **Multi-factor** (complex, QuantMuse style)
4. **ML-based** (complex, autoresearch style)

**Decision:** **EMA Crossover**

**Rationale:**
- Simpel = makkelijk te debuggen
- Trend-following = werkt in duidelijke markten
- Veel documentatie beschikbaar
- Goede baseline voor complexere strategieën
- VectorBT heeft dit built-in

**Parameters:**
```python
fast_ema = 12  # Standard
slow_ema = 26  # Standard
signal_ema = 9 # Optional
```

**Confidence:** ✅ High
**Next Evolution:** Add RSI filter, then multi-factor

---

### Decision 003: EUR/USD als eerste currency pair
**Date:** 2026-03-14
**Context:** Welke markt om mee te beginnen?

**Options:**
1. **EUR/USD** (major, liquid, low spread)
2. **GBP/USD** (major, volatile)
3. **USD/JPY** (major, Asian session)
4. **XAU/USD** (Gold, volatile)
5. **BTC/USD** (Crypto, 24/7)

**Decision:** **EUR/USD**

**Rationale:**
- Meest liquid pair (goed voor execution)
- Lage spreads (lagere kosten)
- 24/5 trading (goed voor data collection)
- Veel historische data beschikbaar
- Standard benchmark in industry

**Future:** Expand naar GBP/USD, USD/JPY in phase 2

**Confidence:** ✅ High

---

### Decision 004: 1-week paper trading experiments
**Date:** 2026-03-14
**Context:** Autoresearch gebruikt 5-minuten time budget, wat voor trading?

**Options:**
1. **1 dag** (te kort, noise)
2. **1 week** (balans)
3. **1 maand** (standaard, maar traag)
4. **3 maanden** (te traag voor rapid iteration)

**Decision:** **1 week**

**Rationale:**
- Genoeg trades voor statistische significantie (~100+ trades)
- Snel genoeg voor rapid iteration
- Dekt verschillende market conditions
- Manageable risk exposure

**Compromise:**
- Quick test: 1 dag historische data (vectorbt)
- Full test: 1 week paper trading (MT5 demo)
- Final test: 1 maand live (klein capital)

**Confidence:** ✅ Medium-High
**Validation:** Required na eerste experiments

---

### Decision 005: Compound metric als primary score
**Date:** 2026-03-14
**Context:** autoresearch gebruikt val_bPB (1 metric), wij hebben meerdere

**Options:**
1. **Sharpe Ratio only** (standard, but incomplete)
2. **Max Drawdown only** (risk-focused, ignores reward)
3. **Profit Factor only** (too simple)
4. **Compound Score** (balanced)

**Decision:** **Compound Score = Sharpe * 0.5 + (1-DD/100) * 0.3 + WinRate * 0.2**

**Rationale:**
- Sharpe ratio is risk-adjusted return (primary)
- Max drawdown is critical for survival (safety)
- Win rate indicates consistency (stability)
- Weights reflect priorities (return > safety > consistency)

**Safety Gates (must pass separately):**
```python
if max_dd > 15: FAIL
if daily_var > 2: FAIL
if consecutive_losses > 5: FAIL
```

**Confidence:** ✅ Medium (needs backtesting validation)

---

## 📚 Knowledge Graph (Growth Tracker)

```
Discoveries (What we know):
├─ MT5 Python API werkt goed ──────────────→ Direct integration
├─ vectorbt needs pandas conversion ───────→ Build MT5DataFetcher
├─ Paper trading = perfect test environment → No risk experimentation
├─ decapod gates essential for safety ──────→ Implement early
├─ QuantMuse factors usable for regimes ───→ Phase 2 integration
└─ EMA crossover good baseline ────────────→ Start simple

Patterns (What works):
├─ Start simple, iterate fast ─────────────→ 1 pair, 1 strategy
├─ Paper trading before live ───────────────→ Mandatory gate
├─ Compound metrics > single metrics ───────→ Balanced score
└─ Safety gates separate from optimization → Hard limits

Integrations (How things connect):
├─ MT5 ←→ MT5DataFetcher ←→ vectorbt ──────→ Backtest pipeline
├─ Auto-Claude → Strategy Generator ───────→ Agent proposes variants
├─ decapod → Safety Validator ──────────────→ Gates before execution
├─ QuantMuse → Regime Detector ─────────────→ Market state
└─ continuous-learning → Pattern Extractor → Knowledge base

Open Questions (What we don't know):
├─ What is optimal paper trading duration? ─→ 1 week hypothesis
├─ How many strategies in ensemble? ─────────→ Start with 1
├─ What metric weights are optimal? ──────────→ 50/30/20 hypothesis
└─ How to detect regime changes reliably? ───→ Phase 2 research
```

---

## 🎯 Current Sprint

### Sprint 0: Foundation & Setup
**Started:** 2026-03-14 | **End:** 2026-03-28
**Goal:** Volledig werkende autoresearch loop met 1 strategie

#### Todo
- [ ] **Environment setup**
  - [ ] Python 3.12 environment
  - [ ] MT5 terminal geïnstalleerd
  - [ ] Demo account geopend
  - [ ] MetaTrader5 Python package
  - [ ] vectorbt geïnstalleerd

- [ ] **Data Pipeline**
  - [ ] MT5DataFetcher class (MT5 → pandas)
  - [ ] Historical data export (1 jaar EUR/USD)
  - [ ] Real-time data stream working

- [ ] **Baseline Strategy**
  - [ ] EMA Crossover implementation
  - [ ] vectorbt backtest working
  - [ ] Calculate baseline metrics

- [ ] **Auto-Claude Integration**
  - [ ] Agent configuratie voor strategy generation
  - [ ] First parameter suggestion

#### In Progress
- [🔄] Research documentation (this file)

#### Done This Sprint
- [x] Repositories geanalyseerd
- [x] Componenten in kaart gebracht
- [x] System architecture ontworpen
- [x] Baseline strategie gekozen (EMA crossover)

#### Blockers
- ⚠️ MT5 demo account nog niet geopend
- ⚠️ Historical data nog niet geëxporteerd

---

## 📈 Experiment Tracker

### Planned Experiments (Phase 1)

| ID | Strategy Variant | Status | Sharpe | Max DD | Notes |
|----|------------------|--------|--------|--------|-------|
| E001 | Baseline EMA(12,26) | ⏳ Planned | - | - | First baseline |
| E002 | EMA(10,20) faster | ⏳ Planned | - | - | Quick reaction |
| E003 | EMA(16,32) slower | ⏳ Planned | - | - | Reduce noise |
| E004 | EMA(12,26) + RSI filter | ⏳ Planned | - | - | Add confirmation |
| E005 | EMA(12,26) + Volume filter | ⏳ Planned | - | - | Confirmation |
| E006 | EMA(12,26) + Session filter | ⏳ Planned | - | - | London only |
| E007 | EMA(12,26) + Volatility filter | ⏳ Planned | - | - | ATR based |
| E008 | EMA(12,26) + Trend filter | ⏳ Planned | - | - | ADX based |
| E009 | Dual EMA crossover | ⏳ Planned | - | - | Two systems |
| E010 | Triple EMA crossover | ⏳ Planned | - | - | Three EMAs |

*More experiments will be generated by Auto-Claude agent*

### Experiment Template

```markdown
## Experiment E###: [Description]

**Date:** YYYY-MM-DD
**Strategy:** [Name]
**Parameters:** [JSON]
**Duration:** [Weeks]

### Hypothesis
[What we expect and why]

### Results
- Sharpe Ratio: X.XX
- Max Drawdown: XX%
- Win Rate: XX%
- Profit Factor: X.XX
- Total Trades: XXX

### Comparison vs Baseline
- Sharpe: [↔/↗/↘] (±X.XX)
- Max DD: [↔/↗/↘] (±X%)
- Verdict: [KEEP/DISCARD/STUDY]

### Notes
[Interesting observations, bugs, etc.]

### Git Commit
[Commit hash for this version]
```

---

## 🔮 Looking Ahead

### Phase 1: Foundation (Week 1-4)
**Focus:** Single strategy, single pair, working loop

- [ ] MT5 integration working
- [ ] Baseline EMA strategy backtested
- [ ] First 10 experiments completed
- [ ] Auto-Claude generating suggestions
- [ ] decapod safety gates active

**Milestone:** Fully autonomous experiment loop running

---

### Phase 2: Optimization (Week 5-8)
**Focus:** Parameter optimization, strategy improvements

- [ ] 100+ experiments completed
- [ ] Best strategy identified
- [ ] Paper trading validation (4 weken)
- [ ] continuous-learning extracting patterns

**Milestone:** Strategy beats baseline significantly

---

### Phase 3: Expansion (Week 9-12)
**Focus:** Multiple strategies, multiple pairs

- [ ] Add RSI strategy
- [ ] Add Mean Reversion strategy
- [ ] Expand to GBP/USD, USD/JPY
- [ ] Ensemble research

**Milestone:** Diversified portfolio of strategies

---

### Phase 4: Live Trading (Week 13+)
**Focus:** Small live test, scale up gradually

- [ ] Live account setup (small capital)
- [ ] 1 month live test
- [ ] Performance comparison paper vs live
- [ ] Scale up if successful

**Milestone:** Profitable live trading

---

## ⚠️ Risks & Mitigations

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| MT5 API issues | Medium | High | Robust error handling, fallbacks |
| Data quality | Low | High | Validation checks, multiple sources |
| System failures | Low | Severe | Redundancy, circuit breakers |
| Auto-Claude stability | Medium | Medium | Human oversight, manual override |

### Trading Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Strategy failure | Medium | Medium | Paper trading mandatory |
| Market crash | Low | Severe | Hard position limits |
| Overfitting | High | High | Out-of-sample testing |
| Black swan | Low | Severe | Diversification, stop-loss |

### AI Safety Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Unintended trades | Low | Severe | decapod interlock gates |
| Runaway loop | Low | Medium | Time budgets, kill switches |
| Poor decisions | Medium | High | Human-in-the-loop phase 1 |

---

## 📝 Notes to Future Me

### Why Are You Doing This?
> "Je wilt een systeem bouwen dat trading strategieën continu verbetert zonder menselijke tussenkomst. Niet om rijk te worden overnight, maar om te leren hoe AI autonomous research kan toepassen op echte problemen."

### Key Principles
1. **Safety first** - Geen experiment dat kapitaal kan verbranden
2. **Start simple** - EMA crossover is genoeg om te beginnen
3. **Measure everything** - Als je het niet meet, kun je het niet verbeteren
4. **Document decisions** - Je toekomstige self wil weten waarom

### If You're Stuck
- Terug naar basics: Werkt de data pipeline?
- Check assumptions: Is je hypothese valide?
- Simplify: Wat is het minimum dat moet werken?
- Ask for help: De repositories hebben communities

### Success Indicators
Je bent op de goede track als:
- [ ] Elke week levert nieuwe data op
- [ ] Elke experiment leert je iets
- [ ] Je code wordt simpeler, niet complexer
- [ ] Je bent niet bang om dingen te breken (demo account!)

### Final Reminder
> "Dit is een marathon, geen sprint. De eerste 4 weken zijn om het systeem te laten werken, niet om winst te maken. Als je na 3 maanden een beter systeem hebt dan vandaag, win je."

— *Past You, 2026-03-14*

---

## 🗂️ Related Documents

- [docs/SAMENVATTING.md](./docs/SAMENVATTING.md) - Repository overzicht
- [docs/ARCHITECTUUR.md](./docs/ARCHITECTUUR.md) - Integratie details
- [docs/COMPONENTEN.md](./docs/COMPONENTEN.md) - Herbruikbare modules
- [docs/DEPENDENCIES.md](./docs/DEPENDENCIES.md) - Installatie gids
- [autoresearch/README.md](./autoresearch/README.md) - Original research paper
- [autoresearch/train.py](./autoresearch/train.py) - Reference implementation

---

## 📊 Quick Reference

### Key Commands (When Built)
```bash
# Start autoresearch loop
python autotrader.py --experiment --duration 1week

# Check experiment status
python autotrader.py --status

# View results
python autotrader.py --results --top 10

# Deploy to paper trading
python autotrader.py --deploy --mode paper

# Emergency stop
python autotrader.py --stop --all
```

### Key Files (To Be Created)
```
├── autotrader.py          # Main entry point
├── strategy/              # Strategy implementations
│   ├── base.py           # Base class
│   ├── ema_crossover.py  # EMA strategy
│   └── variants/         # Auto-generated variants
├── data/                  # Data pipeline
│   ├── mt5_fetcher.py    # MT5 integration
│   └── converter.py      # MT5 → pandas
├── backtest/              # Backtesting engine
│   └── vectorbt_engine.py
├── evaluate/              # Metrics and scoring
│   └── metrics.py
├── safety/                # Risk management
│   └── gates.py          # decapod integration
└── experiments/           # Experiment results
    └── results.tsv
```

---

**🚀 Next Update: After first MT5 connection is established**

---

*End of Research Log*
