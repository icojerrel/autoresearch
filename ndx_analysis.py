#!/usr/bin/env python3
"""
NDX Statistical Analysis — NY Open Edge v4.1
Validates hard-coded Pine Script parameters against actual NDX data.

Usage:
    python3 ndx_analysis.py \
        --daily  /path/to/NDX_daily_max.csv \
        --hourly /path/to/NDX_hourly_2y.csv

Outputs:
    1. SDEV%       → validates sdev_pct = 1.376 in Pine Script
    2. IB stats    → validates IB upper 81% / lower 74%
    3. RTH 1H cont → validates 9AM hour 70% continuation
    4. Day-of-week → bull/bear % by weekday
    5. Monthly     → average return by month
    6. Pine Script SUGGESTED UPDATES (copy-paste ready)
"""

import csv
import math
import sys
import argparse
from datetime import datetime, timezone, timedelta
from collections import defaultdict

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def parse_ts(s):
    """Parse ISO timestamp → datetime (UTC-aware)."""
    s = s.replace(".000Z", "+00:00").replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(s)
    except ValueError:
        # Fallback: strip timezone and treat as UTC
        return datetime.fromisoformat(s[:19]).replace(tzinfo=timezone.utc)

def et_date(dt):
    """Get ET date for a UTC datetime (RTH bars never cross midnight in ET)."""
    # RTH is 9:30–16:00 ET, so UTC date is always the ET date for these bars
    return dt.date()

def mean(vals):
    return sum(vals) / len(vals) if vals else 0.0

def stdev(vals):
    if len(vals) < 2:
        return 0.0
    m = mean(vals)
    variance = sum((x - m) ** 2 for x in vals) / (len(vals) - 1)
    return math.sqrt(variance)

def pct(n, d, decimals=1):
    return round(100 * n / d, decimals) if d > 0 else 0.0

def bar(val, max_val=100, width=20, fill="█", empty="░"):
    filled = round(val / max_val * width)
    return fill * filled + empty * (width - filled)

# ─────────────────────────────────────────────────────────────
# 1. LOAD DAILY DATA
# ─────────────────────────────────────────────────────────────

def load_daily(path):
    rows = []
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                rows.append({
                    "date": parse_ts(row["Date"]).date(),
                    "open":  float(row["Open"]),
                    "high":  float(row["High"]),
                    "low":   float(row["Low"]),
                    "close": float(row["Close"]),
                })
            except (ValueError, KeyError):
                continue
    rows.sort(key=lambda r: r["date"])
    return rows

# ─────────────────────────────────────────────────────────────
# 2. LOAD HOURLY DATA → group by ET date
# ─────────────────────────────────────────────────────────────

def load_hourly(path):
    """Returns dict: date → list of bars (sorted by time)."""
    by_date = defaultdict(list)
    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                dt  = parse_ts(row["Date"])
                day = et_date(dt)
                by_date[day].append({
                    "dt":    dt,
                    "open":  float(row["Open"]),
                    "high":  float(row["High"]),
                    "low":   float(row["Low"]),
                    "close": float(row["Close"]),
                })
            except (ValueError, KeyError):
                continue
    # Sort each day's bars by time
    for day in by_date:
        by_date[day].sort(key=lambda b: b["dt"])
    return by_date

# ─────────────────────────────────────────────────────────────
# ANALYSIS 1: SDEV% from daily data
# Pine Script uses sdev_pct = 1.376 (1σ daily move %)
# ─────────────────────────────────────────────────────────────

def analyze_sdev(daily):
    print("\n" + "═" * 64)
    print("  ANALYSIS 1 — DAILY SDEV%  (validates sdev_pct in Pine Script)")
    print("═" * 64)

    returns = []
    for i in range(1, len(daily)):
        prev = daily[i-1]["close"]
        curr = daily[i]["close"]
        if prev > 0:
            returns.append((curr - prev) / prev * 100)

    # Compute SDEV over different rolling windows
    windows = [
        ("40yr (full)",   len(returns)),
        ("20yr",          252 * 20),
        ("10yr",          252 * 10),
        ("5yr",           252 * 5),
        ("2yr",           252 * 2),
        ("1yr",           252 * 1),
    ]

    results = {}
    for label, n in windows:
        if n > len(returns):
            n = len(returns)
        subset = returns[-n:]
        sd = stdev(subset)
        results[label] = sd
        coverage_68 = pct(sum(1 for r in subset if abs(r) <= sd), len(subset))
        coverage_2x = pct(sum(1 for r in subset if abs(r) <= 2*sd), len(subset))
        print(f"  {label:<14}  n={len(subset):>5}  SDEV={sd:.4f}%  "
              f"within±1σ={coverage_68:.0f}%  within±2σ={coverage_2x:.0f}%")

    # Distribution of daily moves
    r2 = returns[-252*2:]
    buckets = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    print(f"\n  Daily move distribution (2yr, n={len(r2)}):")
    for b in buckets:
        cnt = sum(1 for r in r2 if abs(r) <= b)
        print(f"    |move| ≤ {b:.1f}%:  {pct(cnt,len(r2)):.1f}%  {bar(pct(cnt,len(r2)))}")

    # PINE SCRIPT RECOMMENDATION
    sdev_1yr  = results.get("1yr",  results["40yr (full)"])
    sdev_5yr  = results.get("5yr",  results["40yr (full)"])
    sdev_10yr = results.get("10yr", results["40yr (full)"])
    recommended = round(sdev_5yr, 3)
    print(f"\n  Pine Script current:     sdev_pct = 1.376")
    print(f"  Recommended (5yr avg):   sdev_pct = {recommended:.3f}")
    if abs(recommended - 1.376) < 0.05:
        print(f"  ✓ Current value is within 5% of actual — no change needed")
    else:
        print(f"  ⚠ Difference = {abs(recommended - 1.376):.3f}pp — consider updating")
    return recommended

# ─────────────────────────────────────────────────────────────
# ANALYSIS 2: IB STATS from hourly data
# Pine Script claims: IB upper → H breaks 81%, IB lower → L breaks 74%
# ─────────────────────────────────────────────────────────────

def analyze_ib(hourly):
    print("\n" + "═" * 64)
    print("  ANALYSIS 2 — IB STATS  (validates 81% / 74% in Pine Script)")
    print("═" * 64)

    ib_upper_break_h = 0  # upper half, day H > IB H
    ib_upper_break_l = 0  # upper half, day L < IB L
    ib_upper_total   = 0

    ib_lower_break_h = 0  # lower half, day H > IB H
    ib_lower_break_l = 0  # lower half, day L < IB L
    ib_lower_total   = 0

    ib_upper_only_h  = 0  # upper half: ONLY H breaks (not L)
    ib_lower_only_l  = 0  # lower half: ONLY L breaks (not H)
    ib_upper_both    = 0  # upper half: both break
    ib_lower_both    = 0  # lower half: both break

    # Extension stats: how far does it go past IB high/low?
    ib_upper_ext_pts = []
    ib_lower_ext_pts = []

    for day, bars in hourly.items():
        if len(bars) < 2:
            continue

        ib_bar = bars[0]                  # 9:30-10:30 ET = IB hour
        rest   = bars[1:]                  # 10:30-16:00 ET

        ib_h   = ib_bar["high"]
        ib_l   = ib_bar["low"]
        ib_mid = (ib_h + ib_l) / 2
        ib_c   = ib_bar["close"]

        if ib_h == ib_l:
            continue  # degenerate bar

        # Post-IB range
        post_high = max(b["high"]  for b in rest)
        post_low  = min(b["low"]   for b in rest)

        broke_h = post_high > ib_h
        broke_l = post_low  < ib_l

        if ib_c > ib_mid:  # IB upper
            ib_upper_total += 1
            if broke_h:
                ib_upper_break_h += 1
                ib_upper_ext_pts.append(post_high - ib_h)
            if broke_l:
                ib_upper_break_l += 1
            if broke_h and broke_l:
                ib_upper_both += 1
            if broke_h and not broke_l:
                ib_upper_only_h += 1
        else:              # IB lower
            ib_lower_total += 1
            if broke_l:
                ib_lower_break_l += 1
                ib_lower_ext_pts.append(ib_l - post_low)
            if broke_h:
                ib_lower_break_h += 1
            if broke_h and broke_l:
                ib_lower_both += 1
            if broke_l and not broke_h:
                ib_lower_only_l += 1

    n_u = ib_upper_total
    n_l = ib_lower_total

    print(f"\n  IB Upper half  (n={n_u}):")
    print(f"    High breaks (post-IB):  {pct(ib_upper_break_h, n_u):.1f}%  {bar(pct(ib_upper_break_h,n_u))}")
    print(f"    Low  breaks (false):    {pct(ib_upper_break_l, n_u):.1f}%")
    print(f"    ONLY high breaks:       {pct(ib_upper_only_h,  n_u):.1f}%")
    print(f"    Both break:             {pct(ib_upper_both,    n_u):.1f}%")
    if ib_upper_ext_pts:
        ext = sorted(ib_upper_ext_pts)
        med = ext[len(ext)//2]
        print(f"    Median extension pts:   {med:.1f} pts  (mean={mean(ib_upper_ext_pts):.1f})")

    print(f"\n  IB Lower half  (n={n_l}):")
    print(f"    Low  breaks (post-IB):  {pct(ib_lower_break_l, n_l):.1f}%  {bar(pct(ib_lower_break_l,n_l))}")
    print(f"    High breaks (false):    {pct(ib_lower_break_h, n_l):.1f}%")
    print(f"    ONLY low  breaks:       {pct(ib_lower_only_l,  n_l):.1f}%")
    print(f"    Both break:             {pct(ib_lower_both,    n_l):.1f}%")
    if ib_lower_ext_pts:
        ext = sorted(ib_lower_ext_pts)
        med = ext[len(ext)//2]
        print(f"    Median extension pts:   {med:.1f} pts  (mean={mean(ib_lower_ext_pts):.1f})")

    print(f"\n  Pine Script claims: IB upper → H breaks 81%  |  IB lower → L breaks 74%")
    ub_actual = pct(ib_upper_break_h, n_u)
    lb_actual = pct(ib_lower_break_l, n_l)
    print(f"  Actual (2yr):       IB upper → H breaks {ub_actual:.1f}%  |  IB lower → L breaks {lb_actual:.1f}%")
    if abs(ub_actual - 81) < 5 and abs(lb_actual - 74) < 5:
        print(f"  ✓ Within ±5pp of hard-coded values — no change needed")
    else:
        print(f"  ⚠ Update Pine Script IB labels: upper={ub_actual:.0f}%  lower={lb_actual:.0f}%")
    return ub_actual, lb_actual

# ─────────────────────────────────────────────────────────────
# ANALYSIS 3: RTH FIRST HOUR CONTINUATION
# Pine Script claims: bull 9AM hour → 70% continuation
# Using hourly: first RTH bar (9:30-10:30) direction → session direction
# ─────────────────────────────────────────────────────────────

def analyze_rth_continuation(hourly):
    print("\n" + "═" * 64)
    print("  ANALYSIS 3 — RTH 1H CONTINUATION  (validates 70% in Pine Script)")
    print("═" * 64)

    bull_cont = 0; bull_total = 0
    bear_cont = 0; bear_total = 0

    # Deeper analysis: continuation to each subsequent hour
    by_hour = {1: {"bull": [0,0], "bear": [0,0]},
               2: {"bull": [0,0], "bear": [0,0]},
               3: {"bull": [0,0], "bear": [0,0]},
               4: {"bull": [0,0], "bear": [0,0]},
               5: {"bull": [0,0], "bear": [0,0]}}

    for day, bars in hourly.items():
        if len(bars) < 3:
            continue

        h0 = bars[0]  # 9:30-10:30 ET
        h0_bull = h0["close"] > h0["open"]
        h0_open = h0["open"]

        # Session direction = last bar close vs first bar open
        h_last = bars[-1]["close"]
        sess_bull = h_last > h0_open

        if h0_bull:
            bull_total += 1
            if sess_bull:
                bull_cont += 1
        else:
            bear_total += 1
            if not sess_bull:
                bear_cont += 1

        # Check continuation at each subsequent hour
        for i in range(1, 6):
            if i >= len(bars):
                break
            h_i   = bars[i]
            h_key = i
            if h0_bull:
                by_hour[h_key]["bull"][1] += 1
                if h_i["close"] > h0["close"]:
                    by_hour[h_key]["bull"][0] += 1
            else:
                by_hour[h_key]["bear"][1] += 1
                if h_i["close"] < h0["close"]:
                    by_hour[h_key]["bear"][0] += 1

    print(f"\n  First RTH hour (9:30-10:30 ET) → full session continuation:")
    print(f"    Bull 1H → bull session:  {pct(bull_cont, bull_total):.1f}%  (n={bull_total})  {bar(pct(bull_cont,bull_total))}")
    print(f"    Bear 1H → bear session:  {pct(bear_cont, bear_total):.1f}%  (n={bear_total})  {bar(pct(bear_cont,bear_total))}")

    print(f"\n  Hour-by-hour continuation after bull/bear first hour:")
    hour_labels = ["10:30-11:30", "11:30-12:30", "12:30-13:30", "13:30-14:30", "14:30-15:30"]
    for i in range(1, 6):
        d = by_hour[i]
        bp = pct(d["bull"][0], d["bull"][1]) if d["bull"][1] > 0 else 0
        ep = pct(d["bear"][0], d["bear"][1]) if d["bear"][1] > 0 else 0
        print(f"    {hour_labels[i-1]}  Bull→cont={bp:.0f}%  Bear→cont={ep:.0f}%")

    bull_act = pct(bull_cont, bull_total)
    bear_act = pct(bear_cont, bear_total)
    print(f"\n  Pine Script claims: 9AM continuation = 70% (both directions)")
    avg_cont = (bull_act + bear_act) / 2
    print(f"  Actual 1H cont (2yr): bull={bull_act:.1f}%  bear={bear_act:.1f}%  avg={avg_cont:.1f}%")
    if abs(avg_cont - 70) < 8:
        print(f"  ✓ Within ±8pp of 70% claim — value holds")
    else:
        print(f"  ⚠ Actual avg={avg_cont:.0f}% differs from claimed 70% — consider updating label")
    return bull_act, bear_act

# ─────────────────────────────────────────────────────────────
# ANALYSIS 4: DAY-OF-WEEK BIAS
# ─────────────────────────────────────────────────────────────

def analyze_dow(daily):
    print("\n" + "═" * 64)
    print("  ANALYSIS 4 — DAY-OF-WEEK BIAS")
    print("═" * 64)

    dow_names  = ["Mon", "Tue", "Wed", "Thu", "Fri"]
    dow_bull   = defaultdict(int)
    dow_total  = defaultdict(int)
    dow_ret    = defaultdict(list)

    for i in range(1, len(daily)):
        r    = (daily[i]["close"] - daily[i-1]["close"]) / daily[i-1]["close"] * 100
        dow  = daily[i]["date"].weekday()  # 0=Mon
        if dow > 4:
            continue
        dow_total[dow] += 1
        dow_ret[dow].append(r)
        if r > 0:
            dow_bull[dow] += 1

    print(f"\n  {'Day':<6} {'Bull%':>6} {'AvgRet':>8} {'SDEV':>8} {'n':>6}")
    print(f"  {'─'*6} {'─'*6} {'─'*8} {'─'*8} {'─'*6}")
    for d in range(5):
        n   = dow_total[d]
        b   = pct(dow_bull[d], n)
        avg = mean(dow_ret[d]) if dow_ret[d] else 0
        sd  = stdev(dow_ret[d]) if len(dow_ret[d]) > 1 else 0
        print(f"  {dow_names[d]:<6} {b:>5.1f}%  {avg:>+7.3f}%  {sd:>7.3f}%  {n:>6}")

# ─────────────────────────────────────────────────────────────
# ANALYSIS 5: MONTHLY SEASONALITY
# ─────────────────────────────────────────────────────────────

def analyze_monthly(daily):
    print("\n" + "═" * 64)
    print("  ANALYSIS 5 — MONTHLY SEASONALITY")
    print("═" * 64)

    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    mon_ret   = defaultdict(list)
    mon_bull  = defaultdict(int)
    mon_total = defaultdict(int)

    for i in range(1, len(daily)):
        r   = (daily[i]["close"] - daily[i-1]["close"]) / daily[i-1]["close"] * 100
        mon = daily[i]["date"].month - 1
        mon_ret[mon].append(r)
        mon_total[mon] += 1
        if r > 0:
            mon_bull[mon] += 1

    print(f"\n  {'Month':<6} {'Bull%':>6} {'AvgRet':>8} {'Pos Months':>12}")
    print(f"  {'─'*6} {'─'*6} {'─'*8} {'─'*12}")

    # Aggregate by calendar month
    mon_month_rets = defaultdict(list)
    by_year_month = defaultdict(list)
    for i in range(1, len(daily)):
        r   = (daily[i]["close"] - daily[i-1]["close"]) / daily[i-1]["close"] * 100
        ym  = (daily[i]["date"].year, daily[i]["date"].month)
        by_year_month[ym].append(r)

    for ym, rets in by_year_month.items():
        mon = ym[1] - 1
        mon_month_rets[mon].append(sum(rets))

    for m in range(12):
        n      = mon_total[m]
        bull_p = pct(mon_bull[m], n)
        avg    = mean(mon_ret[m]) if mon_ret[m] else 0
        mrets  = mon_month_rets[m]
        pos_m  = pct(sum(1 for r in mrets if r > 0), len(mrets)) if mrets else 0
        flag   = " ← strong" if pos_m >= 70 else " ← weak" if pos_m <= 40 else ""
        print(f"  {months[m]:<6} {bull_p:>5.1f}%  {avg:>+7.3f}%  {pos_m:>5.0f}% pos{flag}")

# ─────────────────────────────────────────────────────────────
# ANALYSIS 6: DAILY RANGE STATS (IB sizing context)
# ─────────────────────────────────────────────────────────────

def analyze_ranges(hourly):
    print("\n" + "═" * 64)
    print("  ANALYSIS 6 — DAILY RANGE & IB STATS (sizing context)")
    print("═" * 64)

    daily_ranges  = []
    ib_ranges     = []
    ib_range_pcts = []

    for day, bars in hourly.items():
        if len(bars) < 2:
            continue
        day_h = max(b["high"] for b in bars)
        day_l = min(b["low"]  for b in bars)
        day_range = day_h - day_l
        daily_ranges.append(day_range)

        h0 = bars[0]
        ib_range = h0["high"] - h0["low"]
        if day_range > 0:
            ib_ranges.append(ib_range)
            ib_range_pcts.append(ib_range / day_range * 100)

    def percentile(data, p):
        s = sorted(data)
        idx = int(len(s) * p / 100)
        return s[min(idx, len(s)-1)]

    if daily_ranges:
        print(f"\n  Daily Range (pts):")
        print(f"    Mean:   {mean(daily_ranges):.0f} pts")
        print(f"    Median: {percentile(daily_ranges,50):.0f} pts")
        print(f"    25th p: {percentile(daily_ranges,25):.0f} pts")
        print(f"    75th p: {percentile(daily_ranges,75):.0f} pts")
        print(f"    90th p: {percentile(daily_ranges,90):.0f} pts")

    if ib_ranges:
        print(f"\n  IB Range (pts, first 1H candle):")
        print(f"    Mean:   {mean(ib_ranges):.0f} pts")
        print(f"    Median: {percentile(ib_ranges,50):.0f} pts")
        print(f"    25th p: {percentile(ib_ranges,25):.0f} pts")
        print(f"    75th p: {percentile(ib_ranges,75):.0f} pts")

    if ib_range_pcts:
        print(f"\n  IB Range as % of Day Range:")
        print(f"    Mean:   {mean(ib_range_pcts):.0f}%")
        print(f"    Median: {percentile(ib_range_pcts,50):.0f}%")

# ─────────────────────────────────────────────────────────────
# SUMMARY: Pine Script UPDATES
# ─────────────────────────────────────────────────────────────

def print_summary(sdev_rec, ub_actual, lb_actual, bull_cont, bear_cont):
    print("\n" + "═" * 64)
    print("  PINE SCRIPT — SUGGESTED UPDATES")
    print("═" * 64)

    cont_avg = round((bull_cont + bear_cont) / 2)

    print(f"""
  ┌─────────────────────────────────────────────────────────┐
  │  Parameter           Current   Actual    Status         │
  ├─────────────────────────────────────────────────────────┤
  │  sdev_pct            1.376     {sdev_rec:.3f}    {"✓ OK" if abs(sdev_rec-1.376)<0.05 else "⚠ Update"}          │
  │  IB upper label      81%       {ub_actual:.0f}%       {"✓ OK" if abs(ub_actual-81)<5 else "⚠ Update"}          │
  │  IB lower label      74%       {lb_actual:.0f}%       {"✓ OK" if abs(lb_actual-74)<5 else "⚠ Update"}          │
  │  9AM continuation    70%       {cont_avg}%       {"✓ OK" if abs(cont_avg-70)<8 else "⚠ Update"}          │
  └─────────────────────────────────────────────────────────┘
""")
    if abs(sdev_rec - 1.376) >= 0.05:
        print(f"  UPDATE ny_open_edge_v4.pine:")
        print(f"    sdev_pct = input.float({sdev_rec:.3f}, ...")
    if abs(ub_actual - 81) >= 5:
        print(f"    IB upper label:  \"IB {ub_actual:.0f}%\"")
    if abs(lb_actual - 74) >= 5:
        print(f"    IB lower label:  \"IB {lb_actual:.0f}%\"")
    if abs(cont_avg - 70) >= 8:
        print(f"    9AM cont label:  \"9AM Bull/Bear {cont_avg}%\"")

# ─────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="NDX Statistical Analysis for NY Open Edge v4.1")
    parser.add_argument("--daily",  required=True, help="Path to NDX_daily_max.csv")
    parser.add_argument("--hourly", required=True, help="Path to NDX_hourly_2y.csv")
    args = parser.parse_args()

    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  NDX STATISTICAL ANALYSIS — NY Open Edge v4.1               ║")
    print("║  Validates hard-coded Pine Script parameters                 ║")
    print("╚══════════════════════════════════════════════════════════════╝")

    print(f"\nLoading daily data:  {args.daily}")
    daily = load_daily(args.daily)
    print(f"  → {len(daily)} daily bars  ({daily[0]['date']} → {daily[-1]['date']})")

    print(f"Loading hourly data: {args.hourly}")
    hourly = load_hourly(args.hourly)
    print(f"  → {len(hourly)} trading days  "
          f"({min(hourly.keys())} → {max(hourly.keys())})")

    # Run all analyses
    sdev_rec          = analyze_sdev(daily)
    ub_act, lb_act    = analyze_ib(hourly)
    bull_cont, bear_cont = analyze_rth_continuation(hourly)
    analyze_dow(daily)
    analyze_monthly(daily)
    analyze_ranges(hourly)
    print_summary(sdev_rec, ub_act, lb_act, bull_cont, bear_cont)

    print("\n  Run with actual data:")
    print("    python3 ndx_analysis.py \\")
    print("        --daily  /mnt/kimi/output/NDX_daily_max.csv \\")
    print("        --hourly /mnt/kimi/output/NDX_hourly_2y.csv\n")

if __name__ == "__main__":
    main()
