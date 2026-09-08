#!/usr/bin/env python3
"""Draw ForceDelta-VLA as a continuous fast--slow architecture."""
from html import escape
from pathlib import Path
import fitz

OUT=Path(__file__).resolve().parent/"fig02_architecture"
W,H=1900,880
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

# Three predictions feed two targets; rebasing belongs only to delay supervision.
section(24,20,1852,410,"CORRECTION TARGET CONSTRUCTION",BP)
tag(650,66,380,"Eₖ  ·  Sₜ  ·  shared noise εₖ",BLUE)
tag(52,143,250,"Wrench history  ℱₜ",ORANGE)
tag(52,242,250,"Force-agnostic input",GREY)
box(340,124,250,78,"Causal TCN","force encoding",ORANGE)
box(340,222,250,78,"Learned token + adapter","force-agnostic mode",GREY,ts=21)
arrow([(302,162),(336,162)]); arrow([(302,261),(336,261)])
box(650,124,380,176,"Frozen VLA teacher","paired queries",BLUE)
arrow([(590,163),(646,163)]); arrow([(590,261),(646,261)])
arrow([(840,104),(840,120)])
box(1090,86,340,74,"Force-conditioned prediction","at current state Sₜ",ORANGE,ts=21)
box(1090,205,340,74,"Force-agnostic prediction","at current state Sₜ",GREY,ts=21)
box(1090,321,340,68,"Previous reference action","queried at Sₖ · time-aligned",BLUE,ts=21,ss=17)
arrow([(1030,164),(1060,164),(1060,123),(1086,123)])
arrow([(1030,261),(1060,261),(1060,242),(1086,242)])
tag(660,335,365,"State rebasing  Γ(Sₜ,Sₖ)",PURPLE,size=21)
box(1510,90,330,90,"Force target","conditioned − agnostic",ORANGE)
box(1510,283,330,96,"Delay target","current agnostic − previous ref + Γ",PURPLE,ss=16)
# Both current predictions contribute to the force difference.
arrow([(1430,123),(1506,123)])
arrow([(1430,242),(1460,242),(1460,153),(1506,153)])
# Delay compares current agnostic and previous reference after state rebasing.
arrow([(1430,242),(1480,242),(1480,306),(1506,306)])
arrow([(1430,355),(1506,355)])
arrow([(1025,354),(1050,354),(1050,407),(1630,407),(1630,383)],color="#81649A")

section(24,454,1852,270,"CORRECTION POLICY",GP)
inputs=[(55,250,"Cached task context","from Eₖ",BLUE),(325,250,"Current wrench history","causal TCN",ORANGE),(595,210,"Current state","Sₜ",GREY),(825,280,"Reference-action segment","K time-aligned samples",BLUE),(1125,210,"Timing","age + phase",GREY)]
for x,w,a,b,c in inputs:box(x,511,w,78,a,b,c,ts=20,ss=17)
box(55,624,1280,70,"Shared attention module  Φ","two forward passes with shared parameters",GREEN,ts=24,ss=18)
for x in (180,450,700,965,1230):arrow([(x,589),(x,620)])
box(1390,504,440,86,"Force correction","with force input  ·  K steps",ORANGE)
box(1390,624,440,86,"Delay correction","force input masked  ·  K steps",PURPLE)
arrow([(1335,647),(1360,647),(1360,547),(1386,547)])
arrow([(1335,671),(1360,671),(1360,667),(1386,667)])
# Dashed target-to-head links run outside the output boxes.
arrow([(1840,135),(1867,135),(1867,445),(1600,445),(1600,500)],color="#A56C2A",width=1.7,dash="7 6")
arrow([(1840,331),(1850,331),(1850,607),(1600,607),(1600,620)],color="#81649A",width=1.7,dash="7 6")
text(1760,492,"distill",17,color="#6D7377",italic=True)

section(24,746,1852,114,"ACTION COMPOSITION",GREYP)
box(282,793,300,52,"Reference pose",fill=BLUE,ts=20); text(610,829,"+",30,weight="bold")
box(642,793,330,52,"Force correction",fill=ORANGE,ts=19); text(1000,829,"+",30,weight="bold")
box(1032,793,350,52,"Delay correction",fill=PURPLE,ts=18); arrow([(1394,819),(1470,819)])
box(1482,785,310,68,"Commanded pose","gripper follows reference action",GREEN,ts=23,ss=17)

s.append("</svg>"); OUT.with_suffix(".svg").write_text("\n".join(s))
doc=fitz.open(OUT.with_suffix(".svg")); pdf=fitz.open("pdf",doc.convert_to_pdf()); pdf.save(OUT.with_suffix(".pdf"))
pdf[0].get_pixmap(matrix=fitz.Matrix(1.35,1.35),alpha=False).save(OUT.with_suffix(".png")); print(OUT)
