#!/usr/bin/env python3
"""Draw ForceDelta-VLA as a continuous fast--slow architecture."""
from html import escape
from pathlib import Path
import fitz

OUT=Path(__file__).resolve().parent/"fig02_architecture"
W,H=1900,760
INK,EDGE="#202A30","#586B74"
BLUE,BP="#BFDDEB","#E9F3F7"; GREEN,GP="#CBE4BE","#EDF6E9"
ORANGE="#F2C99D"; PURPLE="#D8C9E5"; GREY,GREYP="#DDE4E7","#F5F7F8"
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',f'<rect width="{W}" height="{H}" fill="white"/>']

def text(x,y,v,size=22,anchor="middle",weight="normal",color=INK,italic=False):
    s.append(f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-style="{"italic" if italic else "normal"}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(v)}</text>')
def rect(x,y,w,h,fill="white",stroke=EDGE,r=8,width=1.5,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ""
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"{d}/>')
def arrow(points,color=EDGE,width=1.8,dash=None):
    d=f' stroke-dasharray="{dash}"' if dash else ""; pts=" ".join(f"{x},{y}" for x,y in points)
    s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"{d}/>')
    x,y=points[-1]; px,py=points[-2]; dx,dy=x-px,y-py; n=max((dx*dx+dy*dy)**.5,1e-6); ux,uy=dx/n,dy/n
    p=[(x,y),(x-10*ux+5*uy,y-10*uy-5*ux),(x-10*ux-5*uy,y-10*uy+5*ux)]
    s.append(f'<polygon points="{" ".join(f"{a},{b}" for a,b in p)}" fill="{color}"/>')
def box(x,y,w,h,a,b="",fill="white",ts=23,ss=18,r=8):
    rect(x,y,w,h,fill=fill,r=r); cy=y+h/2
    text(x+w/2,cy-(7 if b else -7),a,ts,weight="bold")
    if b:text(x+w/2,cy+20,b,ss)
def tag(x,y,w,label,fill,size=19):
    rect(x,y,w,38,fill=fill,r=19,width=1.2); text(x+w/2,y+26,label,size)
def section(x,y,w,h,label,fill):
    rect(x,y,w,h,fill=fill,stroke=fill,r=14,width=0); text(x+18,y+31,label,23,anchor="start",weight="bold")

section(24,20,1852,286,"OFFLINE  ·  PAIRED TEACHER TARGET CONSTRUCTION",BP)
tag(650,65,430,"Eₖ  ·  Sₜ  ·  shared noise εₖ",BLUE)
tag(52,132,250,"Wrench history  ℱₜ",ORANGE); tag(52,240,250,"Force-agnostic input",GREY)
box(340,112,250,78,"Causal TCN","force encoding",ORANGE)
box(340,220,250,78,"Learned token + adapter","token + low-rank adapter",GREY,ts=21)
arrow([(302,151),(336,151)]); arrow([(302,259),(336,259)])
box(650,112,430,186,"Frozen VLA teacher","paired force-conditioned and force-agnostic queries",BLUE)
arrow([(590,151),(646,151)]); arrow([(590,259),(646,259)])
arrow([(865,103),(865,108)])
box(1130,66,330,90,"Force-conditioned","current action chunk",ORANGE)
box(1130,192,330,90,"Base action","current prediction",GREY)
arrow([(1080,158),(1105,158),(1105,111),(1126,111)]); arrow([(1080,252),(1105,252),(1105,237),(1126,237)])
box(1550,66,296,90,"Force target","force-conditioned − base",ORANGE)
box(1550,192,296,90,"Delay target","current base − cached base + Γ(Sₜ,Sₖ)",PURPLE,ts=21,ss=15)
arrow([(1460,111),(1546,111)]); arrow([(1460,237),(1546,237)])

section(24,326,1852,266,"ONLINE  ·  SHARED CORRECTION POLICY",GP)
inputs=[(55,250,"Cached task context","from Eₖ",BLUE),(325,250,"Current wrench history","causal TCN",ORANGE),(595,210,"Current state","Sₜ",GREY),(825,280,"Base-action segment","aligned to t₁ … tₖ",BLUE),(1125,210,"Timing","age + phase",GREY)]
for x,w,a,b,c in inputs:box(x,380,w,78,a,b,c,ts=20,ss=17)
box(55,492,1280,70,"Shared set-attention backbone  Φ","typed condition tokens + learned correction query",GREEN,ts=24,ss=18)
for x in (180,450,700,965,1230):arrow([(x,458),(x,488)])
box(1390,354,440,92,"Force correction","force token present  ·  K steps",ORANGE)
box(1390,474,440,92,"Delay correction","force token masked  ·  K steps",PURPLE)
arrow([(1335,515),(1360,515),(1360,400),(1386,400)]); arrow([(1335,539),(1360,539),(1360,520),(1386,520)])

section(24,612,1852,124,"ASYNCHRONOUS ACTION COMPOSITION",GREYP)
box(282,660,300,52,"Cached base pose",fill=BLUE,ts=20); text(610,696,"+",30,weight="bold")
box(642,660,330,52,"Force correction",fill=ORANGE,ts=19); text(1000,696,"+",30,weight="bold")
box(1032,660,350,52,"Delay correction",fill=PURPLE,ts=18); arrow([(1394,686),(1470,686)])
box(1482,651,310,70,"Commanded pose","gripper follows base action",GREEN,ts=23,ss=17)
arrow([(1698,282),(1698,320),(1610,320),(1610,350)],color="#A56C2A",width=1.7,dash="7 6")
arrow([(1742,282),(1742,462),(1610,462),(1610,470)],color="#81649A",width=1.7,dash="7 6")
text(1748,320,"distill",17,anchor="start",color="#6D7377",italic=True)

s.append("</svg>"); OUT.with_suffix(".svg").write_text("\n".join(s))
doc=fitz.open(OUT.with_suffix(".svg")); pdf=fitz.open("pdf",doc.convert_to_pdf()); pdf.save(OUT.with_suffix(".pdf"))
pdf[0].get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False).save(OUT.with_suffix(".png")); print(OUT)
