"""Shared visual vocabulary of Part 3: 3-D Lorenz curves drawn in 2-D by our own projection
(full control of the camera, same flat style as Parts 1-2), and glowing density images for clouds."""
import numpy as np
from numba import njit
from manim import VMobject, ImageMobject, VGroup, Dot, config
from common.style import BG, FG, MUTED, MAP, DIAG, ORBIT, ACCENT, STABLE, DENSITY_STOPS
from common.lorenz import trajectory, SIGMA, RHO, BETA

SCALE = 0.112                     # Lorenz units -> scene units (fits under the equations)
CENTER3 = np.array([0.0, 0.0, 25.0])
SCREEN0 = np.array([0.0, -0.1, 0.0])
TRAIL = [DIAG, ACCENT, ORBIT, MAP]      # palette ramp along a trajectory (same as Part 2's teaser)


def rot(yaw, pitch):
    """Camera: yaw about the vertical z axis, then tilt by pitch. Screen x = rotated x, screen y = z."""
    cy, sy, cp, sp = np.cos(yaw), np.sin(yaw), np.cos(pitch), np.sin(pitch)
    Rz = np.array([[cy, -sy, 0], [sy, cy, 0], [0, 0, 1]])
    Rx = np.array([[1, 0, 0], [0, cp, -sp], [0, sp, cp]])
    return Rx @ Rz


def project(P, yaw=0.0, pitch=0.0, scale=SCALE, center=CENTER3, screen=SCREEN0):
    """(N,3) Lorenz coordinates -> (N,3) scene points (orthographic). Default view = the classic x-z butterfly."""
    Q = (np.atleast_2d(P) - center) @ rot(yaw, pitch).T
    out = np.zeros_like(Q)
    out[:, 0] = Q[:, 0] * scale
    out[:, 1] = Q[:, 2] * scale
    return out + screen


def curve(P, yaw=0.0, pitch=0.0, width=1.6, colors=TRAIL, opacity=1.0, **kw):
    pts = project(P, yaw, pitch, **kw)
    c = VMobject(stroke_width=width, stroke_opacity=opacity)
    c.set_points_as_corners(pts)
    if colors is not None:
        c.set_stroke(color=list(colors) if isinstance(colors, (list, tuple)) else colors)
    return c


def lorenz_points(p0=(1.0, 1.0, 1.0), T=40.0, dt=0.004, skip=0.0, r=RHO, s=SIGMA, b=BETA):
    tr = trajectory(np.array(p0, float), int((T + skip) / dt), dt, s, r, b)
    return tr[int(skip / dt):]


@njit(cache=True)
def _splat(xs, ys, w, h, x0, x1, y0, y1, wts):
    img = np.zeros((h, w))
    for i in range(xs.size):
        fx = (xs[i] - x0) / (x1 - x0) * w
        fy = (y1 - ys[i]) / (y1 - y0) * h
        ix, iy = int(fx), int(fy)
        if 0 <= ix < w - 1 and 0 <= iy < h - 1:
            ax, ay = fx - ix, fy - iy
            img[iy, ix] += (1 - ax) * (1 - ay) * wts[i]
            img[iy, ix + 1] += ax * (1 - ay) * wts[i]
            img[iy + 1, ix] += (1 - ax) * ay * wts[i]
            img[iy + 1, ix + 1] += ax * ay * wts[i]
    return img


def _ramp(t, stops=DENSITY_STOPS):
    cols = np.array([[int(c[i:i + 2], 16) for i in (1, 3, 5)] for c in stops], float)
    t = np.clip(t, 0, 1) * (len(cols) - 1)
    i = np.minimum(t.astype(int), len(cols) - 2)
    a = (t - i)[..., None]
    return (cols[i] * (1 - a) + cols[i + 1] * a).astype(np.uint8)


def glow_image(P, yaw=0.0, pitch=0.0, width=14.2, height=8.0, at=(0.0, 0.0), res=None,
               gain=1.0, weights=None, stops=DENSITY_STOPS, **kw):
    """Density image of a 3-D point set, as an ImageMobject covering width x height scene units."""
    if res is None:
        res = int(config.pixel_width * width / config.frame_width)
    w = max(res, 32)
    h = int(w * height / width)
    S = project(P, yaw, pitch, **kw)
    cx, cy = at
    wts = np.ones(len(S)) if weights is None else np.asarray(weights, float)
    img = _splat(S[:, 0].copy(), S[:, 1].copy(), w, h, cx - width / 2, cx + width / 2,
                 cy - height / 2, cy + height / 2, wts)
    # light blur (2 passes of a 3x3 box) so splats read as glow, not pixels
    for _ in range(2):
        img = (img + np.roll(img, 1, 0) + np.roll(img, -1, 0)) / 3
        img = (img + np.roll(img, 1, 1) + np.roll(img, -1, 1)) / 3
    ref = np.percentile(img[img > 0], 99.5) if np.any(img > 0) else 1.0
    t = np.log1p(gain * 30 * img / ref) / np.log1p(gain * 30)
    rgb = _ramp(t, stops)
    alpha = (np.clip(t * 3, 0, 1) * 255).astype(np.uint8)
    im = ImageMobject(np.dstack([rgb, alpha]))
    im.stretch_to_fit_width(width).stretch_to_fit_height(height).move_to([cx, cy, 0])
    return im


def comet(P, yaw=0.0, pitch=0.0, color=ORBIT, width=3.0, n_seg=12, **kw):
    """Trajectory piece drawn with a fading tail (older = dimmer)."""
    pts = project(P, yaw, pitch, **kw)
    g = VGroup()
    k = max(len(pts) // n_seg, 2)
    for j in range(n_seg):
        seg = pts[j * k:(j + 1) * k + 1]
        if len(seg) < 2:
            continue
        m = VMobject(stroke_width=width * (0.3 + 0.7 * (j + 1) / n_seg), stroke_color=color,
                     stroke_opacity=(j + 1) / n_seg)
        m.set_points_as_corners(seg)
        g.add(m)
    head = Dot(pts[-1], radius=0.06, color=color)
    return VGroup(g, head)


def raster_points(xs, ys, x_range, y_range, width, height, color_hex="#E6E6E6", res=None, gain=1.0):
    """Scatter of many 2-D points as an ImageMobject (for bifurcation diagrams, sections...)."""
    if res is None:
        res = int(config.pixel_width * width / config.frame_width)
    w = max(res, 32)
    h = int(w * height / width)
    img = _splat(np.asarray(xs, float), np.asarray(ys, float), w, h, x_range[0], x_range[1],
                 y_range[0], y_range[1], np.ones(len(xs)))
    ref = np.percentile(img[img > 0], 95) if np.any(img > 0) else 1.0
    a = np.clip(gain * img / ref, 0, 1) ** 0.6
    c = np.array([int(color_hex[i:i + 2], 16) for i in (1, 3, 5)], np.uint8)
    rgba = np.zeros((h, w, 4), np.uint8)
    rgba[..., :3] = c
    rgba[..., 3] = (a * 255).astype(np.uint8)
    im = ImageMobject(rgba)
    im.stretch_to_fit_width(width).stretch_to_fit_height(height)
    return im


def fit_view(P, yaw, pitch, width, height, margin=0.9):
    """center/scale so that the projected point set fills a width x height box."""
    Q = (P - P.mean(0)) @ rot(yaw, pitch).T
    sx = width / (np.ptp(Q[:, 0]) + 1e-9)
    sy = height / (np.ptp(Q[:, 2]) + 1e-9)
    c = P.mean(0)
    mid = np.array([Q[:, 0].min() + Q[:, 0].max(), 0, Q[:, 2].min() + Q[:, 2].max()]) / 2
    c = c + rot(yaw, pitch).T @ mid
    return dict(center=c, scale=margin * min(sx, sy))
