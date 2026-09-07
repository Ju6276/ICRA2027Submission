"""Draw ForceDelta-VLA with the compact visual grammar of pi-series figures."""
from html import escape
from pathlib import Path
import subprocess
import tempfile

try:
    import fitz
except ModuleNotFoundError:
    fitz = None

OUT = Path(__file__).resolve().parent / "fig02_architecture"
W, H = 1900, 980
INK, EDGE, FAINT = "#2D3B42", "#60747E", "#B7C2C7"
CREAM, BLUE, GREEN = "#FBF4E3", "#A9D8E7", "#CDE5BE"
ORANGE, PINK, PURPLE = "#F5CFA2", "#F2C9CD", "#DCCBE8"
GREY, YELLOW = "#DEE5E8", "#F7E4A1"
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     '<style>@page { size: 19.7917in 10.2083in; margin: 0; }</style>',
     '<rect width="100%" height="100%" fill="white"/>']

def text(x, y, value, size=20, anchor="start", weight="normal", color=INK,
         family="Helvetica,Arial,sans-serif"):
    s.append(f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
             f'font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(value)}</text>')

def rect(x, y, w, h, fill="white", stroke=EDGE, radius=7, width=1.35, dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" fill="{fill}" '
             f'stroke="{stroke}" stroke-width="{width}"{dash_attr}/>')

def line(x1, y1, x2, y2, color=EDGE, width=1.4, dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    s.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
             f'stroke-width="{width}"{dash_attr}/>')

def arrow(points, color=EDGE, width=1.45, dash=None):
    dash_attr = f' stroke-dasharray="{dash}"' if dash else ""
    encoded = " ".join(f"{x},{y}" for x, y in points)
    s.append(f'<polyline points="{encoded}" fill="none" stroke="{color}" stroke-width="{width}" '
             f'stroke-linejoin="round"{dash_attr}/>')
    x, y = points[-1]; px, py = points[-2]
    dx, dy = x - px, y - py; norm = max((dx * dx + dy * dy) ** 0.5, 1e-6)
    ux, uy = dx / norm, dy / norm
    tips = [(x, y), (x - 8*ux + 4*uy, y - 8*uy - 4*ux), (x - 8*ux - 4*uy, y - 8*uy + 4*ux)]
    s.append(f'<polygon points="{" ".join(f"{a},{b}" for a,b in tips)}" fill="{color}"/>')

def pill(x, y, w, h, label, fill, size=17, weight="normal"):
    rect(x, y, w, h, fill=fill, radius=h/2)
    text(x+w/2, y+h/2+size*.34, label, size, "middle", weight)

def darken(hex_color, factor=0.90):
    rgb = [int(hex_color[i:i+2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(v*factor):02X}" for v in rgb)

def subscript_pill(x, y, w, h, subscript, fill, size=18):
    """Draw z_{subscript} with a real typographic subscript."""
    rect(x, y, w, h, fill=fill, radius=h/2)
    cx, cy = x + w/2, y + h/2 + size*.25
    s.append(
        f'<text x="{cx}" y="{cy}" font-family="Helvetica,Arial,sans-serif" '
        f'font-size="{size}" fill="{INK}" text-anchor="middle">'
        f'z<tspan baseline-shift="sub" font-size="{size*.68}">{escape(subscript)}</tspan></text>'
    )

def rich_text(x, y, parts, size=16, anchor="middle", color=INK,
              family="Helvetica,Arial,sans-serif"):
    """Text with consistent SVG super/subscripts instead of Unicode glyph hacks.

    ``parts`` contains ``(value, shift)`` pairs, where shift is ``base``,
    ``sub``, or ``super``.
    """
    chunks = []
    i = 0
    while i < len(parts):
        value, shift = parts[i]
        if i+1 < len(parts) and {shift, parts[i+1][1]} == {'sub', 'super'}:
            value2, shift2 = parts[i+1]
            widths = [len(v)*size*.68*.6 for v in (value,value2)]
            chunks.append(f'<tspan baseline-shift="{shift}" font-size="{size*.68}" textLength="{widths[0]}" lengthAdjust="spacingAndGlyphs">{escape(value)}</tspan>')
            chunks.append(f'<tspan dx="{-widths[0]}" baseline-shift="{shift2}" font-size="{size*.68}" textLength="{widths[1]}" lengthAdjust="spacingAndGlyphs">{escape(value2)}</tspan>')
            chunks.append(f'<tspan baseline-shift="baseline" dx="{max(widths)-widths[1]}" font-size="{size}">&#8203;</tspan>')
            i += 2
            continue
        if shift == "base":
            chunks.append(f'<tspan baseline-shift="baseline" font-size="{size}">{escape(value)}</tspan>')
        else:
            chunks.append(
                f'<tspan baseline-shift="{shift}" font-size="{size*.68}">{escape(value)}</tspan>'
            )
        i += 1
    s.append(
        f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
        f'fill="{color}" text-anchor="{anchor}">{"".join(chunks)}</text>'
    )

def rich_pill(x, y, w, h, parts, fill, size=18):
    rect(x, y, w, h, fill=fill, radius=h/2)
    rich_text(x+w/2, y+h/2+size*.25, parts, size)

def small_tokens(x, y, count, color, token_w=23, gap=7):
    token_fill = darken(color)
    for i in range(count):
        rect(x+i*(token_w+gap), y, token_w, 11, token_fill, radius=5, width=1.0)

def token_column(x, y, w, h, color, count=2, masked=False):
    rect(x, y, w, h, color, radius=6)
    total = count*25+(count-1)*7; tx=x+(w-total)/2
    small_tokens(tx, y+10, count, color, 25, 7); small_tokens(tx, y+h-21, count, color, 25, 7)
    if masked:
        for yy in (y+10, y+h-21):
            line(x+w/2-14, yy-1, x+w/2+14, yy+12, INK, 1.3)
            line(x+w/2-14, yy+12, x+w/2+14, yy-1, INK, 1.3)

def model_bar(x, y, w, h, label, size=20):
    rect(x, y, w, h, "white", radius=6, width=1.5)
    text(x+w/2, y+h/2+size*.34, label, size, "middle")

def trapezoid(x, y, w, h, label, fill):
    pts=f"{x+9},{y} {x+w-9},{y} {x+w},{y+h} {x},{y+h}"
    s.append(f'<polygon points="{pts}" fill="{fill}" stroke="{EDGE}" stroke-width="1.3"/>')
    text(x+w/2, y+h/2+6, label, 16, "middle")

def panel_title(x, y, letter, title):
    text(x, y, f"({letter})", 25, weight="bold"); text(x+45, y, title, 25, weight="bold")

def action_strip(x, y, w, h, fill, count=5):
    """A short action chunk; divisions are timesteps, not transformer tokens."""
    rect(x, y, w, h, fill, radius=h/2)
    for i in range(1, count):
        line(x+w*i/count, y+2, x+w*i/count, y+h-2, EDGE, 0.9)

line(635,35,635,438,FAINT,1.1,"5 5"); line(28,455,1872,455,FAINT,1.1)

# (a) A compact PI-style model strip.
panel_title(28,37,"a","Teacher and missing-force mode")
for x,w,c,n in [(42,92,BLUE,2),(142,92,BLUE,2),(242,94,PINK,2),(344,92,PURPLE,1),(444,145,GREEN,4)]:
    token_column(x,168,w,100,c,n)
model_bar(34,201,304,38,"pre-trained VLM",19)
model_bar(338,201,260,38,"FVLMoE + action expert",16)
trapezoid(54,286,70,31,"ViT",BLUE); trapezoid(154,286,70,31,"ViT",BLUE)
arrow([(89,285),(89,268)]); arrow([(189,285),(189,268)])
rect(41,337,196,40,CREAM,radius=6); text(139,363,"multi-view images",17,"middle")
arrow([(89,337),(89,318)]); arrow([(189,337),(189,318)])
pill(251,337,76,40,"L",PINK,18); arrow([(289,337),(289,269)])
rich_pill(352,337,76,40,[("S","base"),("t","sub")],PURPLE,18)
arrow([(390,337),(390,269)])
rich_pill(440,326,70,38,[("z","base"),("F","super"),("t","sub")],ORANGE,18)
subscript_pill(540,326,70,38,"∅F",GREEN,18)
text(475,379,"Force-conditioned",9.5,"middle")
text(475,391,"TCN(history)",9.5,"middle",family="Courier New,monospace")
text(575,379,"Missing-force mode",9.5,"middle")
text(575,391,"missing token",9.5,"middle",family="Courier New,monospace")
rect(345,113,170,40,CREAM,radius=3)
text(430,130,"missing-mode adapter",11,"middle")
text(430,145,"on pose flow output",11,"middle")
arrow([(515,133),(529,133)],width=1.0)
# Either force condition enters the same robotics pathway.  The branches join
# before touching the model boundary so no line is drawn through the box edge.
line(475,326,475,294); line(575,326,575,294); line(475,294,575,294)
rect(501,281,48,22,"white",radius=3)
text(525,296,"OR",11,"middle")
arrow([(525,281),(525,269)])
action_strip(466,82,128,18,YELLOW)
arrow([(530,167),(530,102)])
text(530,59,"H-step action chunk",12,"middle",family="Courier New,monospace")
text(530,74,"both teacher modes",10.5,"middle",family="Courier New,monospace")
text(35,414,"cache: pooled V-L context, reference chunk, query state",15,family="Courier New,monospace")

# (b) Paired cached-context targets.
panel_title(670,37,"b","Paired residual targets")
text(1265,70,"sampled schedule selects current time t and active reference k",15,"middle",family="Courier New,monospace")
rect(765,91,1000,34,GREY,radius=17)
rich_text(1265,113,[("shared cached prefix E","base"),("k","sub"),
                    ("  +  shared flow noise ε","base"),("k","sub")],16)
specs=[(690,"force-conditioned",[("S","base"),("t","sub"),(" + force history","base")],ORANGE),
       (1090,"missing-force",[("S","base"),("t","sub"),(" + missing-force token","base")],GREEN),
       (1490,"cached reference",[("A","base"),("ref","super"),("k","sub"),("(t","base"),
                                   ("1:K","sub"),("); query state S","base"),("k","sub")],BLUE)]
for x,title,sub,c in specs:
    token_column(x+24,157,290,82,c,5); model_bar(x,181,338,36,title,18)
    rich_text(x+169,260,sub,14,family="Courier New,monospace")
# The cached prefix/noise are shared by all three outputs used in target construction.
for center_x in (859,1259,1659):
    arrow([(center_x,125),(center_x,155)])
for bx,c in [(775,ORANGE),(1175,GREEN),(1575,BLUE)]:
    action_strip(bx,286,130,16,c)
    # Begin below the subtitle baseline so the arrow never crosses its glyphs.
    arrow([(bx+65,269),(bx+65,284)])
# Two non-crossing target constructions.  The formulas specify subtraction order;
# the V-shaped lines only indicate which teacher outputs participate.
rect(862,347,356,42,ORANGE,radius=8)
rich_text(1040,373,[("ΔA","base"),("force","super"),
                    (" = conditioned − missing","base")],15,family="Courier New,monospace")
arrow([(840,304),(995,345)]); arrow([(1240,304),(1085,345)])
rect(1262,347,356,42,PURPLE,radius=8)
rich_text(1440,373,[("ΔA","base"),("stale","super"),
                    (" = missing − reference + Γ(S","base"),("t","sub"),
                    (",S","base"),("k","sub"),(")","base")],14,
          family="Courier New,monospace")
arrow([(1240,304),(1395,345)]); arrow([(1640,304),(1485,345)])

# (c) Same token slots and shared block in two passes.
panel_title(28,499,"c","Fast residual policy")
text(618,530,"same typed-token set; two passes share Φ",15,"middle",family="Courier New,monospace")
labels=[("context",[("Z","base"),("intent","super"),("k","sub")],BLUE),
        ("force history",[("u","base"),("F","super"),("t","sub"),(" = TCN(F[t−w:t])","base")],ORANGE),
        ("state",[("S","base"),("t","sub")],PURPLE),
        ("reference",[("A","base"),("ref","super"),("k","sub"),("(t","base"),("1:K","sub"),(")","base")],GREEN),
        ("time",[("ξ","base"),("t,k","sub")],GREY),
        ("query",[("q","base"),("res","sub")],YELLOW)]

def residual_pass(y, masked, head_title, head_color):
    start_x,col_w,gap=42,127,9
    for i,(name,symbol,c) in enumerate(labels):
        x=start_x+i*(col_w+gap); token_column(x,y,col_w,104,GREY if masked and i==1 else c,2 if i==0 else 1,masked and i==1)
        if y==592:
            text(x+col_w/2,y-30,name,15,"middle")
            rich_text(x+col_w/2,y-10,symbol,14,family="Courier New,monospace")
    model_bar(31,y+34,826,38,"shared set attention  Φ",20)
    text(43,y+130,"force token masked" if masked else "force token present",15,family="Courier New,monospace")
    arrow([(858,y+53),(902,y+53)]); pill(905,y+30,245,46,head_title,head_color,18)
    action_strip(1170,y+42,120,22,head_color)
    text(1230,y+82,"K-step correction chunk",12,"middle",family="Courier New,monospace")
    arrow([(1150,y+53),(1167,y+53)])
    rect(925,y-18,205,26,"white",radius=3,dash="4 3")
    text(1027,y,"force target from (b)" if not masked else "staleness target from (b)",12,"middle")
    arrow([(1027,y+8),(1027,y+28)],dash="4 3")

residual_pass(592,False,"force head",ORANGE); residual_pass(786,True,"staleness head",PURPLE)

# (d) Three terms, one junction. Gamma is not added a second time.
panel_title(1325,499,"d","Command composition")
text(1604,531,"per correction step j",14,"middle",family="Courier New,monospace")
text(1525,553,"reference from missing-force query (a)",12,"middle")
rows=[(568,BLUE,"cached reference",[("A","base"),("ref","super"),("k","sub"),("(t","base"),("j","sub"),(")","base")]),
      (650,ORANGE,"force correction (bounded)",[("ΔÂ","base"),("force","super"),("t,j","sub")]),
      (732,PURPLE,"staleness correction (bounded)",[("ΔÂ","base"),("stale","super"),("t,j","sub")])]
for y,c,title,symbol in rows:
    rect(1343,y,365,52,c,radius=7); text(1363,y+22,title,16)
    rich_text(1688,y+34,symbol,15,"end",family="Courier New,monospace")
    line(1708,y+26,1750,y+26)
# Bind each predicted correction strip to its corresponding composition term.
arrow([(1292,645),(1318,645),(1318,676),(1341,676)])
arrow([(1292,839),(1318,839),(1318,758),(1341,758)])
line(1750,594,1750,758); pill(1732,792,36,36,"+","white",21,"bold"); arrow([(1750,758),(1750,790)])
rect(1390,856,360,57,CREAM,radius=7); text(1570,878,"Convert to absolute command",17,"middle","bold")
rich_text(1570,901,[("using S","base"),("k","sub"),("; reference gripper","base")],14)
arrow([(1750,828),(1750,841),(1570,841),(1570,854)])

s.append("</svg>"); OUT.with_suffix(".svg").write_text("\n".join(s))
if fitz is not None:
    d=fitz.open(OUT.with_suffix(".svg")); pdf=fitz.open("pdf",d.convert_to_pdf()); pdf.save(OUT.with_suffix(".pdf"))
    pdf[0].get_pixmap(matrix=fitz.Matrix(1.2,1.2)).save(OUT.with_suffix(".png"))
else:
    uri=OUT.with_suffix(".svg").resolve().as_uri()
    with tempfile.TemporaryDirectory(prefix="fig02_chrome_") as profile:
        subprocess.run(["google-chrome","--headless=new","--disable-gpu","--disable-dev-shm-usage",
                        "--no-sandbox","--no-pdf-header-footer",f"--user-data-dir={profile}",
                        f'--print-to-pdf={OUT.with_suffix(".pdf")}',uri],check=True,timeout=30)
    subprocess.run(["pdftoppm","-png","-singlefile","-r","96",str(OUT.with_suffix(".pdf")),str(OUT)],check=True)
print(OUT)
