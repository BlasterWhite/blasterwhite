#!/usr/bin/env python3
"""Builds the static README visuals in profile/. Text is outlined, so the SVGs
look the same everywhere. Needs fontTools plus the Poppins and Noto Sans CJK fonts."""
import json, math, pathlib, subprocess
from fontTools.ttLib import TTFont, TTCollection
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "profile"
ICONS = json.loads((ROOT / "scripts/icons.json").read_text())

INK, WHITE, MIST = "#0B1A2B", "#FFFFFF", "#C4D2E0"
RED, GREEN, BLUE = "#F2404A", "#2BD540", "#19B4E8"
SQUARE = "#16304A"

def font_file(pattern):
    return subprocess.check_output(["fc-match", "-f", "%{file}", pattern], text=True)

class Face:
    def __init__(self, pattern, index=None):
        path = font_file(pattern)
        self.f = TTCollection(path).fonts[index] if path.endswith(".ttc") else TTFont(path)
        self.gs, self.cmap = self.f.getGlyphSet(), self.f.getBestCmap()
        self.upm = self.f["head"].unitsPerEm
        self.cap = getattr(self.f["OS/2"], "sCapHeight", 0) or self.upm * .7
    def adv(self, ch, size):
        return self.gs[self.cmap[ord(ch)]].width * size / self.upm
    def width(self, text, size, track=0):
        return sum(self.adv(c, size) + track for c in text) - track
    def glyph(self, ch, size, x=0, y=0):
        pen = SVGPathPen(self.gs, ntos=lambda v: f"{v:.1f}".rstrip("0").rstrip("."))
        k = size / self.upm
        self.gs[self.cmap[ord(ch)]].draw(TransformPen(pen, (k, 0, 0, -k, x, y)))
        return pen.getCommands()
    def text(self, text, size, x, y, track=0):
        out = []
        for c in text:
            out.append(self.glyph(c, size, x, y))
            x += self.adv(c, size) + track
        return "".join(out)

BOLD = Face("Poppins:style=Bold")
SEMI = Face("Poppins:style=Medium")
REG = Face("Poppins:style=Regular")
JP = Face("Noto Sans CJK JP:style=Bold", 0)
for i, fnt in enumerate(TTCollection(font_file("Noto Sans CJK JP:style=Bold")).fonts):
    if "Sans CJK JP" in fnt["name"].getDebugName(1):
        JP = Face("Noto Sans CJK JP:style=Bold", i); break

def wave(y0, amp, lam, phase):
    return lambda x: y0 + amp * math.sin(2 * math.pi * x / lam + phase)
def slope(f, x):
    return math.degrees(math.atan2(f(x + 1) - f(x - 1), 2))
def ribbon_d(f, w):
    return "M" + "L".join(f"{x} {f(x):.1f}" for x in range(-30, w + 31, 6))

def riding(face, text, size, x, f, fill, track=0):
    """Sets each glyph on the wave, tilted to follow its slope."""
    parts = []
    mid = face.cap * size / face.upm / 2
    for c in text:
        a = face.adv(c, size)
        if c != " ":
            cx = x + a / 2
            parts.append(f'<path transform="translate({cx:.1f} {f(cx):.1f}) rotate({slope(f, cx):.1f})" '
                         f'd="{face.glyph(c, size, -a / 2, mid)}"/>')
        x += a + track
    return f'<g fill="{fill}">{"".join(parts)}</g>'

def svg(name, w, h, label, body, style=""):
    motion = f"<style>{style}@media (prefers-reduced-motion: reduce){{*{{animation:none!important;opacity:1!important;stroke-dashoffset:0!important}}}}</style>" if style else ""
    doc = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{label}">'
           f'{motion}<defs><clipPath id="c"><rect width="{w}" height="{h}" rx="14"/></clipPath></defs>'
           f'<g clip-path="url(#c)"><rect width="{w}" height="{h}" fill="{INK}"/>{body}</g></svg>\n')
    (OUT / name).write_text(doc)

def hero():
    W, H, T = 840, 300, 74
    lines = [(wave(64, 15, 470, .3), RED, BOLD, "Matéo Guézennec", 46, INK),
             (wave(150, 15, 470, 1.5), GREEN, BOLD, "Fullstack developer", 31, INK),
             (wave(236, 15, 470, 2.7), BLUE, BOLD, "Brittany, France", 31, INK)]
    body, css = "", (".r{fill:none;stroke-dasharray:1;stroke-dashoffset:1;animation:d 1.3s cubic-bezier(.6,0,.2,1) forwards}"
                     ".t{opacity:0;animation:f .5s ease-out forwards}"
                     "@keyframes d{to{stroke-dashoffset:0}}@keyframes f{to{opacity:1}}")
    for i, (f, col, face, text, size, ink) in enumerate(lines):
        body += (f'<path class="r" pathLength="1" d="{ribbon_d(f, W)}" stroke="{col}" stroke-width="{T}" '
                 f'style="animation-delay:{i * .16:.2f}s"/>')
        body += f'<g class="t" style="animation-delay:{.65 + i * .16:.2f}s">{riding(face, text, size, 40, f, ink)}</g>'
    svg("hero.svg", W, H, "Matéo Guézennec, fullstack developer from Brittany, France", body, css)

def stack():
    W, T, step = 840, 88, 71
    rows = [("What you see", RED, ["HTML", "CSS", "Sass", "TypeScript", "JavaScript", "Vue", "Nuxt", "Vite", "Vuetify", "Figma"]),
            ("What runs it", GREEN, ["Node.js", "Express", "GraphQL", "Kafka", "PHP", "Python", "Java", "Kotlin", "C++", "C", "C#"]),
            ("Where it lives", BLUE, ["PostgreSQL", "MySQL", "MongoDB", "Elastic", "Docker", "Nginx", "Linux", "Git"])]
    body, y = "", 40
    names = []
    for i, (title, col, items) in enumerate(rows):
        body += f'<path fill="{WHITE}" d="{SEMI.text(title, 17, 30, y)}"/>'
        f = wave(y + 66, 9, 420, i * 1.3)
        body += f'<path fill="none" d="{ribbon_d(f, W)}" stroke="{col}" stroke-width="{T}"/>'
        for j, name in enumerate(items):
            names.append(name)
            cx = 62 + j * step
            cy = f(cx)
            s = 28 / 24
            if name == "C#":  # the stored glyph is the .NET wordmark, so set the name itself
                body += f'<path fill="{INK}" d="{BOLD.text(name, 24, cx - BOLD.width(name, 24) / 2, cy - 5)}"/>'
            else:
                body += f'<path fill="{INK}" transform="translate({cx - 14:.1f} {cy - 28:.1f}) scale({s:.3f})" d="{ICONS[name]}"/>'
            lw = SEMI.width(name, 12)
            body += f'<path fill="{INK}" d="{SEMI.text(name, 12, cx - lw / 2, cy + 23)}"/>'
        y += 164
    svg("stack.svg", W, y - 21, "Tech stack: " + ", ".join(names), body)

def card(name, title, kicker, accent, desc, tags, visual, css=""):
    W, H = 840, 264
    b = f'<path fill="{WHITE}" d="{BOLD.text(title, 34, 36, 62)}"/>'
    b += f'<path fill="{accent}" d="{SEMI.text(kicker, 17, 36, 92)}"/>'
    for i, l in enumerate(desc):
        b += f'<path fill="{MIST}" d="{REG.text(l, 18, 36, 134 + i * 28)}"/>'
        assert REG.width(l, 18) < 480, l
    b += f'<path fill="{WHITE}" d="{SEMI.text(tags, 15.5, 36, 236)}"/>'
    svg(name, W, H, f"{title}: {kicker}", b + visual, css)

def knight_tour(n=8, start=(0, 0)):
    moves = [(1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1), (-2, 1), (-1, 2)]
    ok = lambda p, seen: 0 <= p[0] < n and 0 <= p[1] < n and p not in seen
    path, seen = [start], {start}
    while len(path) < n * n:
        x, y = path[-1]
        opts = [(x + a, y + b) for a, b in moves if ok((x + a, y + b), seen)]
        nxt = min(opts, key=lambda p: (sum(ok((p[0] + a, p[1] + b), seen) for a, b in moves), abs(p[0] - 3.5) + abs(p[1] - 3.5)))
        path.append(nxt); seen.add(nxt)
    assert len(set(path)) == 64 and all(sorted((abs(p[0] - q[0]), abs(p[1] - q[1]))) == [1, 2] for p, q in zip(path, path[1:]))
    return path

def projects():
    # Unolingo: the three writing systems the app teaches.
    rows = ["あいうえお", "アイウエオ", "日本語漢字"]
    size, x0, y0, v = 58, 532, 45, ""
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            on = r == 0 and c == 0 or r == 1 and c == 2 or r == 2 and c == 3
            x, y = x0 + c * size, y0 + r * size
            v += f'<rect x="{x + 2}" y="{y + 2}" width="{size - 4}" height="{size - 4}" rx="9" fill="{RED if on else SQUARE}"/>'
            w = JP.adv(ch, 30)
            v += f'<path fill="{INK if on else WHITE}" d="{JP.glyph(ch, 30, x + size / 2 - w / 2, y + size / 2 + 11)}"/>'
    card("unolingo.svg", "Unolingo", "Android app to learn Japanese", RED,
         ["Hiragana, katakana and kanji quizzes, with an", "audio mode using Japanese text-to-speech",
          "and a split-screen 1v1 duel on one phone."], "Kotlin, Jetpack Compose, Room", v)
    # ChevalierEchec: a real knight's tour, drawn once on load.
    cell, x0, y0 = 26, 588, 28
    v = "".join(f'<rect x="{x0 + x * cell}" y="{y0 + y * cell}" width="{cell}" height="{cell}" fill="{SQUARE}"/>'
                for y in range(8) for x in range(8) if (x + y) % 2 == 0)
    pts = [(x0 + (x + .5) * cell, y0 + (y + .5) * cell) for x, y in knight_tour()]
    d = "M" + "L".join(f"{x} {y}" for x, y in pts)
    v += (f'<path class="k" pathLength="1" d="{d}" fill="none" stroke="{BLUE}" stroke-width="2.4" stroke-linejoin="round" stroke-linecap="round"/>'
          f'<circle cx="{pts[0][0]}" cy="{pts[0][1]}" r="6" fill="{GREEN}"/>'
          f'<circle class="e" cx="{pts[-1][0]}" cy="{pts[-1][1]}" r="6" fill="{RED}"/>')
    css = (".k{stroke-dasharray:1;stroke-dashoffset:1;animation:k 5s linear .3s forwards}.e{opacity:0;animation:e .2s 5.3s forwards}"
           "@keyframes k{to{stroke-dashoffset:0}}@keyframes e{to{opacity:1}}")
    card("chevalierechec.svg", "ChevalierEchec", "Knight's tour solver", BLUE,
         ["Backtracking algorithms move a knight across", "every square of a chessboard, with a Tkinter",
          "board to watch the tour being solved."], "Python, Tkinter, backtracking", v, css)

hero(); stack(); projects()
