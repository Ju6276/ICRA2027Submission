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

COMPARISON_IMAGES = [None, None]

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
    "font.family": "Arial",
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
    figure_aspect = 8.5 / 3.66
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
    fig, ax = plt.subplots(figsize=(8.5, 3.66))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis("off")
    panel(ax,.012,.045,.642,.88,face="#F4F7F7",edge="#F4F7F7",lw=0,radius=.014,z=0)
    panel(ax,.67,.045,.318,.88,face=CREAM_2,edge=CREAM_2,lw=0,radius=.014,z=0)
    label(ax,.333,.96,"ForceDelta-VLA",size=13,weight="bold")
    label(ax,.829,.96,"Real-robot outcome",size=11.5,weight="bold")

    # Training: four left-to-right groups with one connector between groups.
    label(ax,.032,.89,"Training",size=10.5,weight="bold",ha="left")
    panel(ax,.03,.55,.605,.30,face=POLICY_BLUE)
    label(ax,.092,.818,"Inputs",size=8.1,weight="bold")
    for ix,iy,name,color in [(.043,.75,"Image",PALE_BLUE),(.101,.75,"Language",CREAM),
                             (.043,.675,"State",ACTION_GREEN),(.101,.675,"Force",FORCE_PALE)]:
        panel(ax,ix,iy,.05,.052,face=color,radius=.006)
        label(ax,ix+.025,iy+.026,name,size=6.4,weight="bold")

    panel(ax,.18,.68,.125,.105,face=CREAM)
    label(ax,.2425,.748,"Frozen teacher",size=8.2,weight="bold")
    label(ax,.2425,.712,"matched context/noise",size=6.1)
    arrow(ax,(.156,.738),(.175,.738),scale=7)

    panel(ax,.335,.635,.14,.165,face="white",edge="#7D9099")
    label(ax,.405,.778,"Paired predictions",size=7.5,weight="bold")
    panel(ax,.347,.712,.116,.043,face=FORCE_PALE,radius=.005)
    label(ax,.405,.7335,"Force-conditioned",size=6.1,weight="bold")
    panel(ax,.347,.654,.116,.043,face=PALE_BLUE,radius=.005)
    label(ax,.405,.6755,"Force-agnostic base",size=5.9,weight="bold")
    arrow(ax,(.31,.738),(.33,.718),scale=7)

    panel(ax,.505,.635,.115,.165,face="white",edge="#7D9099")
    label(ax,.5625,.778,"Training targets",size=7.4,weight="bold")
    panel(ax,.517,.712,.091,.043,face=FORCE_PALE,radius=.005)
    label(ax,.5625,.7335,"Force correction",size=5.9,weight="bold")
    panel(ax,.517,.654,.091,.043,face=STALE_PALE,radius=.005)
    label(ax,.5625,.6755,"Delay correction",size=5.9,weight="bold")
    arrow(ax,(.48,.718),(.50,.718),scale=7)
    label(ax,.49,.744,"Δ",size=6.7,weight="bold",color=FORCE_ORANGE)
    label(ax,.332,.585,"paired teacher targets from offline demonstrations",size=7.2,weight="bold",color=SUBTLE)

    # Deployment: no crossing connectors; cached base action occupies its own lower lane.
    label(ax,.032,.505,"Deployment",size=10.5,weight="bold",ha="left")
    panel(ax,.03,.12,.605,.345,face="white",edge="#C8D0D4")
    label(ax,.092,.425,"Live inputs",size=7.5,weight="bold")
    panel(ax,.043,.352,.05,.052,face=ACTION_GREEN,radius=.006); label(ax,.068,.378,"State",size=6.4,weight="bold")
    panel(ax,.101,.352,.05,.052,face=FORCE_PALE,radius=.006); label(ax,.126,.378,"Force",size=6.4,weight="bold")
    panel(ax,.043,.278,.108,.048,face=PALE_BLUE,radius=.006); label(ax,.097,.302,"Task context",size=6.2,weight="bold")

    panel(ax,.185,.29,.15,.105,face=STALE_PALE)
    label(ax,.26,.356,"Distilled correction policy",size=7.3,weight="bold")
    label(ax,.26,.32,"2.43-ms forward pass",size=6.3,color=SUBTLE)
    arrow(ax,(.156,.354),(.18,.347),scale=7); arrow(ax,(.156,.302),(.18,.322),scale=7)

    panel(ax,.37,.315,.12,.062,face=FORCE_PALE); label(ax,.43,.346,"Force correction",size=6.5,weight="bold")
    panel(ax,.37,.232,.12,.062,face=STALE_PALE); label(ax,.43,.263,"Delay correction",size=6.5,weight="bold")
    arrow(ax,(.34,.35),(.365,.346),scale=7); arrow(ax,(.34,.327),(.365,.263),scale=7)

    panel(ax,.185,.16,.15,.062,face=PALE_BLUE); label(ax,.26,.191,"Cached base action",size=6.8,weight="bold")
    ax.add_patch(Circle((.535,.255),.016,facecolor="white",edgecolor=INK,lw=.8,zorder=4)); label(ax,.535,.255,"+",size=9,weight="bold")
    arrow(ax,(.495,.346),(.525,.272),scale=7); arrow(ax,(.495,.263),(.515,.257),scale=7)
    ax.plot([.34,.515],[.191,.191],color=INK,lw=.9,zorder=3)
    arrow(ax,(.515,.191),(.525,.241),scale=7)
    panel(ax,.57,.215,.052,.08,face=ACTION_GREEN); label(ax,.596,.264,"Action",size=6.7,weight="bold"); label(ax,.596,.238,"100 Hz",size=5.8,color=SUBTLE)
    arrow(ax,(.552,.255),(.565,.255),scale=7)

    label(ax,.332,.14,"cached base action + independent high-rate corrections",size=7.2,weight="bold",color=SUBTLE)

    for y,title,color,path in [(.52,"ForceVLA failure",ACCENT_RED,COMPARISON_IMAGES[0]),(.105,"ForceDelta-VLA success","#4E8A45",COMPARISON_IMAGES[1])]:
        panel(ax,.695,y,.268,.335,face="white",edge=color,lw=1.1,radius=.009)
        if path:
            source=Image.open(ROOT/path).convert("RGB")
            fitted=ImageOps.fit(source,(720,420),method=Image.Resampling.LANCZOS)
            ax.imshow(fitted,extent=[.708,.95,y+.045,y+.31],aspect="auto",zorder=3)
        else:
            ax.add_patch(Rectangle((.708,y+.045),.242,.265,facecolor=PLACEHOLDER,edgecolor="#B8B8B0",linewidth=.7,linestyle=(0,(3,2)),zorder=3))
            label(ax,.829,y+.178,"same task and initial condition",size=7.2,color="#888884")
        label(ax,.829,y+.022,title,size=9.2,weight="bold",color=color)
    for out in (OUTPUT_PDF,OUTPUT_PNG):
        fig.savefig(out,dpi=240,bbox_inches="tight",pad_inches=0,facecolor="white")
    plt.close(fig)

if __name__ == "__main__":
    main()
