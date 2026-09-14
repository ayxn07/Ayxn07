import json
import math
import os
import sys
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from svgtext import ANTON, INK, MONO, MONO_B, TEAL, baseline, document, panel, write

TOKEN = os.environ["GITHUB_TOKEN"]
LOGIN = os.environ.get("USERNAME") or sys.argv[1]

PROFILE = """query($login:String!,$cursor:String){user(login:$login){
  followers{totalCount} pullRequests{totalCount} contributionsCollection{contributionYears}
  repositories(ownerAffiliations:OWNER,isFork:false,privacy:PUBLIC,first:100,after:$cursor){
    totalCount pageInfo{hasNextPage endCursor}
    nodes{stargazerCount languages(first:10,orderBy:{field:SIZE,direction:DESC}){edges{size node{name}}}}}}}"""

YEAR = """query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){
  contributionsCollection(from:$from,to:$to){totalCommitContributions
    contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def gql(query, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        json.dumps({"query": query, "variables": variables}).encode(),
        {"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        data = json.load(r)
    if data.get("errors"):
        raise SystemExit(json.dumps(data["errors"], indent=2))
    return data["data"]["user"]


def collect():
    repos, cursor = [], None
    while True:
        user = gql(PROFILE, {"login": LOGIN, "cursor": cursor})
        repos += user["repositories"]["nodes"]
        page = user["repositories"]["pageInfo"]
        if not page["hasNextPage"]:
            break
        cursor = page["endCursor"]

    now = datetime.now(timezone.utc)
    days, commits, total = {}, 0, 0
    for year in sorted(user["contributionsCollection"]["contributionYears"]):
        start = datetime(year, 1, 1, tzinfo=timezone.utc)
        end = min(datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc), now)
        c = gql(YEAR, {"login": LOGIN, "from": start.isoformat(), "to": end.isoformat()})["contributionsCollection"]
        commits += c["totalCommitContributions"]
        total += c["contributionCalendar"]["totalContributions"]
        for week in c["contributionCalendar"]["weeks"]:
            for d in week["contributionDays"]:
                days[d["date"]] = d["contributionCount"]

    langs = defaultdict(int)
    for r in repos:
        for e in r["languages"]["edges"]:
            langs[e["node"]["name"]] += e["size"]

    return {
        "total": total,
        "commits": commits,
        "stars": sum(r["stargazerCount"] for r in repos),
        "prs": user["pullRequests"]["totalCount"],
        "repos": user["repositories"]["totalCount"],
        "followers": user["followers"]["totalCount"],
        "days": days,
        "langs": langs,
        "since": min(days) if days else None,
    }


def streaks(days):
    today = datetime.now(timezone.utc).date()
    ordered = sorted((date.fromisoformat(k), v) for k, v in days.items() if date.fromisoformat(k) <= today)
    best, run, run_start = (0, None, None), 0, None
    for d, v in ordered:
        if v:
            run_start = d if run == 0 else run_start
            run += 1
            if run > best[0]:
                best = (run, run_start, d)
        else:
            run = 0
    # an empty today does not break the streak yet
    cursor = today if days.get(today.isoformat(), 0) else today - timedelta(days=1)
    end, current, start = cursor, 0, None
    while days.get(cursor.isoformat(), 0) > 0:
        current, start = current + 1, cursor
        cursor -= timedelta(days=1)
    return (current, start, end), best


def span(start, end):
    if not start:
        return "no active streak"
    this_year = datetime.now(timezone.utc).year
    fmt = lambda d: d.strftime("%b %d").replace(" 0", " ")
    suffix = "" if end.year == this_year else f" '{end.year % 100:02d}"
    return f"{fmt(start)} - {fmt(end)}{suffix}"


def stats_svg(s):
    W, H, pad = 1200, 372, 48
    (cur, cur_start, cur_end), (best, best_start, best_end) = streaks(s["days"])
    updated = datetime.now(timezone.utc).strftime("%b %d, %Y").upper()
    body = [
        panel(W, H),
        MONO_B.path("LIVE FROM THE GITHUB API", 13, pad, 56, tracking=3),
        MONO_B.path(f"UPDATED {updated}", 13, W - pad, 56, anchor="end", tracking=2),
        f'<rect x="{pad}" y="74" width="{W - pad * 2}" height="2" fill="{INK}"/>',
    ]
    tiles = [
        ("CONTRIBUTIONS", s["total"]), ("COMMITS", s["commits"]), ("STARS EARNED", s["stars"]),
        ("PULL REQUESTS", s["prs"]), ("PUBLIC REPOS", s["repos"]), ("FOLLOWERS", s["followers"]),
    ]
    col_w = 236
    for k, (label, value) in enumerate(tiles):
        r, c = divmod(k, 3)
        x, y = pad + c * col_w, 100 + r * 130
        if c:
            body.append(f'<rect x="{x - 18}" y="{y}" width="1.5" height="104" fill="{INK}" opacity=".35"/>')
        body += [
            "<g>",
            ANTON.path(f"{value:,}", ANTON.fit(f"{value:,}", col_w - 40, 64), x, y + 66),
            MONO_B.path(label, 12, x, y + 96, tracking=2),
            "</g>",
        ]

    bx, by, bw, bh = 792, 100, W - pad - 792, 234
    cx, cy, radius = bx + 104, by + bh / 2, 72
    circ = 2 * math.pi * radius
    frac = 1 if best == 0 else max(cur / best, 0.04 if cur else 0)
    body += [
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="16" fill="{INK}"/>',
        f'<circle cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{TEAL}" stroke-opacity=".22" stroke-width="12"/>',
        f'<circle class="ring" cx="{cx}" cy="{cy}" r="{radius}" fill="none" stroke="{TEAL}" stroke-width="12" '
        f'stroke-linecap="round" stroke-dasharray="{circ * frac:.1f} {circ:.1f}" transform="rotate(-90 {cx} {cy})"/>',
    ]
    size = ANTON.fit(str(cur), 90, 64)
    body.append(ANTON.path(str(cur), size, cx, baseline(ANTON, size, cy), fill=TEAL, anchor="middle"))
    tx = cx + radius + 32
    body += [
        MONO_B.path("CURRENT STREAK", 12, tx, by + 56, fill=TEAL, tracking=1.5),
        MONO.path(span(cur_start, cur_end), 12, tx, by + 78, fill=TEAL),
        f'<rect x="{tx}" y="{by + 100}" width="{bx + bw - 24 - tx}" height="1.5" fill="{TEAL}" opacity=".4"/>',
        MONO_B.path("LONGEST STREAK", 12, tx, by + 132, fill=TEAL, tracking=1.5),
        ANTON.path(f"{best} DAYS", 36, tx, by + 176, fill=TEAL),
        MONO.path(span(best_start, best_end), 12, tx, by + 200, fill=TEAL),
    ]
    css = ""
    label = f"{s['total']:,} contributions, {s['commits']:,} commits, {s['stars']} stars, current streak {cur} days, longest {best} days"
    write("assets/generated/stats.svg", document(W, H, "".join(body), css, label))


def languages_svg(langs):
    W, H, pad = 1200, 250, 48
    top = sorted(langs.items(), key=lambda kv: -kv[1])[:6]
    total = sum(v for _, v in top) or 1
    shades = [1, 0.78, 0.6, 0.45, 0.32, 0.2]
    body = [
        panel(W, H),
        MONO_B.path("LANGUAGES BY CODE SIZE", 13, pad, 56, tracking=3),
        MONO_B.path("OWNED REPOS / FORKS EXCLUDED", 13, W - pad, 56, anchor="end", tracking=2),
        f'<defs><clipPath id="bar"><rect x="{pad}" y="80" width="{W - pad * 2}" height="36" rx="10"/></clipPath></defs>',
        '<g clip-path="url(#bar)"><g class="grow">',
    ]
    x, bar_w = pad, W - pad * 2
    for (name, size), shade in zip(top, shades):
        w = bar_w * size / total
        body.append(f'<rect x="{x:.1f}" y="80" width="{max(w - 3, 1):.1f}" height="36" fill="{INK}" opacity="{shade}"/>')
        x += w
    body.append("</g></g>")
    col_w = (W - pad * 2) / 3
    for k, ((name, size), shade) in enumerate(zip(top, shades)):
        r, c = divmod(k, 3)
        lx, ly = pad + c * col_w, 158 + r * 40
        body += [
            f'<rect x="{lx:.1f}" y="{ly - 14}" width="16" height="16" rx="4" fill="{INK}" opacity="{shade}"/>',
            MONO_B.path(name, 15, lx + 28, ly),
            MONO.path(f"{size / total * 100:.1f}%", 15, lx + col_w - 36, ly, anchor="end"),
        ]
    css = ""
    label = "Top languages: " + ", ".join(f"{n} {v / total * 100:.0f}%" for n, v in top)
    write("assets/generated/languages.svg", document(W, H, "".join(body), css, label))


stats = collect()
stats_svg(stats)
languages_svg(stats["langs"])
