import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import numpy as np

fig, ax = plt.subplots(figsize=(14, 9)); ax.set_xlim(0,14); ax.set_ylim(0,9); ax.axis("off")

def node(x,y,w,h,title,bullets,fc,ts=10,bs=7.8):
    ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle="round,pad=0.1,rounding_size=0.12",
                fc=fc,ec="#222",lw=1.6))
    ax.text(x,y+h/2-0.28,title,ha="center",va="top",fontsize=ts,fontweight="bold")
    ax.text(x,y+h/2-0.62,"\n".join(bullets),ha="center",va="top",fontsize=bs,color="#222")

# center
node(7,4.5,3.0,1.2,"VRDE",["Edge into the","Q2 print?"],"#ffd166",ts=13,bs=9)

branches = [
 (7,7.8,"1 · WHAT it is",["card panel (cohort-split)","+ web/app + jobs + street","panel = sample, no geo"],"#f4a3a3"),
 (12.2,6.0,"2 · WHAT it means",["existing FREQUENCY","0.927 -> 0.896 (-3.4%)","same-store demand softening"],"#a3d5f4"),
 (12.2,3.0,"3 · CONNECTIONS",["app engagement down too","(orthogonal confirm)","jobs: growth = new units"],"#a8e6a3"),
 (2.0,6.0,"4 · PATTERN",["premium growth stock;","expansion masks a","decelerating core"],"#c9b3f0"),
 (2.0,3.0,"5 · EDGE + TRADE",["short via puts into print","catalyst: comps miss +6%","risk #1: already priced"],"#f7c59f"),
]
for x,y,t,b,c in branches:
    ax.annotate("",xy=(x,y),xytext=(7,4.5),arrowprops=dict(arrowstyle="-",lw=1.8,color="#888"))
for x,y,t,b,c in branches:
    node(x,y,3.4,1.5,t,b,c)

ax.text(7,0.5,"delivered comps < priced-in comps  =  the edge   |   compliance (provenance/consent/licensing) is a GATE, not a score",
        ha="center",fontsize=9,fontstyle="italic",color="#b1122c")
ax.text(7,8.7,"VRDE alt-data analysis — reasoning trace",ha="center",fontsize=13,fontweight="bold")
fig.tight_layout()
fig.savefig("/Users/biancarubbico/content-analyst-case/self_analysis_VRDE/mindmap_trace.png",dpi=145)
print("saved mindmap_trace.png")
