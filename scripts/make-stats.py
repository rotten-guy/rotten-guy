#!/usr/bin/env python3
"""Draw assets/stats.svg from the GitHub API, in the Nebula style.

Run by .github/workflows/stats.yml every day (needs GITHUB_TOKEN).
Local preview with made-up numbers, never committed:
    python3 scripts/make-stats.py --sample /tmp/stats.svg
"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request

from nebula import (
    CARD, CYAN, DIM, GREEN, MAGENTA, MONO, MONO_XBOLD, DISPLAY, TEXT, YELLOW,
    background, defs, frame, svg, text, text_width, write,
)

USER = "PoUrRiTuRe"
QUERY = """
query($login: String!) {
  user(login: $login) {
    followers { totalCount }
    contributionsCollection {
      contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes { stargazerCount languages(first: 10) { edges { size node { name } } } }
    }
  }
}"""

LEVELS = ["#161b3a", "rgba(0,240,255,.28)", "rgba(0,240,255,.6)", "#7a6cff", MAGENTA]
LANG_COLOURS = [CYAN, MAGENTA, YELLOW, GREEN, "#7a6cff", "#ff2bd6", DIM]


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req) as resp:
        data = json.load(resp)
    if "errors" in data:
        sys.exit(f"GraphQL errors: {data['errors']}")
    user = data["data"]["user"]
    cal = user["contributionsCollection"]["contributionCalendar"]
    days = [(d["date"], d["contributionCount"]) for w in cal["weeks"] for d in w["contributionDays"]]
    langs = {}
    for repo in user["repositories"]["nodes"]:
        for edge in repo["languages"]["edges"]:
            langs[edge["node"]["name"]] = langs.get(edge["node"]["name"], 0) + edge["size"]
    return {
        "total": cal["totalContributions"],
        "days": days,
        "repos": user["repositories"]["totalCount"],
        "stars": sum(r["stargazerCount"] for r in user["repositories"]["nodes"]),
        "followers": user["followers"]["totalCount"],
        "langs": langs,
    }


def sample():
    rnd = random.Random(1)
    today = dt.date.today()
    start = today - dt.timedelta(days=364 + (today.weekday() + 1) % 7)
    days = [((start + dt.timedelta(d)).isoformat(), rnd.choice([0, 0, 0, 1, 2, 4, 9])) for d in range((today - start).days + 1)]
    return {"total": sum(c for _, c in days), "days": days, "repos": 6, "stars": 3, "followers": 2,
            "langs": {"Python": 90000, "Shell": 60000, "C": 50000, "Lua": 30000, "QML": 20000, "HTML": 9000}}


def streak(days):
    count, items = 0, list(days)
    if items and items[-1][1] == 0:  # today may still be empty
        items = items[:-1]
    for _, c in reversed(items):
        if c == 0:
            break
        count += 1
    return count


def level(count, peak):
    if count == 0:
        return 0
    return min(4, 1 + int(3 * count / max(peak, 1)))


def draw(stats):
    uid, w, h = "st", 1200, 560
    body = [defs(uid, w, h), background(uid, w, h, stars=55, seed=5)]
    body.append(text("❯ ", 14, 46, 13, GREEN))
    body.append(text("gh api user --stats", 30, 46, 13, DIM))
    body.append(text("STATS", 28, 84, 34, f"url(#{uid}-title)", MONO_XBOLD, spacing=6))
    body.append(text(f"updated {dt.date.today().isoformat()} · GitHub Actions", w - 30, 82, 12, DIM, anchor="end"))

    tiles = [("contributions", stats["total"], "last 12 months", CYAN), ("streak", streak(stats["days"]), "days in a row", MAGENTA),
             ("repositories", stats["repos"], "public, not forks", CYAN), ("stars", stats["stars"], "on my repos", MAGENTA)]
    tw = (w - 56 - 3 * 18) / 4
    for i, (label, value, sub, colour) in enumerate(tiles):
        x = 28 + i * (tw + 18)
        body.append(f'<rect x="{x:.1f}" y="104" width="{tw:.1f}" height="104" rx="14" fill="{CARD}" fill-opacity=".72" stroke="{colour}" stroke-opacity=".3"/>')
        body.append(f'<g filter="url(#{uid}-soft)">{text(str(value), x + tw / 2, 162, 40, colour, DISPLAY, anchor="middle")}</g>')
        body.append(text(label.upper(), x + tw / 2, 186, 11, TEXT, MONO_XBOLD, anchor="middle", spacing=1.6))
        body.append(text(sub, x + tw / 2, 200, 10, DIM, anchor="middle"))

    # contribution heatmap, one column per week
    days = stats["days"][-371:]
    peak = sorted(c for _, c in days)[int(len(days) * 0.95)] if days else 1
    first = dt.date.fromisoformat(days[0][0]) if days else dt.date.today()
    offset = (first.weekday() + 1) % 7  # GitHub weeks start on Sunday
    cell, gap = 15, 4
    weeks = (len(days) + offset + 6) // 7
    gx = (w - (weeks * (cell + gap) - gap)) / 2
    gy = 240
    body.append(f'<rect x="28" y="226" width="{w - 56}" height="196" rx="14" fill="{CARD}" fill-opacity=".72" stroke="{CYAN}" stroke-opacity=".2"/>')
    for i, (date, count) in enumerate(days):
        col, row = divmod(i + offset, 7)
        lv = level(count, peak)
        x, y = gx + col * (cell + gap), gy + 14 + row * (cell + gap)
        cls = f' filter="url(#{uid}-soft)"' if lv == 4 else ""
        body.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell}" height="{cell}" rx="4" fill="{LEVELS[lv]}"{cls}/>')
    lx = w - 48 - 5 * 19 - text_width("more", 10)
    body.append(text("less", lx - 8, 410, 10, DIM, anchor="end"))
    for i, colour in enumerate(LEVELS):
        body.append(f'<rect x="{lx + i * 19:.1f}" y="399" width="13" height="13" rx="3" fill="{colour}"/>')
    body.append(text("more", lx + 5 * 19, 410, 10, DIM))
    body.append(text("contributions, last 12 months", 48, 410, 10, DIM))

    # languages
    langs = sorted(stats["langs"].items(), key=lambda kv: -kv[1])
    top, rest = langs[:6], sum(v for _, v in langs[6:])
    if rest:
        top.append(("other", rest))
    total = sum(v for _, v in top) or 1
    body.append(text("LANGUAGES", 28, 458, 13, MAGENTA, MONO_XBOLD, spacing=2.2))
    bx, bw = 28, w - 56
    body.append(f'<clipPath id="{uid}-bar"><rect x="{bx}" y="470" width="{bw}" height="12" rx="6"/></clipPath><g clip-path="url(#{uid}-bar)">')
    x = bx
    for i, (name, size) in enumerate(top):
        part = bw * size / total
        body.append(f'<rect x="{x:.1f}" y="470" width="{part + 1:.1f}" height="12" fill="{LANG_COLOURS[i % len(LANG_COLOURS)]}"/>')
        x += part
    body.append("</g>")
    x = bx
    for i, (name, size) in enumerate(top):
        colour = LANG_COLOURS[i % len(LANG_COLOURS)]
        label = f"{name} {100 * size / total:.0f}%"
        body.append(f'<circle cx="{x + 5}" cy="{510}" r="5" fill="{colour}"/>')
        body.append(text(label, x + 16, 514, 12, TEXT, MONO))
        x += text_width(label, 12) + 40

    body.append(frame(uid, w, h))
    return svg(w, h, "".join(body), "GitHub stats of PoUrRiTuRe")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--sample":
        with open(sys.argv[2], "w") as f:
            f.write(draw(sample()))
        print(f"wrote {sys.argv[2]} (sample data)")
    else:
        write("stats.svg", draw(fetch()))
