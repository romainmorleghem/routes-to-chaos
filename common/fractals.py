"""Escape-time fractals for the series (numba, parallel). One convention everywhere:
cream = bounded orbit, dark->purple->pink->orange = escape speed (same stops as Part 1).
"""
import math
import numpy as np
from numba import njit, prange
from matplotlib.colors import LinearSegmentedColormap

CREAM = np.array([255, 244, 214], np.uint8)
EXT_STOPS = ["#0E1116", "#2B2D6E", "#7A3E9D", "#E85D75", "#F2A541"]
EXT_CMAP = LinearSegmentedColormap.from_list("ext", EXT_STOPS)
# interior colour by period of the attracting cycle (1..8, then grey)
PERIOD_COLORS = np.array([
    [93, 169, 233],   # 1  blue (main cardioid)
    [108, 203, 139],  # 2  green
    [242, 165, 65],   # 3  orange
    [232, 93, 117],   # 4  pink
    [199, 146, 234],  # 5  violet
    [255, 214, 102],  # 6  yellow
    [120, 220, 220],  # 7  cyan
    [240, 128, 70],   # 8  red-orange
    [170, 170, 170],  # >8 grey
], np.uint8)


@njit(cache=True, fastmath=True)
def _escape(zr, zi, cr, ci, maxit):
    for k in range(maxit + 1):
        zr2, zi2 = zr * zr, zi * zi
        if zr2 + zi2 > 16.0:
            return max(k - math.log2(math.log(math.sqrt(zr2 + zi2))), 0.0), zr, zi
        zi = 2 * zr * zi + ci
        zr = zr2 - zi2 + cr
    return -1.0, zr, zi


@njit(parallel=True, cache=True, fastmath=True)
def mandelbrot(re0, re1, im0, im1, w, h, maxit):
    """Smooth escape count of the orbit of 0 for each c (-1 inside)."""
    out = np.empty((h, w), np.float64)
    for j in prange(h):
        ci = im1 - (j + 0.5) / h * (im1 - im0)
        for i in range(w):
            cr = re0 + (i + 0.5) / w * (re1 - re0)
            out[j, i] = _escape(0.0, 0.0, cr, ci, maxit)[0]
    return out


@njit(parallel=True, cache=True, fastmath=True)
def julia(re0, re1, im0, im1, w, h, cr, ci, maxit):
    """Smooth escape count of the orbit of each z0 for fixed c (-1 inside K_c)."""
    out = np.empty((h, w), np.float64)
    for j in prange(h):
        zi0 = im1 - (j + 0.5) / h * (im1 - im0)
        for i in range(w):
            zr0 = re0 + (i + 0.5) / w * (re1 - re0)
            out[j, i] = _escape(zr0, zi0, cr, ci, maxit)[0]
    return out


@njit(parallel=True, cache=True)
def mandelbrot_period(re0, re1, im0, im1, w, h, maxit, maxp):
    """Period of the attracting cycle reached by the orbit of 0 (0 = escapes, -1 = not detected)."""
    out = np.zeros((h, w), np.int32)
    for j in prange(h):
        ci = im1 - (j + 0.5) / h * (im1 - im0)
        for i in range(w):
            cr = re0 + (i + 0.5) / w * (re1 - re0)
            zr, zi = 0.0, 0.0
            esc = False
            for _ in range(maxit):
                zr, zi = zr * zr - zi * zi + cr, 2 * zr * zi + ci
                if zr * zr + zi * zi > 16.0:
                    esc = True
                    break
            if esc:
                continue
            ar, ai = zr, zi
            p = -1
            for k in range(1, maxp + 1):
                zr, zi = zr * zr - zi * zi + cr, 2 * zr * zi + ci
                if (zr - ar) ** 2 + (zi - ai) ** 2 < 1e-12:
                    p = k
                    break
            out[j, i] = p
    return out


@njit(parallel=True, cache=True, fastmath=True)
def julia_mosaic(re0, re1, im0, im1, w, h, nx, ny, maxit, zr_half):
    """Tile the c-window into nx*ny tiles; each tile shows K_c for c = tile centre, z in [-zr,zr]^2."""
    out = np.empty((h, w), np.float64)
    tw, th = w / nx, h / ny
    for j in prange(h):
        ty = int(j / th)
        ci = im1 - (ty + 0.5) / ny * (im1 - im0)
        v = ((j - ty * th) + 0.5) / th
        zi0 = zr_half * (1 - 2 * v) * (th / tw if th < tw else 1.0)
        for i in range(w):
            tx = int(i / tw)
            cr = re0 + (tx + 0.5) / nx * (re1 - re0)
            u = ((i - tx * tw) + 0.5) / tw
            zr0 = zr_half * (2 * u - 1) * (tw / th if tw < th else 1.0)
            out[j, i] = _escape(zr0, zi0, cr, ci, maxit)[0]
    return out


def colorize(esc, maxit=250, mode="ep1", lo=None, hi=None):
    """esc -> RGB. mode 'ep1' reproduces Part 1's epilogue colouring exactly;
    mode 'adaptive' stretches log(escape) between percentiles (deep zooms)."""
    inside = esc < 0
    e = np.where(inside, 0.0, esc)
    if mode == "ep1":
        v = np.clip(np.log1p(e) / np.log1p(maxit) * 1.6, 0, 1)
    else:
        le = np.log1p(e)
        if lo is None or hi is None:
            vals = le[~inside]
            lo, hi = (np.percentile(vals, [1, 99.5]) if vals.size else (0, 1))
        v = np.clip((le - lo) / max(hi - lo, 1e-9), 0, 1) ** 0.8
    rgb = (EXT_CMAP(v)[..., :3] * 255).astype(np.uint8)
    rgb[inside] = CREAM
    return rgb


def period_rgb(esc_rgb, per):
    out = esc_rgb.copy()
    m = per != 0
    idx = np.clip(np.where(per < 0, 9, per), 1, 9) - 1
    out[m] = PERIOD_COLORS[idx[m]]
    return out


def adaptive_range(esc):
    le = np.log1p(esc[esc >= 0])
    return tuple(np.percentile(le, [1, 99.5])) if le.size else (0.0, 1.0)
