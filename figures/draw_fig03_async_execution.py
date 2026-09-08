#!/usr/bin/env python3
"""Schematic execution events, with reference binding derived from query starts."""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

from figure_palette import INK, EDGE, REFERENCE_EDGE

OUT = Path(__file__).resolve().parent / 'fig03_async_execution'
OLD_FILL, OLD_EDGE = '#E9EDF0', '#8597A1'
NEW_FILL, NEW_EDGE = '#BCD8E5', REFERENCE_EDGE
PALETTE = {0: (OLD_FILL, OLD_EDGE), 1: (NEW_FILL, NEW_EDGE)}

# These are schematic event positions, not an experimental timing trace.
# Reference 0 and an earlier correction are already available at the left edge.
REFERENCES = [dict(key=0,start=-180,end=-130), dict(key=1,start=0,end=45)]
QUERIES = [dict(start=-20,end=-10),dict(start=2,end=12),dict(start=17,end=27),
           dict(start=32,end=52),dict(start=58,end=78)]
COMMAND_TIMES = list(range(0,100,10))


def reference_at(t):
    return max((r for r in REFERENCES if r['end'] <= t),key=lambda r:r['start'])['key']


for query in QUERIES:
    query['reference'] = reference_at(query['start'])


def correction_at(t):
    return max((q for q in QUERIES if q['end'] <= t),key=lambda q:q['start'])


# The old-reference correction straddles availability; adoption and command
# selection must follow their own event times rather than a shared vertical line.
assert QUERIES[-2]['start'] < REFERENCES[1]['end'] < QUERIES[-2]['end']
assert QUERIES[-2]['reference'] == 0 and QUERIES[-1]['reference'] == 1
assert correction_at(50)['start'] == 17
assert correction_at(60) is QUERIES[-2]
assert correction_at(80) is QUERIES[-1]

plt.rcParams.update({'font.family':'Times New Roman', 'mathtext.fontset':'stix', 'svg.fonttype':'none'})
fig,ax = plt.subplots(figsize=(7.2,2.65))
fig.subplots_adjust(left=.025,right=.975,top=.97,bottom=.04)
ax.set(xlim=(-2,106),ylim=(-5,67))
ax.axis('off')


def text(x,y,label,size=13,color=INK,ha='left',weight='normal'):
    ax.text(x,y,label,fontsize=size,color=color,ha=ha,va='center',fontweight=weight,zorder=6)


def block(x,y,w,h,fill,edge=None,lw=.7):
    ax.add_patch(Rectangle((x,y),w,h,facecolor=fill,edgecolor=edge or 'none',lw=lw,zorder=3))


def arrow(x1,y1,x2,y2,color=EDGE):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle='-|>',mutation_scale=8,
                                lw=.85,color=color,shrinkA=0,shrinkB=1,zorder=5))


def bracket(left,right,y,label,color):
    ax.plot([left,left,right,right],[y+1.5,y,y,y+1.5],color=color,lw=.8,zorder=4)
    text((left+right)/2,y-4,label,size=13,color=color,ha='center')


# Reference computation is a single interval above the main action sequence.
ready = REFERENCES[1]['end']
block(0,52,ready,4,'#F0F3F5',NEW_EDGE,lw=.65)
text(ready/2,62,'Reference inference',size=13.5,ha='center')
ax.plot([ready,ready],[56,29],color=EDGE,lw=.8,linestyle=(0,(3,3)),zorder=2)
text(ready+2,54,'Ready',size=12.5,color=NEW_EDGE)

# Short intervals remain separate from the denser, continuous control stream.
text(0,43,'Correction inference',size=13.5)
for query in QUERIES[1:]:
    fill,edge=PALETTE[query['reference']]
    block(query['start'],31,query['end']-query['start'],5.5,fill,edge)

# Only the two queries relevant to the handover are connected to execution.
for query in QUERIES[-2:]:
    first_command=next(t for t in COMMAND_TIMES if correction_at(t) is query)
    arrow(query['end'],30.5,first_command,18,PALETTE[query['reference']][1])

# This is the visual center of the figure: actual command transmissions.
text(0,22,'Robot commands · 100 Hz',size=13)
for t in COMMAND_TIMES:
    fill,edge=PALETTE[correction_at(t)['reference']]
    block(t,9,10,8,fill,INK,lw=.55)

first_new=next(t for t in COMMAND_TIMES if correction_at(t)['reference']==1)
bracket(.5,first_new-.5,5,'Current reference',OLD_EDGE)
bracket(first_new+.5,99.5,5,'New reference',NEW_EDGE)
arrow(100.8,13,105.5,13)
text(105,23,'Time',size=11.5,ha='right',color=EDGE)
text(0,-4,'Schematic timing',size=10.5,color=EDGE)

for suffix in ['.svg','.pdf','.png']:
    fig.savefig(OUT.with_suffix(suffix),dpi=240,facecolor='white')
plt.close(fig)
svg_path=OUT.with_suffix('.svg')
svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text().splitlines())+'\n')
