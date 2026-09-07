"""
LEVEL 2 — From a pile of atoms to a revenue signal, and the harder question:
          IS THIS SIGNAL ACTUALLY VALUABLE?

Recap of Level 1:
    We made raw transactions. One row = one purchase by one anonymized consumer.
    We saved them to transactions.parquet. That taught us what the data IS.

The problem with Level 1 for EVALUATION:
    One merchant, two weeks, 20 people. You cannot tell if a signal is good from
    that. To judge a signal you need two things Level 1 did not have:
        1. TRUTH  - the real company revenue, so you can score yourself.
        2. TIME   - enough periods to measure GROWTH, because growth is the
                    thing PMs actually trade, not the dollar level.

So Level 2 builds a bigger toy world where WE control the truth:
    - a TRUE UNIVERSE of thousands of consumers = the whole market.
    - true company revenue = what ALL of them spend, month by month.
    - a PANEL = the slice of consumers the card vendor actually sees.
The vendor sells us the panel. Our job is to decide if the panel is worth buying.

The whole lesson lands on one idea:
    You almost never recover the true dollar LEVEL from a panel, and you do not
    need to. A panel is valuable when its GROWTH tracks the real growth. Level is
    biased and unknowable. Growth is tradable. Most of the traps below are ways
    the growth read gets silently corrupted.
"""

import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

CASE_DIR = "/Users/biancarubbico/content-analyst-case"

# ---------------------------------------------------------------------------
# 0. Nod to Level 1 so the levels connect. We read the atoms we saved before.
# ---------------------------------------------------------------------------
atoms = pd.read_parquet(f"{CASE_DIR}/transactions.parquet")
print("=" * 68)
print("LEVEL 1 HANDOFF: the atom pile we start from")
print("=" * 68)
print(f"{len(atoms)} raw purchases, {atoms['consumer_id'].nunique()} consumers, "
      f"1 merchant, {atoms['date'].nunique()} days.")
print("Too small and too short to JUDGE a signal. We scale up the toy world.\n")

# ---------------------------------------------------------------------------
# 1. THE TRUE UNIVERSE (the real world, which in real life you never see)
# ---------------------------------------------------------------------------
N_UNIVERSE = 5_000            # every Chipotle customer in our toy market
MONTHS = pd.date_range("2025-01-01", periods=18, freq="MS")  # 18 months
M = len(MONTHS)

# Each consumer has a personal frequency (heavy vs light user) and a personal
# average ticket. Heterogeneity is what makes panel SELECTION BIAS possible.
weekly_rate = rng.gamma(shape=1.5, scale=0.8, size=N_UNIVERSE)     # visits/week
ticket      = np.clip(rng.normal(12.0, 2.5, size=N_UNIVERSE), 5.0, None)  # $/visit

# The company's real demand path over 18 months. This is the thing a PM wants
# to predict BEFORE the earnings print. We bake in:
#   - a steady growth trend (the business is compounding)
#   - mild seasonality
#   - one nasty shock in month 10 (a food-safety scare) that lingers.
month_ix   = np.arange(M)
trend      = 1.015 ** month_ix                       # ~1.5% MoM underlying growth
seasonal   = 1 + 0.04 * np.sin(2 * np.pi * month_ix / 12)
shock      = np.ones(M)
shock[9]   = 0.82                                     # scare month: demand -18%
shock[10]  = 0.93                                     # partial recovery next month
demand     = trend * seasonal * shock                 # relative demand multiplier

# Simulate monthly visits for EVERY consumer, then dollars.
# lam = personal monthly visits, scaled by that month's demand multiplier.
weeks_per_month = 4.33
lam    = np.outer(weekly_rate * weeks_per_month, demand)   # shape (N_UNIVERSE, M)
visits = rng.poisson(lam)                                  # integer visit counts
spend  = visits * ticket[:, None]                          # dollars, per consumer/month

true_rev = spend.sum(axis=0)                               # THE TRUTH: total $/month
true_growth = pd.Series(true_rev).pct_change().to_numpy()  # MoM % change

# ---------------------------------------------------------------------------
# 2. THE PANEL (what the vendor actually sells you)
# ---------------------------------------------------------------------------
# Two realistic imperfections, both of which we deliberately build in:
#
#  (a) SELECTION BIAS: a card issuer's customers are not a random sample. Say
#      this panel skews toward heavy users. We sample consumers with probability
#      proportional to how often they eat out. This biases the LEVEL upward.
#
#  (b) PANEL DRIFT: the issuer keeps signing up new cardholders, so the panel
#      GROWS over time (coverage 70% -> 100% of the pool across 18 months).
#      This is the assassin. Raw panel dollars then rise partly because spending
#      rose and partly because the panel got bigger. If you do not correct it,
#      you will read fake growth and get run over.
POOL_SIZE = 400
p_select  = weekly_rate / weekly_rate.sum()               # heavy users favored
pool_idx  = rng.choice(N_UNIVERSE, size=POOL_SIZE, replace=False, p=p_select)

# Panel drift with a realistic DISCONTINUITY: the panel grows slowly, then the
# vendor onboards a whole new bank in month 6 and card count jumps ~35% overnight.
# That jump is pure panel mechanics, zero to do with real demand. It is exactly
# the event that fools people who read raw dollars.
coverage        = np.linspace(0.45, 0.52, M)              # slow organic panel growth
coverage[6:]   += 0.35                                    # month-6 bank onboarding jump
coverage        = np.clip(coverage, 0, 1.0)               # fraction of the pool that is live

naive_dollars = np.zeros(M)      # raw sum of panel spend (the trap)
active_cards  = np.zeros(M)      # how many panelists were "in" that month
for m in range(M):
    k = int(round(POOL_SIZE * coverage[m]))
    active = rng.permutation(pool_idx)[:k]                # which cards are live this month
    naive_dollars[m] = spend[active, m].sum()
    active_cards[m]  = k

# The fix for drift: dollars PER ACTIVE CARD. This strips out "more cards" and
# leaves "more spending per card", which is what tracks real demand.
normalized = naive_dollars / active_cards

naive_growth = pd.Series(naive_dollars).pct_change().to_numpy()
norm_growth  = pd.Series(normalized).pct_change().to_numpy()

# ---------------------------------------------------------------------------
# 3. SCORE THE SIGNAL against the truth we secretly know.
#    We score GROWTH, not level, because growth is the tradable object.
# ---------------------------------------------------------------------------
def corr(a, b):
    a, b = a[1:], b[1:]                                   # drop first NaN growth
    return float(np.corrcoef(a, b)[0, 1])

def rmse_growth(sig_growth):
    a = true_growth[1:]
    b = sig_growth[1:]
    return float(np.sqrt(np.mean((a - b) ** 2)))

print("=" * 68)
print("DOES THE PANEL RECOVER THE TRUTH?")
print("=" * 68)

# Level bias: panel spend-per-card vs true spend-per-capita. Expect > 1 because
# we oversampled heavy users. Point: the LEVEL is biased and basically useless.
true_per_capita = true_rev / N_UNIVERSE
level_bias = (normalized / true_per_capita).mean()
print(f"Level bias (panel $/card vs true $/capita): {level_bias:5.2f}x")
print("  -> The dollar LEVEL is inflated by heavy-user selection. Do not trust level.\n")

print("Growth tracking (correlation of monthly % change vs TRUE % change):")
print(f"  RAW panel dollars   vs truth : corr = {corr(naive_growth, true_growth):+.2f}"
      f"   (contaminated by panel drift)")
print(f"  NORMALIZED per-card vs truth : corr = {corr(norm_growth,  true_growth):+.2f}"
      f"   (drift removed)")
print(f"  RAW  growth RMSE  = {rmse_growth(naive_growth):.3f}")
print(f"  NORM growth RMSE  = {rmse_growth(norm_growth):.3f}")
print("  -> Same raw data, but normalizing for panel drift is the difference")
print("     between a tradable signal and a misleading one.\n")

# Did the signal SEE the shock? A PM cares most about catching turns.
shock_true = true_growth[9]
shock_norm = norm_growth[9]
print(f"The month-10 food-safety shock: true MoM {shock_true:+.1%}, "
      f"panel(normalized) MoM {shock_norm:+.1%}")
print("  -> A good signal flags the turn in the same direction, same ballpark.\n")

# ---------------------------------------------------------------------------
# 4. COVERAGE / BREADTH: does a bigger panel track better? (the 'breadth' box)
#    Rebuild the normalized signal at several panel sizes and score each.
# ---------------------------------------------------------------------------
print("=" * 68)
print("COVERAGE TEST: bigger panel = tighter tracking?")
print("=" * 68)
print(f"{'panel size':>10} | {'growth corr vs truth':>22} | {'growth RMSE':>12}")
print("-" * 50)
for size in [50, 100, 200, 400, 800]:
    idx = rng.choice(N_UNIVERSE, size=size, replace=False, p=p_select)
    # keep drift so this is apples-to-apples, then normalize it out
    dol = np.zeros(M); crd = np.zeros(M)
    for m in range(M):
        k = int(round(size * coverage[m]))
        act = rng.permutation(idx)[:k]
        dol[m] = spend[act, m].sum(); crd[m] = k
    g = pd.Series(dol / crd).pct_change().to_numpy()
    print(f"{size:>10} | {corr(g, true_growth):>+22.2f} | {rmse_growth(g):>12.3f}")
print("  -> Thin panels are noisy. A 3-name signal is a curiosity; breadth is what")
print("     turns it into something a PM can actually size into.\n")

# ---------------------------------------------------------------------------
# 5. Chart it, because the picture is the pitch.
# ---------------------------------------------------------------------------
try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    x = MONTHS[1:]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x, true_growth[1:] * 100, "k-", lw=2.4, label="TRUE revenue growth")
    ax.plot(x, naive_growth[1:] * 100, "r--", lw=1.6, label="Raw panel $ (drift trap)")
    ax.plot(x, norm_growth[1:] * 100, "b-", lw=1.6, label="Normalized panel (per card)")
    ax.axhline(0, color="0.7", lw=0.8)
    ax.set_title("Panel revenue signal vs the truth  (MoM % growth)")
    ax.set_ylabel("month-over-month growth, %")
    ax.legend(loc="lower left", fontsize=9)
    fig.autofmt_xdate()
    fig.tight_layout()
    out = f"{CASE_DIR}/level2_signal_vs_truth.png"
    fig.savefig(out, dpi=130)
    print(f"Saved chart -> {out}")
except Exception as e:
    print(f"(chart skipped: {e})")

# ---------------------------------------------------------------------------
# 6. THE VERDICT you would write in an evaluation memo.
# ---------------------------------------------------------------------------
print("\n" + "=" * 68)
print("THE MEMO: is this dataset worth buying?")
print("=" * 68)
print("""
WHAT IT IS   : anonymized card-panel transactions, one merchant, monthly.
PREDICTS     : direction and rough magnitude of revenue GROWTH ahead of the
               print. Recovers the shock and the trend once cleaned.
LEVEL        : NOT usable. Heavy-user selection inflates the dollar level; only
               growth is trustworthy.
KEY RISK #1  : PANEL DRIFT. Raw dollars conflate 'more spending' with 'more
               cards'. Must normalize per active card or the signal lies.
KEY RISK #2  : BREADTH. Small panels are too noisy to size. Confirm coverage of
               the PM's actual tickers before paying.
STILL OPEN   : latency (how many days after the month does data land?), point-in-
               time history for a real backtest, capacity/decay if everyone buys
               it, and compliance/provenance (consent, PII) which is a GATE.
RECOMMENDATION: worth a paid trial IF (a) coverage hits our names, (b) they can
               deliver point-in-time history to backtest, and (c) provenance is
               clean. Price it against expected P&L, not against 'it feels cool'.
""")
