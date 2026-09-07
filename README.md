# content-analyst-case

A self-built, **synthetic** training project for learning how hedge funds evaluate
**alternative data** and decide whether it can actually generate alpha. I built this
as a student to teach myself the workflow end to end, from a raw, messy dataset to an
investor memo and a trade.

Everything here is fake data I generated on purpose, so the "truth" is known and I can
grade my own analysis against it. No real company, no real data, nothing proprietary.

## What's inside

**The fundamentals — `level1_transactions.py`, `level2_revenue_signal.py`**
- **Level 1:** what a single row of a credit-card panel actually is.
- **Level 2:** turning a panel into a revenue signal and stress-testing it for the traps
  that fool people (panel drift, selection bias, thin coverage). Run it and read the
  printed lesson plus the chart it saves.

**The full case — `self_analysis_VRDE/`**
A fictional fast-casual stock ("Verde Kitchen") reporting earnings in a week. Four raw
vendor feeds: a card panel, web/app activity, job postings, and street context. The job
is to decide whether the data gives a tradable edge into the print. Start with
`MINDMAP.md` for the reasoning and `INVESTOR_MEMO.md` for the conclusion. The visuals
(`decomposition_map.png`, `mindmap_trace.png`) tell the story fast.

> Heads up: `ANSWER_KEY.md` and `_generate_case.py` hold the hidden "truth" behind the
> case. If you want to try the analysis yourself first, don't peek.

## Run it
```bash
pip install numpy pandas pyarrow matplotlib duckdb
python3 level2_revenue_signal.py
```

## Why
I'm learning this in public. If you want the write-up on what this exercise taught me
about the alternative-data industry, it's on my Substack (link in the post that brought
you here).
