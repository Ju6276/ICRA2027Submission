#!/usr/bin/env python3
"""Paper-native vector figure: paired supervision and dual-correction policy.

Coordinates are schematic. Curves illustrate input types, not measured data.
Teacher queries share cached E_k, current S_t and noise; Gamma supervises delay.
The student is shown right-to-left to align its outputs with supervision targets.
"""
from html import escape
from pathlib import Path
import math
import fitz

OUT = Path(__file__).resolve().parent / 'fig02_architecture'
W,H=1900,800
from figure_palette import (INK, EDGE, NEUTRAL, REFERENCE as BLUE,
                            REFERENCE_EDGE as BLUE_D, FORCE as ORANGE,
                            FORCE_EDGE as ORANGE_D, DELAY as PURPLE,
                            DELAY_EDGE as PURPLE_D, COMMAND as GREEN,
                            snowflake_segments)
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="white"/>']

def text(x,y,v,size=23,anchor='middle',weight='normal',color=INK):
    s.append(f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(v)}</text>')
def rect(x,y,w,h,fill='white',stroke=EDGE,r=5,width=1.5):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')
def circle(x,y,r,fill='white',stroke=EDGE):
    s.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.7"/>')
def line(points,color=EDGE,width=1.8,dash=None,arrow=False):
    if dash:
        # Explicit dash segments survive SVG-to-PDF conversion in MuPDF.
        for (ax,ay),(bx,by) in zip(points,points[1:]):
            length=math.hypot(bx-ax,by-ay)
            for offset in range(0,int(length),13):
                end=min(offset+7,length)
                line([(ax+(bx-ax)*offset/length,ay+(by-ay)*offset/length),
                      (ax+(bx-ax)*end/length,ay+(by-ay)*end/length)],color,width)
        if arrow:
            bx,by=points[-1]; ax,ay=points[-2]; length=math.hypot(bx-ax,by-ay)
            line([(bx-(bx-ax)*2/length,by-(by-ay)*2/length),(bx,by)],color,width,arrow=True)
        return
    ds=''
    s.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{ds}/>')
    if arrow:
        x,y=points[-1];px,py=points[-2];dx,dy=x-px,y-py;n=max(math.hypot(dx,dy),1)
        ux,uy=dx/n,dy/n
        pts=[(x,y),(x-9*ux+4*uy,y-9*uy-4*ux),(x-9*ux-4*uy,y-9*uy+4*ux)]
        s.append(f'<polygon points="{" ".join(f"{a},{b}" for a,b in pts)}" fill="{color}"/>')
def tokens(x,y,fill,n=6,w=17,h=30):
    for i in range(n):rect(x+i*(w+4),y,w,h,fill,r=2,width=1)
def curve(x,y,w=125,h=35,color=ORANGE_D):
    line([(x,y),(x,y+h),(x+w,y+h)],color='#B7C1C6',width=1)
    points=[(x+i*w/40,y+h*.55+h*.24*math.sin(i*.42)+h*.12*math.sin(i*1.3)) for i in range(41)]
    line(points,color=color,width=2)
def state(x,y):
    line([(x-45,y+17),(x,y-6),(x+32,y+17),(x+53,y-4)],width=3)
    for a,b in [(x-45,y+17),(x,y-6),(x+32,y+17)]:circle(a,b,5,NEUTRAL)
    line([(x+45,y-11),(x+60,y+3)],width=2)
def clock(x,y):
    circle(x,y,17);line([(x,y-11),(x,y),(x+10,y)],width=2)

text(25,36,'(a) Teacher supervision',29,anchor='start',weight='bold')
text(1010,36,'(b) Dual-correction policy',29,anchor='start',weight='bold')
line([(977,62),(977,737)],color='#CDD5D9',width=1)

# Image and language pictograms describe the cached prefix source, not fresh input.
rect(45,82,111,72,NEUTRAL,r=3)
line([(57,144),(81,114),(111,137),(143,103)],color=BLUE_D,width=2)
circle(130,97,6,'white',BLUE_D)
text(101,183,'Query-time images',20)
rect(194,88,157,57,NEUTRAL,r=9)
line([(209,145),(207,155),(223,145)],width=1.5)
text(272,121,'“Insert the plug”',20)
text(272,183,'Instruction',20)
line([(101,190),(101,213),(166,213),(166,225)],arrow=True)
line([(272,190),(272,213),(229,213),(229,225)],arrow=True)
# Blue visual tokens and cream language tokens explicitly form cached E_k.
rect(123,223,146,37,'#F7FAFB',stroke='#AFC0C7',r=5,width=1)
for i in range(6):
    rect(132+i*21,230,15,23,'#DDE3E7' if i<3 else '#F5F6F7',r=2,width=1)
text(196,283,'Cached context Eₖ',22)
line([(273,241),(361,241),(361,261)],arrow=True)
text(500,194,'Shared noise εₖ',21)
line([(475,207),(475,260)],arrow=True)

# Current state and the two alternative force inputs are explicit.
state(120,305); text(122,354,'Current state Sₜ',23)
line([(194,314),(298,314)],arrow=True)
curve(57,390);text(122,458,'Force history ℱₜ',23,color=ORANGE_D)
line([(194,416),(298,416)],color=ORANGE_D,arrow=True)
circle(119,511,15,'#E6EBED');text(119,518,'z',21)
text(124,554,'Learned token',23)
line([(194,512),(273,512),(273,476),(298,476)],arrow=True)

# One frozen teacher, two modes; avoid expanding the encoder and adapter.
rect(300,265,205,240,NEUTRAL,r=13)
text(402,345,'VLA teacher',27,weight='bold')
for pts in snowflake_segments(402,297,15):line(pts,width=1.8)
line([(324,382),(480,382)],color='#A6BBC4',width=1)
text(402,417,'Paired queries',23)
text(402,452,'Two input modes',20,color=EDGE)
text(246,467,'or',20,color=EDGE)

# Predictions: colored sequence glyphs, not processing boxes.
text(641,249,'Force-conditioned',22,color=ORANGE_D)
tokens(578,266,ORANGE)
text(641,321,'Current state Sₜ',20,color=EDGE)
line([(505,322),(546,322),(546,281),(572,281)],arrow=True)
text(641,374,'Force-agnostic',22)
tokens(578,391,'#E6EBED')
text(641,447,'Current state Sₜ',20,color=EDGE)
line([(505,445),(540,445),(540,406),(572,406)],arrow=True)
text(641,532,'Previous reference',22,color=BLUE_D)
tokens(578,549,BLUE)
text(641,607,'From Sₖ; time-aligned',20,color=EDGE)

# Signed nodes explicitly implement conditioned-agnostic and agnostic-ref+Gamma.
circle(811,281,23,ORANGE)
text(811,289,'Σ',24)
line([(704,281),(786,281)],color=ORANGE_D,arrow=True);text(763,269,'+',21)
line([(704,406),(741,406),(741,318),(795,300)],arrow=True);text(768,330,'−',23)
line([(835,281),(857,281)],color=ORANGE_D,arrow=True)
text(903,249,'Force',23,weight='bold',color=ORANGE_D)
text(903,274,'target',23,weight='bold',color=ORANGE_D)
tokens(870,292,ORANGE,n=6,w=8,h=25)

circle(811,465,23,PURPLE);text(811,473,'Σ',24)
line([(704,406),(766,406),(798,445)],arrow=True);text(782,421,'+',21)
line([(704,564),(753,564),(796,485)],arrow=True);text(756,526,'−',23)
text(811,648,'Γ(Sₜ, Sₖ)',25,color=PURPLE_D)
text(780,680,'Reference-state',21,color=PURPLE_D)
text(780,707,'alignment',21,color=PURPLE_D)
line([(811,621),(811,491)],color=PURPLE_D,arrow=True);text(830,535,'+',21,color=PURPLE_D)
line([(835,465),(857,465)],color=PURPLE_D,arrow=True)
text(903,435,'Delay',23,weight='bold',color=PURPLE_D)
text(903,461,'target',23,weight='bold',color=PURPLE_D)
tokens(870,478,PURPLE,n=6,w=8,h=25)

# Panel (b) reads consistently left to right.
# Teacher supervision runs above the policy, outside the input/data-flow paths.
line([(941,305),(957,305),(957,71),(1566,71),(1566,286)],color=ORANGE_D,dash='6 5',arrow=True)
line([(941,491),(968,491),(968,96),(1633,96),(1633,474),(1607,489)],color=PURPLE_D,dash='6 5',arrow=True)
text(1270,134,'Teacher supervision',20,color=EDGE)

# Input bank: pooled E_k, current state, force history, reference and timing.
tokens(1044,177,NEUTRAL);text(1108,229,'Pooled task context',21)
state(1108,288);text(1108,337,'Current state Sₜ',21)
curve(1044,377);text(1108,443,'Recent force history',21,color=ORANGE_D)
tokens(1044,508,BLUE);text(1108,562,'Reference segment',21)
clock(1108,613);text(1108,662,'Timing: age + phase',21)
line([(1210,191),(1210,613)])
for y in [191,298,401,523,613]:line([(1175,y),(1210,y)])

# Shared attention evaluations and separate heads.
for cy,fill,letter in [(305,ORANGE,'F'),(491,PURPLE,'D')]:
    line([(1210,cy),(1254,cy)],arrow=True)
    for i,color in enumerate([NEUTRAL,'#E6EBED',ORANGE,BLUE,'#E6EBED']):
        x=1260+i*17
        rect(x,cy-17,12,34,color if cy==305 or i!=2 else '#F5F5F5',r=2,width=1)
        if cy==491 and i==2:
            line([(x-2,cy-19),(x+14,cy+19)],color=PURPLE_D,width=2)
            line([(x+14,cy-19),(x-2,cy+19)],color=PURPLE_D,width=2)
    line([(1344,cy),(1362,cy)],arrow=True)
    rect(1366,cy-36,85,72,NEUTRAL,r=9)
    text(1408,cy+12,'Φ',39)
    line([(1455,cy),(1471,cy)],arrow=True)
    circle(1494,cy,19,fill);text(1494,cy+8,letter,23)
    line([(1516,cy),(1532,cy)],arrow=True)
    tokens(1537,cy-14,fill,n=6,w=8,h=28)
line([(1408,345),(1408,451)],dash='6 5')
circle(1408,398,17,'white',stroke='white');text(1408,407,'=',30,color=EDGE)
text(1408,242,'Shared attention',22,weight='bold')
text(1569,355,'Force correction',21,color=ORANGE_D)
text(1569,543,'Delay correction',21,color=PURPLE_D)

# Composition follows the two outputs; a lower branch carries the reference pose.
line([(1610,305),(1720,305),(1720,372)],color=ORANGE_D,arrow=True)
line([(1610,491),(1720,491),(1720,428)],color=PURPLE_D,arrow=True)
line([(1040,523),(994,523),(994,712),(1668,712),(1668,400),(1692,400)],color=BLUE_D,arrow=True)
text(1420,744,'Reference pose',22,color=BLUE_D)
circle(1720,400,25,GREEN);text(1720,409,'+',30)
line([(1748,400),(1796,400)],arrow=True)
text(1829,313,'Absolute pose',21)
text(1829,342,'using Sₖ',20,color=EDGE)
# End-effector pose glyph: a simple parallel-jaw gripper.
rect(1820,360,22,25,GREEN,r=3,width=2)
rect(1799,385,65,22,GREEN,r=4,width=2)
line([(1805,407),(1805,438),(1817,438)],width=4)
line([(1858,407),(1858,438),(1846,438)],width=4)
text(1829,477,'Commanded',21,weight='bold')
text(1829,504,'pose',21,weight='bold')
text(25,771,'Sequence glyphs and force curves are schematic.',19,anchor='start',color=EDGE)

s.append('</svg>');OUT.with_suffix('.svg').write_text('\n'.join(s))
doc=fitz.open(OUT.with_suffix('.svg'));pdf=fitz.open('pdf',doc.convert_to_pdf());pdf.save(OUT.with_suffix('.pdf'))
pdf[0].get_pixmap(matrix=fitz.Matrix(1.15,1.15),alpha=False).save(OUT.with_suffix('.png'))
