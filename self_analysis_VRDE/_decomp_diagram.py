import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

fig, ax = plt.subplots(figsize=(11.5, 9))
ax.set_xlim(0, 10); ax.set_ylim(0, 12); ax.axis("off")

def box(x, y, w, h, title, sub, fc, tc="black"):
    ax.add_patch(FancyBboxPatch((x - w/2, y - h/2), w, h,
                 boxstyle="round,pad=0.08,rounding_size=0.12",
                 fc=fc, ec="black", lw=1.6))
    ax.text(x, y + h*0.14, title, ha="center", va="center",
            fontsize=10.5, fontweight="bold", color=tc)
    if sub:
        ax.text(x, y - h*0.22, sub, ha="center", va="center",
                fontsize=8.2, color=tc, wrap=True)

def arrow(x1, y1, x2, y2, label="", lx=None, ly=None):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", lw=2, color="#333"))
    if label:
        ax.text(lx if lx is not None else (x1+x2)/2,
                ly if ly is not None else (y1+y2)/2,
                label, ha="center", va="center", fontsize=8.4,
                fontstyle="italic", color="#b1122c",
                bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))

ax.text(5, 11.6, "Reading spend like an analyst: peel it apart one force at a time",
        ha="center", fontsize=13, fontweight="bold")

# Level 0
box(5, 10.4, 6.2, 1.1, "TOTAL PANEL SPEND (raw)",
    "moves for 4 reasons you can't separate:\npanel size  ·  # customers  ·  how often  ·  how much", "#f4d06f")

# Step 1: cohort split
arrow(3.9, 9.85, 2.7, 8.95); arrow(6.1, 9.85, 7.3, 8.95)
ax.text(5, 9.55, "STEP 1  —  split by COHORT", ha="center", fontsize=8.6,
        fontstyle="italic", color="#b1122c",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))

box(2.7, 8.35, 3.6, 1.05, "EXISTING customers",
    "= SAME-STORE / comp demand\n(what the multiple is priced on)", "#8ecae6")
box(7.3, 8.35, 3.6, 1.05, "NEW customers",
    "= UNIT growth / acquisition\n(can prop up the headline)", "#c9c9c9")

# Step 2: divide by cards
arrow(2.7, 7.82, 2.7, 6.75, "STEP 2   ÷ active cards\n(kills panel size)", 4.35, 7.28)
box(2.7, 6.15, 3.9, 1.05, "SPEND PER CARD (existing)",
    "= value per customer\nimmune to panel getting bigger", "#95d5b2")

# Step 3: freq x ticket
arrow(2.7, 5.62, 1.9, 4.7); arrow(2.7, 5.62, 5.1, 4.7)
ax.text(3.5, 5.2, "STEP 3   = frequency  ×  ticket", ha="center", fontsize=8.6,
        fontstyle="italic", color="#b1122c",
        bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none"))

box(1.9, 4.1, 3.4, 1.15, "FREQUENCY = txns ÷ cards",
    "HOW OFTEN they come\n>> cleanest DEMAND / loyalty read\ncan't be faked by price or panel size", "#b7e4c7")
box(5.35, 4.1, 3.4, 1.15, "TICKET = spend ÷ txns",
    "HOW MUCH per visit\nprice + basket mix\ncould be inflation, not demand", "#ffd6a5")

# The identity banner
ax.add_patch(FancyBboxPatch((0.6, 2.35), 8.8, 0.85,
             boxstyle="round,pad=0.1,rounding_size=0.1", fc="#fff3b0", ec="#b1122c", lw=1.8))
ax.text(5, 2.78, "THE IDENTITY:   spend  =  cards  ×  frequency  ×  ticket",
        ha="center", fontsize=11.5, fontweight="bold", color="#b1122c")

# key takeaway
ax.text(5, 1.55, "So when a headline number rises, you ask: is it MORE CARDS,\n"
        "MORE VISITS, or HIGHER PRICES? Only 'more visits' is durable demand.",
        ha="center", fontsize=9.4)
ax.text(5, 0.55, "Rising spend-per-card from FREQUENCY = healthy   |   "
        "from TICKET only = leaning on price   |   from CARDS only = just adding doors",
        ha="center", fontsize=8.3, fontstyle="italic", color="#444")

fig.tight_layout()
fig.savefig("/Users/biancarubbico/content-analyst-case/self_analysis_VRDE/decomposition_map.png", dpi=145)
print("saved decomposition_map.png")
