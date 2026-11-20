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
                        transient=2000, samples=1500, x0=0.5):
    """Return a (height, width) array of visit densities, one column per r."""
    r = np.linspace(r_min, r_max, width)
    x = np.full(width, x0)
    for _ in range(transient):
        x = r * x * (1.0 - x)
    img = np.zeros((height, width))
    cols = np.arange(width)
    scale = (height - 1) / (x_max - x_min)
    for _ in range(samples):
        x = r * x * (1.0 - x)
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
