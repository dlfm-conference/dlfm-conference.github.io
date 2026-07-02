#!/usr/bin/env python3
"""Turn a white/near-white background transparent, writing a PNG.

For sponsor/partner logos delivered as JPEGs on a white ground. Keys near-white
pixels to alpha with a feathered edge (so anti-aliased text keeps clean edges,
no white halo). Dark/coloured logo marks are preserved.

Usage: python3 tools/key_white.py <in.(jpg|png|webp)> <out.png> [hi] [lo]
  hi (default 248): min(r,g,b) >= hi  -> fully transparent
  lo (default 228): min(r,g,b) <= lo  -> fully opaque; between = feathered
"""
import sys
from PIL import Image


def main():
    if len(sys.argv) < 3:
        sys.exit("usage: key_white.py <in> <out.png> [hi] [lo]")
    src, dst = sys.argv[1], sys.argv[2]
    hi = int(sys.argv[3]) if len(sys.argv) > 3 else 248
    lo = int(sys.argv[4]) if len(sys.argv) > 4 else 228
    im = Image.open(src).convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            mn = min(r, g, b)
            if mn >= hi:
                na = 0
            elif mn <= lo:
                na = 255
            else:
                na = int((hi - mn) / (hi - lo) * 255)
            if na < a:
                px[x, y] = (r, g, b, na)
    im.save(dst)
    print(f"wrote {dst} ({w}x{h})")


if __name__ == "__main__":
    main()
