"""
CASE GENERATOR — Verde Kitchen (ticker: VRDE), a fictional fast-casual chain.
DO NOT OPEN THIS FILE OR ANSWER_KEY.md UNTIL THE END. It contains the hidden
'truth' behind the data. Peeking ruins the exercise.

It writes four analyst-facing deliverables (the stuff a vendor would ship) plus
a sealed answer key.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(2026)
OUT = "/Users/biancarubbico/content-analyst-case/self_analysis_VRDE"

# 26 weekly periods: Q1 = weeks 1-13 (reported), Q2 = weeks 14-26 (just ended,
# earnings pending). One Monday per week starting early March 2026.
weeks = pd.date_range("2026-03-02", periods=26, freq="W-MON")
W = len(weeks)
t = np.arange(W)

def noise(scale, size=W):
    return rng.normal(1.0, scale, size)

# ---------------------------------------------------------------------------
# HIDDEN TRUTH baked into the numbers (she must discover this):
#  - Existing-customer cohort demand is SOFTENING: visit frequency of the
#    existing base declines ~0.5%/week; ticket roughly flat. This is the
#    same-store-sales (comp) tell, and it is rolling over.
#  - New-customer volume is BOOMING but only because of unit expansion (new
#    store openings), which the job-postings and app-download feeds corroborate.
#  - Headline panel spend still grows, so a lazy read says "fine". The quality
#    of that growth is deteriorating: comps decelerating, carried by new units.
#  - TRAP: at week 18 the data vendor onboards a new bank; panel coverage steps
#    up ~15%. Raw totals jump. Per-active-card metrics do not. Must normalize.
# ---------------------------------------------------------------------------

# EXISTING cohort (customers active at quarter start)
existing_cards_base = 8000 * noise(0.02)
existing_freq  = 0.95 * (0.9955 ** t) * noise(0.03)      # visits/card/week, DECELERATING
existing_ticket = 14.00 * (1.0008 ** t) * noise(0.015)   # $/visit, ~flat + tiny inflation

# NEW cohort (first-seen this window; grows as new stores open)
new_cards = (900 + 105 * t) * noise(0.04)                # rising: unit expansion
new_freq   = 0.80 * (1.0 ** t) * noise(0.04)             # steady
new_ticket = 13.50 * (1.0006 ** t) * noise(0.02)         # slightly below existing

# COVERAGE trap: vendor adds a bank at week 18 -> +15% panel size on counts & $.
coverage = np.ones(W)
coverage[17:] = 1.15

existing_cards = existing_cards_base * coverage
new_cards      = new_cards * coverage
existing_txns  = existing_cards * existing_freq
new_txns       = new_cards * new_freq
existing_spend = existing_txns * existing_ticket
new_spend      = new_txns * new_ticket

active_cards = np.round(existing_cards + new_cards).astype(int)
transactions = np.round(existing_txns + new_txns).astype(int)
total_spend  = (existing_spend + new_spend).round(2)
avg_ticket   = (total_spend / transactions).round(2)

card_panel = pd.DataFrame({
    "week_start": weeks.date,
    "fiscal_quarter": ["Q1"] * 13 + ["Q2"] * 13,
    "active_cards": active_cards,
    "transactions": transactions,
    "total_spend": total_spend,
    "avg_ticket": avg_ticket,
    "new_cust_cards": np.round(new_cards).astype(int),
    "new_cust_spend": new_spend.round(2),
    "new_cust_txns": np.round(new_txns).astype(int),
    "existing_cust_cards": np.round(existing_cards).astype(int),
    "existing_cust_spend": existing_spend.round(2),
    "existing_cust_txns": np.round(existing_txns).astype(int),
})
card_panel.to_csv(f"{OUT}/card_panel_weekly.csv", index=False)

# ---------------------------------------------------------------------------
# WEB / APP feed: downloads booming (acquisition), engagement per user softening.
# ---------------------------------------------------------------------------
web = pd.DataFrame({
    "week_start": weeks.date,
    "app_downloads": np.round((20000 + 950 * t) * noise(0.05)).astype(int),
    "weekly_active_users": np.round((310000 + 3200 * t) * noise(0.03)).astype(int),
    "sessions_per_wau": (3.40 * (0.9965 ** t) * noise(0.02)).round(2),
})
web.to_csv(f"{OUT}/web_app_weekly.csv", index=False)

# ---------------------------------------------------------------------------
# JOB POSTINGS feed: aggressive new-location hiring -> explains unit growth.
# ---------------------------------------------------------------------------
jobs = pd.DataFrame({
    "week_start": weeks.date,
    "total_job_postings": np.round((180 + 9 * t) * noise(0.06)).astype(int),
    "new_location_postings": np.round((40 + 3.2 * t) * noise(0.08)).astype(int),
})
jobs.to_csv(f"{OUT}/job_postings_weekly.csv", index=False)

# ---------------------------------------------------------------------------
# STREET CONTEXT: consensus, history, guidance, valuation.
# ---------------------------------------------------------------------------
street = """# VRDE — Street Context (as of the Q2 pre-earnings window)

## The company
Verde Kitchen (VRDE) — fast-casual Mediterranean chain. Growth stock; the bull
case is durable double-digit same-store sales (SSS / "comps") PLUS aggressive
new-unit growth. Trades at a premium multiple (~55x forward earnings) because
the market is paying for that comp+unit growth to persist.

## Consensus for Q2 (the just-ended quarter, reports in ~1 week)
- Revenue: $312M, +17% YoY
- Same-store sales (comps): +6.0% YoY
- Unit growth: +15% YoY (new stores)
- FY guide from management: full-year comps +5% to +7%

## Reported history (last 6 quarters)
| Quarter | Revenue | Rev YoY | Comps (SSS) | Stock reaction to print |
|---|---|---|---|---|
| Q4-24 | $228M | +26% | +13.5% | +6% |
| Q1-25 | $241M | +24% | +12.0% | +3% |
| Q2-25 | $255M | +22% | +10.5% | -2% (comp decel noticed) |
| Q3-25 | $270M | +20% | +9.0%  | +4% |
| Q4-25 | $289M | +19% | +8.0%  | -1% |
| Q1-26 | $301M | +18% | +7.0%  | -3% (guide seen as full) |

## What the market is debating
Bulls: unit growth runway is huge; comps decel is "normalization" and stabilizes
around mid-single digits (the +6% consensus).
Bears: comps have decelerated 6 quarters straight; at 55x, ANY comp miss or guide
cut de-rates the multiple hard. The whole debate is: where do comps actually land?
"""
with open(f"{OUT}/street_context.md", "w") as f:
    f.write(street)

# ---------------------------------------------------------------------------
# SEALED ANSWER KEY (do not open until the memo is written)
# ---------------------------------------------------------------------------
answer = """# ANSWER KEY — do not open until your memo is done

## What the data actually said
1. Headline panel spend kept rising, so a surface read says "fine."
2. DECOMPOSED: existing-cohort spend PER ACTIVE CARD was decelerating all
   quarter (frequency down ~0.5%/wk, ticket flat). That is the comp tell.
3. New-customer cards/spend boomed, but that is UNIT growth, corroborated by
   rising new-location job postings and app downloads. It props up the headline
   while masking softening same-store demand.
4. TRAP: at week 18 active_cards jumped ~15% (vendor added a bank). Raw total
   spend jumped with it. Per-active-card metrics did NOT. Anyone reading raw
   totals would wrongly see acceleration. Correct move: normalize per active
   card, and/or hold the existing cohort fixed.
5. Web feed confirms it: downloads up (acquisition) but sessions/user down
   (engagement softening) = same story as the card cohort.

## The true outcome (grade yourself against this)
Reported Q2: Revenue ~$309M (roughly in line; unit growth carried it) BUT
comps printed +2.4% vs +6.0% consensus, and management CUT the FY comp guide to
+2-4%. At 55x, the stock fell ~19% on the print.

## The tradable edge
The panel gave a leading read on the ONE metric the multiple hinges on (comps),
ahead of the print, and against a consensus that was too high. Edge = short/UW
or puts into the print. Why it exists: the market anchored on the headline and
unit story; the cohort deterioration was only visible if you decomposed the
panel AND corrected the coverage trap. That is differentiated, timely, and
not-yet-priced -> real edge.

## The main way to get this WRONG
Read headline panel spend, see it rising (amplified by the week-18 coverage
step), and conclude "demand accelerating, buy into the print." That is the trap.
"""
with open(f"{OUT}/ANSWER_KEY.md", "w") as f:
    f.write(answer)

print("Wrote:")
for fn in ["card_panel_weekly.csv", "web_app_weekly.csv", "job_postings_weekly.csv",
           "street_context.md", "ANSWER_KEY.md"]:
    print(" -", fn)
print(f"\ncard_panel: {card_panel.shape[0]} weeks x {card_panel.shape[1]} cols")
