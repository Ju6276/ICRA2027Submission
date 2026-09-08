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
INK,EDGE='#202A30','#647781'
BLUE,BLUE_D='#D8E8EE','#668C9C'
ORANGE,ORANGE_D='#F8DEC2','#B6793D'
PURPLE,PURPLE_D='#E7DDF0','#8D70A7'
GREEN='#E7EEDC'
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
    for a,b in [(x-45,y+17),(x,y-6),(x+32,y+17)]:circle(a,b,5,BLUE)
    line([(x+45,y-11),(x+60,y+3)],width=2)
def clock(x,y):
    circle(x,y,17);line([(x,y-11),(x,y),(x+10,y)],width=2)

text(25,36,'(a) Teacher supervision',29,anchor='start',weight='bold')
text(1010,36,'(b) Dual-correction policy',29,anchor='start',weight='bold')
line([(977,62),(977,737)],color='#CDD5D9',width=1)

# Image and language pictograms describe the cached prefix source, not fresh input.
rect(45,82,111,72,BLUE,r=3)
line([(57,144),(81,114),(111,137),(143,103)],color=BLUE_D,width=2)
circle(130,97,6,'white',BLUE_D)
text(101,183,'Query-time images',20)
rect(194,88,157,57,'#F4EEDC',r=9)
line([(209,145),(207,155),(223,145)],width=1.5)
text(272,121,'“Insert the plug”',20)
text(272,183,'Instruction',20)
line([(45,197),(45,205),(351,205),(351,197)],width=1.2)
text(198,233,'Cached context Eₖ',23)
line([(355,225),(400,225),(400,260)],arrow=True)
text(500,194,'Shared noise εₖ',21)
line([(475,207),(475,260)],arrow=True)

# Current state and the two alternative force inputs are explicit.
state(120,305); text(122,354,'Current state Sₜ',23)
line([(194,314),(298,314)],arrow=True)
curve(57,390);text(122,458,'Force history ℱₜ',23,color=ORANGE_D)
line([(194,416),(298,416)],color=ORANGE_D,arrow=True)
circle(119,511,15,'#E6EBED');text(119,518,'z',21)
text(124,554,'Learned force-agnostic input',19)
line([(194,512),(273,512),(273,476),(298,476)],arrow=True)

# One frozen teacher, two modes; avoid expanding the encoder and adapter.
rect(300,265,205,240,BLUE,r=13)
text(402,325,'Frozen VLA',27,weight='bold');text(402,359,'teacher',27,weight='bold')
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

# Short, aligned supervision lines bridge teacher targets and policy outputs.
line([(941,305),(1060,305)],color=ORANGE_D,dash='6 5',arrow=True)
line([(941,491),(1060,491)],color=PURPLE_D,dash='6 5',arrow=True)
text(1001,379,'Supervision',19)
text(1130,273,'Force correction',23,weight='bold',color=ORANGE_D)
tokens(1070,290,ORANGE)
text(1130,459,'Delay correction',23,weight='bold',color=PURPLE_D)
tokens(1070,476,PURPLE)
line([(1300,305),(1210,305)],color=ORANGE_D,arrow=True)
line([(1300,491),(1210,491)],color=PURPLE_D,arrow=True)

# One shared module, with both passes made visible in its annotations.
rect(1300,249,240,297,GREEN,r=13)
text(1420,285,'Shared attention',25,weight='bold')
text(1420,317,'module Φ',25,weight='bold')
line([(1318,338),(1522,338)],color='#BAC8AE',width=1)
text(1420,370,'Force pass',23,color=ORANGE_D)
text(1420,398,'All inputs',21)
text(1420,451,'Delay pass',23,color=PURPLE_D)
text(1420,479,'Force token masked',20)
text(1420,523,'Two passes · shared weights',18,color=EDGE)

# Student inputs: cached context, state, force, reference, timing.
tokens(1690,118,BLUE);text(1753,169,'Cached task context',22)
state(1753,226);text(1753,274,'Current state Sₜ',22)
curve(1690,313);text(1753,379,'Recent force history',22,color=ORANGE_D)
tokens(1690,428,BLUE);text(1753,482,'Reference segment',22)
clock(1753,538);text(1753,587,'Timing: age + phase',22)
# The bus groups inputs only; masking is done inside the delay pass.
line([(1632,133),(1632,539)],color=EDGE)
for y in [133,236,337,443,538]:line([(1680,y),(1632,y)])
line([(1632,398),(1544,398)],arrow=True)

# Continue panel (b) with explicit composition and an end-effector target glyph.
# Read the pose component of the same reference segment; no extra Gamma term.
line([(1253,483),(1253,499)],color='white',width=8)
line([(1198,305),(1253,305),(1253,659),(1348,678)],color=ORANGE_D,arrow=True)
line([(1198,491),(1228,491),(1228,719),(1348,702)],color=PURPLE_D,arrow=True)
line([(1814,443),(1861,443),(1861,617),(1370,617),(1370,663)],color=BLUE_D,arrow=True)
text(1548,605,'Reference pose',22,color=BLUE_D)
circle(1370,690,25,GREEN)
text(1370,699,'+',30)
line([(1398,690),(1620,690)],arrow=True)
text(1507,663,'To absolute pose',21)
text(1507,724,'using Sₖ',21,color=EDGE)
# Target coordinate frame and gripper outline, not an additional network block.
circle(1685,685,48,'#F4F7EF',stroke='#D4DDC9')
line([(1685,693),(1737,693)],color='#AF6B60',width=2,arrow=True)
line([(1685,693),(1685,643)],color='#6D936A',width=2,arrow=True)
line([(1685,693),(1655,715)],color=BLUE_D,width=2,arrow=True)
line([(1665,671),(1699,671),(1699,681),(1691,681)],width=2.7)
line([(1665,671),(1665,681),(1673,681)],width=2.7)
line([(1682,655),(1682,670)],width=2.7)
text(1685,758,'Commanded pose',24,weight='bold')
text(25,771,'Sequence glyphs and force curves are schematic.',19,anchor='start',color=EDGE)

s.append('</svg>');OUT.with_suffix('.svg').write_text('\n'.join(s))
doc=fitz.open(OUT.with_suffix('.svg'));pdf=fitz.open('pdf',doc.convert_to_pdf());pdf.save(OUT.with_suffix('.pdf'))
pdf[0].get_pixmap(matrix=fitz.Matrix(1.15,1.15),alpha=False).save(OUT.with_suffix('.png'))
