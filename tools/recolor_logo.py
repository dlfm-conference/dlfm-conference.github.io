#!/usr/bin/env python3
"""Recolour a logo to a single target colour (e.g. to match footer text).

Modes:
  flat  — set every opaque pixel to <hex>, preserving alpha. Best for logos
          that are already a flat monochrome wordmark (e.g. RISM).
  ink   — keep only the dark "ink" (outlines/text), recoloured to <hex>, with
          lighter/coloured fills dropped to transparent (feathered edges). Best
          for thick-outlined cartoon logos (e.g. Let's Encode!).

Usage:
  python3 tools/recolor_logo.py <in> <out.png> <hex> flat
  python3 tools/recolor_logo.py <in> <out.png> <hex> ink [lo=90] [hi=160]
"""
import sys
from PIL import Image


def main():
    a = sys.argv
    if len(a) < 5:
        sys.exit("usage: recolor_logo.py <in> <out.png> <hex> <flat|ink> [lo] [hi]")
    src, dst, hexc, mode = a[1], a[2], a[3].lstrip("#"), a[4]
    R, G, B = (int(hexc[i:i+2], 16) for i in (0, 2, 4))
    im = Image.open(src).convert("RGBA")
    px = im.load()
    w, h = im.size
    lo = int(a[5]) if len(a) > 5 else 90
    hi = int(a[6]) if len(a) > 6 else 160
    for y in range(h):
        for x in range(w):
            r, g, b, alpha = px[x, y]
            if mode == "flat":
                if alpha > 0:
                    px[x, y] = (R, G, B, alpha)
            elif mode == "ink":
                L = 0.2126 * r + 0.7152 * g + 0.0722 * b
                if L <= lo:
                    f = 1.0
                elif L >= hi:
                    f = 0.0
                else:
                    f = (hi - L) / (hi - lo)
                px[x, y] = (R, G, B, int(alpha * f))
            else:
                sys.exit(f"unknown mode: {mode}")
    im.save(dst)
    print(f"wrote {dst} ({w}x{h}, mode={mode})")


if __name__ == "__main__":
    main()
