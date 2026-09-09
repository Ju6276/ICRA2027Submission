#!/usr/bin/env python3
"""Draw the Fig. 1 teaser in the visual language of the pi-series papers.

Populate COMPARISON_IMAGES with paths relative to this directory to replace
the two author-reserved rollout placeholders without changing the layout.
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, FancyBboxPatch, Rectangle, PathPatch
from matplotlib.path import Path as MplPath
from PIL import Image, ImageOps
from figure_palette import (INK, EDGE, NEUTRAL, BACKGROUND, REFERENCE, REFERENCE_EDGE, FORCE,
                            FORCE_ACCENT, FORCE_EDGE, DELAY, DELAY_ACCENT,
                            DELAY_EDGE, JOINT_CORRECTION, JOINT_CORRECTION_EDGE,
                            STUDENT_FILL, COMMAND, COMMAND_EDGE, snowflake_segments)


ROOT = Path(__file__).resolve().parent
OUTPUT_PDF = ROOT / "fig01_method_overview.pdf"
OUTPUT_PNG = ROOT / "fig01_method_overview.png"
OUTPUT_SVG = ROOT / "fig01_method_overview.svg"

COMPARISON_IMAGES = [None, None]


SUBTLE = "#58616A"
HAIRLINE = "#66717A"
CREAM = "#F4EEDC"
CREAM_2 = "#FAF6EA"
POLICY_BLUE = "#BFD6DF"
PALE_BLUE = REFERENCE
ACTION_GREEN = COMMAND
FORCE_PALE = FORCE
DELAY_PALE = DELAY
ACCENT_RED = "#D94F43"
PLACEHOLDER = "#ECECE8"


plt.rcParams.update({
    "font.family": "Arial",
    "mathtext.fontset": "dejavusans",
    "svg.fonttype": "none",
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


def robot_arm_icon(ax, x, y, scale=.00065):
    """Compact articulated arm with circular joints and a parallel gripper."""
    from matplotlib.patches import Ellipse, Polygon
    aspect = 8.5 / 3.9 * (.952 - .015)
    def point(px, py):
        return x + scale*px, y + scale*aspect*py
    def stroke(points, color, width, z=5):
        ax.plot(*zip(*(point(*p) for p in points)),color=color,lw=width,
                solid_capstyle="round",solid_joinstyle="round",zorder=z)
    # Stable pedestal and two shaped links.
    ax.add_patch(Polygon([point(*p) for p in [(60,8),(94,8),(83,32),(70,32)]],
                         closed=True,facecolor=INK,edgecolor=INK,lw=.5,zorder=4))
    for start,end in [((77,39),(53,73)),((53,73),(23,82))]:
        stroke([start,end],INK,6.0)
        stroke([start,end],"#DCE3E7",3.9,z=6)
    stroke([(23,82),(20,69)],INK,3.1,z=5)
    for px,py,radius in [(77,39,10),(53,73,9),(23,82,7)]:
        ax.add_patch(Ellipse(point(px,py),2*radius*scale,2*radius*scale*aspect,
                             facecolor="white",edgecolor=INK,lw=.85,zorder=7))
        ax.add_patch(Ellipse(point(px,py),radius*scale,radius*scale*aspect,
                             facecolor=INK,edgecolor="none",zorder=8))
    # Simple, open parallel fingers in the reference blue.
    stroke([(10,67),(29,67)],REFERENCE_EDGE,2.0,z=7)
    stroke([(10,67),(10,56),(14,52)],REFERENCE_EDGE,1.8,z=7)
    stroke([(29,67),(29,56),(25,52)],REFERENCE_EDGE,1.8,z=7)


def action_strip(ax, x, y, w, face, edge, count=5):
    gap = .0018
    cell_w = (w - gap * (count - 1)) / count
    for i in range(count):
        ax.add_patch(Rectangle((x + i * (cell_w + gap), y), cell_w, .025,
                               facecolor=face, edgecolor=edge, lw=.6, zorder=4))


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




def smooth_sequence(ax, points, color, lw=1.3):
    path = MplPath(points, [MplPath.MOVETO] + [MplPath.CURVE4] * 3)
    ax.add_patch(PathPatch(path, facecolor="none", edgecolor=color,
                           linewidth=lw, capstyle="round", zorder=4))


def main():
    fig, ax = plt.subplots(figsize=(8.5, 3.9))
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.set(xlim=(0, 1), ylim=(.015, .952)); ax.axis("off")
    panel(ax,.012,.025,.642,.919,face="#F4F7F7",edge="#F4F7F7",lw=0,radius=.014,z=0)
    panel(ax,.67,.025,.318,.919,face=BACKGROUND,edge=BACKGROUND,lw=0,radius=.014,z=0)

    # Conceptual overview: preparation, paired predictions, and two distinct targets.
    panel(ax,.03,.54,.605,.36,face="white",edge="#C8D0D4")
    # Emoji-like vector pictograms keep the PDF portable and sharp.
    # Images and instruction supply cached context; state is current.
    panel(ax,.245,.665,.17,.15,face=NEUTRAL)
    ax.imshow(Image.open(ROOT/"icons/teacher.png"),extent=[.263,.296,.691,.768],aspect="auto",zorder=5)
    label(ax,.353,.725,"Force-aware\nteacher",size=7.8,weight="bold")
    for pts in snowflake_segments(.302,.765,.006,8.5/3.66):
        ax.plot(*zip(*pts),color=EDGE,lw=.85,zorder=5)

    # A single aligned column for all teacher inputs.
    ax.imshow(Image.open(ROOT/"icons/camera.png"),extent=[.048,.075,.823,.882],aspect="auto",zorder=5)
    label(ax,.09,.852,"Images",size=6.8,ha="left")
    ax.imshow(Image.open(ROOT/"icons/instruction.png"),extent=[.049,.074,.754,.808],aspect="auto",zorder=5)
    label(ax,.09,.781,"Instruction",size=6.8,ha="left")
    ax.plot([.051,.062,.073,.078],[.694,.715,.702,.717],color=EDGE,lw=1,zorder=4)
    for x,y in [(.051,.694),(.062,.715),(.073,.702)]:
        ax.plot(x,y,marker="o",markersize=2.2,color=EDGE,zorder=5)
    label(ax,.09,.708,"State",size=6.8,ha="left")
    ax.imshow(Image.open(ROOT/"icons/force.png"),extent=[.048,.075,.599,.658],aspect="auto",zorder=5)
    label(ax,.09,.628,"Force History",size=6.5,ha="left",color=FORCE_EDGE)
    for y, text, face, edge in [(.635,"ON",FORCE_PALE,FORCE_EDGE),
                                 (.585,"OFF",PALE_BLUE,REFERENCE_EDGE)]:
        panel(ax,.174,y,.033,.026,face=face,edge=edge,lw=.7,radius=.012)
        label(ax,.1905,y+.013,text,size=6.3,color=edge,weight="bold")
    ax.plot([.217,.224,.224,.217],[.874,.874,.583,.583],color=EDGE,lw=.8,zorder=3)
    arrow(ax,(.225,.735),(.241,.735),color=INK,scale=6)
    panel(ax,.46,.718,.155,.088,face=FORCE_PALE,edge=FORCE_ACCENT)
    label(ax,.553,.762,"Force target",size=7.7,weight="bold")
    # Contact force: fingertip presses down onto a surface.
    panel(ax,.477,.761,.010,.032,face="white",edge=FORCE_EDGE,lw=.7,radius=.004)
    ax.plot([.472,.494],[.735,.735],color=FORCE_EDGE,lw=1.1,zorder=5)
    arrow(ax,(.482,.758),(.482,.739),color=FORCE_EDGE,lw=.8,scale=5)
    ax.plot([.473,.47],[.747,.753],color=FORCE_EDGE,lw=.6,zorder=5)
    ax.plot([.491,.494],[.747,.753],color=FORCE_EDGE,lw=.6,zorder=5)
    panel(ax,.46,.588,.155,.106,face=DELAY_PALE,edge=DELAY_ACCENT)
    label(ax,.553,.641,"Delay target",size=7.7,weight="bold")
    # Stopwatch icon for the delay target.
    from matplotlib.patches import Ellipse
    ax.add_patch(Ellipse((.482,.636),.024,.024*8.5/3.9,facecolor="white",edgecolor=DELAY_EDGE,lw=.95,zorder=5))
    ax.plot([.482,.482],[.662,.671],color=DELAY_EDGE,lw=1.5,zorder=5)
    ax.plot([.478,.486],[.673,.673],color=DELAY_EDGE,lw=1.7,solid_capstyle="round",zorder=5)
    ax.plot([.491,.495],[.655,.664],color=DELAY_EDGE,lw=1.6,zorder=5)
    ax.plot([.482,.487],[.636,.650],color=DELAY_EDGE,lw=1,zorder=6)
    ax.plot(.482,.636,marker="o",markersize=1.6,color=DELAY_EDGE,zorder=6)
    arrow(ax,(.42,.762),(.455,.762),scale=8)
    arrow(ax,(.42,.675),(.455,.675),scale=7)
    action_strip(ax,.302,.604,.056,PALE_BLUE,REFERENCE_EDGE)
    label(ax,.33,.573,r"$A^{\mathrm{ref}}$",size=9,color=REFERENCE_EDGE)
    arrow(ax,(.33,.66),(.33,.634),color=REFERENCE_EDGE,scale=6)
    arrow(ax,(.363,.6165),(.455,.6165),scale=7)

    label(ax,.032,.505,"Slow reference + fast correction",size=10.5,weight="bold",ha="left")
    panel(ax,.03,.09,.605,.389,face="white",edge="#C8D0D4")
    panel(ax,.23,.335,.16,.09,face=NEUTRAL)
    label(ax,.31,.393,"Force history + state",size=6.5,weight="bold")
    label(ax,.31,.358,"Cached task context",size=6.8)
    arrow(ax,(.395,.38),(.435,.38),scale=7)
    panel(ax,.44,.335,.175,.09,face=STUDENT_FILL)
    ax.imshow(Image.open(ROOT/"icons/student.png"),extent=[.45,.475,.347,.405],aspect="auto",zorder=5)
    label(ax,.549,.393,"Fast student",size=7.8,weight="bold")
    label(ax,.549,.357,"Correction policy",size=6.5,color=SUBTLE)
    # The slow worker is the same teacher's learned force-agnostic mode.
    panel(ax,.05,.13,.15,.17,face=NEUTRAL)
    ax.imshow(Image.open(ROOT/"icons/teacher.png"),extent=[.06,.086,.224,.284],aspect="auto",zorder=5)
    for pts in snowflake_segments(.087,.28,.0045,8.5/3.66):
        ax.plot(*zip(*pts),color=EDGE,lw=.65,zorder=5)
    label(ax,.143,.262,"Slow teacher",size=7.2,weight="bold")
    # Only the learned force-agnostic mode generates execution references.
    for y, text, face, edge in [(.213,"ON","#F6F7F8","#BCC4C9"),
                                 (.174,"OFF",PALE_BLUE,REFERENCE_EDGE)]:
        panel(ax,.109,y,.068,.025,face=face,edge=edge,lw=.65,radius=.012)
        label(ax,.143,y+.0125,text,size=6.1,color=edge,weight="bold")
    label(ax,.125,.145,"~6 Hz",size=6.8,color=SUBTLE)
    # One local trajectory panel receives the reference and the joint correction.
    panel(ax,.26,.132,.28,.152,face="#FBFDFC",edge="#91A7AF",lw=.85,radius=.011)
    arrow(ax,(.204,.208),(.255,.208),color=REFERENCE_EDGE,lw=1.1,scale=7)
    arrow(ax,(.49,.331),(.49,.289),color=JOINT_CORRECTION_EDGE,lw=1.1,scale=7)
    import numpy as np
    def trajectory_points(u):
        # A spatial sketch of paired reference and corrected poses. The two
        # endpoints coincide, while local corrections change direction along
        # the path. These are illustrative curves, not measured trajectories.
        x = .282 + .236*u
        envelope = np.sin(np.pi*u)**2
        ref_y = .204 + .005*u + .050*np.sin(2*np.pi*u)
        corrected_x = x + .006*envelope
        corrected_y = .204 + .005*u + .019*np.sin(2*np.pi*u) + .004*envelope
        return x,ref_y,corrected_x,corrected_y

    u = np.linspace(0,1,240)
    ref_x,ref_y,adjusted_x,adjusted_y = trajectory_points(u)
    ax.plot(ref_x,ref_y,color=REFERENCE_EDGE,lw=1.25,
            linestyle=(0,(1.4,1.7)),zorder=4)
    ax.plot(adjusted_x,adjusted_y,color=COMMAND_EDGE,lw=1.65,zorder=5)
    # One arrow color denotes the student's joint force-and-delay correction;
    # the arrows point from each reference pose to its adjusted counterpart.
    for position in [.15,.25,.35,.64,.75,.86]:
        rx,ry,cx,cy = trajectory_points(position)
        arrow(ax,(rx,ry),(cx,cy),color=JOINT_CORRECTION_EDGE,lw=.8,scale=4.5,z=6)
    label(ax,.303,.157,r"$A^{\mathrm{ref}}$",size=8.3,color=REFERENCE_EDGE)
    label(ax,.424,.266,"Adjusted trajectory",size=6.6,color=COMMAND_EDGE)
    arrow(ax,(.544,.208),(.57,.208),color=INK,lw=1.1,scale=7)
    # Robot output with command transmission rate.
    robot_arm_icon(ax,.57,.145)
    label(ax,.601,.131,"100 Hz",size=7.4,weight="bold")

    # Both targets feed one short supervision connection to the student below.
    ax.plot([.619,.628,.628,.535],[.762,.762,.565,.565],color=FORCE_ACCENT,lw=.85,linestyle=(0,(3,2)),zorder=6)
    ax.plot([.535,.535],[.584,.565],color=DELAY_ACCENT,lw=.85,linestyle=(0,(3,2)),zorder=6)
    arrow(ax,(.535,.565),(.535,.431),color=JOINT_CORRECTION_EDGE,dashed=True,lw=.85,scale=6,z=6)
    label(ax,.522,.514,"Correction supervision",size=6.4,color=SUBTLE,ha="right")

    for y,title,color,path in [(.535,"ForceVLA failure",ACCENT_RED,COMPARISON_IMAGES[0]),(.09,"ForceDelta-VLA success","#4E8A45",COMPARISON_IMAGES[1])]:
        panel(ax,.685,y,.288,.40,face="white",edge=color,lw=1.1,radius=.009)
        if path:
            source=Image.open(ROOT/path).convert("RGB")
            fitted=ImageOps.fit(source,(720,420),method=Image.Resampling.LANCZOS)
            ax.imshow(fitted,extent=[.698,.96,y+.045,y+.375],aspect="auto",zorder=3)
        else:
            ax.add_patch(Rectangle((.698,y+.045),.262,.33,facecolor=PLACEHOLDER,edgecolor="#B8B8B0",linewidth=.7,linestyle=(0,(3,2)),zorder=3))
            label(ax,.829,y+.21,"same task and initial condition",size=7.2,color="#888884")
        label(ax,.829,y+.022,title,size=9.2,weight="bold",color=color)
    for out in (OUTPUT_PDF,OUTPUT_PNG,OUTPUT_SVG):
        fig.savefig(out,dpi=240,bbox_inches="tight",pad_inches=0,facecolor="white")
    OUTPUT_SVG.write_text("\n".join(line.rstrip() for line in OUTPUT_SVG.read_text().splitlines()) + "\n")
    plt.close(fig)

if __name__ == "__main__":
    main()
