"""
LEVEL 1 — The atom: raw transactions.

Big idea:
Alternative data (like a credit-card panel) does NOT arrive as "Chipotle made
$2.5B this quarter." It arrives as millions of tiny rows, each one a single
purchase by a single (anonymized) consumer at a single merchant on a single day.

Our job later is to turn a pile of these atoms into a number that tracks the
company's real revenue. But first: understand ONE row, and see a small pile.

To keep learning honest, we GENERATE the data ourselves. That means we secretly
know the "truth" and can later check whether our signal recovers it. In real
life you never get that luxury, which is exactly why evaluation is hard.
"""

import numpy as np
import pandas as pd

# A fixed seed makes the "random" data identical every run, so you can trace
# specific numbers and they won't move under you.
rng = np.random.default_rng(42)

# ----------------------------------------------------------------------------
# The panel: we only "see" a sample of consumers.
# A credit-card data vendor doesn't see everyone in America. They see the
# customers of a few banks / card issuers. Call that the PANEL.
# ----------------------------------------------------------------------------
N_CONSUMERS = 20          # tiny on purpose so you can eyeball every row
MERCHANT = "CHIPOTLE"

# Give each consumer an ID and a personal "how often do they eat here" rate.
# Some people are regulars, some are rare. This heterogeneity matters later
# (it's where "panel bias" comes from).
consumers = pd.DataFrame({
    "consumer_id": [f"C{i:03d}" for i in range(N_CONSUMERS)],
    # visits per week, drawn so most people are light users, a few are heavy
    "weekly_visit_rate": rng.gamma(shape=1.5, scale=0.8, size=N_CONSUMERS).round(2),
})

# ----------------------------------------------------------------------------
# Generate transactions for a 2-week window.
# For each consumer, each day, they may or may not buy. If they buy, they spend
# an amount drawn around a typical ticket size (~$12 burrito + drink).
# ----------------------------------------------------------------------------
DAYS = pd.date_range("2026-01-05", periods=14, freq="D")  # 2 weeks, Mon start

rows = []
for _, c in consumers.iterrows():
    daily_prob = c["weekly_visit_rate"] / 7.0   # convert weekly rate -> daily chance
    for day in DAYS:
        if rng.random() < daily_prob:           # did they buy today?
            amount = round(rng.normal(12.0, 3.0), 2)  # ticket size, ~$12 avg
            amount = max(amount, 3.0)            # no sub-$3 burritos
            rows.append({
                "date": day,
                "merchant": MERCHANT,
                "consumer_id": c["consumer_id"],
                "amount": amount,
            })

transactions = pd.DataFrame(rows)

# ----------------------------------------------------------------------------
# Look at the atom.
# ----------------------------------------------------------------------------
print("=" * 60)
print("ONE ROW = ONE PURCHASE. Here are the first 8:")
print("=" * 60)
print(transactions.head(8).to_string(index=False))

print()
print(f"Total transactions in the 2-week window: {len(transactions)}")
print(f"Total dollars spent (panel only):        ${transactions['amount'].sum():,.2f}")
print(f"Distinct consumers who bought at all:    {transactions['consumer_id'].nunique()} of {N_CONSUMERS}")

# Save so the next level can pick up exactly this data.
transactions.to_parquet("/Users/biancarubbico/content-analyst-case/transactions.parquet")
print("\nSaved -> transactions.parquet (Level 2 will read this)")
