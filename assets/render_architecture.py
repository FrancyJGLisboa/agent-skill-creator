#!/usr/bin/env python3
"""Render assets/architecture.excalidraw to SVG, for re-rendering architecture.png.

Edit the .excalidraw JSON (it is hand-authored, with readable element ids), then:

    python3 assets/render_architecture.py assets/architecture.excalidraw /tmp/arch.svg

    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless \\
        --disable-gpu --screenshot=/tmp/arch@2x.png --window-size=<W>,<H> \\
        --force-device-scale-factor=2 --default-background-color=FFFFFFFF \\
        --hide-scrollbars file:///tmp/arch.svg

    magick /tmp/arch@2x.png -resize 1640x -strip assets/architecture.png
    cp assets/architecture.png docs/assets/architecture.png

<W>,<H> are the SVG's own width/height, which this script prints. Rendering at
2x and downscaling keeps the text crisp. The two PNG copies must stay identical.

If the pixel height changes, update the `height` attribute on the hero <img> in
docs/index.html to match (width stays 820; height = round(820 * H_png / W_png)),
or the browser reserves the wrong space and the hero shifts on load.

No Excalidraw app, npm package, or network access is needed. The file uses only
rectangle (roundness 3), ellipse, line, arrow (polyline + optional arrowhead) and
text (fontFamily 3 = monospace), and every element has roughness 0 -- so plain
SVG primitives reproduce it exactly, with no sketchy-stroke simulation.
"""
from __future__ import annotations

import json
import sys
from xml.sax.saxutils import escape

PAD = 28
LINE_H = 1.25
MONO = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', monospace"


def bounds(els):
    xs, ys, xe, ye = [], [], [], []
    for e in els:
        w, h = e.get("width", 0), e.get("height", 0)
        if e["type"] in ("arrow", "line"):
            pts = e.get("points", [[0, 0]])
            for px, py in pts:
                xs.append(e["x"] + px)
                ys.append(e["y"] + py)
                xe.append(e["x"] + px)
                ye.append(e["y"] + py)
        else:
            xs.append(e["x"])
            ys.append(e["y"])
            xe.append(e["x"] + w)
            ye.append(e["y"] + h)
    return min(xs) - PAD, min(ys) - PAD, max(xe) + PAD, max(ye) + PAD


def stroke_attrs(e):
    a = f'stroke="{e.get("strokeColor", "#1e1e1e")}" stroke-width="{e.get("strokeWidth", 2)}"'
    a += ' stroke-linecap="round" stroke-linejoin="round"'
    if e.get("strokeStyle") == "dashed":
        a += f' stroke-dasharray="{e.get("strokeWidth", 2) * 4},{e.get("strokeWidth", 2) * 3}"'
    elif e.get("strokeStyle") == "dotted":
        a += f' stroke-dasharray="1,{e.get("strokeWidth", 2) * 2}"'
    op = e.get("opacity", 100) / 100
    if op != 1:
        a += f' opacity="{op}"'
    return a


def fill_of(e):
    bg = e.get("backgroundColor", "transparent")
    return "none" if bg in ("transparent", None) else bg


def arrowhead(x1, y1, x2, y2, color, size=14):
    """A filled triangle at (x2,y2) pointing along the segment."""
    import math
    ang = math.atan2(y2 - y1, x2 - x1)
    spread = math.radians(22)
    p1 = (x2 - size * math.cos(ang - spread), y2 - size * math.sin(ang - spread))
    p2 = (x2 - size * math.cos(ang + spread), y2 - size * math.sin(ang + spread))
    pts = f"{x2:.1f},{y2:.1f} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return f'<polygon points="{pts}" fill="{color}"/>'


def render(path_in, path_out):
    doc = json.load(open(path_in))
    els = [e for e in doc["elements"] if not e.get("isDeleted")]
    x0, y0, x1, y1 = bounds(els)
    w, h = x1 - x0, y1 - y0
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{h:.0f}" '
        f'viewBox="{x0:.0f} {y0:.0f} {w:.0f} {h:.0f}">',
        f'<rect x="{x0:.0f}" y="{y0:.0f}" width="{w:.0f}" height="{h:.0f}" '
        f'fill="{doc.get("appState", {}).get("viewBackgroundColor", "#ffffff")}"/>',
    ]

    for e in els:
        t = e["type"]
        if t == "rectangle":
            rw, rh = e["width"], e["height"]
            r = 0
            if e.get("roundness"):
                r = min(32, min(rw, rh) * 0.25)
            out.append(
                f'<rect x="{e["x"]}" y="{e["y"]}" width="{rw}" height="{rh}" rx="{r:.1f}" '
                f'fill="{fill_of(e)}" {stroke_attrs(e)}/>'
            )
        elif t == "ellipse":
            out.append(
                f'<ellipse cx="{e["x"] + e["width"] / 2}" cy="{e["y"] + e["height"] / 2}" '
                f'rx="{e["width"] / 2}" ry="{e["height"] / 2}" '
                f'fill="{fill_of(e)}" {stroke_attrs(e)}/>'
            )
        elif t in ("arrow", "line"):
            pts = [(e["x"] + px, e["y"] + py) for px, py in e.get("points", [])]
            if len(pts) < 2:
                continue
            d = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
            out.append(f'<polyline points="{d}" fill="none" {stroke_attrs(e)}/>')
            if e.get("endArrowhead") == "arrow":
                out.append(arrowhead(*pts[-2], *pts[-1], e.get("strokeColor", "#1e1e1e")))
            if e.get("startArrowhead") == "arrow":
                out.append(arrowhead(*pts[1], *pts[0], e.get("strokeColor", "#1e1e1e")))
        elif t == "text":
            size = e.get("fontSize", 20)
            align = e.get("textAlign", "left")
            anchor = {"left": "start", "center": "middle", "right": "end"}[align]
            tx = {"start": e["x"], "middle": e["x"] + e.get("width", 0) / 2,
                  "end": e["x"] + e.get("width", 0)}[anchor]
            lines = e["text"].split("\n")
            # Excalidraw's text box top is e["y"]; first baseline sits ~0.79em down.
            for i, line in enumerate(lines):
                by = e["y"] + i * size * LINE_H + size * 0.79
                out.append(
                    f'<text x="{tx:.1f}" y="{by:.1f}" font-family="{MONO}" '
                    f'font-size="{size}" fill="{e.get("strokeColor", "#1e1e1e")}" '
                    f'text-anchor="{anchor}" '
                    f'font-weight="{"bold" if e.get("fontFamily") == 9 else "normal"}'
                    f'">{escape(line)}</text>'
                )
    out.append("</svg>")
    open(path_out, "w").write("\n".join(out))
    print(f"{path_out}  {w:.0f}x{h:.0f}  ({len(els)} elements)")


if __name__ == "__main__":
    render(sys.argv[1], sys.argv[2])
