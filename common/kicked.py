"""Standard map  p' = p + K sin(theta),  theta' = theta + p'  and the quantum kicked rotor."""
import numpy as np
from numba import njit, prange

TWO_PI = 2 * np.pi


@njit(cache=True)
def orbit(th, p, K, n):
    """n iterates on the torus [0,2pi)^2"""
    out = np.empty((n, 2))
    for i in range(n):
        p = (p + K * np.sin(th)) % TWO_PI
        th = (th + p) % TWO_PI
        out[i, 0] = th
        out[i, 1] = p
    return out


@njit(cache=True)
def lift_step(th, p, K, n):
    """n kicks on the cylinder (p unbounded), theta mod 2pi"""
    for i in range(n):
        p = p + K * np.sin(th)
        th = (th + p) % TWO_PI
    return th, p


@njit(parallel=True, cache=True)
def spread(th0, p0, K, n, every):
    """<(p - p0)^2> every `every` kicks for an ensemble on the cylinder"""
    m = th0.size
    nout = n // every
    acc = np.zeros((m, nout))
    for j in prange(m):
        th, p = th0[j], p0[j]
        for k in range(nout):
            th, p = lift_step(th, p, K, every)
            acc[j, k] = (p - p0[j]) ** 2
    return acc.sum(axis=0) / m


@njit(cache=True)
def monodromy(th, p, K, q):
    """iterate q steps on the lift, return final state and the tangent matrix"""
    a, b, c, d = 1.0, 0.0, 0.0, 1.0     # [[dth/dth0, dth/dp0], [dp/dth0, dp/dp0]]
    for i in range(q):
        k = K * np.cos(th)
        c, d = c + k * a, d + k * b      # dp' = dp + K cos(th) dth
        a, b = a + c, b + d              # dth' = dth + dp'
        p = p + K * np.sin(th)
        th = th + p
    return th, p, a, b, c, d


def periodic(th, p, K, q, P, tol=1e-12, it=60):
    """Newton for an orbit with T^q(th,p) = (th + 2 pi P, p) on the lift. returns (th, p, trace) or None"""
    for _ in range(it):
        t1, p1, a, b, c, d = monodromy(th, p, K, q)
        F = np.array([t1 - th - TWO_PI * P, p1 - p])
        J = np.array([[a - 1, b], [c, d - 1]])
        try:
            dx = np.linalg.solve(J, -F)
        except np.linalg.LinAlgError:
            return None
        th, p = th + dx[0], p + dx[1]
        if not np.isfinite(th) or abs(dx).max() < tol:
            break
    t1, p1, a, b, c, d = monodromy(th, p, K, q)
    if abs(t1 - th - TWO_PI * P) + abs(p1 - p) > 1e-8:
        return None
    return th, p, a + d, np.array([[a, b], [c, d]])


# ---------------------------------------------------------------- quantum kicked rotor
def qkr(k, tau, n, N=4096, beta=0.0, record=()):
    """psi_m, m in [-N/2, N/2): kick exp(-i k cos th), free exp(-i tau (m+beta)^2 / 2).
    returns <m^2>(t) for t = 0..n and |psi_m|^2 snapshots at the requested times"""
    m = np.fft.fftfreq(N, 1.0 / N)
    th = TWO_PI * np.arange(N) / N
    kick = np.exp(-1j * k * np.cos(th))
    free = np.exp(-1j * tau * (m + beta) ** 2 / 2)
    psi = np.zeros(N, complex); psi[0] = 1.0
    m2 = np.empty(n + 1); m2[0] = 0.0
    snaps = {}
    for t in range(1, n + 1):
        psi = np.fft.fft(np.fft.ifft(psi) * kick)
        psi *= free
        pr = np.abs(psi) ** 2
        m2[t] = (pr * m ** 2).sum() / pr.sum()
        if t in record:
            snaps[t] = np.fft.fftshift(pr / pr.sum())
    return m2, snaps, np.fft.fftshift(m)
