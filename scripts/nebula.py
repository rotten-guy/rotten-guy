"""Shared helpers to draw "Nebula" SVGs for the profile README.

Text is converted to paths with the fonts in scripts/fonts/, so the pictures look
the same everywhere (GitHub shows SVGs as images: they cannot load web fonts).
Animations use SMIL (<animate>), which GitHub keeps.
"""
import random
import re
from functools import lru_cache
from html import escape
from pathlib import Path

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
FONTS = Path(__file__).resolve().parent / "fonts"

BG, CARD = "#070914", "#12162e"
CYAN, MAGENTA, YELLOW, GREEN, PINK = "#00f0ff", "#e600ff", "#ffb800", "#00ff66", "#ff2bd6"
TEXT, DIM, DIMMER, WHITE = "#d6def5", "#7d86a8", "#5d6688", "#ffffff"

MONO, MONO_BOLD, MONO_XBOLD = "JetBrainsMono-Regular", "JetBrainsMono-Bold", "JetBrainsMono-ExtraBold"
DISPLAY, DISPLAY_BOLD = "Outfit-Black", "Outfit-Bold"


@lru_cache(maxsize=None)
def _font(name):
    font = TTFont(FONTS / f"{name}.ttf")
    return font, font.getGlyphSet(), font.getBestCmap(), font["head"].unitsPerEm, font["hmtx"]


def text_width(text, size, font=MONO, spacing=0.0):
    f, _, cmap, upm, hmtx = _font(font)
    total = sum(hmtx[cmap.get(ord(c), ".notdef")][0] for c in text) * size / upm
    return total + spacing * max(len(text) - 1, 0)


def text(s, x, y, size, fill=TEXT, font=MONO, anchor="start", spacing=0.0, extra=""):
    """Return an SVG <path> drawing `s` with its baseline at y."""
    f, glyphs, cmap, upm, hmtx = _font(font)
    width = text_width(s, size, font, spacing)
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    scale = size / upm
    pen = SVGPathPen(glyphs)
    cursor = x
    for c in s:
        name = cmap.get(ord(c), ".notdef")
        glyphs[name].draw(TransformPen(pen, (scale, 0, 0, -scale, cursor, y)))
        cursor += hmtx[name][0] * scale + spacing
    d = re.sub(r"-?\d+\.\d+", lambda m: f"{float(m.group()):.1f}".rstrip("0").rstrip("."), pen.getCommands())
    return f'<path d="{d}" fill="{fill}"{extra}/>' if d else ""


def defs(uid, w, h):
    """Background gradients, neon glow and the rotating border gradient."""
    return f"""<defs>
  <radialGradient id="{uid}-g1" cx="88%" cy="0%" r="75%"><stop offset="0" stop-color="{MAGENTA}" stop-opacity=".26"/><stop offset="1" stop-color="{MAGENTA}" stop-opacity="0"/></radialGradient>
  <radialGradient id="{uid}-g2" cx="0%" cy="100%" r="75%"><stop offset="0" stop-color="{CYAN}" stop-opacity=".2"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>
  <radialGradient id="{uid}-g3" cx="45%" cy="60%" r="55%"><stop offset="0" stop-color="#2838ff" stop-opacity=".16"/><stop offset="1" stop-color="#2838ff" stop-opacity="0"/></radialGradient>
  <linearGradient id="{uid}-title" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{MAGENTA}"/></linearGradient>
  <linearGradient id="{uid}-border" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{CYAN}"/><stop offset=".5" stop-color="{MAGENTA}"/><stop offset="1" stop-color="{CYAN}"/>
    <animateTransform attributeName="gradientTransform" type="rotate" from="0 .5 .5" to="360 .5 .5" dur="10s" repeatCount="indefinite"/>
  </linearGradient>
  <filter id="{uid}-glow" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="{uid}-soft" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur stdDeviation="3" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <clipPath id="{uid}-clip"><rect width="{w}" height="{h}" rx="18"/></clipPath>
</defs>"""


def background(uid, w, h, stars=60, seed=7):
    rnd = random.Random(seed)
    out = [
        f'<g clip-path="url(#{uid}-clip)">',
        f'<rect width="{w}" height="{h}" fill="{BG}"/>',
        f'<rect width="{w}" height="{h}" fill="url(#{uid}-g1)"/>',
        f'<rect width="{w}" height="{h}" fill="url(#{uid}-g2)"/>',
        f'<rect width="{w}" height="{h}" fill="url(#{uid}-g3)"/>',
    ]
    for _ in range(stars):
        x, y, r = rnd.uniform(0, w), rnd.uniform(0, h), rnd.uniform(0.4, 1.4)
        colour = rnd.choice([CYAN, MAGENTA]) if rnd.random() < 0.12 else "#dce4ff"
        lo, dur, begin = rnd.uniform(0.15, 0.4), rnd.uniform(2.5, 6), rnd.uniform(0, 5)
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{colour}">'
            f'<animate attributeName="opacity" values="1;{lo:.2f};1" dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/></circle>'
        )
    out.append("</g>")
    return "".join(out)


def frame(uid, w, h, animated=True):
    """Outer border: rotating cyan / magenta gradient, like the Hyprland borders."""
    stroke = f"url(#{uid}-border)" if animated else "rgba(125,134,168,.3)"
    return f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="17" fill="none" stroke="{stroke}" stroke-width="2"/>'


def title_bar(uid, w, label, tag=None, tag_colour=CYAN):
    out = [
        f'<path d="M0,46 H{w}" stroke="{DIM}" stroke-opacity=".25"/>',
        f'<circle cx="24" cy="23" r="6" fill="{PINK}"/><circle cx="44" cy="23" r="6" fill="{YELLOW}"/><circle cx="64" cy="23" r="6" fill="{CYAN}"/>',
        text(label, w / 2, 28, 13, DIM, anchor="middle"),
    ]
    if tag:
        tw = text_width(tag, 11) + 22
        out.append(f'<rect x="{w - 18 - tw:.1f}" y="12" width="{tw:.1f}" height="22" rx="11" fill="none" stroke="{tag_colour}" stroke-opacity=".6"/>')
        out.append(text(tag, w - 18 - tw / 2, 27, 11, tag_colour, anchor="middle"))
    return "".join(out)


def keycap(label, x, y, size=13, super_=False, pad=11, h=30):
    """A keycap like the cheatsheet keys. Returns (svg, width)."""
    w = text_width(label, size, MONO_BOLD) + 2 * pad
    colour = MAGENTA if super_ else CYAN
    fill = "rgba(230,0,255,.14)" if super_ else "rgba(0,240,255,.10)"
    svg = (
        f'<rect x="{x:.1f}" y="{y + 3:.1f}" width="{w:.1f}" height="{h}" rx="8" fill="{colour}" fill-opacity=".25"/>'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="8" fill="{CARD}"/>'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h}" rx="8" fill="{fill}" stroke="{colour}" stroke-opacity=".6"/>'
        + text(label, x + w / 2, y + h / 2 + size * 0.36, size, "#e9f6ff", MONO_BOLD, anchor="middle")
    )
    return svg, w


def keycap_rows(labels, x, y, max_w, size=13, gap=8, row_h=40, supers=()):
    """Lay keycaps out in rows inside max_w. Returns (svg, height used)."""
    out, cx, cy = [], x, y
    for label in labels:
        w = text_width(label, size, MONO_BOLD) + 22
        if cx + w > x + max_w and cx > x:
            cx, cy = x, cy + row_h
        svg, w = keycap(label, cx, cy, size, label in supers)
        out.append(svg)
        cx += w + gap
    return "".join(out), cy - y + row_h


def svg(w, h, body, title):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{escape(title)}">'
        f"<title>{escape(title)}</title>{body}</svg>\n"
    )


def write(name, content):
    path = ROOT / "assets" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    print(f"wrote {path.relative_to(ROOT)} ({len(content) // 1024} KB)")
