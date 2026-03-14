# Dependencies en Requirements

## Overzicht

Dit document beschrijft alle dependencies, installatie-instructies en compatibiliteit tussen repositories.

---

## Systeem Requirements

### Minimum Systeem Specificaties

| Component | Minimum | Aanbevolen |
|-----------|---------|------------|
| OS | Windows 10/11, macOS 12+, Ubuntu 20.04+ | Windows 11, macOS 14+, Ubuntu 22.04+ |
| RAM | 16 GB | 32 GB+ |
| Opslag | 50 GB vrij | 200 GB+ SSD |
| GPU | - | NVIDIA RTX 3080+ (voor ML) |
| CPU | 4 cores | 8+ cores |

### Software Requirements

| Software | Versie | Verplicht |
|----------|--------|-----------|
| Python | 3.10+ | Ja |
| Node.js | 18+ | Ja (voor Auto-Claude frontend) |
| Rust | 1.85 | Ja (voor decapod) |
| Git | 2.30+ | Ja |
| CUDA | 12.8 | Nee (aanbevolen voor ML) |
| Docker | 20.10+ | Nee (aanbevolen) |
| NinjaTrader | 8.1.2.1+ | Alleen voor orderflowbot |

---

## Per Repository Dependencies

### 1. autoresearch

**Python Versie:** 3.10+

**Core Dependencies:**
```
torch==2.9.1+cu128  # PyTorch met CUDA 12.8
kernels
tiktoken
rustbpe
numpy
pandas
pyarrow
matplotlib
requests
```

**Installatie:**
```bash
# Virtuele environment aanmaken
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installeren
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128
pip install kernels tiktoken rustbpe numpy pandas pyarrow matplotlib requests

# Setup uitvoeren
python prepare.py  # Downloads data, traint tokenizer
```

**Optioneel:**
- CUDA 12.8 voor GPU versnelling
- Jupyter Notebook voor analyse

**Schijfruimte:** ~10 GB (data + model)

---

### 2. Auto-Claude

**Backend (Python 3.12+):**

```
# Requirements uit package.json
claude-agent-sdk
graphiti
pydantic
python-dotenv
```

**Frontend (Node.js 18+):**

```
electron 39.2.7
react 19.2.3
typescript
tailwindcss
vitest
playwright
```

**Installatie:**
```bash
# Backend
cd apps/backend
pip install -r requirements.txt

# Frontend
cd apps/frontend
npm install
npm run build  # Of npm run dev voor development

# Electron app
npm run electron:build
```

**Optionele Integraties:**
- OpenAI API key (voor alternatieve LLM)
- GitHub Personal Access Token (voor PR automatisering)
- Linear API key (voor issue tracking)

**Schijfruimte:** ~5 GB

---

### 3. Scrapling

**Python Versie:** 3.10+

**Core Dependencies:**
```
lxml>=6.0.2
cssselect>=1.4.0
orjson>=3.11.7
tld>=0.13.1
w3lib>=2.4.0
typing_extensions
```

**Optionele Dependencies:**
```bash
# Voor browser automation
pip install 'scrapling[fetchers]'

# Voor AI integration
pip install 'scrapling[ai]'

# Voor interactive shell
pip install 'scrapling[shell]'

# Alles tegelijk
pip install 'scrapling[all]'
```

**Specifieke Fetcher Requirements:**
```bash
# Playwright (voor DynamicFetcher/StealthyFetcher)
playwright==1.40+
curl_cffi
browserforge
anyio
```

**Installatie:**
```bash
pip install scrapling

# Browsers installeren (voor fetchers)
scrapling install
```

**Schijfruimte:** ~500 MB (zonder browsers)

---

### 4. vectorbt-backtesting-skills

**Python Versie:** 3.10+

**Core Dependencies:**
```
vectorbt==0.28.4
TA-Lib==0.6.8
pandas
numpy
plotly
matplotlib
```

**Data Sources:**
```
openalgo==1.0.45  # Indiase markten
yfinance          # Global markten
python-dotenv
```

**Development/Testing:**
```
jupyter
nbformat
tqdm
anywidget
```

**Installatie:**
```bash
# Virtuele environment
python -m venv venv
source venv/bin/activate

# Dependencies installeren
pip install vectorbt TA-Lib pandas numpy plotly matplotlib yfinance python-dotenv

# TA-Lib installatie (specifiek per OS)
# Ubuntu/Debian:
sudo apt-get install ta-lib
pip install TA-Lib

# macOS:
brew install ta-lib
pip install TA-Lib

# Windows:
# Download .whl van https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib
pip install TA_Lib-0.6.8-cpXXX-cpXXX-win_amd64.whl

# OpenAlgo setup
export OPENALGO_API_KEY="your_api_key"
export OPENALGO_ENDPOINT="http://127.0.0.1:5000"
```

**Schijfruimte:** ~2 GB

---

### 5. decapod

**Rust Versie:** 1.85+ (edition 2024)

**Core Dependencies (uit Cargo.toml):**
```toml
[dependencies]
rusqlite = "0.32"      # SQLite database
clap = "4.5"           # CLI interface
serde = "1.0"          # JSON serialization
tiktoken-rs = "0.6"    # Tokenization
rayon = "1.10"         # Parallelism
rust-embed = "8.5"     # Embedded files
```

**Installatie:**
```bash
# Rust installeren (indien niet aanwezig)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Rust toolchain update
rustup update
rustup default stable

# decapod builden
cd decapod
cargo build --release

# Binary beschikbaar in target/release/decapod
```

**Testen:**
```bash
cargo test
cargo bench
```

**Schijfruimte:** ~500 MB

---

### 6. claude-code-continuous-learning-skill

**Python Versie:** 3.10+

**Dependencies:**
```
# Geen specifieke Python dependencies vereist
# Gebruikt bash scripts en Claude Code integratie
```

**Installatie:**
```bash
# Kopieer naar Claude Code skills directory
cp -r claude-code-continuous-learning-skill ~/.claude/skills/

# Of project-specifiek
cp -r claude-code-continuous-learning-skill .claude/skills/

# Activation hook instellen
chmod +x ~/.claude/skills/claude-code-continuous-learning-skill/scripts/continuous-learning-activator.sh
```

**Optioneel:**
```bash
# Voor research integration
pip install openai anthropic google-generativeai
```

**Schijfruimte:** ~50 MB

---

### 7. QuantMuse

**Python Versie:** 3.10+
**C++ Compiler:** GCC 9+ / MSVC 2019+

**Python Dependencies:**
```
# Data fetchers
yfinance
python-binance
alpha-vantage

# Analysis
pandas
numpy
scipy
statsmodels

# AI/ML
openai
langchain
textblob
vaderSentiment

# Web
fastapi
uvicorn
streamlit
websockets

# Storage
redis
psycopg2-binary
sqlalchemy
```

**C++ Dependencies:**
```
# C++17 of hoger
# Boost libraries
# OpenSSL
```

**Installatie:**
```bash
# Python dependencies
pip install yfinance python-binance alpha-vantage pandas numpy scipy statsmodels
pip install openai langchain textblob vaderSentiment
pip install fastapi uvicorn streamlit websockets
pip install redis psycopg2-binary sqlalchemy

# Redis (optioneel, voor caching)
# Ubuntu/Debian:
sudo apt-get install redis-server

# macOS:
brew install redis

# Windows:
# Download van https://redis.io/download

# PostgreSQL (optioneel, voor persistent storage)
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Windows:
# Download van https://www.postgresql.org/download/

# API Keys instellen
export OPENAI_API_KEY="your_openai_key"
export ALPHA_VANTAGE_API_KEY="your_av_key"
export BINANCE_API_KEY="your_binance_key"
```

**C++ Backend Build:**
```bash
cd QuantMuse/backend
mkdir build && cd build
cmake ..
make
```

**Schijfruimte:** ~5 GB (inclusief database)

---

### 8. orderflowbot-warm

**Platform:** NinjaTrader 8.1.2.1+
**Language:** C# 8.0
**Framework:** .NET 8.0

**Dependencies:**
```
NinjaTrader.Core  (via NinjaTrader SDK)
System.Text.Json  (standard library)
xUnit             (testing)
Moq               (mocking)
```

**Installatie:**
```bash
# NinjaTrader installeren
# Download van https://www.ninjatrader.com/

# Visual Studio 2019+ met .NET 8.0 SDK
# Download van https://visualstudio.microsoft.com/

# Repository openen in Visual Studio
cd orderflowbot-warm
# Open NinjaTrader.sln

# Restore NuGet packages
dotnet restore

# Build solution
dotnet build --configuration Release

# Output in NinjaTrader/AddOns/OrderFlowBot/
```

**Vereist:**
- NinjaTrader 8.1.2.1 of hoger
- Volumetric data (lifetime license of OrderFlow+ subscription)
- Voor ontwikkeling: Visual Studio 2019+ met .NET desktop development workload

**Schijfruimte:** ~1 GB

---

## Cross-Repository Compatibiliteit

### Python Version Matrix

| Repository | Min Python | Max Python | Opmerking |
|------------|------------|------------|-----------|
| autoresearch | 3.10 | 3.12 | PyTorch compatibility |
| Auto-Claude (backend) | 3.12 | 3.13 | Nieuwste features |
| Scrapling | 3.10 | 3.13 | Breed compatible |
| vectorbt-skills | 3.10 | 3.12 | NumPy compatibility |
| QuantMuse | 3.10 | 3.12 | Pandas compatibility |
| continuous-learning | 3.10 | 3.13 | Minimale requirements |

**Aanbevolen:** Python 3.12 voor alle repositories

### Dependency Conflicten

**Potentiële Conflicten:**
```
PyTorch versies:
- autoresearch: torch==2.9.1
- QuantMuse: Geen directe PyTorch dependency

Oplossing: Gebruik torch==2.9.1 in gedeelde environment
```

```
NumPy/Pandas versies:
- vectorbt: Vereist specifieke versies
- QuantMuse: Meer flexibel

Oplossing: Pin versies in requirements.txt
```

### Virtuele Environment Strategy

**Optie 1: Shared Environment**
```bash
python -m venv shared_env
source shared_env/bin/activate
pip install -r requirements_all.txt  # Gecombineerde requirements
```

**Optie 2: Separate Environments**
```bash
# Per repository
python -m venv autoresearch_env
python -m venv quantmuse_env
python -m venv scrapling_env
```

**Optie 3: Conda (Aanbevolen voor Data Science)**
```bash
conda create -n trading python=3.12
conda activate trading
conda install pytorch pandas numpy plotly
pip install vectorbt scrapling
```

---

## Installatie Checklist

### Stap 1: Basis Tools
- [ ] Python 3.12 geïnstalleerd
- [ ] Node.js 18+ geïnstalleerd
- [ ] Rust 1.85+ geïnstalleerd
- [ ] Git 2.30+ geïnstalleerd
- [ ] Visual Studio Code (optioneel)

### Stap 2: Python Packages
- [ ] Virtuele environment gecreëerd
- [ ] PyTorch 2.9.1 geïnstalleerd
- [ ] TA-Lib geïnstalleerd
- [ ] Overige Python packages geïnstalleerd

### Stap 3: Extra Software
- [ ] Redis (optioneel)
- [ ] PostgreSQL (optioneel)
- [ ] Docker (optioneel)
- [ ] NinjaTrader 8 (alleen voor orderflowbot)

### Stap 4: API Keys
- [ ] OpenAI API key
- [ ] Alpha Vantage API key
- [ ] Binance API key
- [ ] OpenAlgo API key (Indiase markten)

### Stap 5: Repository Setup
- [ ] autoresearch: `python prepare.py`
- [ ] Auto-Claude: `npm install` in apps/frontend
- [ ] Scrapling: `scrapling install`
- [ ] decapod: `cargo build --release`
- [ ] QuantMuse: Database setup
- [ ] orderflowbot: Build in Visual Studio

---

## Probleemoplossing

### Common Issues

**Issue: TA-Lib installatie faalt**
```bash
# Ubuntu/Debian
sudo apt-get install build-essential wget
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install
pip install TA-Lib
```

**Issue: PyTorch CUDA versie mismatch**
```bash
# Check CUDA versie
nvidia-smi

# Installeer juiste PyTorch versie
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Issue: Rust compiler niet gevonden**
```bash
# Rust installeren
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env
```

**Issue: Node.js versie te oud**
```bash
# Gebruik nvm voor versie management
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

---

## Performance Optimalisatie

### GPU Acceleratie
```bash
# Check of CUDA beschikbaar is
python -c "import torch; print(torch.cuda.is_available())"

# GPU geheugen check
nvidia-smi
```

### Parallel Processing
```bash
# Scrapling concurrentie instellen
export SCRAPLING_CONCURRENCY=10

# Rust build optimalisatie
export CARGO_BUILD_JOBS=8
```

### Caching
```bash
# Redis configureren voor QuantMuse
redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
```

---

**Documentatie versie:** 1.0.0
**Laatste update:** 2026-03-14
