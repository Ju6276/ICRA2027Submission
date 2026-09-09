"""Fig. 2: teacher-defined correction targets and correction-policy training.

Run this script to regenerate the manuscript PDF, PNG, and editable SVG.
Optional input thumbnails are loaded from figures/inputs/; missing assets use
illustrative placeholders.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Circle
from PIL import Image

OUT = Path(__file__).resolve().parent
PAPER = OUT.parent
from figure_palette import (
    snowflake_segments, FORCE, DELAY, REFERENCE,
    FORCE_EDGE, DELAY_EDGE, REFERENCE_EDGE, STUDENT_FILL, STUDENT_ACCENT,
)

# Pastel palette inspired by the user's reference figure. Pale blue marks
# visual-language/context modules, green the teacher action expert, yellow
# force modules/targets, lavender delay targets, and peach shared attention.
# Dark text and outlines preserve contrast; data-flow and symbols are unchanged.
INK = '#202020'
EDGE = '#383838'
NEUTRAL = '#FFFFFF'
NEUTRAL_STROKE = '#555555'
VLM_MODULE = '#DEEBF7'
CONTEXT_TOKEN = '#BDD7EE'
ACTION_MODULE = '#E2EFDA'
ACTION_INNER = '#C6E0B4'
FORCE_MODULE = '#FFF2CC'
DELAY_MODULE = '#EEEAF4'
GENERIC_MODULE = '#F2F2F2'
SHARED_ACCENT = STUDENT_ACCENT
SHARED_FILL = STUDENT_FILL
SHARED_EDGE = EDGE

plt.rcParams.update({
    'font.family': 'Arial',
    'mathtext.fontset': 'stix',
    'svg.fonttype': 'none',
})
fig = plt.figure(figsize=(18, 11.18), facecolor='white')
ax = fig.add_axes([0, 0, 1, 1])
ax.set(xlim=(0, 1800), ylim=(1210, 92))
ax.axis('off')
QUIET = '#595959'
RULE = '#BDBDBD'


def text(x, y, s, size=19, color=INK, ha='left', weight='normal', z=8):
    ax.text(x, y, s, fontsize=size, color=color, ha=ha, va='center',
            weight=weight, zorder=z)


def panel(x, y, w, h, face='white', edge='none', radius=8, lw=1, z=1):
    p = FancyBboxPatch((x, y), w, h,
                      boxstyle=f'round,pad=0,rounding_size={radius}',
                      facecolor=face, edgecolor=edge, lw=lw, zorder=z)
    ax.add_patch(p)
    return p


def line(points, color=EDGE, lw=1.2, dash=False, z=3):
    ax.plot(*zip(*points), color=color, lw=lw,
            linestyle=(0, (3, 3)) if dash else '-',
            solid_capstyle='round', solid_joinstyle='round', zorder=z)


def arrow(a, b, color=EDGE, lw=1.3, scale=10, z=4, dash=False):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=scale,
                                color=color, lw=lw, shrinkA=0, shrinkB=0,
                                linestyle=(0, (4, 3)) if dash else '-',
                                zorder=z))


def snowflake(x, y, r=10):
    for pts in snowflake_segments(x, y, r):
        line(pts, lw=1.3, z=5)


def sequence(x, y, w=150, n=5, color=REFERENCE, edge=REFERENCE_EDGE, h=15):
    gap = 5
    stepw = (w-gap*(n-1))/n
    for i in range(n):
        panel(x+i*(stepw+gap), y, stepw, h, color, edge,
              radius=2, lw=.85, z=4)


def asset(name, x, y, w, h):
    path = PAPER / 'figures' / 'inputs' / name
    if not path.exists():
        return False
    im = Image.open(path)
    scale = min(w/im.width, h/im.height)
    ww, hh = im.width*scale, im.height*scale
    xx, yy = x+(w-ww)/2, y+(h-hh)/2
    ax.imshow(im, extent=[xx, xx+ww, yy+hh, yy], aspect='auto', zorder=4)
    return True


def views(x, y, w=155, h=58):
    if not asset('fig02_multiview.png', x, y, w, h):
        for i in range(3):
            xx = x+i*(w+4)/3
            panel(xx, y, (w-8)/3, h, 'white', '#8A8A8A', radius=4, lw=.9)
            text(xx+(w-8)/6, y+h/2, f'View {i+1}', size=10.5,
                 color=QUIET, ha='center')


def force_history(x, y, w=155, h=50):
    if not asset('fig02_force_history.png', x, y, w, h):
        # Input placeholder, without numerical axes or empirical measurements.
        line([(x, y+2), (x, y+h), (x+w, y+h)], color=NEUTRAL_STROKE, lw=.8)
        t = np.linspace(0, 1, 120)
        yy = y+h*(.68-.25*np.sin(2*np.pi*t)*np.exp(-.9*t)-.15*t)
        line(list(zip(x+5+(w-10)*t, yy)), color=FORCE_EDGE, lw=1.7)


def state(x, y, w=128, h=48):
    if not asset('fig02_state.png', x, y, w, h):
        ox, oy = x+24, y+29
        arrow((ox, oy), (ox+32, oy), color=EDGE, scale=7, lw=1.1)
        arrow((ox, oy), (ox, oy-24), color=EDGE, scale=7, lw=1.1)
        arrow((ox, oy), (ox-16, oy+14), color=EDGE, scale=7, lw=1.1)
        for i, ww in enumerate([45, 31, 39]):
            panel(x+68, y+9+i*12, ww, 5, '#636363', radius=2)


def route(points, color=EDGE, lw=1.25, scale=9):
    if len(points) > 2:
        line(points[:-1], color, lw)
    arrow(points[-2], points[-1], color, lw, scale)


def operation(cx, cy, symbol='+', edge=EDGE, radius=14):
    ax.add_patch(Circle((cx, cy), radius, fc='white', ec=edge, lw=1.3, zorder=5))
    text(cx, cy, symbol, size=18, color=edge, ha='center', z=6)


def transform(x, y, w, h, label, color=NEUTRAL, edge=EDGE, size=18, direction='right', taper=7):
    points = ([(x,y), (x+w,y), (x+w-8,y+h), (x+8,y+h)]
              if direction == 'down' else
              [(x,y), (x+w,y+taper), (x+w,y+h-taper), (x,y+h)])
    ax.add_patch(Polygon(points,
                         fc=color, ec=edge, lw=1.1, zorder=3))
    if isinstance(label, tuple):
        offset = 14
        text(x+w/2, y+h/2-offset, label[0], size=size, ha='center')
        text(x+w/2, y+h/2+offset, label[1], size=size, ha='center')
    else:
        text(x+w/2, y+h/2, label, size=size, ha='center')


def token(cx, y, label, fill=NEUTRAL, edge=NEUTRAL_STROKE, w=43, h=31):
    panel(cx-w/2, y, w, h, fill, edge, radius=2, lw=.8, z=4)
    text(cx, y+h/2, label, size=20, ha='center', z=5)


# Training history is shown locally: pretrained frozen teacher modules,
# previously learned token/adapter, and the correction policy being trained.
# The depicted data flow remains correction distillation, not teacher fitting.
text(35, 130, '(a) Teacher-defined correction targets', size=24, weight='bold')

# The visual-language prefix is produced from the earlier reference query,
# then reused in both current teacher calls. It is not a new raw modality.
text(132, 185, r'Images $V_k$', size=20, ha='center')
views(42, 207, 180, 43)
text(132, 274, r'Instruction $L$', size=20, ha='center')
panel(46, 294, 177, 32, GENERIC_MODULE, '#8A8A8A', radius=3, lw=.8)
# A text-input placeholder, not a claimed instruction from the dataset.
for yy, width in [(303, 136), (311, 112), (319, 124)]:
    line([(65, yy), (65+width, yy)], color=NEUTRAL_STROKE, lw=1)
arrow((228, 228), (268, 228))
arrow((228, 310), (268, 310))
panel(272, 211, 208, 128, CONTEXT_TOKEN, EDGE, radius=4)
panel(268, 207, 208, 128, VLM_MODULE, EDGE, radius=4, lw=1.2, z=2)
text(372, 271, 'VLM', size=29, ha='center', weight='bold')
snowflake(454, 225, 9)
# E_k labels the VLM output connection directly. The student receives its
# pooled representation, not a second independently encoded visual context.
line([(486, 271), (615, 271), (615, 385)], color=INK, lw=1.4)
text(550, 247, r'$E_k$', size=25, ha='center')

# Current state is a shared input to both teacher modes, distinct from the
# stored reference's query state S_k used in reference-state alignment.
text(132, 349, r'State $S_t$', size=20, ha='center')
state(75, 365, 126, 42)
# Context and state merge only at the shared-input junction. State does not
# enter the vision-language encoder or the learned missing-force token.
line([(223, 385), (615, 385)], color=INK, lw=1.4)
ax.add_patch(Circle((615, 385), 3, fc=INK, ec='none', zorder=5))
arrow((615, 385), (650, 385), color=INK, lw=1.4)

# Shared action-expert weights; the adapter appears only in the learned
# force-agnostic mode. The measured history enters only the conditioned call.
panel(650, 331, 320, 256, ACTION_MODULE, EDGE, radius=5, lw=1.25)
text(804, 352, 'Action expert', size=21, weight='bold', ha='center')
text(807, 385, r'Shared $E_k$, $S_t$, $\epsilon_k$', size=20, color=EDGE, ha='center')
snowflake(947, 351, 9)
panel(668, 436, 280, 55, ACTION_INNER, EDGE, radius=3, lw=.9)
text(809, 464, 'Force-conditioned', size=20, ha='center')
panel(668, 507, 280, 71, VLM_MODULE, EDGE, radius=3, lw=.9)
text(809, 529, 'Force-agnostic', size=20, ha='center')
# The adapter is part of this mode, not a separate processing stage.
text(809, 560, 'with pose adapter', size=16, color=INK, ha='center')

text(132, 429, r'Force history $\mathcal{F}_t$', size=20, ha='center')
force_history(43, 446, 171, 36)
arrow((222, 464), (255, 464))
transform(263, 434, 167, 60, ('Force', 'encoder'),
          color=FORCE_MODULE, edge=EDGE, size=20)
snowflake(420, 424, 7)
arrow((437, 464), (469, 464))
token(507, 448, r'$z_t^F$', FORCE, FORCE_EDGE, w=61)
arrow((545, 464), (668, 464))
text(462, 543, 'Learned token', size=20, ha='right', color=EDGE)
token(507, 527, r'$z_{\varnothing F}$', FORCE_MODULE, NEUTRAL_STROKE, w=67)
snowflake(553, 515, 6)
arrow((549, 543), (668, 543), color=EDGE)

# All three glyphs below are K-step pose-action segments at matching times.
# The stored segment is a separate input; it is NOT produced by a current call.
pose_chunks = [
    (464, r'$\mathcal{P}(A^{\mathrm{cond}}_{T,t|k,1:K})$', ACTION_INNER, EDGE),
    (543, r'$\mathcal{P}(A^{\mathrm{ref}}_{T,t|k,1:K})$', 'white', REFERENCE_EDGE),
    (631, r'$\mathcal{P}(A^{\mathrm{ref}}_k(t_{1:K}))$', REFERENCE, REFERENCE_EDGE),
]
for y, label, fill, edge in pose_chunks:
    text(1116, y-40, label, size=21, ha='center', color=edge)
    sequence(1020, y-12, 193, h=24, color=fill, edge=edge)
arrow((976, 464), (1013, 464))
arrow((976, 543), (1013, 543), color=REFERENCE_EDGE)
text(807, 631, r'Reference stored at $S_k$', size=20,
     color=REFERENCE_EDGE, ha='center')
arrow((974, 631), (1013, 631), color=REFERENCE_EDGE)

# Stagger the two signed sums: a current force-agnostic prediction enters
# the force sum negatively and the delay sum positively. The stored reference
# enters only the delay sum, negatively. Signs sit beside distinct input ports.
operation(1300, 464)
operation(1360, 585)
arrow((1219, 464), (1281, 464), color=EDGE)
text(1253, 447, '+', size=19, ha='center')
line([(1219, 543), (1360, 543)], color=REFERENCE_EDGE)
ax.add_patch(Circle((1300, 543), 2.3, fc=REFERENCE_EDGE, ec='none', zorder=5))
arrow((1300, 543), (1300, 483), color=REFERENCE_EDGE)
text(1320, 503, '−', size=20, color=REFERENCE_EDGE)
arrow((1360, 543), (1360, 566), color=REFERENCE_EDGE)
text(1379, 553, '+', size=19, color=REFERENCE_EDGE)
route([(1219, 631), (1270, 631), (1270, 585), (1341, 585)], color=REFERENCE_EDGE)
text(1312, 568, '−', size=20, ha='center', color=REFERENCE_EDGE)

arrow((1320, 464), (1580, 464), color=FORCE_EDGE)
arrow((1380, 585), (1395, 585), color=DELAY_EDGE)
panel(1400, 562, 160, 46, DELAY_MODULE, DELAY_EDGE, radius=3, lw=1.1)
text(1480, 585, r'$+\;\Gamma(S_t,S_k)$', size=21, color=INK, ha='center')
text(1510, 636, 'Reference-state alignment', size=17,
     color=DELAY_EDGE, ha='center')
arrow((1563, 585), (1580, 585), color=DELAY_EDGE)

target_force = r'$\Delta A^{\mathrm{force}}_{T,t|k,1:K}$'
target_delay = r'$\Delta A^{\mathrm{delay}}_{T,k\rightarrow t,1:K}$'
# Group the two teacher-defined targets as the supervision bundle. Its only
# outgoing path goes to the existing distillation objective in panel (b).
panel(1572, 398, 209, 226, 'white', '#A0A0A0', radius=5, lw=1)
for cy, title, fill, edge in [
    (464, 'Force target', FORCE, FORCE_EDGE),
    (585, 'Delay target', DELAY, DELAY_EDGE),
]:
    text(1674, cy-42, title, size=22, color=edge, ha='center', weight='bold')
    sequence(1588, cy-12, 172, color=fill, edge=edge, h=24)

line([(35, 655), (1765, 655)], color=RULE, lw=.8)
text(35, 686, '(b) Student correction policy', size=24, weight='bold')

# Inputs and their encoders remain outside the attention module. The context
# uses a learned projector, the force history uses its own causal encoder;
# state, flattened reference and timing use the manuscript's projections.
# Five inputs are stacked at the left. Every row proceeds left to right:
# observation/context -> encoder or projection -> condition token(s).
rows = [776, 868, 960, 1052, 1144]
for cy, title, lab in zip(
    rows,
    ['Pooled context', 'Force history', 'State', 'Reference', 'Timing'],
    [r'$(\bar E_k,\bar m_k)$', r'$\mathcal{F}_t$', r'$S_t$',
     r'$A_k^{\mathrm{ref}}(t_{1:K})$', r'$\xi_{t,k}$'],
):
    text(140, cy-20, title, size=20, ha='center')
    text(140, cy+17, lab, size=24, ha='center')
    if title != 'Reference':
        arrow((250, cy), (294, cy), scale=9)
        arrow((493, cy), (539, cy), scale=9)

# P_ctx -> P_Z denotes the sequential context mappings in the supplement
# and eq:conditioning_set; the remaining projections retain their symbols.
transform(300, 743, 185, 66, r'$P_{\mathrm{ctx}}\!\rightarrow\!P_Z$', color=VLM_MODULE, size=23, taper=13)
transform(300, 835, 185, 66, ('Force', 'encoder'),
          color=FORCE_MODULE, edge=EDGE, size=20)
transform(300, 927, 185, 66, r'$P_S$', color=GENERIC_MODULE, size=23)
# One horizontal reference chunk uses the same action-block glyph as panel (a).
# Deterministic flattening before P_A is specified in the manuscript and is
# implicit here; each block denotes an action step, not an attention token.
sequence(250, 1040, 156, h=24, color=REFERENCE, edge=REFERENCE_EDGE)
arrow((413, 1052), (437, 1052), scale=8)
# The learned projection produces one token in the shared input group.
ax.add_patch(Polygon([(444,1019), (508,1032), (508,1072), (444,1085)],
                     fc=VLM_MODULE, ec=EDGE, lw=1.1, zorder=3))
text(475, 1052, r'$P_A$', size=23, ha='center')
arrow((515, 1052), (539, 1052), scale=8)
transform(300, 1111, 185, 66, r'$P_\xi$', color=GENERIC_MODULE, size=23)

# One vertical group of projected tokens. The bracket denotes the complete
# conditioning set; no repeated title is needed. P_A produces one token.
panel(551, 763, 61, 30, VLM_MODULE, NEUTRAL_STROKE, radius=2, lw=.8)
panel(556, 758, 61, 30, CONTEXT_TOKEN, NEUTRAL_STROKE, radius=2, lw=.8, z=3)
text(638, 776, r'$\cdots$', size=21, color=EDGE, ha='center')
token(584, 852, r'$u_t^F$', FORCE, FORCE_EDGE, w=61, h=32)
token(584, 944, '', GENERIC_MODULE, w=61, h=32)
token(584, 1036, '', REFERENCE, REFERENCE_EDGE, w=61, h=32)
token(584, 1128, '', GENERIC_MODULE, w=61, h=32)
line([(663, 741), (678, 741), (678, 1179), (663, 1179)],
     color=NEUTRAL_STROKE, lw=1)

# The complete condition set branches into the two shared-weight evaluations.
# Mask_F remains upstream of attention and only on the delay evaluation.
# The caption specifies the two separate evaluations, shared learned query,
# and query-position readout. A single silhouette denotes the shared module.
arrow((678, 960), (717, 960), scale=9)
line([(717, 900), (717, 1020)])
arrow((717, 900), (850, 900), scale=9)
arrow((717, 1020), (735, 1020), scale=8)
panel(741, 1002, 88, 36, 'white', NEUTRAL_STROKE, radius=3, lw=1)
text(785, 1020, r'$\mathrm{Mask}_F$', size=19, ha='center')
arrow((835, 1020), (850, 1020), scale=8)

# Approved option A: input arrows stop at the shared module; output arrows
# begin at its right boundary. No data-flow lines cross the box interior.
panel(850, 860, 260, 200, SHARED_FILL, SHARED_EDGE, radius=5, lw=1.1)
text(980, 947, 'Shared attention', size=20, ha='center', weight='bold')
text(980, 986, r'$\Phi$', size=30, ha='center')
for cy, head, weight, pred, fill, edge in [
    (900, 'Force head', r'$W_{\mathrm{force}}$', r'$\Delta\hat A^{\mathrm{force}}_{t,1:K}$', FORCE, FORCE_EDGE),
    (1020, 'Delay head', r'$W_{\mathrm{delay}}$', r'$\Delta\hat A^{\mathrm{delay}}_{t,1:K}$', DELAY, DELAY_EDGE),
]:
    arrow((1110, cy), (1142, cy), color=SHARED_EDGE, scale=9)
    transform(1150, cy-38, 150, 76, (head, weight), fill, edge, size=18)
    arrow((1307, cy), (1353, cy), color=edge, scale=9)
    sequence(1360, cy-12, 168, h=24, color=fill, edge=edge)
    text(1444, cy-45, pred, size=24, color=edge, ha='center')
    arrow((1535, cy), (1600, cy), color=edge, scale=9)

# Teacher targets enter the same objective as both student predictions.
panel(1600, 860, 176, 200, 'white', EDGE, radius=10, lw=1.2)
text(1688, 960, r'$\mathcal{L}_{\mathrm{distill}}$', size=26, ha='center')
line([(1698, 624), (1698, 694)], color=SHARED_EDGE, lw=1.6, dash=True)
text(1698, 718, 'Distillation', size=20, color=SHARED_EDGE, ha='center', weight='bold')
arrow((1698, 742), (1698, 860), color=SHARED_EDGE, lw=1.6, scale=12, dash=True)

for suffix in ['png', 'pdf', 'svg']:
    fig.savefig(OUT / f'fig02_architecture.{suffix}', dpi=150, facecolor='white')
svg_path = OUT / 'fig02_architecture.svg'
svg_path.write_text('\n'.join(s.rstrip() for s in svg_path.read_text().splitlines())+'\n')
print(OUT / 'fig02_architecture.png')
