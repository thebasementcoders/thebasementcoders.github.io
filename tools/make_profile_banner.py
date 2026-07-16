#!/usr/bin/env python3
"""Generate The Basement Coders brand banners (pure PIL, reproducible).

Renders two sizes from one proportional layout:
  * profile-banner-4096x2304.png — 16:9 developer-profile banner (GitHub, etc.)
  * web-header.png               — wide 3:1 strip for the site header (no crop)

Brand (from index.html): 135° dark-slate → indigo gradient, paper text, the
"Small, useful apps — made with care." tagline, and a terminal-prompt motif.
"""
from PIL import Image, ImageDraw, ImageFont

# Brand palette (from index.html)
SLATE = (43, 47, 58)      # #2b2f3a
INDIGO = (63, 81, 181)    # #3f51b5
PAPER = (247, 243, 233)   # #f7f3e9

FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make(W, H, out, *, two_line_title):
    """Render a banner. `two_line_title` stacks "The Basement" / "Coders" (tall
    formats); otherwise a single "The Basement Coders" line (wide strips)."""
    cx = W // 2

    # ── 135° diagonal gradient (top-left slate → bottom-right indigo) ──────
    base = Image.new("RGB", (W, H))
    gpx = base.load()
    for y in range(H):
        yy = y / H
        for x in range(W):
            gpx[x, y] = lerp(SLATE, INDIGO, (x / W + yy) / 2.0)
    draw = ImageDraw.Draw(base, "RGBA")

    # ── Starfield, denser toward the dark top-left corner ─────────────────
    seed = 1234567

    def rnd():
        nonlocal seed
        seed = (1103515245 * seed + 12345) & 0x7FFFFFFF
        return seed / 0x7FFFFFFF

    dots = int(W * H / 10000)
    for _ in range(dots):
        x = rnd() * W
        y = rnd() * H
        corner = 1.0 - ((x / W) + (y / H)) / 2.0
        if rnd() > corner * 0.9:
            continue
        r = 1 + rnd() * (H / 1000)
        a = int(40 + corner * 120)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, a))

    # ── Proportional type sizes ───────────────────────────────────────────
    title_px = int(H * (0.155 if two_line_title else 0.20))
    prompt_px = int(title_px * 0.42)
    tag_px = int(title_px * 0.37)
    title_font = ImageFont.truetype(FONT_BOLD, title_px)
    prompt_font = ImageFont.truetype(FONT_MONO, prompt_px)
    tag_font = ImageFont.truetype(FONT_REG, tag_px)

    def centered(text, font, y, fill, shadow=True):
        off = max(2, H // 384)
        if shadow:
            draw.text((cx + off, y + off), text, font=font, fill=(0, 0, 0, 90),
                      anchor="mm")
        draw.text((cx, y), text, font=font, fill=fill, anchor="mm")

    # ── Vertical rhythm (fractions of H) ──────────────────────────────────
    prompt = "~/basement $"
    if two_line_title:
        y_prompt, y_t1, y_t2 = H * 0.31, H * 0.50, H * 0.66
        y_rule, y_tag = H * 0.76, H * 0.82
    else:
        y_prompt, y_t1 = H * 0.22, H * 0.50
        y_t2 = None
        y_rule, y_tag = H * 0.68, H * 0.80

    # terminal prompt + blinking cursor block
    centered(prompt, prompt_font, y_prompt, (255, 255, 255, 150), shadow=False)
    pb = draw.textbbox((cx, y_prompt), prompt, font=prompt_font, anchor="mm")
    cur_h = pb[3] - pb[1]
    gap = prompt_px * 0.2
    draw.rectangle([pb[2] + gap, pb[1] + cur_h * 0.08,
                    pb[2] + gap + prompt_px * 0.5, pb[3] - cur_h * 0.08],
                   fill=(255, 255, 255, 150))

    # title
    if two_line_title:
        centered("The Basement", title_font, y_t1, PAPER)
        centered("Coders", title_font, y_t2, PAPER)
    else:
        centered("The Basement Coders", title_font, y_t1, PAPER)

    # thin accent rule
    rule_w = W * 0.19
    draw.rounded_rectangle([cx - rule_w, y_rule - 3, cx + rule_w, y_rule + 3],
                           radius=3, fill=(255, 255, 255, 190))

    # tagline
    centered("Small, useful apps — made with care.", tag_font, y_tag,
             (247, 243, 233, 235), shadow=False)

    base.save(out)
    print("wrote", out, base.size)


if __name__ == "__main__":
    make(4096, 2304, "profile-banner-4096x2304.png", two_line_title=True)
    make(2400, 800, "web-header.png", two_line_title=False)
