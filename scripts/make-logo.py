#!/usr/bin/env python3
"""Draw the two logos into assets/logo/.

Usage: python3 scripts/make-logo.py   (needs: pip install fonttools)

- avatar-circle.svg / avatar-square.svg: "rotten / guy>_", the personal logo
  (profile picture, anything about me as a person)
- site.svg: ">_", the logo of the portfolio website (favicon, nav bar)

PNG exports: open the SVG in a browser or run
`inkscape avatar-circle.svg -w 1024 -o avatar-circle.png`.
"""
from nebula import BG, CYAN, DISPLAY, MAGENTA, ROOT, text, text_width

OUT = ROOT / "assets" / "logo"


def defs(uid):
    return f"""<defs>
<linearGradient id="{uid}g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{MAGENTA}"/></linearGradient>
<radialGradient id="{uid}bg" cx="72%" cy="22%" r="90%"><stop offset="0" stop-color="#2a0a4a"/><stop offset=".6" stop-color="#0b0e22"/><stop offset="1" stop-color="{BG}"/></radialGradient>
<filter id="{uid}glow" x="-20%" y="-40%" width="140%" height="180%"><feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>"""


def prompt(x, baseline, h):
    """'>_' as tall as the lowercase letters, with a thick underscore sitting low like a terminal cursor."""
    w, sw, top = h * 0.55, h * 0.2, baseline - h
    chevron = (f'<path d="M{x + sw / 2:.1f} {top + sw / 2:.1f} L{x + w:.1f} {top + h / 2:.1f} L{x + sw / 2:.1f} {baseline - sw / 2:.1f}" '
               f'fill="none" stroke="{MAGENTA}" stroke-width="{sw:.1f}" stroke-linecap="round" stroke-linejoin="round"/>')
    ux, uh, uw = x + w + h * 0.16, sw * 1.35, h * 0.72
    cursor = f'<rect x="{ux:.1f}" y="{baseline - uh * 0.45:.1f}" width="{uw:.1f}" height="{uh:.1f}" rx="{uh / 2:.1f}" fill="{CYAN}"/>'
    return chevron + cursor, ux + uw - x


def wordmark(target=142, gap=26):
    """'rotten' over 'guy>_', both lines exactly `target` wide, centred on (128, 128)."""
    s1 = target / text_width("rotten", 100, DISPLAY) * 100
    s2 = target / (text_width("guy", 100, DISPLAY) + 10 + prompt(0, 0, 50)[1]) * 100
    block = s1 * 0.72 + gap + s2 * 0.72  # cap of "rotten", gap, x-height + descender of "guy"
    y1 = 128 - block / 2 + s1 * 0.72
    y2 = y1 + gap + s2 * 0.5
    x = 128 - target / 2
    gw = text_width("guy", s2, DISPLAY)
    cursor, _ = prompt(x + gw + s2 * 0.1, y2, s2 * 0.5)
    return text("rotten", x, y1, s1, CYAN, DISPLAY) + text("guy", x, y2, s2, MAGENTA, DISPLAY) + cursor


def avatar(shape):
    uid = "av"
    if shape == "circle":
        frame = (f'<circle cx="128" cy="128" r="124" fill="url(#{uid}bg)"/>'
                 f'<circle cx="128" cy="128" r="120" fill="none" stroke="url(#{uid}g)" stroke-width="6"/>')
    else:  # full-bleed square: survives any crop a website applies
        frame = (f'<rect width="256" height="256" fill="url(#{uid}bg)"/>'
                 f'<rect x="10" y="10" width="236" height="236" rx="54" fill="none" stroke="url(#{uid}g)" stroke-width="6"/>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">'
            f'{defs(uid)}{frame}<g filter="url(#{uid}glow)">{wordmark()}</g></svg>\n')


def site():
    uid = "si"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" width="256" height="256">{defs(uid)}'
            f'<circle cx="128" cy="128" r="120" fill="url(#{uid}bg)"/>'
            f'<g filter="url(#{uid}glow)"><path d="M66 82 L120 128 L66 174" fill="none" stroke="{MAGENTA}" stroke-width="20" '
            f'stroke-linecap="round" stroke-linejoin="round"/><rect x="134" y="160" width="62" height="18" rx="9" fill="{CYAN}"/></g>'
            f'<circle cx="128" cy="128" r="117" fill="none" stroke="url(#{uid}g)" stroke-width="5"/></svg>\n')


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, content in (("avatar-circle.svg", avatar("circle")), ("avatar-square.svg", avatar("square")), ("site.svg", site())):
        (OUT / name).write_text(content)
        print(f"wrote assets/logo/{name}")
