import math
import textwrap

from svgtext import ANTON, INK, MONO, MONO_B, TEAL, baseline, brand, document, icon, legible, panel, write

BLINK = "@keyframes blink{50%{opacity:0}}.blink{animation:blink 1s steps(1) infinite}"
NUDGE = "@keyframes nudge{50%{transform:translateX(5px)}}.nudge{animation:nudge 1.4s ease-in-out infinite}"


def typing():
    W, H, size, x0, base = 1200, 130, 34, 48, 82
    lines = [
        "building AI agents & MCP servers",
        "shipping Next.js apps to the edge",
        "rendering 3D worlds in Three.js",
        "pushing Flutter & Expo apps to stores",
    ]
    period, slot = 3.6 * len(lines), 100 / len(lines)
    tx = x0 + MONO_B.width("> ", size)
    css, body = [BLINK], [panel(W, H), MONO_B.path(">", size, x0, base)]
    for i, line in enumerate(lines):
        w = MONO_B.width(line, size)
        a, b = i * slot, (i + 1) * slot
        before = f"0%,{a - 0.01:.2f}%{{opacity:0}}" if i else ""
        css.append(
            f"@keyframes v{i}{{{before}{a:.2f}%,{b - 0.01:.2f}%{{opacity:1}}{b:.2f}%,100%{{opacity:0}}}}"
            f".v{i}{{animation:v{i} {period:.1f}s linear infinite}}"
            f"@keyframes r{i}{{0%,{a:.2f}%{{transform:translateX(0)}}{a + slot * 0.45:.2f}%,100%{{transform:translateX({w:.1f}px)}}}}"
            f".r{i}{{animation:r{i} {period:.1f}s steps({len(line)},end) infinite}}"
        )
        # a teal cover slides right one character at a time, dragging the cursor with it
        # attribute defaults are the no-animation fallback: first line fully typed, the rest hidden
        hidden = ' opacity="0"' if i else ""
        shift = f'transform="translate({w:.1f} 0)"'
        body.append(
            f'<g class="v{i}"{hidden}>{MONO_B.path(line, size, tx, base)}'
            f'<rect class="r{i}" {shift} x="{tx - 2:.1f}" y="{base - size:.1f}" width="{w + 60:.1f}" height="{size * 1.4:.1f}" fill="{TEAL}"/>'
            f'<g class="r{i}" {shift}><rect class="blink" x="{tx + 2:.1f}" y="{base - size * 0.78:.1f}" '
            f'width="{size * 0.5:.1f}" height="{size * 0.95:.1f}" fill="{INK}"/></g></g>'
        )
    status = "STATUS: BUILDING"
    pw = MONO_B.width(status, 13) + 48
    px = W - 48 - pw
    body += [
        f'<rect x="{px:.1f}" y="22" width="{pw:.1f}" height="34" rx="17" fill="{INK}"/>',
        f'<circle class="blink" cx="{px + 20:.1f}" cy="39" r="5" fill="{TEAL}"/>',
        MONO_B.path(status, 13, px + 34, baseline(MONO_B, 13, 39), fill=TEAL),
        MONO.path("DUBAI, UAE", 15, W - 48, 88, anchor="end"),
        MONO.path("CS / AI & BIG DATA @ UOWD", 15, W - 48, 110, anchor="end"),
    ]
    write("assets/typing.svg", document(W, H, "".join(body), "".join(css), "> building AI agents & MCP servers"))


def chip(name, label, num=None, logo=None, out=False):
    W, H = 240, 68
    body, lx = [panel(W, H, 14)], 22
    if num:
        body += [
            f'<rect x="8" y="8" width="54" height="52" rx="10" fill="{INK}"/>',
            ANTON.path(num, 28, 35, baseline(ANTON, 28, 34), fill=TEAL, anchor="middle"),
        ]
        lx = 76
    elif logo:
        body.append(icon(logo, 22, 21, 26))
        lx = 62
    size = ANTON.fit(label, W - lx - 50, 30)
    body.append(ANTON.path(label, size, lx, baseline(ANTON, size, 34)))
    ax = W - 30
    if out:
        d, move = f"M{ax - 7} 41l14-14m-10 0h10v10", "translate(2px,-2px)"
    else:
        d, move = f"M{ax} 25v18m-7-7l7 7 7-7", "translateY(3px)"
    body.append(f'<path class="bob" d="{d}" fill="none" stroke="{INK}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>')
    css = f"@keyframes bob{{50%{{transform:{move}}}}}.bob{{animation:bob 1.6s ease-in-out infinite}}"
    write(f"assets/{name}.svg", document(W, H, "".join(body), css, label))


def section(slug, num, title, note):
    W, H, size = 1200, 100, 60
    y = baseline(ANTON, size, H / 2)
    tw = ANTON.width(title, size)
    cap = ANTON.cap * size
    body = [
        panel(W, H),
        f'<rect x="10" y="10" width="112" height="80" rx="12" fill="{INK}"/>',
        ANTON.path(num, 50, 66, baseline(ANTON, 50, H / 2), fill=TEAL, anchor="middle"),
        ANTON.path(title, size, 150, y),
        f'<rect class="blink" x="{150 + tw + 14:.1f}" y="{y - cap:.1f}" width="16" height="{cap:.1f}" fill="{INK}"/>',
        MONO.path(note, 17, W - 40, baseline(MONO, 17, H / 2), anchor="end"),
    ]
    write(f"assets/section-{slug}.svg", document(W, H, "".join(body), BLINK, f"{num} {title}"))


def whoami():
    W, pad = 1200, 48
    left, right = [], []

    left.append(MONO_B.path("WHOAMI.EXE", 13, pad, 64, tracking=3))
    y = 64
    for word in ("FULL-STACK", "DEVELOPER"):
        s = ANTON.fit(word, 520, 130)
        y += 22 + ANTON.cap * s
        left.append(ANTON.path(word, s, pad, y))
    y += 20
    left.append(f'<rect x="{pad}" y="{y:.1f}" width="80" height="8" fill="{INK}"/>')
    y += 24
    bio = (
        "CS student at the University of Wollongong in Dubai, majoring in AI & Big Data. "
        "I build the whole thing - pixels, APIs, agents and the edge. If a task can be automated, it will be."
    )
    for line in textwrap.wrap(bio, 46):
        y += 30
        left.append(MONO.path(line, 17, pad, y))
    left_end = y

    rows = [
        ("BASED IN", ["Dubai, UAE"]),
        ("STUDYING", ["Computer Science - AI & Big Data", "University of Wollongong in Dubai"]),
        ("BUILDING", [
            "Ayxn Studio - free AI image & video studio",
            "AI agents + MCP servers wired into real tools",
            "Portfolio OS - a macOS desktop in the browser",
        ]),
        ("SHIPS WITH", ["Next.js / React / TypeScript / Three.js", "Flutter / Expo / Node.js / Supabase / Python"]),
        ("CERTIFIED", ["Full-Stack Development", "Flutter App Development"]),
        ("MOTTO", ['"If I have to do it twice, I build a tool."']),
    ]
    rx, y = 640, 40
    for label, values in rows:
        right.append(f'<rect x="{rx}" y="{y}" width="{W - pad - rx}" height="2" fill="{INK}"/>')
        right.append(MONO_B.path(label, 12, rx, y + 28, tracking=2.5))
        vy = y + 28
        for v in values:
            assert MONO.width(v, 17) <= W - pad - rx, v
            vy += 27
            right.append(MONO.path(v, 17, rx, vy))
        y = vy + 22
    H = int(max(left_end + 120, y + 26))

    prompt = "> ayxn07@github:~$ whoami"
    bw = MONO_B.width(prompt, 15) + 64
    by = H - pad - 52
    left += [
        f'<rect x="{pad}" y="{by}" width="{bw:.1f}" height="52" rx="10" fill="{INK}"/>',
        MONO_B.path(prompt, 15, pad + 22, baseline(MONO_B, 15, by + 26), fill=TEAL),
        f'<rect class="blink" x="{pad + 22 + MONO_B.width(prompt, 15) + 8:.1f}" y="{by + 16}" width="10" height="20" fill="{TEAL}"/>',
    ]
    label = "Full-stack developer. CS student at UOWD, AI & Big Data. Based in Dubai. Building Ayxn Studio, AI agents, MCP servers and Portfolio OS."
    write("assets/whoami.svg", document(W, H, panel(W, H) + "".join(left + right), BLINK, label))


def card_icon(kind):
    if kind == "studio":
        css = "@keyframes flow{to{stroke-dashoffset:-8}}.flow{stroke-dasharray:4 4;animation:flow .8s linear infinite}"
        svg = (
            f'<g transform="translate(314 54)">'
            f'<path class="flow" d="M24 12C40 12 40 32 56 32M24 52C40 52 40 32 56 32" fill="none" stroke="{INK}" stroke-width="2.4"/>'
            f'<rect x="1" y="4" width="23" height="16" rx="4" fill="{TEAL}" stroke="{INK}" stroke-width="2.4"/>'
            f'<rect x="1" y="44" width="23" height="16" rx="4" fill="{TEAL}" stroke="{INK}" stroke-width="2.4"/>'
            f'<rect x="56" y="20" width="26" height="24" rx="5" fill="{INK}"/>'
            f'<circle class="blink" cx="69" cy="32" r="4" fill="{TEAL}"/></g>'
        )
    elif kind == "sound":
        css = "@keyframes eq{0%,100%{transform:scaleY(.25)}50%{transform:scaleY(1)}}.bar{transform-box:fill-box;transform-origin:50% 100%;animation:eq 1.1s ease-in-out infinite}"
        svg = "".join(
            f'<rect class="bar" style="animation-delay:-{i * 0.17:.2f}s" x="{324 + i * 10}" y="52" width="6" height="62" rx="2" fill="{INK}"/>'
            for i in range(7)
        )
    elif kind == "face":
        css = "@keyframes scan{0%,100%{transform:translateY(4px)}50%{transform:translateY(58px)}}.scan{animation:scan 2.4s ease-in-out infinite}"
        svg = (
            f'<g transform="translate(330 52)" fill="none" stroke="{INK}" stroke-width="2.4">'
            f'<path d="M0 14V0H14M50 0H64V14M0 50V64H14M50 64H64V50"/>'
            f'<circle cx="32" cy="29" r="14"/><path d="M26 34Q32 39 38 34M17 52Q32 42 47 52"/>'
            f'<circle cx="27" cy="26" r="1.6" fill="{INK}"/><circle cx="37" cy="26" r="1.6" fill="{INK}"/>'
            f'<rect class="scan" x="4" y="0" width="56" height="2.5" fill="{INK}" stroke="none"/></g>'
        )
    else:
        css = ""
        svg = (
            f'<g transform="translate(316 54)">'
            f'<rect width="80" height="58" rx="7" fill="{INK}"/>'
            + "".join(f'<circle cx="{10 + k * 9}" cy="9" r="2.6" fill="{TEAL}"/>' for k in range(3))
            + f'<rect y="17" width="80" height="1.5" fill="{TEAL}" opacity=".5"/>'
            + MONO_B.path("> boot", 10, 9, 38, fill=TEAL)
            + f'<rect class="blink" x="{9 + MONO_B.width("> boot ", 10):.1f}" y="29" width="6" height="11" fill="{TEAL}"/>'
            + f'<rect x="14" y="46" width="52" height="5" rx="2.5" fill="{TEAL}" opacity=".6"/></g>'
        )
    return css, svg


def card(slug, idx, title, status, desc, tags, link, kind):
    W, H = 420, 290
    lines = textwrap.wrap(desc, 44)
    assert len(lines) <= 3, f"{slug}: description needs {len(lines)} lines"
    icon_css, icon_svg = card_icon(kind)
    body = [
        f'<defs><clipPath id="c"><rect width="{W}" height="{H}" rx="18"/></clipPath></defs>',
        f'<g clip-path="url(#c)">{panel(W, H, 0)}<rect y="{H - 48}" width="{W}" height="48" fill="{INK}"/></g>',
        MONO_B.path(f"PROJECT_0{idx}", 11, 24, 38, tracking=2.5),
    ]
    sw = MONO_B.width(status, 11, 1.5) + 40
    sx = W - 24 - sw
    body += [
        f'<rect x="{sx:.1f}" y="20" width="{sw:.1f}" height="26" rx="13" fill="{INK}"/>',
        f'<circle class="blink" cx="{sx + 15:.1f}" cy="33" r="4" fill="{TEAL}"/>',
        MONO_B.path(status, 11, sx + 27, baseline(MONO_B, 11, 33), fill=TEAL, tracking=1.5),
    ]
    size = ANTON.fit(title, 270, 46)
    body += [ANTON.path(title, size, 24, 102), f'<rect x="24" y="116" width="56" height="6" fill="{INK}"/>']
    body += [MONO.path(line, 13, 24, 148 + i * 20) for i, line in enumerate(lines)]
    x = 24
    for t in tags:
        w = MONO_B.width(t, 11) + 22
        body += [
            f'<rect x="{x:.1f}" y="208" width="{w:.1f}" height="24" rx="12" fill="none" stroke="{INK}" stroke-width="1.8"/>',
            MONO_B.path(t, 11, x + w / 2, baseline(MONO_B, 11, 220), anchor="middle"),
        ]
        x += w + 8
    assert x - 8 <= W - 24, f"{slug}: tags overflow"
    body += [
        f'<g class="nudge">{MONO_B.path("-> " + link, 13, 24, baseline(MONO_B, 13, H - 24), fill=TEAL)}</g>',
        ANTON.path("OPEN", 20, W - 24, baseline(ANTON, 20, H - 24), fill=TEAL, anchor="end"),
        icon_svg,
    ]
    write(f"assets/card-{slug}.svg", document(W, H, "".join(body), BLINK + NUDGE + icon_css, f"{title}: {desc}"))


def stack(slug, name, items):
    W, LW, pitch, row_h = 1200, 250, 100, 112
    per_row = (W - LW - 40) // pitch
    rows = math.ceil(len(items) / per_row)
    H = 34 + rows * row_h + 10
    size = ANTON.fit(name, LW - 64, 36)
    body = [
        panel(W, H),
        f'<rect x="10" y="10" width="{LW - 20}" height="{H - 20}" rx="12" fill="{INK}"/>',
        ANTON.path(name, size, 34, H / 2 + 2, fill=TEAL),
        MONO_B.path(f"{len(items):02d} TOOLS", 12, 34, H / 2 + 28, fill=TEAL, tracking=2),
    ]
    for k, (logo, label) in enumerate(items):
        r, c = divmod(k, per_row)
        tx, ty = LW + 20 + c * pitch, 30 + r * row_h
        assert MONO_B.width(label, 11) <= pitch - 6, label
        body.append(
            f'<g><rect x="{tx + 18}" y="{ty}" width="64" height="64" rx="14" fill="{INK}"/>'
            f"{icon(logo, tx + 33, ty + 15, 34, fill=legible(brand(logo)))}"
            f"{MONO_B.path(label, 11, tx + 50, ty + 86, anchor='middle')}</g>"
        )
    css = ""
    write(f"assets/stack-{slug}.svg", document(W, H, "".join(body), css, f"{name}: " + ", ".join(l for _, l in items)))


def footer():
    W, H, pad = 1200, 290, 48
    title = "LET'S BUILD SOMETHING"
    size = ANTON.fit(title, W - pad * 2 - 40, 150)
    y = 64 + 26 + ANTON.cap * size
    tw = ANTON.width(title, size)
    line_y = y + 28
    ty = line_y + 44
    body = [
        panel(W, H),
        MONO_B.path("END OF TRANSMISSION", 13, pad, 64, tracking=3),
        ANTON.path(title, size, pad, y),
        f'<rect class="blink" x="{pad + tw + 14:.1f}" y="{y - ANTON.cap * size:.1f}" width="22" height="{ANTON.cap * size:.1f}" fill="{INK}"/>',
        f'<rect x="{pad}" y="{line_y:.1f}" width="{W - pad * 2}" height="2" fill="{INK}"/>',
        MONO.path("ayxn07dev@gmail.com", 17, pad, ty),
        MONO.path("portfolio.ayxn07.com", 17, W / 2, ty, anchor="middle"),
        MONO.path("Dubai, UAE", 17, W - pad, ty, anchor="end"),
    ]
    write("assets/footer.svg", document(W, int(ty + 40), "".join(body).replace(panel(W, H), panel(W, int(ty + 40))), BLINK, "Let's build something - ayxn07dev@gmail.com"))


typing()

for n, (num, label) in enumerate([("01", "WHOAMI"), ("02", "PROJECTS"), ("03", "STACK"), ("04", "STATS"), ("05", "SNAKE")]):
    chip(f"nav-{label.lower()}", label, num=num)

chip("link-portfolio", "PORTFOLIO", out=True)
chip("link-linkedin", "LINKEDIN", logo="linkedin", out=True)
chip("link-x", "X / TWITTER", logo="x", out=True)
chip("link-instagram", "INSTAGRAM", logo="instagram", out=True)
chip("link-email", "EMAIL", logo="gmail", out=True)

section("whoami", "01", "WHOAMI", "// the human behind the commits")
section("projects", "02", "PROJECTS", "// things i shipped")
section("stack", "03", "STACK", "// tools of the trade")
section("stats", "04", "STATS", "// live from the github api, refreshed daily")
section("snake", "05", "SNAKE", "// it eats my contribution graph")
section("connect", "06", "CONNECT", "// say hi")

whoami()

card("ayxn-studio", 1, "AYXN STUDIO", "LIVE",
     "Free AI image and video generation studio with a node-based flow editor built entirely from scratch.",
     ["Next.js 16", "Supabase", "React Flow", "Three.js"], "studio.ayxn07.com", "studio")
card("soundify", 2, "SOUNDIFY", "FLUTTER",
     "Spotify-style music streaming app in Flutter with BLoC state management and a clean, scalable architecture.",
     ["Flutter", "Dart", "BLoC", "Cross-platform"], "github.com/ayxn07/soundify", "sound")
card("faceattend", 3, "FACEATTEND", "PYTHON",
     "Touchless attendance system: computer vision detects and identifies faces over webcam and logs every timestamp.",
     ["Python", "Computer Vision", "CustomTkinter"], "github.com/ayxn07/FaceAttend-System", "face")
card("portfolio-os", 4, "PORTFOLIO OS", "ONLINE",
     "A macOS-style desktop that runs in the browser - windows, dock and apps. My portfolio, but it boots.",
     ["JavaScript", "Desktop UI", "Live site"], "ayxn07.com", "os")

stack("languages", "LANGUAGES", [
    ("typescript", "TypeScript"), ("javascript", "JavaScript"), ("python", "Python"), ("dart", "Dart"),
    ("kotlin", "Kotlin"), ("html5", "HTML5"), ("css", "CSS"),
])
stack("frontend", "FRONTEND", [
    ("react", "React"), ("nextdotjs", "Next.js"), ("vite", "Vite"), ("tailwindcss", "Tailwind"),
    ("threedotjs", "Three.js"), ("mui", "MUI"), ("bootstrap", "Bootstrap"), ("daisyui", "DaisyUI"),
    ("chakraui", "Chakra UI"), ("chartdotjs", "Chart.js"), ("reactrouter", "React Router"),
])
stack("mobile", "MOBILE", [
    ("flutter", "Flutter"), ("expo", "Expo"), ("react", "React Native"), ("kotlin", "Kotlin"),
])
stack("backend", "BACKEND & DATA", [
    ("nodedotjs", "Node.js"), ("express", "Express"), ("supabase", "Supabase"), ("firebase", "Firebase"),
    ("mongodb", "MongoDB"), ("mysql", "MySQL"),
])
stack("cloud", "CLOUD & TOOLS", [
    ("cloudflare", "Cloudflare"), ("amazonwebservices", "AWS"), ("netlify", "Netlify"),
    ("wordpress", "WordPress"), ("git", "Git"), ("github", "GitHub"),
])
stack("design", "DESIGN & MOTION", [
    ("figma", "Figma"), ("blender", "Blender"), ("adobeaftereffects", "After Effects"),
    ("adobepremierepro", "Premiere Pro"), ("adobephotoshop", "Photoshop"), ("adobeillustrator", "Illustrator"),
    ("canva", "Canva"),
])

footer()
