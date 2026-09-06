"""Editable SVG architecture drawing, inspired by PI's pastel token diagrams.
All topology and labels describe ForceDelta-VLA, not the PI model architecture.
"""
from pathlib import Path
from html import escape
import fitz
OUT=Path(__file__).resolve().parent/'fig02_network_pi_style_v1'
W,H=1800,1100
INK='#263238'; EDGE='#72818A'
BLUE='#B9DCE7'; GREEN='#CFE0BD'; ORANGE='#F4D3AB'
PINK='#EFD4D9'; PURPLE='#DCCFE8'; GREY='#E1E6E9'; YELLOW='#F7E5AA'
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="white"/>']
def text(x,y,t,size=22,anchor='start',bold=False,color=INK):
 s.append(f'<text x="{x}" y="{y}" font-family="Helvetica,Arial,sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color}" text-anchor="{anchor}">{escape(t)}</text>')
def rect(x,y,w,h,fill='white',stroke=EDGE,r=6):
 s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.3"/>')
def line(x1,y1,x2,y2,color=EDGE,width=1.6):
 s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>')
def path(points,color=EDGE,arrow=True):
 s.append(f'<polyline points="{" ".join(f"{x},{y}" for x,y in points)}" fill="none" stroke="{color}" stroke-width="1.7" stroke-linejoin="round"/>')
 if arrow:
  x,y=points[-1];a,b=points[-2];dx,dy=x-a,y-b;ln=(dx*dx+dy*dy)**.5;ux,uy=dx/ln,dy/ln
  p=[(x,y),(x-9*ux+4*uy,y-9*uy-4*ux),(x-9*ux-4*uy,y-9*uy+4*ux)]
  s.append(f'<polygon points="{" ".join(f"{a},{b}" for a,b in p)}" fill="{color}"/>')
def tokens(x,y,n,color,width=25,gap=7):
 for i in range(n):rect(x+i*(width+gap),y,width,12,color,EDGE,5)
def box(x,y,w,h,title,sub='',fill='white',size=22):
 rect(x,y,w,h,fill)
 text(x+w/2,y+h/2+(0 if sub else 7),title,size,'middle')
 if sub:text(x+w/2,y+h/2+25,sub,18,'middle')
# Two training panels, separated by whitespace and one light rule.
text(30,36,'(a) Teacher and reference learning',25,bold=True)
text(650,36,'(b) Paired residual supervision',25,bold=True)
line(620,57,620,454,'#D8DFE3',1)
box(30,62,270,48,'1  Fine-tune teacher',fill='#F4F7F8',size=20)
path([(305,86),(320,86)])
box(325,62,265,48,'2  Learn missing-force mode',fill='#F4F7F8',size=18)
text(165,134,'Then freeze teacher weights',17,'middle')
text(458,134,'Train token + adapter only',17,'middle')
# PI-like backbone and action expert: token columns behind a white model bar.
for x,w,col in [(38,92,BLUE),(139,92,BLUE),(240,110,PINK),(368,218,GREEN)]:
 rect(x,176,w,109,col)
 tokens(x+9,187,max(2,int((w-10)/32)),col,22,7)
 tokens(x+9,259,max(2,int((w-10)/32)),col,22,7)
box(30,211,330,42,'Vision–language backbone',size=21)
box(360,211,230,42,'Action expert',size=22)
# Input encoders and labels.
for x in [43,144]:
 s.append(f'<polygon points="{x},331 {x+80},331 {x+67},302 {x+13},302" fill="{BLUE}" stroke="{EDGE}" stroke-width="1.3"/>')
 text(x+40,323,'ViT',18,'middle')
 path([(x+40,301),(x+40,287)])
box(37,346,194,43,'Multi-view images',fill='#F1F7F9',size=19)
path([(84,346),(84,332)]);path([(184,346),(184,332)])
box(244,322,106,59,'Instruction','L',PINK,size=18)
path([(297,321),(297,287)])
box(370,316,99,46,'State',fill=PURPLE,size=19)
path([(419,315),(419,287)])
box(480,316,107,46,'Force mode',fill=ORANGE,size=17)
path([(533,315),(533,287)])
text(478,390,'TCN(history) / missing token',17,'middle')
text(478,412,'Flow noise → action expert',18,'middle')
text(30,438,'Cache: context, reference action, query state',20)
# The two frozen teacher modes share context/noise at target extraction.
box(650,62,1118,58,'3  Schedule replay selects current time t and cached reference k',
    'Paired teacher queries share cached context Eₖ and flow noise εₖ',fill='#F4F7F8',size=22)
cols=[(650,'Force-conditioned teacher','Current state + wrench history',ORANGE),
      (1032,'Missing-force teacher','Current state + missing token',GREEN),
      (1414,'Cached reference','Interpolated at target timestamps',BLUE)]
for xx,title,sub,col in cols:box(xx,162,354,90,title,sub,col,size=21)
# A/B/C are explicitly named pose predictions, avoiding ambiguous subtraction ports.
text(827,287,'Conditioned pose',20,'middle')
text(1209,287,'Missing-force pose',20,'middle')
text(1591,287,'Reference pose',20,'middle')
path([(827,295),(827,316),(970,316),(970,340)])
path([(1209,295),(1209,316),(1090,316),(1090,340)])
path([(1209,295),(1209,327),(1390,327),(1390,340)])
path([(1591,295),(1591,316),(1510,316),(1510,340)])
box(845,341,370,76,'Force residual target','Conditioned pose − missing-force pose',ORANGE,size=23)
box(1270,341,370,76,'Staleness residual target','Missing-force pose − reference pose',PURPLE,size=23)
text(1209,452,'Distillation supervises the two residual outputs below.',20,'middle')
line(30,480,1770,480,'#CBD5DA',1.2)
# Residual architecture: repeated token columns and a shared white attention bar.
text(30,524,'(c) Residual policy',25,bold=True)
text(1300,524,'(d) Command composition',25,bold=True)
labels=[('Cached intent','Zₖ',BLUE),('Force embedding','Causal TCN',ORANGE),
 ('Current state','Sₜ',PURPLE),('Reference action','Aʳᵉᶠ(t)',GREEN),('Age / phase','ξₜ,ₖ',GREY),('Learned query','qᵣₑₛ',YELLOW)]
for i,(lab,sub,col) in enumerate(labels):
 xx=55+i*138
 text(xx+61,567,lab,18,'middle');text(xx+61,590,sub,16,'middle')
for yy,masked in [(625,False),(820,True)]:
 for i,(_,_,col) in enumerate(labels):
  xx=55+i*138;fill=GREY if masked and i==1 else col
  rect(xx,yy,122,120,fill)
  n=2 if i==0 else 1
  tokens(xx+((122-(n*30+(n-1)*8))/2),yy+13,n,fill,30,8)
  tokens(xx+((122-(n*30+(n-1)*8))/2),yy+95,n,fill,30,8)
  if masked and i==1:
   for dy in [13,95]:
    line(xx+44,yy+dy-2,xx+78,yy+dy+14,INK)
    line(xx+44,yy+dy+14,xx+78,yy+dy-2,INK)
 box(43,yy+40,838,43,'Shared attention Φ',size=23)
 text(55,yy+147,'Force token masked' if masked else 'Force token present',19)
 cy=yy+61
 path([(883,cy),(942,cy)])
 box(944,cy-29,270,58,'Staleness head' if masked else 'Force head',fill=PURPLE if masked else ORANGE,size=22)
text(450,1032,'Both passes share Φ; the output projections are separate.',20,'middle')
# Four independent inputs to composition; rebasing stays outside attention.
box(1300,565,430,58,'Cached reference action',fill=BLUE,size=23)
box(1300,657,430,58,'Force correction',fill=ORANGE,size=23)
box(1300,769,430,58,'Learned staleness correction',fill=PURPLE,size=22)
box(1300,881,430,66,'Deterministic rebasing Γ(Sₜ, Sₖ)','Current state + cached query state',GREY,size=21)
path([(1214,686),(1298,686)])
path([(1214,881),(1250,881),(1250,798),(1298,798)])
# Explicit cached-state source, rather than attributing rebasing to the network.
for cy in [594,686,798,914]:path([(1730,cy),(1752,cy)],arrow=False)
line(1752,594,1752,985)
path([(1752,985),(1515,985),(1515,1004)])
box(1300,1006,430,65,'Bound corrections; compose pose','Convert to absolute command using Sₖ',fill='#F4F7F8',size=21)
s.append('</svg>')
OUT.with_suffix('.svg').write_text('\n'.join(s))
d=fitz.open(OUT.with_suffix('.svg'))
pdf=fitz.open('pdf',d.convert_to_pdf());pdf.save(OUT.with_suffix('.pdf'))
pdf[0].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(OUT.with_suffix('.png'))
print(OUT)
