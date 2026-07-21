#!/usr/bin/env python
"""Remove pure-green chroma-key background -> transparent RGBA PNG.
Pure PIL (no numpy). Includes green despill on kept pixels.
Usage: python chroma_key.py <src.png> <dst.png> [out_size]
"""
import sys
from PIL import Image, ImageChops

THRESH = 34          # green-excess above this => background
FEATHER = 26         # soft edge width in green-excess units


def key(src, dst, out_size=600):
    im = Image.open(src).convert("RGB")
    r, g, b = im.split()
    rb_max = ImageChops.lighter(r, b)
    green_excess = ImageChops.subtract(g, rb_max)  # 0..255, high where green

    # alpha: 255 (opaque) below THRESH, ramp to 0 across FEATHER
    def a_map(x):
        if x <= THRESH:
            return 255
        if x >= THRESH + FEATHER:
            return 0
        return int(255 * (1 - (x - THRESH) / FEATHER))

    alpha = green_excess.point(a_map)

    # despill: clamp green channel down to rb_max where there is green spill
    g_despilled = ImageChops.darker(g, rb_max)
    im = Image.merge("RGB", (r, g_despilled, b))

    out = im.convert("RGBA")
    out.putalpha(alpha)

    if out_size:
        out = out.resize((out_size, out_size), Image.LANCZOS)
    out.save(dst)
    print(dst)


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    size = int(sys.argv[3]) if len(sys.argv) > 3 else 600
    key(src, dst, size)
