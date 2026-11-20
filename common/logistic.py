"""Numerics for the logistic map f_r(x) = r x (1 - x). Vectorised numpy."""
import numpy as np

DELTA = 4.669201609102990
ALPHA = -2.502907875095892
R_INF = 3.569945671870945


def f(r, x):
    return r * x * (1.0 - x)


def orbit(r, x0, n):
    xs = np.empty(n + 1)
    xs[0] = x0
    for i in range(n):
        xs[i + 1] = f(r, xs[i])
    return xs


def bifurcation_density(r_min, r_max, x_min, x_max, width, height,
                        transient=2000, samples=1500, x0=0.5, fn=None):
    """Return a (height, width) array of visit densities, one column per r.

    `fn(r, x)` is the (vectorised) map; default is the logistic map."""
    fn = fn or f
    r = np.linspace(r_min, r_max, width)
    x = np.full(width, x0, dtype=float)
    for _ in range(transient):
        x = fn(r, x)
    img = np.zeros((height, width))
    cols = np.arange(width)
    scale = (height - 1) / (x_max - x_min)
    for _ in range(samples):
        x = fn(r, x)
        row = np.round((x_max - x) * scale).astype(int)
        ok = (row >= 0) & (row < height)
        np.add.at(img, (row[ok], cols[ok]), 1.0)
    return img


def density_to_rgb(img, stops, gamma=0.45):
    """Map densities to RGB uint8 with a log-ish tone curve."""
    from matplotlib.colors import LinearSegmentedColormap
    cmap = LinearSegmentedColormap.from_list("rtc", stops)
    col_max = img.max(axis=0, keepdims=True)
    col_max[col_max == 0] = 1
    v = (img / col_max) ** gamma
    return (cmap(v)[..., :3] * 255).astype(np.uint8)


def lyapunov(r, transient=1000, n=4000, x0=0.5):
    r = np.atleast_1d(np.asarray(r, float))
    x = np.full_like(r, x0)
    for _ in range(transient):
        x = r * x * (1 - x)
    acc = np.zeros_like(r)
    for _ in range(n):
        x = r * x * (1 - x)
        acc += np.log(np.abs(r * (1 - 2 * x)) + 1e-300)
    return acc / n


def orbit_fn(fn, r, x0, n):
    xs = np.empty(n + 1)
    xs[0] = x0
    for i in range(n):
        xs[i + 1] = fn(r, xs[i])
    return xs


def mandelbrot_escape(re_min, re_max, im_min, im_max, width, height, iters=300):
    """Smooth escape-time values (nan inside the set)."""
    c = (np.linspace(re_min, re_max, width)[None, :]
         + 1j * np.linspace(im_max, im_min, height)[:, None])
    z = np.zeros_like(c)
    out = np.full(c.shape, np.nan)
    alive = np.ones(c.shape, bool)
    for k in range(iters):
        z[alive] = z[alive] ** 2 + c[alive]
        esc = alive & (np.abs(z) > 4)
        out[esc] = k + 1 - np.log2(np.log(np.abs(z[esc])))
        alive &= ~esc
    return out
