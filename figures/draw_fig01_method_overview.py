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
                            STUDENT_FILL, COMMAND, COMMAND_EDGE, snowflake_segments, draw_input_icon)


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
    panel(ax,.03,.54,.605,.395,face="white",edge="#8DAFC9",radius=.013)
    panel(ax,.036,.886,.593,.043,face="#C9DFF2",edge="none",lw=0,radius=.009)
    label(ax,.048,.908,"Teacher-defined correction targets",size=10.0,weight="bold",ha="left",color="#254C6E")
    # Aligned modality cards organize inputs without adding method details.
    for y,h in [(.817,.064),(.746,.064),(.675,.064),(.574,.094)]:
        panel(ax,.041,y,.168,h,face="#E8EFF5",edge="none",lw=0,radius=.009,z=3)
    # Emoji-like vector pictograms keep the PDF portable and sharp.
    # Images and instruction supply cached context; state is current.
    panel(ax,.245,.665,.17,.15,face="#D5E5F3",edge="#45677F",radius=.011)
    ax.imshow(Image.open(ROOT/"icons/teacher.png"),extent=[.263,.296,.691,.768],aspect="auto",zorder=5)
    label(ax,.353,.725,"Force-aware\nteacher",size=7.8,weight="bold")
    for pts in snowflake_segments(.302,.765,.006,8.5/3.66):
        ax.plot(*zip(*pts),color=EDGE,lw=.85,zorder=5)

    # A single aligned column for all teacher inputs.
    ax.imshow(Image.open(ROOT/"icons/camera.png"),extent=[.048,.075,.823,.882],aspect="auto",zorder=5)
    label(ax,.09,.852,"Images",size=7.3,ha="left")
    ax.imshow(Image.open(ROOT/"icons/instruction.png"),extent=[.049,.074,.754,.808],aspect="auto",zorder=5)
    label(ax,.09,.781,"Instruction",size=7.3,ha="left")
    draw_input_icon(ax,"proprioception",.062,.708,.034,.070)
    label(ax,.09,.708,"Proprioception",size=7.3,ha="left")
    history_asset = ROOT / "inputs/fig02_force_history.png"
    if history_asset.exists():
        ax.imshow(Image.open(history_asset),extent=[.046,.078,.604,.654],aspect="auto",zorder=5)
    else:
        # Same illustrative history curve as Fig. 2; replace both from the shared asset.
        import numpy as np
        t_history=np.linspace(0,1,120)
        history_y=.654-.050*(.68-.25*np.sin(2*np.pi*t_history)*np.exp(-.9*t_history)-.15*t_history)
        ax.plot([.046,.046,.078],[.652,.604,.604],color=HAIRLINE,lw=.7,zorder=5)
        ax.plot(.047+.030*t_history,history_y,color=FORCE_EDGE,lw=1.3,zorder=5)
    label(ax,.09,.628,"Force History",size=7.0,ha="left",color=FORCE_EDGE)
    for y, text, face, edge in [(.635,"ON",FORCE_PALE,FORCE_EDGE),
                                 (.585,"OFF",PALE_BLUE,REFERENCE_EDGE)]:
        panel(ax,.174,y,.033,.026,face=face,edge=edge,lw=.7,radius=.012,z=4)
        label(ax,.1905,y+.013,text,size=6.3,color=edge,weight="bold")
    ax.plot([.217,.224,.224,.217],[.874,.874,.583,.583],color=EDGE,lw=.8,zorder=3)
    arrow(ax,(.225,.735),(.241,.735),color=INK,scale=6)
    panel(ax,.46,.718,.155,.088,face=FORCE_PALE,edge=FORCE_ACCENT)
    label(ax,.559,.762,"Force target",size=7.7,weight="bold")
    # A round pushbutton on a low base, with downward contact from the gripper.
    from matplotlib.patches import Ellipse
    draw_input_icon(ax,"proprioception",.484,.785,.022,.034,z=5)
    arrow(ax,(.484,.768),(.484,.751),color=FORCE_EDGE,lw=1.05,scale=6,z=7)
    panel(ax,.471,.726,.026,.009,face="#D6DBDE",edge="#66757D",
          lw=.65,radius=.002,z=5)
    ax.add_patch(Rectangle((.476,.737),.016,.006,facecolor="#C89C31",
                          edgecolor=FORCE_EDGE,lw=.65,zorder=6))
    ax.add_patch(Ellipse((.484,.737),.016,.009,facecolor="#C89C31",
                        edgecolor=FORCE_EDGE,lw=.65,zorder=6))
    ax.add_patch(Ellipse((.484,.745),.020,.012,facecolor="#FFE19A",
                        edgecolor=FORCE_EDGE,lw=.8,zorder=7))
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

    panel(ax,.03,.09,.605,.425,face="white",edge="#8EACA6",radius=.013)
    panel(ax,.036,.460,.593,.047,face="#CFE4DC",edge="none",lw=0,radius=.009)
    label(ax,.045,.487,"Slow reference + fast correction",size=10.5,weight="bold",ha="left")
    # Current sensing and cached visual-language context have distinct sources.
    panel(ax,.225,.401,.175,.046,face="#EDF2F5",edge="#667D8D",radius=.007)
    label(ax,.3125,.433,"Force history +",size=7.0,weight="bold")
    label(ax,.3125,.412,"proprioception",size=7.0,weight="bold")
    arrow(ax,(.405,.424),(.435,.424),scale=7)
    panel(ax,.225,.343,.175,.043,face=PALE_BLUE,edge=REFERENCE_EDGE,radius=.007)
    label(ax,.3125,.3645,"Cached task context",size=7.1)
    arrow(ax,(.405,.3645),(.435,.3645),color=REFERENCE_EDGE,scale=7)
    panel(ax,.44,.357,.175,.09,face=STUDENT_FILL)
    ax.imshow(Image.open(ROOT/"icons/student.png"),extent=[.45,.475,.369,.427],aspect="auto",zorder=5)
    label(ax,.549,.415,"Fast student",size=8.2,weight="bold")
    label(ax,.549,.379,"Correction policy",size=7.0,color=SUBTLE)
    # The slow worker uses the learned force-agnostic teacher mode.
    panel(ax,.048,.177,.15,.185,face="#D5E5F3",edge="#45677F",radius=.011)
    ax.imshow(Image.open(ROOT/"icons/teacher.png"),extent=[.058,.084,.287,.347],aspect="auto",zorder=5)
    for pts in snowflake_segments(.085,.343,.0045,8.5/3.66):
        ax.plot(*zip(*pts),color=EDGE,lw=.65,zorder=5)
    label(ax,.141,.327,"Slow teacher",size=7.6,weight="bold")
    for y, text, face, edge in [(.273,"ON","#F6F7F8","#BCC4C9"),
                                 (.232,"OFF",PALE_BLUE,REFERENCE_EDGE)]:
        panel(ax,.107,y,.068,.025,face=face,edge=edge,lw=.65,radius=.012)
        label(ax,.141,y+.0125,text,size=6.5,color=edge,weight="bold")
    label(ax,.123,.192,"Inference ~5 Hz",size=7.0,color=SUBTLE)
    # The slow teacher caches its visual-language context together with the reference.
    ax.plot([.202,.213,.213],[.327,.327,.3645],color=REFERENCE_EDGE,lw=1.1,zorder=3)
    arrow(ax,(.213,.3645),(.220,.3645),color=REFERENCE_EDGE,lw=1.1,scale=6)
    # A larger spatial sketch emphasizes the composition of the separately predicted force and delay corrections.
    panel(ax,.225,.12,.325,.205,face="#FBFDFC",edge="#91A7AF",lw=.85,radius=.011)
    arrow(ax,(.202,.222),(.220,.222),color=REFERENCE_EDGE,lw=1.1,scale=7)
    arrow(ax,(.49,.353),(.49,.330),color=JOINT_CORRECTION_EDGE,lw=1.1,scale=7)
    import numpy as np
    def trajectory_points(u):
        # A spatial sketch of paired reference and corrected poses. The two
        # endpoints coincide, while local corrections change direction along
        # the path. These are illustrative curves, not measured trajectories.
        x = .246 + .282*u
        envelope = np.sin(np.pi*u)**2
        ref_y = .231 + .005*u + .054*np.sin(2*np.pi*u)
        corrected_x = x + .006*envelope
        corrected_y = .231 + .005*u + .021*np.sin(2*np.pi*u) + .004*envelope
        return x,ref_y,corrected_x,corrected_y

    u = np.linspace(0,1,240)
    ref_x,ref_y,adjusted_x,adjusted_y = trajectory_points(u)
    ax.plot(ref_x,ref_y,color=REFERENCE_EDGE,lw=1.25,
            linestyle=(0,(1.4,1.7)),zorder=4)
    ax.plot(adjusted_x,adjusted_y,color=COMMAND_EDGE,lw=1.65,zorder=5)
    # One arrow color denotes the sum of the separately predicted force and delay corrections;
    # the arrows point from each reference pose to its adjusted counterpart.
    for position in [.15,.25,.35,.64,.75,.86]:
        rx,ry,cx,cy = trajectory_points(position)
        arrow(ax,(rx,ry),(cx,cy),color=JOINT_CORRECTION_EDGE,lw=.95,scale=5.2,z=6)
    # Read left to right: stored reference, predicted pose corrections, adjusted trajectory.
    ax.plot([.240,.255],[.143,.143],color=REFERENCE_EDGE,lw=1.2,linestyle=(0,(1.4,1.7)),zorder=5)
    label(ax,.259,.143,r"$A^{\mathrm{ref}}$",size=7.2,ha="left",color=REFERENCE_EDGE)
    arrow(ax,(.318,.133),(.318,.154),color=JOINT_CORRECTION_EDGE,lw=1,scale=5)
    label(ax,.329,.143,"Force + delay",size=6.6,ha="left",color=JOINT_CORRECTION_EDGE)
    ax.plot([.422,.437],[.143,.143],color=COMMAND_EDGE,lw=1.6,zorder=5)
    label(ax,.441,.143,"Adjusted trajectory",size=6.3,ha="left",color=COMMAND_EDGE)
    arrow(ax,(.554,.222),(.574,.222),color=INK,lw=1.1,scale=7)
    # Robot output with command transmission rate.
    robot_arm_icon(ax,.574,.159)
    label(ax,.604,.145,"100 Hz",size=7.4,weight="bold")

    # Both target branches feed the same distillation link to the student.
    ax.plot([.619,.632],[.762,.762],color=FORCE_ACCENT,lw=1.4,zorder=6)
    ax.plot([.619,.632],[.641,.641],color=DELAY_ACCENT,lw=1.4,zorder=6)
    ax.plot([.632,.632,.535],[.762,.565,.565],color=JOINT_CORRECTION_EDGE,
            lw=1.15,linestyle=(0,(3,2)),zorder=6)
    # Highlight correction distillation as the learning step between targets and student.
    arrow(ax,(.535,.561),(.535,.549),color="#80304F",lw=1.3,scale=7,z=8)
    panel(ax,.376,.477,.240,.065,face="#A83F68",edge="#80304F",lw=1.2,radius=.009,z=7)
    # A small glowing lightbulb emphasizes learning without adding method content.
    ax.add_patch(Ellipse((.397,.511),.032,.064,facecolor="#D883A2",
                        edgecolor="none",alpha=.65,zorder=8))
    ax.add_patch(Ellipse((.397,.516),.013,.027,facecolor="#FFFFFF",
                        edgecolor="#FFFFFF",lw=.9,zorder=9))
    ax.plot([.394,.394,.400,.400],[.506,.498,.498,.506],color="#FFFFFF",lw=.9,zorder=9)
    ax.plot([.394,.400],[.494,.494],color="#FFFFFF",lw=1.1,zorder=9)
    for dx,dy,ex,ey in [(-.009,0,-.013,0),(.009,0,.013,0),
                         (0,.018,0,.025),(-.007,.014,-.010,.020),(.007,.014,.010,.020)]:
        ax.plot([.397+dx,.397+ex],[.516+dy,.516+ey],color="#FFE2EB",lw=.7,zorder=9)
    label(ax,.513,.510,"Correction distillation",size=8.2,weight="bold",
          color="#FFFFFF",z=10)
    arrow(ax,(.535,.472),(.535,.453),color="#80304F",lw=1.5,scale=8,z=8)

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
