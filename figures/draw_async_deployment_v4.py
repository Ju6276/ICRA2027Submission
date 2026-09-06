"""Minimal reference-binding schematic; timings are illustrative."""
from pathlib import Path
from html import escape
import fitz
OUT = Path(__file__).resolve().parent / 'fig03_async_deployment_v4'
W,H=1120,430
INK,OLD,BLUE='#26343D','#687784','#2479AE'
X,S=230,100
x=lambda t:X+S*t
s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">','<rect width="100%" height="100%" fill="white"/>']
def text(a,b,t,size=20,col=INK,anchor='start',bold=False):
 s.append(f'<text x="{a}" y="{b}" font-family="Helvetica,Arial,sans-serif" font-size="{size}" fill="{col}" text-anchor="{anchor}" font-weight="{"bold" if bold else "normal"}">{escape(t)}</text>')
def line(a,b,c,d,col=INK,width=1.5):
 s.append(f'<line x1="{a}" y1="{b}" x2="{c}" y2="{d}" stroke="{col}" stroke-width="{width}"/>')
def rect(a,b,w,h,fill,stroke,r=3):
 s.append(f'<rect x="{a}" y="{b}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="1.7"/>')
def arrow(a,b,c,d,col=INK):
 line(a,b,c,d,col)
 pts=f'{c},{d} {c-8},{d-4} {c-8},{d+4}' if b==d else f'{c},{d} {c-4},{d-8} {c+4},{d-8}'
 s.append(f'<polygon points="{pts}" fill="{col}"/>')
# Three lanes: no sample slots or predicted horizons.
for yy in [84,198]:line(X,yy,1080,yy,'#CAD2D8')
for yy,a,b in [(75,'Reference','inference'),(187,'Residual','inference'),(322,'Applied','corrections')]:
 text(22,yy,a,22,bold=True);text(22,yy+27,b,22,bold=True)
ready=2.3
# One dashed line: reference publication, distinct from command adoption.
for yy in range(106,358,12):
 if not 140 <= yy <= 164: line(x(ready),yy,x(ready),min(yy+6,358),BLUE)
rect(x(.3),62,x(ready)-x(.3),44,'#E7F2F8',BLUE)
text((x(.3)+x(ready))/2,91,'Query k',21,BLUE,'middle')
text(x(ready)+14,125,'Reference k available',21,BLUE)
queries=[(0,0,.65,'k−1'),(1,2,2.7,'k−1'),(2,4.8,5.5,'k')]
for q,start,end,ref in queries:
 c=BLUE if ref=='k' else OLD
 rect(x(start),176,x(end)-x(start),44,'#E7F2F8' if ref=='k' else '#EDF0F2',c)
 text((x(start)+x(end))/2,205,f'q{q}',20,c,'middle')
 text(x(start),159,f'Binds {ref}',20,c)
# Highlight the only interval the figure needs to explain.
line(x(ready),268,x(5.5),268,OLD)
line(x(ready),262,x(ready),274,OLD)
line(x(5.5),262,x(5.5),274,OLD)
text((x(ready)+x(5.5))/2,254,'Old binding retained',20,OLD,'middle')
# Continuous execution band; query labels identify the supplying result.
rect(x(0),310,x(5.5)-x(0),48,'#DEE4E8',OLD,r=0)
rect(x(5.5),310,x(8.4)-x(5.5),48,'#C6E2F2',BLUE,r=0)
line(x(.65),311,x(.65),357,'#A9B4BD',1)
line(x(2.7),311,x(2.7),357,'#A9B4BD',1)
text(x(.325),341,'…',22,OLD,'middle')
text((x(.65)+x(2.7))/2,341,'q0 · k−1',20,INK,'middle')
text((x(2.7)+x(5.5))/2,341,'q1 · k−1',20,INK,'middle')
text((x(5.5)+x(8.4))/2,341,'q2 · k',20,BLUE,'middle')
# Only the result that changes the binding gets a connector.
arrow(x(5.5),221,x(5.5),306,BLUE)
text(x(5.5)+14,291,'q2 result available',20,BLUE)
arrow(X,400,1080,400)
text(1080,390,'Time',19,INK,'end')
s.append('</svg>')
OUT.with_suffix('.svg').write_text('\n'.join(s))
svg=fitz.open(OUT.with_suffix('.svg'))
pdf=fitz.open('pdf',svg.convert_to_pdf())
pdf.save(OUT.with_suffix('.pdf'))
pdf[0].get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(OUT.with_suffix('.png'))
