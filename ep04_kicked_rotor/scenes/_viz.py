"""Phase portraits of the standard map / area-preserving Henon map as images, and a labelled frame."""
import numpy as np
from numba import njit
from manim import (ImageMobject, VGroup, Rectangle, Line, MathTex, config, UP, DOWN, LEFT, RIGHT)
from common.style import FG, MUTED

PI = np.pi
REG = ["#5DA9E9", "#6CCB8B", "#C792EA", "#F2A541", "#7FD1C7"]   # regular orbits (tori, islands)
CHAOS = "#E85D75"                                                # chaotic sea


@njit(cache=True)
def _orbits_std(th0, p0, K, n):
    """standard map, p shown in [-pi, pi). returns points (m*n, 2) and a Lyapunov estimate per orbit"""
    m = th0.size
    pts = np.empty((m * n, 2))
    lyap = np.empty(m)
    tp = 2 * PI
    for j in range(m):
        th, p = th0[j], p0[j]
        u, v = 1.0, 0.0
        s = 0.0
        for i in range(n):
            k = K * np.cos(th)
            v = v + k * u
            u = u + v
            nr = np.sqrt(u * u + v * v)
            s += np.log(nr)
            u /= nr; v /= nr
            p = p + K * np.sin(th)
            th = (th + p) % tp
            p = (p + PI) % tp - PI
            pts[j * n + i, 0] = th
            pts[j * n + i, 1] = p
        lyap[j] = s / n
    return pts, lyap


@njit(cache=True)
def _orbits_henon(x0, y0, a, n):
    m = x0.size
    pts = np.full((m * n, 2), np.nan)
    lyap = np.zeros(m)
    for j in range(m):
        x, y = x0[j], y0[j]
        u, v = 1.0, 0.0
        s = 0.0
        for i in range(n):
            u, v = -2 * a * x * u + v, -u
            nr = np.sqrt(u * u + v * v)
            s += np.log(nr)
            u /= nr; v /= nr
            x, y = 1 - a * x * x + y, -x
            if abs(x) > 8:
                lyap[j] = -1.0
                for t in range(n):
                    pts[j * n + t, 0] = np.nan
                break
            pts[j * n + i, 0] = x
            pts[j * n + i, 1] = y
        if lyap[j] == 0.0:
            lyap[j] = s / n
    return pts, lyap


@njit(cache=True)
def _splat_rgb(xs, ys, cols, w, h, x0, x1, y0, y1):
    img = np.zeros((h, w, 3))
    cnt = np.zeros((h, w))
    for i in range(xs.size):
        if not np.isfinite(xs[i]):
            continue
        fx = (xs[i] - x0) / (x1 - x0) * w
        fy = (y1 - ys[i]) / (y1 - y0) * h
        ix, iy = int(fx), int(fy)
        if 0 <= ix < w and 0 <= iy < h:
            cnt[iy, ix] += 1
            for c in range(3):
                img[iy, ix, c] += cols[i, c]
    return img, cnt


def hexrgb(c):
    return np.array([int(c[i:i + 2], 16) for i in (1, 3, 5)], float)


def to_image(pts, orbit_cols, n, x_range, y_range, width, height, res=None, gain=1.0, gamma=0.45):
    if res is None:
        res = int(config.pixel_width * width / config.frame_width)
    w = max(res, 32); h = int(w * height / width)
    cols = np.repeat(orbit_cols, n, axis=0)
    img, cnt = _splat_rgb(pts[:, 0].copy(), pts[:, 1].copy(), cols, w, h, *x_range, *y_range)
    rgba = np.zeros((h, w, 4), np.uint8)
    nz = cnt > 0
    rgba[nz, :3] = np.clip(img[nz] / cnt[nz][:, None], 0, 255).astype(np.uint8)
    ref = np.percentile(cnt[nz], 90) if nz.any() else 1
    rgba[..., 3] = (np.clip(gain * cnt / ref, 0, 1) ** gamma * 255).astype(np.uint8)
    im = ImageMobject(rgba)
    im.stretch_to_fit_width(width).stretch_to_fit_height(height)
    return im


def std_ics(n_line=90, n_rand=60, seed=0):
    rng = np.random.default_rng(seed)
    p = np.linspace(-PI, PI, n_line, endpoint=False) + 1e-3
    th = np.concatenate([np.full(n_line // 2, PI), np.full(n_line - n_line // 2, 0.0), rng.random(n_rand) * 2 * PI])
    pp = np.concatenate([p[::2], p[1::2], (rng.random(n_rand) - 0.5) * 2 * PI])
    return th, pp


def portrait(K, width=6.4, height=6.4, n=1500, ics=None, thr=0.03, chaos=CHAOS, gain=1.0, res=None,
             single=None, box=None, m=200):
    if box is not None:
        rng = np.random.default_rng(5)
        ics = (rng.uniform(*box[0], m), rng.uniform(*box[1], m))
    th, pp = std_ics() if ics is None else ics
    pts, ly = _orbits_std(th.astype(float), pp.astype(float), float(K), n)
    cols = np.empty((th.size, 3))
    for j in range(th.size):
        if single is not None:
            cols[j] = hexrgb(single)
        else:
            cols[j] = hexrgb(chaos) if ly[j] > thr else hexrgb(REG[j % len(REG)])
    xr, yr = ((0, 2 * PI), (-PI, PI)) if box is None else box
    return to_image(pts, cols, n, xr, yr, width, height, res=res, gain=gain)


def henon_fixed(a):
    x = (-1 + np.sqrt(1 + a)) / a
    return x, -x


def henon_portrait(a, width, height, xr=(-0.4, 1.0), yr=(-1.0, 0.4), n=1500, m=2500, seed=0, gain=1.0,
                   view=None):
    rng = np.random.default_rng(seed)
    xf, yf = henon_fixed(a)
    x0 = rng.uniform(*xr, m); y0 = rng.uniform(*yr, m)
    pts, ly = _orbits_henon(x0, y0, float(a), n)
    cols = np.array([hexrgb(CHAOS) if l > 0.03 else hexrgb(REG[j % len(REG)]) for j, l in enumerate(ly)])
    return to_image(pts, cols, n, view[0] if view else xr, view[1] if view else yr, width, height, gain=gain)


class Frame(VGroup):
    """box for theta in [0, 2pi] (x) and p in [-pi, pi] (y) with labels"""

    def __init__(self, width=6.4, height=6.4, center=(0, 0, 0), labels=True, fs=26):
        super().__init__()
        self.w, self.h, self.c = width, height, np.array(center, float)
        box = Rectangle(width=width, height=height, stroke_color=MUTED, stroke_width=1.5).move_to(center)
        self.add(box)
        if labels:
            for v, t in ((0, "0"), (PI, r"\pi"), (2 * PI, r"2\pi")):
                self.add(MathTex(t, font_size=fs, color=MUTED).next_to(self.c2p(v, -PI), DOWN, buff=0.12))
            for v, t in ((-PI, r"-\pi"), (0, "0"), (PI, r"\pi")):
                self.add(MathTex(t, font_size=fs, color=MUTED).next_to(self.c2p(0, v), LEFT, buff=0.12))
            self.add(MathTex(r"\theta", font_size=fs + 4, color=FG).next_to(self.c2p(2 * PI, -PI), RIGHT,
                                                                           buff=0.2))
            self.add(MathTex(r"p", font_size=fs + 4, color=FG).next_to(self.c2p(0, PI), UP, buff=0.15))

    def c2p(self, th, p):
        return self.c + np.array([(th / (2 * PI) - 0.5) * self.w, (p / (2 * PI)) * self.h, 0])


def golden_orbit(K, P=610, q=987, th0=PI):
    """points of the symmetric P/q orbit (Fibonacci approximant of the golden curve), by 1-D shooting"""
    from common.kicked import monodromy, orbit
    p0 = 2 * PI * P / q
    for k in np.linspace(0.05, K, 60):
        m = q // 2 if q % 2 == 0 else (q + 1) // 2
        for _ in range(50):
            t, p, a, b, c, d = monodromy(th0, p0, k, m)
            g, dg = (t - th0 - PI * P, b) if q % 2 == 0 else (2 * t - p - 2 * th0 - 2 * PI * P, 2 * b - d)
            p0 -= g / dg
            if abs(g / dg) < 1e-14:
                break
    o = orbit(th0, p0, K, q)
    o[:, 1] = (o[:, 1] + PI) % (2 * PI) - PI
    return o


@njit(cache=True)
def lift_p(th, p, K, n):
    out = np.empty(n)
    for i in range(n):
        p = p + K * np.sin(th)
        th = (th + p) % (2 * PI)
        out[i] = p
    return out
