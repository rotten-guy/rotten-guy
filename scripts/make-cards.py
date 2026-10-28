#!/usr/bin/env python3
"""Draw the static pictures of the profile README into assets/.

Usage: python3 scripts/make-cards.py   (needs: pip install fonttools)

banner.svg, the project cards and skills.svg. The pictures with live data are
drawn every day by GitHub Actions: make-stats.py (GitHub) and make-training.py
(typing and Root-Me).
"""
from nebula import (
    BG, CARD, CYAN, DIM, DISPLAY, DISPLAY_BOLD, GREEN, MAGENTA, MONO_BOLD, MONO_XBOLD, PINK, TEXT,
    WHITE, YELLOW, background, defs, frame, keycap_rows, svg, text, text_width, title_bar, write,
)

ARCH_LOGO = ["      /\\", "     /  \\", "    /    \\", "   /      \\", "  /   ,,   \\", " /   |  |   \\", "/_-''    ''-_\\"]

# small line icons, 24 x 24, drawn with the accent colour
ICONS = {
    "nebula": '<circle cx="12" cy="12" r="4"/><ellipse cx="12" cy="12" rx="10" ry="4" transform="rotate(-25 12 12)"/>',
    "keyboard": '<rect x="2" y="6" width="20" height="12" rx="2"/><path d="M6 10h0M10 10h0M14 10h0M18 10h0M7 14h10"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    "book": '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M4 21V5M8 7h7"/>',
}


def icon_box(uid, name, x, y, colour):
    return (
        f'<rect x="{x}" y="{y}" width="46" height="46" rx="12" fill="{BG}" fill-opacity=".7" stroke="{DIM}" stroke-opacity=".3"/>'
        f'<g transform="translate({x + 11} {y + 11})" fill="none" stroke="{colour}" stroke-width="2" '
        f'stroke-linecap="round" stroke-linejoin="round" filter="url(#{uid}-soft)">{ICONS[name]}</g>'
    )


# ───────────────────────── banner ─────────────────────────
def banner():
    uid, w, h = "bn", 1200, 420
    body = [defs(uid, w, h), background(uid, w, h, stars=110, seed=3)]

    body.append(text("QUICK SETTINGS · ", 64, 92, 15, TEXT, DISPLAY_BOLD, spacing=3.2))
    body.append(text("whoami", 64 + text_width("QUICK SETTINGS · ", 15, DISPLAY_BOLD, 3.2) + 3.2, 92, 15, MAGENTA, DISPLAY_BOLD, spacing=3.2))
    body.append(f'<g filter="url(#{uid}-glow)">{text("JOSHUA", 58, 196, 116, CYAN, DISPLAY)}</g>')
    body.append(
        f'<g filter="url(#{uid}-glow)">{text("GILLET", 104, 300, 116, MAGENTA, DISPLAY)}'
        '<animate attributeName="opacity" values="1;1;.5;1;.6;1;1" keyTimes="0;.9;.92;.94;.96;.98;1" dur="7s" repeatCount="indefinite"/></g>'
    )
    pill_w = text_width("ROTTEN_GUY", 16, DISPLAY, 2) + 46
    body.append(f'<rect x="64" y="326" width="{pill_w:.1f}" height="40" rx="20" fill="{MAGENTA}" fill-opacity=".14" stroke="{MAGENTA}" stroke-opacity=".6" stroke-width="2"/>')
    body.append(text("ROTTEN_GUY", 64 + pill_w / 2, 352, 16, MAGENTA, DISPLAY, anchor="middle", spacing=2))
    body.append(text("networks & telecoms student · arch + hyprland · split keyboards", 64, 398, 13, DIM))

    # kitty window with fastfetch
    x0, y0, ww, wh = 676, 40, 486, 340
    body.append(f'<rect x="{x0}" y="{y0}" width="{ww}" height="{wh}" rx="16" fill="{CARD}" fill-opacity=".82"/>')
    body.append(f'<rect x="{x0}" y="{y0}" width="{ww}" height="{wh}" rx="16" fill="none" stroke="url(#{uid}-border)" stroke-width="2"/>')
    body.append(f'<g transform="translate({x0} {y0})">{title_bar(uid, ww, "kitty · ~")}</g>')
    for i, line in enumerate(ARCH_LOGO):
        body.append(text(line, x0 + 24, y0 + 104 + i * 19, 14, MAGENTA, MONO_BOLD))
    rows = [("USR", "rotten_guy", CYAN), None, ("EDU", "BUT Networks & Telecoms", YELLOW), ("OS", "Arch Linux x86_64", CYAN),
            ("DE", "Hyprland (Lua config)", MAGENTA), ("SH", "zsh + starship", MAGENTA), None,
            ("ED", "LazyVim", GREEN), ("KB", "Lily58 · ZMK · wireless", GREEN)]
    y = y0 + 80
    for row in rows:
        if row is None:
            y += 8
            continue
        key, value, colour = row
        body.append(text(key, x0 + 196, y, 13.5, colour, MONO_XBOLD))
        body.append(text(value, x0 + 246, y, 13.5, WHITE))
        y += 21
    for i, colour in enumerate([PINK, "#ff007f", YELLOW, "#00a8ff", GREEN, "#ffd000", CYAN, "#ff0055"]):
        body.append(f'<circle cx="{x0 + 202 + i * 22}" cy="{y + 6}" r="6" fill="{colour}"/>')

    # starship prompt + typed command
    py = y0 + wh - 46
    segs = [("▲", "#303030", WHITE), ("~/profile", "#2f6fe8", WHITE), ("main", "#4fbf26", BG)]
    sx = x0 + 22
    for label, fill, colour in segs:
        sw = text_width(label, 12.5) + 30
        body.append(f'<path d="M{sx + 9},{py - 15} h{sw - 9} l-9,21 h-{sw - 9} z" fill="{fill}"/>')
        body.append(text(label, sx + sw / 2, py + 1, 12.5, colour, anchor="middle"))
        sx += sw + 12
        body.append(f'<path d="M{sx - 11},{py - 4} h9" stroke="{DIM}"/>')
    body.append(f'<path d="M{sx - 2},{py - 4} H{x0 + ww - 22}" stroke="{DIM}" stroke-opacity=".6"/>')
    cmd = "cat ~/projects/README.md"
    cy = py + 26
    body.append(text("❯", x0 + 22, cy, 14, GREEN, MONO_BOLD))
    full = text_width(cmd, 14)
    steps = len(cmd)
    values = ";".join(f"{full * i / steps:.1f}" for i in range(steps + 1)) + ";" + ";".join([f"{full:.1f}"] * 12)
    body.append(
        f'<clipPath id="{uid}-type"><rect x="{x0 + 42}" y="{cy - 16}" height="22" width="0">'
        f'<animate attributeName="width" values="{values}" dur="5s" repeatCount="indefinite" calcMode="discrete"/></rect></clipPath>'
    )
    body.append(f'<g clip-path="url(#{uid}-type)">{text(cmd, x0 + 42, cy, 14, TEXT)}</g>')
    body.append(
        f'<rect x="{x0 + 44}" y="{cy - 14}" width="2" height="18" fill="{CYAN}">'
        f'<animate attributeName="x" values="{";".join(f"{x0 + 44 + float(v):.1f}" for v in values.split(";"))}" dur="5s" repeatCount="indefinite" calcMode="discrete"/>'
        '<animate attributeName="opacity" values="1;0" dur="1s" repeatCount="indefinite" calcMode="discrete"/></rect>'
    )

    body.append(frame(uid, w, h))
    write("banner.svg", svg(w, h, "".join(body), "Joshua Gillet · rotten_guy · Nebula profile banner"))


# ───────────────────────── cards ─────────────────────────
def card(name, uid, label, tag, tag_colour, icon, accent, title, subtitle, bullets, tags, footer=None, progress=None):
    w, h = 600, 370
    body = [defs(uid, w, h), background(uid, w, h, stars=26, seed=len(title)), title_bar(uid, w, label, tag, tag_colour)]
    body.append(icon_box(uid, icon, 26, 66, accent))
    body.append(text(title, 88, 100, 30, WHITE, DISPLAY))
    body.append(text(subtitle, 26, 140, 13, MAGENTA, MONO_BOLD))
    y = 172
    for bold, rest in bullets:
        body.append(text("▸", 26, y, 13, CYAN))
        bw = text_width(bold, 13, MONO_BOLD)
        body.append(text(bold, 46, y, 13, CYAN, MONO_BOLD))
        body.append(text(rest, 46 + bw, y, 13, TEXT))
        y += 24
    if progress is not None:
        bar_y = y + 4
        body.append(f'<rect x="26" y="{bar_y}" width="{w - 52}" height="10" rx="5" fill="{BG}" stroke="{DIM}" stroke-opacity=".3"/>')
        body.append(
            f'<rect x="26" y="{bar_y}" width="{(w - 52) * progress:.1f}" height="10" rx="5" fill="url(#{uid}-title)">'
            '<animate attributeName="opacity" values="1;.55;1" dur="2s" repeatCount="indefinite"/></rect>'
        )
    if tags:
        tag_svg, _ = keycap_rows(tags, 26, h - 92, w - 52, size=12, row_h=36)
        body.append(tag_svg)
    if footer:
        left, right = footer
        body.append(text(left[0], 26, h - 24, 12, DIM))
        body.append(text(left[1], 26 + text_width(left[0], 12), h - 24, 12, left[2], MONO_BOLD))
        body.append(text(right, w - 26, h - 24, 12, CYAN, anchor="end"))
    body.append(frame(uid, w, h))
    write(f"{name}.svg", svg(w, h, "".join(body), f"{title}: {subtitle}"))


def cards():
    card(
        "card-dotfiles", "cd", "rotten_dotfiles · personal", "146 commits · 49 PRs", CYAN, "nebula", CYAN,
        "rotten_dotfiles", "A neon cyan / magenta Hyprland rice.",
        [("Fingerprint login", " on the greeter and the lock screen"),
         ("Animated borders", ", constant-speed gradient spin"),
         ("Backup tooling", " that syncs and repairs 2 machines"),
         ("NVIDIA sleep fix", ", PipeWire mic chain, cheatsheet")],
        ["Arch", "Hyprland · Lua", "Bash", "Python", "QML", "systemd"],
        footer=(("status: ", "daily driver", GREEN), "open repository →"),
    )
    card(
        "card-lily58", "cl", "rotten_lily58 · personal", "firmware", MAGENTA, "keyboard", MAGENTA,
        "rotten Lily58", "Wireless split keyboard, custom ZMK screens.",
        [("Bongo cat", " typing along, with glasses (and thug ones)"),
         ("Right screen", ": Arch logo, spinning wireframe cube"),
         ("Sprite pipeline", ": ASCII pixel art → C arrays"),
         ("4 BT profiles", ", firmware built by GitHub Actions")],
        ["C", "Zephyr RTOS", "ZMK", "Python", "GitHub Actions"],
        footer=(("status: ", "on my desk", GREEN), "open repository →"),
    )
    card(
        "card-portfolio", "cp", "rotten-guy.github.io · personal", "live", GREEN, "globe", CYAN,
        "rotten_portfolio", "This theme, as a website.",
        [("Workspaces", ": sections on keys 1 … 5, live clock"),
         ("SUPER + K", ": fuzzel-like search menu"),
         ("Greeter hero", ", kitty + fastfetch card"),
         ("No framework", ": plain HTML / CSS / JS")],
        ["HTML", "CSS", "JavaScript", "GitHub Pages"],
        footer=(("status: ", "online", GREEN), "rotten-guy.github.io →"),
    )
    card(
        "card-guides", "cg", "~/dotfiles/docs · write-ups", "4 guides", YELLOW, "book", YELLOW,
        "Write-ups", "Things I fixed, written down.",
        [("ZMK dongle", ": solder-free, illustrated"),
         ("IKEv2 + EAP VPN", " on Arch with strongSwan"),
         ("Tablet as a monitor", ": Sunshine + Moonlight"),
         ("Arch notes", ": backups, NTFS, Bluetooth, WSL")],
        ["Markdown", "Networking", "Linux"],
        footer=(("status: ", "growing", GREEN), "read them →"),
    )
    # card-rootme.svg and card-typing.svg are drawn with live data by make-training.py


# ───────────────────────── skills ─────────────────────────
def skills():
    uid, w = "sk", 1200
    groups = [
        ("NETWORKS & SYSTEMS", ["Linux", "Arch", "systemd", "SSH", "TCP/IP", "VPN · IKEv2", "NetworkManager", "BlueZ", "PAM", "Docker", "WSL · Kali"], {"Linux", "Arch"}),
        ("LANGUAGES", ["Bash", "Python", "Lua", "C", "C++", "PHP", "SQL", "HTML", "CSS", "JavaScript", "TypeScript", "QML"], {"Bash", "Python", "Lua"}),
        ("TOOLS", ["Git", "GitHub", "Neovim", "GitHub Actions", "MySQL", "Node.js", "kitty · zsh", "Claude Code"], {"Git", "GitHub", "Neovim"}),
        ("HARDWARE", ["ZMK", "Zephyr RTOS", "nice!nano", "e-paper", "Arduino", "Split keyboards"], {"ZMK"}),
    ]
    col_w, gap, top = (w - 3 * 28) / 2, 28, 96
    blocks, heights = [], []
    for i, (name, labels, supers) in enumerate(groups):
        x = 28 + (i % 2) * (col_w + gap)
        keys, used = keycap_rows(labels, x + 22, 0, col_w - 44, size=13, supers=supers)
        heights.append(used + 64)
        blocks.append((x, name, keys))
    row_h = [max(heights[0], heights[1]), max(heights[2], heights[3])]
    h = int(top + row_h[0] + row_h[1] + gap + 50)
    body = [defs(uid, w, h), background(uid, w, h, stars=50, seed=11)]
    body.append(text("~/.config/skills", 30, 46, 13, DIM))
    body.append(text("❯ ", 30 - 16, 46, 13, GREEN))
    body.append(text("SKILLS", 28, 84, 34, f"url(#{uid}-title)", MONO_XBOLD, spacing=6))
    body.append(text("magenta keys = daily use", w - 30, 82, 13, DIM, anchor="end"))
    for i, (x, name, keys) in enumerate(blocks):
        y = top + (0 if i < 2 else row_h[0] + gap)
        bh = row_h[0 if i < 2 else 1]
        body.append(f'<rect x="{x:.1f}" y="{y + 10}" width="{col_w:.1f}" height="{bh - 10}" rx="16" fill="{CARD}" fill-opacity=".72" stroke="{CYAN}" stroke-opacity=".28"/>')
        body.append(text(name, x + 22, y + 44, 13, MAGENTA, MONO_XBOLD, spacing=2.2))
        body.append(f'<g transform="translate(0 {y + 62})">{keys}</g>')
    body.append(frame(uid, w, h))
    write("skills.svg", svg(w, h, "".join(body), "Skills drawn as keycaps"))


if __name__ == "__main__":
    banner()
    cards()
    skills()
