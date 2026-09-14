import base64
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

GH = Path(__file__).resolve().parents[1]
REPO = GH.parent
TEAL = "#66bcbe"
INK = "#0a0a0a"
REDUCED = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"


def num(v):
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


class Font:
    # Text is emitted as outlines so GitHub renders the real typeface everywhere
    def __init__(self, name):
        self.tt = TTFont(GH / "fonts" / name)
        self.glyphs = self.tt.getGlyphSet()
        self.cmap = self.tt.getBestCmap()
        self.upm = self.tt["head"].unitsPerEm
        self.hmtx = self.tt["hmtx"]
        self.cap = self.tt["OS/2"].sCapHeight / self.upm

    def _glyph(self, ch):
        return self.cmap.get(ord(ch)) or self.cmap[ord("?")]

    def width(self, text, size, tracking=0):
        scale = size / self.upm
        return sum(self.hmtx[self._glyph(c)][0] * scale for c in text) + tracking * max(len(text) - 1, 0)

    def fit(self, text, max_width, max_size, tracking=0):
        return min(max_size, max_size * max_width / self.width(text, max_size, tracking))

    def path(self, text, size, x, y, fill=INK, anchor="start", tracking=0, attrs=""):
        w = self.width(text, size, tracking)
        x -= {"start": 0, "middle": w / 2, "end": w}[anchor]
        scale = size / self.upm
        pen = SVGPathPen(self.glyphs, num)
        for c in text:
            g = self._glyph(c)
            self.glyphs[g].draw(TransformPen(pen, (scale, 0, 0, -scale, x, y)))
            x += self.hmtx[g][0] * scale + tracking
        return f'<path d="{pen.getCommands()}" fill="{fill}"{attrs}/>'


ANTON = Font("Anton-Regular.ttf")
MONO = Font("SpaceMono-Regular.ttf")
MONO_B = Font("SpaceMono-Bold.ttf")


def baseline(font, size, center_y):
    return center_y + font.cap * size / 2


def brand(slug):
    h = json.loads((GH / "icons" / "brands.json").read_text(encoding="utf-8")).get(slug)
    return f"#{h}" if h else None


def legible(hex_color, floor=0.09):
    # near-black brand marks switch to white so they survive a black tile
    if not hex_color:
        return None
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lum = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    return "#ffffff" if 0.2126 * lum(r) + 0.7152 * lum(g) + 0.0722 * lum(b) < floor else hex_color


def icon(slug, x, y, size, fill=None):
    color = GH / "icons" / "color" / f"{slug}.svg"
    if color.exists():
        # multi-colour marks with no simple-icons path get embedded whole
        data = base64.b64encode(color.read_bytes()).decode()
        return f'<image x="{num(x)}" y="{num(y)}" width="{size}" height="{size}" href="data:image/svg+xml;base64,{data}"/>'
    fill = fill or brand(slug)
    src = (GH / "icons" / f"{slug}.svg").read_text(encoding="utf-8")
    d = re.search(r'<path d="([^"]+)"', src).group(1)
    return f'<path transform="translate({num(x)} {num(y)}) scale({size / 24:.4f})" d="{d}" fill="{fill}"/>'


def panel(w, h, rx=18):
    return f'<rect width="{w}" height="{h}" rx="{rx}" fill="{TEAL}"/>'


def document(w, h, body, css="", label=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-label="{escape(label, {chr(34): "&quot;"})}">\n'
        f"<style>{css}{REDUCED}</style>\n{body}\n</svg>\n"
    )


def write(rel, content):
    p = REPO / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print("wrote", rel, f"{len(content) // 1024} KB")
