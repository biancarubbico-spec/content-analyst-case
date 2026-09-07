"""
LEVEL 3 data generator — a UNIVERSE of tickers, too big to eyeball.

15 fictional consumer tickers x ~2 quarters of DAILY data x 4 regions.
Each ticker has a hidden 'comp trajectory' (existing-customer frequency slope):
some decelerating (the ones you must CATCH), some stable, some accelerating.
One ticker also has a mid-series panel-coverage jump (the trap from Level 2).

You never read this file to do the exercise; you QUERY the output.
"""
import numpy as np, pandas as pd
rng = np.random.default_rng(11)
OUT = "/Users/biancarubbico/content-analyst-case/level3_sifting"

dates   = pd.date_range("2026-03-02", periods=182, freq="D")   # 26 weeks, daily
regions = ["NORTHEAST", "SOUTHEAST", "MIDWEST", "WEST"]

# ticker -> (base_weekly_freq, freq_slope_per_day, has_coverage_jump)
# slope < 0 = decelerating comps (catch these); ~0 stable; > 0 accelerating
tickers = {
    "VRDE": (0.95, -0.0009, False),   # decelerating (our case company)
    "BRGR": (0.80, -0.0011, False),   # decelerating hard
    "CAFE": (1.20, -0.0006, True),    # decelerating + COVERAGE JUMP trap
    "PIZZ": (0.70, -0.0008, False),   # decelerating
    "SUSH": (0.55,  0.0000, False),   # stable
    "TACO": (1.10,  0.0002, False),   # stable/slightly up
    "WOKS": (0.60,  0.0009, False),   # accelerating
    "GRLL": (0.85,  0.0006, False),   # accelerating
    "SALD": (0.90, -0.0002, False),   # mild decel
    "DELI": (0.75,  0.0001, False),   # stable
    "BOWL": (1.00,  0.0011, False),   # accelerating hard
    "FRYZ": (0.65, -0.0010, False),   # decelerating
    "NOOD": (0.80,  0.0003, False),   # stable/up
    "CHIK": (1.30, -0.0004, False),   # mild decel, big name
    "SMTH": (0.50,  0.0007, False),   # accelerating
}

rows = []
for tkr, (base_freq, slope, jump) in tickers.items():
    tk_new_growth = rng.uniform(3, 9)         # new cards added per day (unit growth)
    tk_ticket     = rng.uniform(9, 18)        # avg $/visit for this brand
    ex_cards_base = rng.uniform(1500, 6000)   # existing base size (panel)
    for d_i, day in enumerate(dates):
        cov = 1.0
        if jump and d_i >= 100:               # coverage step for the trap ticker
            cov = 1.18
        freq_today = (base_freq/7.0) * (1 + slope*d_i)   # daily freq, drifting
        for reg in regions:
            reg_mult = {"NORTHEAST":1.0,"SOUTHEAST":0.9,"MIDWEST":0.8,"WEST":1.1}[reg]
            ex_cards = ex_cards_base * reg_mult * cov * rng.normal(1, 0.05)
            ex_txns  = ex_cards * freq_today * rng.normal(1, 0.06)
            ex_spend = ex_txns * tk_ticket * rng.normal(1, 0.03)
            new_cards = (200 + tk_new_growth*d_i) * reg_mult * cov * rng.normal(1, 0.08)
            new_txns  = new_cards * 0.8/7.0 * rng.normal(1, 0.08)
            new_spend = new_txns * tk_ticket*0.95 * rng.normal(1, 0.04)
            rows.append((day.date(), tkr, reg,
                         int(ex_cards), int(ex_txns), round(ex_spend,2),
                         int(new_cards), int(new_txns), round(new_spend,2)))

df = pd.DataFrame(rows, columns=[
    "date","ticker","region","existing_cards","existing_txns","existing_spend",
    "new_cards","new_txns","new_spend"])
df.to_parquet(f"{OUT}/universe_panel.parquet", index=False)
df.to_csv(f"{OUT}/universe_panel.csv", index=False)
print(f"rows: {len(df):,}   tickers: {df.ticker.nunique()}   "
      f"days: {df.date.nunique()}   regions: {df.region.nunique()}")
print("saved universe_panel.parquet + .csv")
