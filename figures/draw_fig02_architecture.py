"""Fig. 2: teacher-defined correction targets and correction-policy training.

Run this script to regenerate the manuscript PDF, PNG, and editable SVG.
Optional input thumbnails are loaded from figures/inputs/; missing assets use
illustrative placeholders.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Rectangle, Circle
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


def condition_tokens(cx, y, masked=False, scale=1):
    # The context is a token group; the remaining conditions each use a token.
    # A flattened K-step action segment is projected to ONE reference token.
    colors = [NEUTRAL, FORCE, NEUTRAL, REFERENCE, NEUTRAL]
    labels = [r'$\mathrm{ctx}\,\cdots$', r'$F$', r'$S$', r'$A$', r'$\xi$']
    widths = [60*scale, *([32*scale]*4)]
    h, gap = 32*scale, 6*scale
    xx = cx-(sum(widths)+4*gap)/2
    for i, (color, lab, w) in enumerate(zip(colors, labels, widths)):
        panel(xx, y, w, h, color, NEUTRAL_STROKE, radius=3, lw=.7, z=3)
        if masked and i == 1:
            p = Rectangle((xx+1, y+1), w-2, h-2, facecolor='#F4F4F4',
                          edgecolor=DELAY_EDGE, hatch='////', lw=0, zorder=4)
            ax.add_patch(p)
            text(xx+w/2, y+h/2, lab, size=17*scale, color=DELAY_EDGE,
                 ha='center', z=5)
        else:
            text(xx+w/2, y+h/2, lab, size=17*scale, ha='center', z=5)
        xx += w+gap


def output(cx, y, s, fill, edge, width=244):
    panel(cx-width/2, y, width, 47, fill, edge, radius=7, lw=1.05, z=4)
    text(cx, y+23, s, size=22, ha='center', color=edge)


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
text(1760, 130, r'Reference query $k$ from schedule replay', size=17,
     color=EDGE, ha='right')

# The visual-language prefix is produced from the earlier reference query,
# then reused in both current teacher calls. It is not a new raw modality.
views(42, 191, 180, 61)
text(132, 275, r'Images $V_k$', size=19, ha='center')
panel(46, 300, 177, 37, 'white', '#8A8A8A', radius=3, lw=.8)
text(134, 318, '“Insert the plug”', size=17, ha='center')
text(134, 363, r'Instruction $L$', size=19, ha='center')
arrow((228, 221), (259, 221))
arrow((228, 318), (259, 318))
panel(272, 211, 208, 128, 'white', EDGE, radius=4)
panel(268, 207, 208, 128, 'white', EDGE, radius=4, lw=1.2, z=2)
text(372, 256, 'Vision–language', size=19, ha='center')
text(372, 285, 'encoder', size=19, ha='center')
text(372, 316, r'Pretrained $\theta$', size=16, color=EDGE, ha='center')
snowflake(454, 225, 9)
arrow((486, 255), (522, 255))
sequence(533, 244, 165, n=6, h=22, color=NEUTRAL, edge=NEUTRAL_STROKE)
text(615, 213, r'$E_k$', size=25, ha='center')
text(615, 288, r'Saved at $k$, reused at $t$', size=18, color=EDGE, ha='center')
route([(615, 306), (615, 358), (644, 358)])

# Current state is a shared input to both teacher modes, distinct from the
# stored reference's query state S_k used in reference-state alignment.
panel(748, 198, 221, 103, 'white', EDGE, radius=4, lw=1.2)
text(858, 221, r'Current state $S_t$', size=19, ha='center')
state(801, 243, 126, 46)
arrow((858, 301), (858, 327), color=INK, lw=1.5, scale=11)

# Shared action-expert weights; the adapter appears only in the learned
# force-agnostic mode. The measured history enters only the conditioned call.
panel(650, 327, 320, 234, 'white', EDGE, radius=5, lw=1.25)
text(804, 350, 'Pretrained action expert', size=17, weight='bold', ha='center')
text(807, 379, r'Shared $E_k$, $S_t$, $\epsilon_k$', size=18, color=EDGE, ha='center')
snowflake(957, 338, 7)
panel(668, 401, 280, 44, 'white', EDGE, radius=3, lw=.9)
text(809, 423, 'Force-conditioned', size=19, ha='center')
panel(668, 484, 280, 69, 'white', EDGE, radius=3, lw=.9)
text(809, 504, 'Force-agnostic', size=19, ha='center')
panel(722, 525, 174, 22, 'white', NEUTRAL_STROKE, radius=2, lw=.8)
text(809, 536, 'Pose adapter', size=16, color=INK, ha='center')

force_history(43, 404, 171, 45)
text(128, 477, r'Force history $\mathcal{F}_t$', size=19, ha='center')
arrow((222, 423), (255, 423))
transform(263, 393, 167, 60, ('Causal force', 'encoder'),
          color=FORCE_MODULE, edge=FORCE_EDGE, size=18)
snowflake(420, 387, 7)
arrow((437, 423), (469, 423))
token(507, 407, r'$z_t^F$', FORCE, FORCE_EDGE, w=61)
arrow((545, 423), (662, 423))
text(462, 518, 'Learned token', size=19, ha='right', color=EDGE)
token(507, 502, r'$z_{\varnothing F}$', NEUTRAL, NEUTRAL_STROKE, w=67)
snowflake(553, 490, 6)
arrow((549, 518), (662, 518), color=EDGE)
text(435, 580, r'Token + adapter learned with $\theta$ fixed', size=16.5,
     ha='center', color=EDGE)

# All three glyphs below are K-step pose-action segments at matching times.
# The stored segment is a separate input; it is NOT produced by a current call.
text(1116, 335, 'Pose action chunks', size=19, color=EDGE, ha='center')
pose_chunks = [
    (423, r'$\mathcal{P}(A^{\mathrm{cond}}_{T,t|k,1:K})$', '#F4F4F4', EDGE),
    (518, r'$\mathcal{P}(A^{\mathrm{ref}}_{T,t|k,1:K})$', 'white', REFERENCE_EDGE),
    (609, r'$\mathcal{P}(A^{\mathrm{ref}}_k(t_{1:K}))$', REFERENCE, REFERENCE_EDGE),
]
for y, label, fill, edge in pose_chunks:
    text(1116, y-40, label, size=23, ha='center', color=edge)
    sequence(1020, y-12, 193, h=24, color=fill, edge=edge)
arrow((976, 423), (1013, 423))
arrow((976, 518), (1013, 518), color=REFERENCE_EDGE)
text(807, 586, r'Reference query $k$', size=19, color=REFERENCE_EDGE, ha='center')
text(807, 615, r'Stored $A_k^{\mathrm{ref}}$ at $S_k$', size=18,
     color=REFERENCE_EDGE, ha='center')
arrow((974, 609), (1013, 609), color=REFERENCE_EDGE)

# Signed inputs make the order of the two differences explicit.
operation(1300, 458)
operation(1300, 575)
route([(1219, 423), (1300, 423), (1300, 438)], color=EDGE)
text(1283, 437, '+', size=17, ha='right')
line([(1219, 518), (1300, 518)], color=REFERENCE_EDGE)
ax.add_patch(Circle((1300, 518), 2.3, fc=REFERENCE_EDGE, ec='none', zorder=5))
arrow((1300, 512), (1300, 478), color=REFERENCE_EDGE)
text(1283, 488, '−', size=18, ha='right', color=REFERENCE_EDGE)
arrow((1300, 524), (1300, 555), color=REFERENCE_EDGE)
text(1283, 545, '+', size=17, ha='right', color=REFERENCE_EDGE)
route([(1219, 609), (1300, 609), (1300, 595)], color=REFERENCE_EDGE)
text(1283, 601, '−', size=18, ha='right', color=REFERENCE_EDGE)

arrow((1320, 458), (1580, 458), color=FORCE_EDGE)
arrow((1320, 575), (1353, 575), color=DELAY_EDGE)
panel(1360, 552, 175, 46, '#FCEAF1', DELAY_EDGE, radius=3, lw=1.1)
text(1447, 575, r'$+\;\Gamma(S_t,S_k)$', size=22, color=INK, ha='center')
text(1447, 620, 'Reference-state alignment', size=17,
     color=DELAY_EDGE, ha='center')
arrow((1542, 575), (1580, 575), color=DELAY_EDGE)

target_force = r'$\Delta A^{\mathrm{force}}_{T,t|k,1:K}$'
target_delay = r'$\Delta A^{\mathrm{delay}}_{T,k\rightarrow t,1:K}$'
for cy, label, title, fill, edge in [
    (458, target_force, 'Force target', FORCE, FORCE_EDGE),
    (575, target_delay, 'Delay target', DELAY, DELAY_EDGE),
]:
    text(1447, cy-42, title, size=20, color=edge, ha='center', weight='bold')
    text(1674, cy-43, label, size=24, color=edge, ha='center')
    sequence(1588, cy-12, 172, color=fill, edge=edge, h=24)

line([(35, 655), (1765, 655)], color=RULE, lw=.8)
text(35, 686, '(b) Train the correction policy', size=24, weight='bold')

# Inputs and their encoders remain outside the attention module. The context
# uses a learned projector, the force history uses its own causal encoder;
# state, flattened reference and timing use the manuscript's projections.
centers = [125, 322, 503, 684, 847]
for cx, title in zip(centers, ['Pooled context', 'Force history', 'State', 'Reference', 'Timing']):
    text(cx, 732, title, size=18, ha='center')
sequence(52, 763, 146, n=6, color=NEUTRAL, edge=NEUTRAL_STROKE, h=17)
force_history(253, 748, 140, 36)
state(462, 746, 93, 38)
sequence(615, 764, 139, h=20)
text(847, 771, 'Age + phase', size=17, color=EDGE, ha='center')
for cx, lab in zip(centers, [r'$(\bar E_k,\bar m_k)$', r'$\mathcal{F}_t$', r'$S_t$',
                            r'$A_k^{\mathrm{ref}}(t_{1:K})$', r'$\xi_{t,k}$']):
    text(cx, 807, lab, size=21, ha='center')
    arrow((cx, 827), (cx, 834), scale=7)
transform(45, 840, 160, 74, ('Context', 'projection'), size=17)
transform(244, 840, 156, 74, ('Causal force', 'encoder'),
          color=FORCE_MODULE, edge=FORCE_EDGE, size=17)
transform(458, 840, 90, 74, r'$P_S$', size=23)
transform(606, 840, 156, 74, ('Flatten', r'Project $P_A$'), size=16.5)
transform(801, 840, 92, 74, r'$P_\xi$', size=23)
for cx in centers:
    arrow((cx, 920), (cx, 934), scale=8)

# A context token group, and one token each for force, state, reference, timing.
panel(74, 946, 78, 30, NEUTRAL, NEUTRAL_STROKE, radius=2, lw=.8)
panel(79, 941, 78, 30, NEUTRAL, NEUTRAL_STROKE, radius=2, lw=.8, z=3)
text(118, 956, r'$\mathrm{ctx}$', size=19, ha='center')
text(178, 956, r'$\cdots$', size=21, color=EDGE, ha='center')
token(322, 941, r'$u_t^F$', FORCE, FORCE_EDGE, w=58)
token(503, 941, r'$S$', w=43)
token(684, 941, r'$A$', REFERENCE, REFERENCE_EDGE, w=43)
token(847, 941, r'$\xi$', w=43)
line([(45, 984), (45, 993), (894, 993), (894, 984)], color=NEUTRAL_STROKE, lw=.9)
text(470, 1016, r'Condition tokens $\mathcal{C}_t$', size=20, color=EDGE, ha='center')

# Same direction for both student evaluations. The operator masks only the
# force token in C_t; it does not mask the force encoder during teacher queries.
arrow((902, 956), (949, 956))
line([(949, 956), (962, 956), (962, 850), (1051, 850)])
arrow((1034, 850), (1056, 850))
text(1009, 823, r'$\mathcal{C}_t$', size=23, ha='center', color=EDGE)
line([(962, 956), (962, 1007), (973, 1007)])
panel(978, 988, 67, 38, '#FCEAF1', DELAY_EDGE, radius=3, lw=1)
text(1012, 1007, r'$\mathrm{Mask}_F$', size=18, ha='center', color=DELAY_EDGE)
arrow((1048, 1007), (1056, 1007), color=DELAY_EDGE, scale=7)
text(1012, 1064, 'Force token masked', size=16, color=DELAY_EDGE, ha='center')

text(1142, 778, 'Shared attention', size=20, ha='center', weight='bold')
panel(1045, 807, 196, 241, SHARED_FILL, SHARED_EDGE, radius=4, lw=1.1)
panel(1053, 808, 180, 5, SHARED_ACCENT, radius=1, z=2)
text(1142, 931, 'Shared weights', size=17, color=EDGE, ha='center')
for cy, head, pred, fill, edge in [
    (850, 'Force head', r'$\Delta\hat A^{\mathrm{force}}_{t,1:K}$', FORCE, FORCE_EDGE),
    (1007, 'Delay head', r'$\Delta\hat A^{\mathrm{delay}}_{t,1:K}$', DELAY, DELAY_EDGE),
]:
    panel(1062, cy-31, 162, 62, 'white', NEUTRAL_STROKE, radius=3, lw=.8)
    text(1143, cy-11, r'Attention $\Phi$', size=18, ha='center')
    text(1143, cy+16, r'Query $q_{\mathrm{corr}}$', size=18, color=EDGE, ha='center')
    arrow((1230, cy), (1247, cy), scale=8)
    transform(1253, cy-27, 134, 54, head, fill, edge, size=17)
    arrow((1393, cy), (1412, cy), color=edge, scale=8)
    text(1484, cy-40, pred, size=24, color=edge, ha='center')
    sequence(1420, cy-12, 128, h=24, color=fill, edge=edge)
    arrow((1554, cy), (1645, cy), color=edge)
    operation(1674, cy, r'$\ell_{\mathrm{pose}}$', edge=edge, radius=24)

# Repeat the exact target symbols beside the local losses. This avoids long
# inter-panel wires while identifying their origin unambiguously.
text(1674, 686, 'Targets from (a)', size=18, ha='center', color=EDGE)
for cy, lab, fill, edge in [
    (850, target_force, FORCE, FORCE_EDGE),
    (1007, target_delay, DELAY, DELAY_EDGE),
]:
    text(1674, cy-111, lab, size=23, color=edge, ha='center')
    sequence(1607, cy-69, 134, h=22, color=fill, edge=edge)
    arrow((1674, cy-40), (1674, cy-30), color=edge, scale=8)
text(1674, 1056, 'Stepwise pose loss', size=17, color=EDGE, ha='center')

for suffix in ['png', 'pdf', 'svg']:
    fig.savefig(OUT / f'fig02_architecture.{suffix}', dpi=150, facecolor='white')
svg_path = OUT / 'fig02_architecture.svg'
svg_path.write_text('\n'.join(s.rstrip() for s in svg_path.read_text().splitlines())+'\n')
print(OUT / 'fig02_architecture.png')
