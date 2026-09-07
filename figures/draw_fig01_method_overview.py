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
FAILURE_LABELS = ["Reference error", "Stale reference", "Jamming", "Nonlocal recovery"]
SETUP_IMAGES = ["fig04a_franka_platform.png", "fig04b_bimanual_platform.png"]

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
    "font.family": "Courier New",
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


def setup_card(ax, x, y, w, h, title, image_path):
    pad = 0.0
    title_h = 0.0
    source = Image.open(ROOT / image_path).convert("RGB")
    image_x0, image_x1 = x + pad, x + w - pad
    image_y0, image_y1 = y + title_h, y + h - pad
    available_w, available_h = image_x1 - image_x0, image_y1 - image_y0
    figure_aspect = 12.2 / 5.25
    source_aspect = source.width / source.height
    fitted_h = available_w * figure_aspect / source_aspect
    if fitted_h <= available_h:
        draw_w, draw_h = available_w, fitted_h
    else:
        draw_h = available_h
        draw_w = available_h * source_aspect / figure_aspect
    cx, cy = (image_x0 + image_x1) / 2, (image_y0 + image_y1) / 2
    ax.imshow(source, extent=[cx - draw_w / 2, cx + draw_w / 2,
                             cy - draw_h / 2, cy + draw_h / 2],
              aspect="auto", zorder=3)
    label(ax, x + w / 2, y + h + 0.018, title, size=7.2, weight="bold")




def main():
    fig, ax = plt.subplots(figsize=(12.2, 5.25))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
    panel(ax, .012, .045, .295, .865, face=CREAM_2, edge=CREAM_2,
          lw=0, radius=.014, z=0)
    panel(ax, .738, .045, .247, .865, face=CREAM_2, edge=CREAM_2,
          lw=0, radius=.014, z=0)
    panel(ax, .32, .185, .408, .39, face="#F4F7F7", edge="#F4F7F7",
          lw=0, radius=.014, z=0)
    label(ax, .16, .95, 'Conventional force-aware VLA', size=11.5, weight='bold')
    panel(ax, .035, .70, .25, .17, face=PALE_BLUE)
    label(ax, .16, .83, 'Vision / language / state / force', size=7.2)
    label(ax, .16, .775, 'Full-action prediction', size=10, weight='bold')
    label(ax, .16, .73, 'task-level motion + contact adjustment', size=6.8)
    label(ax, .16, .646, 'Contact changes can outpace\naction updates', size=8, color=ACCENT_RED)
    for (x,y), title, path in zip([(.025,.34),(.17,.34),(.025,.07),(.17,.07)], FAILURE_LABELS, FAILURE_IMAGES):
        image_card(ax, x, y, .125, .23, title, path)
    label(ax, .53, .95, 'ForceDelta-VLA', size=13, weight='bold')
    panel(ax, .345, .61, .375, .27, face=POLICY_BLUE)
    label(ax,.5325,.842,'Missing-force residual distillation',size=9.2,weight='bold')
    panel(ax,.365,.675,.145,.105,face=CREAM)
    label(ax,.4375,.745,'Frozen teacher',size=8.1,weight='bold')
    label(ax,.4375,.705,'force / missing-force modes',size=5.8)
    panel(ax,.55,.685,.15,.085,face='white')
    label(ax,.625,.7275,'Paired correction\ntargets',size=7.2,weight='bold')
    arrow(ax,(.515,.727),(.545,.727))
    # Supervision terminates on the same policy used online.
    arrow(ax,(.625,.68),(.625,.565),color=STALE_PURPLE,lw=1,dashed=True)
    label(ax,.654,.625,'Distill',size=7.5,color=STALE_PURPLE)
    label(ax, .5325, .545, 'Fast residual execution', size=9.0, weight='bold')
    label(ax,.375,.495,'Current force / state',size=6.4,ha='left')
    label(ax,.375,.445,'Reference + context',size=6.0,ha='left')
    panel(ax,.535,.425,.16,.10,face=STALE_PALE)
    label(ax,.615,.475,'Residual policy',size=8.0,weight='bold')
    arrow(ax,(.475,.49),(.53,.49))
    arrow(ax,(.475,.445),(.53,.455))
    panel(ax,.36,.275,.135,.09,face=PALE_BLUE)
    label(ax,.4275,.32,'Missing-force\nreference',size=6.8,weight='bold')
    panel(ax,.535,.275,.16,.09,face=ACTION_GREEN)
    label(ax,.615,.32,'Corrected action',size=7.2,weight='bold')
    arrow(ax,(.50,.32),(.53,.32))
    arrow(ax,(.615,.42),(.615,.37))

    label(ax, .85, .95, 'Robot platforms', size=11, weight='bold')
    setup_card(ax, .75, .54, .22, .31, 'Single-arm setup', SETUP_IMAGES[0])
    setup_card(ax, .75, .10, .22, .31, 'Bimanual setup', SETUP_IMAGES[1])
    for out in (OUTPUT_PDF, OUTPUT_PNG):
        fig.savefig(out,dpi=240,bbox_inches='tight',pad_inches=0,facecolor='white')
    plt.close(fig)

if __name__ == "__main__":
    main()
