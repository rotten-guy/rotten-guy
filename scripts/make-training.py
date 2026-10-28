#!/usr/bin/env python3
"""Fetch typing and Root-Me stats, then draw them in the Nebula style.

Run by .github/workflows/stats.yml every day:
    python3 scripts/make-training.py            # fetch + draw into assets/
Local preview with made-up numbers, never committed:
    python3 scripts/make-training.py --sample /tmp/preview

Sources (all optional, a source that fails keeps its previous data):
- keybr      public profile data, https://www.keybr.com/_/sync/data/<id> (binary, see read_keybr)
- Monkeytype public profile, https://api.monkeytype.com/users/<name>/profile
- Root-Me    official API, needs the ROOTME_API_KEY secret

Writes assets/training.json (also read by the website), typing.svg (Lily58 typing
"i use arch btw" at the real speed), activity.svg (typing calendar), card-typing.svg
and card-rootme.svg.
"""
import datetime as dt
import json
import os
import random
import struct
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from nebula import (
    BG, CARD, CYAN, DIM, DISPLAY, GREEN, MAGENTA, MONO, MONO_BOLD, MONO_XBOLD, ROOT, TEXT, WHITE, YELLOW,
    background, defs, frame, svg, text, text_width, title_bar,
)

KEYBR_ID = "752ae7r"
MONKEYTYPE_USER = "rotten_guy"
ROOTME_USER = "rotten-guy"
GAG = "i use arch btw"
DATA = ROOT / "assets" / "training.json"
UA = {"User-Agent": "rotten-guy-profile-stats (github.com/rotten-guy/rotten-guy)"}


# ───────────────────────── fetching ─────────────────────────
def get(url, headers=None, raw=False):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read()
    return body if raw else json.loads(body)


def read_keybr(buf):
    """Parse keybr's binary results file (packages/keybr-result-io in keybr.com).

    Header: int32 0x4B455942 "KEYB", int32 version 2. Then results until the end:
    uint8 layout, uint8 text type, uint32 timestamp (s), VLQ time (ms), VLQ length,
    VLQ errors, VLQ histogram size, then size × 4 VLQs. Big endian, VLQs are
    7-bit groups with the high bit set on every byte but the last.
    """
    pos = 0

    def u8():
        nonlocal pos
        pos += 1
        return buf[pos - 1]

    def vlq():
        value = 0
        while True:
            b = u8()
            value = (value << 7) | (b & 0x7F)
            if not b & 0x80:
                return value

    if len(buf) < 8:
        return []
    sig, ver = struct.unpack(">II", buf[:8])
    if sig != 0x4B455942 or ver != 2:
        raise ValueError(f"unexpected keybr header {sig:#x} v{ver}")
    pos, results = 8, []
    while pos < len(buf):
        u8(), u8()
        (ts,) = struct.unpack(">I", buf[pos:pos + 4])
        pos += 4
        time_ms, length, errors, size = vlq(), vlq(), vlq(), vlq()
        for _ in range(size * 4):
            vlq()
        results.append((ts, time_ms, length, errors))
    return results


def fetch_keybr():
    results = read_keybr(get(f"https://www.keybr.com/_/sync/data/{KEYBR_ID}", raw=True))
    if not results:
        return None
    days, speeds = {}, []
    for ts, time_ms, length, errors in results:
        day = dt.datetime.fromtimestamp(ts, dt.timezone.utc).date().isoformat()
        d = days.setdefault(day, {"minutes": 0.0, "lessons": 0})
        d["minutes"] += time_ms / 60000
        d["lessons"] += 1
        if time_ms > 0 and length > 0:
            speeds.append((length / (time_ms / 60000) / 5, 1 - errors / max(length, 1)))
    recent = speeds[-50:]
    return {
        "lessons": len(results),
        "minutes": round(sum(t for _, t, _, _ in results) / 60000, 1),
        "wpm_avg": round(sum(s for s, _ in recent) / len(recent), 1),
        "wpm_best": round(max(s for s, _ in speeds), 1),
        "accuracy": round(100 * sum(a for _, a in recent) / len(recent), 1),
        "first": dt.datetime.fromtimestamp(results[0][0], dt.timezone.utc).date().isoformat(),
        "days": {k: {"minutes": round(v["minutes"], 1), "lessons": v["lessons"]} for k, v in days.items()},
    }


def fetch_monkeytype():
    data = get(f"https://api.monkeytype.com/users/{urllib.parse.quote(MONKEYTYPE_USER)}/profile")["data"]
    pbs = {}
    for mode in ("15", "30", "60", "120"):
        runs = (data.get("personalBests") or {}).get("time", {}).get(mode) or []
        if runs:
            best = max(runs, key=lambda r: r["wpm"])
            pbs[mode] = {"wpm": round(best["wpm"], 1), "acc": round(best["acc"], 1)}
    stats = data.get("typingStats") or {}
    out = {
        "tests": stats.get("completedTests", 0),
        "minutes": round((stats.get("timeTyping") or 0) / 60, 1),
        "streak": data.get("streak", 0),
        "max_streak": data.get("maxStreak", 0),
        "pb": pbs,
        "days": {},
    }
    activity = data.get("testActivity")  # only when "show activity on public profile" is on
    if activity:
        last = dt.datetime.fromtimestamp(activity["lastDay"] / 1000, dt.timezone.utc).date()
        tests = activity["testsByDays"]
        for i, count in enumerate(tests):
            if count:
                out["days"][(last - dt.timedelta(days=len(tests) - 1 - i)).isoformat()] = count
    return out


def fetch_rootme():
    key = os.environ.get("ROOTME_API_KEY")
    if not key:
        return None
    cookie = {"Cookie": f"api_key={key}"}
    found = get(f"https://api.www.root-me.org/auteurs?nom={urllib.parse.quote(ROOTME_USER)}", cookie)
    # the API answers [{"0": {"id_auteur": "…", "nom": "…"}, …}]
    candidates = [v for v in (found[0] if isinstance(found, list) else found).values() if isinstance(v, dict)]
    match = next((c for c in candidates if c.get("nom", "").lower() == ROOTME_USER), candidates[0])
    me = get(f"https://api.www.root-me.org/auteurs/{match['id_auteur']}", cookie)
    validations = me.get("validations") or []
    validations = sorted(validations, key=lambda v: v.get("date", ""), reverse=True)
    return {
        "score": int(me.get("score") or 0),
        "position": int(me.get("position") or 0),
        "rank": me.get("rang") or "",
        "solved": len(validations),
        "recent": [{"title": v.get("titre", ""), "date": v.get("date", "")[:10]} for v in validations[:3]],
    }


def fetch():
    data = json.loads(DATA.read_text()) if DATA.exists() else {}
    for name, fn in (("keybr", fetch_keybr), ("monkeytype", fetch_monkeytype), ("rootme", fetch_rootme)):
        try:
            value = fn()
            if value is not None:
                data[name] = value
                print(f"{name}: ok")
            else:
                print(f"{name}: skipped")
        except Exception as err:  # keep the previous data, the other sources still update
            print(f"{name}: failed ({err!r}), keeping previous data")
    data["updated"] = dt.date.today().isoformat()
    return data


def sample():
    rnd = random.Random(4)
    today = dt.date.today()
    days, mt_days = {}, {}
    for i in range(300):
        day = today - dt.timedelta(days=i)
        if rnd.random() < 0.55:
            m = round(rnd.choice([4, 8, 10, 12, 15, 22, 35]) * rnd.uniform(.8, 1.2), 1)
            days[day.isoformat()] = {"minutes": m, "lessons": int(m * 2.3)}
        if i < 40 and rnd.random() < 0.4:
            mt_days[day.isoformat()] = rnd.randint(1, 12)
    return {
        "updated": today.isoformat(),
        "keybr": {"lessons": 2310, "minutes": round(sum(d["minutes"] for d in days.values()), 1), "wpm_avg": 74.2,
                  "wpm_best": 96.8, "accuracy": 97.1, "first": "2025-01-12", "days": days},
        "monkeytype": {"tests": 128, "minutes": 61.5, "streak": 4, "max_streak": 9,
                       "pb": {"15": {"wpm": 98.4, "acc": 97.0}, "30": {"wpm": 91.2, "acc": 96.5},
                              "60": {"wpm": 84.7, "acc": 96.8}}, "days": mt_days},
        "rootme": {"score": 245, "position": 48213, "rank": "newbie", "solved": 14,
                   "recent": [{"title": "HTTP - Open redirect", "date": "2026-10-20"},
                              {"title": "HTTP - User-agent", "date": "2026-10-18"},
                              {"title": "HTML - Source code", "date": "2026-10-15"}]},
    }


# ───────────────────────── helpers ─────────────────────────
def typing_wpm(data):
    """Speed used for the animation: Monkeytype 60 s PB, else keybr average."""
    pb = (data.get("monkeytype") or {}).get("pb", {})
    for mode in ("60", "30", "15"):
        if mode in pb:
            return pb[mode]["wpm"]
    return (data.get("keybr") or {}).get("wpm_avg") or 60


def hours(minutes):
    h, m = divmod(int(round(minutes)), 60)
    return f"{h}h{m:02d}" if h else f"{m} min"


def merged_days(data):
    """{date: (keybr minutes, monkeytype tests)} for the calendar."""
    out = {}
    for day, d in ((data.get("keybr") or {}).get("days") or {}).items():
        out[day] = (d["minutes"], 0)
    for day, n in ((data.get("monkeytype") or {}).get("days") or {}).items():
        out[day] = (out.get(day, (0, 0))[0], n)
    return out


def streaks(days):
    active = sorted(d for d, (m, t) in days.items() if m or t)
    best = cur = 0
    prev = None
    for d in active:
        day = dt.date.fromisoformat(d)
        cur = cur + 1 if prev and (day - prev).days == 1 else 1
        best = max(best, cur)
        prev = day
    today = dt.date.today()
    current = 0
    day = today if today.isoformat() in days else today - dt.timedelta(days=1)
    while day.isoformat() in days and any(days[day.isoformat()]):
        current += 1
        day -= dt.timedelta(days=1)
    return current, best


# ───────────────────────── Lily58 geometry (same as dotfiles make-keymap.py) ─────────────────────────
STAGGER = [0.5, 0.38, 0.12, 0, 0.12, 0.25]
INNER = (6.05, 2.75)
THUMBS = [(2.5, 4.1), (3.5, 4.12), (4.5, 4.3)]
BIG_THUMB = (5.8, 4.3, 30)
HALF_W, GAP = 7.2, 2.6
WIDTH = 2 * HALF_W + GAP
BASE = (["Esc", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "`",
         "Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "-",
         "Shift", "A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'",
         "Ctrl", "Z", "X", "C", "V", "B", "[", "]", "N", "M", ",", ".", "/", "Shift",
         "Alt", "Super", "LOWER", "Space", "Enter", "RAISE", "Bksp", "Super"])


def positions():
    def left(c, r):
        return (c, STAGGER[c] + r, 0)

    def mirror(p):
        x, y, rot = p
        return (WIDTH - x - 1, y, -rot)

    pos = []
    for r in range(3):
        pos += [left(c, r) for c in range(6)] + [mirror(left(5 - c, r)) for c in range(6)]
    pos += [left(c, 3) for c in range(6)] + [(*INNER, 0), mirror((*INNER, 0))]
    pos += [mirror(left(5 - c, 3)) for c in range(6)]
    thumbs = [(x, y, 0) for x, y in THUMBS] + [BIG_THUMB]
    pos += thumbs + [mirror(t) for t in reversed(thumbs)]
    return pos


def key_index(char):
    return BASE.index("Space") if char == " " else BASE.index(char.upper())


# ───────────────────────── typing.svg ─────────────────────────
def typing_svg(data):
    uid, w, h = "ty", 1200, 520
    wpm = typing_wpm(data)
    step = 60 / (wpm * 5)                       # seconds per character
    typed = len(GAG) * step
    t0, hold = 0.8, 3.2
    dur = t0 + typed + hold
    U, ox, oy = 40, 40, 132
    body = [defs(uid, w, h), background(uid, w, h, stars=70, seed=9)]
    body.append(text("❯ ", 14, 46, 13, GREEN))
    body.append(text(f"keybr --profile {KEYBR_ID} · monkeytype --user {MONKEYTYPE_USER}", 30, 46, 13, DIM))
    body.append(text("TYPING", 28, 84, 34, f"url(#{uid}-title)", MONO_XBOLD, spacing=6))
    body.append(text("on my Lily58, at my real speed", w - 30, 82, 13, DIM, anchor="end"))

    # screen line above the keyboard
    sx, sy, sw = ox, oy - 36, WIDTH * U
    body.append(f'<rect x="{sx}" y="{sy - 4}" width="{sw:.0f}" height="34" rx="10" fill="{BG}" fill-opacity=".8" stroke="{DIM}" stroke-opacity=".35"/>')
    body.append(text("❯", sx + 14, sy + 18, 14, GREEN, MONO_BOLD))
    cx = sx + 36
    char_w = text_width("m", 15)
    for i, ch in enumerate(GAG):
        on = (t0 + (i + 1) * step) / dur
        body.append(
            f'<g opacity="0">{text(ch, cx + i * char_w, sy + 18, 15, WHITE)}'
            f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{on:.4f};1" calcMode="discrete" dur="{dur:.2f}s" repeatCount="indefinite"/></g>'
        )
    xs = ";".join(f"{cx + i * char_w:.1f}" for i in range(len(GAG) + 1))
    kt = ";".join(["0"] + [f"{(t0 + (i + 1) * step) / dur:.4f}" for i in range(len(GAG))])
    body.append(
        f'<rect x="{cx:.1f}" y="{sy + 3}" width="2" height="19" fill="{CYAN}">'
        f'<animate attributeName="x" values="{xs}" keyTimes="{kt}" calcMode="discrete" dur="{dur:.2f}s" repeatCount="indefinite"/>'
        '<animate attributeName="opacity" values="1;0" dur="1s" calcMode="discrete" repeatCount="indefinite"/></rect>'
    )
    gag_on = (t0 + typed + 0.4) / dur
    body.append(
        f'<g opacity="0">{text("0 typos · nobody asked", sx + sw - 14, sy + 18, 12, MAGENTA, MONO_BOLD, anchor="end")}'
        f'<animate attributeName="opacity" values="0;1;0" keyTimes="0;{gag_on:.4f};1" calcMode="discrete" dur="{dur:.2f}s" repeatCount="indefinite"/></g>'
    )

    # keyboard, with a flash on every key press
    presses = {}
    for i, ch in enumerate(GAG):
        presses.setdefault(key_index(ch), []).append(t0 + i * step)
    flash = min(0.14, step * 0.8)
    for i, (x, y, rot) in enumerate(positions()):
        big = i >= 50 and rot != 0
        kw, kh = 0.9 * U, (1.4 if big else 0.9) * U
        px, py = ox + (x + 0.05) * U, oy + 26 + (y + 0.05) * U
        kcx, kcy = px + kw / 2, py + kh / 2
        tr = f' transform="rotate({rot} {kcx:.1f} {kcy:.1f})"' if rot else ""
        thumb = i >= 50
        stroke = MAGENTA if thumb else CYAN
        label = BASE[i]
        size = 13 if len(label) <= 2 else (10 if len(label) <= 5 else 8)
        g = [f'<g{tr}><rect x="{px:.1f}" y="{py:.1f}" width="{kw:.1f}" height="{kh:.1f}" rx="7" fill="{CARD}" stroke="{stroke}" stroke-opacity=".7" stroke-width="1.4"/>']
        if i in presses:
            times = []
            for t in presses[i]:
                times += [(t / dur, 1), ((t + flash) / dur, 0)]
            keytimes = "0;" + ";".join(f"{k:.4f}" for k, _ in times) + ";1"
            values = "0;" + ";".join(str(v) for _, v in times) + ";0"
            colour = MAGENTA if thumb else CYAN
            g.append(f'<rect x="{px:.1f}" y="{py:.1f}" width="{kw:.1f}" height="{kh:.1f}" rx="7" fill="{colour}" opacity="0" filter="url(#{uid}-soft)">'
                     f'<animate attributeName="opacity" values="{values}" keyTimes="{keytimes}" calcMode="discrete" dur="{dur:.2f}s" repeatCount="indefinite"/></rect>')
        g.append(text(label, kcx, kcy + size * 0.36, size, TEXT, MONO_BOLD, anchor="middle"))
        g.append("</g>")
        body.append("".join(g))

    # stats column
    kb, mt = data.get("keybr") or {}, data.get("monkeytype") or {}
    px0, pw = ox + WIDTH * U + 30, w - (ox + WIDTH * U + 30) - 28
    tiles = [
        (f"{wpm:.0f}", "WPM IN THIS ANIMATION", "monkeytype 60 s PB" if "60" in (mt.get("pb") or {}) else "keybr average", CYAN),
        (f"{kb.get('wpm_avg', 0):.0f}", "KEYBR AVERAGE", f"best {kb.get('wpm_best', 0):.0f} · {kb.get('accuracy', 0):.0f}% accuracy", MAGENTA),
        (hours(kb.get("minutes", 0) + mt.get("minutes", 0)), "TIME TYPING", f"{kb.get('lessons', 0)} keybr lessons · {mt.get('tests', 0)} tests", CYAN),
    ]
    for i, (big, label, sub, colour) in enumerate(tiles):
        y = 116 + i * 122
        body.append(f'<rect x="{px0:.1f}" y="{y}" width="{pw:.1f}" height="106" rx="14" fill="{CARD}" fill-opacity=".72" stroke="{colour}" stroke-opacity=".3"/>')
        body.append(f'<g filter="url(#{uid}-soft)">{text(big, px0 + pw / 2, y + 52, 38, colour, DISPLAY, anchor="middle")}</g>')
        body.append(text(label, px0 + pw / 2, y + 76, 11, TEXT, MONO_XBOLD, anchor="middle", spacing=1.4))
        body.append(text(sub, px0 + pw / 2, y + 93, 10, DIM, anchor="middle"))
    body.append(frame(uid, w, h))
    return svg(w, h, "".join(body), f"Lily58 typing '{GAG}' at {wpm:.0f} WPM")


# ───────────────────────── activity.svg ─────────────────────────
LEVELS = ["#161b3a", "rgba(0,240,255,.28)", "rgba(0,240,255,.6)", "#7a6cff", MAGENTA]


def level(minutes, tests):
    total = minutes + tests * 0.75   # a Monkeytype test is about 45 s
    if total <= 0:
        return 0
    return 1 if total < 5 else 2 if total < 12 else 3 if total < 25 else 4


def activity_svg(data):
    uid, w, h = "ac", 1200, 330
    days = merged_days(data)
    today = dt.date.today()
    start = today - dt.timedelta(days=364 + (today.weekday() + 1) % 7)
    body = [defs(uid, w, h), background(uid, w, h, stars=40, seed=12)]
    body.append(text("❯ ", 14, 46, 13, GREEN))
    body.append(text("cat ~/.cache/typing/*.log | wc -l", 30, 46, 13, DIM))
    body.append(text("TYPING LOG", 28, 84, 34, f"url(#{uid}-title)", MONO_XBOLD, spacing=6))
    year = [d for d in days if d >= start.isoformat()]
    minutes = sum(days[d][0] for d in year)
    current, best = streaks(days)
    body.append(text(f"{hours(minutes)} · {len(year)} days · streak {current} (best {best})", w - 30, 82, 13, DIM, anchor="end"))
    cell, gap = 15, 4
    weeks = ((today - start).days + 7) // 7
    gx = (w - (weeks * (cell + gap) - gap)) / 2
    for i in range((today - start).days + 1):
        day = start + dt.timedelta(days=i)
        col, row = divmod(i, 7)
        m, t = days.get(day.isoformat(), (0, 0))
        lv = level(m, t)
        f = f' filter="url(#{uid}-soft)"' if lv == 4 else ""
        body.append(f'<rect x="{gx + col * (cell + gap):.1f}" y="{112 + row * (cell + gap)}" width="{cell}" height="{cell}" rx="4" fill="{LEVELS[lv]}"{f}/>')
    lx = w - 48 - 5 * 19 - text_width("more", 10)
    body.append(text("less", lx - 8, 278, 10, DIM, anchor="end"))
    for i, colour in enumerate(LEVELS):
        body.append(f'<rect x="{lx + i * 19:.1f}" y="267" width="13" height="13" rx="3" fill="{colour}"/>')
    body.append(text("more", lx + 5 * 19, 278, 10, DIM))
    body.append(text("keybr minutes + Monkeytype tests per day · hover the days on rotten-guy.github.io", 48, 278, 10, DIM))
    body.append(text(f"updated {data.get('updated', today.isoformat())} · GitHub Actions", w / 2, h - 18, 10, DIM, anchor="middle"))
    body.append(frame(uid, w, h))
    return svg(w, h, "".join(body), "Typing calendar")


# ───────────────────────── small cards ─────────────────────────
def card(uid, label, tag, tag_colour, title, subtitle, tiles, lines, footer):
    w, h = 600, 370
    body = [defs(uid, w, h), background(uid, w, h, stars=26, seed=len(title)), title_bar(uid, w, label, tag, tag_colour)]
    body.append(text(title, 26, 100, 30, WHITE, DISPLAY))
    body.append(text(subtitle, 26, 132, 13, MAGENTA, MONO_BOLD))
    tw = (w - 52 - 2 * 12) / 3
    for i, (big, small, colour) in enumerate(tiles):
        x = 26 + i * (tw + 12)
        body.append(f'<rect x="{x:.1f}" y="150" width="{tw:.1f}" height="84" rx="12" fill="{BG}" fill-opacity=".6" stroke="{colour}" stroke-opacity=".3"/>')
        body.append(f'<g filter="url(#{uid}-soft)">{text(big, x + tw / 2, 194, 30 if len(big) < 7 else 22, colour, DISPLAY, anchor="middle")}</g>')
        body.append(text(small, x + tw / 2, 220, 10, DIM, anchor="middle", spacing=1))
    y = 262
    for bold, rest in lines:
        body.append(text("▸", 26, y, 12.5, CYAN))
        bw = text_width(bold, 12.5, MONO_BOLD)
        body.append(text(bold, 46, y, 12.5, CYAN, MONO_BOLD))
        body.append(text(rest, 46 + bw, y, 12.5, TEXT))
        y += 22
    left, right = footer
    body.append(text(left[0], 26, h - 22, 12, DIM))
    body.append(text(left[1], 26 + text_width(left[0], 12), h - 22, 12, left[2], MONO_BOLD))
    body.append(text(right, w - 26, h - 22, 12, CYAN, anchor="end"))
    body.append(frame(uid, w, h))
    return svg(w, h, "".join(body), f"{title}: {subtitle}")


def clip(s, n=44):
    return s if len(s) <= n else s[: n - 1] + "…"


def rootme_card(data):
    rm = data.get("rootme")
    if not rm:
        return card("cr", "~/training · security", "in progress", MAGENTA, "Root-Me", "Hacking challenges, one category at a time.",
                    [("…", "SCORE", CYAN), ("…", "SOLVED", MAGENTA), ("…", "POSITION", CYAN)],
                    [("Web-server", ", network, cracking, forensics"), ("Goal", ": the security side of networks & telecoms")],
                    (("status: ", "warming up", GREEN), "root-me.org/rotten-guy →"))
    lines = [(clip(r["title"], 34), f"  {r['date']}") for r in rm["recent"]] or [("No challenge yet", ", the first one is coming")]
    return card("cr", "~/training · security", rm.get("rank") or "in progress", MAGENTA, "Root-Me", "Latest validated challenges:",
                [(str(rm["score"]), "POINTS", CYAN), (str(rm["solved"]), "SOLVED", MAGENTA), (f"#{rm['position']}", "POSITION", CYAN)],
                lines, (("updated ", data.get("updated", ""), GREEN), "root-me.org/rotten-guy →"))


def typing_card(data):
    kb, mt = data.get("keybr") or {}, data.get("monkeytype") or {}
    pb = mt.get("pb") or {}
    best = max((v["wpm"] for v in pb.values()), default=kb.get("wpm_best", 0))
    current, longest = streaks(merged_days(data))
    lines = [("keybr", f": {kb.get('lessons', 0)} lessons since {kb.get('first', '…')}"),
             ("Monkeytype", ": " + " · ".join(f"{m}s {v['wpm']:.0f}" for m, v in sorted(pb.items(), key=lambda kv: int(kv[0]))) if pb else ": first tests soon"),
             ("Streak", f": {current} days (best {longest})")]
    return card("ct", "~/training · typing", "on a Lily58", YELLOW, "Typing", "keybr + Monkeytype, on my own keyboard.",
                [(f"{kb.get('wpm_avg', 0):.0f}", "AVG WPM", CYAN), (f"{best:.0f}", "BEST WPM", MAGENTA),
                 (hours(kb.get("minutes", 0) + mt.get("minutes", 0)), "TYPING", CYAN)],
                lines, (("updated ", data.get("updated", ""), GREEN), "keybr.com/profile →"))


def draw(data, out):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for name, content in (("typing.svg", typing_svg(data)), ("activity.svg", activity_svg(data)),
                          ("card-typing.svg", typing_card(data)), ("card-rootme.svg", rootme_card(data))):
        (out / name).write_text(content)
        print(f"wrote {out / name} ({len(content) // 1024} KB)")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--sample":
        data = sample()
        Path(sys.argv[2]).mkdir(parents=True, exist_ok=True)
        (Path(sys.argv[2]) / "training.json").write_text(json.dumps(data, indent=1))
        draw(data, sys.argv[2])
    else:
        data = fetch()
        DATA.write_text(json.dumps(data, indent=1, sort_keys=True) + "\n")
        draw(data, ROOT / "assets")
