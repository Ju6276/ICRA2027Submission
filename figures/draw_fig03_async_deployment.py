#!/usr/bin/env python3
"""Draw the asynchronous cached-packet protocol for Figure 3."""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle


ROOT = Path(__file__).resolve().parent
OUTPUT_PDF = ROOT / "fig03_async_deployment.pdf"
OUTPUT_PNG = ROOT / "fig03_async_deployment.png"

INK = "#171717"
MUTED = "#657078"
REF = "#759EAD"
REF_PALE = "#DCE9ED"
OLD = "#92999D"
OLD_PALE = "#E4E5E3"
CREAM = "#F4EEDC"
FIELD = "#EAF1F3"


plt.rcParams.update({
    "font.family": "DejaVu Sans Mono",
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
    fig = plt.figure(figsize=(7.8, 2.95), dpi=220, facecolor="white")
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # Shared execution field.
    ax.add_patch(FancyBboxPatch(
        (0.235, 0.105), 0.735, 0.805,
        boxstyle="round,pad=0.004,rounding_size=0.012",
        facecolor=FIELD, edgecolor="none", zorder=0,
    ))

    ys = {"reference": 0.785, "residual": 0.485, "steps": 0.205}
    labels = [
        ("reference worker", ys["reference"]),
        ("residual query", ys["residual"]),
        ("correction steps", ys["steps"]),
    ]
    for text, y in labels:
        ax.text(0.210, y, text, ha="right", va="center",
                fontsize=8.5, fontweight="bold", color=INK)
        arrow(ax, 0.238, y, 0.958, y, color=MUTED, width=0.65)

    # Reference queries and completion time.
    rounded(ax, 0.292, 0.690, 0.253, 0.190, r"query $k$", CREAM, size=10.5)
    rounded(ax, 0.610, 0.690, 0.253, 0.190, r"query $k{+}1$", CREAM, size=10.5)
    ax.text(0.292, 0.916, r"request $t_k$", fontsize=7.2,
            color=MUTED, ha="left", va="bottom")
    ax.text(0.610, 0.916, r"request $t_{k+1}$", fontsize=7.2,
            color=MUTED, ha="left", va="bottom")

    publish_x = 0.550
    ax.plot([publish_x, publish_x], [0.125, 0.900], color=REF,
            linewidth=0.9, linestyle=(0, (4, 3)), zorder=1)
    rounded(ax, publish_x + 0.010, 0.596, 0.202, 0.070,
            r"publish $C_k$ at $\bar t_k$", "white", size=7.2)

    # Residual queries. The middle query starts before C_k is published.
    query_xs = [0.250, 0.443, 0.636]
    query_colors = [(OLD_PALE, OLD), (OLD_PALE, OLD), (REF_PALE, REF)]
    for x, (face, edge) in zip(query_xs, query_colors):
        ax.add_patch(Circle((x, ys["residual"]), 0.013,
                            facecolor=face, edgecolor=edge,
                            linewidth=0.8, zorder=4))
        ax.plot([x, x], [ys["residual"] - 0.018, 0.345],
                color=edge, linewidth=0.65, linestyle=(0, (1, 3)), zorder=2)

    # Brackets identify the immutable cached packet used at query time.
    chunks = [
        (0.2580, 0.4430, OLD),
        (0.4505, 0.6355, OLD),
        (0.6430, 0.8285, REF),
    ]
    for left, right, color in chunks:
        ax.plot([left, right], [0.345, 0.345], color=color, linewidth=0.8)
        ax.plot([left, left], [0.345, 0.323], color=color, linewidth=0.8)
        ax.plot([right, right], [0.345, 0.323], color=color, linewidth=0.8)
    ax.text(0.538, 0.370, r"generated from $C_{k-1}$",
            ha="right", va="bottom", fontsize=6.7, color=OLD)
    ax.text(0.656, 0.370, r"generated from $C_k$",
            ha="left", va="bottom", fontsize=6.7, color=REF)

    # Published K-step correction samples. Two samples execute after C_k is
    # available but retain old fill because their query read C_{k-1}.
    start, gap, width, height = 0.258, 0.0385, 0.031, 0.100
    for idx in range(15):
        x = start + idx * gap
        if idx < 8:
            face, edge, style = OLD_PALE, OLD, "-"
        elif idx < 10:
            face, edge, style = OLD_PALE, REF, (0, (2, 2))
        else:
            face, edge, style = REF_PALE, REF, "-"
        ax.add_patch(FancyBboxPatch(
            (x, ys["steps"] - height / 2), width, height,
            boxstyle="round,pad=0.001,rounding_size=0.004",
            facecolor=face, edgecolor=edge, linewidth=0.75,
            linestyle=style, zorder=4,
        ))

    ax.text(0.264, 0.105, r"$K$-step residual chunk", ha="left",
            va="top", fontsize=6.7, color=OLD)
    ax.text(0.585, 0.105, "new reference affects the next residual query",
            ha="left", va="top", fontsize=6.5, color=REF)

    fig.savefig(OUTPUT_PDF, bbox_inches="tight", pad_inches=0,
                facecolor="white")
    fig.savefig(OUTPUT_PNG, dpi=220, bbox_inches="tight", pad_inches=0,
                facecolor="white")
    plt.close(fig)
    print(OUTPUT_PDF)
    print(OUTPUT_PNG)


if __name__ == "__main__":
    main()
