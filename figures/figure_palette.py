"""Shared semantic palette for Figures 1--3 and a vector snowflake."""
import math
INK = '#202A30'
EDGE = '#647781'
NEUTRAL = '#EEF1F3'
BACKGROUND = '#F7F8F9'
# Shared data colors match Fig. 2's targets, heads, and reference chunks.
# Peach denotes the shared student module and the composed pose adjustment; it is a
# semantic color, not an RGB mixture of the separately supervised outputs.
REFERENCE = '#7FAFDC'
REFERENCE_EDGE = '#38688B'
FORCE = '#FFD05A'
FORCE_EDGE = '#80601C'
FORCE_ACCENT = FORCE_EDGE
DELAY = '#BFA3E0'
DELAY_EDGE = '#66428D'
DELAY_ACCENT = DELAY_EDGE
STUDENT_FILL = '#F4AF83'
STUDENT_ACCENT = '#DF925E'
JOINT_CORRECTION = STUDENT_ACCENT
JOINT_CORRECTION_EDGE = '#9A6444'
COMMAND = '#85A771'
COMMAND_EDGE = '#4E8A45'


def snowflake_segments(cx, cy, radius, yscale=1):
    for i in range(6):
        angle = math.pi * i / 3
        ux, uy = math.cos(angle), math.sin(angle)
        yield [(cx,cy),(cx+radius*ux,cy+radius*uy*yscale)]
        for side in [-1,1]:
            yield [(cx+.58*radius*ux,cy+.58*radius*uy*yscale),
                   (cx+radius*(.8*ux-side*.19*uy),
                    cy+radius*(.8*uy+side*.19*ux)*yscale)]


def draw_tcp_gripper(ax, cx, cy, width, height, z=5):
    """Compact mechanical two-finger gripper, with no face-like details."""
    from matplotlib.patches import FancyBboxPatch, Polygon
    def point(u, v):
        return cx + u * width, cy + v * height
    def rounded(u, v, w, h, fill, edge='#3F5666', layer=0, radius=.04):
        x, y1 = point(u, v)
        _, y2 = point(u, v+h)
        ax.add_patch(FancyBboxPatch((x,min(y1,y2)),w*width,abs(y2-y1),
            boxstyle=f"round,pad=0,rounding_size={width*radius}",
            facecolor=fill,edgecolor=edge,linewidth=.8,zorder=z+layer))
    # Wrist coupling and a small rounded actuator body.
    rounded(-.14,.35,.28,.17,'#465D6C')
    rounded(-.34,.07,.68,.32,'#E8EFF3',layer=1,radius=.08)
    rounded(-.27,.12,.54,.07,'#7AA8C6',edge='none',layer=2,radius=.025)
    # Articulated fingers surround an open grasping space; dark pads face inward.
    for side in [-1,1]:
        outline=[(.22,.09),(.35,.08),(.44,-.09),(.33,-.43),(.17,-.43),(.17,-.29),(.25,-.29),(.30,-.10)]
        ax.add_patch(Polygon([point(side*u,v) for u,v in outline],closed=True,
            facecolor='#B7CDDC',edgecolor='#3F5666',linewidth=.85,
            joinstyle='round',zorder=z+2))
        pad=[(.17,-.28),(.25,-.28),(.25,-.44),(.17,-.44)]
        ax.add_patch(Polygon([point(side*u,v) for u,v in pad],closed=True,
            facecolor='#334C5C',edgecolor='none',zorder=z+3))


def draw_input_icon(ax, kind, cx, cy, width, height, z=5):
    """Small outline modality icons for the method diagram."""
    from matplotlib.patches import FancyBboxPatch, Polygon, Ellipse
    def pt(u,v):
        return cx+u*width,cy+v*height
    edge='#40515D'
    if kind == 'proprioception':
        start=len(ax.patches)
        draw_tcp_gripper(ax,cx,cy,width,height,z=z)
        for i,p in enumerate(list(ax.patches)[start:]):
            p.set_facecolor('#40515D' if i in [0,4,6] else '#FFFFFF')
        return
    if kind in ['instruction','context']:
        x,y=pt(-.40,-.20); _,y2=pt(0,.40)
        ax.add_patch(FancyBboxPatch((x,min(y,y2)),.8*width,abs(y2-y),
            boxstyle=f'round,pad=0,rounding_size={width*.10}',
            facecolor='white',edgecolor=edge,lw=1.15,zorder=z))
        ax.add_patch(Polygon([pt(-.23,-.18),pt(-.30,-.43),pt(.03,-.18)],
            closed=False,facecolor='white',edgecolor=edge,lw=1.15,zorder=z+1))
        for u in [-.20,0,.20]:
            ax.add_patch(Ellipse(pt(u,.10),width*.07,abs(height)*.07,
                facecolor=edge,edgecolor='none',zorder=z+2))
    elif kind == 'timing':
        ax.add_patch(Ellipse(pt(0,0),width*.85,abs(height)*.85,
            facecolor='white',edgecolor=edge,lw=1.2,zorder=z))
        ax.plot(*zip(pt(0,.28),pt(0,0),pt(.23,0)),color=edge,lw=1.2,zorder=z+1)
    elif kind == 'reference':
        for u in [-.43,-.12,.19]:
            x,y=pt(u,-.28); _,y2=pt(u,.28)
            ax.add_patch(FancyBboxPatch((x,min(y,y2)),width*.24,abs(y2-y),
                boxstyle=f'round,pad=0,rounding_size={width*.025}',
                facecolor='white',edgecolor=edge,lw=.9,zorder=z))
