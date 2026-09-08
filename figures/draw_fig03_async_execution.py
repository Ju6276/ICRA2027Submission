#!/usr/bin/env python3
"""Single-column execution timeline, styled consistently with Figures 1 and 2."""
from html import escape
from pathlib import Path
import fitz

OUT = Path(__file__).resolve().parent / 'fig03_async_execution'
W, H = 900, 520
INK, EDGE = '#202A30', '#586B74'
BLUE, CREAM = '#BFD6DF', '#F4EEDC'
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     f'<rect width="{W}" height="{H}" fill="white"/>']


def text(x, y, label, size=22, anchor='start', weight='normal', color=INK):
    s.append(f'<text x="{x}" y="{y}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(label)}</text>')


def rect(x, y, w, h, fill, stroke=EDGE, radius=7, width=1.5):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>')


def line(points, color=EDGE, width=1.5, dash=None, arrow=False):
    pts = ' '.join(f'{x},{y}' for x,y in points)
    dashed = f' stroke-dasharray="{dash}"' if dash else ''
    s.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round"{dashed}/>')
    if arrow:
        x,y=points[-1]; px,py=points[-2]
        dx,dy=x-px,y-py; n=(dx*dx+dy*dy)**.5
        ux,uy=dx/n,dy/n
        p=[(x,y),(x-8*ux+4*uy,y-8*uy-4*ux),(x-8*ux-4*uy,y-8*uy+4*ux)]
        s.append(f'<polygon points="{" ".join(f"{a},{b}" for a,b in p)}" fill="{color}"/>')


# Soft bands, thin outlines, and typography follow the method architecture.
for y,h,fill in [(55,122,'#E8F1F4'),(191,174,'#EDF6E9'),(379,91,'#F5F7F8')]:
    rect(12,y,876,h,fill,stroke='none',radius=12,width=0)

rect(223,13,24,18,BLUE,radius=3)
text(258,30,'Previous reference',21)
rect(572,13,24,18,CREAM,radius=3)
text(607,30,'New reference',21)

text(30,93,'Reference',23,weight='bold')
text(30,121,'generation',23,weight='bold')
text(30,153,'≈6 Hz',21,color=EDGE)
text(30,243,'Correction',23,weight='bold')
text(30,271,'inference',23,weight='bold')
text(30,416,'Robot commands',22,weight='bold')
text(30,446,'100 Hz',21,color=EDGE)

# Only one reference handover is expanded; no assumed query period is shown.
text(611,88,'Reference ready',21,anchor='middle')
rect(223,111,388,40,CREAM)
text(417,138,'Generate new reference',22,anchor='middle')
line([(611,97),(611,109)],arrow=True)
line([(611,151),(611,207)],dash='5 4')
line([(611,239),(611,288)],dash='5 4')
text(545,228,'Read current state + recent force history',21,anchor='middle')

for x,fill in [(250,BLUE),(410,BLUE),(580,BLUE),(748,CREAM)]:
    line([(x,239),(x,251)],arrow=True)
    rect(x,254,62,34,fill,radius=5)

# These labels make reference binding visible without introducing new indices.
line([(611,290),(611,302)],arrow=True)
text(598,327,'Keep previous',21,anchor='middle')
text(598,351,'reference',21,anchor='middle')
line([(779,290),(779,302)],arrow=True)
text(779,327,'Adopt new',21,anchor='middle')
text(779,351,'reference',21,anchor='middle')

# Uniform cells are command transmissions, not action-chunk samples.
for x in range(223,864,24):
    rect(x,412,18,26,BLUE if x<823 else CREAM,radius=2,width=1)
line([(223,490),(877,490)],width=1.3,arrow=True)
text(223,514,'Schematic; not to scale',19,color=EDGE)
text(877,514,'Time',20,anchor='end')

s.append('</svg>')
OUT.with_suffix('.svg').write_text('\n'.join(s))
doc=fitz.open(OUT.with_suffix('.svg'))
pdf=fitz.open('pdf',doc.convert_to_pdf())
pdf.save(OUT.with_suffix('.pdf'))
pdf[0].get_pixmap(matrix=fitz.Matrix(1.6,1.6),alpha=False).save(OUT.with_suffix('.png'))
