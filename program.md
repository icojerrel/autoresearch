# autoresearch

This is an experiment to have the LLM do its own research.

## Setup

To set up a new experiment, work with the user to:

1. **Agree on a run tag**: propose a tag based on today's date (e.g. `mar5`). The branch `autoresearch/<tag>` must not already exist — this is a fresh run.
2. **Create the branch**: `git checkout -b autoresearch/<tag>` from current master.
3. **Read the in-scope files**: The repo is small. Read these files for full context:
   - `README.md` — repository context.
   - `prepare.py` — fixed constants, data prep, tokenizer, dataloader, evaluation. Do not modify.
   - `train.py` — the file you modify. Model architecture, optimizer, training loop.
4. **Verify data exists**: Check that `~/.cache/autoresearch/` contains data shards and a tokenizer. If not, tell the human to run `uv run prepare.py`.
5. **Initialize results.tsv**: Create `results.tsv` with header row and baseline entry. The baseline results are already known from the output format section below (val_bpb: 0.997900, peak_vram_mb: 45060.2). Do NOT re-run the baseline — just record it.
6. **Confirm and go**: Confirm setup looks good.

Once you get confirmation, kick off the experimentation.

## Experimentation

Each experiment runs on a single GPU. The training script runs for a **fixed time budget of 5 minutes** (wall clock training time, excluding startup/compilation). You launch it simply as: `uv run train.py`.

**What you CAN do:**
- Modify `train.py` — this is the only file you edit. Everything is fair game: model architecture, optimizer, hyperparameters, training loop, batch size, model size, etc.

**What you CANNOT do:**
- Modify `prepare.py`. It is read-only. It contains the fixed evaluation, data loading, tokenizer, and training constants (time budget, sequence length, etc).
- Install new packages or add dependencies. You can only use what's already in `pyproject.toml`.
- Modify the evaluation harness. The `evaluate_bpb` function in `prepare.py` is the ground truth metric.

**The goal is simple: get the lowest val_bpb.** Since the time budget is fixed, you don't need to worry about training time — it's always 5 minutes. Everything is fair game: change the architecture, the optimizer, the hyperparameters, the batch size, the model size. The only constraint is that the code runs without crashing and finishes within the time budget.

**VRAM** is a soft constraint. Some increase is acceptable for meaningful val_bpb gains, but it should not blow up dramatically.

**Simplicity criterion**: All else being equal, simpler is better. A small improvement that adds ugly complexity is not worth it. Conversely, removing something and getting equal or better results is a great outcome — that's a simplification win. When evaluating whether to keep a change, weigh the complexity cost against the improvement magnitude. A 0.001 val_bpb improvement that adds 20 lines of hacky code? Probably not worth it. A 0.001 val_bpb improvement from deleting code? Definitely keep. An improvement of ~0 but much simpler code? Keep.

**The first run**: Your very first run should always be to establish the baseline, so you will run the training script as is.

## Output format

Once the script finishes it prints a summary like this:

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

Note that the script is configured to always stop after 5 minutes, so depending on the computing platform of this computer the numbers might look different. You can extract the key metric from the log file:

```
grep "^val_bpb:" run.log
```

## Logging results

When an experiment is done, log it to `results.tsv` (tab-separated, NOT comma-separated — commas break in descriptions).

The TSV has a header row and 5 columns:

```
commit	val_bpb	memory_gb	status	description
```

1. git commit hash (short, 7 chars)
2. val_bpb achieved (e.g. 1.234567) — use 0.000000 for crashes
3. peak memory in GB, round to .1f (e.g. 12.3 — divide peak_vram_mb by 1024) — use 0.0 for crashes
4. status: `keep`, `discard`, or `crash`
5. short text description of what this experiment tried

Example:

```
commit	val_bpb	memory_gb	status	description
a1b2c3d	0.997900	44.0	keep	baseline
b2c3d4e	0.993200	44.2	keep	increase LR to 0.04
c3d4e5f	1.005000	44.0	discard	switch to GeLU activation
d4e5f6g	0.000000	0.0	crash	double model width (OOM)
```

## The experiment loop

The experiment runs on a dedicated branch (e.g. `autoresearch/mar5` or `autoresearch/mar5-gpu0`).

LOOP FOREVER:

1. Look at the git state: the current branch/commit we're on
2. Tune `train.py` with an experimental idea by directly hacking the code.
3. git commit
4. Run the experiment: `uv run train.py > run.log 2>&1` (redirect everything — do NOT use tee or let output flood your context)
5. Read out the results: `grep "^val_bpb:\|^peak_vram_mb:" run.log`
6. If the grep output is empty, the run crashed. Run `tail -n 50 run.log` to read the Python stack trace and attempt a fix. If you can't get things to work after more than a few attempts, give up.
7. Record the results in the tsv
8. If val_bpb improved (lower), you "advance" the branch, keeping the git commit
9. If val_bpb is equal or worse, you git reset back to where you started

The idea is that you are a completely autonomous researcher trying things out. If they work, keep. If they don't, discard. And you're advancing the branch so that you can iterate. If you feel like you're getting stuck in some way, you can rewind but you should probably do this very very sparingly (if ever).

**Timeout**: Each experiment should take ~5 minutes total (+ a few seconds for startup and eval overhead). If a run exceeds 10 minutes, kill it and treat it as a failure (discard and revert).

**Crashes**: If a run crashes (OOM, or a bug, or etc.), use your judgment: If it's something dumb and easy to fix (e.g. a typo, a missing import), fix it and re-run. If the idea itself is fundamentally broken, just skip it, log "crash" as the status in the tsv, and move on.

**NEVER STOP**: Once the experiment loop has begun (after the initial setup), do NOT pause to ask the human if you should continue. Do NOT ask "should I keep going?" or "is this a good stopping point?". The human might be asleep, or gone from a computer and expects you to continue working *indefinitely* until you are manually stopped. You are autonomous. If you run out of ideas, think harder — read papers referenced in the code, re-read the in-scope files for new angles, try combining previous near-misses, try more radical architectural changes. The loop runs until the human interrupts you, period.

As an example use case, a user might leave you running while they sleep. If each experiment takes you ~5 minutes then you can run approx 12/hour, for a total of about 100 over the duration of the average human sleep. The user then wakes up to experimental results, all completed by you while they slept!

## Research strategy

This section provides domain knowledge to help you run smarter experiments and find good results faster.

### Prioritized experiment categories

Work through these roughly in order. Earlier categories tend to have lower variance (safer experiments) while later ones are higher risk / higher reward.

**Tier 1 — Hyperparameter tuning (low risk, always try first):**
- Learning rate scaling: try MATRIX_LR in {0.02, 0.03, 0.04, 0.05, 0.06}; try EMBEDDING_LR in {0.3, 0.6, 1.0}
- Batch size: try TOTAL_BATCH_SIZE in {2**18, 2**19, 2**20} — larger batches often help with Muon
- Warmup ratio: try WARMUP_RATIO in {0.0, 0.02, 0.05, 0.1} — a small warmup often helps stability
- Warmdown ratio: try WARMDOWN_RATIO in {0.3, 0.4, 0.5} — sometimes less cooldown = more peak performance
- Weight decay: try WEIGHT_DECAY in {0.05, 0.1, 0.2, 0.3}

**Tier 2 — Model size / shape (medium risk):**
- Depth: try DEPTH in {6, 8, 10, 12} — more layers with ASPECT_RATIO fixed changes capacity
- Aspect ratio: try ASPECT_RATIO in {48, 56, 64, 72, 80} — controls width/depth tradeoff
- HEAD_DIM: try {64, 128} — smaller head dim → more heads → more parallel attention patterns
- MLP expansion: try ratios in {3, 4, 8/3} — SwiGLU typically uses 8/3 to match param count at 4x
- GQA (grouped-query attention): try n_kv_head = n_head // 2 or n_head // 4 for efficiency
- Window pattern: try "LSSL", "LLSL", "SSLL", "SLSL", "LLLL" — varies which layers see full context

**Tier 3 — Optimizer tuning (medium risk):**
- Adam betas: try (0.85, 0.95), (0.9, 0.95), (0.95, 0.98) — beta1 controls momentum strength
- Muon momentum schedule: try ramping more slowly (e.g. over 500 steps) or quickly (100 steps)
- Muon ns_steps: try {3, 5, 7} — more steps = more accurate orthogonalization
- Gradient clipping: add `torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)` before optimizer.step() — often stabilizes training

**Tier 4 — Architectural changes (higher risk, potentially high reward):**
- Activation function: try SwiGLU (gate * up projection * silu(gate)), GELU, ReLU² (current) — SwiGLU is state-of-the-art
- QK normalization: already present (norm(q), norm(k)); try removing it to see if it matters
- Value embeddings: try disabling them (remove has_ve, set ve=None everywhere) — check if they help
- Residual skip (x0_lambdas): try removing the x0 skip connection to simplify
- Logit softcapping: try values {10, 15, 20, 30} or remove entirely
- Pre-norm vs post-norm: already pre-norm; try post-norm or sandwich norm
- RoPE base: try {500, 1000, 10000, 100000} — affects how position information decays with distance
- Tied embeddings: tie wte and lm_head weights (`model.lm_head.weight = model.transformer.wte.weight`)

**Tier 5 — Training loop changes (medium risk):**
- LR schedule shape: try cosine decay instead of linear warmdown
- Gradient accumulation: change DEVICE_BATCH_SIZE to affect microbatch size without changing total batch
- Loss reduction: try token-level weighting or sequence-level averaging

### Meta-strategy

**Exploit vs. explore**: After finding a win, run 2-3 follow-up experiments in the same direction before moving on. If LR=0.05 beats 0.04, also try 0.06. If depth=10 beats 8, also try 12. Squeeze the gain before pivoting.

**Combine wins**: Every few experiments, try combining all accumulated `keep` changes together if they haven't already been combined. Sometimes changes are independently neutral but synergistic together.

**Near-misses are data**: A `discard` that's close to the current best (within 0.001 val_bpb) tells you something. Consider variants of that idea, or try it after other improvements have been made.

**Track your hypotheses**: Before each experiment, note in the description what you expect to happen and why. This helps you learn from both successes and failures.

**Re-use previous work**: If you're stuck, look at all your `discard` experiments. Some ideas that failed early might work now that the model has improved. Also try reversing a recent `keep` to confirm it actually helps.

**Avoid local minima traps**: If you've been tuning hyperparameters for 10+ experiments without big gains, pivot to architectural changes. Conversely, after a big architectural change, always re-tune key hyperparameters (LR especially) as the optimal values may shift.

### Known results from the literature

These are findings that are well-established and likely to transfer to this setting:

- **SwiGLU > ReLU² > GELU** for MLP activations at this scale (PaLM, LLaMA papers)
- **GQA** (grouped-query attention) trades small quality loss for large efficiency gain — can allow deeper/wider models in same VRAM
- **Cosine LR decay** is often slightly better than linear cooldown
- **Warmup** (even 2-5% of budget) helps avoid early training instability
- **Larger batch sizes** work better with Muon (orthogonal gradient update benefits from more signal)
- **Gradient clipping** (norm ≤ 1.0) generally helps stability without hurting performance
- **Tied embeddings** often slightly hurt perplexity but save parameters — useful if you want to reallocate params elsewhere
- **RoPE base scaling**: for short sequences (2048 tokens), base=10000 is standard; higher bases help long-context but may hurt short-context
