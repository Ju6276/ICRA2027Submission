#!/usr/bin/env python3
"""Three deployment lanes with timestamp-derived reference binding and steps.

Horizontal positions are schematic multiples of the action-sample interval.
The teacher lane shows a visible segment of one longer reference chunk.
Student sequences show K-step predictions; dark portions are selected.
The bottom lane shows pose-action steps, not individual 100 Hz transmissions.
"""
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from figure_palette import (
    INK, EDGE, REFERENCE, REFERENCE_EDGE,
    JOINT_CORRECTION, JOINT_CORRECTION_EDGE, COMMAND,
)

OUT = Path(__file__).resolve().parent / 'fig03_async_execution'
K = 5
WINDOW_END = 7.4
REFERENCES = [dict(index=0, start=-7, ready=-.2)]
QUERIES = [
    dict(start=0., ready=.3, y=65),
    dict(start=2.4, ready=2.7, y=43),
]


def reference_at(t):
    return max((r for r in REFERENCES if r['ready'] <= t),
               key=lambda r: r['start'])['index']


def query_at(t):
    return max((q for q in QUERIES
                if q['ready'] <= t < q['start'] + K),
               key=lambda q: q['start'])


for i, q in enumerate(QUERIES):
    q['reference'] = reference_at(q['start'])
    q['selected_start'] = q['ready']
    q['selected_end'] = min(
        QUERIES[i + 1]['ready'] if i + 1 < len(QUERIES) else WINDOW_END,
        q['start'] + K,
    )

# Both independent student updates reuse one completed reference. The next
# student query starts before its result can replace the current result.
assert [q['reference'] for q in QUERIES] == [0, 0]
assert query_at(2.5) is QUERIES[0]
assert query_at(2.8) is QUERIES[1]

# Intersect each predicted sample interval with that query's selected interval.
selected_steps = []
for q in QUERIES:
    for j in range(K):
        a = max(q['start'] + j, q['selected_start'])
        b = min(q['start'] + j + 1, q['selected_end'])
        if a < b:
            assert query_at((a + b) / 2) is q
            selected_steps.append((a, b, q, j + 1))
assert all(abs(a[1] - b[0]) < 1e-8
           for a, b in zip(selected_steps, selected_steps[1:]))

plt.rcParams.update({
    'font.family': 'Times New Roman',
    'mathtext.fontset': 'stix',
    'svg.fonttype': 'none',
})
fig, ax = plt.subplots(figsize=(7.2, 2.55))
fig.subplots_adjust(left=.015, right=.985, top=.965, bottom=.045)
ax.set(xlim=(-2.9, 8.65), ylim=(-16, 116))
ax.axis('off')


def text(x, y, label, size=14, color=INK, ha='left'):
    ax.text(x, y, label, fontsize=size, color=color, ha=ha,
            va='center', zorder=8)


def step(a, b, y, color, alpha=1, height=7, zorder=3):
    """A separated action-step mark, without shared cell borders."""
    gap = min(.075, (b-a)*.12)
    ax.add_patch(FancyBboxPatch(
        (a+gap, y-height/2), b-a-2*gap, height,
        boxstyle='round,pad=0,rounding_size=.07',
        mutation_aspect=9, facecolor=color, edgecolor='none',
        alpha=alpha, zorder=zorder,
    ))


def arrow(x1, y1, x2, y2, color=EDGE):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>',
                                mutation_scale=7, lw=.7, color=color,
                                shrinkA=0, shrinkB=0, zorder=5))


# Three row labels, with the student updates grouped within one lane.
text(-.55, 97, 'Slow teacher', ha='right')
text(-.55, 85, r'$A_k^{\mathrm{ref}}$', size=15, color=REFERENCE_EDGE, ha='right')
text(-.55, 59, 'Fast student', ha='right')
text(-.55, 45, r'$\Delta\hat A^{\mathrm{force}}+\Delta\hat A^{\mathrm{delay}}$',
     size=13, color=JOINT_CORRECTION_EDGE, ha='right')
text(-.55, 12, 'Execution', ha='right')
text(-.55, -1, r'$\mathcal{P}(A^{\mathrm{cmd}})$', size=14, ha='right')

# A compact key makes the selection visible without splitting force and delay.
step(4.0, 4.4, 110, JOINT_CORRECTION, height=5)
text(4.5, 110, 'Selected', size=12, color=EDGE)
step(6.25, 6.65, 110, JOINT_CORRECTION, alpha=.16, height=5)
text(6.75, 110, 'Unused', size=12, color=EDGE)

# A cropped sequence of discrete reference samples, with continuation marks.
# Its original sample grid differs from the second student's query grid;
# reference poses are interpolated at correction timestamps during composition.
assert abs(REFERENCES[0]['start']-round(REFERENCES[0]['start'])) < 1e-8
for j in range(8):
    step(j, j+1, 92, REFERENCE, height=9)
text(-.15, 92, r'$\cdots$', size=12, color=REFERENCE_EDGE, ha='right')
text(8.1, 92, r'$\cdots$', size=12, color=REFERENCE_EDGE)

# One color denotes the joint pose adjustment, matching Fig. 1's correction
# arrows. Force and delay remain separately predicted and bounded in the method.
# Faint portions show predicted steps that are not selected for execution.
for q in QUERIES:
    y = q['y']
    for j in range(K):
        x = q['start'] + j
        step(x, x+1, y, JOINT_CORRECTION, alpha=.16)
        a = max(x, q['selected_start'])
        b = min(x+1, q['selected_end'])
        if a < b:
            step(a, b, y, JOINT_CORRECTION, zorder=4)

# Only selected valid steps reach the bottom lane. Inference and preemption
# can shorten a step; a full K-step chunk is not assumed to execute.
for a, b, q, j in selected_steps:
    step(a, b, 10, COMMAND, height=9)

# Short vertical links map each selected interval to its executed action steps.
for q in QUERIES:
    mid=(q['selected_start']+q['selected_end'])/2
    arrow(mid,q['y']-6,mid,19,color=JOINT_CORRECTION_EDGE)

# Show where the newer completed result replaces the earlier result.
for q in QUERIES[1:]:
    x = q['selected_start']
    ax.plot([x, x], [3, 17], color=EDGE, lw=.7, zorder=5)
text(.3, -5, 'Reference + corrections', size=11.5, color=EDGE)
arrow(6.25, -5, 7.4, -5)
text(6.1, -5, 'Time', size=11.5, color=EDGE, ha='right')

for suffix in ['.svg', '.pdf', '.png']:
    fig.savefig(OUT.with_suffix(suffix), dpi=240, facecolor='white')
plt.close(fig)
svg_path = OUT.with_suffix('.svg')
svg_path.write_text('\n'.join(line.rstrip() for line in svg_path.read_text().splitlines()) + '\n')
