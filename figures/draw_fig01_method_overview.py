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
    # The small logical canvas makes labels remain legible after full-width
    # reduction on an ICRA page. PNG and vector PDF are emitted together.
    fig = plt.figure(figsize=(12.2, 4.65), dpi=240, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ---------------------------------------------------------------------
    # Left: the coupled baseline and four user-replaceable failure frames.
    # ---------------------------------------------------------------------
    label(ax, 0.157, 0.948, "Conventional force-aware VLA",
          size=12.2, weight="bold")
    label(ax, 0.157, 0.907, "one model predicts the complete action",
          size=7.8, color=SUBTLE)

    panel(ax, 0.036, 0.706, 0.242, 0.150, face=PALE_BLUE,
          edge=HAIRLINE, lw=0.8, radius=0.008)
    label(ax, 0.157, 0.829, "Vision   Language   State   Force",
          size=7.8)
    arrow(ax, (0.157, 0.811), (0.157, 0.784), color=HAIRLINE, lw=0.75)
    panel(ax, 0.073, 0.738, 0.168, 0.048, face="white",
          edge=HAIRLINE, lw=0.7, radius=0.006)
    label(ax, 0.157, 0.762, "Unified VLA policy", size=8.5, weight="bold")
    arrow(ax, (0.157, 0.735), (0.157, 0.704), color=INK, lw=0.8)
    label(ax, 0.157, 0.684, "full action chunk", size=8.2, weight="bold")

    label(ax, 0.157, 0.634, "contact changes can outpace action updates",
          size=7.8, color=ACCENT_RED, weight="bold")
    arrow(ax, (0.157, 0.666), (0.157, 0.646), color=ACCENT_RED,
          lw=0.8, dashed=True)

    card_w, card_h = 0.126, 0.220
    positions = [(0.022, 0.354), (0.164, 0.354),
                 (0.022, 0.092), (0.164, 0.092)]
    for pos, title, path in zip(positions, FAILURE_LABELS, FAILURE_IMAGES):
        image_card(ax, *pos, card_w, card_h, title, path)

    # Thin brace-like separator, matching the understated pi paper figures.
    ax.plot([0.314, 0.314], [0.083, 0.870], color=INK, lw=0.75)
    ax.plot([0.306, 0.314], [0.870, 0.870], color=INK, lw=0.75)
    ax.plot([0.306, 0.314], [0.083, 0.083], color=INK, lw=0.75)

    # ---------------------------------------------------------------------
    # Right: one large policy area, then an asynchronous execution timeline.
    # ---------------------------------------------------------------------
    label(ax, 0.655, 0.948, "ForceDelta-VLA", size=12.2, weight="bold")
    label(ax, 0.655, 0.907,
          "distill paired corrections offline; execute them independently",
          size=7.8, color=SUBTLE)

    panel(ax, 0.344, 0.525, 0.624, 0.330, face=POLICY_BLUE,
          edge=HAIRLINE, lw=0.8, radius=0.010)
    label(ax, 0.656, 0.825, "Teacher-guided residual supervision",
          size=9.4, weight="bold")

    # Teacher and its two matched operating modes.
    panel(ax, 0.365, 0.615, 0.142, 0.148, face=CREAM_2,
          edge=HAIRLINE, lw=0.7, radius=0.007)
    label(ax, 0.436, 0.733, "Frozen temporal teacher",
          size=8.0, weight="bold")
    label(ax, 0.436, 0.697, "shared context + noise", size=6.9,
          color=SUBTLE)
    panel(ax, 0.384, 0.638, 0.104, 0.038, face=FORCE_PALE,
          edge=FORCE_ORANGE, lw=0.7, radius=0.005)
    label(ax, 0.436, 0.657, "full force", size=7.5, weight="bold")

    panel(ax, 0.535, 0.704, 0.135, 0.058, face="white",
          edge=HAIRLINE, lw=0.7, radius=0.006)
    label(ax, 0.6025, 0.742, "force-conditioned", size=7.3)
    token_strip(ax, 0.548, 0.710, 0.109, FORCE_ORANGE, count=6)
    panel(ax, 0.535, 0.620, 0.135, 0.058, face="white",
          edge=HAIRLINE, lw=0.7, radius=0.006)
    label(ax, 0.6025, 0.658, "missing-force", size=7.3)
    token_strip(ax, 0.548, 0.626, 0.109, "#6FA083", count=6)
    arrow(ax, (0.507, 0.708), (0.532, 0.733), color=INK, lw=0.7)
    arrow(ax, (0.507, 0.668), (0.532, 0.649), color=INK, lw=0.7)

    label(ax, 0.700, 0.690, "$-$", size=14, weight="bold")
    arrow(ax, (0.671, 0.733), (0.691, 0.704), color=INK, lw=0.7)
    arrow(ax, (0.671, 0.649), (0.691, 0.679), color=INK, lw=0.7)
    panel(ax, 0.724, 0.664, 0.106, 0.062, face=FORCE_PALE,
          edge=FORCE_ORANGE, lw=0.8, radius=0.007)
    label(ax, 0.777, 0.695, r"$\Delta A^{force}$", size=8.8, weight="bold")

    panel(ax, 0.724, 0.566, 0.142, 0.072, face=STALE_PALE,
          edge=STALE_PURPLE, lw=0.8, radius=0.007)
    label(ax, 0.795, 0.613, r"$\Delta A^{stale}$", size=8.5, weight="bold")
    label(ax, 0.795, 0.586, r"missing $-$ reference $+\,\Gamma$",
          size=6.5, color=SUBTLE)

    panel(ax, 0.879, 0.673, 0.066, 0.046, face="white",
          edge=HAIRLINE, lw=0.7, radius=0.006)
    label(ax, 0.912, 0.696, "paired targets", size=6.5, weight="bold")
    arrow(ax, (0.831, 0.695), (0.876, 0.695), color=INK, lw=0.75)
    arrow(ax, (0.868, 0.602), (0.895, 0.670), color=STALE_PURPLE,
          lw=0.7, connection="arc3,rad=-0.18")

    # Async deployment: sparse reference packets and dense residual packets.
    label(ax, 0.656, 0.474, "Deploy asynchronously", size=9.5,
          weight="bold")
    label(ax, 0.350, 0.402, "Reference worker", size=8.2, weight="bold",
          ha="left")
    label(ax, 0.350, 0.370, "vision + language + state", size=6.9,
          color=SUBTLE, ha="left")
    panel(ax, 0.502, 0.356, 0.145, 0.070, face=PALE_BLUE,
          edge=HAIRLINE, lw=0.75, radius=0.007)
    label(ax, 0.5745, 0.391, r"cache $A^{ref}, Z^{intent}, S_k$",
          size=7.5, weight="bold")
    arrow(ax, (0.467, 0.390), (0.498, 0.390), color=INK, lw=0.75)

    label(ax, 0.350, 0.280, "Residual worker", size=8.2, weight="bold",
          ha="left")
    label(ax, 0.350, 0.248, "wrench + state + time", size=6.9,
          color=SUBTLE, ha="left")
    panel(ax, 0.502, 0.222, 0.145, 0.080, face=STALE_PALE,
          edge=HAIRLINE, lw=0.75, radius=0.007)
    label(ax, 0.5745, 0.271, "compact residual policy", size=7.3,
          weight="bold")
    label(ax, 0.5745, 0.243,
          r"$\Delta A^{force}+\Delta A^{stale}$", size=7.2)
    arrow(ax, (0.467, 0.260), (0.498, 0.260), color=INK, lw=0.75)
    arrow(ax, (0.5745, 0.353), (0.5745, 0.305), color=INK, lw=0.75)

    panel(ax, 0.704, 0.280, 0.105, 0.076, face="white",
          edge=HAIRLINE, lw=0.8, radius=0.007)
    label(ax, 0.7565, 0.329, r"$A^{ref}+\Delta A$", size=8.4, weight="bold")
    label(ax, 0.7565, 0.301, "compose pose", size=7.0)
    arrow(ax, (0.648, 0.390), (0.701, 0.340), color=INK, lw=0.75)
    arrow(ax, (0.648, 0.260), (0.701, 0.300), color=INK, lw=0.75)
    arrow(ax, (0.810, 0.318), (0.845, 0.318), color=INK, lw=0.9)
    panel(ax, 0.849, 0.279, 0.102, 0.078, face=ACTION_GREEN,
          edge=HAIRLINE, lw=0.75, radius=0.007)
    label(ax, 0.900, 0.341, "pose command", size=7.5, weight="bold")
    token_strip(ax, 0.866, 0.288, 0.068, "#769A65", count=5)

    # Two simple packet timelines communicate rate separation without numbers.
    x0, x1 = 0.397, 0.936
    ax.plot([x0, x1], [0.153, 0.153], color=HAIRLINE, lw=0.65)
    ax.plot([x0, x1], [0.096, 0.096], color=HAIRLINE, lw=0.65)
    label(ax, 0.350, 0.153, "reference", size=6.8, ha="left")
    label(ax, 0.350, 0.096, "residual", size=6.8, ha="left")
    for x in (0.440, 0.635, 0.830):
        ax.add_patch(Rectangle((x, 0.143), 0.044, 0.020,
                               facecolor=PALE_BLUE, edgecolor=HAIRLINE,
                               linewidth=0.65, zorder=4))
    for idx in range(13):
        x = 0.415 + idx * 0.039
        ax.add_patch(Rectangle((x, 0.087), 0.021, 0.018,
                               facecolor=FORCE_PALE, edgecolor=FORCE_ORANGE,
                               linewidth=0.55, zorder=4))
    label(ax, 0.663, 0.040,
          "reuse task-level motion; update contact corrections independently",
          size=8.3, weight="bold")

    fig.savefig(OUTPUT_PDF, bbox_inches="tight", pad_inches=0,
                facecolor="white")
    fig.savefig(OUTPUT_PNG, dpi=240, bbox_inches="tight", pad_inches=0,
                facecolor="white")
    plt.close(fig)
    print(OUTPUT_PDF)
    print(OUTPUT_PNG)


if __name__ == "__main__":
    main()
