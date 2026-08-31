#!/usr/bin/env python3
"""Trace the bass clef out of assets/logo/dlfm-logo.png into an SVG path.

The 404 page's motif (_includes/tacet-bar.html) is a bar of music that does not
sound, and its clef is the logo's OWN clef rather than a look-alike — so the two
cannot drift apart stylistically. This script is how that path was produced; run
it again if the logo is ever redrawn, and paste the result into the include.

Method:
  1. Locate the staff lines in the logo: rows that are dark across most of its
     width. They give both the staff spacing and the position of the F line.
  2. Erase those lines WITHOUT cutting the clef that crosses them: inside a
     line's rows, a pixel keeps the darker of the two pixels straddling the
     line. The clef's strokes are dark on both sides and survive; the 3px line
     has paper above and below and vanishes.
  3. Crop to the clef (left of the "D", whose stem is a full-height column),
     smooth and upscale with mkbitmap, vectorise with potrace.
  4. Map potrace's coordinates into the staff units the include draws in:
     10 units per staff space, F line (second from the top) at y = 13.

Requires potrace and mkbitmap on PATH (brew install potrace), plus Pillow.

Usage:
  python3 tools/trace_clef.py [clef-x] [--keep]      # clef-x defaults to 8
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
LOGO = ROOT / "assets/logo/dlfm-logo.png"
UNIT = 10.0          # staff units per staff space, as the include draws them
STAFF_F = 13.0       # where the include puts the F line
SCALE = 6            # mkbitmap -s
PRECISION = 1


def staff_bands(mask, w, h):
    """Rows that are dark across most of the width, grouped into lines."""
    bands = []
    for y in range(h):
        if sum(mask[y]) / w > 0.8:
            if bands and bands[-1][1] == y - 1:
                bands[-1][1] = y
            else:
                bands.append([y, y])
    if len(bands) != 5:
        sys.exit(f"expected 5 staff lines in the logo, found {len(bands)}")
    return bands


def main():
    argv = [a for a in sys.argv[1:] if not a.startswith("-")]
    keep = "--keep" in sys.argv
    clef_x = float(argv[0]) if argv else 8.0

    im = Image.open(LOGO).convert("RGBA")
    w, h = im.size
    px = im.load()

    def lum(x, y):                        # composited over paper, so edges stay grey
        r, g, b, a = px[x, y]
        return 255 - a * (255 - (r + g + b) // 3) // 255

    grey = [[lum(x, y) for x in range(w)] for y in range(h)]
    mask = [[grey[y][x] < 128 for x in range(w)] for y in range(h)]
    bands = staff_bands(mask, w, h)

    lines = [(a + b) / 2 for a, b in bands]
    space = (lines[-1] - lines[0]) / 4          # logo px per staff space
    f_line = lines[1]                           # F line: second from the top
    print(f"staff lines at {lines}, space {space:.3f}px, F line {f_line}", file=sys.stderr)

    for r0, r1 in bands:                        # step 2
        for y in range(r0, r1 + 1):
            for x in range(w):
                grey[y][x] = max(grey[r0 - 1][x], grey[r1 + 1][x])
    for y in range(h):
        for x in range(w):
            mask[y][x] = grey[y][x] < 128

    # The "D" begins at the first column that is ink for most of the staff's height.
    wall = next(x for x in range(w)
                if sum(mask[y][x] for y in range(int(lines[0]), int(lines[-1]))) > 100)
    cols = [x for x in range(wall) if any(mask[y][x] for y in range(h))]
    rows = [y for y in range(h) if any(mask[y][x] for x in range(wall))]
    x0, x1, y0, y1 = min(cols), max(cols), min(rows), max(rows)
    print(f'"D" at x={wall}; clef {x0},{y0}..{x1},{y1}', file=sys.stderr)

    tmp = Path(tempfile.mkdtemp(prefix="clef-"))
    pgm, pbm, out = tmp / "clef.pgm", tmp / "clef.pbm", tmp / "clef.svg"
    crop = Image.new("L", (x1 - x0 + 1, y1 - y0 + 1))
    cp = crop.load()
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            cp[x - x0, y - y0] = grey[y][x]
    crop.save(pgm)
    subprocess.run(["mkbitmap", "-f", "20", "-s", str(SCALE), "-t", "0.48",
                    "-o", str(pbm), str(pgm)], check=True)
    subprocess.run(["potrace", "-s", "--alphamax", "1.334", "--opttolerance", "1.0",
                    "--turdsize", "8", "-o", str(out), str(pbm)], check=True)

    svg = out.read_text(encoding="utf-8")
    height = float(re.search(r'height="([\d.]+)pt"', svg).group(1))

    def T(X, Y):
        """potrace units -> upscaled px -> logo px -> staff units."""
        ux, uy = X * 0.1, height - Y * 0.1
        lx, ly = x0 + ux / SCALE, y0 + uy / SCALE
        return (clef_x + (lx - x0) * UNIT / space,
                STAFF_F + (ly - f_line) * UNIT / space)

    def num(v):
        return (f"%.{PRECISION}f" % v).rstrip("0").rstrip(".") or "0"

    pieces = []
    for m in re.finditer(r'<path d="(.*?)"', svg, re.S):
        toks = re.findall(r"[MmCcLlVvHhZz]|-?\d*\.?\d+", m.group(1))
        cur = cmd = None
        i = 0
        while i < len(toks):
            t = toks[i]
            if t.isalpha():
                cmd = t
                i += 1
                if cmd in "Zz":
                    pieces.append("Z")
                continue
            if cmd in "Mm":
                X, Y = float(toks[i]), float(toks[i + 1]); i += 2
                if cmd == "m" and cur:
                    X, Y = cur[0] + X, cur[1] + Y
                cur = (X, Y)
                pieces.append("M " + " ".join(num(v) for v in T(X, Y)))
                cmd = "l" if cmd == "m" else "L"
            elif cmd in "Ll":
                X, Y = float(toks[i]), float(toks[i + 1]); i += 2
                if cmd == "l":
                    X, Y = cur[0] + X, cur[1] + Y
                cur = (X, Y)
                pieces.append("L " + " ".join(num(v) for v in T(X, Y)))
            elif cmd in "Cc":
                v = [float(x) for x in toks[i:i + 6]]; i += 6
                if cmd == "c":
                    v = [cur[0] + v[0], cur[1] + v[1], cur[0] + v[2],
                         cur[1] + v[3], cur[0] + v[4], cur[1] + v[5]]
                pieces.append("C " + " ".join(
                    num(c) for pt in (T(v[0], v[1]), T(v[2], v[3]), T(v[4], v[5])) for c in pt))
                cur = (v[4], v[5])
            elif cmd in "VvHh":
                a = float(toks[i]); i += 1
                if cmd == "v":
                    cur = (cur[0], cur[1] + a)
                elif cmd == "V":
                    cur = (cur[0], a)
                elif cmd == "h":
                    cur = (cur[0] + a, cur[1])
                else:
                    cur = (a, cur[1])
                pieces.append("L " + " ".join(num(v) for v in T(*cur)))
            else:
                sys.exit(f"unhandled path command {cmd!r}")

    print(" ".join(pieces))
    if keep:
        print(f"intermediates kept in {tmp}", file=sys.stderr)


if __name__ == "__main__":
    main()
