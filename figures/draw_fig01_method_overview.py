#!/usr/bin/env python3
"""Draw the Fig. 1 teaser in the visual language of the pi-series papers.

Populate FAILURE_IMAGES with paths relative to this directory to replace the
four placeholders without changing the layout.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle
from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parent
OUTPUT_PDF = ROOT / "fig01_method_overview.pdf"
OUTPUT_PNG = ROOT / "fig01_method_overview.png"

FAILURE_IMAGES = [None, None, None, None]
FAILURE_LABELS = ["Impact", "Jamming", "Stick--slip", "Delayed recovery"]

INK = "#121212"
SUBTLE = "#58616A"
HAIRLINE = "#66717A"
CREAM = "#F4EEDC"
CREAM_2 = "#FAF6EA"
POLICY_BLUE = "#BFD6DF"
PALE_BLUE = "#E8F1F4"
ACTION_GREEN = "#DCE9D3"
FORCE_ORANGE = "#E99B5A"
FORCE_PALE = "#FAE8D7"
STALE_PURPLE = "#8F72AE"
STALE_PALE = "#EEE7F4"
ACCENT_RED = "#D94F43"
PLACEHOLDER = "#ECECE8"


plt.rcParams.update({
    "font.family": "DejaVu Sans Mono",
    "mathtext.fontset": "dejavusans",
    "axes.linewidth": 0.8,
})


def panel(ax, x, y, w, h, face="white", edge=INK, lw=0.8, radius=0.008,
          linestyle="-", z=2):
    p = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        facecolor=face, edgecolor=edge, linewidth=lw,
        linestyle=linestyle, zorder=z,
    )
    ax.add_patch(p)
    return p


def label(ax, x, y, text, size=9, weight="normal", color=INK,
          ha="center", va="center", z=5, linespacing=1.05):
    ax.text(x, y, text, fontsize=size, fontweight=weight, color=color,
            ha=ha, va=va, zorder=z, linespacing=linespacing)


def arrow(ax, start, end, color=INK, lw=0.9, dashed=False, scale=8,
          connection="arc3", z=3):
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-|>", mutation_scale=scale,
        color=color, linewidth=lw, linestyle="--" if dashed else "-",
        connectionstyle=connection, shrinkA=0.5, shrinkB=0.5, zorder=z,
    ))


def token_strip(ax, x, y, w, color, count=7):
    panel(ax, x, y, w, 0.042, face="white", edge=HAIRLINE,
          lw=0.65, radius=0.010, z=3)
    left = x + 0.014
    usable = w - 0.028
    for idx in range(count):
        cx = left + idx * usable / max(count - 1, 1)
        ax.add_patch(Circle((cx, y + 0.021), 0.0052,
                            facecolor=color, edgecolor=color, zorder=5))


def image_card(ax, x, y, w, h, title, image_path=None):
    panel(ax, x, y, w, h, face=CREAM, edge="#D5CCB5", lw=0.75,
          radius=0.009, z=2)
    pad = 0.008
    image_y = y + 0.030
    image_h = h - 0.041
    if image_path:
        source = Image.open(ROOT / image_path).convert("RGB")
        fitted = ImageOps.fit(source, (600, 380), method=Image.Resampling.LANCZOS)
        ax.imshow(fitted, extent=[x + pad, x + w - pad, image_y,
                                 image_y + image_h], aspect="auto", zorder=3)
    else:
        ax.add_patch(Rectangle(
            (x + pad, image_y), w - 2 * pad, image_h,
            facecolor=PLACEHOLDER, edgecolor="#B8B8B0", linewidth=0.65,
            linestyle=(0, (3, 2)), zorder=3,
        ))
        label(ax, x + w / 2, image_y + image_h / 2,
              "failure frame", size=7.2, color="#8A8A84")
        # Small corner marks remain unobtrusive after a real image is inserted.
        ax.plot([x + pad + 0.009, x + pad + 0.026],
                [image_y + image_h - 0.010] * 2, color="#A6A69F", lw=0.6, zorder=4)
    label(ax, x + w / 2, y + 0.015, title, size=7.8, weight="bold")




def main():
    fig, ax = plt.subplots(figsize=(12.2, 4.65))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
    label(ax, .16, .95, 'Unified force-aware VLA', size=12, weight='bold')
    panel(ax, .035, .70, .25, .17, face=PALE_BLUE)
    label(ax, .16, .83, 'Vision / language / state / force', size=7.2)
    label(ax, .16, .775, 'Full-action prediction', size=10, weight='bold')
    label(ax, .16, .73, 'task-level motion + contact adjustment', size=6.8)
    label(ax, .16, .646, 'Contact changes can outpace\naction updates', size=8, color=ACCENT_RED)
    for (x,y), title, path in zip([(.025,.34),(.17,.34),(.025,.07),(.17,.07)], FAILURE_LABELS, FAILURE_IMAGES):
        image_card(ax, x, y, .125, .23, title, path)
    ax.plot([.32,.32],[.06,.97],color=HAIRLINE,lw=.7)
    label(ax, .66, .95, 'ForceDelta-VLA', size=13, weight='bold')
    panel(ax, .345, .57, .62, .31, face=POLICY_BLUE)
    label(ax,.655,.836,'Missing-force residual distillation',size=10,weight='bold')
    panel(ax,.365,.63,.165,.135,face=CREAM)
    label(ax,.4475,.727,'Frozen teacher',size=9,weight='bold')
    label(ax,.4475,.679,'force-conditioned\n+ learned missing-force mode',size=6.7)
    panel(ax,.59,.65,.19,.095,face='white')
    label(ax,.685,.697,'Paired correction targets',size=8.2,weight='bold')
    arrow(ax,(.535,.698),(.585,.698))
    # Supervision terminates on the same policy used online.
    ax.plot([.784,.96,.96,.59],[.698,.698,.18,.18],color=STALE_PURPLE,lw=1,ls='--')
    arrow(ax,(.59,.18),(.59,.221),color=STALE_PURPLE,lw=1,dashed=True)
    label(ax,.89,.20,'Distill',size=9,color=STALE_PURPLE)
    label(ax,.60,.50,'Independent residual execution',size=10,weight='bold')
    panel(ax,.355,.36,.19,.09,face=PALE_BLUE)
    label(ax,.45,.405,'Missing-force reference',size=8.3,weight='bold')
    panel(ax,.49,.225,.195,.095,face=STALE_PALE)
    label(ax,.5875,.2725,'Residual policy',size=9,weight='bold')
    label(ax,.403,.275,'Recent force\nCurrent state',size=7.5)
    arrow(ax,(.452,.275),(.485,.275))
    arrow(ax,(.52,.355),(.55,.324))
    label(ax,.655,.345,'cached reference + task context',size=6.7)
    panel(ax,.735,.34,.155,.105,face=ACTION_GREEN)
    label(ax,.8125,.3925,'Reference\n+ corrections',size=9,weight='bold')
    arrow(ax,(.55,.425),(.73,.425))
    arrow(ax,(.685,.275),(.72,.275)); arrow(ax,(.72,.275),(.755,.335))
    label(ax,.65,.10,'Reuse task-level motion.\nExecute contact corrections independently.',size=10,weight='bold')
    for out in (OUTPUT_PDF, OUTPUT_PNG):
        fig.savefig(out,dpi=240,bbox_inches='tight',pad_inches=0,facecolor='white')
    plt.close(fig)

if __name__ == "__main__":
    main()
