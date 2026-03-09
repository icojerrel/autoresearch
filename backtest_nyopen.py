#!/usr/bin/env python3
"""
Synthetic backtest — NY Open Edge v4.1 strategy
Simulates the core pattern-classification + sweep logic using GBM price data.

Usage:
    uv run backtest_nyopen.py [--sessions N] [--seed S] [--plot]

Output:
    - Per-session results table
    - Rolling hit rate over time
    - Summary statistics per pattern
"""
import argparse
import random
import math
import sys

# ─────────────────────────────────────────────────────────────
# GBM PARAMETERS (calibrated to NQ 5-minute bars, 2021-2025)
# ─────────────────────────────────────────────────────────────
NQ_INITIAL   = 20_000.0   # starting price
ANNUAL_DRIFT = 0.15       # annualised drift (bull market)
ANNUAL_VOL   = 0.22       # annualised volatility
TRADING_DAYS = 252
BARS_PER_DAY = 78         # 5-minute bars, 6.5 RTH hours

DT           = 1 / (TRADING_DAYS * BARS_PER_DAY)
DRIFT_PER_BAR = (ANNUAL_DRIFT - 0.5 * ANNUAL_VOL**2) * DT
VOL_PER_BAR   = ANNUAL_VOL * math.sqrt(DT)

# Session times in bar-indices (5-min bars from midnight)
# Midnight = bar 0
ASIA_START   = 0     # 00:00 ET
ASIA_END     = 24    # 02:00 ET
LONDON_START = 24    # 02:00 ET
LONDON_END   = 96    # 08:00 ET
NY_START     = 96    # 08:00 ET
RTH_START    = 114   # 09:30 ET
IB_END       = 126   # 10:30 ET
NOON_START   = 138   # 11:30 ET
NOON_END     = 150   # 12:30 ET
RTH_END      = 192   # 16:00 ET
DAY_BARS     = 192   # 16-hour window (00:00-16:00 ET), 5-min bars

# Stats database — from Pine Script (see get_stats in ny_open_edge_v4.pine)
# [hi_pct, lo_pct, med_pen_pts, fail_rate, n, tier]
STATS = {
    (1, True):  (58, 42, 35, 49, 80,  2),
    (1, False): (44, 56, 33, 49, 241, 2),
    (2, True):  (60, 40, 50, 42, 30,  3),
    (2, False): (38, 62, 55, 39, 34,  3),
    (3, True):  (78, 22, 45, 37, 220, 1),
    (3, False): (55, 45, 30, 44, 280, 2),
    (4, True):  (47, 53, 28, 45, 260, 2),
    (4, False): (18, 82, 42, 38, 170, 1),
}

TIER_LABEL = {1: "Tier1", 2: "Tier2", 3: "Tier3"}


# ─────────────────────────────────────────────────────────────
# PRICE GENERATION
# ─────────────────────────────────────────────────────────────
def gen_day(price_start, rng):
    """
    Generate one 16-hour trading day as a list of (open, high, low, close)
    5-minute bars using Geometric Brownian Motion.
    Returns (bars, price_end).
    """
    bars = []
    p = price_start
    for _ in range(DAY_BARS):
        o = p
        z = rng.gauss(0, 1)
        p = p * math.exp(DRIFT_PER_BAR + VOL_PER_BAR * z)
        # Intrabar: simulate H/L using half-bar noise
        z2 = rng.gauss(0, 1)
        mid_h = max(o, p) * math.exp( abs(VOL_PER_BAR * 0.5 * z2))
        mid_l = min(o, p) * math.exp(-abs(VOL_PER_BAR * 0.5 * z2))
        bars.append((o, mid_h, mid_l, p))
    return bars, p


def session_range(bars, start, end):
    """High and low over bars[start:end]."""
    hi = max(b[1] for b in bars[start:end])
    lo = min(b[2] for b in bars[start:end])
    return hi, lo


# ─────────────────────────────────────────────────────────────
# PATTERN CLASSIFICATION (mirrors Pine Script classify())
# ─────────────────────────────────────────────────────────────
def classify(asia_h, asia_l, lon_h, lon_l):
    """
    P1 = London Engulfs Asia   (lon_h > asia_h AND lon_l < asia_l)
    P2 = Asia Engulfs London   (asia_h > lon_h AND asia_l < lon_l)
    P3 = Partial Up            (lon_h > asia_h AND lon_l >= asia_l)
    P4 = Partial Down          (lon_l < asia_l AND lon_h <= asia_h)
    """
    if lon_h > asia_h and lon_l < asia_l:
        return 1
    elif asia_h > lon_h and asia_l < lon_l:
        return 2
    elif lon_h > asia_h and lon_l >= asia_l:
        return 3
    elif lon_l < asia_l and lon_h <= asia_h:
        return 4
    else:
        return 1  # Fallback (rare equal edges)


# ─────────────────────────────────────────────────────────────
# OUTCOME EVALUATION
# ─────────────────────────────────────────────────────────────
def evaluate_outcome(bars, lon_h, lon_l, bias_bull):
    """
    Detect whether the US session (NY_START:RTH_END) swept London H or L.
    Returns (hi_swept, lo_swept, hi_pen, lo_pen).
    """
    hi_swept = lo_swept = False
    hi_pen = lo_pen = 0.0
    for b in bars[NY_START:RTH_END]:
        if b[1] > lon_h:
            hi_swept = True
            hi_pen = max(hi_pen, b[1] - lon_h)
        if b[2] < lon_l:
            lo_swept = True
            lo_pen = max(lo_pen, lon_l - b[2])
    both = hi_swept and lo_swept
    if both:
        return hi_swept, lo_swept, hi_pen, lo_pen, "both"
    if bias_bull and hi_swept and not lo_swept:
        return hi_swept, lo_swept, hi_pen, lo_pen, "correct"
    if not bias_bull and lo_swept and not hi_swept:
        return hi_swept, lo_swept, hi_pen, lo_pen, "correct"
    if both:
        winner = "correct" if (bias_bull and hi_pen > lo_pen) or (not bias_bull and lo_pen > hi_pen) else "wrong"
        return hi_swept, lo_swept, hi_pen, lo_pen, winner
    return hi_swept, lo_swept, hi_pen, lo_pen, "wrong"


# ─────────────────────────────────────────────────────────────
# MAIN BACKTEST LOOP
# ─────────────────────────────────────────────────────────────
def run_backtest(n_sessions=500, seed=42, rolling_lb=20, tier_filter=None):
    rng = random.Random(seed)
    price = NQ_INITIAL

    results = []
    pat_stats = {p: {"correct": 0, "wrong": 0, "both": 0, "skip": 0} for p in range(1, 5)}
    rolling_window = []

    print(f"\n{'─'*80}")
    print(f"  NY Open Edge v4.1 — Synthetic Backtest")
    print(f"  Sessions: {n_sessions}  |  Seed: {seed}  |  Rolling LB: {rolling_lb}")
    if tier_filter:
        print(f"  Tier filter: only Tier {tier_filter}")
    print(f"{'─'*80}")
    print(f"{'Sess':>4}  {'Pat':>3}  {'Mid':>4}  {'Tier':>5}  "
          f"{'Bias':>5}  {'HiSw':>4}  {'LoSw':>4}  {'Outcome':>8}  {'Roll%':>6}")
    print(f"{'─'*80}")

    for sess in range(1, n_sessions + 1):
        bars, price = gen_day(price, rng)

        asia_h, asia_l = session_range(bars, ASIA_START, ASIA_END)
        lon_h,  lon_l  = session_range(bars, LONDON_START, LONDON_END)
        lon_mid        = (lon_h + lon_l) / 2.0

        ny_open_price = bars[NY_START][0]
        above_mid     = ny_open_price > lon_mid

        pat = classify(asia_h, asia_l, lon_h, lon_l)
        hi_pct, lo_pct, med_pen, fail_rate, n, tier = STATS[(pat, above_mid)]
        bias_bull = hi_pct >= lo_pct

        # Tier filter — skip if not the requested tier
        if tier_filter and tier != tier_filter:
            pat_stats[pat]["skip"] += 1
            continue

        hi_swept, lo_swept, hi_pen, lo_pen, outcome = evaluate_outcome(
            bars, lon_h, lon_l, bias_bull
        )

        # Rolling accuracy
        if outcome == "correct":
            rolling_window.append(1)
            pat_stats[pat]["correct"] += 1
        elif outcome == "both":
            rolling_window.append(0)
            pat_stats[pat]["both"] += 1
        else:
            rolling_window.append(0)
            pat_stats[pat]["wrong"] += 1

        if len(rolling_window) > rolling_lb:
            rolling_window.pop(0)
        roll_pct = sum(rolling_window) / len(rolling_window) * 100

        bias_str = "BULL" if bias_bull else "BEAR"
        outcome_str = {
            "correct": "✓ correct",
            "wrong":   "✗ wrong  ",
            "both":    "≈ both   ",
        }[outcome]

        print(f"{sess:>4}  P{pat}   {'abv' if above_mid else 'blw':>4}  "
              f"{TIER_LABEL[tier]:>5}  {bias_str:>5}  "
              f"{'Y' if hi_swept else 'N':>4}  {'Y' if lo_swept else 'N':>4}  "
              f"{outcome_str}  {roll_pct:>5.1f}%")
        results.append({
            "sess": sess, "pat": pat, "above_mid": above_mid,
            "tier": tier, "bias_bull": bias_bull,
            "hi_swept": hi_swept, "lo_swept": lo_swept,
            "outcome": outcome, "roll_pct": roll_pct,
        })

    return results, pat_stats


# ─────────────────────────────────────────────────────────────
# SUMMARY STATS
# ─────────────────────────────────────────────────────────────
def print_summary(results, pat_stats, n_sessions):
    total    = len(results)
    correct  = sum(1 for r in results if r["outcome"] == "correct")
    wrong    = sum(1 for r in results if r["outcome"] == "wrong")
    both     = sum(1 for r in results if r["outcome"] == "both")

    print(f"\n{'═'*80}")
    print(f"  SUMMARY — {total} evaluated sessions (of {n_sessions} generated)")
    print(f"{'═'*80}")
    print(f"  Overall hit rate : {100*correct/total:>5.1f}%  ({correct}/{total})")
    print(f"  Wrong            : {100*wrong/total:>5.1f}%  ({wrong}/{total})")
    print(f"  Both swept       : {100*both/total:>5.1f}%  ({both}/{total})")
    print()
    print(f"  {'Pattern':<22}  {'N':>4}  {'Correct':>8}  {'Wrong':>7}  {'Both':>6}  {'Hit%':>6}")
    print(f"  {'─'*60}")

    pat_names = {
        1: "P1 London Engulfs Asia",
        2: "P2 Asia Engulfs London",
        3: "P3 Partial Up",
        4: "P4 Partial Down",
    }
    for p in range(1, 5):
        s = pat_stats[p]
        n_p = s["correct"] + s["wrong"] + s["both"]
        if n_p == 0:
            continue
        hit = 100 * s["correct"] / n_p
        print(f"  {pat_names[p]:<22}  {n_p:>4}  {s['correct']:>8}  "
              f"{s['wrong']:>7}  {s['both']:>6}  {hit:>5.1f}%")

    print()

    # Tier breakdown
    tier_corr = {1: 0, 2: 0, 3: 0}
    tier_tot  = {1: 0, 2: 0, 3: 0}
    for r in results:
        tier_tot[r["tier"]] += 1
        if r["outcome"] == "correct":
            tier_corr[r["tier"]] += 1
    print(f"  Tier breakdown:")
    for t in [1, 2, 3]:
        if tier_tot[t] == 0:
            continue
        print(f"    Tier {t}: {100*tier_corr[t]/tier_tot[t]:.1f}%  "
              f"({tier_corr[t]}/{tier_tot[t]})")

    print()
    # Rolling accuracy at the end
    last_roll = results[-1]["roll_pct"] if results else 0
    print(f"  Rolling accuracy (last {min(20, len(results))} sessions): {last_roll:.1f}%")
    print()
    print("  NOTE: This is a synthetic backtest using GBM-simulated NQ prices.")
    print("  Results show the PATTERN DISTRIBUTION and HIT RATES of the statistical")
    print("  edges, not live trading P&L. Use real data for accurate calibration.")
    print(f"{'═'*80}\n")


# ─────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NY Open Edge synthetic backtest")
    parser.add_argument("--sessions", type=int, default=200,
                        help="Number of sessions to simulate (default: 200)")
    parser.add_argument("--seed",     type=int, default=42,
                        help="Random seed for reproducibility (default: 42)")
    parser.add_argument("--rolling",  type=int, default=20,
                        help="Rolling accuracy lookback in sessions (default: 20)")
    parser.add_argument("--tier",     type=int, default=None, choices=[1, 2, 3],
                        help="Only evaluate sessions with this tier (1=strongest)")
    args = parser.parse_args()

    results, pat_stats = run_backtest(
        n_sessions=args.sessions,
        seed=args.seed,
        rolling_lb=args.rolling,
        tier_filter=args.tier,
    )
    print_summary(results, pat_stats, args.sessions)
