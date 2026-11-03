#!/usr/bin/env python3
"""Builds the BlasterWhite logo: three tildes stacked on top of each other, one color each.

Pure geometry (no fonts, no dependencies). Each tilde is a sine wave drawn as a thick
stroke with round caps, the same wave shape as the ribbons in the profile hero.

Usage:
    python3 scripts/build_logo.py                       # writes profile/logo.svg and profile/logo-dark.svg
    python3 scripts/build_logo.py --colors "#F2404A,#2BD540,#19B4E8" --gap 0.36 --stroke 0.16
"""
import argparse
import math
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
INK = "#0B1A2B"
COLORS = ["#F2404A", "#2BD540", "#19B4E8"]  # red, green, blue: same order as the hero ribbons


def tilde(cx, cy, width, amp, steps=96, extend=0.14):
    """Path for one tilde centred on (cx, cy): hump on the left, dip on the right.

    One full sine period, extended a little at both ends so the tips curl back
    like a typed ~ instead of ending flat.
    """
    t0, t1 = -math.pi * (1 + extend), math.pi * (1 + extend)
    pts = []
    for i in range(steps + 1):
        t = t0 + (t1 - t0) * i / steps
        x = cx + width / 2 * t / math.pi / (1 + extend)
        y = cy + amp * math.sin(t)  # SVG y points down: sin < 0 on the left = hump up
        pts.append(f"{x:.2f} {y:.2f}")
    return "M" + "L".join(pts)


def logo(size, colors, gap, stroke, amp, width, bg=None, radius=0.22):
    """Returns an SVG document. All lengths except size are fractions of size."""
    s = size
    sw = stroke * s
    mid = s / 2
    paths = []
    for i, col in enumerate(colors):
        cy = mid + (i - (len(colors) - 1) / 2) * gap * s
        d = tilde(mid, cy, width * s, amp * s)
        paths.append(f'<path d="{d}" fill="none" stroke="{col}" stroke-width="{sw:.2f}" '
                     f'stroke-linecap="round" stroke-linejoin="round"/>')
    back = f'<rect width="{s}" height="{s}" rx="{radius * s:.1f}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{s}" height="{s}" viewBox="0 0 {s} {s}" '
            f'role="img" aria-label="BlasterWhite logo">{back}{"".join(paths)}</svg>\n')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--colors", default=",".join(COLORS), help="comma-separated colors, top to bottom")
    ap.add_argument("--size", type=int, default=512, help="canvas size in px (square)")
    ap.add_argument("--gap", type=float, default=0.24, help="vertical distance between tildes, fraction of size")
    ap.add_argument("--stroke", type=float, default=0.11, help="line thickness, fraction of size")
    ap.add_argument("--amp", type=float, default=0.075, help="wave height, fraction of size")
    ap.add_argument("--width", type=float, default=0.62, help="tilde width, fraction of size")
    ap.add_argument("--bg", default=INK, help="background of the dark variant")
    ap.add_argument("--out", default=str(ROOT / "profile"), help="output folder")
    a = ap.parse_args()

    colors = [c.strip() for c in a.colors.split(",") if c.strip()]
    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    common = dict(size=a.size, colors=colors, gap=a.gap, stroke=a.stroke, amp=a.amp, width=a.width)
    (out / "logo.svg").write_text(logo(**common))
    (out / "logo-dark.svg").write_text(logo(**common, bg=a.bg))
    print(f"wrote {out / 'logo.svg'} and {out / 'logo-dark.svg'}")


if __name__ == "__main__":
    main()
