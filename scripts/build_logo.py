#!/usr/bin/env python3
"""Builds the BlasterWhite logo: three "~" stacked close together, one color each.

The tilde is the real glyph from Source Code Pro Black, embedded below as an outline so the
script needs no font and no dependency. To try another font, pass --font (needs fontTools).

Usage:
    python3 scripts/build_logo.py                        # writes profile/logo.svg and profile/logo-dark.svg
    python3 scripts/build_logo.py --gap=-0.15            # tildes closer (negative values nest them)
    python3 scripts/build_logo.py --colors "#F2404A,#2BD540,#19B4E8"
    python3 scripts/build_logo.py --font /path/to/Font-Bold.ttf
"""
import argparse
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
INK = "#0B1A2B"
COLORS = ["#F2404A", "#2BD540", "#19B4E8"]  # red, green, blue: same order as the hero ribbons

# "asciitilde" from Source Code Pro Black (SIL Open Font License 1.1), in font units, y pointing up.
TILDE = (
    "M384 234C450 234 512 278 558 386L456 434C438 384 413 354 386 354"
    "C332 354 300 426 216 426C150 426 88 382 42 274L144 226"
    "C162 276 188 306 214 306C268 306 300 234 384 234Z"
)
TILDE_BOUNDS = (42, 226, 558, 434)  # xMin, yMin, xMax, yMax


def glyph_from_font(path, char="~"):
    """Extracts a glyph outline and its bounds from a font file (needs fontTools)."""
    from fontTools.ttLib import TTFont
    from fontTools.pens.svgPathPen import SVGPathPen
    from fontTools.pens.boundsPen import BoundsPen
    font = TTFont(path)
    gs = font.getGlyphSet()
    glyph = gs[font.getBestCmap()[ord(char)]]
    pen, bounds = SVGPathPen(gs), BoundsPen(gs)
    glyph.draw(pen)
    glyph.draw(bounds)
    return pen.getCommands(), bounds.bounds


def logo(d, bounds, size, colors, gap, margin, bg=None, radius=0.22):
    """Stacks the glyph once per color, centred in a square of `size` px.

    gap is the space between two tildes, as a fraction of the tilde's height.
    margin is the free space around the stack, as a fraction of size.
    """
    x0, y0, x1, y1 = bounds
    gw, gh = x1 - x0, y1 - y0
    n = len(colors)
    stack_h = gh * (n + gap * (n - 1))
    k = size * (1 - 2 * margin) / max(gw, stack_h)  # font units -> px
    left = (size - gw * k) / 2
    top = (size - stack_h * k) / 2
    paths = []
    for i, col in enumerate(colors):
        ty = top + i * gh * (1 + gap) * k  # top edge of this tilde, in px
        # flip y (fonts point up), then move the glyph's top-left corner to (left, ty)
        tf = f"translate({left - x0 * k:.2f} {ty + y1 * k:.2f}) scale({k:.5f} {-k:.5f})"
        paths.append(f'<path transform="{tf}" fill="{col}" d="{d}"/>')
    back = f'<rect width="{size}" height="{size}" rx="{radius * size:.1f}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" '
            f'viewBox="0 0 {size} {size}" role="img" aria-label="BlasterWhite logo">'
            f'{back}{"".join(paths)}</svg>\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--colors", default=",".join(COLORS), help="comma-separated colors, top to bottom")
    ap.add_argument("--gap", type=float, default=0.05,
                    help="space between tildes, fraction of a tilde's height; negative nests them (pass as --gap=-0.1)")
    ap.add_argument("--size", type=int, default=512, help="canvas size in px (square)")
    ap.add_argument("--margin", type=float, default=0.16, help="space around the logo, fraction of size")
    ap.add_argument("--bg", default=INK, help="background of the dark variant")
    ap.add_argument("--font", help="take the tilde from this font file instead of Source Code Pro Black (needs fontTools)")
    ap.add_argument("--out", default=str(ROOT / "profile"), help="output folder")
    a = ap.parse_args()

    d, bounds = glyph_from_font(a.font) if a.font else (TILDE, TILDE_BOUNDS)
    colors = [c.strip() for c in a.colors.split(",") if c.strip()]
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    common = dict(d=d, bounds=bounds, size=a.size, colors=colors, gap=a.gap, margin=a.margin)
    (out / "logo.svg").write_text(logo(**common))
    (out / "logo-dark.svg").write_text(logo(**common, bg=a.bg))
    print(f"wrote {out / 'logo.svg'} and {out / 'logo-dark.svg'}")


if __name__ == "__main__":
    main()
