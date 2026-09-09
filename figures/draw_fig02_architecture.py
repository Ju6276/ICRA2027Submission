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
from figure_palette import snowflake_segments

# Palette C hues with increased saturation for small data glyphs. Blue marks
# reference actions; orange marks force corrections, rose delay corrections,
# and coral the shared student module. Generic modules have white faces.
FORCE = '#E99D4D'
DELAY = '#CF638F'
REFERENCE = '#639AC5'
FORCE_EDGE = '#A96017'
DELAY_EDGE = '#9E3561'
REFERENCE_EDGE = '#2F6793'
INK = '#202020'
EDGE = '#383838'
NEUTRAL = '#FFFFFF'
NEUTRAL_STROKE = '#666666'
FORCE_MODULE = '#FFF0DF'
SHARED_ACCENT = '#DC806E'
SHARED_FILL = '#FCECE7'
SHARED_EDGE = '#AD503C'

plt.rcParams.update({
    'font.family': 'Arial',
    'mathtext.fontset': 'stix',
    'svg.fonttype': 'none',
})
fig = plt.figure(figsize=(18, 9.88), facecolor='white')
ax = fig.add_axes([0, 0, 1, 1])
ax.set(xlim=(0, 1800), ylim=(1080, 92))
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


def arrow(a, b, color=EDGE, lw=1.3, scale=10, z=4):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle='-|>', mutation_scale=scale,
                                color=color, lw=lw, shrinkA=0, shrinkB=0,
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


def transform(x, y, w, h, label, color=NEUTRAL, edge=EDGE, size=18):
    ax.add_patch(Polygon([(x,y), (x+w,y+7), (x+w,y+h-7), (x,y+h)],
                         fc=color, ec=edge, lw=1.1, zorder=3))
    if isinstance(label, tuple):
        text(x+w/2, y+h/2-14, label[0], size=size, ha='center')
        text(x+w/2, y+h/2+14, label[1], size=size, ha='center')
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
panel(46, 294, 177, 32, 'white', '#8A8A8A', radius=3, lw=.8)
# A text-input placeholder, not a claimed instruction from the dataset.
for yy, width in [(303, 136), (311, 112), (319, 124)]:
    line([(65, yy), (65+width, yy)], color=NEUTRAL_STROKE, lw=1)
arrow((228, 228), (268, 228))
arrow((228, 310), (268, 310))
panel(272, 211, 208, 128, 'white', EDGE, radius=4)
panel(268, 207, 208, 128, 'white', EDGE, radius=4, lw=1.2, z=2)
text(372, 257, 'Vision–language', size=20, ha='center')
text(372, 287, 'encoder', size=20, ha='center')
snowflake(454, 225, 9)
arrow((486, 255), (522, 255))
sequence(533, 244, 108, n=3, h=22, color=NEUTRAL, edge=NEUTRAL_STROKE)
text(675, 255, r'$\cdots$', size=22, color=EDGE, ha='center')
text(615, 213, r'$E_k$', size=25, ha='center')
text(615, 288, r'Context from $k$', size=20, color=EDGE, ha='center')

# Current state is a shared input to both teacher modes, distinct from the
# stored reference's query state S_k used in reference-state alignment.
text(132, 349, r'State $S_t$', size=20, ha='center')
state(75, 365, 126, 42)
# Context and state merge only at the shared-input junction. State does not
# enter the vision-language encoder or the learned missing-force token.
line([(223, 385), (615, 385)], color=INK, lw=1.4)
line([(615, 305), (615, 385)], color=INK, lw=1.4)
ax.add_patch(Circle((615, 385), 3, fc=INK, ec='none', zorder=5))
arrow((615, 385), (650, 385), color=INK, lw=1.4)

# Shared action-expert weights; the adapter appears only in the learned
# force-agnostic mode. The measured history enters only the conditioned call.
panel(650, 331, 320, 256, 'white', EDGE, radius=5, lw=1.25)
text(804, 352, 'Action expert', size=21, weight='bold', ha='center')
text(807, 385, r'Shared $E_k$, $S_t$, $\epsilon_k$', size=20, color=EDGE, ha='center')
snowflake(947, 351, 9)
panel(668, 436, 280, 55, 'white', EDGE, radius=3, lw=.9)
text(809, 464, 'Force-conditioned', size=20, ha='center')
panel(668, 507, 280, 71, 'white', EDGE, radius=3, lw=.9)
text(809, 529, 'Force-agnostic', size=20, ha='center')
panel(722, 548, 174, 25, 'white', NEUTRAL_STROKE, radius=2, lw=.8)
text(809, 560, 'Pose adapter', size=17, color=INK, ha='center')

text(132, 429, r'Force history $\mathcal{F}_t$', size=20, ha='center')
force_history(43, 446, 171, 36)
arrow((222, 464), (255, 464))
transform(263, 434, 167, 60, ('Force', 'encoder'),
          color=FORCE_MODULE, edge=FORCE_EDGE, size=20)
snowflake(420, 424, 7)
arrow((437, 464), (469, 464))
token(507, 448, r'$z_t^F$', FORCE, FORCE_EDGE, w=61)
arrow((545, 464), (668, 464))
text(462, 543, 'Learned token', size=20, ha='right', color=EDGE)
token(507, 527, r'$z_{\varnothing F}$', NEUTRAL, NEUTRAL_STROKE, w=67)
snowflake(553, 515, 6)
arrow((549, 543), (668, 543), color=EDGE)

# All three glyphs below are K-step pose-action segments at matching times.
# The stored segment is a separate input; it is NOT produced by a current call.
pose_chunks = [
    (464, r'$\mathcal{P}(A^{\mathrm{cond}}_{T,t|k,1:K})$', '#F4F4F4', EDGE),
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

# Signed inputs make the order of the two differences explicit.
operation(1300, 501)
operation(1300, 585)
route([(1219, 464), (1300, 464), (1300, 481)], color=EDGE)
text(1283, 478, '+', size=17, ha='right')
line([(1219, 543), (1300, 543)], color=REFERENCE_EDGE)
ax.add_patch(Circle((1300, 543), 2.3, fc=REFERENCE_EDGE, ec='none', zorder=5))
arrow((1300, 537), (1300, 521), color=REFERENCE_EDGE)
text(1283, 528, '−', size=18, ha='right', color=REFERENCE_EDGE)
arrow((1300, 549), (1300, 565), color=REFERENCE_EDGE)
text(1283, 558, '+', size=17, ha='right', color=REFERENCE_EDGE)
route([(1219, 631), (1300, 631), (1300, 605)], color=REFERENCE_EDGE)
text(1283, 616, '−', size=18, ha='right', color=REFERENCE_EDGE)

arrow((1320, 501), (1580, 501), color=FORCE_EDGE)
arrow((1320, 585), (1353, 585), color=DELAY_EDGE)
panel(1360, 562, 175, 46, '#FCEAF1', DELAY_EDGE, radius=3, lw=1.1)
text(1447, 585, r'$+\;\Gamma(S_t,S_k)$', size=22, color=INK, ha='center')
text(1447, 636, 'Reference-state alignment', size=18,
     color=DELAY_EDGE, ha='center')
arrow((1542, 585), (1580, 585), color=DELAY_EDGE)

target_force = r'$\Delta A^{\mathrm{force}}_{T,t|k,1:K}$'
target_delay = r'$\Delta A^{\mathrm{delay}}_{T,k\rightarrow t,1:K}$'
for cy, title, fill, edge in [
    (501, 'Force target', FORCE, FORCE_EDGE),
    (585, 'Delay target', DELAY, DELAY_EDGE),
]:
    text(1674, cy-42, title, size=22, color=edge, ha='center', weight='bold')
    sequence(1588, cy-12, 172, color=fill, edge=edge, h=24)

line([(35, 655), (1765, 655)], color=RULE, lw=.8)
text(35, 686, '(b) Train the correction policy', size=24, weight='bold')

# Inputs and their encoders remain outside the attention module. The context
# uses a learned projector, the force history uses its own causal encoder;
# state, flattened reference and timing use the manuscript's projections.
centers = [125, 322, 503, 684, 847]
for cx, title in zip(centers, ['Pooled context', 'Force history', 'State', 'Reference', 'Timing']):
    text(cx, 732, title, size=18, ha='center')
sequence(52, 763, 106, n=3, color=NEUTRAL, edge=NEUTRAL_STROKE, h=17)
text(182, 772, r'$\cdots$', size=19, color=EDGE, ha='center')
force_history(253, 748, 140, 36)
state(462, 746, 93, 38)
sequence(615, 764, 139, h=20)
for cx, lab in zip(centers, [r'$(\bar E_k,\bar m_k)$', r'$\mathcal{F}_t$', r'$S_t$',
                            r'$A_k^{\mathrm{ref}}(t_{1:K})$', r'$\xi_{t,k}$']):
    text(cx, 807, lab, size=21, ha='center')
    arrow((cx, 827), (cx, 834), scale=7)
# P_ctx produces Z_k^ctx (supplement); P_Z maps it to conditioning tokens
# (eq:conditioning_set). The arrow denotes this existing sequential mapping.
transform(40, 840, 170, 74, r'$P_{\mathrm{ctx}}\!\rightarrow\!P_Z$', size=23)
transform(244, 840, 156, 74, ('Force', 'encoder'),
          color=FORCE_MODULE, edge=FORCE_EDGE, size=20)
transform(458, 840, 90, 74, r'$P_S$', size=23)
transform(606, 840, 156, 74, ('Flatten', r'$P_A$'), size=20)
transform(801, 840, 92, 74, r'$P_\xi$', size=23)
for cx in centers:
    arrow((cx, 920), (cx, 934), scale=8)

# A context token group, and one token each for force, state, reference, timing.
panel(74, 946, 78, 30, NEUTRAL, NEUTRAL_STROKE, radius=2, lw=.8)
panel(79, 941, 78, 30, NEUTRAL, NEUTRAL_STROKE, radius=2, lw=.8, z=3)
text(178, 956, r'$\cdots$', size=21, color=EDGE, ha='center')
token(322, 941, r'$u_t^F$', FORCE, FORCE_EDGE, w=58)
# Unnamed glyphs are the outputs of the labeled projections above, not new
# aliases for raw state, action, or timing inputs. The bracket groups all C_t.
token(503, 941, '', w=43)
token(684, 941, '', REFERENCE, REFERENCE_EDGE, w=43)
token(847, 941, '', w=43)
line([(45, 934), (35, 934), (35, 993), (894, 993), (894, 934), (884, 934)],
     color=NEUTRAL_STROKE, lw=.9)
text(470, 1016, r'$\mathcal{C}_t$', size=23, color=EDGE, ha='center')

# Same direction for both student evaluations. The operator masks only the
# force token in C_t; it does not mask the force encoder during teacher queries.
arrow((894, 956), (949, 956))
line([(949, 956), (962, 956), (962, 850), (1040, 850)])
arrow((1040, 850), (1060, 850))
text(1009, 823, r'$\mathcal{C}_t$', size=23, ha='center', color=EDGE)
line([(962, 956), (962, 1007), (973, 1007)])
panel(978, 988, 67, 38, '#FCEAF1', DELAY_EDGE, radius=3, lw=1)
text(1012, 1007, r'$\mathrm{Mask}_F$', size=18, ha='center', color=DELAY_EDGE)
arrow((1045, 1007), (1060, 1007), color=DELAY_EDGE, scale=7)

text(1142, 778, 'Shared attention', size=21, ha='center', weight='bold')
# One parameterized module, evaluated separately along the two horizontal
# paths. The query-output glyphs and separate heads lie outside its boundary.
panel(1060, 807, 164, 241, SHARED_FILL, SHARED_EDGE, radius=4, lw=1.1)
panel(1068, 808, 148, 5, SHARED_ACCENT, radius=1, z=2)
text(1142, 927, r'$\Phi$', size=37, color=SHARED_EDGE, ha='center')
# q_corr is a learned INPUT shared by both calls (eq:force_output/delay_output).
# It is appended after the delay branch masks C_t's force token.
panel(980, 910, 69, 34, 'white', EDGE, radius=2, lw=.9)
text(1014, 927, r'$q_{\mathrm{corr}}$', size=20, ha='center')
line([(1049, 927), (1081, 927)], color=EDGE, lw=1.1)
ax.add_patch(Circle((1081, 927), 2.3, fc=EDGE, ec='none', zorder=5))
arrow((1081, 927), (1081, 850), color=EDGE, lw=1.1, scale=8)
arrow((1081, 927), (1081, 1007), color=EDGE, lw=1.1, scale=8)
for cy, head, weight, pred, fill, edge in [
    (850, 'Force head', r'$W_{\mathrm{force}}$', r'$\Delta\hat A^{\mathrm{force}}_{t,1:K}$', FORCE, FORCE_EDGE),
    (1007, 'Delay head', r'$W_{\mathrm{delay}}$', r'$\Delta\hat A^{\mathrm{delay}}_{t,1:K}$', DELAY, DELAY_EDGE),
]:
    arrow((1060, cy), (1235, cy), color=SHARED_EDGE, scale=8)
    panel(1240, cy-14, 30, 28, SHARED_ACCENT, SHARED_EDGE, radius=2, lw=.8)
    # Brackets denote selection of the query-position feature, as in Phi(...)[q].
    text(1255, cy-36, r'$[q_{\mathrm{corr}}]$', size=20, color=EDGE, ha='center')
    arrow((1275, cy), (1290, cy), scale=8)
    transform(1296, cy-38, 134, 76, (head, weight), fill, edge, size=17)
    arrow((1436, cy), (1453, cy), color=edge, scale=8)
    text(1524, cy-40, pred, size=24, color=edge, ha='center')
    sequence(1460, cy-12, 128, h=24, color=fill, edge=edge)
    arrow((1594, cy), (1671, cy), color=edge)
    operation(1700, cy, r'$\ell_{\mathrm{pose}}$', edge=edge, radius=24)

# Matching target chunks identify supervision without repeating long formulae.
# Their colors and vertical order agree with the named targets in panel (a).
text(1664, 744, 'Targets from (a)', size=20, ha='center', color=EDGE)
for cy, lab, fill, edge in [
    (850, target_force, FORCE, FORCE_EDGE),
    (1007, target_delay, DELAY, DELAY_EDGE),
]:
    sequence(1633, cy-69, 134, h=22, color=fill, edge=edge)
    arrow((1700, cy-40), (1700, cy-30), color=edge, scale=8)

for suffix in ['png', 'pdf', 'svg']:
    fig.savefig(OUT / f'fig02_architecture.{suffix}', dpi=150, facecolor='white')
svg_path = OUT / 'fig02_architecture.svg'
svg_path.write_text('\n'.join(s.rstrip() for s in svg_path.read_text().splitlines())+'\n')
print(OUT / 'fig02_architecture.png')
