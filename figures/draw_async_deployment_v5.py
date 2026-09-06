"""Minimal reference-binding schematic; timings are illustrative."""
from pathlib import Path
from html import escape
import fitz
OUT = Path(__file__).resolve().parent / 'fig03_async_deployment_v5'
W,H=1280,430
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
# Show just the two computations needed to explain the transition.
for yy in [84,198]:line(230,yy,1250,yy,'#CAD2D8')
for yy,a,b in [(75,'Reference','inference'),(187,'Residual','inference'),(322,'Applied','corrections')]:
 text(22,yy,a,22,bold=True);text(22,yy+27,b,22,bold=True)
for yy in range(106,308,12):line(520,yy,520,min(yy+6,308),BLUE)
rect(230,62,290,44,'#E7F2F8',BLUE)
text(375,91,'Compute new reference',21,BLUE,'middle')
text(536,126,'New reference available',21,BLUE)
rect(390,176,230,44,'#EDF0F2',OLD)
text(505,205,'Uses old reference',21,OLD,'middle')
rect(700,176,220,44,'#E7F2F8',BLUE)
text(810,205,'Uses new reference',21,BLUE,'middle')
line(520,268,920,268,OLD)
line(520,262,520,274,OLD)
line(920,262,920,274,OLD)
text(720,254,'Keep using old reference',21,OLD,'middle')
rect(230,310,690,48,'#DEE4E8',OLD,r=0)
rect(920,310,330,48,'#C6E2F2',BLUE,r=0)
text(575,341,'Based on old reference',22,INK,'middle')
text(1085,341,'Based on new reference',22,BLUE,'middle')
arrow(920,221,920,306,BLUE)
text(938,263,'New corrections ready',21,BLUE)
text(938,290,'Switch here',21,BLUE,bold=True)
arrow(230,400,1250,400)
text(1250,390,'Time',19,INK,'end')
s.append('</svg>')
OUT.with_suffix('.svg').write_text('\n'.join(s))
svg=fitz.open(OUT.with_suffix('.svg'))
pdf=fitz.open('pdf',svg.convert_to_pdf())
pdf.save(OUT.with_suffix('.pdf'))
pdf[0].get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(OUT.with_suffix('.png'))
