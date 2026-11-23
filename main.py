#!/usr/bin/env python3
"""The Monday World - one-page newspaper summing up Monday 23 November 2026.

Draws a 1024x1024 PNG with only the Python standard library: its own
5x7 bitmap font and its own PNG encoder. Deterministic: two runs write
byte-identical output. Writes to $MAKEFUN_OUTPUT_DIR/entry.png, or
/output/entry.png when the variable is not set.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (250, 246, 236)
PAPER2 = (244, 238, 224)
INK = (28, 28, 26)
RED = (176, 32, 32)
RED_DK = (140, 22, 22)
BLUE = (30, 64, 120)
GREEN = (28, 110, 60)
AMBER = (176, 110, 0)
GREY = (110, 106, 96)
LIGHT = (214, 206, 190)
SKY = (196, 222, 236)
SEA = (64, 130, 168)
SAND = (232, 204, 150)

# ------------------------------------------------------- 5x7 bitmap font
# Each glyph is 7 rows of 5 cells; '#' is on, '.' is off.
_FONT = {
    'A': (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'B': ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    'C': (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    'D': ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    'E': ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    'F': ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    'G': (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    'H': ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    'I': (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'J': ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    'K': ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    'L': ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    'M': ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    'N': ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    'O': (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'P': ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    'Q': (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    'R': ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    'S': (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    'T': ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    'U': ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    'V': ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'W': ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    'X': ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    'Y': ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    'Z': ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    'a': (".....", ".....", ".####", "....#", ".####", "#...#", ".####"),
    'b': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    'c': (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    'd': ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    'e': (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    'f': ("..##.", ".#...", ".#...", "####.", ".#...", ".#...", ".#..."),
    'g': (".....", ".####", "#...#", "#...#", ".####", "....#", ".###."),
    'h': ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'i': (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    'j': (".....", "...#.", ".....", "..##.", "...#.", "...#.", "##..."),
    'k': ("#....", "#....", "#..#.", "#.#..", "##...", "#.#..", "#..#."),
    'l': (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    'm': (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    'n': (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    'o': (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    'p': (".....", "####.", "#...#", "#...#", "####.", "#....", "#...."),
    'q': (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    'r': (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    's': (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    't': (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    'u': (".....", ".....", "#...#", "#...#", "#...#", "#..##", ".##.#"),
    'v': (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    'w': (".....", ".....", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    'x': (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    'y': (".....", "#...#", "#...#", ".#.#.", "..#..", "..#..", ".##.."),
    'z': (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    '0': (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    '1': ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    '2': (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    '3': ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    '4': ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    '5': ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    '6': (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    '7': ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    '8': (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    '9': (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    ' ': (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    '.': (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ',': (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ':': (".....", ".....", ".##..", ".....", ".##..", ".....", "....."),
    ';': (".....", ".....", ".##..", ".....", ".##..", "..#..", ".#..."),
    '!': ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    '?': (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    '-': (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    '(': ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ')': (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '/': ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    '%': ("#...#", "#..#.", "...#.", "..#..", ".#...", "#..#.", "#...#"),
    '&': (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    '+': (".....", ".....", "..#..", ".###.", "..#..", ".....", "....."),
    '=': (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    '*': (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    '#': (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    '$': ("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    '@': (".###.", "#...#", "#.###", "#.#.#", "#.###", "#....", ".###."),
    '_': (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    '[': (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    ']': (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
}

# Normalise fancy punctuation to the glyphs above.
_NORM = {
    '\u2019': "'", '\u2018': "'", '\u201c': '"', '\u201d': '"',
    '\u2013': '-', '\u2014': '-', '\u00b7': '.', '\u2022': '.',
    '\u2192': '>', '\u00d7': 'x', '\u2265': '>', '\u2264': '<',
}


def glyph(ch):
    return _FONT.get(_NORM.get(ch, ch), _FONT['?'])


def text_width(s, scale):
    return len(s) * 6 * scale - scale


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def get(self, x, y):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            return tuple(self.px[i:i + 3])
        return (0, 0, 0)

    def fill(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            self.px[base:base + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def rect(self, x, y, w, h, c, t=1):
        self.fill(x, y, w, t, c)
        self.fill(x, y + h - t, w, t, c)
        self.fill(x, y, t, h, c)
        self.fill(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c):
        self.fill(x, y, w, 1, c)

    def vline(self, x, y, h, c):
        self.fill(x, y, 1, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c, filled=True):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = (xx - cx) ** 2 + (yy - cy) ** 2
                if filled:
                    if d <= r * r:
                        self.set(xx, yy, c)
                else:
                    if abs(d - r * r) <= r:
                        self.set(xx, yy, c)

    def poly(self, pts, c):
        # Scanline fill of a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.fill(int(xs[j]), y, max(1, int(xs[j + 1]) - int(xs[j])), 1, c)

    def draw_char(self, x, y, ch, scale, c):
        g = glyph(ch)
        for row in range(7):
            for col in range(5):
                if g[row][col] == '#':
                    self.fill(x + col * scale, y + row * scale, scale, scale, c)

    def text(self, x, y, s, scale, c):
        for i, ch in enumerate(s):
            self.draw_char(x + i * 6 * scale, y, ch, scale, c)
        return x + text_width(s, scale)

    def text_centred(self, cx, y, s, scale, c):
        return self.text(cx - text_width(s, scale) // 2, y, s, scale, c)

    def wrap(self, s, scale, max_w):
        """Split s into lines of at most max_w pixels. Returns list of lines."""
        words = s.split(' ')
        lines, cur = [], ''
        for wd in words:
            trial = (cur + ' ' + wd).strip()
            if text_width(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, c, max_w, leading=None):
        """Draw wrapped paragraph. Returns y just below the last line."""
        lh = leading if leading is not None else 9 * scale
        for ln in self.wrap(s, scale, max_w):
            self.text(x, y, ln, scale, c)
            y += lh
        return y


def png_bytes(cv):
    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]

    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        out += struct.pack('>I', zlib.crc32(tag + data) & 0xffffffff)
        return out

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
            + chunk(b'IEND', b''))

# ------------------------------------------------------------ illustrations
def lead_cop31(cv, x, y, w, h):
    """Antalya conference hall: flags, a long table, a torn pact paper."""
    cv.fill(x, y, w, h, (222, 214, 196))
    cv.fill(x, y, w, h // 2, (188, 206, 220))
    cv.fill(x, y + h // 2, w, h - h // 2, (120, 96, 72))
    # hall columns
    for cx in range(x + 12, x + w - 8, 44):
        cv.fill(cx, y + 8, 8, h // 2 - 4, (240, 236, 224))
    # flags on the table: EU blue, Turkey red, Australia blue
    flags = [(42, 92, 168), (176, 32, 32), (30, 64, 120)]
    for i, fc in enumerate(flags):
        fx = x + 18 + i * 34
        cv.vline(fx, y + 22, 46, INK)
        cv.fill(fx + 1, y + 22, 26, 16, fc)
        if i == 0:
            for sx in (6, 13, 20):
                cv.set(fx + sx, y + 28, (250, 220, 80))
        if i == 1:
            cv.circle(fx + 12, y + 30, 4, (250, 246, 236))
    # long table
    cv.fill(x + 6, y + h - 52, w - 12, 10, (96, 68, 44))
    cv.fill(x + 6, y + h - 42, w - 12, 26, (70, 48, 32))
    # torn pact paper on the table
    px, py = x + w // 2 - 34, y + h - 96
    cv.poly([(px, py), (px + 68, py), (px + 62, py + 40), (px + 34, py + 30),
             (px + 30, py + 44), (px, py + 40)], (250, 248, 240))
    cv.rect(px, py, 68, 44, INK, 1)
    cv.hline(px + 8, py + 10, 52, INK)
    cv.hline(px + 8, py + 18, 40, INK)
    # big red X over the paper
    cv.line(px + 6, py + 26, px + 62, py + 6, RED)
    cv.line(px + 62, py + 26, px + 6, py + 6, RED)
    cv.line(px + 7, py + 27, px + 63, py + 7, RED)
    cv.line(px + 63, py + 27, px + 7, py + 7, RED)


def lead_hormuz(cv, x, y, w, h):
    """Strait of Hormuz: sea, two tankers, fire and smoke."""
    cv.fill(x, y, w, h, SKY)
    cv.fill(x, y + 26, w, 14, (250, 220, 140))
    cv.circle(x + w - 34, y + 26, 16, (250, 214, 120))
    # distant cliffs
    cv.poly([(x, y + 40), (x + 60, y + 28), (x + 120, y + 42), (x, y + 48)],
            (150, 128, 96))
    cv.poly([(x + w, y + 40), (x + w - 70, y + 30), (x + w - 130, y + 42),
             (x + w, y + 48)], (150, 128, 96))
    # sea
    cv.fill(x, y + 46, w, h - 46, SEA)
    for wy in range(y + 56, y + h - 8, 12):
        cv.hline(x + 8, wy, w - 16, (120, 180, 205))
    # tanker 1 (left, listing)
    tx, ty = x + 16, y + h - 66
    cv.fill(tx, ty, 120, 22, (40, 40, 44))
    cv.fill(tx + 8, ty - 16, 26, 16, (200, 60, 40))
    cv.fill(tx + 44, ty - 24, 10, 24, (220, 220, 220))
    cv.fill(tx + 90, ty - 10, 22, 10, (200, 60, 40))
    # flames on tanker 1
    for fx, fh in ((tx + 10, 26), (tx + 26, 34), (tx + 46, 24), (tx + 96, 30)):
        cv.poly([(fx, ty - 16), (fx + 8, ty - 16 - fh), (fx + 16, ty - 16)],
                (250, 140, 20))
        cv.poly([(fx + 4, ty - 16), (fx + 8, ty - 16 - fh + 12), (fx + 12, ty - 16)],
                (250, 210, 40))
    # smoke
    for sx, sy, sr in ((tx + 20, ty - 52, 9), (tx + 34, ty - 62, 11),
                       (tx + 52, ty - 70, 8), (tx + 104, ty - 56, 10)):
        cv.circle(sx, sy, sr, (90, 90, 92))
    # tanker 2 (right, smaller, burning stern)
    tx2, ty2 = x + w - 108, y + h - 52
    cv.fill(tx2, ty2, 92, 18, (52, 52, 56))
    cv.fill(tx2 + 60, ty2 - 12, 18, 12, (200, 60, 40))
    cv.poly([(tx2 + 66, ty2 - 12), (tx2 + 72, ty2 - 40), (tx2 + 78, ty2 - 12)],
            (250, 140, 20))
    cv.circle(tx2 + 72, ty2 - 48, 8, (90, 90, 92))


def lead_markets(cv, x, y, w, h):
    """Stock chart crashing: candlesticks, red arrow, city silhouettes."""
    cv.fill(x, y, w, h, (232, 228, 216))
    # grid
    for gy in range(y + 14, y + h - 30, 16):
        cv.hline(x + 6, gy, w - 12, LIGHT)
    # buildings
    for bx, bh in ((14, 46), (40, 66), (66, 38), (w - 84, 58), (w - 56, 40),
                   (w - 30, 70)):
        cv.fill(x + bx, y + h - 30 - bh, 22, bh, (120, 118, 112))
    # candlesticks falling left to right
    candles = [(18, 26, 10, 1), (48, 40, 8, 0), (78, 52, 12, 1),
               (108, 66, 9, 0), (138, 78, 12, 1), (168, 92, 10, 0),
               (198, 104, 12, 1), (228, 116, 9, 0), (258, 128, 12, 1)]
    for cx, top, ch, up in candles:
        col = GREEN if up else RED
        cv.vline(x + cx + 4, y + top - 6, ch + 12, col)
        cv.fill(x + cx, y + top, 9, ch, col)
    # big red down arrow
    cv.line(x + 20, y + 18, x + w - 30, y + h - 44, RED)
    cv.line(x + 21, y + 18, x + w - 29, y + h - 44, RED)
    cv.line(x + w - 30, y + h - 44, x + w - 62, y + h - 48, RED)
    cv.line(x + w - 30, y + h - 44, x + w - 34, y + h - 74, RED)
    # floor line
    cv.hline(x + 6, y + h - 30, w - 12, INK)


# Small 40x40 field icons for the mid stories.
def icon(cv, x, y, kind):
    bg = {'conflict': (176, 32, 32), 'politics': (30, 64, 120),
          'sport': (28, 110, 60), 'disaster': (200, 90, 20),
          'justice': (90, 60, 140), 'society': (160, 60, 110),
          'science': (20, 120, 120), 'economy': (140, 110, 0),
          'health': (200, 40, 80), 'security': (70, 70, 78)}.get(kind, GREY)
    cv.fill(x, y, 40, 40, bg)
    cv.rect(x, y, 40, 40, INK, 1)
    fg = (250, 246, 236)
    if kind == 'conflict':  # missile
        cv.line(x + 10, y + 30, x + 28, y + 12, fg)
        cv.line(x + 28, y + 12, x + 24, y + 10, fg)
        cv.line(x + 28, y + 12, x + 30, y + 16, fg)
        cv.circle(x + 10, y + 30, 3, fg)
    elif kind == 'politics':  # ballot box
        cv.rect(x + 9, y + 18, 22, 14, fg, 1)
        cv.fill(x + 9, y + 18, 22, 4, fg)
        cv.line(x + 15, y + 12, x + 19, y + 17, fg)
        cv.line(x + 19, y + 17, x + 27, y + 7, fg)
    elif kind == 'sport':  # trophy
        cv.fill(x + 14, y + 10, 12, 12, fg)
        cv.fill(x + 17, y + 22, 6, 6, fg)
        cv.fill(x + 12, y + 28, 16, 3, fg)
    elif kind == 'disaster':  # flame
        cv.poly([(x + 20, y + 8), (x + 28, y + 22), (x + 24, y + 30),
                 (x + 16, y + 30), (x + 12, y + 22)], fg)
    elif kind == 'justice':  # columns
        cv.fill(x + 8, y + 10, 24, 3, fg)
        for cx in (10, 18, 26):
            cv.fill(x + cx, y + 14, 3, 14, fg)
        cv.fill(x + 8, y + 29, 24, 3, fg)
    elif kind == 'society':  # people
        cv.circle(x + 14, y + 14, 4, fg)
        cv.circle(x + 26, y + 14, 4, fg)
        cv.fill(x + 9, y + 20, 10, 12, fg)
        cv.fill(x + 21, y + 20, 10, 12, fg)
    elif kind == 'science':  # flask
        cv.fill(x + 17, y + 8, 6, 8, fg)
        cv.poly([(x + 17, y + 16), (x + 23, y + 16), (x + 28, y + 30),
                 (x + 12, y + 30)], fg)
    elif kind == 'economy':  # chart bars
        cv.fill(x + 9, y + 24, 5, 8, fg)
        cv.fill(x + 17, y + 18, 5, 14, fg)
        cv.fill(x + 25, y + 12, 5, 20, fg)
    elif kind == 'health':  # cross
        cv.fill(x + 17, y + 9, 6, 22, fg)
        cv.fill(x + 9, y + 15, 22, 6, fg)
    else:  # security: shield
        cv.poly([(x + 20, y + 8), (x + 29, y + 12), (x + 29, y + 22),
                 (x + 20, y + 32), (x + 11, y + 22), (x + 11, y + 12)], fg)


# ------------------------------------------------------------- world map
# Continents as rough polygons on a 0-100 x 0-50 grid.
CONTINENTS = [
    [(4, 8), (12, 3), (22, 4), (28, 8), (26, 14), (20, 15), (18, 22),
     (13, 24), (8, 20), (4, 14)],                      # North America
    [(30, 2), (35, 2), (35, 6), (30, 6)],              # Greenland
    [(24, 26), (30, 24), (34, 29), (31, 38), (26, 37), (23, 30)],  # S. America
    [(46, 22), (56, 20), (63, 24), (61, 32), (55, 40), (49, 34),
     (45, 28)],                                          # Africa
    [(46, 8), (56, 6), (59, 11), (53, 14), (47, 12)],   # Europe
    [(59, 6), (86, 4), (96, 10), (93, 18), (81, 22), (71, 26),
     (64, 20), (59, 14)],                                # Asia
    [(78, 26), (87, 28), (85, 32), (77, 30)],           # SE Asia
    [(82, 36), (93, 36), (94, 42), (84, 42)],           # Australia
]
# Pins: (grid x, grid y, story number)
PINS = [
    (63, 14, 1), (66, 20, 2), (57, 8, 4), (10, 18, 5), (43, 15, 7),
    (52, 11, 8), (45, 8, 9), (82, 30, 10), (54, 30, 11), (60, 11, 12),
    (61, 17, 13), (28, 34, 19), (50, 8, 23), (73, 24, 26),
]


def draw_map(cv, x, y, w, h):
    cv.fill(x, y, w, h, (198, 222, 234))
    sx, sy = w / 100.0, h / 50.0
    for poly in CONTINENTS:
        pts = [(x + int(px * sx), y + int(py * sy)) for px, py in poly]
        cv.poly(pts, (196, 186, 158))
        for i in range(len(pts)):
            cv.line(pts[i][0], pts[i][1], pts[(i + 1) % len(pts)][0],
                    pts[(i + 1) % len(pts)][1], (120, 110, 88))
    for px, py, n in PINS:
        cx, cy = x + int(px * sx), y + int(py * sy)
        cv.circle(cx, cy, 7, RED)
        cv.circle(cx, cy, 7, INK, filled=False)
        num = str(n)
        tx = cx - text_width(num, 1) // 2
        cv.text(tx, cy - 3, num, 1, (250, 246, 236))

# ------------------------------------------------------------------ stories
# Badge: C = CONFIRMED (2+ outlets), O = OFFICIAL (on the record),
# R = REPORTED (one outlet). Every story happened or was first reported
# on Monday 23 November 2026.
BADGE_COL = {'C': GREEN, 'O': BLUE, 'R': AMBER}
BADGE_NAME = {'C': 'CONFIRMED', 'O': 'OFFICIAL', 'R': 'REPORTED'}

LEADS = [
    dict(n=1, tag='CLIMATE · ANTALYA', src='REUTERS', badge='C',
         kind='cop31',
         head='COP31 COLLAPSES — no deal as the world splits over fossil fuels',
         text='The longest climate summit in history ends in Antalya with no pact. '
              'The EU and about 130 nations reject a text that never names fossil '
              'fuels; 90+ nations back an electrification pledge instead.'),
    dict(n=2, tag='CONFLICT · STRAIT OF HORMUZ', src='CLAIM · TEHRAN', badge='R',
         kind='hormuz',
         head='TANKERS ABLAZE NEAR HORMUZ AS IRAN WAR BURNS ON',
         text="Iran's navy says two supertankers hit mines and caught fire. "
              'A strike wounds two in Bahrain. Trump dares Iran to test the US '
              'blockade and says new strikes could come after the New Year.'),
    dict(n=3, tag='ECONOMY · MARKETS', src='BLOOMBERG', badge='C',
         kind='markets',
         head='AI SELL-OFF SPREADS — ASIA SLIDES AGAIN, US FUTURES BOUNCE',
         text='Kospi falls 3.5% and Sensex sheds 1,430 points on Monday as the AI '
              "rout spreads. US futures rebound after Friday's crash: S&P -3.7%, "
              'Nasdaq -5.3%, Nvidia -14%. Gold jumps; Bitcoin back to $61,386.'),
]

MIDS = [
    dict(n=4, kind='conflict', tag='UKRAINE WAR', badge='C',
         head='Dymer strike kills 10, toll 15',
         fact="Days after Putin vows a 'painful' reply, homes burn across Ukraine."),
    dict(n=5, kind='justice', tag='JUSTICE · MEXICO', badge='C',
         head="'El Chapo Isidro' held in Sinaloa",
         fact='FBI most-wanted drug lord held; arrest was Friday, confirmed Monday.'),
    dict(n=6, kind='politics', tag='POLITICS · USA', badge='R',
         head='Democrats take 258 House seats',
         fact='Largest House majority in 30+ years after the 3 November midterms.'),
    dict(n=7, kind='sport', tag='SPORT · MOTOGP', badge='C',
         head='Marquez wins eighth MotoGP title',
         fact='Levels Agostini in Portimao; Bezzecchi wins the race.'),
    dict(n=8, kind='sport', tag='SPORT · TENNIS', badge='C',
         head='Alcaraz wins ATP Finals title',
         fact='6-2, 7-6 in Turin over the world No. 1; final played Sunday.'),
    dict(n=9, kind='sport', tag='SPORT · FOOTBALL', badge='C',
         head='Liverpool thrash Man Utd 4-0',
         fact="Pochettino's nightmare debut at Anfield; Yoro sent off early."),
    dict(n=10, kind='disaster', tag='DISASTER · INDONESIA', badge='C',
         head='24 killed in Indonesia fire',
         fact='Blaze at Cikande, Banten; about 30 still missing in the wreckage.'),
    dict(n=11, kind='conflict', tag='CONFLICT · SUDAN', badge='R',
         head='Five children killed in Khartoum',
         fact='Strikes hit Khartoum and Omdurman as the war grinds on.'),
    dict(n=12, kind='politics', tag='POLITICS · TURKEY', badge='R',
         head='Istanbul rallies vs media takeover',
         fact='Protesters march against a government media takeover.'),
    dict(n=13, kind='society', tag='SOCIETY · GAZA', badge='R',
         head="Gaza war left 'toxic wasteland'",
         fact='Widespread contamination across Gaza, a new report finds.'),
]

# (number, headline, badge)
LIST = [
    (14, 'Ukraine drone cripples Russian ship off Libya', 'R'),
    (15, 'Russian cargo ship ablaze, drifts to Finland', 'R'),
    (16, 'Iran claims it downed a US MQ-9 drone', 'R'),
    (17, 'Denmark: Russia plotted to kill US rapper', 'R'),
    (18, 'Lebanese villagers return as ceasefire begins', 'C'),
    (19, 'Storm devastates Tupancireta, Brazil', 'C'),
    (20, 'Houthis claim Saudi refinery hit', 'R'),
    (21, '24 civilians killed in South Sudan attack', 'R'),
    (22, 'Bolsonaro in intensive care', 'R'),
    (23, 'Belgium airports to shut in strike', 'R'),
    (24, 'Delta outage delays 1,600+ flights', 'C'),
    (25, 'Trump signs law ending the penny', 'O'),
    (26, 'Nepal PM welcomed in Delhi by Modi', 'O'),
    (27, 'India keeps 3rd in Lowy Power Index', 'O'),
    (28, 'Indonesia seizes ship with rocket chemical', 'R'),
    (29, 'India v NZ first Test ends in draw', 'C'),
    (30, 'Thitikul wins third straight LPGA title', 'C'),
    (31, 'Price wins Grand Slam of Darts', 'C'),
    (32, 'Molly Meldrum, Australian music voice, dies', 'C'),
    (33, 'AI-assisted proof of Riemann claimed', 'R'),
    (34, "Volcanism 'explains' Challenger Deep", 'R'),
    (35, 'Star seen spiralling into giant companion', 'R'),
    (36, "Meta exec: superintelligence 'arriving'", 'R'),
    (37, 'US spy chief defends Trump on Putin', 'R'),
    (38, 'Ebola-area fighting disrupts response', 'R'),
    (39, 'West Bank medic attacks surge 350%', 'R'),
    (40, 'Thanksgiving storm: NYC faces rain, wind', 'R'),
]

TIMELINE = [
    ('04:00', 'COP31 ends with no deal in Antalya'),
    ('05:04', 'Iran says it downed a US drone'),
    ('05:45', 'Nepal PM welcomed in Delhi'),
    ('07:11', 'Democrats take 258 House seats'),
    ('07:32', 'Ukraine claims Merkury hit off Libya'),
    ('09:56', 'Sensex sheds 1,430 points'),
]

NUMBERS = [
    ('15', 'KILLED IN RUSSIAN ATTACKS ON UKRAINE'),
    ('-3.5%', 'KOSPI ON MONDAY'),
    ('258', 'DEMOCRAT HOUSE SEATS'),
    ('24', 'DEAD IN INDONESIA FACTORY FIRE'),
    ('2', 'TANKERS ABLAZE NEAR HORMUZ'),
    ('$61,386', 'BITCOIN ON MONDAY'),
]

REGION_COUNTS = 'Europe 10 · Asia 6 · Middle East 6 · Africa 4 · Americas 11 · Oceania 2 · Space 1'


def badge(cv, x, y, kind):
    """Small verification badge: coloured box with a white letter."""
    cv.fill(x, y, 15, 13, BADGE_COL[kind])
    cv.rect(x, y, 15, 13, INK, 1)
    cv.text(x + 5, y + 3, kind, 1, (250, 246, 236))


def badge_word(cv, x, y, kind, scale=1):
    """Badge as a coloured word (used in lead tag lines)."""
    w = text_width(BADGE_NAME[kind], scale) + 8
    cv.fill(x, y - 2, w, 11 * scale + 2, BADGE_COL[kind])
    cv.text(x + 4, y, BADGE_NAME[kind], scale, (250, 246, 236))
    return w


# -------------------------------------------------------------------- page
def build():
    cv = Canvas(W, H, PAPER)
    X, CW = 22, 980

    # top rule
    cv.fill(X, 10, CW, 3, INK)

    # kicker
    cv.text(X, 18, 'THE MONDAY WORLD', 2, RED)
    kr = '40 STORIES · 6 REGIONS · 11 FIELDS · ALL FROM THIS MONDAY'
    cv.text(X + CW - text_width(kr, 1), 20, kr, 1, INK)

    # masthead
    cv.text_centred(W // 2, 40, 'MONDAY 23 NOVEMBER 2026', 4, INK)
    cv.fill(X, 78, CW, 2, INK)

    # ---- timeline strip
    y = 88
    cv.fill(X, y, 118, 22, RED)
    cv.text(X + 8, y + 7, 'THE DAY IN UTC', 1, (250, 246, 236))
    slot_w = (CW - 118) // 6
    for i, (tm, lbl) in enumerate(TIMELINE):
        sx = X + 118 + i * slot_w
        cv.text(sx + 6, y + 2, tm, 2, RED_DK)
        cv.para(sx + 6, y + 18, lbl, 1, INK, slot_w - 10, leading=8)
        if i:
            cv.vline(sx, y + 2, 38, LIGHT)
    cv.hline(X, y + 44, CW, INK)

    # ---- numbers strip
    y = 140
    cv.fill(X, y, 158, 22, INK)
    cv.text(X + 8, y + 7, 'THE DAY IN NUMBERS', 1, (250, 246, 236))
    nw = (CW - 158) // 6
    for i, (num, lbl) in enumerate(NUMBERS):
        nx = X + 158 + i * nw
        cv.text_centred(nx + nw // 2, y + 2, num, 3, RED)
        cv.para(nx + 6, y + 26, lbl, 1, INK, nw - 12, leading=8)
        if i:
            cv.vline(nx, y + 2, 44, LIGHT)
    cv.hline(X, y + 50, CW, INK)

    # ---- three leads
    y = 196
    lw = (CW - 20) // 3
    lh_img = 132
    for i, st in enumerate(LEADS):
        lx = X + i * (lw + 10)
        cv.rect(lx, y, lw, 284, INK, 1)
        if st['kind'] == 'cop31':
            lead_cop31(cv, lx + 1, y + 1, lw - 2, lh_img)
        elif st['kind'] == 'hormuz':
            lead_hormuz(cv, lx + 1, y + 1, lw - 2, lh_img)
        else:
            lead_markets(cv, lx + 1, y + 1, lw - 2, lh_img)
        ty = y + lh_img + 8
        cv.text(lx + 8, ty, str(st['n']) + ' ' + st['tag'], 1, RED)
        bw = badge_word(cv, lx + lw - 8 - (text_width(BADGE_NAME[st['badge']], 1) + 8),
                        ty + 2, st['badge'])
        cv.text(lx + lw - 8 - text_width(st['src'], 1), ty + 14, st['src'], 1, GREY)
        hy = ty + 26
        hy = cv.para(lx + 8, hy, st['head'], 2, INK, lw - 16, leading=17)
        cv.para(lx + 8, hy + 4, st['text'], 1, INK, lw - 16, leading=9)

    # ---- ten mids, two columns x five rows
    y = 490
    mw = (CW - 10) // 2
    for i, st in enumerate(MIDS):
        col, row = i % 2, i // 2
        mx = X + col * (mw + 10)
        my = y + row * 48
        icon(cv, mx, my + 2, st['kind'])
        cv.text(mx + 48, my + 2, str(st['n']) + ' ' + st['tag'], 1, RED)
        badge(cv, mx + mw - 17, my + 2, st['badge'])
        cv.text(mx + 48, my + 15, st['head'], 2, INK)
        cv.text(mx + 48, my + 32, st['fact'], 1, INK)
        if row < 4:
            cv.hline(mx, my + 44, mw, LIGHT)

    # ---- map + also list
    y = 738
    cv.text(X, y, 'WHERE IT HAPPENED', 2, RED)
    cv.text(X + 348, y, 'ALSO ON MONDAY 23 NOVEMBER', 2, RED)
    my = y + 18
    draw_map(cv, X, my, 330, 160)
    cv.rect(X, my, 330, 160, INK, 1)
    cv.para(X, my + 166, REGION_COUNTS, 1, INK, 330, leading=9)
    # list in two columns
    col_w = (CW - 348 - 10) // 2
    for i, (n, head, b) in enumerate(LIST):
        col, row = i % 2, i // 2
        lx = X + 348 + col * (col_w + 10)
        ly = my + row * 14
        cv.text(lx, ly, str(n) + '.', 1, RED)
        cv.text(lx + 22, ly, head, 1, INK)
        badge(cv, lx + col_w - 17, ly - 1, b)

    # ---- date check
    y = 954
    cv.fill(X, y, CW, 28, (250, 232, 210))
    cv.rect(X, y, CW, 28, INK, 1)
    cv.fill(X, y, 92, 28, RED)
    cv.text(X + 8, y + 10, 'DATE CHECK', 1, (250, 246, 236))
    cv.text(X + 100, y + 3,
            'Left out — they broke before Monday: Friday’s Wall Street rout; the Sinaloa', 1, INK)
    cv.text(X + 100, y + 15,
            'arrest was Friday, confirmed Monday; COP31’s gavel fell Sunday, Monday is the fallout.', 1, INK)

    # ---- footer
    y = 988
    cv.text(X, y, 'Every story here happened or was first reported on Monday 23 November 2026.', 1, INK)
    cv.text(X, y + 10,
            'C = CONFIRMED (2+ outlets) · O = OFFICIAL (on the record) · R = REPORTED (one outlet).', 1, INK)
    cv.text(X + CW - text_width('Sources: AP, Reuters, AFP, BBC, CNN, Al Jazeera, The Hindu.', 1),
            y, 'Sources: AP, Reuters, AFP, BBC, CNN, Al Jazeera, The Hindu.', 1, INK)
    cv.text(X + CW - text_width('Original drawings.', 1), y + 10, 'Original drawings.', 1, INK)

    # bottom bar
    cv.fill(X, 1008, CW, 2, INK)
    cv.text_centred(W // 2, 1014, 'MONDAY 23 NOVEMBER 2026 · ONE DAY, ONE PICTURE', 1, INK)
    return cv


def main():
    out_dir = os.environ.get('MAKEFUN_OUTPUT_DIR', '/output')
    os.makedirs(out_dir, exist_ok=True)
    data = png_bytes(build())
    path = os.path.join(out_dir, 'entry.png')
    with open(path, 'wb') as f:
        f.write(data)
    print('wrote', path, len(data), 'bytes')


if __name__ == '__main__':
    main()
