# CLAUDE.md — autoresearch

Autonomous AI research framework where an agent iterates on LLM training code (one 5-minute run at a time) to minimize validation bits-per-byte (val_bpb).

---

## Repository Overview

**Purpose:** Give an AI agent a small but real LLM training setup, let it experiment overnight. Agent modifies `train.py`, trains for 5 minutes, checks if the result improved, keeps or discards, and repeats indefinitely.

**Key philosophy:**
- Single file to modify (`train.py`) — scope is minimal and diffs are reviewable
- Fixed 5-minute time budget — all experiments are directly comparable
- Single metric (`val_bpb`) — vocab-size-independent, lower is better
- Simplicity wins — removing code and getting equal results is as good as an improvement

---

## Project Structure

```
autoresearch/
├── train.py          # Agent edits this: model, optimizer, training loop
├── prepare.py        # READ-ONLY: data prep, tokenizer, evaluation harness
├── program.md        # Agent instructions (human edits this to guide research)
├── README.md         # Project documentation
├── pyproject.toml    # Python dependencies (uv)
├── uv.lock           # Locked dependency versions
├── analysis.ipynb    # Jupyter notebook to visualize results.tsv
└── progress.png      # Teaser image of experiment progress over time
```

**Generated at runtime (gitignored):**
- `results.tsv` — tab-separated experiment log
- `run.log` — stdout/stderr from the last training run
- `~/.cache/autoresearch/` — downloaded data shards and trained tokenizer

---

## Development Environment

**Requirements:** Single NVIDIA GPU (H100 tested), Python 3.10, `uv`.

```bash
# Install uv (if not present)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# One-time data prep (~2 min, downloads shards + trains tokenizer)
uv run prepare.py

# Single training run (~5 min)
uv run train.py
```

**Package manager:** `uv` — do not use `pip` or `conda`.

**Python version:** 3.10 (pinned in `.python-version`).

**Dependencies (pyproject.toml):**
- `torch==2.9.1` (CUDA 12.8)
- `kernels>=0.11.7` (Flash Attention 3)
- `tiktoken>=0.11.0` (tokenization)
- `rustbpe>=0.1.0` (BPE tokenizer training)
- `pyarrow>=21.0.0` (parquet file handling)
- `numpy`, `pandas`, `matplotlib`, `requests`

**No new packages may be installed** — only use what is already in `pyproject.toml`.

---

## The Experiment Workflow

See `program.md` for the authoritative agent instructions. Summary:

### Setup (once per run tag)
1. Agree on a run tag (e.g. `mar5`)
2. Create branch: `git checkout -b autoresearch/<tag>` from master
3. Read `README.md`, `prepare.py`, and `train.py` for full context
4. Verify data exists at `~/.cache/autoresearch/`; if not, run `uv run prepare.py`
5. Initialize `results.tsv` with header + baseline entry (val_bpb: 0.997900, 44.0 GB) — do NOT re-run baseline

### Experiment Loop (run forever until interrupted)
```
1. Modify train.py with an experimental idea
2. git commit
3. uv run train.py > run.log 2>&1
4. grep "^val_bpb:\|^peak_vram_mb:" run.log
5. If empty → crash; run tail -n 50 run.log to debug
6. Log result to results.tsv
7. If val_bpb improved → keep the commit ("advance")
8. If equal or worse → git reset to previous state
```

**Timeout:** If a run exceeds 10 minutes, kill it and treat as failure.

**NEVER STOP** the loop once started — the human may be asleep.

---

## results.tsv Format

Tab-separated (NOT comma-separated — commas break descriptions). Five columns:

```
commit	val_bpb	memory_gb	status	description
a1b2c3d	0.997900	44.0	keep	baseline
b2c3d4e	0.993200	44.2	keep	increase matrix LR to 0.05
c3d4e5f	1.005000	44.0	discard	switch to GeLU activation
d4e5f6g	0.000000	0.0	crash	double model width (OOM)
```

- `commit`: 7-char short hash
- `val_bpb`: e.g. `1.234567`; use `0.000000` for crashes
- `memory_gb`: `peak_vram_mb / 1024`, rounded to 1 decimal; use `0.0` for crashes
- `status`: `keep`, `discard`, or `crash`
- `description`: short text (no tabs)

---

## What You CAN and CANNOT Modify

| File | Editable? | Notes |
|------|-----------|-------|
| `train.py` | **Yes** | Everything is fair game |
| `prepare.py` | **No** | Read-only; contains fixed evaluation |
| `program.md` | Human only | Human edits to guide research direction |
| `pyproject.toml` | **No** | No new dependencies |
| `results.tsv` | **Yes** | Append experiment results here |

---

## Key Source Files

### prepare.py — Fixed Constants & Evaluation

Do not modify. Contains:

**Constants:**
```python
MAX_SEQ_LEN   = 2048       # Context length (fixed)
TIME_BUDGET   = 300        # 5-minute training budget in seconds
EVAL_TOKENS   = 40 * 524288  # Validation token count
VOCAB_SIZE    = 8192       # BPE vocabulary size
VAL_SHARD     = MAX_SHARD = 6542  # Pinned validation shard
```

**Key classes/functions:**
- `Tokenizer`: Wraps tiktoken, methods: `from_directory()`, `encode()`, `decode()`, `get_vocab_size()`
- `make_dataloader(tokenizer, B, T, split)`: BOS-aligned dataloader with 100% utilization (best-fit packing, no padding)
- `evaluate_bpb(model, tokenizer, batch_size)`: **Sacred — ground truth metric, never modify**
- `download_data(num_shards, download_workers=8)`: Downloads parquet shards from HuggingFace with 5 retries

**Data source:** `karpathy/climbmix-400b-shuffle` on HuggingFace (6543 parquet shards ~100 MB each). Default: 10 training shards + pinned shard 6542 for validation.

**Cache location:** `~/.cache/autoresearch/` (data shards + tokenizer)

### train.py — Model, Optimizer, Training Loop

The only file the agent edits. Current state:

**Model config (`GPTConfig` dataclass):**
```python
sequence_len    = 2048
vocab_size      = (from tokenizer, ~8192)
n_layer         = 12 (default)
n_head          = 6
n_kv_head       = 6  # GQA: set < n_head to enable
n_embd          = 768 (default)
window_pattern  = "SSSL"  # S=half-context sliding window, L=full attention
```

**Architecture highlights:**
- Token embeddings (wte) + value embeddings (alternating layers, ResFormer-style)
- RoPE (Rotary Position Embeddings)
- Flash Attention 3 (with Hopper fallback for non-H100 GPUs)
- Sliding window attention via `window_pattern` (`"S"` = half-context, `"L"` = full)
- Value residual gating (`resid_lambdas`, `x0_lambdas` — learnable per-layer scalars)
- MLP: Linear → ReLU² → Linear (squared ReLU)
- Logit softcapping (tanh-based)

**Optimizer (`MuonAdamW`):**
- **Muon** for matrix-shaped parameters (orthogonalized gradients, "Polar Express" — 3-5 Newton-Schulz iterations)
- **AdamW** for everything else (scalars, biases, embeddings)
- Compiled with `@torch.compile()` for fused CUDA kernels

**Hyperparameters (top of train.py — primary knobs):**
```python
ASPECT_RATIO       = 64     # model_dim = DEPTH * ASPECT_RATIO
HEAD_DIM           = 128    # target head dimension
WINDOW_PATTERN     = "SSSL" # attention pattern per layer
TOTAL_BATCH_SIZE   = 2**19  # ~524K tokens/step (gradient accumulation)
DEVICE_BATCH_SIZE  = 128    # per-GPU micro-batch
DEPTH              = 8      # number of transformer layers

EMBEDDING_LR       = 0.6
UNEMBEDDING_LR     = 0.004
MATRIX_LR          = 0.04
SCALAR_LR          = 0.5
WEIGHT_DECAY       = 0.2
WARMUP_RATIO       = 0.0
WARMDOWN_RATIO     = 0.5
```

**Training loop features:**
- Gradient accumulation with prefetch
- EMA loss smoothing (beta=0.9)
- Dynamic LR scheduling (linear warmup → cosine/linear warmdown)
- Dynamic weight decay and Muon momentum scheduling
- GC freeze/disable after warmup (performance optimization)
- Fast-fail: aborts if `loss > 100` (detects divergence early)
- Hard stop at exactly `TIME_BUDGET = 300` seconds of training

**Output format (printed at end of run):**
```
---
val_bpb:          0.997900
training_seconds: 300.1
total_seconds:    325.9
peak_vram_mb:     45060.2
mfu_percent:      39.80
total_tokens_M:   499.6
num_steps:        953
num_params_M:     50.3
depth:            8
```

Extract metrics from log with:
```bash
grep "^val_bpb:\|^peak_vram_mb:" run.log
```

---

## Evaluation Metric

**`val_bpb`** — validation bits per byte. Lower is better.

- Vocabulary-size-independent (converts from nats/token via `log(2) * vocab_size / bytes_per_token`)
- Evaluated on a fixed pinned shard (shard 6542) to ensure reproducibility
- Computed by `evaluate_bpb()` in `prepare.py` — **this function must never be modified**

**Baseline:** `0.997900` val_bpb at `44.0 GB` VRAM

**VRAM constraint:** Soft. Some increase is acceptable for meaningful val_bpb gains, but avoid dramatic blowups.

---

## Git Conventions

- **Experiment branches** are named `autoresearch/<tag>` (e.g. `autoresearch/mar5`)
- Each experiment gets its own commit before running
- Successful experiments: keep the commit, continue from it
- Failed experiments: `git reset --hard HEAD~1` to discard
- **Feature/documentation branches** use `claude/<description>-<id>` naming

**Commit style:** Short, descriptive, imperative mood. Describe *what* the experiment tried.

---

## Simplicity Criterion

When deciding whether to keep a change, weigh complexity cost against improvement magnitude:

| Change | Verdict |
|--------|---------|
| 0.001 val_bpb improvement + 20 lines of hacky code | Probably discard |
| 0.001 val_bpb improvement from deleting code | Keep |
| ~0 improvement but much simpler code | Keep |
| Large improvement at any complexity | Keep |

---

## Hardware & Platform Notes

- **Tested hardware:** Single H100 GPU (~45 GB VRAM, BF16 mixed precision)
- **Required:** CUDA-enabled NVIDIA GPU (Flash Attention 3 with Hopper-specific fallback)
- **Not supported out-of-box:** CPU, Apple Silicon (MPS), multi-GPU
- **Forks for other platforms:**
  - macOS: [miolini/autoresearch-macos](https://github.com/miolini/autoresearch-macos)
  - MLX: [trevin-creator/autoresearch-mlx](https://github.com/trevin-creator/autoresearch-mlx)

Environment variables set by `train.py`:
```python
PYTORCH_ALLOC_CONF = "expandable_segments:True"
HF_HUB_DISABLE_PROGRESS_BARS = "1"
```

---

## analysis.ipynb

Jupyter notebook for visualizing experiment results. Reads `results.tsv` and generates:
- Experiment outcome counts (keep/discard/crash)
- Scatter plot with running minimum frontier line
- Summary stats (baseline vs. best achieved)
- Top improvements ranked by delta val_bpb

Run after experiments complete: `jupyter notebook analysis.ipynb`

---

## .gitignore Notes

The following are intentionally excluded from version control:
- `CLAUDE.md`, `AGENTS.md` — generated per-session by launchers
- `results/`, `queue/` — runtime artifacts
- `dev/` — experimental scratch code
- `.venv`, `worktrees/` — local environment files
- `__pycache__`, `*.pyc` — Python bytecode
