#!/usr/bin/env python3
"""Draw the asynchronous cached-packet protocol for Figure 3."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parent
OUTPUT_PDF = ROOT / "fig03_async_execution.pdf"
OUTPUT_PNG = ROOT / "fig03_async_execution.png"

INK = "#171717"
MUTED = "#657078"
REF = "#759EAD"
REF_PALE = "#DCE9ED"
OLD = "#92999D"
OLD_PALE = "#E4E5E3"
CREAM = "#F4EEDC"
FIELD = "#EAF1F3"


plt.rcParams.update({
    "font.family": "Courier New",
    "mathtext.fontset": "dejavusans",
})


def arrow(ax, x1, y1, x2, y2, color=INK, width=0.8):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=8,
        linewidth=width, color=color, shrinkA=0, shrinkB=0, zorder=2,
    ))


def rounded(ax, x, y, w, h, text, face, edge=MUTED, size=8.5):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.005,rounding_size=0.009",
        facecolor=face, edgecolor=edge, linewidth=0.8, zorder=3,
    ))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=size, color=INK, zorder=4)




def main():
    # Illustrative schedule in action-sample intervals, not measured latency.
    # Query timestamps, availability and chunk samples share one time axis.
    # Export close to the final single-column width to preserve label size.
    fig, ax = plt.subplots(figsize=(4.4,2.06))
    fig.subplots_adjust(left=.19,right=.99,top=.93,bottom=.16)
    ax.set(xlim=(-.1,9),ylim=(-.15,3.7)); ax.axis('off')
    def bar(a,b,y,txt,fill):
        ax.add_patch(Rectangle((a,y-.17),b-a,.34,facecolor=fill,edgecolor=MUTED,lw=.7,zorder=3))
        ax.text((a+b)/2,y,txt,ha='center',va='center',fontsize=7,zorder=4)
    for y,txt in [(3.2,'Base-action query'),(2.25,'Correction query'),(1.3,'Latest completed base action'),(.35,'Correction steps')]:
        ax.text(-.25,y,txt,ha='right',va='center',fontsize=8)
        ax.plot([0,8.7],[y,y],color=MUTED,lw=.6,zorder=0)
    bar(.8,3.5,3.2,r'$k$',CREAM); bar(4.2,7.8,3.2,r'$k+1$',CREAM)
    ax.text(.8,3.5,r'$t_k$',ha='center',fontsize=8)
    ax.text(3.5,3.5,r'$\bar t_k$: publish',ha='center',fontsize=8)
    ax.plot([3.5,3.5],[.02,3.38],color=REF,ls='--',lw=.8,zorder=1)
    bar(0,3.5,1.3,r'Base action $k-1$',OLD_PALE); bar(3.5,7.8,1.3,r'Base action $k$',REF_PALE)
    bar(7.8,8.7,1.3,r'$k+1$',CREAM)
    # Starts before publication retain base action k-1; a later query reads base action k.
    queries=[(0,.35,OLD_PALE,'query 1'),(2,2.4,OLD_PALE,'query 2'),(4.3,4.7,REF_PALE,'query 3')]
    for a,b,c,q in queries:
        bar(a,b,2.25,'',c)
        ax.text(a,2.59,q,fontsize=7.5,ha='center')
        ax.plot([b,b],[2.07,.55],color=MUTED,ls=':',lw=.7,zorder=1)
    # Latest completed query preempts the previous chunk; K=5, delta_t=1.
    for n,(a,b,c,q) in enumerate(queries):
        end=queries[n+1][1] if n+1<len(queries) else 8.7
        ax.text(b+.20,.80,q,fontsize=7.5,ha='left')
        ax.plot([b+.05,end-.05],[.65,.65],color=MUTED,lw=.7)
        for j in range(5):
            l=max(a+j,b); r=min(a+j+1,end,8.7)
            if r>l:
                bar(l,r,.35,str(j+1),c)
    ax.text(4.5,-.18,'Time →',fontsize=8,ha='center',va='top')
    for out in (OUTPUT_PDF,OUTPUT_PNG):
        fig.savefig(out,dpi=220,bbox_inches='tight',pad_inches=.03)
    plt.close(fig)

if __name__ == "__main__":
    main()
