# Herbruikbare Componenten Per Repository

## Overzicht

Dit document beschrijft de herbruikbare componenten uit elke repository die ingezet kunnen worden in nieuwe projecten.

---

## 1. autoresearch - Herbruikbare Componenten

### 1.1 Evaluatie Framework
**Locatie:** `prepare.py`

**Beschrijving:** Gestandaardiseerde evaluatie metric voor LLM modellen

**Componenten:**
```python
evaluate_bpb(model, val_loader)  # Returns validation bits per byte
```

**Herbruikbaarheid:**
- Model-agnostische evaluatie
- Kan aangepast worden voor andere taken (classification, generation)
- Consistente metriek voor A/B testing

### 1.2 Hybrid Optimizer
**Locatie:** `train.py`

**Beschrijving:** Muon + AdamW hybrid optimizer voor verschillende parameter types

**Componenten:**
```python
# Matrix parameters → Muon optimizer
# Embedding/scalars → AdamW optimizer
```

**Herbruikbaarheid:**
- Efficiënt voor grote transformers
- Combineert snelheid van Muon met stabiliteit van AdamW
- Momentum scheduling en weight decay aanpasbaar

### 1.3 Flash Attention Integration
**Locatie:** `train.py`

**Beschrijving:** Dynamische kernel selectie voor efficiënte attention

**Componenten:**
```python
# Automatic fallback: Flash Attention 3 → xFormers → SDPA
```

**Herbruikbaarheid:**
- GPU capability detection
- Multi-backend support
- Drop-in replacement voor standard attention

### 1.4 Memory Management
**Locatie:** `train.py`

**Beschrijving:** GC optimalisatie strategies

**Componenten:**
```python
# Proactive GC before critical sections
# VRAM monitoring system
```

**Herbruikbaarheid:**
- Voorkomt memory stalls tijdens training
- Configurbaar garbage collection
- Memory profiling utilities

### 1.5 Experiment Tracking
**Locatie:** `analysis.ipynb`

**Beschrijving:** TSV-based logging met git integratie

**Componenten:**
```python
# results.tsv format: timestamp, val_bpb, description, status
# Git commits per experiment
```

**Herbruikbaarheid:**
- Simpele, database-vrije logging
- Version controlled experimenten
- Success/failure tracking

### 1.6 Fixed-Budget Training Loop
**Locatie:** `train.py`

**Beschrijving:** Tijd-gebaseerde training termination

**Componenten:**
```python
# Exact 5-minute time budget
# Progress tracking met remaining time
```

**Herbruikbaarheid:**
- Fair comparison tussen architecturen
- Reproducible time budgets
- Clean shutdown mechanism

---

## 2. Auto-Claude - Herbruikbare Componenten

### 2.1 Multi-Agent Framework
**Locatie:** `apps/backend/agents/`

**Beschrijving:** Modulair agent systeem met gespecialiseerde rollen

**Componenten:**
```python
# PlannerAgent  - Creates subtask-based plans
# CoderAgent    - Implements individual subtasks
# QAReviewerAgent - Validates acceptance criteria
# QAFixerAgent  - Resolves issues iteratively
```

**Herbruikbaarheid:**
- Role-based agent permissions
- Spawn subagents capability
- Parallel execution support

### 2.2 Graphiti Memory System
**Locatie:** `apps/backend/integrations/`

**Beschrijving:** Graph database voor cross-session context

**Componenten:**
```python
# Semantic search across sessions
# Session insights extraction
# Multi-provider support (OpenAI, Anthropic, Ollama)
```

**Herbruikbaarheid:**
- Persistente knowledge base
- Relationship detection
- Context retrieval by similarity

### 2.3 Spec Creation Pipeline
**Locatie:** `apps/backend/spec_agents/`

**Beschrijving:** Dynamische fases pipeline (3-8 fases)

**Componenten:**
```python
# SIMPLE: Discovery → Quick Spec → Validate
# STANDARD: Discovery → Requirements → [Research] → Context → Spec → Plan → Validate
# COMPLEX: Full pipeline + Research + Self-Critique
```

**Herbruikbaarheid:**
- Complexity-based routing
- Modular phase system
- Customizable pipelines

### 2.4 Git Worktree Isolation
**Locatie:** `apps/backend/core/`

**Beschrijving:** Veilige feature development met isolatie

**Componenten:**
```python
# Create isolated worktrees
# Auto-merge with AI conflict resolution
# Workspace cleanup
```

**Herbruikbaarheid:**
- Non-destructive branching
- Parallel feature development
- Safe experimentation

### 2.5 Security Model
**Locatie:** `apps/backend/core/`

**Beschrijving:** Drie-laags beveiliging

**Componenten:**
```python
# OS sandbox isolation
# File restriction system
# Command allowlisting based on stack
```

**Herbruikbaarheid:**
- Project-aware security
- Dynamic permission system
- Audit logging

---

## 3. Scrapling - Herbruikbare Componenten

### 3.1 Adaptive Parser
**Locatie:** `scrapling/parser.py`

**Beschrijving:** HTML parser met automatische element relocatie

**Componenten:**
```python
# CSS selectors, XPath, text search
# Similarity-based element finding
# Auto selector generation
```

**Herbruikbaarheid:**
- Handles website structure changes
- Multiple selection methods
- Robust element tracking

### 3.2 Fetcher Classes
**Locatie:** `scrapling/fetchers/`

**Beschrijving:** Drie fetcher types voor verschillende use cases

**Componenten:**
```python
Fetcher()           # Fast HTTP with TLS impersonation
DynamicFetcher()    # Browser automation with Playwright
StealthyFetcher()   # Anti-bot bypass mode
```

**Herbruikbaarheid:**
- Simple API voor alle types
- Session management
- State persistence

### 3.3 Spider Framework
**Locatie:** `scrapling/spiders/`

**Beschrijving:** Scrapy-achtig crawling framework

**Componenten:**
```python
# Concurrent crawling met throttling
# Pause & resume met checkpoints
# Multi-session support
# Streaming mode
```

**Herbruikbaarheid:**
- Familiar Scrapy API
- Async parse callbacks
- Built-in export (JSON/JSONL)

### 3.4 Anti-Bot Bypass
**Locatie:** `scrapling/engines/`

**Beschrijving:** Cloudflare Turnstile en andere bypasses

**Componenten:**
```python
# Fingerprint spoofing
# Proxy rotation
# Browser automation stealth
```

**Herbruikbaarheid:**
- Bypass common protections
- Custom rotation strategies
- Headless browser support

### 3.5 MCP Server
**Locatie:** `scrapling/core/`

**Beschrijving:** AI integration server

**Componenten:**
```python
# Intelligent data extraction
# AI-assisted scraping
# Context-aware parsing
```

**Herbruikbaarheid:**
- LLM integration
- Structured output
- Semantic understanding

---

## 4. vectorbt-backtesting-skills - Herbruikbare Componenten

### 4.1 Strategy Library
**Locatie:** `backtesting/`

**Beschrijving:** 8 pre-built trading strategies

**Componenten:**
```python
# EMA Crossover, RSI, Donchian Channel
# Supertrend, MACD Breakout, SDA2 Trend
# Momentum, Dual Momentum
```

**Herbruikbaarheid:**
- Ready-to-use strategies
- Configurable parameters
- Multi-asset support

### 4.2 Data Fetcher
**Locatie:** Integration met OpenAlgo

**Beschrijving:** Indiase markt data source

**Componenten:**
```python
# NSE, BSE, NFO (futures), MCX commodities
# Historical data met flexible ranges
# Multiple timeframes (1m, 5m, 15m, 1h, D)
```

**Herbruikbaarheid:**
- API integration patterns
- Authentication handling
- Data alignment utilities

### 4.3 Signal Processing
**Locatie:** Strategy implementations

**Beschrijving:** Signal cleaning en generation

**Componenten:**
```python
# ta.exrem() for duplicate removal
# Multiple timeframe support
# Proper indexing
```

**Herbruikbaarheid:**
- Clean signal generation
- Timeframe flexibility
- Missing data handling

### 4.4 Portfolio Simulation
**Locatie:** VectorBT integration

**Beschrijving:** Complete portfolio backtesting

**Componenten:**
```python
# vbt.Portfolio.from_signals()
# Percent-based sizing (equities)
# Lot-size aware (futures)
```

**Herbruikbaarheid:**
- Realistic simulation
- Multiple sizing approaches
- Comprehensive metrics

### 4.5 Visualization
**Locatie:** Plotly charts

**Beschrijving:** Interactive performance charts

**Componenten:**
```python
# Portfolio value curves
# Underwater plots (drawdown)
# Cumulative returns
```

**Herbruikbaarheid:**
- Dark theme styling
- Export capabilities
- Interactive exploration

---

## 5. decapod - Herbruikbare Componenten

### 5.1 Constitution System
**Locatie:** `constitution/`

**Beschrijving:** Embedded contracts en documentation

**Componenten:**
```yaml
# DECAPOD.md - Core contracts
# INTERFACES.md - API specifications
# ALGORITHMS.md - Design patterns
```

**Herbruikbaarheid:**
- Rust-embed for embedded files
- Version-controlled policies
- Multi-format support

### 5.2 Assurance Framework
**Locatie:** `src/core/`

**Beschrijving:** Drie uitkomsten model

**Componenten:**
```rust
// Advisory - Clear next actions
// Interlock - Hard policy boundaries
// Attestation - Structured proof
```

**Herbruikbaarheid:**
- Policy enforcement
- Verification gates
- Audit trails

### 5.3 Plugin System
**Locatie:** `src/plugins/`

**Beschrijving:** Uitbreidbare plugins

**Componenten:**
```rust
// todo, eval, health, knowledge
// Custom plugin development
```

**Herbruikbaarheid:**
- Modular architecture
- Extensible design
- Isolated plugins

### 5.4 Context Capsules
**Locatie:** `src/core/`

**Beschrijving:** Deterministic scoped context

**Componenten:**
```rust
// Scoped context returns
// Deterministic behavior
// Reproducible results
```

**Herbruikbaarheid:**
- Predictable context
- Scoped operations
- Testable components

---

## 6. claude-code-continuous-learning-skill - Herbruikbare Componenten

### 6.1 Skill Template
**Locatie:** `resources/skill-template.md`

**Beschrijving:** Comprehensive template voor skill creatie

**Componenten:**
```yaml
---
name: kebab-case-name
description: Precise with trigger conditions
author: Claude Code
version: 1.0.0
date: YYYY-MM-DD
---
```

**Herbruikbaarheid:**
- Standardized format
- YAML frontmatter
- Clear structure

### 6.2 Quality Gates
**Locatie:** Core system

**Beschrijving:** Vier criteria voor skill creatie

**Componenten:**
```python
# Reusable - Helps future tasks
# Non-trivial - Requires discovery
# Specific - Clear triggers
# Verified - Tested solution
```

**Herbruikbaarheid:**
- Prevents over-extraction
- Ensures quality
- Maintains standards

### 6.3 Activation Hook
**Locatie:** `scripts/continuous-learning-activator.sh`

**Beschrijving:** Automatische evaluatie trigger

**Componenten:**
```bash
# Runs on every prompt
# Guides evaluation process
# Ensures no knowledge loss
```

**Herbruikbaarheid:**
- Bash scripting pattern
- Hook integration
- User reminders

### 6.4 Research Integration
**Locatie:** `resources/research-references.md`

**Beschrijving:** Academic foundation

**Componenten:**
```python
# Voyager (2023) - Skill libraries
# CASCADE (2024) - Meta-skills
# SEAgent (2025) - Trial and error
# Reflexion (2023) - Self-reflection
```

**Herbruikbaarheid:**
- Research-backed approach
- Citations and references
- Theoretical foundation

---

## 7. QuantMuse - Herbruikbare Componenten

### 7.1 Data Fetchers
**Locatie:** `data_service/`

**Beschrijving:** Multi-source data integration

**Componenten:**
```python
# binance_fetcher.py - Crypto data
# yahoo_fetcher.py - Stock data
# alpha_vantage_fetcher.py - Financial data + news
```

**Herbruikbaarheid:**
- WebSocket connections
- REST API patterns
- Real-time streaming

### 7.2 Factor Calculator
**Locatie:** `data_service/factor_calculator.py`

**Beschrijving:** Multi-factor analysis

**Componenten:**
```python
# Momentum factors (20d, 60d, 252d returns)
# Value factors (P/E, P/B, P/S, dividend yield)
# Quality factors (ROE, ROA, debt ratios)
# Size and volatility factors
```

**Herbruikbaarheid:**
- Standardized factors
- Configurable periods
- Multi-asset support

### 7.3 Strategy Framework
**Locatie:** `data_service/builtin_strategies.py`

**Beschrijving:** 8+ built-in strategies

**Componenten:**
```python
# Momentum, Value, Quality Growth
# Multi-Factor, Mean Reversion
# Low Volatility, Sector Rotation
# Risk Parity
```

**Herbruikbaarheid:**
- Modular strategy design
- Composable factors
- Backtesting integration

### 7.4 LLM Integration
**Locatie:** `data_service/llm_integration.py`

**Beschrijving:** OpenAI GPT integration

**Componenten:**
```python
# Market trend analysis
# Trading signal generation
# Risk assessment
# Portfolio optimization suggestions
```

**Herbruikbaarheid:**
- GPT-4 API patterns
- Prompt engineering
- Structured output

### 7.5 Sentiment Analyzer
**Locatie:** `data_service/sentiment_analyzer.py`

**Beschrijving:** Market sentiment scoring

**Componenten:**
```python
# News article processing
# Social media monitoring
# Sentiment factor generation
```

**Herbruikbaarheid:**
- Text preprocessing
- Sentiment scoring
- Factor conversion

### 7.6 Risk Management
**Locatie:** `data_service/` (various)

**Beschrijving:** Comprehensive risk tools

**Componenten:**
```python
# VaR and CVaR calculations
# Position sizing algorithms
# Drawdown monitoring
# Leverage limits
```

**Herbruikbaarheid:**
- Standard risk metrics
- Real-time monitoring
- Alert systems

### 7.7 Web Interface
**Locatie:** `data_service/api_server.py`, `dashboard.py`

**Beschrijving:** FastAPI + Streamlit

**Componenten:**
```python
# REST API server
# Interactive dashboard
# Strategy management UI
# Real-time visualization
```

**Herbruikbaarheid:**
- FastAPI patterns
- Streamlit components
- WebSocket support
- Plotly integration

---

## 8. orderflowbot-warm - Herbruikbare Componenten

### 8.1 Order Flow Data Structures
**Locatie:** `NinjaTrader/AddOns/OrderFlowBot/Models/DataBars/`

**Beschrijving:** Volumetric data modellen

**Componenten:**
```csharp
// Cumulative Delta Bars
// Volume at Price
// Value Areas, Point of Control
// Imbalances, Stacked Imbalances
```

**Herbruikbaarheid:**
- Standardized order flow data
- Bid/Ask volume tracking
- Delta calculations

### 8.2 Strategy Framework
**Locatie:** `NinjaTrader/AddOns/OrderFlowBot/Models/Strategies/`

**Beschrijving:** Extensible strategy system

**Componenten:**
```csharp
// StrategyBase - Base class for custom strategies
// StackedImbalances - Example implementation
// Custom strategy development
```

**Herbruikbaarheid:**
- Inheritance-based design
- Configuration-driven
- Alert system integration

### 8.3 Event System
**Locatie:** `NinjaTrader/AddOns/OrderFlowBot/Events/`

**Beschrijving:** Event-driven architecture

**Componenten:**
```csharp
// Trading events
// Messaging system
// Strategy events
```

**Herbruikbaarheid:**
- Decoupled components
- Async event handling
- Extensible events

### 8.4 Dependency Injection
**Locatie:** `NinjaTrader/AddOns/OrderFlowBot/Containers/`

**Beschrijving:** Service container pattern

**Componenten:**
```csharp
// Service resolution
// Event container
// Configuration injection
```

**Herbruikbaarheid:**
- Testable design
- Modular services
- Configuration management

### 8.5 Configuration System
**Locatie:** `NinjaTrader/AddOns/OrderFlowBot/Configs/`

**Beschrijving:** JSON-based configuration

**Componenten:**
```csharp
// Bar classification
// Data bar settings
// Trading settings
```

**Herbruikbaarheid:**
- JSON serialization
- Type-safe configuration
- Validation

---

## Cross-Repository Component Synergies

### Data Pipeline
```
Scrapling (Web Scraping)
    ↓
QuantMuse Data Fetchers (Normalization)
    ↓
autoresearch Data Loader (Preparation)
    ↓
VectorBT (Backtesting)
```

### AI/ML Pipeline
```
Auto-Claude (Agent Orchestration)
    ↓
decapod (Control & Safety)
    ↓
autoresearch (Training Loop)
    ↓
continuous-learning-skill (Knowledge Retention)
```

### Trading Pipeline
```
QuantMuse (Strategy Generation)
    ↓
vectorbt-backtesting-skills (Validation)
    ↓
orderflowbot-warm (Execution)
```

---

## Aanbevolen Startpunten

### Voor Trading Development
1. Start met **vectorbt-backtesting-skills** voor strategie validatie
2. Integreer **QuantMuse** data fetchers voor real-time data
3. Gebruik **orderflowbot-warm** patterns voor execution

### Voor AI Automation
1. Gebruik **Auto-Claude** framework voor agent orkestratie
2. Integreer **decapod** voor safety en control
3. Activeer **continuous-learning-skill** voor knowledge retention

### Voor Data Projects
1. Gebruik **Scrapling** voor web data acquisitie
2. Pas **autoresearch** training loop patterns toe
3. Integreer met **QuantMuse** voor verwerking en analyse

---

**Documentatie versie:** 1.0.0
**Laatste update:** 2026-03-14
