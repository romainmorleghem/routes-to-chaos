"""Lorenz system (and friends): fast numba integrators shared by Part 3's scenes, compute scripts and checks."""
import numpy as np
from numba import njit

SIGMA, RHO, BETA = 10.0, 28.0, 8.0 / 3.0


@njit(cache=True)
def _rhs(x, y, z, s, r, b):
    return s * (y - x), x * (r - z) - y, x * y - b * z


@njit(cache=True)
def trajectory(p0, n, dt, s=SIGMA, r=RHO, b=BETA):
    """RK4, returns (n+1, 3) array."""
    out = np.empty((n + 1, 3))
    x, y, z = p0[0], p0[1], p0[2]
    out[0] = x, y, z
    for i in range(n):
        k1 = _rhs(x, y, z, s, r, b)
        k2 = _rhs(x + .5 * dt * k1[0], y + .5 * dt * k1[1], z + .5 * dt * k1[2], s, r, b)
        k3 = _rhs(x + .5 * dt * k2[0], y + .5 * dt * k2[1], z + .5 * dt * k2[2], s, r, b)
        k4 = _rhs(x + dt * k3[0], y + dt * k3[1], z + dt * k3[2], s, r, b)
        x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        y += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        z += dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        out[i + 1] = x, y, z
    return out


@njit(cache=True)
def cloud(P, n, dt, s=SIGMA, r=RHO, b=BETA):
    """Advance an (N,3) cloud of points n RK4 steps in place."""
    for j in range(P.shape[0]):
        x, y, z = P[j, 0], P[j, 1], P[j, 2]
        for i in range(n):
            k1 = _rhs(x, y, z, s, r, b)
            k2 = _rhs(x + .5 * dt * k1[0], y + .5 * dt * k1[1], z + .5 * dt * k1[2], s, r, b)
            k3 = _rhs(x + .5 * dt * k2[0], y + .5 * dt * k2[1], z + .5 * dt * k2[2], s, r, b)
            k4 = _rhs(x + dt * k3[0], y + dt * k3[1], z + dt * k3[2], s, r, b)
            x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
            y += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
            z += dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        P[j, 0], P[j, 1], P[j, 2] = x, y, z
    return P


@njit(cache=True)
def z_maxima(p0, n, dt, skip, s=SIGMA, r=RHO, b=BETA):
    """Successive local maxima of z (parabolic refinement), after `skip` transient steps."""
    tr = trajectory(p0, n, dt, s, r, b)
    out = np.empty(n)
    m = 0
    for i in range(max(skip, 1), n):
        a, c, e = tr[i - 1, 2], tr[i, 2], tr[i + 1, 2]
        if c > a and c >= e:
            den = a - 2 * c + e
            out[m] = c - 0.125 * (a - e) ** 2 / den if den != 0 else c
            m += 1
    return out[:m]


@njit(cache=True)
def lyapunov_spectrum(p0, T, dt, s=SIGMA, r=RHO, b=BETA, transient=50.0):
    """Benettin/QR method with RK4 on the variational equations. Returns the 3 exponents."""
    x, y, z = p0[0], p0[1], p0[2]
    Q = np.eye(3)
    acc = np.zeros(3)
    nT = int(transient / dt)
    n = int(T / dt)
    for i in range(nT + n):
        # RK4 on state + tangent: d/dt Q = J(x) Q
        def J(x, y, z):
            return np.array([[-s, s, 0.0], [r - z, -1.0, -x], [y, x, -b]])
        k1 = _rhs(x, y, z, s, r, b); K1 = J(x, y, z) @ Q
        x2, y2, z2 = x + .5 * dt * k1[0], y + .5 * dt * k1[1], z + .5 * dt * k1[2]
        k2 = _rhs(x2, y2, z2, s, r, b); K2 = J(x2, y2, z2) @ (Q + .5 * dt * K1)
        x3, y3, z3 = x + .5 * dt * k2[0], y + .5 * dt * k2[1], z + .5 * dt * k2[2]
        k3 = _rhs(x3, y3, z3, s, r, b); K3 = J(x3, y3, z3) @ (Q + .5 * dt * K2)
        x4, y4, z4 = x + dt * k3[0], y + dt * k3[1], z + dt * k3[2]
        k4 = _rhs(x4, y4, z4, s, r, b); K4 = J(x4, y4, z4) @ (Q + dt * K3)
        x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        y += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        z += dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        Q = Q + dt / 6 * (K1 + 2 * K2 + 2 * K3 + K4)
        Q, R = np.linalg.qr(Q)
        for k in range(3):
            if R[k, k] < 0:
                R[k, k] = -R[k, k]
                Q[:, k] = -Q[:, k]
            if i >= nT:
                acc[k] += np.log(R[k, k])
    return acc / (n * dt)


def fixed_points(r=RHO, s=SIGMA, b=BETA):
    pts = [np.zeros(3)]
    if r > 1:
        q = np.sqrt(b * (r - 1))
        pts += [np.array([q, q, r - 1]), np.array([-q, -q, r - 1])]
    return pts


def jacobian(p, r=RHO, s=SIGMA, b=BETA):
    x, y, z = p
    return np.array([[-s, s, 0.0], [r - z, -1.0, -x], [y, x, -b]])


RHO_HOPF = SIGMA * (SIGMA + BETA + 3) / (SIGMA - BETA - 1)      # ≈ 24.7368


# ---- other attractors (gallery) -------------------------------------------------------------
@njit(cache=True)
def _rhs_any(kind, x, y, z):
    if kind == 0:      # Roessler a=b=0.2, c=5.7
        return -y - z, x + 0.2 * y, 0.2 + z * (x - 5.7)
    if kind == 1:      # Thomas b=0.208186
        b = 0.208186
        return np.sin(y) - b * x, np.sin(z) - b * y, np.sin(x) - b * z
    if kind == 2:      # Aizawa
        a, b, c, d, e, f = 0.95, 0.7, 0.6, 3.5, 0.25, 0.1
        return ((z - b) * x - d * y, d * x + (z - b) * y,
                c + a * z - z ** 3 / 3 - (x * x + y * y) * (1 + e * z) + f * z * x ** 3)
    # Halvorsen a=1.89
    a = 1.89
    return (-a * x - 4 * y - 4 * z - y * y, -a * y - 4 * z - 4 * x - z * z, -a * z - 4 * x - 4 * y - x * x)


@njit(cache=True)
def trajectory_any(kind, p0, n, dt):
    out = np.empty((n + 1, 3))
    x, y, z = p0[0], p0[1], p0[2]
    out[0] = x, y, z
    for i in range(n):
        k1 = _rhs_any(kind, x, y, z)
        k2 = _rhs_any(kind, x + .5 * dt * k1[0], y + .5 * dt * k1[1], z + .5 * dt * k1[2])
        k3 = _rhs_any(kind, x + .5 * dt * k2[0], y + .5 * dt * k2[1], z + .5 * dt * k2[2])
        k4 = _rhs_any(kind, x + dt * k3[0], y + dt * k3[1], z + dt * k3[2])
        x += dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        y += dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        z += dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        out[i + 1] = x, y, z
    return out


@njit(cache=True)
def section_return(p, dt, zs, s=SIGMA, r=RHO, b=BETA, nmax=200000):
    """Flow from p (on the plane z=zs, going up) to the next upward crossing of z=zs. Returns (point, time)."""
    x, y, z = p[0], p[1], p[2]
    t = 0.0
    for i in range(nmax):
        k1 = _rhs(x, y, z, s, r, b)
        k2 = _rhs(x + .5 * dt * k1[0], y + .5 * dt * k1[1], z + .5 * dt * k1[2], s, r, b)
        k3 = _rhs(x + .5 * dt * k2[0], y + .5 * dt * k2[1], z + .5 * dt * k2[2], s, r, b)
        k4 = _rhs(x + dt * k3[0], y + dt * k3[1], z + dt * k3[2], s, r, b)
        nx = x + dt / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
        ny = y + dt / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
        nz = z + dt / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
        if i > 10 and z < zs <= nz:
            a = (zs - z) / (nz - z)
            return np.array([x + a * (nx - x), y + a * (ny - y), zs]), t + a * dt
        x, y, z = nx, ny, nz
        t += dt
    return np.array([np.nan, np.nan, np.nan]), t
