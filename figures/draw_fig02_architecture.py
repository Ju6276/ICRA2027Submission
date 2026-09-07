#!/usr/bin/env python3
"""Draw the compact three-panel ForceDelta-VLA architecture figure."""
from html import escape
from pathlib import Path
import fitz

OUT = Path(__file__).resolve().parent / "fig02_architecture"
W, H = 1900, 720
INK, EDGE, FAINT = "#26343B", "#647983", "#B9C5CA"
CREAM, BLUE, BLUE_PALE = "#FBF4E3", "#A9D8E7", "#E6F1F4"
GREEN, ORANGE, PURPLE = "#CDE5BE", "#F5CFA2", "#DCCBE8"
GREY, YELLOW = "#DEE5E8", "#F7E4A1"
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="white"/>']

def text(x,y,value,size=18,anchor="middle",weight="normal",color=INK):
    size = max(20, size * 1.55)
    s.append(f'<text x="{x}" y="{y}" font-family="Helvetica,Arial,sans-serif" font-size="{size}" '
             f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(value)}</text>')

def rect(x,y,w,h,fill="white",stroke=EDGE,radius=8,width=1.4,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" '
             f'stroke="{stroke}" stroke-width="{width}"{d}/>')

def line(x1,y1,x2,y2,color=EDGE,width=1.5,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"{d}/>')

def arrow(points,color=EDGE,width=1.5,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    pts=" ".join(f"{x},{y}" for x,y in points)
    s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"{d}/>')
    x,y=points[-1]; px,py=points[-2]; dx,dy=x-px,y-py; n=max((dx*dx+dy*dy)**.5,1e-6); ux,uy=dx/n,dy/n
    tips=[(x,y),(x-8*ux+4*uy,y-8*uy-4*ux),(x-8*ux-4*uy,y-8*uy+4*ux)]
    s.append(f'<polygon points="{" ".join(f"{a},{b}" for a,b in tips)}" fill="{color}"/>')

def pill(x,y,w,h,value,fill,size=15,weight="normal"):
    rect(x,y,w,h,fill=fill,radius=h/2); text(x+w/2,y+h/2+size*.34,value,size,weight=weight)

def title(x,letter,value):
    text(x,42,f"({letter})",25,"start","bold"); text(x+58,42,value,25,"start","bold")

def token_row(x,y,count,color,width=20,gap=8):
    for i in range(count): rect(x+i*(width+gap),y,width,12,color,radius=6,width=1.0)

# Two semantic groups: target construction, then prediction and execution.
rect(18,62,585,630,CREAM,CREAM,14,0)
rect(648,62,1234,630,"#F4F7F7","#F4F7F7",14,0)
line(625,25,625,695,FAINT,1.1)

# (a) Paired teacher predictions and targets.
title(30,"a","Paired teacher targets")
pill(58,88,175,36,"prefix Eₖ",BLUE,14); pill(246,88,135,36,"state Sₜ",GREY,12)
pill(394,88,174,36,"noise εₖ",GREY,12)
rect(92,158,438,68,BLUE,radius=9); text(311,188,"frozen VLA teacher",20,weight="bold")
text(311,211,"shared backbone and action expert",13)
for cx in (145,311,477): arrow([(cx,126),(cx,155)])
pill(48,270,185,42,"force history -> TCN",ORANGE,13); pill(369,270,186,42,"missing-force token",BLUE_PALE,13)
rect(48,342,235,70,ORANGE,radius=8); text(165,370,"force-conditioned",15,weight="bold"); text(165,395,"current prediction",12)
rect(320,342,235,70,BLUE_PALE,radius=8); text(437,370,"missing-force",15,weight="bold"); text(437,395,"current prediction",12)
arrow([(141,315),(141,339)]); arrow([(462,315),(462,339)])
arrow([(260,226),(260,326),(165,326),(165,339)])
arrow([(350,226),(350,326),(437,326),(437,339)])
rect(48,486,238,68,ORANGE,radius=8); text(167,514,"force target",16,weight="bold"); text(167,538,"conditioned - missing",11)
rect(316,486,239,68,PURPLE,radius=8); text(435,511,"staleness target",16,weight="bold")
text(435,532,"missing - reference",10); text(435,547,"+ rebasing",10)
arrow([(165,415),(165,483)]); arrow([(437,415),(437,483)])
arrow([(437,430),(437,454),(245,454),(245,483)])
pill(316,606,238,36,"cached reference (query k)",BLUE,11); text(435,671,"aligned at tⱼ",10)
arrow([(435,606),(435,557)])

# (b) The shared residual policy and its online composition.
title(660,"b","Residual policy and execution"); text(1030,92,"same typed conditioning set",15)
labels=[(755,"intent",BLUE),(864,"force",ORANGE),(973,"state",GREY),(1082,"reference",BLUE),(1191,"time",GREY)]
for x,value,color in labels:
    rect(x,120,94,72,color,radius=7); token_row(x+23,139,2 if value=="intent" else 1,color); text(x+47,181,value,12)
pill(684,225,225,38,"force token present",ORANGE,13)
pill(1151,225,225,38,"force token masked",GREY,13)
line(802,205,1238,205)
for x,_,_ in labels: line(x+47,192,x+47,205)
arrow([(797,205),(797,222)]); arrow([(1264,205),(1264,222)])
rect(714,305,634,72,"white",radius=9); text(1031,337,"shared set attention Φ",20,weight="bold")
text(1031,361,"evaluated twice with residual query",13)
arrow([(797,266),(797,302)]); arrow([(1264,266),(1264,302)])
rect(684,420,225,64,ORANGE,radius=28); text(796,448,"force head",17,weight="bold"); text(796,471,"K-step correction",12)
rect(1151,420,225,64,PURPLE,radius=28); text(1263,448,"staleness head",17,weight="bold"); text(1263,471,"K-step correction",12)
arrow([(797,380),(797,417)]); arrow([(1264,380),(1264,417)])
# Compact online composition closes the loop without a third apparent stage.
rect(680,582,205,50,BLUE,radius=8); text(782,613,"cached reference",13)
text(905,615,"+",22,weight="bold")
rect(928,582,205,50,ORANGE,radius=8); text(1030,613,"force correction",13)
text(1153,615,"+",22,weight="bold")
rect(1176,582,220,50,PURPLE,radius=8); text(1286,613,"staleness correction",12)
arrow([(1402,607),(1450,607)])
rect(1456,574,270,66,"white",radius=9); text(1591,604,"commanded pose",17,weight="bold")
text(1591,626,"based at cached state Sₖ",11)
pill(1464,657,254,28,"gripper from reference",BLUE_PALE,11)
arrow([(796,487),(796,560),(1030,560),(1030,579)])
arrow([(1263,487),(1263,560),(1286,560),(1286,579)])

s.append("</svg>"); OUT.with_suffix(".svg").write_text("\n".join(s))
doc=fitz.open(OUT.with_suffix(".svg")); pdf=fitz.open("pdf",doc.convert_to_pdf()); pdf.save(OUT.with_suffix(".pdf"))
pdf[0].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(OUT.with_suffix(".png")); print(OUT)
