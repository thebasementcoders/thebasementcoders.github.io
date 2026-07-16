#!/usr/bin/env python3
"""Generate The Basement Coders developer-profile banner (4096x2304, 16:9).

Matches the brand on index.html: a 135° dark-slate → indigo gradient, paper-
coloured text, and the "Small, useful apps — made with care." tagline, with a
subtle terminal-prompt motif for the "coders" vibe. Pure PIL, reproducible.
"""
from PIL import Image, ImageDraw, ImageFont
import math

W, H = 4096, 2304
OUT = "profile-banner-4096x2304.png"

# Brand palette (from index.html)
SLATE = (43, 47, 58)      # #2b2f3a
INDIGO = (63, 81, 181)    # #3f51b5
PAPER = (247, 243, 233)   # #f7f3e9

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ── 135° diagonal gradient (top-left slate → bottom-right indigo) ──────────
base = Image.new("RGB", (W, H), SLATE)
px = base.load()
# projection onto the 135° axis: t = (x + y) normalised
maxproj = W + H
for y in range(H):
    for x in range(0, W, 1):
        pass  # replaced by row fill below for speed

# Fast row-wise gradient: precompute per-(x+y) colour is expensive; do it with
# a small gradient image scaled up along the diagonal instead.
grad = Image.new("RGB", (W, H))
gpx = grad.load()
for y in range(H):
    yy = y / H
    for x in range(W):
        t = (x / W + yy) / 2.0
        gpx[x, y] = lerp(SLATE, INDIGO, t)
base = grad
draw = ImageDraw.Draw(base, "RGBA")

# ── Subtle starfield / code-dust in the dark corner ────────────────────────
# deterministic pseudo-random dots (no Math.random needed)
seed = 1234567
def rnd():
    global seed
    seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
    return seed / 0x7FFFFFFF

for _ in range(900):
    x = rnd() * W
    y = rnd() * H
    # brighter/denser toward the dark top-left corner
    corner = 1.0 - ((x / W) + (y / H)) / 2.0
    if rnd() > corner * 0.9:
        continue
    r = 1 + rnd() * 2.2
    a = int(40 + corner * 120)
    draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))

# ── Title, prompt, tagline (centred stack) ──────────────────────────────────
title_font = ImageFont.truetype(FONT_BOLD, 360)
prompt_font = ImageFont.truetype(FONT_MONO, 150)
tag_font = ImageFont.truetype(FONT_REG, 132)

cx = W // 2

# terminal prompt line above the title: "~/basement $ ▮"
prompt = "~/basement $"
draw.text((cx, 720), prompt, font=prompt_font, fill=(255, 255, 255, 150),
          anchor="mm")
# blinking-cursor block after the prompt
pb = draw.textbbox((cx, 720), prompt, font=prompt_font, anchor="mm")
draw.rectangle([pb[2] + 30, pb[1] + 10, pb[2] + 100, pb[3] - 10],
               fill=(255, 255, 255, 150))

# Title — two words, tight stack, paper colour with soft shadow
def centered(text, font, y, fill, shadow=True):
    if shadow:
        draw.text((cx + 6, y + 6), text, font=font, fill=(0, 0, 0, 90),
                  anchor="mm")
    draw.text((cx, y), text, font=font, fill=fill, anchor="mm")

centered("The Basement", title_font, 1150, PAPER)
centered("Coders", title_font, 1520, PAPER)

# accent rule under the title (thin)
draw.rounded_rectangle([cx - 380, 1748, cx + 380, 1754], radius=3,
                       fill=(255, 255, 255, 190))

# tagline
centered("Small, useful apps — made with care.", tag_font, 1900,
         (247, 243, 233, 235), shadow=False)

base.save(OUT)
print("wrote", OUT, base.size)
