"""HTML building blocks for the tutorial video.

Every component takes b=N: the element appears once narration beat N has started
(b=0 means always visible). build.py screenshots one frame per beat.
"""
import html
import json
from pathlib import Path

ICONS = json.loads((Path(__file__).parent / "icons.json").read_text())
COL = {"teal": "#19B5C4", "amber": "#F2A541", "red": "#E5534B", "green": "#3FB27F",
       "purple": "#8B7BD0", "slate": "#7C8FA0", "white": "#F2F6F9"}

CSS = """
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:1920px;height:1080px;overflow:hidden}
body{background:#0B1620;color:#F2F6F9;font-family:'Liberation Sans','DejaVu Sans',Arial,sans-serif;font-size:34px;line-height:1.28}
.scene{position:relative;width:1920px;height:1080px;padding:64px 90px 70px}
.serif{font-family:'Liberation Serif','DejaVu Serif',Georgia,serif}
.mono{font-family:'DejaVu Sans Mono','Liberation Mono',monospace}
.hdr{display:flex;align-items:baseline;gap:26px;margin-bottom:34px}
.kick{font-size:26px;letter-spacing:3px;text-transform:uppercase;color:#19B5C4;font-weight:700;white-space:nowrap}
.ttl{font-size:62px;font-weight:700;font-family:'Liberation Serif','DejaVu Serif',Georgia,serif;line-height:1.08}
.foot{position:absolute;left:90px;bottom:26px;font-size:20px;color:#5E7384;letter-spacing:.5px}
.foot b{color:#19B5C4}
.r{opacity:0;transform:translateY(18px);transition:none}
.r.on{opacity:1;transform:none}
.row{display:flex;gap:28px}
.col{display:flex;flex-direction:column;gap:24px}
.grow{flex:1}
.card{background:#14283A;border-radius:22px;padding:30px 34px;border:2px solid #1E3A52}
.card h3{font-size:36px;margin-bottom:10px;line-height:1.1}
.card p,.card li{font-size:30px;color:#C9D6E0}
.card ul{padding-left:34px}
.card li{margin:8px 0}
.t-teal{color:#19B5C4}.t-amber{color:#F2A541}.t-red{color:#E5534B}.t-green{color:#3FB27F}.t-purple{color:#8B7BD0}.t-slate{color:#9DB2C2}.t-white{color:#F2F6F9}
.b-teal{border-color:#19B5C4}.b-amber{border-color:#F2A541}.b-red{border-color:#E5534B}.b-green{border-color:#3FB27F}.b-purple{border-color:#8B7BD0}
.ic{display:inline-flex;width:56px;height:56px;vertical-align:middle}
.ic svg{width:100%;height:100%}
.disc{display:inline-flex;align-items:center;justify-content:center;border-radius:50%;flex:none}
.disc .ic{width:54%;height:54%}
.stat .n{font-size:100px;font-weight:700;font-family:'Liberation Serif','DejaVu Serif',serif;line-height:1}
.stat .l{font-size:28px;color:#9DB2C2;margin-top:10px}
.chip{display:inline-block;border-radius:40px;padding:8px 26px;font-size:28px;font-weight:700;margin:6px 8px 6px 0}
.big{font-size:44px}
.sub{font-size:30px;color:#9DB2C2}
.call{border-radius:20px;padding:24px 32px;font-size:32px;font-weight:600;line-height:1.3}
.call.red{background:#3A1E22;border:2px solid #E5534B}
.call.amber{background:#3B2E17;border:2px solid #F2A541}
.call.green{background:#173528;border:2px solid #3FB27F}
.call.teal{background:#123540;border:2px solid #19B5C4}
.arrow{font-size:60px;color:#7C8FA0;align-self:center;font-weight:700}
table{border-collapse:separate;border-spacing:0 10px;width:100%}
th{font-size:24px;letter-spacing:2px;text-transform:uppercase;color:#7C8FA0;text-align:left;padding:4px 22px}
td{background:#14283A;padding:16px 22px;font-size:29px;color:#E3EBF1;vertical-align:middle}
td:first-child{border-radius:16px 0 0 16px;font-weight:700}td:last-child{border-radius:0 16px 16px 0}
tr.r{opacity:0}tr.r.on{opacity:1}
.term{background:#050B11;border:2px solid #22394D;border-radius:18px;padding:26px 34px;font-family:'DejaVu Sans Mono','Liberation Mono',monospace;font-size:27px;line-height:1.5;color:#CFE0EC}
.term .ln{white-space:pre;display:block}
.term .c{color:#6C8599}.term .ok{color:#3FB27F}.term .bad{color:#E5534B}.term .hi{color:#F2A541}.term .p{color:#19B5C4}
.bar{display:flex;align-items:center;gap:22px;margin:14px 0}
.bar .lab{width:430px;font-size:29px;color:#E3EBF1;text-align:right}
.bar .trk{flex:1;height:44px;background:#14283A;border-radius:10px;overflow:hidden}
.bar .fil{height:100%;border-radius:10px}
.bar .v{width:90px;font-size:32px;font-weight:700}
.vbars{display:flex;align-items:flex-end;gap:26px;height:520px;padding:0 10px}
.vb{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;height:100%}
.vb .fil{width:100%;border-radius:14px 14px 0 0}
.vb .n{font-size:44px;font-weight:700;margin-bottom:8px}
.vb .l{font-size:26px;color:#C9D6E0;margin-top:14px;text-align:center}
.step{background:#14283A;border:2px solid #1E3A52;border-radius:20px;padding:22px 24px;text-align:center;flex:1}
.step .num{font-size:50px;font-weight:700;font-family:'Liberation Serif',serif}
.step .tt{font-size:30px;font-weight:700;margin-top:4px}
.step .ss{font-size:25px;color:#9DB2C2;margin-top:6px}
.venn{position:relative;width:900px;height:500px}
.venn div{position:absolute;border-radius:50%}
.bigtitle{font-size:92px;line-height:1.05}
"""


def esc(s):
    return html.escape(s, quote=False)


def _b(b):
    return f' data-b="{b}"' if b else ""


def _r(b):
    return " r" if b else ""


def ic(name, color="white", size=56):
    c = COL.get(color, color)
    return f'<span class="ic" style="width:{size}px;height:{size}px;color:{c}">{ICONS[name]}</span>'


def disc(name, color="teal", size=96, icolor="#0B1620", b=0):
    c = COL.get(color, color)
    return (f'<span class="disc{_r(b)}"{_b(b)} style="width:{size}px;height:{size}px;background:{c};color:{icolor}">'
            f'<span class="ic">{ICONS[name]}</span></span>')


def scene(kicker, title, body, foot=True):
    f = '<div class="foot"><b>AWS</b> CIS posture assessment tutorial &nbsp;|&nbsp; VaultBridge Financial (simulated)</div>' if foot else ""
    return (f'<div class="scene"><div class="hdr"><div class="kick">{esc(kicker)}</div>'
            f'<div class="ttl">{esc(title)}</div></div><div class="body">{body}</div>{f}</div>')


def row(*items, gap=28, cls=""):
    return f'<div class="row {cls}" style="gap:{gap}px">{"".join(items)}</div>'


def col(*items, gap=24, cls="", style=""):
    return f'<div class="col {cls}" style="gap:{gap}px;{style}">{"".join(items)}</div>'


def card(title="", text="", color=None, icon=None, b=0, cls="", style="", items=None, title_color=None):
    bc = f" b-{color}" if color else ""
    tc = f" t-{title_color or color}" if (title_color or color) else ""
    head = ""
    if icon:
        head = (f'<div style="display:flex;align-items:center;gap:20px;margin-bottom:14px">'
                f'{disc(icon, color or "teal", 74)}<h3 class="{tc}" style="margin:0">{esc(title)}</h3></div>')
    elif title:
        head = f'<h3 class="{tc}">{esc(title)}</h3>'
    body = f"<p>{text}</p>" if text else ""
    if items:
        body += "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>"
    return f'<div class="card{bc}{_r(b)} {cls}"{_b(b)} style="{style}">{head}{body}</div>'


def stat(num, label, color="teal", b=0, style="", size=100):
    return (f'<div class="stat{_r(b)}"{_b(b)} style="{style}"><div class="n t-{color}" style="font-size:{size}px">{esc(num)}</div>'
            f'<div class="l">{esc(label)}</div></div>')


def chip(text, color="teal", b=0, dark=True):
    c = COL.get(color, color)
    fg = "#0B1620" if dark else "#fff"
    return f'<span class="chip{_r(b)}"{_b(b)} style="background:{c};color:{fg}">{esc(text)}</span>'


def call(text, color="amber", b=0, style=""):
    return f'<div class="call {color}{_r(b)}"{_b(b)} style="{style}">{text}</div>'


def arrow(b=0, txt="→"):
    return f'<div class="arrow{_r(b)}"{_b(b)}>{txt}</div>'


def term(lines, title="terminal", b0=0, style=""):
    """lines: list of (text, kind, beat). kind in '', c, ok, bad, hi, p."""
    out = []
    for text, kind, beat in lines:
        out.append(f'<span class="ln {kind}{_r(beat)}"{_b(beat)}>{esc(text) or "&nbsp;"}</span>')
    return f'<div class="term{_r(b0)}"{_b(b0)} style="{style}">{"".join(out)}</div>'


def table(headers, rows, b0=0, widths=None, style=""):
    """rows: list of (cells, beat)."""
    h = "".join(f'<th{"" if not widths else f" style=width:{widths[i]}"}>{esc(x)}</th>' for i, x in enumerate(headers))
    body = ""
    for cells, beat in rows:
        tds = "".join(f"<td>{c}</td>" for c in cells)
        body += f'<tr class="{_r(beat).strip()}"{_b(beat)}>{tds}</tr>'
    return f'<table style="{style}"><thead><tr>{h}</tr></thead><tbody>{body}</tbody></table>'


def hbars(items, maxv, b0=0, labw=430):
    """items: list of (label, value, color, beat, text)."""
    out = []
    for lab, val, color, beat, txt in items:
        w = 100 * val / maxv
        c = COL.get(color, color)
        out.append(
            f'<div class="bar{_r(beat)}"{_b(beat)}><div class="lab" style="width:{labw}px">{esc(lab)}</div>'
            f'<div class="trk"><div class="fil" style="width:{w}%;background:{c}"></div></div>'
            f'<div class="v" style="color:{c}">{esc(txt if txt is not None else str(val))}</div></div>')
    return "".join(out)


def vbars(items, maxv, height=520):
    """items: list of (label, value, color, beat)."""
    out = []
    for lab, val, color, beat in items:
        c = COL.get(color, color)
        hpx = max(8, int(height * 0.78 * val / maxv))
        out.append(
            f'<div class="vb{_r(beat)}"{_b(beat)}><div class="n" style="color:{c}">{val}</div>'
            f'<div class="fil" style="height:{hpx}px;background:{c}"></div><div class="l">{lab}</div></div>')
    return f'<div class="vbars" style="height:{height}px">{"".join(out)}</div>'


def steps(items, b0=1, num_color="teal", each=1):
    """items: list of (num, title, sub, color)."""
    out = []
    for i, (n, t, s, color) in enumerate(items):
        if i:
            out.append(f'<div class="arrow{_r(b0 + i * each)}"{_b(b0 + i * each)} style="font-size:44px">→</div>')
        out.append(
            f'<div class="step{_r(b0 + i * each)}"{_b(b0 + i * each)}><div class="num t-{color}">{esc(n)}</div>'
            f'<div class="tt">{esc(t)}</div><div class="ss">{esc(s)}</div></div>')
    return f'<div class="row" style="gap:14px;align-items:stretch">{"".join(out)}</div>'


def raw(inner, b=0, cls="", style=""):
    return f'<div class="{cls}{_r(b)}"{_b(b)} style="{style}">{inner}</div>'
