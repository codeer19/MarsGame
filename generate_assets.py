#!/usr/bin/env python3
"""
MarsPixelAssets — Complete 2D Top-Down Pixel-Art Game Asset Generator
Designed for a Soul Knight-inspired scientifically grounded Mars exploration game.
All sprites are drawn directly on low-resolution native pixel grids (16x16, 24x24,
32x32, 48x48, 64x64) using a restrained 33-color 16-bit palette with hard pixel
clusters, crisp dark outlines, and zero anti-aliasing.
"""

import json
import math
import os
import random
import shutil
import zipfile
from pathlib import Path
from PIL import Image

# ==============================================================================
# 1. MASTER 33-COLOR 16-BIT INDIE PIXEL-ART PALETTE (RGBA, STRICTLY OPAQUE OR 0)
# ==============================================================================
PAL = {
    ".": (0, 0, 0, 0),            # Transparent
    "k": (24, 18, 28, 255),       # Deep charcoal-violet outline
    "w": (48, 24, 26, 255),       # Dark warm rust-brown outline/crevice
    # Martian Terrain Ramp (6 shades)
    "m0": (78, 32, 28, 255),      # Deep crater shadow
    "m1": (118, 46, 34, 255),     # Burnt sienna dark
    "m2": (158, 66, 44, 255),     # Classic rusty Mars red (base ground)
    "m3": (194, 92, 56, 255),     # Warm terracotta highlight
    "m4": (218, 126, 78, 255),    # Sunlit ochre dust
    "m5": (236, 166, 112, 255),   # Fine pale sandstone highlight
    # Martian Basalt & Rock Ramp (5 shades)
    "r0": (42, 36, 44, 255),      # Deep basalt shadow / sprite ground shadow
    "r1": (68, 56, 62, 255),      # Dark brown-slate rock
    "r2": (98, 82, 86, 255),      # Muted gray-brown rock mid
    "r3": (134, 114, 112, 255),   # Warm rock highlight
    "r4": (172, 148, 138, 255),   # Crisp top-edge rock glint
    # Astronaut Suit & Tech Metal Ramp (6 shades)
    "s0": (54, 64, 82, 255),      # Dark steel chassis/joints
    "s1": (92, 104, 126, 255),    # Muted steel mid
    "s2": (138, 150, 172, 255),   # Cool blue-gray suit shadow
    "s3": (192, 202, 218, 255),   # Suit light gray midtone
    "s4": (236, 242, 248, 255),   # Off-white suit primary
    "s5": (252, 254, 255, 255),   # Pure specular highlight
    # Visor & Cool Cyan Tech Ramp (4 shades)
    "v0": (18, 30, 58, 255),      # Deep navy visor base
    "v1": (36, 68, 128, 255),     # Cobalt visor mid
    "c0": (56, 168, 238, 255),    # Cyan scanner/visor reflection
    "c1": (164, 236, 255, 255),   # Ice-cyan bright glint
    # Orange Trim & Gold/Yellow Mineral Ramp (5 shades)
    "o0": (162, 60, 22, 255),     # Deep orange trim shadow
    "o1": (232, 106, 36, 255),    # NASA/indie orange trim base
    "y0": (214, 148, 28, 255),    # Warm amber/gold dark
    "y1": (248, 202, 56, 255),    # Saturated yellow crystal mid
    "y2": (255, 244, 148, 255),   # Pale yellow crystal highlight
    # Emerald Green Mineral & Bio/Radiation Ramp (3 shades)
    "g0": (26, 90, 56, 255),      # Deep emerald shadow
    "g1": (54, 172, 92, 255),     # Saturated green crystal mid
    "g2": (148, 240, 138, 255),   # Bright mint/radiation highlight
    # Amethyst Purple Rare Mineral Ramp (3 shades)
    "p0": (76, 32, 108, 255),     # Deep purple shadow
    "p1": (146, 64, 202, 255),    # Saturated purple crystal mid
    "p2": (220, 148, 255, 255),   # Bright lavender glint
    # Crimson Alert & Health Ramp (2 shades)
    "d0": (138, 26, 40, 255),     # Deep crimson shadow
    "d1": (232, 56, 70, 255),     # Bright red health/hazard
}

# Alternate suit skin color remappings (uses colors from the existing master palette!)
SKIN_PALETTES = {
    "default_white": {},
    "blue_explorer": {
        "s2": PAL["v1"],
        "s3": PAL["c0"],
        "s4": PAL["c1"],
        "o0": PAL["y0"],
        "o1": PAL["y1"],
    },
    "red_commander": {
        "s2": PAL["d0"],
        "s3": PAL["o0"],
        "s4": PAL["d1"],
        "o0": PAL["y0"],
        "o1": PAL["y1"],
    },
    "green_biosuit": {
        "s2": PAL["g0"],
        "s3": PAL["g1"],
        "s4": PAL["g2"],
        "o0": PAL["v1"],
        "o1": PAL["c0"],
    },
    "purple_vanguard": {
        "s2": PAL["p0"],
        "s3": PAL["p1"],
        "s4": PAL["p2"],
        "o0": PAL["y0"],
        "o1": PAL["y1"],
    },
}


# ==============================================================================
# 2. LOW-LEVEL PIXEL CANVAS PRIMITIVES (STRICTLY HARD-EDGED, NO ANTI-ALIASING)
# ==============================================================================
class PixelCanvas:
    def __init__(self, width: int, height: int, bg=(0, 0, 0, 0)):
        self.w = width
        self.h = height
        self.img = Image.new("RGBA", (width, height), bg)
        self.px = self.img.load()

    def set_px(self, x: int, y: int, col_key, palette_override=None):
        if 0 <= x < self.w and 0 <= y < self.h:
            if col_key == "." or col_key is None:
                return
            if isinstance(col_key, tuple):
                self.px[x, y] = col_key
            else:
                if palette_override and col_key in palette_override:
                    self.px[x, y] = palette_override[col_key]
                else:
                    self.px[x, y] = PAL[col_key]

    def rect(self, x: int, y: int, w: int, h: int, col_key, outline=None, palette_override=None):
        for dy in range(h):
            for dx in range(w):
                if outline and (dx == 0 or dx == w - 1 or dy == 0 or dy == h - 1):
                    self.set_px(x + dx, y + dy, outline, palette_override)
                else:
                    self.set_px(x + dx, y + dy, col_key, palette_override)

    def ellipse(self, cx: int, cy: int, rx: int, ry: int, col_key, outline=None, palette_override=None):
        for y in range(cy - ry - 1, cy + ry + 2):
            for x in range(cx - rx - 1, cx + rx + 2):
                nx = (x - cx) / max(0.5, rx)
                ny = (y - cy) / max(0.5, ry)
                dist = nx * nx + ny * ny
                if dist <= 1.0:
                    if outline:
                        out_nb = False
                        for ox, oy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                            nnx = (x + ox - cx) / max(0.5, rx)
                            nny = (y + oy - cy) / max(0.5, ry)
                            if nnx * nnx + nny * nny > 1.0:
                                out_nb = True
                                break
                        if out_nb:
                            self.set_px(x, y, outline, palette_override)
                        else:
                            self.set_px(x, y, col_key, palette_override)
                    else:
                        self.set_px(x, y, col_key, palette_override)

    def line(self, x0: int, y0: int, x1: int, y1: int, col_key, palette_override=None):
        """Bresenham integer pixel line (strictly hard-edged)."""
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_px(x0, y0, col_key, palette_override)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def polygon_points(self, pts, col_key, outline=None, palette_override=None):
        """Scanline fill polygon with optional hard pixel outline."""
        min_y = max(0, min(p[1] for p in pts))
        max_y = min(self.h - 1, max(p[1] for p in pts))
        n = len(pts)
        for y in range(min_y, max_y + 1):
            nodes = []
            j = n - 1
            for i in range(n):
                yi, yj = pts[i][1], pts[j][1]
                xi, xj = pts[i][0], pts[j][0]
                if (yi < y <= yj) or (yj < y <= yi):
                    nodes.append(int(round(xi + (y - yi) / (yj - yi) * (xj - xi))))
                j = i
            nodes.sort()
            for i in range(0, len(nodes) - 1, 2):
                for x in range(max(0, nodes[i]), min(self.w - 1, nodes[i + 1]) + 1):
                    self.set_px(x, y, col_key, palette_override)
        if outline:
            for i in range(n):
                p0 = pts[i]
                p1 = pts[(i + 1) % n]
                self.line(p0[0], p0[1], p1[0], p1[1], outline, palette_override)


# ==============================================================================
# 3. CATEGORY A: MAIN ASTRONAUT CHARACTER (32x32 NATIVE FRAMES)
# ==============================================================================
def draw_astronaut_frame(
    direction: str = "down",
    anim: str = "idle",
    frame_idx: int = 0,
    skin: str = "default_white",
) -> Image.Image:
    """
    Draws a coherent 32x32 top-down pixel-art astronaut sprite with opaque pixel shadow.
    """
    c = PixelCanvas(32, 32)
    po = SKIN_PALETTES.get(skin, {})

    if anim == "defeated" and frame_idx >= 2:
        c.ellipse(16, 24, 10, 3, "r0")
        c.rect(7, 17, 7, 6, "s2", outline="k", palette_override=po)
        c.rect(11, 18, 9, 7, "s4", outline="k", palette_override=po)
        c.rect(12, 19, 7, 2, "s3", palette_override=po)
        c.line(18, 19, 18, 23, "o1", palette_override=po)
        c.rect(19, 19, 6, 3, "s3", outline="k", palette_override=po)
        c.rect(19, 22, 6, 3, "s2", outline="k", palette_override=po)
        c.rect(24, 19, 3, 6, "s0", outline="k", palette_override=po)
        c.ellipse(9, 20, 5, 5, "s4", outline="k", palette_override=po)
        c.rect(6, 18, 5, 5, "v0", outline="k", palette_override=po)
        c.set_px(7, 19, "d1")
        if frame_idx == 2:
            c.set_px(7, 12, "y1")
            c.set_px(11, 11, "c1")
            c.set_px(9, 13, "y2")
        else:
            c.set_px(8, 11, "c0")
            c.set_px(12, 12, "y1")
        return c.img

    bob_y = 0
    lean_x = 0
    left_leg_dy = 0
    right_leg_dy = 0
    left_leg_dx = 0
    right_leg_dx = 0
    left_arm_dy = 0
    right_arm_dy = 0
    right_arm_dx = 0

    if anim == "idle":
        bob_y = 1 if frame_idx % 2 == 1 else 0
    elif anim == "walk":
        if frame_idx == 0:
            bob_y = -1
            left_leg_dy = -2
            right_leg_dy = 1
            left_arm_dy = 1
            right_arm_dy = -1
            if direction in ("left", "right"):
                left_leg_dx = -2
                right_leg_dx = 2
        elif frame_idx == 2:
            bob_y = -1
            left_leg_dy = 1
            right_leg_dy = -2
            left_arm_dy = -1
            right_arm_dy = 1
            if direction in ("left", "right"):
                left_leg_dx = 2
                right_leg_dx = -2
    elif anim == "run":
        if frame_idx == 0:
            bob_y = -2
            left_leg_dy = -3
            right_leg_dy = 1
            left_arm_dy = 2
            right_arm_dy = -2
            if direction == "left":
                lean_x = -1
                left_leg_dx = -3
                right_leg_dx = 3
            elif direction == "right":
                lean_x = 1
                left_leg_dx = -3
                right_leg_dx = 3
        elif frame_idx == 1:
            lean_x = -1 if direction == "left" else (1 if direction == "right" else 0)
        elif frame_idx == 2:
            bob_y = -2
            left_leg_dy = 1
            right_leg_dy = -3
            left_arm_dy = -2
            right_arm_dy = 2
            if direction == "left":
                lean_x = -1
                left_leg_dx = 3
                right_leg_dx = -3
            elif direction == "right":
                lean_x = 1
                left_leg_dx = 3
                right_leg_dx = -3
        elif frame_idx == 3:
            lean_x = -1 if direction == "left" else (1 if direction == "right" else 0)
    elif anim == "collect":
        if frame_idx in (1, 2):
            bob_y = 2
            right_arm_dy = 2
        elif frame_idx == 3:
            bob_y = -1
            right_arm_dy = -2
    elif anim == "scan":
        right_arm_dy = -1
    elif anim == "tool":
        right_arm_dy = -1
        if frame_idx % 2 == 1:
            right_arm_dx = 1 if direction != "left" else -1
    elif anim == "hurt":
        bob_y = -1 if frame_idx == 0 else 1
        lean_x = -1 if direction == "right" else (1 if direction == "left" else 0)
        left_arm_dy = -2
        right_arm_dy = -2
    elif anim == "defeated":
        bob_y = 2 if frame_idx == 0 else 4
        left_arm_dy = 1
        right_arm_dy = 1

    cx = 16 + lean_x
    hy = 10 + bob_y
    ty = 18 + bob_y

    # 1. Crisp pixel-art ground shadow (opaque r0)
    c.ellipse(16, 29, 6, 2, "r0")

    if anim == "run" and frame_idx in (0, 2):
        dust_x = 22 if direction == "left" else (10 if direction == "right" else 16)
        c.set_px(dust_x, 28, "m4")
        c.set_px(dust_x + 1, 27, "m5")
        c.set_px(dust_x - 1, 29, "m3")

    # 2. Backpack (behind torso for down, left, right)
    if direction == "down":
        c.rect(cx - 7, ty - 2, 14, 5, "s2", outline="k", palette_override=po)
        c.set_px(cx - 5, ty - 3, "s0")
        c.set_px(cx - 5, ty - 4, "o1", palette_override=po)
    elif direction == "left":
        c.rect(cx + 2, ty - 2, 6, 9, "s3", outline="k", palette_override=po)
        c.rect(cx + 3, ty, 4, 5, "s2", palette_override=po)
        c.line(cx + 4, ty + 1, cx + 6, ty + 1, "o1", palette_override=po)
        c.set_px(cx + 5, ty - 3, "s0")
        c.set_px(cx + 5, ty - 4, "c0")
    elif direction == "right":
        c.rect(cx - 8, ty - 2, 6, 9, "s3", outline="k", palette_override=po)
        c.rect(cx - 7, ty, 4, 5, "s2", palette_override=po)
        c.line(cx - 6, ty + 1, cx - 4, ty + 1, "o1", palette_override=po)
        c.set_px(cx - 5, ty - 3, "s0")
        c.set_px(cx - 5, ty - 4, "c0")

    # 3. Legs & Boots
    ly_base = 24 + (1 if anim == "collect" and frame_idx in (1, 2) else 0)
    if direction in ("down", "up"):
        ll_y = ly_base + left_leg_dy
        c.rect(cx - 5, ll_y, 4, 4, "s3", outline="k", palette_override=po)
        c.rect(cx - 5, ll_y + 3, 4, 3, "s0", outline="k", palette_override=po)
        c.line(cx - 4, ll_y + 3, cx - 3, ll_y + 3, "o1", palette_override=po)
        rl_y = ly_base + right_leg_dy
        c.rect(cx + 1, rl_y, 4, 4, "s3", outline="k", palette_override=po)
        c.rect(cx + 1, rl_y + 3, 4, 3, "s0", outline="k", palette_override=po)
        c.line(cx + 2, rl_y + 3, cx + 3, rl_y + 3, "o1", palette_override=po)
    else:
        back_dx = right_leg_dx
        front_dx = left_leg_dx
        back_dy = min(0, right_leg_dy)
        front_dy = min(0, left_leg_dy)
        c.rect(cx - 2 + back_dx, ly_base + back_dy, 4, 4, "s2", outline="k", palette_override=po)
        c.rect(cx - 2 + back_dx, ly_base + back_dy + 3, 4, 3, "s0", outline="k", palette_override=po)
        c.rect(cx - 2 + front_dx, ly_base + front_dy, 4, 4, "s4", outline="k", palette_override=po)
        c.rect(cx - 2 + front_dx, ly_base + front_dy + 3, 4, 3, "s0", outline="k", palette_override=po)
        c.line(cx - 1 + front_dx, ly_base + front_dy + 3, cx + front_dx, ly_base + front_dy + 3, "o1", palette_override=po)

    # 4. Torso
    if direction in ("down", "up"):
        c.rect(cx - 6, ty - 1, 12, 8, "s4", outline="k", palette_override=po)
        c.line(cx - 5, ty + 5, cx + 4, ty + 5, "s2", palette_override=po)
        c.line(cx - 5, ty + 4, cx + 4, ty + 4, "o1", palette_override=po)
        c.set_px(cx, ty + 4, "s0")
        if direction == "down":
            c.rect(cx - 3, ty + 1, 6, 3, "s3", palette_override=po)
            c.set_px(cx - 2, ty + 2, "c0")
            c.set_px(cx + 1, ty + 2, "o1", palette_override=po)
            c.line(cx - 5, ty, cx - 4, ty, "o1", palette_override=po)
            c.line(cx + 3, ty, cx + 4, ty, "o1", palette_override=po)
    else:
        c.rect(cx - 4, ty - 1, 8, 8, "s4", outline="k", palette_override=po)
        c.line(cx - 3, ty + 4, cx + 2, ty + 4, "o1", palette_override=po)
        c.line(cx - 3, ty + 5, cx + 2, ty + 5, "s2", palette_override=po)

    # 5. Backpack when facing UP
    if direction == "up":
        c.rect(cx - 6, ty - 2, 12, 8, "s3", outline="k", palette_override=po)
        c.rect(cx - 4, ty - 1, 8, 5, "s2", palette_override=po)
        c.rect(cx - 3, ty, 2, 4, "s4", palette_override=po)
        c.rect(cx + 1, ty, 2, 4, "s4", palette_override=po)
        c.line(cx - 4, ty + 4, cx + 3, ty + 4, "o1", palette_override=po)
        c.set_px(cx, ty + 1, "c0")
        c.set_px(cx - 4, ty - 3, "s0")
        c.set_px(cx - 4, ty - 4, "o1", palette_override=po)

    # 6. Arms & Gloves
    if direction in ("down", "up"):
        la_y = ty + left_arm_dy
        c.rect(cx - 8, la_y, 3, 6, "s4", outline="k", palette_override=po)
        c.set_px(cx - 7, la_y + 3, "o1", palette_override=po)
        c.rect(cx - 8, la_y + 4, 3, 2, "s0", outline="k", palette_override=po)
        ra_y = ty + right_arm_dy
        ra_x = cx + 5 + right_arm_dx
        c.rect(ra_x, ra_y, 3, 6, "s4", outline="k", palette_override=po)
        c.set_px(ra_x + 1, ra_y + 3, "o1", palette_override=po)
        c.rect(ra_x, ra_y + 4, 3, 2, "s0", outline="k", palette_override=po)
    elif direction == "left":
        fa_y = ty + right_arm_dy
        fa_x = cx - 3 + right_arm_dx
        c.rect(fa_x, fa_y, 4, 6, "s4", outline="k", palette_override=po)
        c.line(fa_x + 1, fa_y + 3, fa_x + 2, fa_y + 3, "o1", palette_override=po)
        c.rect(fa_x, fa_y + 4, 4, 2, "s0", outline="k", palette_override=po)
    elif direction == "right":
        fa_y = ty + right_arm_dy
        fa_x = cx - 1 + right_arm_dx
        c.rect(fa_x, fa_y, 4, 6, "s4", outline="k", palette_override=po)
        c.line(fa_x + 1, fa_y + 3, fa_x + 2, fa_y + 3, "o1", palette_override=po)
        c.rect(fa_x, fa_y + 4, 4, 2, "s0", outline="k", palette_override=po)

    # 7. Helmet
    c.ellipse(cx, hy, 7, 6, "s4", outline="k", palette_override=po)
    c.line(cx - 3, hy - 4, cx + 1, hy - 4, "s5", palette_override=po)
    c.line(cx - 4, hy + 4, cx + 4, hy + 4, "s2", palette_override=po)
    c.line(cx - 1, hy - 5, cx + 1, hy - 5, "o1", palette_override=po)

    if direction == "down":
        c.rect(cx - 8, hy - 1, 2, 3, "o1", outline="k", palette_override=po)
        c.rect(cx + 6, hy - 1, 2, 3, "o1", outline="k", palette_override=po)
        c.rect(cx - 5, hy - 2, 10, 6, "v0", outline="k")
        c.rect(cx - 4, hy - 1, 8, 4, "v1" if anim != "hurt" else "d0")
        c.rect(cx - 3, hy, 6, 3, "v0" if anim != "hurt" else "d1")
        c.line(cx - 3, hy - 1, cx - 1, hy - 1, "c0")
        c.set_px(cx - 3, hy, "c1")
        c.set_px(cx + 2, hy + 1, "c0")
    elif direction == "up":
        c.rect(cx - 8, hy - 1, 2, 3, "o1", outline="k", palette_override=po)
        c.rect(cx + 6, hy - 1, 2, 3, "o1", outline="k", palette_override=po)
        c.rect(cx - 3, hy - 1, 6, 4, "s3", palette_override=po)
        c.line(cx - 2, hy + 1, cx + 2, hy + 1, "o1", palette_override=po)
    elif direction == "left":
        c.rect(cx + 1, hy - 1, 3, 3, "o1", outline="k", palette_override=po)
        c.rect(cx - 7, hy - 2, 7, 6, "v0", outline="k")
        c.rect(cx - 6, hy - 1, 5, 4, "v1" if anim != "hurt" else "d1")
        c.rect(cx - 5, hy, 4, 3, "v0")
        c.line(cx - 5, hy - 1, cx - 3, hy - 1, "c1")
        c.set_px(cx - 5, hy, "c0")
    elif direction == "right":
        c.rect(cx - 4, hy - 1, 3, 3, "o1", outline="k", palette_override=po)
        c.rect(cx, hy - 2, 7, 6, "v0", outline="k")
        c.rect(cx + 1, hy - 1, 5, 4, "v1" if anim != "hurt" else "d1")
        c.rect(cx + 1, hy, 4, 3, "v0")
        c.line(cx + 3, hy - 1, cx + 5, hy - 1, "c1")
        c.set_px(cx + 5, hy, "c0")

    # 8. Interaction Props / Effects
    if anim == "scan":
        sx = cx + 7 if direction != "left" else cx - 9
        sy = ty + 1
        c.rect(sx, sy, 3, 3, "s0", outline="k")
        c.set_px(sx + (2 if direction != "left" else 0), sy + 1, "c1")
        wave_r = 2 + frame_idx * 2
        wx = sx + (3 if direction != "left" else -1)
        for dy in range(-2, 3):
            c.set_px(wx + (wave_r if direction != "left" else -wave_r), sy + 1 + dy, "c0")
        c.set_px(wx + ((wave_r - 1) if direction != "left" else -(wave_r - 1)), sy + 1, "c1")
    elif anim == "collect":
        gx = cx + (5 if direction == "right" else (-6 if direction == "left" else 4))
        gy = 25 if frame_idx < 2 else (22 if frame_idx == 2 else 18)
        c.rect(gx, gy, 4, 5, "c0", outline="k")
        c.set_px(gx + 1, gy + 1, "c1")
        if frame_idx >= 2:
            c.set_px(gx - 1, gy - 1, "y2")
            c.set_px(gx + 4, gy, "c1")
    elif anim == "tool":
        tx_tool = cx + (6 if direction != "left" else -10)
        ty_tool = ty + 2
        c.rect(tx_tool, ty_tool, 5, 3, "o1", outline="k")
        tip_x = tx_tool + (5 if direction != "left" else -2)
        c.line(tip_x, ty_tool + 1, tip_x + (2 if direction != "left" else -2), ty_tool + 1, "c1")
        if frame_idx % 2 == 1:
            sp_x = tip_x + (3 if direction != "left" else -3)
            c.set_px(sp_x, ty_tool - 1, "y2")
            c.set_px(sp_x + (1 if direction != "left" else -1), ty_tool + 2, "y1")
            c.set_px(sp_x, ty_tool + 1, "c1")
    elif anim == "hurt":
        c.set_px(cx - 8, hy - 5, "d1")
        c.set_px(cx - 7, hy - 4, "y2")
        c.set_px(cx + 8, hy - 5, "d1")
        c.set_px(cx + 7, hy - 4, "y2")

    return c.img


# ==============================================================================
# 4. CATEGORY B: MARS TERRAIN TILESET (32 DISTINCT 32x32 TILES)
# ==============================================================================
def make_base_mars_tile(seed: int, base_col="m2", dark_col="m1", light_col="m3", speck_density=14) -> PixelCanvas:
    rng = random.Random(seed)
    c = PixelCanvas(32, 32, PAL[base_col])
    for _ in range(speck_density):
        x = rng.randint(0, 30)
        y = rng.randint(0, 30)
        col = dark_col if rng.random() < 0.55 else light_col
        w = rng.choice([1, 2, 2, 3])
        h = rng.choice([1, 1, 2])
        for dy in range(h):
            for dx in range(w):
                c.set_px((x + dx) % 32, (y + dy) % 32, col)
    return c


def draw_rock_cluster(c: PixelCanvas, cx: int, cy: int, rx: int, ry: int):
    c.ellipse(cx + 1, cy + 2, rx, ry, "m0")
    c.ellipse(cx, cy, rx, ry, "r2", outline="k")
    c.ellipse(cx - 1, cy - 1, max(1, rx - 2), max(1, ry - 2), "r3")
    c.line(cx - max(1, rx - 2), cy - max(1, ry - 2), cx, cy - max(1, ry - 2), "r4")
    c.line(cx - rx + 2, cy + ry - 1, cx + rx - 2, cy + ry - 1, "r0")


def generate_terrain_tiles() -> dict:
    tiles = {}

    # 1. Plain red Martian ground
    t1 = make_base_mars_tile(101, "m2", "m1", "m3", 12)
    tiles["01_plain_red_ground"] = (t1.img, {"category": "ground", "walkable": True, "description": "Plain red Martian ground"})

    # 2. Ground with sparse small stones
    t2 = make_base_mars_tile(102, "m2", "m1", "m3", 14)
    for sx, sy in [(7, 9), (22, 6), (14, 23), (26, 20)]:
        t2.rect(sx, sy + 1, 3, 2, "m0")
        t2.rect(sx, sy, 3, 2, "r2", outline="w")
        t2.set_px(sx + 1, sy, "r3")
    tiles["02_sparse_small_stones"] = (t2.img, {"category": "ground", "walkable": True, "description": "Ground with sparse small stones"})

    # 3. Dense rocky ground
    t3 = make_base_mars_tile(103, "m1", "m0", "m2", 18)
    for sx, sy, rw, rh in [(4, 5, 4, 3), (15, 4, 5, 3), (24, 9, 4, 3), (8, 15, 5, 4), (20, 17, 5, 3), (5, 25, 4, 3), (16, 25, 6, 4), (26, 26, 3, 3)]:
        t3.rect(sx, sy + 1, rw, rh, "m0")
        t3.rect(sx, sy, rw, rh, "r2", outline="k")
        t3.line(sx + 1, sy + 1, sx + rw - 2, sy + 1, "r3")
    tiles["03_dense_rocky_ground"] = (t3.img, {"category": "ground", "walkable": True, "description": "Dense rocky ground"})

    # 4. Sand or fine Martian dust (rippled wind dunes)
    t4 = make_base_mars_tile(104, "m4", "m3", "m5", 10)
    for ry in range(4, 32, 6):
        for x in range(32):
            wave = int(round(math.sin(x * math.pi / 8.0)))
            t4.set_px(x, (ry + wave) % 32, "m5")
            t4.set_px(x, (ry + wave + 1) % 32, "m3")
    tiles["04_fine_martian_sand"] = (t4.img, {"category": "sand", "walkable": True, "description": "Sand or fine Martian dust with wind ripples"})

    # 5. Fine reddish soil
    t5 = make_base_mars_tile(105, "m1", "m0", "m2", 24)
    for sx, sy in [(6, 6), (19, 11), (11, 21), (25, 25), (27, 5), (4, 24)]:
        t5.rect(sx, sy, 2, 2, "m3")
    tiles["05_fine_reddish_soil"] = (t5.img, {"category": "soil", "walkable": True, "description": "Fine dark reddish iron-rich soil"})

    # 6. Small isolated rocks
    t6 = make_base_mars_tile(106, "m2", "m1", "m3", 12)
    draw_rock_cluster(t6, 10, 11, 4, 3)
    draw_rock_cluster(t6, 22, 21, 5, 3)
    tiles["06_small_isolated_rocks"] = (t6.img, {"category": "rock", "walkable": True, "description": "Small isolated basalt rocks"})

    # 7. Large boulders
    t7 = make_base_mars_tile(107, "m2", "m1", "m3", 12)
    draw_rock_cluster(t7, 15, 16, 10, 8)
    draw_rock_cluster(t7, 23, 22, 5, 4)
    tiles["07_large_boulders"] = (t7.img, {"category": "obstacle", "walkable": False, "description": "Large impassable Martian boulders"})

    # 8. Crater floor
    t8 = make_base_mars_tile(108, "m0", "w", "m1", 16)
    for r in [11, 7]:
        for a in range(0, 360, 15):
            rad = math.radians(a)
            t8.set_px(int(16 + r * math.cos(rad)), int(16 + r * math.sin(rad)), "m1")
    tiles["08_crater_floor"] = (t8.img, {"category": "crater", "walkable": True, "description": "Recessed dark crater floor"})

    # 9. Crater rim
    t9 = make_base_mars_tile(109, "m2", "m1", "m3", 10)
    t9.rect(0, 14, 32, 18, "m0")
    for x in range(32):
        arch_y = int(10 + 4 * math.sin(x * math.pi / 31.0))
        for y in range(arch_y, 32):
            t9.set_px(x, y, "m0" if y > arch_y + 4 else "m1")
        t9.set_px(x, arch_y - 2, "m4")
        t9.set_px(x, arch_y - 1, "m5")
        t9.set_px(x, arch_y, "k")
        t9.set_px(x, arch_y + 1, "r1")
        t9.set_px(x, arch_y + 2, "w")
    tiles["09_crater_rim"] = (t9.img, {"category": "crater", "walkable": False, "description": "Elevated crater rim edge"})

    # 10. Cliff top
    t10 = make_base_mars_tile(110, "m3", "m2", "m4", 12)
    for x in range(32):
        lip = 24 + (1 if (x // 4) % 2 == 0 else 0)
        t10.set_px(x, lip - 2, "m5")
        t10.set_px(x, lip - 1, "r4")
        t10.set_px(x, lip, "k")
        for y in range(lip + 1, 32):
            t10.set_px(x, y, "r1" if (x // 6) % 2 == 0 else "r2")
        if x % 7 == 0:
            t10.line(x, lip + 1, x, 31, "k")
    tiles["10_cliff_top"] = (t10.img, {"category": "cliff", "walkable": False, "description": "Cliff top rocky lip"})

    # 11. Cliff side or vertical wall
    t11 = PixelCanvas(32, 32, PAL["r1"])
    for y in range(32):
        for x in range(32):
            col = "r2" if ((x + y // 4) // 5) % 2 == 0 else "r1"
            if y in (8, 18, 27):
                col = "r0"
            elif y in (9, 19):
                col = "r3"
            t11.set_px(x, y, col)
    for vx in [6, 15, 24]:
        t11.line(vx, 0, vx + 1, 31, "k")
    t11.rect(0, 28, 32, 4, "m0")
    t11.line(0, 28, 31, 28, "k")
    tiles["11_cliff_side_wall"] = (t11.img, {"category": "cliff", "walkable": False, "description": "Stratified vertical cliff wall"})

    # 12. Cliff corner
    t12 = make_base_mars_tile(112, "m2", "m1", "m3", 10)
    t12.rect(8, 0, 24, 24, "m3")
    t12.line(8, 0, 8, 22, "k")
    t12.line(9, 0, 9, 22, "m5")
    t12.line(8, 22, 31, 22, "k")
    t12.line(9, 21, 31, 21, "r4")
    t12.rect(8, 23, 24, 9, "r1", outline="k")
    for vx in [14, 22, 28]:
        t12.line(vx, 23, vx, 30, "r0")
    tiles["12_cliff_corner"] = (t12.img, {"category": "cliff", "walkable": False, "description": "Cliff outer left corner transition"})

    # 13. Uphill slope
    t13 = make_base_mars_tile(113, "m2", "m1", "m3", 10)
    for step_y in [6, 13, 20, 27]:
        t13.line(2, step_y - 1, 29, step_y - 1, "m4")
        t13.line(2, step_y, 29, step_y, "m0")
        t13.line(4, step_y + 1, 27, step_y + 1, "m1")
    tiles["13_uphill_slope"] = (t13.img, {"category": "slope", "walkable": True, "description": "Terraced uphill Martian slope"})

    # 14. Downhill slope
    t14 = make_base_mars_tile(114, "m1", "m0", "m2", 10)
    for step_y in [5, 12, 19, 26]:
        t14.line(3, step_y, 28, step_y, "w")
        t14.line(3, step_y + 1, 28, step_y + 1, "m3")
        for sx in range(5, 28, 6):
            t14.set_px(sx, step_y + 2, "r2")
    tiles["14_downhill_slope"] = (t14.img, {"category": "slope", "walkable": True, "description": "Scree downhill Martian slope"})

    # 15. Broken rocky ridge
    t15 = make_base_mars_tile(115, "m2", "m1", "m3", 12)
    pts = [(2, 24), (8, 10), (14, 16), (20, 6), (28, 18), (30, 26)]
    for i in range(len(pts) - 1):
        draw_rock_cluster(t15, (pts[i][0] + pts[i + 1][0]) // 2, (pts[i][1] + pts[i + 1][1]) // 2, 5, 4)
    tiles["15_broken_rocky_ridge"] = (t15.img, {"category": "ridge", "walkable": False, "description": "Jagged broken rocky ridge"})

    # 16. Rubble field
    t16 = make_base_mars_tile(116, "m2", "m1", "m3", 16)
    rng16 = random.Random(116)
    for _ in range(18):
        rx = rng16.randint(2, 27)
        ry = rng16.randint(2, 27)
        rw = rng16.randint(2, 4)
        rh = rng16.randint(2, 3)
        t16.rect(rx, ry, rw, rh, rng16.choice(["r1", "r2", "r3"]), outline="k")
    tiles["16_rubble_field"] = (t16.img, {"category": "rubble", "walkable": True, "description": "Rough impact rubble field"})

    # 17. Dusty path (horizontal)
    t17 = make_base_mars_tile(117, "m2", "m1", "m3", 10)
    t17.rect(0, 7, 32, 18, "m4")
    t17.rect(0, 10, 32, 12, "m5")
    for x in range(32):
        t17.set_px(x, 7 + (x % 3 == 0), "m3")
        t17.set_px(x, 24 - (x % 4 == 0), "m1")
        if x % 4 == 0:
            t17.rect(x, 11, 2, 2, "m3")
            t17.rect(x, 19, 2, 2, "m3")
    tiles["17_dusty_path"] = (t17.img, {"category": "path", "walkable": True, "description": "Compacted dusty rover/explorer path"})

    # 18. Ancient rock formation
    t18 = make_base_mars_tile(118, "m2", "m1", "m3", 12)
    t18.ellipse(16, 25, 11, 4, "m0")
    t18.rect(7, 14, 18, 11, "r1", outline="k")
    t18.rect(9, 9, 14, 7, "r2", outline="k")
    t18.rect(11, 5, 10, 6, "r3", outline="k")
    t18.line(12, 6, 19, 6, "r4")
    tiles["18_ancient_rock_formation"] = (t18.img, {"category": "formation", "walkable": False, "description": "Layered ancient Martian mesa outcrop"})

    # 19. Blue mineral-bearing rock
    t19 = make_base_mars_tile(119, "m2", "m1", "m3", 12)
    draw_rock_cluster(t19, 16, 17, 10, 8)
    for cx, cy in [(12, 14), (16, 12), (20, 16), (14, 19), (18, 15)]:
        t19.rect(cx, cy, 3, 3, "c0", outline="v0")
        t19.set_px(cx + 1, cy + 1, "c1")
    tiles["19_blue_mineral_rock"] = (t19.img, {"category": "mineral_node", "walkable": False, "description": "Basalt outcrop rich in blue azurite/cobalt crystals"})

    # 20. Yellow mineral-bearing rock
    t20 = make_base_mars_tile(120, "m2", "m1", "m3", 12)
    draw_rock_cluster(t20, 16, 17, 10, 8)
    for cx, cy in [(11, 15), (15, 12), (19, 14), (16, 18), (21, 18)]:
        t20.rect(cx, cy, 3, 3, "y1", outline="o0")
        t20.set_px(cx + 1, cy + 1, "y2")
    tiles["20_yellow_mineral_rock"] = (t20.img, {"category": "mineral_node", "walkable": False, "description": "Basalt outcrop rich in yellow sulfur/heliodor veins"})

    # 21. Greenish mineral-bearing rock
    t21 = make_base_mars_tile(121, "m2", "m1", "m3", 12)
    draw_rock_cluster(t21, 16, 17, 10, 8)
    for cx, cy in [(12, 13), (17, 13), (14, 17), (19, 17), (16, 15)]:
        t21.rect(cx, cy, 3, 3, "g1", outline="g0")
        t21.set_px(cx + 1, cy + 1, "g2")
    tiles["21_green_mineral_rock"] = (t21.img, {"category": "mineral_node", "walkable": False, "description": "Basalt outcrop rich in green Martian olivine"})

    # 22. Unusual geological formation
    t22 = make_base_mars_tile(122, "m2", "m1", "m3", 10)
    for bx, by, bh in [(8, 14, 10), (14, 10, 14), (20, 12, 12), (11, 18, 9), (17, 17, 10)]:
        t22.rect(bx, by, 6, bh, "r2", outline="k")
        t22.rect(bx + 1, by + 1, 4, 3, "r4")
        t22.set_px(bx + 2, by + 2, "p1")
    tiles["22_unusual_geological_formation"] = (t22.img, {"category": "formation", "walkable": False, "description": "Hexagonal columnar basalt geological anomaly"})

    # 23. Ice-bearing patch
    t23 = make_base_mars_tile(123, "m2", "m1", "m3", 10)
    t23.ellipse(16, 16, 12, 10, "s3", outline="v1")
    t23.ellipse(15, 15, 9, 7, "c1")
    t23.ellipse(14, 14, 5, 4, "s5")
    t23.line(10, 16, 20, 12, "c0")
    t23.line(12, 20, 22, 17, "c0")
    tiles["23_ice_bearing_patch"] = (t23.img, {"category": "science_surface", "walkable": True, "description": "Exposed subsurface water-ice permafrost patch"})

    # 24. Metal-rich or scientifically interesting surface
    t24 = make_base_mars_tile(124, "m2", "m1", "m3", 12)
    t24.ellipse(16, 16, 11, 9, "s0", outline="k")
    t24.ellipse(15, 15, 8, 6, "s1")
    for mx, my in [(12, 13), (17, 12), (14, 17), (19, 16)]:
        t24.rect(mx, my, 3, 2, "s4")
        t24.set_px(mx, my, "c1")
    tiles["24_metal_rich_surface"] = (t24.img, {"category": "science_surface", "walkable": True, "description": "Iron-nickel meteorite-enriched metallic surface"})

    # 25..32: Seamless Edge, Corner & Path Variants
    t25 = t12.img.transpose(Image.FLIP_LEFT_RIGHT)
    tiles["25_cliff_corner_right"] = (t25, {"category": "cliff", "walkable": False, "description": "Cliff outer right corner transition"})

    t26 = make_base_mars_tile(126, "m2", "m1", "m3", 10)
    t26.rect(8, 0, 24, 32, "m3")
    t26.line(8, 0, 8, 31, "k")
    t26.line(9, 0, 9, 31, "r4")
    t26.line(7, 0, 7, 31, "m0")
    tiles["26_cliff_edge_left"] = (t26.img, {"category": "cliff", "walkable": False, "description": "Cliff left vertical boundary"})

    t27 = t26.img.transpose(Image.FLIP_LEFT_RIGHT)
    tiles["27_cliff_edge_right"] = (t27, {"category": "cliff", "walkable": False, "description": "Cliff right vertical boundary"})

    t28 = t9.img.transpose(Image.FLIP_TOP_BOTTOM)
    tiles["28_crater_rim_bottom"] = (t28, {"category": "crater", "walkable": False, "description": "Crater southern rim edge"})

    t29 = t9.img.transpose(Image.ROTATE_90)
    tiles["29_crater_rim_left"] = (t29, {"category": "crater", "walkable": False, "description": "Crater western rim edge"})

    t30 = t9.img.transpose(Image.ROTATE_270)
    tiles["30_crater_rim_right"] = (t30, {"category": "crater", "walkable": False, "description": "Crater eastern rim edge"})

    t31 = t17.img.transpose(Image.ROTATE_90)
    tiles["31_dusty_path_vertical"] = (t31, {"category": "path", "walkable": True, "description": "Compacted dusty path vertical"})

    t32 = make_base_mars_tile(132, "m2", "m1", "m3", 10)
    t32.rect(0, 7, 32, 18, "m4")
    t32.rect(7, 0, 18, 32, "m4")
    t32.rect(0, 10, 32, 12, "m5")
    t32.rect(10, 0, 12, 32, "m5")
    tiles["32_dusty_path_cross"] = (t32.img, {"category": "path", "walkable": True, "description": "Dusty rover path 4-way intersection"})

    return tiles


# ==============================================================================
# 5. CATEGORY C: MINERALS & SCIENTIFIC COLLECTIBLES (24x24 NATIVE SPRITES)
# ==============================================================================
def draw_crystal_sprite(c_dark: str, c_mid: str, c_bright: str, variant: int = 0) -> Image.Image:
    c = PixelCanvas(24, 24)
    c.ellipse(12, 20, 7, 2, "r0")
    c.rect(6, 17, 12, 4, "r1", outline="k")
    c.line(7, 18, 16, 18, "r3")
    pts_main = [(12, 3), (16, 9), (15, 18), (9, 18), (8, 9)]
    c.polygon_points(pts_main, c_mid, outline="k")
    c.line(12, 4, 10, 17, c_bright)
    c.line(12, 4, 14, 17, c_dark)
    pts_left = [(5, 9), (9, 12), (9, 18), (5, 18), (4, 13)]
    c.polygon_points(pts_left, c_dark, outline="k")
    c.line(6, 10, 7, 16, c_mid)
    pts_right = [(19, 8 if variant % 2 == 0 else 10), (20, 13), (18, 18), (15, 18), (15, 12)]
    c.polygon_points(pts_right, c_mid, outline="k")
    c.line(18, 10, 17, 16, c_bright)
    c.set_px(11, 6, "s5")
    c.set_px(6, 11, "s5")
    return c.img


def generate_minerals_and_items():
    minerals = {}
    items = {}

    minerals["blue_mineral_crystal"] = draw_crystal_sprite("v1", "c0", "c1", 0)
    minerals["yellow_mineral_crystal"] = draw_crystal_sprite("y0", "y1", "y2", 1)
    minerals["green_mineral_crystal"] = draw_crystal_sprite("g0", "g1", "g2", 0)
    minerals["purple_rare_mineral"] = draw_crystal_sprite("p0", "p1", "p2", 1)

    c5 = PixelCanvas(24, 24)
    c5.ellipse(12, 19, 7, 2, "r0")
    c5.ellipse(12, 14, 6, 5, "r2", outline="k")
    c5.ellipse(11, 12, 4, 3, "r3")
    c5.line(9, 11, 13, 11, "r4")
    c5.rect(13, 14, 2, 2, "o1")
    minerals["small_rock_sample"] = c5.img

    c6 = PixelCanvas(24, 24)
    c6.ellipse(12, 20, 6, 2, "r0")
    c6.rect(7, 5, 10, 15, "s3", outline="k")
    c6.rect(6, 4, 12, 3, "o1", outline="k")
    c6.rect(6, 17, 12, 3, "s0", outline="k")
    c6.rect(9, 8, 6, 8, "v0", outline="k")
    c6.rect(10, 10, 4, 5, "m3")
    c6.line(10, 9, 10, 15, "c1")
    minerals["geological_sample_container"] = c6.img

    c7 = PixelCanvas(24, 24)
    c7.ellipse(12, 20, 7, 2, "r0")
    c7.rect(6, 14, 12, 6, "s3", outline="k")
    c7.ellipse(12, 13, 5, 3, "m2", outline="k")
    c7.ellipse(12, 12, 3, 2, "m4")
    c7.set_px(10, 13, "y1")
    c7.set_px(14, 12, "m5")
    minerals["soil_sample"] = c7.img

    c8 = PixelCanvas(24, 24)
    c8.ellipse(12, 20, 6, 2, "r0")
    c8.rect(8, 4, 8, 16, "v1", outline="k")
    c8.rect(7, 3, 10, 3, "s0", outline="k")
    c8.rect(7, 18, 10, 3, "s0", outline="k")
    c8.polygon_points([(12, 7), (14, 11), (12, 16), (10, 11)], "p2", outline="p0")
    c8.line(9, 6, 9, 16, "c1")
    minerals["crystal_sample"] = c8.img

    c9 = PixelCanvas(24, 24)
    c9.ellipse(12, 20, 6, 2, "r0")
    c9.rect(6, 5, 12, 14, "v0", outline="k")
    c9.rect(8, 7, 8, 10, "s0", outline="c0")
    for py in range(7, 17, 3):
        c9.line(4, py, 6, py, "y1")
        c9.line(18, py, 20, py, "y1")
    c9.rect(10, 9, 4, 6, "c1")
    items["scientific_data_chip"] = c9.img

    c10 = PixelCanvas(24, 24)
    c10.ellipse(12, 20, 6, 2, "r0")
    c10.ellipse(12, 12, 7, 7, "c0", outline="k")
    c10.ellipse(12, 12, 5, 5, "c1")
    c10.ellipse(12, 12, 2, 2, "s5")
    c10.rect(9, 4, 6, 2, "o1", outline="k")
    c10.rect(9, 18, 6, 2, "o1", outline="k")
    items["e_cell_energy"] = c10.img

    c11 = PixelCanvas(24, 24)
    c11.ellipse(12, 20, 6, 2, "r0")
    c11.rect(10, 3, 4, 3, "s0", outline="k")
    c11.line(9, 4, 14, 4, "o1")
    c11.rect(7, 6, 10, 14, "s4", outline="k")
    c11.rect(8, 9, 8, 5, "c0")
    c11.line(9, 7, 9, 18, "s5")
    c11.line(15, 7, 15, 18, "s2")
    items["oxygen_tank"] = c11.img

    c12 = PixelCanvas(24, 24)
    c12.ellipse(12, 20, 6, 2, "r0")
    c12.rect(9, 4, 6, 2, "s3", outline="k")
    c12.rect(6, 6, 12, 14, "s0", outline="k")
    c12.rect(7, 7, 10, 4, "o1")
    c12.line(13, 10, 10, 14, "y2")
    c12.line(10, 14, 13, 14, "y2")
    c12.line(13, 14, 11, 18, "y1")
    items["battery"] = c12.img

    c13 = PixelCanvas(24, 24)
    c13.ellipse(12, 20, 7, 2, "r0")
    c13.rect(9, 4, 6, 3, "s0", outline="k")
    c13.rect(4, 7, 16, 12, "s4", outline="k")
    c13.line(5, 8, 18, 8, "s5")
    c13.line(5, 17, 18, 17, "s2")
    c13.rect(11, 10, 2, 6, "d1")
    c13.rect(9, 12, 6, 2, "d1")
    items["health_repair_kit"] = c13.img

    all_collectibles = {}
    all_collectibles.update(minerals)
    all_collectibles.update(items)
    return minerals, all_collectibles


# ==============================================================================
# 6. CATEGORY D: ENVIRONMENTAL OBJECTS & PROPS (17 SPRITES: 32x32, 48x48, 64x64)
# ==============================================================================
def generate_environmental_objects() -> dict:
    objs = {}

    # 1. Mars Rover (64x64)
    r = PixelCanvas(64, 64)
    r.ellipse(32, 52, 24, 7, "r0")
    for wy in [18, 31, 44]:
        r.rect(10, wy, 7, 9, "s0", outline="k")
        r.line(11, wy + 2, 15, wy + 2, "s2")
        r.line(11, wy + 5, 15, wy + 5, "s2")
        r.rect(47, wy, 7, 9, "s0", outline="k")
        r.line(48, wy + 2, 52, wy + 2, "s2")
        r.line(48, wy + 5, 52, wy + 5, "s2")
        r.line(17, wy + 4, 21, wy + 4, "s1")
        r.line(43, wy + 4, 47, wy + 4, "s1")
    r.rect(18, 15, 28, 36, "s4", outline="k")
    r.rect(20, 17, 24, 32, "s3", outline="k")
    r.rect(22, 24, 20, 14, "v0", outline="k")
    r.line(22, 31, 41, 31, "c0")
    r.line(32, 24, 32, 37, "c0")
    r.rect(22, 39, 20, 8, "y1", outline="k")
    r.rect(28, 7, 8, 9, "s2", outline="k")
    r.rect(26, 4, 12, 5, "o1", outline="k")
    r.set_px(32, 5, "c1")
    r.rect(35, 14, 10, 7, "s4", outline="k")
    r.rect(37, 16, 6, 3, "v0")
    r.set_px(38, 17, "c1")
    r.set_px(41, 17, "d1")
    objs["mars_rover"] = (r.img, {"size": [64, 64], "description": "6-wheeled scientific Mars rover"})

    # 2. Small exploration drone (32x32)
    d = PixelCanvas(32, 32)
    d.ellipse(16, 28, 6, 2, "r0")
    d.line(12, 18, 8, 25, "s0")
    d.line(20, 18, 24, 25, "s0")
    d.line(4, 8, 28, 8, "s1")
    d.line(6, 7, 26, 7, "s4")
    d.line(5, 11, 27, 11, "s0")
    d.rect(12, 12, 8, 8, "y1", outline="k")
    d.rect(13, 14, 6, 4, "o1")
    d.set_px(16, 16, "c1")
    d.rect(15, 6, 2, 7, "s0")
    objs["small_exploration_drone"] = (d.img, {"size": [32, 32], "description": "Coaxial Mars exploration rotorcraft drone"})

    # 3. Research habitat (64x64)
    h = PixelCanvas(64, 64)
    h.ellipse(32, 36, 27, 22, "r0")
    h.ellipse(32, 30, 24, 20, "s4", outline="k")
    h.ellipse(30, 27, 19, 15, "s5")
    h.line(10, 30, 54, 30, "s2")
    h.line(32, 11, 32, 48, "s2")
    h.line(16, 17, 48, 43, "s2")
    h.line(16, 43, 48, 17, "s2")
    h.rect(14, 28, 36, 4, "o1", outline="k")
    h.ellipse(32, 24, 7, 5, "v0", outline="k")
    h.ellipse(31, 23, 4, 3, "c0")
    h.set_px(29, 22, "c1")
    h.rect(24, 44, 16, 15, "s3", outline="k")
    h.rect(26, 46, 12, 3, "o1")
    h.rect(27, 51, 10, 8, "s0", outline="k")
    h.set_px(35, 54, "g2")
    objs["research_habitat"] = (h.img, {"size": [64, 64], "description": "Pressurized Mars surface research habitat dome"})

    # 4. Communication beacon (32x32)
    b = PixelCanvas(32, 32)
    b.ellipse(16, 27, 8, 3, "r0")
    b.line(16, 18, 9, 27, "s0")
    b.line(16, 18, 23, 27, "s0")
    b.line(16, 18, 16, 28, "s0")
    b.rect(12, 13, 8, 7, "s4", outline="k")
    b.rect(13, 15, 6, 3, "o1")
    b.line(16, 5, 16, 13, "s1")
    b.ellipse(16, 5, 3, 3, "c0", outline="k")
    b.set_px(15, 4, "c1")
    objs["communication_beacon"] = (b.img, {"size": [32, 32], "description": "Tripod surface navigation & telemetry beacon"})

    # 5. Communication tower (48x64)
    ct = PixelCanvas(48, 64)
    ct.ellipse(24, 58, 14, 4, "r0")
    ct.rect(14, 50, 20, 9, "s2", outline="k")
    ct.rect(16, 52, 16, 5, "o1", outline="k")
    ct.line(17, 50, 21, 12, "s1")
    ct.line(30, 50, 26, 12, "s1")
    for ty_bar in range(16, 50, 7):
        w_half = 2 + (ty_bar - 12) // 8
        ct.line(24 - w_half, ty_bar, 24 + w_half, ty_bar, "s3")
        ct.line(24 - w_half, ty_bar, 24 + w_half, ty_bar + 5, "s0")
    ct.ellipse(16, 22, 6, 6, "s4", outline="k")
    ct.ellipse(15, 22, 3, 3, "c0")
    ct.rect(21, 8, 6, 5, "o1", outline="k")
    ct.ellipse(24, 5, 3, 3, "d1", outline="k")
    ct.set_px(23, 4, "y2")
    objs["communication_tower"] = (ct.img, {"size": [48, 64], "description": "High-gain lattice communication relay tower"})

    # 6. Solar panel (32x32)
    sp = PixelCanvas(32, 32)
    sp.ellipse(16, 28, 8, 2, "r0")
    sp.rect(14, 21, 4, 7, "s1", outline="k")
    sp.rect(4, 7, 24, 15, "s3", outline="k")
    sp.rect(6, 9, 20, 11, "v0", outline="k")
    for gx in [11, 16, 21]:
        sp.line(gx, 9, gx, 19, "c0")
    sp.line(6, 14, 25, 14, "c0")
    sp.line(7, 10, 10, 10, "c1")
    objs["solar_panel"] = (sp.img, {"size": [32, 32], "description": "Photovoltaic solar array wing"})

    # 7. Supply crate (32x32)
    sc = PixelCanvas(32, 32)
    sc.rect(6, 25, 20, 4, "r0")
    sc.rect(6, 8, 20, 18, "s4", outline="k")
    sc.rect(8, 10, 16, 5, "o1", outline="k")
    sc.rect(8, 16, 16, 8, "s3", outline="k")
    sc.rect(14, 13, 4, 5, "s0", outline="k")
    sc.set_px(15, 15, "c1")
    objs["supply_crate"] = (sc.img, {"size": [32, 32], "description": "Standardized mission supply crate"})

    # 8. Storage container (48x48)
    stc = PixelCanvas(48, 48)
    stc.rect(6, 36, 36, 6, "r0")
    stc.rect(6, 12, 36, 26, "s3", outline="k")
    stc.rect(8, 14, 32, 7, "s4")
    stc.rect(8, 22, 32, 4, "o1", outline="k")
    for rib_x in range(12, 38, 6):
        stc.line(rib_x, 14, rib_x, 35, "s1")
    stc.rect(20, 21, 8, 6, "s0", outline="k")
    stc.set_px(23, 24, "g2")
    objs["storage_container"] = (stc.img, {"size": [48, 48], "description": "Heavy pressurized cargo storage container"})

    # 9. Scientific scanning instrument (32x32)
    ssi = PixelCanvas(32, 32)
    ssi.ellipse(16, 27, 8, 3, "r0")
    ssi.line(16, 17, 9, 27, "s0")
    ssi.line(16, 17, 23, 27, "s0")
    ssi.line(16, 17, 16, 28, "s0")
    ssi.rect(10, 9, 12, 9, "s4", outline="k")
    ssi.rect(12, 11, 8, 5, "v0", outline="k")
    ssi.ellipse(16, 13, 2, 2, "c1")
    ssi.rect(14, 6, 4, 4, "o1", outline="k")
    objs["scientific_scanning_instrument"] = (ssi.img, {"size": [32, 32], "description": "Laser spectrometer & subsurface scanner"})

    # 10. Sample collection device (32x32)
    scd = PixelCanvas(32, 32)
    scd.ellipse(16, 27, 9, 3, "r0")
    scd.rect(8, 18, 16, 9, "s2", outline="k")
    scd.rect(10, 8, 12, 11, "o1", outline="k")
    scd.rect(12, 10, 8, 7, "v0", outline="k")
    scd.line(16, 11, 16, 28, "s4")
    scd.set_px(14, 13, "c1")
    objs["sample_collection_device"] = (scd.img, {"size": [32, 32], "description": "Automated regolith core drill & sample extractor"})

    # 11. Sign or scientific marker (32x32)
    sm = PixelCanvas(32, 32)
    sm.ellipse(14, 28, 6, 2, "r0")
    sm.rect(11, 25, 6, 4, "s1", outline="k")
    sm.rect(13, 6, 2, 20, "s4", outline="k")
    sm.rect(14, 7, 12, 8, "o1", outline="k")
    sm.line(16, 9, 23, 9, "s5")
    sm.line(16, 12, 21, 12, "y2")
    objs["scientific_marker_sign"] = (sm.img, {"size": [32, 32], "description": "High-visibility scientific survey marker post"})

    # 12. Antenna (32x32)
    ant = PixelCanvas(32, 32)
    ant.ellipse(16, 28, 7, 2, "r0")
    ant.rect(12, 22, 8, 6, "s1", outline="k")
    ant.rect(15, 14, 2, 9, "s0")
    ant.ellipse(16, 11, 8, 6, "s4", outline="k")
    ant.ellipse(16, 11, 5, 3, "s3")
    ant.line(16, 11, 21, 6, "s0")
    ant.set_px(21, 6, "c1")
    objs["antenna"] = (ant.img, {"size": [32, 32], "description": "Parabolic dish telemetry antenna"})

    # 13. Small rock formations (32x32)
    srf = PixelCanvas(32, 32)
    draw_rock_cluster(srf, 12, 20, 7, 5)
    draw_rock_cluster(srf, 20, 17, 6, 7)
    draw_rock_cluster(srf, 15, 13, 5, 6)
    objs["small_rock_formations"] = (srf.img, {"size": [32, 32], "description": "Wind-sculpted Martian rock spire cluster"})

    # 14. Cactus-like fictional alien plant (32x32)
    ap = PixelCanvas(32, 32)
    ap.ellipse(16, 28, 7, 2, "r0")
    ap.rect(13, 9, 6, 19, "g1", outline="k")
    ap.line(15, 10, 15, 26, "g2")
    ap.rect(8, 14, 6, 4, "g1", outline="k")
    ap.rect(8, 10, 4, 6, "g1", outline="k")
    ap.rect(18, 16, 6, 4, "g1", outline="k")
    ap.rect(20, 11, 4, 7, "g1", outline="k")
    ap.rect(14, 6, 4, 4, "p2", outline="k")
    ap.set_px(15, 7, "c1")
    objs["alien_cactus_plant"] = (ap.img, {"size": [32, 32], "description": "Stylized Martian extremophile cactus flora"})

    # 15. Dead tree or unusual plant (32x32)
    dt = PixelCanvas(32, 32)
    dt.ellipse(16, 28, 7, 2, "r0")
    dt.rect(14, 16, 4, 12, "w", outline="k")
    dt.line(15, 17, 15, 26, "r3")
    dt.line(15, 17, 8, 9, "w")
    dt.line(15, 16, 9, 9, "r2")
    dt.line(16, 18, 24, 10, "w")
    dt.line(16, 17, 23, 10, "r3")
    dt.line(11, 13, 13, 7, "r2")
    dt.set_px(8, 8, "o1")
    dt.set_px(24, 9, "o1")
    objs["dead_tree_unusual_plant"] = (dt.img, {"size": [32, 32], "description": "Desiccated iron-oxide petrified vent flora"})

    # 16. Geological fossil (32x32)
    gf = PixelCanvas(32, 32)
    draw_rock_cluster(gf, 16, 17, 11, 8)
    gf.ellipse(16, 16, 6, 5, "m5", outline="w")
    gf.ellipse(16, 16, 3, 3, "m4", outline="w")
    gf.set_px(16, 16, "y2")
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        gf.set_px(int(16 + 5 * math.cos(rad)), int(16 + 4 * math.sin(rad)), "w")
    objs["geological_fossil"] = (gf.img, {"size": [32, 32], "description": "Exposed ancient spiral fossil embedded in rock slab"})

    # 17. Ancient rock or surface formation (48x48)
    arf = PixelCanvas(48, 48)
    arf.ellipse(24, 40, 18, 5, "r0")
    arf.rect(8, 16, 10, 24, "r2", outline="k")
    arf.rect(30, 16, 10, 24, "r1", outline="k")
    arf.rect(6, 10, 36, 9, "r3", outline="k")
    arf.line(8, 12, 40, 12, "r4")
    arf.set_px(13, 24, "c1")
    arf.set_px(13, 28, "c0")
    arf.set_px(35, 24, "c1")
    arf.set_px(35, 28, "c0")
    objs["ancient_surface_formation"] = (arf.img, {"size": [48, 48], "description": "Large eroded Martian sandstone arch formation"})

    return objs


# ==============================================================================
# 7. CATEGORY E: HAZARDS & ENVIRONMENTAL EFFECTS (32x32 NATIVE SPRITES & ANIMS)
# ==============================================================================
def generate_hazards_and_effects():
    hazards = {}
    effects = {}

    # 1. Sandstorm or dust storm (4 frames)
    for f in range(4):
        c = PixelCanvas(32, 32)
        for ring, ry, rx, col in [(0, 24, 6, "m2"), (1, 19, 8, "m3"), (2, 13, 10, "m4"), (3, 7, 12, "m5")]:
            shift = int(2 * math.sin((f + ring) * math.pi / 2))
            c.ellipse(16 + shift, ry, rx, 3, col, outline="w")
        c.set_px(6 + f * 3, 10, "m5")
        c.set_px(25 - f * 2, 16, "m4")
        c.set_px(10 + f * 2, 24, "r2")
        hazards[f"sandstorm_f{f+1}"] = c.img
        if f == 0:
            hazards["sandstorm_hazard"] = c.img

    # 2. Rockfall warning or falling-rock hazard (4 frames)
    for f in range(4):
        c = PixelCanvas(32, 32)
        col_ret = "d1" if f % 2 == 0 else "o1"
        c.ellipse(16, 22, 10, 5, col_ret, outline="k")
        c.ellipse(16, 22, 7, 3, "m0")
        if f < 2:
            c.rect(15, 12, 2, 6, "y2", outline="k")
            c.rect(15, 19, 2, 2, "y2", outline="k")
        else:
            by = 8 if f == 2 else 18
            draw_rock_cluster(c, 16, by, 6, 5)
            if f == 3:
                c.set_px(8, 19, "m5")
                c.set_px(24, 18, "m4")
        hazards[f"rockfall_hazard_f{f+1}"] = c.img
        if f == 0:
            hazards["rockfall_warning_hazard"] = c.img

    # 3. Radiation zone (2 frames)
    for f in range(2):
        c = PixelCanvas(32, 32)
        c.ellipse(16, 18, 12, 8, "g0", outline="k")
        c.ellipse(16, 18, 8, 5, "g1")
        c.ellipse(16, 18, 3, 2, "g2" if f == 0 else "y2")
        for px, py in [(10, 12 - f * 2), (21, 10 - f * 2), (15, 7 - f * 2)]:
            c.rect(px, py, 2, 2, "g2", outline="k")
        hazards[f"radiation_zone_f{f+1}"] = c.img
        if f == 0:
            hazards["radiation_zone"] = c.img

    # 4. Heat zone (2 frames)
    for f in range(2):
        c = PixelCanvas(32, 32)
        c.ellipse(16, 19, 12, 7, "d0", outline="k")
        c.ellipse(16, 19, 9, 5, "o1")
        c.ellipse(16, 19, 5, 3, "y1" if f == 0 else "y2")
        for wx in [10, 16, 22]:
            wy = 12 - f * 2
            c.line(wx, wy, wx + 1, wy - 3, "y2")
        hazards[f"heat_zone_f{f+1}"] = c.img
        if f == 0:
            hazards["heat_zone"] = c.img

    # 5. Cracked terrain
    c_crack = PixelCanvas(32, 32)
    pts_crack = [(4, 6), (11, 13), (9, 19), (17, 16), (22, 24), (28, 27)]
    for i in range(len(pts_crack) - 1):
        c_crack.line(pts_crack[i][0], pts_crack[i][1], pts_crack[i + 1][0], pts_crack[i + 1][1], "k")
        c_crack.line(pts_crack[i][0] + 1, pts_crack[i][1], pts_crack[i + 1][0] + 1, pts_crack[i + 1][1], "w")
        c_crack.line(pts_crack[i][0], pts_crack[i][1] + 1, pts_crack[i + 1][0], pts_crack[i + 1][1] + 1, "m0")
    c_crack.line(17, 16, 24, 9, "k")
    c_crack.line(11, 13, 6, 23, "k")
    hazards["cracked_terrain"] = c_crack.img

    # 6. Small hostile robotic unit (4 frames)
    for f in range(4):
        c = PixelCanvas(32, 32)
        c.ellipse(16, 26, 8, 3, "r0")
        leg_off = 1 if f % 2 == 1 else -1
        for lx, ly in [(7, 22 + leg_off), (9, 26 - leg_off), (25, 22 - leg_off), (23, 26 + leg_off)]:
            c.line(16, 18, lx, ly, "s0")
            c.rect(lx - 1, ly, 2, 2, "o1")
        c.ellipse(16, 16, 7, 6, "s0", outline="k")
        c.ellipse(15, 14, 5, 3, "s1")
        eye_x = 15 + (1 if f == 1 else (-1 if f == 3 else 0))
        c.rect(eye_x - 2, 15, 5, 3, "d0", outline="k")
        c.rect(eye_x - 1, 16, 3, 2, "d1")
        c.set_px(eye_x, 16, "y2")
        c.line(16, 7, 16, 10, "s1")
        c.set_px(16, 7, "d1" if f % 2 == 0 else "y1")
        hazards[f"hostile_robot_f{f+1}"] = c.img
        if f == 0:
            hazards["hostile_robotic_unit"] = c.img

    # --- ENVIRONMENTAL EFFECTS ---
    for f in range(4):
        c = PixelCanvas(32, 32)
        r_rad = 3 + f * 3
        c.ellipse(16, 16, r_rad, r_rad, None, outline="c1")
        if r_rad > 4:
            c.ellipse(16, 16, r_rad - 2, r_rad - 2, None, outline="c0")
        c.set_px(16, 16, "s5")
        effects[f"scanning_pulse_f{f+1}"] = c.img
        if f == 2:
            effects["scanning_pulse"] = c.img

    for f in range(4):
        c = PixelCanvas(32, 32)
        for sx, sy in [(10, 22 - f * 3), (21, 20 - f * 3), (15, 25 - f * 4), (13, 15 - f * 2), (19, 13 - f * 2)]:
            if 2 <= sy < 29:
                c.set_px(sx, sy, "y2")
                c.set_px(sx - 1, sy, "c1")
                c.set_px(sx + 1, sy, "c1")
                c.set_px(sx, sy - 1, "c0")
                c.set_px(sx, sy + 1, "c0")
        effects[f"sample_collection_effect_f{f+1}"] = c.img
        if f == 1:
            effects["sample_collection_effect"] = c.img

    for f in range(4):
        c = PixelCanvas(32, 32)
        rad = 6 - f
        if rad > 1:
            c.ellipse(12 + f, 20 - f * 2, rad, rad - 1, "m4", outline="m2")
            c.ellipse(18 - f, 22 - f * 2, max(2, rad - 1), max(2, rad - 2), "m5", outline="m3")
        effects[f"dust_trail_f{f+1}"] = c.img
        if f == 0:
            effects["dust_trail"] = c.img

    fp_v = PixelCanvas(32, 32)
    for fx, fy in [(11, 8), (18, 14), (11, 20), (18, 26)]:
        fp_v.rect(fx, fy, 4, 5, "m0", outline="m3")
        fp_v.line(fx + 1, fy + 2, fx + 2, fy + 2, "m2")
    effects["footprints"] = fp_v.img
    effects["footprints_horizontal"] = fp_v.img.transpose(Image.ROTATE_90)

    for f in range(4):
        c = PixelCanvas(32, 32)
        c.ellipse(16, 16, 3, 3, "s5", outline="c1")
        for angle in range(f * 22, 360 + f * 22, 60):
            rad = math.radians(angle)
            x1 = int(16 + (7 + (f % 2) * 3) * math.cos(rad))
            y1 = int(16 + (7 + (f % 2) * 3) * math.sin(rad))
            c.line(16, 16, x1, y1, "y2" if angle % 120 == 0 else "c1")
        effects[f"spark_energy_f{f+1}"] = c.img
        if f == 1:
            effects["spark_energy_effect"] = c.img

    for f in range(4):
        c = PixelCanvas(32, 32)
        if f == 0:
            c.ellipse(16, 16, 6, 6, "y2", outline="o1")
            c.ellipse(16, 16, 3, 3, "s5")
        elif f == 1:
            c.ellipse(16, 16, 10, 10, "o1", outline="k")
            c.ellipse(15, 15, 7, 7, "y1")
            c.ellipse(15, 15, 4, 4, "y2")
        elif f == 2:
            c.ellipse(14, 14, 8, 8, "r0", outline="k")
            c.ellipse(19, 17, 7, 7, "r1", outline="k")
            c.ellipse(16, 16, 5, 5, "o1")
            c.set_px(15, 15, "y2")
        else:
            c.ellipse(12, 11, 5, 5, "r1", outline="k")
            c.ellipse(21, 14, 4, 4, "r2", outline="k")
            c.ellipse(15, 20, 4, 3, "r0", outline="k")
            c.set_px(16, 15, "o1")
        effects[f"explosion_malfunction_f{f+1}"] = c.img
        if f == 1:
            effects["small_explosion_malfunction"] = c.img

    return hazards, effects


# ==============================================================================
# 8. CATEGORY F: GAME UI & INTERFACE ICONS (15 ICONS + BARS + MINIMAP + CONTROLS)
# ==============================================================================
def generate_ui_assets():
    icons = {}

    def make_icon_badge(border_col="c0") -> PixelCanvas:
        c = PixelCanvas(16, 16)
        c.rect(1, 1, 14, 14, "v0", outline="k")
        c.rect(2, 2, 12, 12, "v0", outline=border_col)
        return c

    ic = make_icon_badge("d1")
    ic.rect(7, 4, 2, 8, "d1")
    ic.rect(4, 7, 8, 2, "d1")
    ic.set_px(7, 5, "s5")
    icons["health_icon"] = ic.img

    ic = make_icon_badge("c0")
    ic.ellipse(8, 8, 3, 4, "c0", outline="c1")
    ic.set_px(7, 6, "s5")
    icons["oxygen_icon"] = ic.img

    ic = make_icon_badge("y1")
    ic.rect(6, 4, 4, 1, "s4")
    ic.rect(5, 5, 6, 7, "y1", outline="s4")
    ic.set_px(8, 7, "s5")
    icons["battery_icon"] = ic.img

    ic = make_icon_badge("o1")
    ic.rect(6, 4, 4, 8, "c1", outline="s4")
    ic.rect(5, 4, 6, 2, "o1")
    ic.rect(7, 7, 2, 4, "m3")
    icons["sample_icon"] = ic.img

    ic = make_icon_badge("p1")
    ic.polygon_points([(8, 4), (11, 8), (8, 12), (5, 8)], "p2", outline="p1")
    ic.set_px(8, 6, "s5")
    icons["mineral_icon"] = ic.img

    ic = make_icon_badge("c0")
    ic.rect(4, 5, 8, 6, "s4", outline="s2")
    ic.line(6, 5, 6, 10, "c0")
    ic.line(9, 5, 9, 10, "c0")
    ic.set_px(8, 7, "d1")
    icons["map_icon"] = ic.img

    ic = make_icon_badge("c1")
    ic.ellipse(8, 8, 4, 4, None, outline="c0")
    ic.ellipse(8, 8, 2, 2, None, outline="c1")
    ic.set_px(8, 8, "s5")
    icons["scanner_icon"] = ic.img

    ic = make_icon_badge("y1")
    ic.polygon_points([(8, 3), (12, 8), (8, 13), (4, 8)], "y1", outline="y2")
    ic.set_px(8, 8, "s5")
    icons["objective_marker"] = ic.img

    ic = make_icon_badge("o1")
    ic.polygon_points([(8, 4), (12, 11), (4, 11)], "o1", outline="y2")
    ic.line(8, 6, 8, 8, "k")
    ic.set_px(8, 10, "k")
    icons["hazard_marker"] = ic.img

    ic = make_icon_badge("c0")
    ic.polygon_points([(8, 4), (12, 10), (8, 8), (4, 10)], "c1", outline="c0")
    icons["route_marker"] = ic.img

    ic = make_icon_badge("g1")
    ic.rect(5, 5, 6, 6, "g1", outline="g2")
    ic.set_px(8, 8, "s5")
    icons["interaction_icon"] = ic.img

    ic = make_icon_badge("o1")
    ic.rect(5, 5, 6, 7, "s4", outline="o1")
    ic.rect(6, 4, 4, 2, "s2")
    ic.line(6, 8, 9, 8, "o1")
    icons["inventory_icon"] = ic.img

    ic = make_icon_badge("s3")
    ic.rect(5, 5, 2, 6, "s5")
    ic.rect(9, 5, 2, 6, "s5")
    icons["pause_icon"] = ic.img

    ic = make_icon_badge("s3")
    ic.ellipse(8, 8, 4, 4, "s3", outline="s5")
    ic.ellipse(8, 8, 2, 2, "v0")
    icons["settings_icon"] = ic.img

    ic = make_icon_badge("c0")
    ic.rect(5, 4, 6, 8, "s4", outline="s2")
    ic.line(6, 6, 9, 6, "v1")
    ic.line(6, 8, 9, 8, "v1")
    ic.line(6, 10, 8, 10, "v1")
    icons["mission_log_icon"] = ic.img

    ui_icons_atlas = Image.new("RGBA", (5 * 16, 3 * 16), (0, 0, 0, 0))
    for idx, (name, img) in enumerate(icons.items()):
        col = idx % 5
        row = idx // 5
        ui_icons_atlas.paste(img, (col * 16, row * 16))

    hud_bars = Image.new("RGBA", (64 * 4, 12 * 3), (0, 0, 0, 0))
    bar_specs = [
        ("health", "d0", "d1", "s5"),
        ("oxygen", "v1", "c0", "c1"),
        ("battery", "y0", "y1", "y2"),
    ]
    individual_bars = {}
    for r_idx, (bname, c_dark, c_mid, c_hi) in enumerate(bar_specs):
        for c_idx, frac in enumerate([0.0, 1.0, 0.5, 0.25]):
            bc = PixelCanvas(64, 12)
            bc.rect(1, 1, 62, 10, "v0", outline="k")
            bc.rect(2, 2, 60, 8, "s0", outline="s2")
            fill_w = int(56 * frac)
            if fill_w > 0:
                bc.rect(4, 4, fill_w, 4, c_mid)
                bc.line(4, 4, 4 + fill_w - 1, 4, c_hi)
                bc.line(4, 7, 4 + fill_w - 1, 7, c_dark)
            hud_bars.paste(bc.img, (c_idx * 64, r_idx * 12))
            individual_bars[f"bar_{bname}_{int(frac*100)}pct"] = bc.img

    mm = PixelCanvas(64, 64)
    mm.rect(0, 0, 64, 64, "v0", outline="k")
    mm.rect(2, 2, 60, 60, "s0", outline="c0")
    for y in range(6, 58):
        for x in range(6, 58):
            mm.px[x, y] = (0, 0, 0, 0)
            if x in (6, 57) or y in (6, 57):
                mm.set_px(x, y, "k")
    mm.rect(30, 1, 4, 4, "o1", outline="k")
    mm.rect(30, 59, 4, 4, "c0", outline="k")
    mm.rect(1, 30, 4, 4, "c0", outline="k")
    mm.rect(59, 30, 4, 4, "c0", outline="k")
    minimap_frame = mm.img

    ctrl = PixelCanvas(128, 64)
    ctrl.ellipse(28, 32, 22, 22, "v0", outline="k")
    ctrl.ellipse(28, 32, 19, 19, "s0", outline="c0")
    ctrl.ellipse(28, 32, 8, 8, "v1")
    ctrl.ellipse(72, 20, 10, 10, "o1", outline="k")
    ctrl.ellipse(71, 19, 6, 6, "y1")
    ctrl.ellipse(72, 46, 10, 10, "c0", outline="k")
    ctrl.ellipse(71, 45, 6, 6, "c1")
    ctrl.ellipse(104, 32, 12, 12, "g1", outline="k")
    ctrl.ellipse(103, 31, 8, 8, "g2")

    return icons, ui_icons_atlas, hud_bars, individual_bars, minimap_frame, ctrl.img


# ==============================================================================
# 9. SPRITE SHEET & ATLAS PACKING HELPERS
# ==============================================================================
def pack_grid_atlas(sprite_list, cell_w: int, cell_h: int, cols: int):
    rows = math.ceil(len(sprite_list) / cols)
    atlas = Image.new("RGBA", (cols * cell_w, rows * cell_h), (0, 0, 0, 0))
    mapping = []
    for idx, (name, img) in enumerate(sprite_list):
        c = idx % cols
        r = idx // cols
        ox = c * cell_w + (cell_w - img.width) // 2
        oy = r * cell_h + (cell_h - img.height) // 2
        atlas.paste(img, (ox, oy))
        mapping.append({
            "index": idx,
            "name": name,
            "row": r,
            "col": c,
            "x": c * cell_w,
            "y": r * cell_h,
            "cell_width": cell_w,
            "cell_height": cell_h,
            "sprite_width": img.width,
            "sprite_height": img.height,
        })
    return atlas, mapping


# ==============================================================================
# 10. EXAMPLE LEVEL & PREVIEW SHEET GENERATORS (NEAREST-NEIGHBOR ONLY)
# ==============================================================================
def build_example_level(terrain_tiles, astronaut_frames, minerals, items, objects, hazards, effects, ui_assets):
    map_w, map_h = 20, 15
    tile_w, tile_h = 32, 32

    # Base ground uses seamless m2-based tiles (01_plain_red_ground, 02_sparse_small_stones, 06_small_isolated_rocks)
    # so there are zero hard checkerboard tile seams across the open Martian plains!
    grid = []
    rng = random.Random(2026)
    for y in range(map_h):
        row = []
        for x in range(map_w):
            r_val = rng.random()
            if r_val < 0.68:
                row.append("01_plain_red_ground")
            elif r_val < 0.92:
                row.append("02_sparse_small_stones")
            else:
                row.append("06_small_isolated_rocks")
        grid.append(row)

    # Top cliff ridge along row 0..1
    for x in range(0, 14):
        grid[0][x] = "10_cliff_top"
        grid[1][x] = "11_cliff_side_wall"
    grid[0][14] = "25_cliff_corner_right"
    grid[1][14] = "13_uphill_slope"

    # Dusty path running horizontally & branching vertically to research habitat and crater
    for x in range(2, 18):
        grid[7][x] = "17_dusty_path"
    grid[7][10] = "32_dusty_path_cross"
    for y in range(3, 7):
        grid[y][10] = "31_dusty_path_vertical"
    for y in range(8, 13):
        grid[y][10] = "31_dusty_path_vertical"

    # Impact crater in bottom-left (rows 9..12, cols 2..6) with continuous dark 08_crater_floor inside
    for x in range(3, 6):
        grid[9][x] = "09_crater_rim"
        grid[12][x] = "28_crater_rim_bottom"
    for y in range(10, 12):
        grid[y][2] = "29_crater_rim_left"
        grid[y][6] = "30_crater_rim_right"
        for x in range(3, 6):
            grid[y][x] = "08_crater_floor"

    # Mineral-bearing rock clusters & geological features on seamless m2 ground
    grid[3][3] = "19_blue_mineral_rock"
    grid[3][4] = "19_blue_mineral_rock"
    grid[4][16] = "20_yellow_mineral_rock"
    grid[5][17] = "20_yellow_mineral_rock"
    grid[11][15] = "21_green_mineral_rock"
    grid[12][16] = "22_unusual_geological_formation"
    grid[13][8] = "23_ice_bearing_patch"
    grid[13][9] = "24_metal_rich_surface"
    grid[5][7] = "07_large_boulders"
    grid[13][13] = "18_ancient_rock_formation"
    grid[8][15] = "16_rubble_field"

    level_img = Image.new("RGBA", (map_w * tile_w, map_h * tile_h), PAL["m2"])
    for y in range(map_h):
        for x in range(map_w):
            tname = grid[y][x]
            t_img = terrain_tiles[tname][0]
            level_img.paste(t_img, (x * tile_w, y * tile_h))

    placed_entities = []

    def place_sprite(img: Image.Image, px: int, py: int, name: str, category: str):
        level_img.alpha_composite(img, (px, py))
        placed_entities.append({"name": name, "category": category, "x": px, "y": py, "width": img.width, "height": img.height})

    # Research habitat & base equipment
    place_sprite(objects["research_habitat"][0], 11 * 32, 1 * 32 + 8, "research_habitat", "object")
    place_sprite(objects["solar_panel"][0], 13 * 32 + 8, 2 * 32, "solar_panel", "object")
    place_sprite(objects["solar_panel"][0], 14 * 32 + 12, 2 * 32, "solar_panel", "object")
    place_sprite(objects["communication_tower"][0], 16 * 32, 1 * 32, "communication_tower", "object")
    place_sprite(objects["supply_crate"][0], 11 * 32, 4 * 32, "supply_crate", "object")
    place_sprite(objects["storage_container"][0], 8 * 32, 2 * 32, "storage_container", "object")
    place_sprite(objects["communication_beacon"][0], 9 * 32, 5 * 32, "communication_beacon", "object")

    # Mars Rover & Exploration Drone
    place_sprite(objects["mars_rover"][0], 4 * 32, 5 * 32 + 10, "mars_rover", "object")
    place_sprite(objects["small_exploration_drone"][0], 6 * 32 + 8, 4 * 32, "small_exploration_drone", "object")
    place_sprite(objects["scientific_marker_sign"][0], 9 * 32, 8 * 32, "scientific_marker_sign", "object")
    place_sprite(objects["scientific_scanning_instrument"][0], 7 * 32, 10 * 32, "scientific_scanning_instrument", "object")
    place_sprite(objects["ancient_surface_formation"][0], 17 * 32, 9 * 32, "ancient_surface_formation", "object")
    place_sprite(objects["alien_cactus_plant"][0], 14 * 32, 10 * 32, "alien_cactus_plant", "object")
    place_sprite(objects["geological_fossil"][0], 12 * 32, 11 * 32, "geological_fossil", "object")

    # Collectible minerals & items
    place_sprite(minerals["blue_mineral_crystal"], 2 * 32 + 4, 3 * 32 + 4, "blue_mineral_crystal", "mineral")
    place_sprite(minerals["blue_mineral_crystal"], 3 * 32 + 4, 4 * 32 + 4, "blue_mineral_crystal", "mineral")
    place_sprite(minerals["yellow_mineral_crystal"], 15 * 32 + 4, 4 * 32 + 4, "yellow_mineral_crystal", "mineral")
    place_sprite(minerals["yellow_mineral_crystal"], 16 * 32 + 4, 5 * 32 + 4, "yellow_mineral_crystal", "mineral")
    place_sprite(minerals["green_mineral_crystal"], 14 * 32 + 4, 11 * 32 + 4, "green_mineral_crystal", "mineral")
    place_sprite(minerals["purple_rare_mineral"], 4 * 32 + 4, 10 * 32 + 4, "purple_rare_mineral", "mineral")
    place_sprite(items["oxygen_tank"], 10 * 32 + 4, 5 * 32 + 4, "oxygen_tank", "item")
    place_sprite(items["battery"], 12 * 32 + 4, 5 * 32 + 4, "battery", "item")
    place_sprite(items["geological_sample_container"], 8 * 32 + 4, 10 * 32 + 4, "geological_sample_container", "item")

    # Hazards & Effects
    place_sprite(hazards["radiation_zone"], 13 * 32, 12 * 32, "radiation_zone", "hazard")
    place_sprite(hazards["sandstorm_hazard"], 17 * 32, 12 * 32, "sandstorm_hazard", "hazard")
    place_sprite(hazards["hostile_robotic_unit"], 15 * 32, 8 * 32, "hostile_robotic_unit", "hazard")
    place_sprite(effects["footprints"], 9 * 32, 7 * 32, "footprints", "effect")
    place_sprite(effects["scanning_pulse"], 10 * 32, 7 * 32, "scanning_pulse", "effect")

    # Main Astronaut Character at center crossroads scanning
    place_sprite(astronaut_frames["astronaut_right_scan_f2"], 10 * 32, 7 * 32 - 4, "astronaut_player", "character")

    tilemap_json = {
        "name": "Mars Outpost Alpha — Sample Exploration Sector",
        "disclaimer": "Artistic indie game tilemap demonstration. Not derived from NASA orbital DEM/HiRISE telemetry.",
        "tile_width": tile_w,
        "tile_height": tile_h,
        "map_columns": map_w,
        "map_rows": map_h,
        "terrain_atlas": "../terrain/mars_terrain_tiles_32px.png",
        "layers": {
            "ground_tiles": grid,
            "entities": placed_entities,
        },
    }

    preview_level = level_img.resize((map_w * tile_w * 2, map_h * tile_h * 2), Image.NEAREST)
    return preview_level, tilemap_json


# ==============================================================================
# 11. MAIN PIPELINE EXECUTION
# ==============================================================================
def main():
    work_dir = Path("/working_dir/c_39102b0c2ac0cf5a/artifacts/file_generation/ttl=63d")
    inter_dir = work_dir / "intermediate"
    out_dir = work_dir / "output"
    pack_root = inter_dir / "MarsPixelAssets"

    if pack_root.exists():
        shutil.rmtree(pack_root)

    subdirs = [
        "characters/frames",
        "terrain/individual",
        "minerals/individual",
        "items/individual",
        "objects/individual",
        "hazards/individual",
        "effects/individual",
        "ui/individual",
        "preview",
        "examples",
    ]
    for sd in subdirs:
        (pack_root / sd).mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    # A. Astronaut frames & sheets
    directions = ["down", "up", "left", "right"]
    anim_defs = [
        ("idle", 2),
        ("walk", 4),
        ("run", 4),
        ("scan", 4),
        ("collect", 4),
        ("tool", 4),
        ("hurt", 2),
        ("defeated", 4),
    ]

    astronaut_frames = {}
    dir_sheets_meta = {}

    for d in directions:
        sheet = Image.new("RGBA", (4 * 32, len(anim_defs) * 32), (0, 0, 0, 0))
        rows_meta = []
        for r_idx, (anim_name, f_count) in enumerate(anim_defs):
            for f_idx in range(f_count):
                frame_img = draw_astronaut_frame(d, anim_name, f_idx, "default_white")
                fname = f"astronaut_{d}_{anim_name}_f{f_idx+1}"
                astronaut_frames[fname] = frame_img
                frame_img.save(pack_root / "characters/frames" / f"{fname}.png")
                sheet.paste(frame_img, (f_idx * 32, r_idx * 32))
            rows_meta.append({
                "row": r_idx,
                "animation": anim_name,
                "direction": d,
                "frame_count": f_count,
                "frame_width": 32,
                "frame_height": 32,
            })
        sheet_name = f"astronaut_{d}.png"
        sheet.save(pack_root / "characters" / sheet_name)
        dir_sheets_meta[sheet_name] = {
            "width": sheet.width,
            "height": sheet.height,
            "frame_width": 32,
            "frame_height": 32,
            "rows": rows_meta,
        }

    walk_sheet = Image.new("RGBA", (4 * 32, 4 * 32), (0, 0, 0, 0))
    for r_idx, d in enumerate(directions):
        for f_idx in range(4):
            walk_sheet.paste(astronaut_frames[f"astronaut_{d}_walk_f{f_idx+1}"], (f_idx * 32, r_idx * 32))
    walk_sheet.save(pack_root / "characters/astronaut_walk_4_directions.png")

    run_sheet = Image.new("RGBA", (4 * 32, 4 * 32), (0, 0, 0, 0))
    for r_idx, d in enumerate(directions):
        for f_idx in range(4):
            run_sheet.paste(astronaut_frames[f"astronaut_{d}_run_f{f_idx+1}"], (f_idx * 32, r_idx * 32))
    run_sheet.save(pack_root / "characters/astronaut_run_4_directions.png")

    inter_rows = []
    for anim_name in ["scan", "collect", "tool", "hurt"]:
        for d in directions:
            inter_rows.append((anim_name, d, 2 if anim_name == "hurt" else 4))
    inter_rows.append(("defeated", "down", 4))
    inter_sheet = Image.new("RGBA", (4 * 32, len(inter_rows) * 32), (0, 0, 0, 0))
    for r_idx, (anim_name, d, f_count) in enumerate(inter_rows):
        for f_idx in range(f_count):
            inter_sheet.paste(astronaut_frames[f"astronaut_{d}_{anim_name}_f{f_idx+1}"], (f_idx * 32, r_idx * 32))
    inter_sheet.save(pack_root / "characters/astronaut_interactions.png")

    skin_names = ["default_white", "blue_explorer", "red_commander", "green_biosuit", "purple_vanguard"]
    skins_sheet = Image.new("RGBA", (8 * 32, len(skin_names) * 32), (0, 0, 0, 0))
    for r_idx, sname in enumerate(skin_names):
        for d_idx, d in enumerate(directions):
            idle_skin = draw_astronaut_frame(d, "idle", 0, sname)
            walk_skin = draw_astronaut_frame(d, "walk", 0, sname)
            idle_skin.save(pack_root / "characters/frames" / f"astronaut_skin_{sname}_{d}_idle.png")
            walk_skin.save(pack_root / "characters/frames" / f"astronaut_skin_{sname}_{d}_walk.png")
            skins_sheet.paste(idle_skin, (d_idx * 2 * 32, r_idx * 32))
            skins_sheet.paste(walk_skin, ((d_idx * 2 + 1) * 32, r_idx * 32))
    skins_sheet.save(pack_root / "characters/astronaut_alternate_skins.png")

    character_manifest = {
        "character": "Mars Explorer Astronaut",
        "native_frame_size": [32, 32],
        "directions": directions,
        "animations": {name: count for name, count in anim_defs},
        "alternate_skins": skin_names,
        "sheets": {
            **dir_sheets_meta,
            "astronaut_walk_4_directions.png": {
                "width": 128,
                "height": 128,
                "frame_width": 32,
                "frame_height": 32,
                "row_order": directions,
                "frames_per_row": 4,
            },
            "astronaut_run_4_directions.png": {
                "width": 128,
                "height": 128,
                "frame_width": 32,
                "frame_height": 32,
                "row_order": directions,
                "frames_per_row": 4,
            },
            "astronaut_interactions.png": {
                "width": 128,
                "height": len(inter_rows) * 32,
                "frame_width": 32,
                "frame_height": 32,
                "rows": [
                    {"row": i, "animation": a, "direction": d, "frames": fc}
                    for i, (a, d, fc) in enumerate(inter_rows)
                ],
            },
            "astronaut_alternate_skins.png": {
                "width": 256,
                "height": len(skin_names) * 32,
                "frame_width": 32,
                "frame_height": 32,
                "row_order": skin_names,
                "column_order": [
                    "down_idle", "down_walk", "up_idle", "up_walk",
                    "left_idle", "left_walk", "right_idle", "right_walk",
                ],
            },
        },
    }
    with open(pack_root / "characters/character_manifest.json", "w", encoding="utf-8") as f:
        json.dump(character_manifest, f, indent=2)

    # B. Terrain Tileset
    terrain_tiles = generate_terrain_tiles()
    terrain_list = []
    for tname, (timg, tmeta) in terrain_tiles.items():
        timg.save(pack_root / "terrain/individual" / f"{tname}.png")
        terrain_list.append((tname, timg))

    terrain_atlas, terrain_mapping = pack_grid_atlas(terrain_list, 32, 32, cols=8)
    terrain_atlas.save(pack_root / "terrain/mars_terrain_tiles_32px.png")
    for entry in terrain_mapping:
        entry.update(terrain_tiles[entry["name"]][1])

    terrain_manifest = {
        "tileset_name": "mars_terrain_tiles_32px",
        "tile_width": 32,
        "tile_height": 32,
        "columns": 8,
        "rows": 4,
        "total_tiles": len(terrain_mapping),
        "atlas_file": "mars_terrain_tiles_32px.png",
        "tiles": terrain_mapping,
    }
    with open(pack_root / "terrain/terrain_manifest.json", "w", encoding="utf-8") as f:
        json.dump(terrain_manifest, f, indent=2)

    # C. Minerals & Items
    minerals, all_collectibles = generate_minerals_and_items()
    mineral_list = []
    for mname, mimg in minerals.items():
        mimg.save(pack_root / "minerals/individual" / f"{mname}.png")
        mineral_list.append((mname, mimg))
    minerals_atlas, minerals_map = pack_grid_atlas(mineral_list, 24, 24, cols=4)
    minerals_atlas.save(pack_root / "minerals/minerals_atlas.png")

    item_list = []
    for iname, iimg in all_collectibles.items():
        iimg.save(pack_root / "items/individual" / f"{iname}.png")
        item_list.append((iname, iimg))
    items_atlas, items_map = pack_grid_atlas(item_list, 24, 24, cols=5)
    items_atlas.save(pack_root / "items/items_atlas.png")

    # D. Environmental Objects
    objects = generate_environmental_objects()
    obj_list = []
    for oname, (oimg, ometa) in objects.items():
        oimg.save(pack_root / "objects/individual" / f"{oname}.png")
        obj_list.append((oname, oimg))
    objects_atlas, objects_map = pack_grid_atlas(obj_list, 64, 64, cols=5)
    objects_atlas.save(pack_root / "objects/objects_atlas.png")

    # E. Hazards & Effects
    hazards, effects = generate_hazards_and_effects()
    hazard_list = []
    for hname, himg in hazards.items():
        himg.save(pack_root / "hazards/individual" / f"{hname}.png")
        hazard_list.append((hname, himg))
    hazards_atlas, hazards_map = pack_grid_atlas(hazard_list, 32, 32, cols=6)
    hazards_atlas.save(pack_root / "hazards/hazards_atlas.png")

    effect_list = []
    for ename, eimg in effects.items():
        eimg.save(pack_root / "effects/individual" / f"{ename}.png")
        effect_list.append((ename, eimg))
    effects_atlas, effects_map = pack_grid_atlas(effect_list, 32, 32, cols=6)
    effects_atlas.save(pack_root / "effects/effects_atlas.png")

    # F. UI Assets
    icons, ui_icons_atlas, hud_bars, individual_bars, minimap_frame, controls_img = generate_ui_assets()
    ui_icons_atlas.save(pack_root / "ui/ui_icons.png")
    hud_bars.save(pack_root / "ui/hud_bars.png")
    minimap_frame.save(pack_root / "ui/minimap_frame.png")
    controls_img.save(pack_root / "ui/controls.png")
    for ic_name, ic_img in icons.items():
        ic_img.save(pack_root / "ui/individual" / f"{ic_name}.png")
    for b_name, b_img in individual_bars.items():
        b_img.save(pack_root / "ui/individual" / f"{b_name}.png")

    # G. Previews & Example Level (strictly nearest-neighbor)
    example_level_img, sample_tilemap = build_example_level(
        terrain_tiles, astronaut_frames, minerals, all_collectibles, objects, hazards, effects, icons
    )
    example_level_img.save(pack_root / "preview/example_level.png")
    with open(pack_root / "examples/sample_tilemap.json", "w", encoding="utf-8") as f:
        json.dump(sample_tilemap, f, indent=2)

    # Astronaut preview (4x nearest-neighbor enlargement showing walk, run, all 5 suit skins, and interactions)
    astro_prev_native = Image.new("RGBA", (256, 352), PAL["k"])
    astro_prev_native.alpha_composite(walk_sheet, (0, 0))
    astro_prev_native.alpha_composite(run_sheet, (128, 0))
    astro_prev_native.alpha_composite(skins_sheet, (0, 128))
    # Add sample interaction rows (scan_down, collect_down, tool_down, defeated_down) at y=288
    astro_prev_native.alpha_composite(inter_sheet.crop((0, 0, 128, 32)), (0, 288))      # scan down
    astro_prev_native.alpha_composite(inter_sheet.crop((0, 128, 128, 160)), (128, 288)) # collect down
    astro_prev_native.alpha_composite(inter_sheet.crop((0, 256, 128, 288)), (0, 320))   # tool down
    astro_prev_native.alpha_composite(inter_sheet.crop((0, 512, 128, 544)), (128, 320)) # defeated
    astro_prev = astro_prev_native.resize((256 * 3, 352 * 3), Image.NEAREST)
    astro_prev.save(pack_root / "preview/astronaut_preview.png")

    terrain_prev = terrain_atlas.resize((terrain_atlas.width * 4, terrain_atlas.height * 4), Image.NEAREST)
    terrain_prev.save(pack_root / "preview/terrain_preview.png")

    contact_native = Image.new("RGBA", (384, 320), PAL["k"])
    contact_native.alpha_composite(walk_sheet, (8, 8))
    contact_native.alpha_composite(terrain_atlas, (144, 8))
    contact_native.alpha_composite(minerals_atlas, (8, 144))
    contact_native.alpha_composite(items_atlas, (112, 144))
    contact_native.alpha_composite(ui_icons_atlas, (240, 144))
    contact_native.alpha_composite(hud_bars.resize((128, 18), Image.NEAREST), (240, 198))
    contact_native.alpha_composite(minimap_frame, (312, 224))
    contact_native.alpha_composite(objects["mars_rover"][0], (8, 224))
    contact_native.alpha_composite(objects["research_habitat"][0], (76, 224))
    contact_native.alpha_composite(objects["communication_tower"][0], (144, 224))
    contact_native.alpha_composite(hazards["sandstorm_hazard"], (200, 236))
    contact_native.alpha_composite(hazards["radiation_zone"], (236, 236))
    contact_native.alpha_composite(effects["scanning_pulse"], (272, 236))
    contact_sheet = contact_native.resize((384 * 3, 320 * 3), Image.NEAREST)
    contact_sheet.save(pack_root / "preview/asset_contact_sheet.png")

    # H. HTML5 Canvas Demo & Documentation
    html_demo = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>MarsPixelAssets — HTML5 Canvas Atlas & Tilemap Demo</title>
  <style>
    body {
      background: #18121c;
      color: #ecf2f8;
      font-family: monospace;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 24px;
    }
    canvas {
      image-rendering: pixelated;
      image-rendering: crisp-edges;
      border: 2px solid #38a8ee;
      background: #4e201c;
      margin-top: 12px;
    }
  </style>
</head>
<body>
  <h2>MarsPixelAssets — HTML5 Canvas Tile & Sprite Atlas Demo</h2>
  <p>Demonstrates loading <code>mars_terrain_tiles_32px.png</code> and <code>astronaut_walk_4_directions.png</code> with crisp nearest-neighbor rendering.</p>
  <canvas id="gameCanvas" width="512" height="384"></canvas>
  <script>
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;

    const TILE_SIZE = 32;
    const SCALE = 2;

    const terrainAtlas = new Image();
    terrainAtlas.src = '../terrain/mars_terrain_tiles_32px.png';

    const astroAtlas = new Image();
    astroAtlas.src = '../characters/astronaut_walk_4_directions.png';

    const TILES = {
      PLAIN: [0, 0],
      STONES: [1, 0],
      PATH_H: [0, 2],
      BLUE_ROCK: [2, 2],
      YELLOW_ROCK: [3, 2],
      CRATER_FLOOR: [7, 0]
    };

    const sampleGrid = [
      ['PLAIN', 'STONES', 'PLAIN', 'BLUE_ROCK', 'PLAIN', 'PLAIN', 'YELLOW_ROCK', 'PLAIN'],
      ['PLAIN', 'PLAIN', 'STONES', 'PLAIN', 'PLAIN', 'STONES', 'PLAIN', 'PLAIN'],
      ['PATH_H', 'PATH_H', 'PATH_H', 'PATH_H', 'PATH_H', 'PATH_H', 'PATH_H', 'PATH_H'],
      ['PLAIN', 'CRATER_FLOOR', 'CRATER_FLOOR', 'PLAIN', 'STONES', 'PLAIN', 'PLAIN', 'STONES'],
      ['PLAIN', 'CRATER_FLOOR', 'CRATER_FLOOR', 'PLAIN', 'PLAIN', 'BLUE_ROCK', 'PLAIN', 'PLAIN'],
      ['STONES', 'PLAIN', 'PLAIN', 'PLAIN', 'PLAIN', 'PLAIN', 'PLAIN', 'PLAIN']
    ];

    let frame = 0;
    function render() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      for (let r = 0; r < sampleGrid.length; r++) {
        for (let c = 0; c < sampleGrid[r].length; c++) {
          const [tc, tr] = TILES[sampleGrid[r][c]];
          ctx.drawImage(
            terrainAtlas,
            tc * TILE_SIZE, tr * TILE_SIZE, TILE_SIZE, TILE_SIZE,
            c * TILE_SIZE * SCALE, r * TILE_SIZE * SCALE, TILE_SIZE * SCALE, TILE_SIZE * SCALE
          );
        }
      }
      const walkCol = frame % 4;
      ctx.drawImage(
        astroAtlas,
        walkCol * TILE_SIZE, 3 * TILE_SIZE, TILE_SIZE, TILE_SIZE,
        3 * TILE_SIZE * SCALE, 2 * TILE_SIZE * SCALE - 8, TILE_SIZE * SCALE, TILE_SIZE * SCALE
      );
      frame++;
    }

    let loaded = 0;
    const onAssetLoad = () => {
      loaded++;
      if (loaded === 2) setInterval(render, 180);
    };
    terrainAtlas.onload = onAssetLoad;
    astroAtlas.onload = onAssetLoad;
  </script>
</body>
</html>
"""
    with open(pack_root / "examples/sample_atlas_usage.html", "w", encoding="utf-8") as f:
        f.write(html_demo)

    master_manifest = {
        "pack_name": "MarsPixelAssets",
        "version": "1.0.0",
        "style": "16-bit Top-Down Indie Pixel Art (Martian Exploration)",
        "palette_colors": len(PAL) - 1,
        "categories": {
            "characters": character_manifest,
            "terrain": terrain_manifest,
            "minerals": {
                "atlas": "minerals/minerals_atlas.png",
                "native_size": [24, 24],
                "sprites": minerals_map,
            },
            "items": {
                "atlas": "items/items_atlas.png",
                "native_size": [24, 24],
                "sprites": items_map,
            },
            "objects": {
                "atlas": "objects/objects_atlas.png",
                "cell_size": [64, 64],
                "sprites": objects_map,
            },
            "hazards": {
                "atlas": "hazards/hazards_atlas.png",
                "native_size": [32, 32],
                "sprites": hazards_map,
            },
            "effects": {
                "atlas": "effects/effects_atlas.png",
                "native_size": [32, 32],
                "sprites": effects_map,
            },
            "ui": {
                "ui_icons_atlas": "ui/ui_icons.png",
                "icon_size": [16, 16],
                "icons": list(icons.keys()),
                "hud_bars": "ui/hud_bars.png",
                "minimap_frame": "ui/minimap_frame.png",
                "controls": "ui/controls.png",
            },
        },
    }
    with open(pack_root / "asset_manifest.json", "w", encoding="utf-8") as f:
        json.dump(master_manifest, f, indent=2)

    readme_md = """# MarsPixelAssets — 2D Top-Down Mars Exploration Pixel-Art Asset Pack

A complete, game-ready 2D pixel-art asset library designed for a *Soul Knight*-inspired scientifically grounded Mars exploration game in HTML5 Canvas / JavaScript and standard 2D engines (Godot, Unity, Phaser, PixiJS).

## Key Specifications
- **True Native Pixel Grids**:
  - **Astronaut Character**: `32x32` pixels per frame (transparent PNGs)
  - **Mars Terrain Tileset**: `32x32` pixels per tile (32 tiles total: 24 core surface/geological tiles + 8 cliff/crater/path transition tiles)
  - **Minerals & Collectibles**: `24x24` pixels (`8` minerals & geological samples + `5` survival/scientific items = `13` collectibles)
  - **Environmental Objects & Props**: `32x32` (small props), `48x48` (storage container, ancient arch), `48x64` (comm tower), and `64x64` (Mars rover, research habitat dome)
  - **Hazards & Effects**: `32x32` pixels with multi-frame animations
  - **UI & HUD Icons**: `16x16` icons (`ui_icons.png`), `64x12` HUD bars (`hud_bars.png`), `64x64` minimap frame (`minimap_frame.png`), and touch/joystick controls (`controls.png`)
- **Restrained 16-Bit Palette**: 33 deliberate RGBA colors with hard-edged pixel clusters, consistent dark outlines (`#18121c`), and zero anti-aliasing.
- **Reproducibility**: Run `python3 generate_assets.py` with Pillow (`PIL`) to regenerate or customize any sprite, palette, or atlas.

## Directory Structure
- `characters/` — Directional sheets (`astronaut_down.png`, `astronaut_up.png`, `astronaut_left.png`, `astronaut_right.png`), `astronaut_walk_4_directions.png`, `astronaut_run_4_directions.png`, `astronaut_interactions.png`, `astronaut_alternate_skins.png`, `character_manifest.json`, and 152 individual frame PNGs in `characters/frames/`.
- `terrain/` — `mars_terrain_tiles_32px.png` (256x128 atlas), `terrain_manifest.json`, and 32 individual `32x32` PNG tiles in `terrain/individual/`.
- `minerals/` — `minerals_atlas.png` and individual `24x24` mineral/sample PNGs in `minerals/individual/`.
- `items/` — `items_atlas.png` and all 13 collectible individual `24x24` PNGs in `items/individual/`.
- `objects/` — `objects_atlas.png` and 17 individual prop/vehicle/building PNGs in `objects/individual/`.
- `hazards/` — `hazards_atlas.png` and 23 hazard base + animation frame PNGs in `hazards/individual/`.
- `effects/` — `effects_atlas.png` and 27 environmental effect frame PNGs in `effects/individual/`.
- `ui/` — `ui_icons.png`, `hud_bars.png`, `minimap_frame.png`, `controls.png`, and individual icons/bars in `ui/individual/`.
- `preview/` — Nearest-neighbor enlarged inspection sheets (`asset_contact_sheet.png`, `astronaut_preview.png`, `terrain_preview.png`, `example_level.png`).
- `examples/` — `sample_tilemap.json` and `sample_atlas_usage.html`.

## Scientific vs. Artistic Note
All sprites and the sample level layout (`examples/sample_tilemap.json`) are hand-crafted artistic pixel-art game assets inspired by Martian geology (basalt columns, ferric oxide dust, olivine/sulfur/azurite mineral veins, rover/habitat architecture) and are not direct exports of NASA orbital telemetry.
"""
    with open(pack_root / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_md)

    shutil.copyfile(__file__, pack_root / "generate_assets.py")

    # I. Package ZIP Archive & Copy Key Output Files
    zip_path = out_dir / "MarsPixelAssets.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(pack_root):
            for file in sorted(files):
                full_p = Path(root) / file
                rel_p = full_p.relative_to(inter_dir)
                zf.write(full_p, str(rel_p))

    for key_file in [
        pack_root / "preview/asset_contact_sheet.png",
        pack_root / "preview/astronaut_preview.png",
        pack_root / "preview/terrain_preview.png",
        pack_root / "preview/example_level.png",
    ]:
        shutil.copyfile(key_file, out_dir / key_file.name)

    print(f"SUCCESS: Generated MarsPixelAssets.zip at {zip_path} ({zip_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
