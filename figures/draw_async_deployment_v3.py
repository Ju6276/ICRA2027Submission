"""Draw an illustrative schedule, not a measured runtime trace.

Chunk samples are anchored at query START, each valid for one unit (1/f_A).
Execution selects the freshest completed valid query. Earlier predictions may
be superseded. Reference identity is read once, at residual-query start.
"""
from pathlib import Path
from html import escape
import math
import fitz

OUT = Path(__file__).resolve().parent / 'fig03_async_deployment_v3'
K = 5
REFERENCE_READY = 2.2
# query id, start, availability, reference sampled at start
QUERIES = [(0, 0.0, 0.35, 'k−1'), (1, 2.0, 2.4, 'k−1'), (2, 4.0, 4.35, 'k')]
X0, SCALE = 255, 110
W, H = 1300, 630
OLD, BLUE, INK = '#657C8B', '#2275AC', '#233847'
COLORS = {'k−1': OLD, 'k': BLUE}
FILLS = {'k−1': '#D7E1E7', 'k': '#BCDCEF'}

def x(t): return X0 + SCALE*t

# Verify selected references and generate applied intervals from schedule.
for _, start, ready, ref in QUERIES:
    assert ready >= start
    assert ref == ('k' if start >= REFERENCE_READY else 'k−1')
assert QUERIES[1][1] < REFERENCE_READY < QUERIES[1][2]
boundaries = {0.0, 9.0, REFERENCE_READY}
for _, start, ready, _ in QUERIES:
    boundaries.add(ready)
    boundaries.update(start+j for j in range(K+1))
times = sorted(t for t in boundaries if 0 <= t <= 9)
applied = []
for left, right in zip(times, times[1:]):
    mid = (left+right)/2
    valid = [q for q in QUERIES if q[2] <= mid < q[1]+K]
    if not valid:
        assert right <= QUERIES[0][2]
        selected = (-1, 0, 'k−1')  # earlier valid chunk, outside the crop
    else:
        qid, start, _, ref = max(valid, key=lambda q:q[1])
        selected = (qid, 1+math.floor(mid-start), ref)
    if applied and applied[-1][2:] == selected:
        applied[-1] = (applied[-1][0], right, *selected)
    else:
        applied.append((left, right, *selected))
assert all(abs(a[1]-b[0])<1e-9 for a,b in zip(applied,applied[1:]))
assert next(a[0] for a in applied if a[4]=='k') == QUERIES[2][2]
for left, right, qid, step, _ in applied:
    if qid < 0: continue
    _, start, ready, _ = QUERIES[qid]
    assert left >= ready and left >= start+step-1 and right <= start+step+1e-9

s=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="white"/>']
def text(xx, yy, label, size=19, color=INK, bold=False, anchor='start'):
    s.append(f'<text x="{xx}" y="{yy}" font-family="Helvetica,Arial,sans-serif" font-size="{size}" font-weight="{"bold" if bold else "normal"}" fill="{color}" text-anchor="{anchor}">{escape(label)}</text>')
def line(x1,y1,x2,y2,color='#CFD8DE',width=1.3):
    s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"/>')
def dashed(xx,y1,y2,color):
    for yy in range(int(y1),int(y2),11):line(xx,yy,xx,min(yy+5,y2),color,1.4)
def rect(xx,yy,ww,hh,fill,stroke=None,r=3):
    s.append(f'<rect x="{xx}" y="{yy}" width="{ww}" height="{hh}" rx="{r}" fill="{fill}" stroke="{stroke or fill}" stroke-width="1.5"/>')
def dot(xx,yy,col):s.append(f'<circle cx="{xx}" cy="{yy}" r="4" fill="{col}"/>')
def arrow(x1,y1,x2,y2,col=INK):
    line(x1,y1,x2,y2,col,1.4)
    pts=f'{x2},{y2} {x2-8},{y2-4} {x2-8},{y2+4}' if y1==y2 else f'{x2},{y2} {x2-4},{y2-8} {x2+4},{y2-8}'
    s.append(f'<polygon points="{pts}" fill="{col}"/>')
def bracket(left,right,yy,label,col):
    line(left,yy,right,yy,col);line(left,yy-5,left,yy,col);line(right,yy-5,right,yy,col)
    text((left+right)/2,yy+24,label,17,col,anchor='middle')

# Light row backgrounds; candidate chunks use separate subrows.
for yy,hh in [(50,72),(176,66),(283,130),(485,46)]:
    rect(236,yy,1034,hh,'#F7F9FA',r=7)
text(23,79,'Reference',21,BLUE,True);text(23,105,'inference',21,BLUE,True)
text(23,201,'Residual',21,INK,True);text(23,227,'inference',21,INK,True)
text(23,331,'Predicted',21,INK,True);text(23,357,'chunks',21,INK,True)
text(23,503,'Applied',21,INK,True);text(23,529,'corrections',21,INK,True)
for yy in [86,210]:arrow(246,yy,1255,yy,'#D0D9DF')
# Reference publication is an event, not adoption by an already-started query.
rect(x(.55),66,x(REFERENCE_READY)-x(.55),40,'#E7F2F8',BLUE)
text((x(.55)+x(REFERENCE_READY))/2,92,'Query k',20,BLUE,True,'middle')
dot(x(.55),86,BLUE)
dashed(x(REFERENCE_READY),109,149,BLUE)
dashed(x(REFERENCE_READY),182,529,BLUE)
text(x(REFERENCE_READY)+12,139,'Reference k available',18,BLUE,True)
# Later reference queries are omitted to focus on one binding transition.

# Bind at START, release result at END. Filled square marks result-ready event.
for qid,start,ready,ref in QUERIES:
    col=COLORS[ref]
    rect(x(start),193,x(ready)-x(start),34,'#E7EDF1' if ref=='k−1' else '#E7F2F8',col)
    dot(x(start),210,col)
    rect(x(ready)-3,207,6,6,col,r=0)
    text(x(start),173,f'q{qid}: reads {ref}',17,col,True)
    yy=291+qid*41
    dashed(x(start),230,yy,col)
    # Completion guide stops before applied interval (overdrawn by candidate cells).
    dashed(x(ready),230,481,col)

# Full candidate time horizon, anchored at the start of each query.
for qid,start,ready,ref in QUERIES:
    yy=291+qid*41;col=COLORS[ref]
    text(222,yy+21,f'q{qid}',17,col,True,'end')
    for j in range(K):
        rect(x(start+j)+1,yy,SCALE-2,29,'white',col)
        text(x(start+j+.5),yy+21,str(j+1),17,col,anchor='middle')
    if qid==2:
        text(x(5.8),263,'Samples stay on query-start timestamps',17,INK)

# Event annotations occupy their own band.
line(x(REFERENCE_READY),450,x(QUERIES[2][2]),450,OLD,1.6)
line(x(REFERENCE_READY),450,x(REFERENCE_READY),457,OLD,1.6)
line(x(QUERIES[2][2]),450,x(QUERIES[2][2]),457,OLD,1.6)
text((x(REFERENCE_READY)+x(QUERIES[2][2]))/2,440,'Old reference retained',17,OLD,True,'middle')
text(x(QUERIES[2][2])+14,465,'Apply q2 result',17,BLUE,True)
arrow(x(QUERIES[2][2]),459,x(QUERIES[2][2]),484,BLUE)

# Actual application: partial first/last samples, no time shift and no gaps.
for left,right,qid,step,ref in applied:
    rect(x(left)+.6,489,x(right)-x(left)-1.2,38,FILLS[ref],COLORS[ref],r=1)
    text((x(left)+x(right))/2,515,'…' if qid<0 else str(step),17,COLORS[ref],anchor='middle')
for idx,q in enumerate(QUERIES):
    left=q[2];right=QUERIES[idx+1][2] if idx+1<len(QUERIES) else 9
    bracket(x(left),x(right),544,f'q{idx} · reference {q[3]}',COLORS[q[3]])
arrow(255,603,1255,603,INK)
text(255,628,'Illustrative schedule (K = 5); each numbered slot is one action-sample interval.',16,INK)
text(1255,590,'Time',17,INK,anchor='end')
text(23,592,'Hollow: predicted',15,INK)
text(23,615,'Filled: applied',15,INK)
s.append('</svg>')
OUT.with_suffix('.svg').write_text('\n'.join(s))
d=fitz.open(OUT.with_suffix('.svg'));pdf=fitz.open('pdf',d.convert_to_pdf());pdf.save(OUT.with_suffix('.pdf'))
pdf[0].get_pixmap(matrix=fitz.Matrix(1.6,1.6)).save(OUT.with_suffix('.png'))
print('Verified applied intervals:',applied)
print('Saved',OUT)
