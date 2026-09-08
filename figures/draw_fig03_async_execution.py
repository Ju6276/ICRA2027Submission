#!/usr/bin/env python3
"""Illustrative local timing around one reference publication, not a robot trace."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

ROOT = Path(__file__).resolve().parent
OLD = '#E1E4E6'
NEW = '#C4DDE8'
INK = '#202A30'
EDGE = '#687680'
# User-confirmed fast rate: 100 Hz. Illustrative compute time rounds the
# reported 2.43-ms mean; it is not a measured per-query latency trace.
STARTS = [-1.0, 9.0, 19.0]
COMPUTE_MS = 2.4
READY_MS = 0.0
LEFT, RIGHT = -8.0, 25.0


def reference_at_start(t):
    return 'Previous' if t < READY_MS else 'New'


def main():
    plt.rcParams.update({'font.family': 'Arial', 'mathtext.fontset': 'dejavusans'})
    fig, ax = plt.subplots(figsize=(3.45, 2.70))
    fig.subplots_adjust(left=.235, right=.98, top=.87, bottom=.23)
    ax.set(xlim=(LEFT, RIGHT), ylim=(-.35, 3.65))
    ax.axis('off')
    fig.text(.5, .975, 'One reference update · correction period: 10 ms',
             ha='center', va='top', fontsize=7.2, color=INK)

    def bar(a, b, y, text, color):
        ax.add_patch(Rectangle((a, y-.19), b-a, .38,
                              facecolor=color, edgecolor=EDGE, lw=.65, zorder=3))
        if text:
            ax.text((a+b)/2, y, text, ha='center', va='center',
                    fontsize=7, color=INK, zorder=4)

    lanes=[(3.2, 'Slow\ncomputation'), (2.3, 'Available\nreference'),
           (1.25, 'Fast\ncomputation'), (.15, 'Reference\nused in output')]
    for y, label in lanes:
        ax.text(LEFT-1, y, label, ha='right', va='center', fontsize=6.9, color=INK)
        if y != 3.2:
            ax.plot([LEFT,RIGHT],[y,y],color=EDGE,lw=.5,zorder=0)

    # The slow computation starts before this cropped time window.
    bar(LEFT, 0, 3.2, '', NEW)
    ax.text(-4, 3.52, '…', ha='center', fontsize=9, color=INK)
    ax.plot([0,0],[-.1,3.5],color='#39738F',lw=.85,ls='--',zorder=1)
    ax.scatter([0],[3.2],s=15,color='#39738F',zorder=5)
    ax.text(1.1,3.2,'New reference ready',ha='left',va='center',fontsize=7,color=INK)

    bar(LEFT,0,2.3,'Previous',OLD)
    bar(0,RIGHT,2.3,'New',NEW)

    ends=[start+COMPUTE_MS for start in STARTS]
    for i,(start,end) in enumerate(zip(STARTS,ends),1):
        ref=reference_at_start(start)
        color=OLD if ref=='Previous' else NEW
        bar(start,end,1.25,'',color)
        ax.text((start+end)/2,1.72,f'Update {i}',ha='center',fontsize=6.8,color=INK)
        # Circle: input/reference read. Square: result becomes available.
        ax.scatter([start],[1.25],s=12,facecolors='white',edgecolors=INK,lw=.65,zorder=5)
        ax.scatter([end],[1.25],s=10,marker='s',color=INK,zorder=5)
        ax.plot([end,end],[1.03,.36],color=EDGE,ls=':',lw=.7,zorder=1)

    # Display the reference used in composed commands, not chunk step indices.
    # Update 1 starts before publication and retains the previous reference;
    # the new reference first affects output when Update 2 finishes.
    switch=ends[1]
    bar(LEFT,switch,.15,'Previous',OLD)
    bar(switch,RIGHT,.15,'New',NEW)
    ax.annotate('',xy=(switch,.38),xytext=(switch,.87),
                arrowprops=dict(arrowstyle='-|>',color='#39738F',lw=.8))

    axis_y=-.29
    ax.plot([LEFT,RIGHT],[axis_y,axis_y],color=EDGE,lw=.65,clip_on=False)
    for t in [0,10,20]:
        ax.plot([t,t],[axis_y,axis_y-.07],color=EDGE,lw=.65,clip_on=False)
        ax.text(t,axis_y-.12,str(t),ha='center',va='top',fontsize=7,color=INK)
    fig.text(.61,.115,'Time relative to reference publication (ms)',ha='center',fontsize=6.4,color=INK)
    fig.text(.5,.047,'○ Read inputs / start     ■ Result ready',ha='center',fontsize=7,color=INK)
    for suffix in ['pdf','png']:
        fig.savefig(ROOT/f'fig03_async_execution.{suffix}',dpi=240,bbox_inches='tight',pad_inches=.035)
    plt.close(fig)


if __name__=='__main__':
    main()
