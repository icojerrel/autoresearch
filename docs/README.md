# Project Documentatie Index

## Welkom

Deze map bevat uitgebreide documentatie over de acht gekloonde repositories van icojerrel. Deze repositories vormen samen een krachtige toolkit voor AI-gestuurde ontwikkeling, quantitative trading en data scraping.

---

## Documentatie Overzicht

### 📋 [SAMENVATTING.md](./SAMENVATTING.md)
**Algemeen overzicht van alle repositories**

Bevat:
- Quick reference tabel
- Per repository detail (doel, technologie, functionaliteit)
- Synergieën tussen repositories
- Aanbevolen volgende stappen

**Lees dit eerst** voor een compleet begrip van alle beschikbare tools.

---

### 🧩 [COMPONENTEN.md](./COMPONENTEN.md)
**Herbruikbare componenten per repository**

Bevat:
- Gedetailleerde beschrijving van herbruikbare componenten
- Code voorbeelden en API's
- Cross-repository synergieën
- Aanbevolen startpunten per use case

**Lees dit** wanneer je specifieke componenten wilt hergebruiken in je project.

---

### 🏗️ [ARCHITECTUUR.md](./ARCHITECTUUR.md)
**Integratie architectuur en use cases**

Bevat:
- High-level architectuur diagrammen
- Vier complete use cases met data flows
- API contracten en communicatie protocollen
- Deployment modellen
- Security consideraties

**Lees dit** wanneer je begrijpt hoe alles samenwerkt.

---

### 📦 [DEPENDENCIES.md](./DEPENDENCIES.md)
**Installatie instructies en requirements**

Bevat:
- Systeem requirements per repository
- Gedetailleerde installatie stappen
- API keys en configuratie
- Probleemoplossing
- Performance optimalisatie

**Lees dit** wanneer je klaar bent om te installeren.

---

## Snelle Start Gids

### 1. Begin Hier
```
1. Lees SAMENVATTING.md → Begrip van alle tools
2. Lees ARCHITECTUUR.md → Begrip van integraties
3. Lees DEPENDENCIES.md → Installatie stappen
```

### 2. Per Use Case

#### Trading Strategy Development
```
1. SAMENVATTING.md → #4, #7, #8 (vectorbt, QuantMuse, orderflowbot)
2. COMPONENTEN.md → Trading Pipeline sectie
3. ARCHITECTUUR.md → Use Case 1
4. DEPENDENCIES.md → Installatie van trading components
```

#### AI Automation
```
1. SAMENVATTING.md → #2, #5, #6 (Auto-Claude, decapod, continuous-learning)
2. COMPONENTEN.md → AI/ML Pipeline sectie
3. ARCHITECTUUR.md → Use Case 2
4. DEPENDENCIES.md → Installatie van AI components
```

#### Data Scraping & Processing
```
1. SAMENVATTING.md → #3 (Scrapling)
2. COMPONENTEN.md → Data Pipeline sectie
3. ARCHITECTUUR.md → Use Case 3
4. DEPENDENCIES.md → Scrapling installatie
```

---

## Repository Map

| # | Repo | Type | Primary Use |
|---|------|------|-------------|
| 1 | [autoresearch](../) | ML Research | Autonome LLM optimalisatie |
| 2 | [Auto-Claude](../Auto-Claude/) | AI Framework | Multi-agent ontwikkeling |
| 3 | [Scrapling](../Scrapling/) | Web Scraping | Adaptive data extraction |
| 4 | [vectorbt-backtesting-skills](../vectorbt-backtesting-skills/) | Trading | Strategy backtesting |
| 5 | [decapod](../decapod/) | Control Plane | AI agent safety |
| 6 | [claude-code-continuous-learning-skill](../claude-code-continuous-learning-skill/) | Knowledge | Persistente learning |
| 7 | [QuantMuse](../QuantMuse/) | Trading | Quantitative platform |
| 8 | [orderflowbot-warm](../orderflowbot-warm/) | Trading | Order flow execution |

---

## Systeem Architectuur Visueel

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONTROL & ORCHESTRATION                       │
│                                                                   │
│    Auto-Claude (Agents) ←→ decapod (Safety) ←→ Learning         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        DATA & PROCESSING                        │
│                                                                   │
│    Scrapling (Web) → QuantMuse (Market) → autoresearch (ML)     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                         EXECUTION                               │
│                                                                   │
│    vectorbt (Backtest) → orderflowbot (Live Trading)            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Belangrijkste Concepten

### 1. Autonomous Development
**Auto-Claude + decapod** stelt AI agents in staat om:
- Features te plannen en implementeren
- Code te schrijven en te testen
- Veilige boundaries te respecteren

### 2. Continuous Learning
**continuous-learning-skill** zorgt voor:
- Persistente kennis across sessies
- Automatische extractie van patterns
- Verbetering over tijd

### 3. Trading Pipeline
**QuantMuse + vectorbt + orderflowbot** biedt:
- Data acquisitie en analyse
- Strategy backtesting
- Live trade execution

### 4. Data Acquisition
**Scrapling** levert:
- Adaptive web scraping
- Anti-bot bypass
- AI-powered extraction

---

## Installatie Quick Reference

### Minimum Requirements
- Python 3.12
- Node.js 18+
- Rust 1.85+
- 16 GB RAM
- 50 GB vrije schijfruimte

### Quick Install (Allemaal)
```bash
# Python environment
python -m venv trading_env
source trading_env/bin/activate

# Core packages
pip install torch pandas numpy plotly
pip install vectorbt scrapling

# Auto-Claude frontend
cd Auto-Claude/apps/frontend && npm install

# decapod
cd decapod && cargo build --release
```

Zie DEPENDENCIES.md voor gedetailleerde instructies.

---

## API Keys Benodigd

Voor volledige functionaliteit:

| Service | Doel | Repository |
|---------|------|------------|
| OpenAI API | AI analysis | Auto-Claude, QuantMuse |
| Alpha Vantage | Market data | QuantMuse |
| Binance API | Crypto trading | QuantMuse |
| OpenAlgo API | Indian markets | vectorbt-skills |

---

## Support en Bijdragen

### Issues
Als je problemen ondervindt:
1. Check DEPENDENCIES.md → Probleemoplossing sectie
2. Check repository README's
3. Open een issue op de betreffende repository

### Documentatie Updates
Deze documentatie is gegenereerd op 2026-03-14.
Voor updates:
1. Check repository changelogs
2. Update documentatie bij nieuwe versies

---

## Versie

**Documentatie versie:** 1.0.0
**Auteur:** Claude Code Analysis
**Laatste update:** 2026-03-14

---

## Volgende Stappen

1. 📖 **Lees SAMENVATTING.md** voor een compleet overzicht
2. 🏗️ **Bekijk ARCHITECTUUR.md** voor integratie mogelijkheden
3. 📦 **Installeer via DEPENDENCIES.md** wanneer je klaar bent
4. 🧩 **Gebruik COMPONENTEN.md** om te bouwen

---

**Veel succes met je project!** 🚀
